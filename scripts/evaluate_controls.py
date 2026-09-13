"""Evaluate deterministic controls against the isolated synthetic challenge labels."""

import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT
from src.controls.engine import CONTROL_FUNCTIONS, evaluate_control
from src.dataplane.population import build
from src.register.obligations import for_controls, load_candidates, review_composition


OUTPUT = ROOT / "docs/phase-4-control-results.json"


def deny_network(event, args):
    if event.startswith("socket."):
        raise RuntimeError("Control evaluation must be offline")


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def evaluate():
    inputs = json.loads((ROOT / "data/population-inputs.json").read_text())
    inputs["operational_context"] = json.loads((ROOT / "data/operational-context.json").read_text())
    contract = json.loads((ROOT / "data/population-contract.json").read_text())
    artifacts, population_report = build(inputs, contract)
    committed_truth = (ROOT / "data/ground_truth/control-cases.json").read_bytes()
    if committed_truth != artifacts["ground_truth"]:
        raise ValueError("Committed challenge labels differ from the seeded build")
    truth = json.loads(committed_truth)
    cases = [json.loads(line) for line in artifacts["control_cases"].splitlines()]
    labels = {item["case_id"]: item for item in truth["cases"]}
    if set(labels) != {case["case_id"] for case in cases}:
        raise ValueError("Challenge inputs and labels do not align")
    obligations = {record["obligation_id"]: record for record in for_controls(load_candidates())}
    if set(CONTROL_FUNCTIONS) != set(obligations):
        raise ValueError("Control coverage does not match the eligible register")

    results = []
    for case in cases:
        obligation = obligations[case["obligation_id"]]
        state = dict(case)
        state["business_calendar"] = {
            "calendar_id": "SYNTHETIC-WEEKDAYS-2026-08-09",
            "coverage_start": "2026-08-03",
            "coverage_end": case["as_of_date"],
            "public_holidays": [],
        }
        control = evaluate_control(obligation, state, date.fromisoformat(case["as_of_date"]))
        expected = labels[case["case_id"]]
        results.append({
            "case_id": case["case_id"],
            "obligation_id": case["obligation_id"],
            "expected_status": expected["expected_status"],
            "actual_status": control.status,
            "evidence_gaps": list(control.evidence_gaps),
            "applied_record_sha256": control.applied_record_sha256,
            "applied_source_sha256": control.applied_source_sha256,
            "applied_source_version": control.applied_source_version,
            "applied_clause_reference": control.applied_clause_reference,
            "business_calendar_id": control.business_calendar_id,
        })
    tp = sum(row["expected_status"] == "breach" and row["actual_status"] == "breach" for row in results)
    fp = sum(row["expected_status"] != "breach" and row["actual_status"] == "breach" for row in results)
    fn = sum(row["expected_status"] == "breach" and row["actual_status"] != "breach" for row in results)
    tn = sum(row["expected_status"] != "breach" and row["actual_status"] != "breach" for row in results)
    matrix = Counter((row["expected_status"], row["actual_status"]) for row in results)
    exact = sum(row["expected_status"] == row["actual_status"] for row in results)
    under_evidenced = [row for row in results if row["expected_status"] == "insufficient_evidence"]
    version_matches = sum(
        row["applied_record_sha256"] == obligations[row["obligation_id"]]["record_sha256"] and
        row["applied_source_sha256"] == obligations[row["obligation_id"]]["source_sha256"] and
        row["applied_clause_reference"] == obligations[row["obligation_id"]]["clause_reference"]
        for row in results)
    return {
        "status": "Phase 4 complete: deterministic controls evaluated on isolated synthetic challenge cases",
        "synthetic_evaluation": True,
        "evaluated_on": contract["scenario_as_of"],
        "eligible_obligations": len(obligations),
        "implemented_control_functions": len(CONTROL_FUNCTIONS),
        "challenge_cases": len(results),
        "challenge_obligations": len({row["obligation_id"] for row in results}),
        "case_mix": dict(sorted(Counter(row["expected_status"] for row in results).items())),
        "metrics": {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn,
            "breach_detection_recall": ratio(tp, tp + fn),
            "breach_detection_precision": ratio(tp, tp + fp),
            "false_positive_rate": ratio(fp, fp + tn),
            "exact_status_accuracy": ratio(exact, len(results)),
            "insufficient_evidence_recall": ratio(
                sum(row["actual_status"] == "insufficient_evidence" for row in under_evidenced),
                len(under_evidenced)),
            "version_and_citation_match_rate": ratio(version_matches, len(results)),
        },
        "confusion_matrix": [
            {"expected": expected, "actual": actual, "count": count}
            for (expected, actual), count in sorted(matrix.items())
        ],
        "results": results,
        "review_composition": review_composition(list(obligations.values())),
        "population_artifact_sha256": population_report["artifact_sha256"],
        "control_boundary": "Pure functions receive an obligation, customer state and explicit date. They perform no I/O and make no model call.",
        "business_day_limit": "Business-day controls require a bounded supplied calendar. The synthetic window contains no NSW or Victorian public holiday; production calendars are not implemented.",
        "scope_limit": "Measured cases cover six of 32 eligible obligations. Callable coverage is 32/32; unmeasured obligation semantics are not claimed as benchmarked.",
        "model_calls": 0,
        "model_spend_aud": 0,
    }


def main(check=False):
    sys.addaudithook(deny_network)
    report = evaluate()
    if check:
        if report != json.loads(OUTPUT.read_text()):
            raise ValueError("Control evaluation differs from committed evidence")
        print("PASS: 32/32 controls bound; 18 challenge cases replay exactly; network disabled")
    else:
        OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"controls": report["implemented_control_functions"],
                          "cases": report["challenge_cases"], **report["metrics"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    main(parser.parse_args().check)
