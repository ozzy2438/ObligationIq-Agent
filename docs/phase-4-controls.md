# Phase 4 — deterministic control engine

Revised 13 September 2026. All 32 eligible obligations retain a distinct, pure control callable. The evaluation now uses the frozen 72-case set shared with Phase 7: two cases for every obligation plus timing boundaries, a declared holiday fixture, partial evidence, cross-regime traps, a point-in-time version gap and out-of-order input events. Inputs are in `data/evaluation-cases.json`; labels remain isolated in `data/ground_truth/`.

## Measured synthetic result

| Metric | Result |
|---|---:|
| Cases / obligations | 72 / 32 |
| True positives / false positives | 31 / 3 |
| False negatives / true negatives | 0 / 38 |
| Breach recall | 100% |
| Breach precision | 91.18% |
| False-positive rate | 7.32% |
| Exact status accuracy | 93.06% |
| Version/citation binding | 100% |

The five retained errors are findings. OIQ-002 and OIQ-021 do not reject a mismatched case regime and produce false breaches. Two OIQ-010 cases use a business-day deadline beyond the supplied calendar coverage; the engine returns `at_risk` or `breach` instead of `insufficient_evidence`. OIQ-028 applies the current record to a trigger predating that version and returns `compliant` instead of `insufficient_evidence`. No control was changed after the challenge labels were frozen. The machine-readable report includes every case, a per-obligation breakdown and the error taxonomy.

## Boundary and limits

Each result records the applied obligation/source digests, source version, clause, effective interval, review provenance, evaluation date and evidence gaps. Controls perform no I/O or inference. The declared holiday fixture tests arithmetic but is synthetic; a production holiday service is absent. The 72 cases are authored edge cases and do not estimate prevalence, legal completeness or production accuracy. Two of 32 source reviews were human-verified and 30 were agent-reviewed.

## Reproduce

```sh
python scripts/evaluate.py --check
python scripts/evaluate_controls.py --check
python scripts/check_boundaries.py
pytest
```

[Machine-readable result](phase-4-control-results.json).
