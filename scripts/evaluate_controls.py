"""Evaluate deterministic controls on the frozen all-obligation challenge set."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import ROOT
from src.controls.engine import CONTROL_FUNCTIONS, evaluate_control
from src.eval.harness import FILES, validate_frozen
from src.register.obligations import for_controls, load_candidates, review_composition

OUTPUT = ROOT / "docs/phase-4-control-results.json"


def deny_network(event, args):
    if event.startswith("socket."):
        raise RuntimeError("Control evaluation must be offline")


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def metrics(rows):
    tp = sum(r["expected_status"] == "breach" and r["actual_status"] == "breach" for r in rows)
    fp = sum(r["expected_status"] != "breach" and r["actual_status"] == "breach" for r in rows)
    fn = sum(r["expected_status"] == "breach" and r["actual_status"] != "breach" for r in rows)
    tn = sum(r["expected_status"] != "breach" and r["actual_status"] != "breach" for r in rows)
    exact = sum(r["expected_status"] == r["actual_status"] for r in rows)
    return {
        "true_positives": tp, "false_positives": fp, "false_negatives": fn,
        "true_negatives": tn, "breach_detection_recall": ratio(tp, tp + fn),
        "breach_detection_precision": ratio(tp, tp + fp),
        "false_positive_rate": ratio(fp, fp + tn),
        "exact_status_accuracy": ratio(exact, len(rows)),
    }


def evaluate():
    payloads = validate_frozen()
    cases = payloads["cases"]["cases"]
    labels = {item["case_id"]: item for item in payloads["truth"]["cases"]}
    obligations = {record["obligation_id"]: record for record in for_controls(load_candidates())}
    if set(CONTROL_FUNCTIONS) != set(obligations) or len(obligations) != 32:
        raise ValueError("Control coverage does not match the eligible register")
    if set(labels) != {case["case_id"] for case in cases}:
        raise ValueError("Challenge inputs and labels do not align")

    results = []
    for case in cases:
        obligation = obligations[case["obligation_id"]]
        control = evaluate_control(obligation, case, case["as_of_date"])
        expected = labels[case["case_id"]]
        results.append({
            "case_id": case["case_id"], "obligation_id": case["obligation_id"],
            "challenge_type": expected["challenge_type"],
            "expected_status": expected["expected_status"], "actual_status": control.status,
            "expected_evidence_gaps": expected["expected_evidence_gaps"],
            "evidence_gaps": list(control.evidence_gaps),
            "applied_record_sha256": control.applied_record_sha256,
            "applied_source_sha256": control.applied_source_sha256,
            "applied_source_version": control.applied_source_version,
            "applied_clause_reference": control.applied_clause_reference,
            "business_calendar_id": control.business_calendar_id,
        })
    by_obligation = {}
    for obligation_id in sorted(obligations):
        subset = [row for row in results if row["obligation_id"] == obligation_id]
        by_obligation[obligation_id] = {"cases": len(subset), **metrics(subset)}
    errors = [row for row in results if (row["expected_status"], row["expected_evidence_gaps"])
              != (row["actual_status"], row["evidence_gaps"])]
    taxonomy = Counter(
        (row["challenge_type"], row["expected_status"], row["actual_status"]) for row in errors)
    version_matches = sum(
        row["applied_record_sha256"] == obligations[row["obligation_id"]]["record_sha256"] and
        row["applied_source_sha256"] == obligations[row["obligation_id"]]["source_sha256"] and
        row["applied_clause_reference"] == obligations[row["obligation_id"]]["clause_reference"]
        for row in results)
    return {
        "status": "Phase 4 revised: all-obligation hard-case evaluation published without retuning",
        "synthetic_evaluation": True, "evaluated_on": payloads["contract"]["frozen_on"],
        "eligible_obligations": len(obligations),
        "implemented_control_functions": len(CONTROL_FUNCTIONS),
        "challenge_cases": len(results), "challenge_obligations": len(by_obligation),
        "case_mix": dict(sorted(Counter(row["challenge_type"] for row in results).items())),
        "expected_status_mix": dict(sorted(Counter(row["expected_status"] for row in results).items())),
        "metrics": {**metrics(results),
                    "version_and_citation_match_rate": ratio(version_matches, len(results))},
        "per_obligation": by_obligation,
        "error_taxonomy": [
            {"challenge_type": kind, "expected": expected, "actual": actual, "count": count}
            for (kind, expected, actual), count in sorted(taxonomy.items())
        ],
        "errors": errors, "results": results,
        "review_composition": review_composition(list(obligations.values())),
        "evaluation_manifest_sha256": hashlib.sha256(FILES["manifest"].read_bytes()).hexdigest(),
        "control_boundary": "Pure functions receive an obligation, customer state and explicit date. They perform no I/O and make no model call.",
        "scope_limit": "Seventy-two synthetic cases cover all 32 obligations. They test authored edge cases, not production prevalence or legal completeness.",
        "no_retuning": "Observed failures are retained as findings; controls were not changed after labels were frozen.",
        "model_calls": 0, "model_spend_aud": 0,
    }


def main(check=False):
    sys.addaudithook(deny_network)
    report = evaluate()
    if check:
        if report != json.loads(OUTPUT.read_text()):
            raise ValueError("Control evaluation differs from committed evidence")
        print("PASS: 32 controls and 72 frozen hard cases replay exactly; network disabled")
    else:
        OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({"cases": report["challenge_cases"], **report["metrics"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    main(parser.parse_args().check)
