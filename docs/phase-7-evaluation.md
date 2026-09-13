# Phase 7 — frozen three-arm evaluation

The evaluation contract, 72 pseudonymous synthetic inputs, isolated labels, eight-point evidence rubric and implementation hashes are frozen before the paid run. The set covers every obligation and includes timing boundaries, business-day and declared-holiday arithmetic, incomplete evidence, cross-regime traps, a point-in-time version gap, near-miss nonbreaches and out-of-order event input. `docs/phase-7-frozen-manifest.json` binds the cases, labels, review decisions, gateway, price table and agent code.

The four arms are:

1. `manual_checklist_surrogate`: a programmatic document-review worksheet. It is not observed human performance, and human latency is unmeasured.
2. `deterministic_rules`: the unchanged Phase 4 engine.
3. `rules_plus_agent_cheap`: the same immutable rule status plus retriever, timeline, GPT-5 nano drafter and deterministic critic.
4. `rules_plus_agent_strong`: the identical drafter/critic workload routed explicitly to GPT-5 mini with reason `quality_review`.

Each arm is scored on breach recall and precision, false-positive rate, exact status accuracy, evidence completeness, citation accuracy, groundedness and under-evidenced refusal correctness. Compute latency is measured for the local arms and gateway latency for model arms; neither is converted into staff time. Each agent arm uses one call per case with a 512-token completion cap. Raw model text and source excerpts remain local; public results retain hashes, usage, costs and critic outcomes.

The eight binary completeness criteria are case identity/synthetic label, status, rationale, gap list, record/source binding, full citation, ordered timeline and review composition. Citation accuracy tests emitted claims rather than rewarding omissions. Groundedness verifies frozen status, gaps and citation binding; agent JSON must preserve fixed fields and introduce no unsupported date or obligation identifier. This is a bounded structured-claim check, not a general factuality guarantee.

Unmeasured: staff hours saved, penalties avoided, customer satisfaction and human reviewer latency. The evaluation is synthetic and does not estimate breach prevalence or production performance.

## Reproduce

```sh
python scripts/evaluate.py --check
python scripts/evaluate_controls.py --check
python scripts/evaluate_risk.py --check
```

`--live` requires the separate live-mode flag, both deployment identities, fresh price pins and a clear or policy-recoverable ledger. Ambiguous outcomes are charged at their reservation maximum and retried under ADR-008; more than five in one run or a limit breach halts. `--cache-replay` verifies both model arms with zero additional reservation or spend. Neither command is an ordinary reproduction step.
