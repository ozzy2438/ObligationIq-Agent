"""Evaluate and locally register the deterministic risk-triage baseline."""

import argparse
from collections import Counter
from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import ROOT
from src.risk.baseline import HIGH_PRIORITY_THRESHOLD, POLICY_VERSION, rank_control_result

import evaluate_controls


OUTPUT = ROOT / "docs/phase-5-risk-results.json"
POLICY = ROOT / "data/risk-baseline-policy.json"
EXPERIMENT = "obligationiq-risk"
REGISTERED_MODEL = "obligationiq-rule-risk-baseline"
ALIAS = "champion"


def deny_network(event, args):
    if event.startswith("socket."):
        raise RuntimeError("Risk evaluation and tracking must be offline")


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def priority_metrics(rows):
    expected_positive = lambda row: row["expected_status"] == "breach"
    predicted_positive = lambda row: row["priority_score"] >= HIGH_PRIORITY_THRESHOLD
    tp = sum(expected_positive(row) and predicted_positive(row) for row in rows)
    fp = sum(not expected_positive(row) and predicted_positive(row) for row in rows)
    fn = sum(expected_positive(row) and not predicted_positive(row) for row in rows)
    tn = sum(not expected_positive(row) and not predicted_positive(row) for row in rows)
    return {"true_positives": tp, "false_positives": fp, "false_negatives": fn,
            "true_negatives": tn, "recall": ratio(tp, tp + fn),
            "precision": ratio(tp, tp + fp), "false_positive_rate": ratio(fp, fp + tn)}


@dataclass(frozen=True)
class EvaluatedControl:
    case_id: str
    obligation_id: str
    status: str
    evidence_gaps: tuple[str, ...]
    applied_record_sha256: str


def _as_control(row):
    return EvaluatedControl(
        case_id=row["case_id"], obligation_id=row["obligation_id"],
        status=row["actual_status"], evidence_gaps=tuple(row["evidence_gaps"]),
        applied_record_sha256=row["applied_record_sha256"])


def evaluate():
    controls = evaluate_controls.evaluate()
    assessments = []
    for row in controls["results"]:
        risk = rank_control_result(_as_control(row))
        assessments.append({
            "case_id": risk.case_id,
            "obligation_id": risk.obligation_id,
            "expected_status": row["expected_status"],
            "challenge_type": row["challenge_type"],
            "control_status": risk.control_status,
            "priority_score": risk.priority_score,
            "priority_band": risk.priority_band,
            "reason_codes": list(risk.reason_codes),
            "evidence_gap_count": risk.evidence_gap_count,
            "applied_record_sha256": risk.applied_record_sha256,
            "is_compliance_decision": risk.is_compliance_decision,
            "is_calibrated_probability": risk.is_calibrated_probability,
        })
    measured = priority_metrics(assessments)
    by_obligation = {}
    for obligation_id in sorted({row["obligation_id"] for row in assessments}):
        subset = [row for row in assessments if row["obligation_id"] == obligation_id]
        by_obligation[obligation_id] = {"cases": len(subset), **priority_metrics(subset)}
    errors = [row for row in assessments if
              (row["expected_status"] == "breach") !=
              (row["priority_score"] >= HIGH_PRIORITY_THRESHOLD)]
    taxonomy = Counter((row["challenge_type"], row["expected_status"], row["control_status"])
                       for row in errors)
    return {
        "status": "Phase 5 complete: deterministic triage baseline shipped; learned model not trained",
        "synthetic_evaluation": True,
        "evaluated_on": controls["evaluated_on"],
        "review_horizon_days": 30,
        "challenge_cases": len(assessments),
        "challenge_obligations": len({row["obligation_id"] for row in assessments}),
        "baseline": {
            "policy_version": POLICY_VERSION,
            "high_priority_threshold": HIGH_PRIORITY_THRESHOLD,
            "metrics_against_frozen_breach_labels": measured,
            "per_obligation": by_obligation,
            "error_taxonomy": [
                {"challenge_type": kind, "expected": expected, "control_status": actual,
                 "count": count}
                for (kind, expected, actual), count in sorted(taxonomy.items())
            ],
            "priority_band_counts": dict(sorted(Counter(row["priority_band"] for row in assessments).items())),
            "assessments": assessments,
        },
        "learned_model": {
            "status": "NOT_TRAINED",
            "training_rows": 0,
            "metric_comparison": "NOT_APPLICABLE",
            "reason": "No longitudinal outcomes establish whether a case breaches within 30 days. Training on the injected control labels would reproduce authored rules and leak the target.",
        },
        "decision": {
            "ship": "rule_based_baseline",
            "basis": "The baseline is deterministic and measurable for current breach triage. A learned candidate is ineligible without temporally valid labels, so no comparative performance claim is made.",
            "prediction_limit": "The score orders current control results into a 30-day review queue; it is not a forecast or calibrated breach probability.",
        },
        "mlflow": {
            "package": "mlflow-skinny",
            "version": "3.16.0",
            "backend": "local file store",
            "experiment": EXPERIMENT,
            "registered_model": REGISTERED_MODEL,
            "alias": ALIAS,
            "tracked_and_registered": True,
            "run_identifier": "retained only in ignored local receipt",
        },
        "review_composition": controls["review_composition"],
        "scope_limit": "The measured ranking reuses 72 frozen synthetic cases across all 32 obligations. It does not validate 30-day prediction or real prevalence.",
        "model_calls": 0,
        "model_spend_aud": 0,
    }


