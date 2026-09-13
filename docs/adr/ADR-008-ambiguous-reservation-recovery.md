# ADR-008: Ambiguous reservation recovery

## Context

The first bounded Phase 7 run returned 22 successful GPT-5 nano responses and then lost a response outcome. The ledger correctly retained a 713 micro-AUD hold, but requiring manual reconciliation for every such event made a low-cost batch unnecessarily fragile. Releasing the hold would understate possible Azure spend.

## Decision

Accepted on 13 September 2026. An ambiguous reservation is settled as committed spend at its full reserved maximum. It is never released or recorded as zero. The same workload is then submitted again under a stable run identifier.

Every settlement writes an `ambiguous_settlement` reconciliation and structured cost-log record. Confirmed token-rated usage and worst-case usage, including these conservative settlements, are reported separately. Recovery continues automatically for up to five ambiguous outcomes per run. A sixth ambiguity halts with its reservation unresolved. Settlement also halts before mutation if it would exceed the daily or lifetime ledger limit.

An interrupted process may recover ambiguous reservations carrying the same run identifier before admitting new work. A still-active `reserved` row remains blocking because the ledger cannot infer that its writer has stopped. Cache hits remain free and require no recovery reservation.

## Consequences

The ledger can overstate cost when Azure did not bill the ambiguous request, and a re-run can be billed twice. It cannot understate the defined worst case. The public cost model must distinguish confirmed successful-response usage from conservative ambiguous settlements. The policy favours bounded continuity over exact invoice attribution; Azure billing remains the eventual external reconciliation source.
