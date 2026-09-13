"""Frozen four-arm evaluation for the independent synthetic pilot."""

from collections import Counter
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import time

from src.agents.pipeline import build_evidence_pack
from src.config import ROOT, Settings, settings
from src.controls.engine import MINIMUM_WAIT_CONTROLS, evaluate_control
from src.dataplane.corpus import load_manifest
from src.gateway.ledger import Ledger
from src.gateway.prices import ROUTES, get_price
from src.register.obligations import for_controls, load_candidates, review_composition


AS_OF = "2026-09-13"
SEED = 20260913
OUTPUT_CAP = 512
MODEL_VERSION = "2025-08-07"
MODEL_TIERS = {
    "cheap": {"model": "gpt-5-nano", "deployment": "obligationiq-gpt5nano",
              "arm": "rules_plus_agent_cheap", "escalation_reason": None},
    "strong": {"model": "gpt-5-mini", "deployment": "obligationiq-gpt5mini",
               "arm": "rules_plus_agent_strong", "escalation_reason": "quality_review"},
}
OBLIGATIONS = tuple(f"OIQ-{index:03d}" for index in range(1, 33))
FILES = {
    "contract": ROOT / "data/evaluation-contract.json",
    "cases": ROOT / "data/evaluation-cases.json",
    "truth": ROOT / "data/ground_truth/evaluation-cases.json",
    "rubric": ROOT / "docs/phase-7-evidence-rubric.json",
    "manifest": ROOT / "docs/phase-7-frozen-manifest.json",
    "results": ROOT / "docs/phase-7-evaluation-results.json",
}
FROZEN_CODE = (
    "src/eval/harness.py", "src/agents/drafter.py", "src/agents/critic.py",
    "src/agents/pipeline.py", "src/gateway/llm_client.py", "src/gateway/prices.py",
    "data/obligation-candidates.json", "data/human-reviews.json",
    "data/source-reviews.json", "data/operational-reviews.json",
)