def track(report, tracking_root):
    import mlflow
    from mlflow import MlflowClient
    from mlflow.exceptions import MlflowException

    tracking_root.mkdir(parents=True, exist_ok=True)
    store = tracking_root / "store"
    store.mkdir(exist_ok=True)
    tracking_uri = store.as_uri()
    os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
    mlflow.set_tracking_uri(tracking_uri)
    experiment = mlflow.set_experiment(EXPERIMENT)
    metrics = report["baseline"]["metrics_against_frozen_breach_labels"]
    with mlflow.start_run(experiment_id=experiment.experiment_id, run_name=POLICY_VERSION) as run:
        mlflow.log_params({
            "policy_version": POLICY_VERSION,
            "review_horizon_days": report["review_horizon_days"],
            "high_priority_threshold": report["baseline"]["high_priority_threshold"],
            "learned_model_status": report["learned_model"]["status"],
        })
        mlflow.log_metrics({name: float(value) for name, value in metrics.items() if value is not None})
        mlflow.log_artifact(str(POLICY), artifact_path="policy")
        run_id = run.info.run_id
        source = mlflow.get_artifact_uri("policy")
    client = MlflowClient(tracking_uri=tracking_uri)
    try:
        client.create_registered_model(REGISTERED_MODEL)
    except MlflowException as error:
        if "already exists" not in str(error).lower():
            raise
    version = client.create_model_version(
        name=REGISTERED_MODEL,
        source=source,
        run_id=run_id,
        tags={"artifact_type": "deterministic_policy", "compliance_decision": "false"},
    )
    client.set_registered_model_alias(REGISTERED_MODEL, ALIAS, version.version)
    recorded = client.get_run(run_id)
    aliased = client.get_model_version_by_alias(REGISTERED_MODEL, ALIAS)
    if recorded.data.params["policy_version"] != POLICY_VERSION or aliased.run_id != run_id:
        raise ValueError("MLflow tracking or registry readback failed")
    receipt = {
        "tracking_uri": tracking_uri,
        "run_id": run_id,
        "registered_model": REGISTERED_MODEL,
        "version": version.version,
        "alias": ALIAS,
    }
    (tracking_root / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main(check=False):
    sys.addaudithook(deny_network)
    report = evaluate()
    if check:
        if report != json.loads(OUTPUT.read_text()):
            raise ValueError("Risk evaluation differs from committed evidence")
        with tempfile.TemporaryDirectory(prefix="obligationiq-mlflow-") as directory:
            receipt = track(report, Path(directory))
            if not receipt["run_id"] or not receipt["version"]:
                raise ValueError("MLflow local verification receipt is incomplete")
        print("PASS: risk baseline replays; learned model withheld; local MLflow registry read back; network disabled")
    else:
        OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
        track(report, ROOT / ".local/mlflow")
        print(json.dumps({"ship": report["decision"]["ship"],
                          **report["baseline"]["metrics_against_frozen_breach_labels"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    main(parser.parse_args().check)
