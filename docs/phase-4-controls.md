# Phase 4 — deterministic control engine

Status on 13 September 2026: **complete for the independent pilot**. Every one of the 32 eligible obligation records has a distinct pure control callable. The common evaluator applies source-required evidence, timing direction, deadline unit, supplied business calendar and point-in-time version interval without network or model access. [Machine-readable results](phase-4-control-results.json) bind every result to the exact register and population fingerprints.

## Measured synthetic result

The isolated Phase 3 set contains 18 cases across six obligations: OIQ-002, OIQ-023, OIQ-024, OIQ-028, OIQ-030 and OIQ-032. Each obligation contributes one compliant case, one breach and one deliberately incomplete evidence case.

| Metric | Result |
|---|---:|
| Breach true positives | 6 |
| False positives | 0 |
| False negatives | 0 |
| True negatives | 12 |
| Detection recall | 100% |
| Detection precision | 100% |
| False-positive rate | 0% |
| Exact three-status accuracy | 100% |
| Insufficient-evidence recall | 100% |
| Version/citation binding | 100% |

These are exact results on seeded synthetic injections designed from the same reviewed obligations as the controls. They prove replay and control behaviour against the held labels; they do not estimate production accuracy or breach prevalence. Callable coverage is 32/32, while benchmark coverage is six of 32 obligations.

## Decision boundary

`ControlResult` records the applied obligation digest, source digest/version, clause reference, effective interval, review method, evaluation date and evidence gaps. A missing trigger, action state, required evidence item or bounded business calendar returns `insufficient_evidence`. A date outside the exact obligation version returns `not_applicable`. `at_risk` is available for an incomplete action whose source deadline has not yet passed.

Business-day arithmetic excludes weekends and the supplied calendar's holidays. The synthetic benchmark supplies a bounded weekdays-only calendar for an interval deliberately free of intervening NSW/Victorian public holidays. A production holiday service is not implemented. Month deadlines use calendar-month arithmetic.

The 32 underlying records comprise two human-verified source reviews (6.25%) and 30 authorised-agent source reviews (93.75%). All 32 also have separate agent operational-applicability review for this independent synthetic evaluation. No agent-reviewed record is presented as human-verified.

## Reproduce

```sh
python scripts/build_population.py --check
python scripts/evaluate_controls.py --check
python scripts/check_boundaries.py
pytest
```

The evaluation harness is the only layer that reads the isolated labels. Controls and agents cannot import evaluation/build surfaces or contain a `ground_truth` reference; CI fails on either. The engine has no I/O and no LLM import. Model calls and spend are zero.