def canonical(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def add_business_days(value, count, holidays):
    """Independent checklist arithmetic; it does not import control timing code."""
    current = date.fromisoformat(value)
    blocked = {date.fromisoformat(day) for day in holidays}
    for _ in range(count):
        current += timedelta(days=1)
        while current.weekday() >= 5 or current in blocked:
            current += timedelta(days=1)
    return current.isoformat()


def evaluation_contract():
    return {
        "version": 1,
        "seed": SEED,
        "synthetic": True,
        "frozen_on": AS_OF,
        "as_of_date": AS_OF,
        "case_design": "Two cases for every obligation plus eight frozen hard cases: boundaries, holiday arithmetic, partial evidence, jurisdiction, point-in-time and event sequence.",
        "obligation_ids": list(OBLIGATIONS),
        "arms": ["manual_checklist_surrogate", "deterministic_rules",
                 "rules_plus_agent_cheap", "rules_plus_agent_strong"],
        "manual_baseline_limit": "Programmatic document-review checklist; no human reviewer or human timing measurement.",
        "model_routes": MODEL_TIERS,
        "model_version": MODEL_VERSION,
        "sku": "GlobalStandard",
        "account_region": "australiaeast",
        "max_output_tokens_per_case": OUTPUT_CAP,
        "calls_per_case": 1,
        "strong_model_escalation_reason": "quality_review",
        "unmeasured": ["staff hours saved", "penalties avoided", "customer satisfaction", "human reviewer latency"],
    }


def evidence_rubric():
    return {
        "version": 1,
        "scoring": "Eight binary criteria per case; completeness is earned points divided by available points.",
        "criteria": [
            {"id": "identity", "description": "Pseudonymous case identifier and synthetic label."},
            {"id": "status", "description": "Explicit immutable control status."},
            {"id": "reason", "description": "Factual decision rationale."},
            {"id": "gaps", "description": "Explicit evidence-gap list, including an empty list."},
            {"id": "version_binding", "description": "Applied record and source digests."},
            {"id": "citation", "description": "Issuer, title, version, URL, clause, pages and source digests."},
            {"id": "timeline", "description": "Ordered evidence timeline."},
            {"id": "review_composition", "description": "Human-verified and agent-reviewed proportions."},
        ],
        "citation_accuracy": "All citation fields an arm emits must exactly match the reviewed register; omissions reduce completeness.",
        "groundedness": "Structured status, gaps and citations must match frozen case/register facts. Agent JSON must also preserve fixed fields and introduce no unsupported date or OIQ identifier.",
    }


def add_months(value, count):
    current = date.fromisoformat(value)
    index = current.month - 1 + count
    year, month = current.year + index // 12, index % 12 + 1
    days = [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
            31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return current.replace(year=year, month=month, day=min(current.day, days[month - 1])).isoformat()


def previous_business_day(value, holidays=()):
    current = date.fromisoformat(value) - timedelta(days=1)
    blocked = {date.fromisoformat(day) for day in holidays}
    while current.weekday() >= 5 or current in blocked:
        current -= timedelta(days=1)
    return current.isoformat()


def base_anchor(obligation):
    if obligation["deadline_unit"] == "months" or (obligation["deadline_value"] or 0) >= 50:
        return "2026-07-01"
    if (obligation["deadline_value"] or 0) >= 25:
        return "2026-07-20"
    if obligation["deadline_value"]:
        return "2026-08-03"
    return "2026-08-25"


def deadline_for(obligation, anchor, holidays=()):
    if obligation["deadline_unit"] == "business_days":
        return add_business_days(anchor, obligation["deadline_value"], holidays)
    if obligation["deadline_unit"] == "months":
        return add_months(anchor, obligation["deadline_value"])
    return None


def case_record(obligation, variant, *, regime=None, anchor=None, holidays=(),
                missing=None, point_in_time=False, event_stream=None):
    anchor = anchor or base_anchor(obligation)
    deadline = deadline_for(obligation, anchor, holidays)
    case_id = "CASE-" + hashlib.sha256(
        f"phase7:{SEED}:{obligation['obligation_id']}:{variant}".encode()).hexdigest()[:16]
    evidence = {name: {"present": name != missing} for name in obligation["evidence_required"]}
    case = {
        "case_id": case_id, "synthetic": True, "obligation_id": obligation["obligation_id"],
        "regime": regime or obligation["regime"], "as_of_date": AS_OF,
        "trigger_occurred": True, "trigger_at": anchor, "evidence": evidence,
    }
    if obligation["deadline_unit"] == "business_days":
        case["business_calendar"] = {
            "calendar_id": "SYNTHETIC-DECLARED-HOLIDAYS-2026",
            "coverage_start": "2026-01-01", "coverage_end": AS_OF,
            "public_holidays": list(holidays),
        }
    if variant in {"near_miss_nonbreach", "one_day_before", "holiday_boundary", "sequence"}:
        if deadline is None:
            case.update(action_completed=True, action_at="2026-08-26")
            expected = "compliant"
        elif deadline > AS_OF:
            case.update(action_completed=False, non_completion_confirmed_at=AS_OF)
            expected = ("insufficient_evidence" if obligation["deadline_unit"] == "business_days"
                        else "compliant" if obligation["obligation_id"] in MINIMUM_WAIT_CONTROLS
                        else "at_risk")
        else:
            action = (previous_business_day(deadline, holidays)
                      if variant == "one_day_before" else deadline)
            case.update(action_completed=True, action_at=action)
            expected = "compliant"
    elif variant == "breach":
        if deadline is None:
            case.update(action_completed=False, non_completion_confirmed_at=AS_OF)
        elif deadline > AS_OF and obligation["deadline_unit"] == "business_days":
            case.update(action_completed=True, action_at=AS_OF)
            expected = "insufficient_evidence"
        elif obligation["timing_operator"] == "at_most":
            case.update(action_completed=True, action_at=add_business_days(deadline, 1, holidays))
        else:
            case.update(action_completed=True, action_at=previous_business_day(deadline, holidays))
        if not (deadline and deadline > AS_OF and obligation["deadline_unit"] == "business_days"):
            expected = "breach"
    elif variant == "partial_evidence":
        case.update(action_completed=True, action_at=deadline or "2026-08-26")
        expected = "insufficient_evidence"
    elif variant == "jurisdiction_trap":
        if deadline is None:
            case.update(action_completed=False, non_completion_confirmed_at=AS_OF)
        elif obligation["timing_operator"] == "at_most":
            case.update(action_completed=True, action_at=add_business_days(deadline, 1, holidays))
        else:
            case.update(action_completed=True, action_at=previous_business_day(deadline, holidays))
        expected = "not_applicable"
    elif point_in_time:
        case["as_of_date"] = "2026-07-10"
        case["business_calendar"]["coverage_end"] = "2026-07-10"
        case.update(action_completed=True, action_at="2026-07-09")
        expected = "insufficient_evidence"
    else:
        raise ValueError("Unknown evaluation variant")
    if event_stream is not None:
        case["event_stream"] = event_stream
    expected_gaps = ([missing] if missing else
                     ["applicable_obligation_version"] if point_in_time else [])
    if expected == "insufficient_evidence" and deadline and deadline > case["as_of_date"] and not expected_gaps:
        expected_gaps = ["business_calendar"]
    return case, {
        "case_id": case_id, "obligation_id": obligation["obligation_id"],
        "challenge_type": variant, "expected_status": expected,
        "expected_evidence_gaps": expected_gaps,
    }


def build_cases():
    obligations = {row["obligation_id"]: row for row in for_controls(load_candidates())}
    cases, labels = [], []
    for obligation_id in OBLIGATIONS:
        obligation = obligations[obligation_id]
        for variant in ("near_miss_nonbreach", "breach"):
            case, label = case_record(obligation, variant)
            cases.append(case); labels.append(label)
    extras = [
        case_record(obligations["OIQ-002"], "one_day_before"),
        case_record(obligations["OIQ-023"], "holiday_boundary", anchor="2026-08-07",
                    holidays=("2026-08-10",)),
        case_record(obligations["OIQ-024"], "partial_evidence",
                    missing=obligations["OIQ-024"]["evidence_required"][0]),
        case_record(obligations["OIQ-002"], "jurisdiction_trap", regime="VIC"),
        case_record(obligations["OIQ-021"], "jurisdiction_trap", regime="NERL_NERR"),
        case_record(obligations["OIQ-028"], "point_in_time", anchor="2026-06-30",
                    point_in_time=True),
        case_record(obligations["OIQ-008"], "sequence", event_stream=[
            {"event_type": "action", "occurred_on": "2026-08-10"},
            {"event_type": "trigger", "occurred_on": "2026-08-03"},
        ]),
        case_record(obligations["OIQ-005"], "holiday_boundary", anchor="2026-08-03",
                    holidays=("2026-08-10",)),
    ]
    for case, label in extras:
        cases.append(case); labels.append(label)
    return (
        {"synthetic": True, "seed": SEED, "as_of_date": AS_OF, "cases": cases},
        {"synthetic": True, "seed": SEED, "as_of_date": AS_OF, "cases": labels},
    )


def manual_checklist(obligation, case):
    """Static worksheet surrogate. It is not observed human performance."""
    gaps = [name for name in obligation["evidence_required"]
            if not isinstance(case.get("evidence", {}).get(name), dict)
            or case["evidence"][name].get("present") is not True]
    if case.get("regime") != obligation["regime"]:
        status, reason, gaps = "not_applicable", "The worksheet rejects a jurisdiction-regime mismatch.", []
    elif obligation.get("effective_from") and case.get("trigger_at") < obligation["effective_from"]:
        status, reason = "insufficient_evidence", "The trigger predates the available obligation version."
        gaps = ["applicable_obligation_version"]
    elif case.get("trigger_occurred") is not True:
        status, reason = "insufficient_evidence", "The worksheet lacks affirmative trigger evidence."
        gaps = ["trigger_occurred"]
    elif gaps:
        status, reason = "insufficient_evidence", "The worksheet identifies missing required evidence."
    elif obligation["deadline_value"] is None:
        if case.get("action_completed") is True:
            status, reason = "compliant", "The worksheet records the required action as completed."
        elif case.get("action_completed") is False and case.get("non_completion_confirmed_at"):
            status, reason = "breach", "The worksheet records affirmative non-completion."
        else:
            status, reason, gaps = "insufficient_evidence", "Completion is not evidenced.", ["action_completion"]
    else:
        calendar = case.get("business_calendar", {})
        deadline = deadline_for(obligation, case["trigger_at"], calendar.get("public_holidays", []))
        if (obligation["deadline_unit"] == "business_days" and
                calendar.get("coverage_end", "") < deadline):
            status, reason, gaps = ("insufficient_evidence",
                                    "The supplied calendar does not cover the full deadline interval.",
                                    ["business_calendar"])
        elif case.get("action_completed") is True and case.get("action_at"):
            if obligation["timing_operator"] == "at_most":
                status = "compliant" if case["action_at"] <= deadline else "breach"
            else:
                status = "compliant" if case["action_at"] >= deadline else "breach"
            reason = "The worksheet compares the recorded action date with the source deadline."
        elif (case.get("action_completed") is False and
              obligation["obligation_id"] in MINIMUM_WAIT_CONTROLS):
            status, reason = "compliant", "The worksheet confirms no restricted action occurred."
        elif case.get("action_completed") is False and case.get("non_completion_confirmed_at"):
            status = "breach" if case["as_of_date"] >= deadline else "at_risk"
            reason = "The worksheet records an incomplete minimum-duration requirement."
        else:
            status, reason, gaps = "insufficient_evidence", "Completion is not evidenced.", ["action_completion"]
    return {
        "synthetic": True, "case_id": case["case_id"],
        "obligation_id": obligation["obligation_id"], "control_status": status,
        "reason": reason, "evidence_gaps": sorted(gaps),
        "clause_reference": obligation["clause_reference"],
        "review_composition": review_composition([obligation]),
        "baseline_type": "programmatic_manual_checklist_surrogate",
    }


def rubric_points(arm, artifact):
    del arm
    citation = artifact.get("citation")
    timeline = artifact.get("timeline")
    composition = artifact.get("review_composition")
    status = artifact.get("control_status", artifact.get("status"))
    reason = artifact.get("control_reason", artifact.get("reason"))
    citation_fields = {"source_id", "title", "issuer", "version", "url", "regime",
                       "clause_reference", "parent_clause", "pdf_pages", "source_sha256",
                       "source_clause_sha256"}
    ordered_timeline = (isinstance(timeline, list) and
                        timeline == sorted(timeline, key=lambda row: (
                            row.get("occurred_on", ""), row.get("event_type", ""),
                            row.get("evidence_item") or "")))
    return {
        "identity": (artifact.get("synthetic") is True and
                     re.fullmatch(r"CASE-[0-9a-f]{16}", str(artifact.get("case_id", ""))) is not None),
        "status": isinstance(status, str) and bool(status),
        "reason": isinstance(reason, str) and bool(reason.strip()),
        "gaps": isinstance(artifact.get("evidence_gaps"), list),
        "version_binding": all(re.fullmatch(r"[0-9a-f]{64}", str(artifact.get(key, "")))
                               for key in ("applied_record_sha256", "applied_source_sha256")),
        "citation": isinstance(citation, dict) and citation_fields <= set(citation),
        "timeline": ordered_timeline,
        "review_composition": (isinstance(composition, dict) and
                               all(key in composition for key in
                                   ("total", "human_verified", "human_verified_proportion",
                                    "agent_reviewed", "agent_reviewed_proportion"))),
    }


def citation_is_accurate(arm, artifact, obligation):
    if arm == "manual_checklist_surrogate":
        return artifact["clause_reference"] == obligation["clause_reference"]
    if arm == "deterministic_rules":
        return (artifact["applied_clause_reference"] == obligation["clause_reference"] and
                artifact["applied_record_sha256"] == obligation["record_sha256"] and
                artifact["applied_source_sha256"] == obligation["source_sha256"])
    citation = artifact["citation"]
    source = next(row for row in load_manifest()["sources"] if row["id"] == obligation["source_id"])
    expected = {
        "source_id": obligation["source_id"], "title": obligation["instrument"],
        "issuer": source["issuer"],
        "version": obligation["source_version"], "url": obligation["source_url"],
        "regime": obligation["regime"], "clause_reference": obligation["clause_reference"],
        "parent_clause": obligation["parent_clause"], "source_sha256": obligation["source_sha256"],
        "source_clause_sha256": obligation["source_clause_sha256"],
        "pdf_pages": [obligation["source_page_start"], obligation["source_page_end"]],
    }
    return all(citation.get(key) == value for key, value in expected.items())


def model_narrative_grounded(pack):
    assistance = pack["model_assistance"]
    try:
        value = json.loads(assistance["text"])
    except (KeyError, TypeError, json.JSONDecodeError):
        return False, "Model output is not valid JSON."
    expected_keys = {"summary", "fixed_control_status", "clause_reference", "evidence_gaps"}
    if (set(value) != expected_keys or not isinstance(value["summary"], str)
            or value["fixed_control_status"] != pack["control_status"]
            or value["clause_reference"] != pack["citation"]["clause_reference"]
            or value["evidence_gaps"] != pack["evidence_gaps"]):
        return False, "Model output changes or omits a fixed structured fact."
    dates = set(re.findall(r"\b20\d\d-\d\d-\d\d\b", value["summary"]))
    ids = set(re.findall(r"\bOIQ-\d{3}\b", value["summary"]))
    timeline_dates = {row["occurred_on"] for row in pack["timeline"]}
    if not dates <= timeline_dates or not ids <= {pack["obligation_id"]}:
        return False, "Model summary introduces an unsupported date or obligation identifier."
    return True, "Fixed fields match and no unsupported date or obligation identifier was introduced."


def detection_metrics(rows):
    tp = sum(row["expected"] == "breach" and row["actual"] == "breach" for row in rows)
    fp = sum(row["expected"] != "breach" and row["actual"] == "breach" for row in rows)
    fn = sum(row["expected"] == "breach" and row["actual"] != "breach" for row in rows)
    tn = sum(row["expected"] != "breach" and row["actual"] != "breach" for row in rows)
    ratio = lambda a, b: a / b if b else None
    return {
        "true_positives": tp, "false_positives": fp, "false_negatives": fn,
        "true_negatives": tn, "recall": ratio(tp, tp + fn),
        "precision": ratio(tp, tp + fp), "false_positive_rate": ratio(fp, fp + tn),
        "exact_status_accuracy": ratio(sum(r["expected"] == r["actual"] for r in rows), len(rows)),
    }


def frozen_payloads():
    cases, truth = build_cases()
    return {"contract": evaluation_contract(), "cases": cases, "truth": truth,
            "rubric": evidence_rubric()}


def build_manifest(payloads):
    hashes = {str(FILES[key].relative_to(ROOT)): digest(canonical(value))
              for key, value in payloads.items()}
    hashes.update({path: digest((ROOT / path).read_bytes()) for path in FROZEN_CODE})
    return {
        "version": 1, "frozen_on": AS_OF,
        "purpose": "Binds cases, hidden labels, rubric, register decisions, gateway and agent code before live results.",
        "sha256": dict(sorted(hashes.items())),
    }


def prepare():
    payloads = frozen_payloads()
    for key, value in payloads.items():
        FILES[key].parent.mkdir(parents=True, exist_ok=True)
        FILES[key].write_bytes(canonical(value))
    FILES["manifest"].write_bytes(canonical(build_manifest(payloads)))
    return {"cases": len(payloads["cases"]["cases"]), "sha256": digest(FILES["manifest"].read_bytes())}


def validate_frozen():
    payloads = frozen_payloads()
    for key, value in payloads.items():
        if not FILES[key].is_file() or FILES[key].read_bytes() != canonical(value):
            raise ValueError(f"Frozen Phase 7 {key} differs from its deterministic definition")
    expected = build_manifest(payloads)
    if json.loads(FILES["manifest"].read_text()) != expected:
        raise ValueError("Frozen Phase 7 manifest or bound implementation changed")
    return payloads


def offline_arms(payloads, *, measure_latency=False):
    obligations = {row["obligation_id"]: row for row in for_controls(load_candidates())}
    labels = {row["case_id"]: row for row in payloads["truth"]["cases"]}
    rows = {"manual_checklist_surrogate": [], "deterministic_rules": []}
    for case in payloads["cases"]["cases"]:
        obligation, expected = obligations[case["obligation_id"]], labels[case["case_id"]]
        started = time.perf_counter()
        manual = manual_checklist(obligation, case)
        manual_latency = round((time.perf_counter() - started) * 1000, 3)
        started = time.perf_counter()
        control = evaluate_control(obligation, case, case["as_of_date"]).to_dict()
        control_latency = round((time.perf_counter() - started) * 1000, 3)
        control["synthetic"] = True
        control["review_composition"] = review_composition([obligation])
        for arm, artifact in (("manual_checklist_surrogate", manual),
                              ("deterministic_rules", control)):
            actual = artifact["control_status"] if arm.startswith("manual") else artifact["status"]
            actual_gaps = artifact["evidence_gaps"]
            row = {"case_id": case["case_id"], "expected": expected["expected_status"],
                              "actual": actual,
                              "expected_gaps": expected["expected_evidence_gaps"],
                              "actual_gaps": actual_gaps, "artifact": artifact,
                              "grounded": (actual == expected["expected_status"] and
                                           actual_gaps == expected["expected_evidence_gaps"] and
                                           citation_is_accurate(arm, artifact, obligation))}
            if measure_latency:
                row["latency_ms"] = manual_latency if arm.startswith("manual") else control_latency
            rows[arm].append(row)
    return rows


def preflight():
    payloads = validate_frozen()
    rows = offline_arms(payloads)
    metrics = {arm: detection_metrics(values) for arm, values in rows.items()}
    if metrics["manual_checklist_surrogate"]["exact_status_accuracy"] != 1.0:
        raise ValueError("The frozen checklist baseline differs from its authored labels")
    return {"cases": len(payloads["cases"]["cases"]), "offline_metrics": metrics}


def _aggregate_arm(arm, rows, obligations):
    earned = sum(sum(rubric_points(arm, row["artifact"]).values()) for row in rows)
    possible = len(rows) * len(evidence_rubric()["criteria"])
    citation = sum(citation_is_accurate(arm, row["artifact"], obligations[row["artifact"]["obligation_id"]])
                   for row in rows)
    grounded = sum(row.get("grounded", True) for row in rows)
    result = {
        "cases": len(rows), "detection": detection_metrics(rows),
        "evidence_pack_completeness": earned / possible,
        "evidence_rubric_points": earned, "evidence_rubric_possible": possible,
        "citation_accuracy": citation / len(rows), "groundedness": grounded / len(rows),
    }
    under_evidenced = [row for row in rows if row["expected"] == "insufficient_evidence"]
    result["under_evidenced_refusal_correctness"] = (
        sum(row["actual"] == "insufficient_evidence" and
            row["actual_gaps"] == row["expected_gaps"] for row in under_evidenced) /
        len(under_evidenced) if under_evidenced else None)
    if all("latency_ms" in row for row in rows):
        latencies = [row["latency_ms"] for row in rows]
        result.update(latency_ms_mean=sum(latencies) / len(latencies),
                      latency_ms_min=min(latencies), latency_ms_max=max(latencies))
    if any("critic_accepted" in row for row in rows):
        result["critic_acceptance_rate"] = sum(row.get("critic_accepted", False) for row in rows) / len(rows)
    return result


def _model_costs(ledger, model):
    records = [row for row in ledger.call_records() if row.get("model") == model]
    confirmed = sum(int(Decimal(row["estimated_aud"]) * 1_000_000)
                    for row in records if row.get("status") == "success")
    ambiguous = sum(int(Decimal(row["estimated_aud"]) * 1_000_000)
                    for row in records if row.get("status") == "ambiguous_settlement")
    latencies = [row["latency_ms"] for row in records if row.get("status") == "success"]
    return {"confirmed_microaud": confirmed, "ambiguous_microaud": ambiguous,
            "worst_case_microaud": confirmed + ambiguous,
            "successful_provider_responses": len(latencies),
            "ambiguous_settlements": sum(row.get("status") == "ambiguous_settlement" for row in records),
            "gateway_latency_ms": latencies}


def _run_agent_arm(tier, payloads, obligations, labels, config, ledger):
    route = MODEL_TIERS[tier]
    arm, run_id = route["arm"], f"phase7-{tier}-{AS_OF.replace('-', '')}"
    rows, public = [], []
    for original in payloads["cases"]["cases"]:
        case = dict(original)
        case["evaluation_run_id"] = run_id
        expected, obligation = labels[case["case_id"]], obligations[case["obligation_id"]]
        started = time.perf_counter()
        before = ledger.summary()["committed_microaud"]
        pack, critic = build_evidence_pack(
            case, use_model=True, tier=tier, escalation_reason=route["escalation_reason"],
            config=config, max_output_tokens=OUTPUT_CAP, strict=False)
        latency_ms = round((time.perf_counter() - started) * 1000, 3)
        after = ledger.summary()["committed_microaud"]
        artifact = pack.to_dict()
        narrative_grounded, reason = model_narrative_grounded(artifact)
        grounded = (narrative_grounded and artifact["control_status"] == expected["expected_status"]
                    and artifact["evidence_gaps"] == expected["expected_evidence_gaps"]
                    and citation_is_accurate(arm, artifact, obligation))
        raw = artifact["model_assistance"].pop("text")
        artifact["model_assistance"]["output_sha256"] = digest(raw.encode())
        rows.append({
            "case_id": case["case_id"], "expected": expected["expected_status"],
            "actual": artifact["control_status"],
            "expected_gaps": expected["expected_evidence_gaps"],
            "actual_gaps": artifact["evidence_gaps"], "artifact": artifact,
            "grounded": grounded, "critic_accepted": critic.accepted,
        })
        public.append({
            "case_id": case["case_id"], "obligation_id": case["obligation_id"],
            "expected_status": expected["expected_status"],
            "actual_status": artifact["control_status"], "critic": critic.to_dict(),
            "grounded": grounded, "groundedness_reason": reason,
            "current_pipeline_latency_ms": latency_ms,
            "cache_reused": after == before,
            "model_assistance": artifact["model_assistance"],
        })
    return arm, rows, public


def live_evaluate(config: Settings = settings):
    payloads = validate_frozen()
    if config.mode != "live" or not config.allow_live:
        raise ValueError("Live evaluation requires LLM_MODE=live and LLM_ALLOW_LIVE=true")
    for tier, route in MODEL_TIERS.items():
        if (config.azure["AZURE_OPENAI_DEPLOYMENT_" + tier.upper()] != route["deployment"] or
                get_price(ROUTES[tier]).version != MODEL_VERSION):
            raise ValueError("Live deployment or model version differs from the frozen contract")
    obligations = {row["obligation_id"]: row for row in for_controls(load_candidates())}
    labels = {row["case_id"]: row for row in payloads["truth"]["cases"]}
    rows = offline_arms(payloads, measure_latency=True)
    ledger = Ledger(config.state_dir / "gateway.sqlite3", config.daily_limit, config.project_limit)
    public_cases = {}
    for tier in ("cheap", "strong"):
        arm, arm_rows, public = _run_agent_arm(tier, payloads, obligations, labels, config, ledger)
        rows[arm], public_cases[arm] = arm_rows, public
    if ledger.summary()["held_microaud"]:
        raise ValueError("Ledger has an unresolved reservation")
    arm_metrics = {arm: _aggregate_arm(arm, value, obligations) for arm, value in rows.items()}
    execution = {}
    for tier, route in MODEL_TIERS.items():
        costs = _model_costs(ledger, route["model"])
        latencies = costs.pop("gateway_latency_ms")
        if len(latencies) != len(payloads["cases"]["cases"]):
            raise ValueError("Provider response count does not match the frozen case set")
        arm_metrics[route["arm"]].update(
            gateway_latency_ms_mean=sum(latencies) / len(latencies),
            gateway_latency_ms_min=min(latencies), gateway_latency_ms_max=max(latencies))
        execution[tier] = {
            "model": route["model"], "model_version": MODEL_VERSION,
            "deployment": route["deployment"], "tier": tier,
            "escalation_reason": route["escalation_reason"],
            "max_output_tokens_per_case": OUTPUT_CAP,
            **costs,
            "confirmed_cost_per_case_aud": str(
                Decimal(costs["confirmed_microaud"]) / Decimal(72_000_000)),
            "worst_case_cost_per_case_aud": str(
                Decimal(costs["worst_case_microaud"]) / Decimal(72_000_000)),
            "raw_outputs_committed": False,
        }
    cheap, strong = (arm_metrics[MODEL_TIERS[tier]["arm"]] for tier in ("cheap", "strong"))
    quality_fields = ("evidence_pack_completeness", "citation_accuracy", "groundedness",
                      "under_evidenced_refusal_correctness", "critic_acceptance_rate")
    delta = {key: strong[key] - cheap[key] for key in quality_fields}
    delta["confirmed_cost_per_case_aud"] = str(
        Decimal(execution["strong"]["confirmed_cost_per_case_aud"]) -
        Decimal(execution["cheap"]["confirmed_cost_per_case_aud"]))
    delta["gateway_latency_ms_mean"] = (strong["gateway_latency_ms_mean"] -
                                         cheap["gateway_latency_ms_mean"])
    meaningful = any(delta[key] >= 0.01 for key in quality_fields)
    recommendation = (
        "Retain cheap-model default; the strong drafter did not improve a measured quality rate by at least one percentage point."
        if not meaningful else
        "Use strong routing only for the measured quality criteria where it materially exceeded the cheap drafter; deterministic rules retain status authority."
    )
    costs = ledger.cost_summary()
    report = {
        "status": "Phase 7 complete: frozen four-arm all-obligation synthetic evaluation",
        "synthetic_evaluation": True, "evaluated_on": AS_OF,
        "frozen_manifest_sha256": digest(FILES["manifest"].read_bytes()),
        "cases_per_arm": 72, "obligations": len(OBLIGATIONS), "arms": arm_metrics,
        "manual_baseline_limit": evaluation_contract()["manual_baseline_limit"],
        "agent_execution": execution, "strong_minus_cheap": delta,
        "ledger_costs_aud": {key.removesuffix("_microaud") + "_aud":
                             str(Decimal(value) / Decimal(1_000_000))
                             for key, value in costs.items()},
        "review_composition": review_composition(list(obligations.values())),
        "cases_public": public_cases,
        "unmeasured": evaluation_contract()["unmeasured"],
        "recommendation": recommendation,
        "scope_limit": "Seventy-two synthetic cases across all 32 obligations; no production, prevalence or human-effort claim.",
    }
    FILES["results"].write_bytes(canonical(report))
    return report


def cache_replay(config: Settings = settings):
    payloads = validate_frozen()
    cached = replace(config, mode="cached", allow_live=False)
    obligations = {row["obligation_id"]: row for row in for_controls(load_candidates())}
    labels = {row["case_id"]: row for row in payloads["truth"]["cases"]}
    ledger = Ledger(cached.state_dir / "gateway.sqlite3", cached.daily_limit, cached.project_limit)
    before = ledger.summary()
    for tier in ("cheap", "strong"):
        _run_agent_arm(tier, payloads, obligations, labels, cached, ledger)
    after = ledger.summary()
    if before != after:
        raise ValueError("Cached replay changed paid reservations")
    return {"cases_per_model": 72, "models": 2, "additional_spend_aud": "0"}


def validate_results(report):
    if report.get("frozen_manifest_sha256") != digest(FILES["manifest"].read_bytes()):
        raise ValueError("Published result is not bound to the frozen manifest")
    if report.get("synthetic_evaluation") is not True or report.get("cases_per_arm") != 72:
        raise ValueError("Published result scope changed")
    expected = {"manual_checklist_surrogate", "deterministic_rules",
                "rules_plus_agent_cheap", "rules_plus_agent_strong"}
    if set(report.get("arms", {})) != expected:
        raise ValueError("Published four-arm result is incomplete")
    public = [row for arm in report.get("cases_public", {}).values() for row in arm]
    if any("text" in row.get("model_assistance", {}) for row in public):
        raise ValueError("Raw model narrative must remain local")


def check():
    result = preflight()
    if FILES["results"].is_file():
        validate_results(json.loads(FILES["results"].read_text()))
    return result
