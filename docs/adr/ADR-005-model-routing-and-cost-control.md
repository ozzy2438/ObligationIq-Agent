# ADR-005: Model routing and cost control

## Context

Azure budgets are delayed alerts, while model reasoning, retries, duplicate requests and uncertain responses can consume money before an alert arrives. The project has a 10 AUD ceiling, 6 AUD application limit and 1 AUD UTC-day limit. Routing must follow measured quality and cost rather than model-size assumptions.

## Decision

Accepted and validated on 13 September 2026. GPT-5 nano is the default. GPT-5 mini requires a fixed escalation reason; the measured route uses `quality_review`. Model/version/region/SKU prices, currency, source and retrieval date are pinned. Prices are rounded upward at stored precision and older than 31 days cannot be used. A missing model price hard-stops. Development defaults to `dry_run`; `cached` never falls through to live; `live` needs a separate enable flag.

One private SQLite database stores reservations, response cache, call logs and reconciliation records. `BEGIN IMMEDIATE` serialises admission. Reserve the full configured input/output bounds, including reasoning within completion tokens, at uncached price plus 25% headroom. A success commits actual returned usage and cache atomically; an exact cache hit reserves and costs zero. Unknown or ambiguous prior state fails closed under ADR-008. Structured capacity rejection follows ADR-009.

The Phase 7 comparison used the same 72 synthetic cases and 512-token cap. Nano and mini had equal detection, evidence completeness, citation accuracy and refusal correctness. Mini improved groundedness and critic acceptance by 2.78 percentage points, cost 5.51 times more and added 1.429 seconds to mean metered response latency. Keep nano as default; allow mini only for explicit quality review where that bounded quality difference matters. Neither model decides status.

## Consequences

Confirmed spend was 0.035471 AUD; the conservative total was 0.039036 AUD, including 0.003565 AUD retained overstatement from the pre-ADR-009 429 defect. The limits had ample headroom. The ledger does not control other Azure resources, other clients, tax or invoice pricing. Deleting its database breaks lifetime continuity. Serial admission and low TPM limit throughput, which is accepted for this pilot.
