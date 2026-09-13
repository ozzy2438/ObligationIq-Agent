# Phase 5 — risk baseline and model decision

Status on 13 September 2026: **complete for the independent pilot**. The shipped component is a deterministic review-priority policy over version-bound control results. It places confirmed breaches first, then evidence gaps and open pre-deadline controls. It never changes a compliance status and emits neither a probability nor a compliance decision. [Machine-readable result](phase-5-risk-results.json).

## Model decision

The available evaluation data contains 18 authored current-state challenge cases across six obligations. It has no longitudinal outcome showing whether a non-breach case later breached within 30 days. A gradient-boosted classifier trained on these rows would learn the injection/control construction and leak the target. More features or cross-validation would make that leakage look precise without making it valid.

The learned candidate is therefore `NOT_TRAINED`. This is a data-validity gate, not a failed model experiment, and no comparative model metric is reported. The deterministic baseline is the only defensible component to ship. It orders current work for a 30-day review queue; it is not a forecast of 30-day breach risk.

## Measured synthetic result

At the fixed high-priority threshold of 90, the policy maps a deterministic `breach` to 100, `insufficient_evidence` to 70, `at_risk` to 60, and `compliant` or `not_applicable` to zero. On the isolated Phase 3 cases:

| Metric against current injected breach labels | Result |
|---|---:|
| Cases / obligations | 18 / 6 |
| True positives | 6 |
| False positives | 0 |
| False negatives | 0 |
| True negatives | 12 |
| Recall | 100% |
| Precision | 100% |
| False-positive rate | 0% |

This is current-state triage replay because the baseline consumes Phase 4 statuses. It is not an independent gain over the control engine, a production accuracy estimate, or evidence of predictive performance. Evidence-gap cases remain visible in the separate `evidence_review` band even though they are not classified as confirmed breach.

## Local MLflow evidence

`mlflow-skinny==3.16.0` records the policy version, fixed parameters and evaluation metrics in its local file store. The policy JSON is logged as an artefact, registered as `obligationiq-rule-risk-baseline`, and its new version is assigned the `champion` alias after readback. Run and version identifiers remain in `.local/mlflow/receipt.json`; `.local/` is ignored and rejected by the tracked-file guard.

The registry entry is an operational policy artefact, not a trained statistical model. Managed MLflow, Databricks registry, remote artefact storage, drift monitoring and deployment remain unimplemented.

## Reproduce

```sh
python -m pip install -e '.[risk]'
python scripts/evaluate_risk.py --check
```

The check rebuilds the synthetic control results, compares the committed report, creates a temporary local MLflow store, registers the policy, reads the alias back, blocks sockets and deletes the temporary store. Model calls and model spend are zero.
