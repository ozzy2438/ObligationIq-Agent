# Phase 7 — frozen four-arm evaluation

The evaluation contract, 72 pseudonymous synthetic inputs, isolated labels, eight-point evidence rubric and implementation hashes are frozen before the paid run. The set covers every obligation and includes timing boundaries, business-day and declared-holiday arithmetic, incomplete evidence, cross-regime traps, a point-in-time version gap, near-miss nonbreaches and out-of-order event input. `docs/phase-7-frozen-manifest.json` binds the cases, labels, review decisions, gateway, price table and agent code.

The four arms are:

1. `manual_checklist_surrogate`: a programmatic document-review worksheet. It is not observed human performance, and human latency is unmeasured.
2. `deterministic_rules`: the unchanged Phase 4 engine.
3. `rules_plus_agent_cheap`: the same immutable rule status plus retriever, timeline, GPT-5 nano drafter and deterministic critic.
4. `rules_plus_agent_strong`: the identical drafter/critic workload routed explicitly to GPT-5 mini with reason `quality_review`.

Each arm is scored on breach recall and precision, false-positive rate, exact status accuracy, evidence completeness, citation accuracy, groundedness and under-evidenced refusal correctness. Compute latency is measured for the local arms and gateway latency for model arms; neither is converted into staff time. Each agent arm uses one call per case with a 512-token completion cap. Raw model text and source excerpts remain local; public results retain hashes, usage, costs and critic outcomes.

The eight binary completeness criteria are case identity/synthetic label, status, rationale, gap list, record/source binding, full citation, ordered timeline and review composition. Citation accuracy tests emitted claims rather than rewarding omissions. Groundedness verifies frozen status, gaps and citation binding; agent JSON must preserve fixed fields and introduce no unsupported date or obligation identifier. This is a bounded structured-claim check, not a general factuality guarantee.

Unmeasured: staff hours saved, penalties avoided, customer satisfaction and human reviewer latency. The evaluation is synthetic and does not estimate breach prevalence or production performance.

## Results

The 72-case run completed on 13 September 2026. Each arm covered all 32 obligations. The checklist surrogate reproduced its authored labels exactly; this is a label-consistency check, not measured human performance. The deterministic and both agent arms shared the rule engine's 31 true positives, 3 false positives, no false negatives and 38 true negatives: recall **1.0000**, precision **0.9118**, false-positive rate **0.0732**, and exact status accuracy **0.9306**. The five retained status/gap errors are analysed in `phase-4-controls.md`; the model did not change or conceal them.

| Arm | Evidence completeness | Citation accuracy | Groundedness | Under-evidenced refusal | Critic acceptance | Mean latency |
|---|---:|---:|---:|---:|---:|---:|
| Checklist surrogate | 0.6250 | 1.0000 | 1.0000 | 1.0000 | — | 0.005 ms local |
| Deterministic rules | 0.7500 | 1.0000 | 0.9306 | 0.2500 | — | 0.009 ms local |
| Rules + GPT-5 nano | 0.8750 | 1.0000 | 0.9028 | 0.2500 | 0.9722 | 3,344.84 ms gateway |
| Rules + GPT-5 mini | 0.8750 | 1.0000 | 0.9306 | 0.2500 | 1.0000 | 4,773.93 ms gateway |

Each model arm made 69 metered requests for 72 cases because three byte-identical requests reused the disk cache. The cheap arm cost **0.005451 AUD**, or **0.0000757083 AUD/case**; the strong arm cost **0.030020 AUD**, or **0.0004169444 AUD/case**. Mini cost 5.51 times as much and its mean metered response latency was 42.7% higher. It improved groundedness and critic acceptance by 2.78 percentage points, while completeness, citation accuracy, refusal correctness and detection stayed unchanged. Keep GPT-5 nano as the default. Reserve mini for an explicit quality review where recovering that groundedness gap matters; deterministic rules retain compliance authority.

Confirmed metered spend was **0.035471 AUD**. The conservative ledger total was **0.039036 AUD**, including **0.003565 AUD** overstated by the historical 429 misclassification. Per-case figures above use confirmed metered spend. Twenty-nine mini and three nano capacity rejections were released at zero cost under ADR-009. A cached replay completed all 144 model-arm case executions with zero additional reservation or spend.

## Reproduce

```sh
python scripts/evaluate.py --check
python scripts/evaluate_controls.py --check
python scripts/evaluate_risk.py --check
```

`--live` requires the separate live-mode flag, both deployment identities, fresh price pins and a clear or policy-recoverable ledger. Ambiguous outcomes are charged at their reservation maximum and retried under ADR-008; more than five in one run or a limit breach halts. Structured 429 capacity rejections release the reservation and use bounded serial retry under ADR-009. `--cache-replay` verifies both model arms with zero additional reservation or spend. Neither command is an ordinary reproduction step.
