# Phase 7 — frozen three-arm evaluation

The evaluation contract, 72 pseudonymous synthetic inputs, isolated labels, eight-point evidence rubric and implementation hashes are frozen before the paid run. The set covers every obligation and includes timing boundaries, business-day and declared-holiday arithmetic, incomplete evidence, cross-regime traps, a point-in-time version gap, near-miss nonbreaches and out-of-order event input. `docs/phase-7-frozen-manifest.json` binds the cases, labels, review decisions, gateway, price table and agent code.

The three arms are:

1. `manual_checklist_surrogate`: a programmatic document-review worksheet. It is not observed human performance, and human latency is unmeasured.
2. `deterministic_rules`: the unchanged Phase 4 engine.
3. `rules_plus_agent`: the same immutable rule status plus retriever, timeline, GPT-5 nano drafter and deterministic critic.

Each arm is scored on breach recall and precision, false-positive rate, exact status accuracy, evidence completeness, citation accuracy and groundedness. Compute latency is measured for all arms; it is not converted into staff time. The agent arm uses one cheap-tier call per case, no strong escalation and a 512-token completion cap. Raw model text and source excerpts remain local; public results retain hashes, usage, costs and critic outcomes.

The eight binary completeness criteria are case identity/synthetic label, status, rationale, gap list, record/source binding, full citation, ordered timeline and review composition. Citation accuracy tests emitted claims rather than rewarding omissions. Groundedness verifies frozen status, gaps and citation binding; agent JSON must preserve fixed fields and introduce no unsupported date or obligation identifier. This is a bounded structured-claim check, not a general factuality guarantee.

Unmeasured: staff hours saved, penalties avoided, customer satisfaction and human reviewer latency. The evaluation is synthetic and does not estimate breach prevalence or production performance.

## Reproduce

```sh
python scripts/evaluate.py --check
python scripts/evaluate_controls.py --check
python scripts/evaluate_risk.py --check
```

`--live` requires the separate live-mode flag, current deployment identity, fresh price pin and a clear ledger. It must not be run as an ordinary reproduction step.
