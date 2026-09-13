# Phase 5 — risk baseline and model decision

Revised 13 September 2026. The shipped component remains a deterministic review-priority policy over version-bound control results. It ranks confirmed breaches first, then evidence gaps and open controls. It cannot change a compliance status and emits neither a probability nor a compliance decision.

## Measured synthetic result

At the fixed high-priority threshold of 90, the 72-case all-obligation evaluation produces TP 31, FP 3, FN 0 and TN 38: 100% recall, 91.18% precision and a 7.32% false-positive rate. The three false positives are inherited from Phase 4: two jurisdiction traps and one OIQ-010 calendar-coverage case classified as a breach. The report includes a per-obligation breakdown and error taxonomy.

This is deterministic triage replay because the policy consumes Phase 4 statuses. It adds no detection performance over the control engine. Evidence-gap and `at_risk` cases remain visible below the breach threshold.

## Model decision

The project still has no longitudinal label showing whether a case breaches within 30 days. Training against authored challenge labels would leak the rules and create a misleading score. The learned candidate therefore remains `NOT_TRAINED`; the baseline is shipped plainly. It is a review queue, not a forecast.

`mlflow-skinny==3.16.0` records and registers the policy in a local file store. Managed MLflow, Databricks registry, remote storage, monitoring and deployment remain absent. The evaluation is synthetic, makes no model call and incurs no model spend.

## Reproduce

```sh
python -m pip install -e '.[risk]'
python scripts/evaluate_risk.py --check
```

[Machine-readable result](phase-5-risk-results.json).
