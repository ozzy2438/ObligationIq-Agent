# ADR-007: Control eligibility and operational review provenance

## Context

Source-content approval establishes that a register record agrees with a pinned authoritative clause. It does not establish that the obligation applies to a particular customer state, jurisdiction or evaluation scenario. The Phase 2 gate therefore admitted no records to controls. Two records have explicit human source review and 30 have owner-authorised agent source review; representing all 32 as human-verified would destroy the audit distinction, while excluding the latter would prevent a bounded independent evaluation.

## Decision

Accepted on 13 September 2026. A record is control-eligible only when its source review is `APPROVED`, its source and reviewed-record SHA-256 bindings are unchanged, and a separate operational review sets `operational_review_status=ELIGIBLE_FOR_EVALUATION`. Operational review has its own method, reviewer, date, basis and bound pre-operational record digest. Any digest mismatch fails closed and requires review again.

The current agent operational assessment is limited to this independent, synthetic, electricity-only evaluation. NERL/NERR records may be applied only to matching NSW synthetic cases; Victorian Code records only to matching Victorian synthetic cases. Each control must still evaluate the record's trigger, customer segment, effective date and evidence. Eligibility does not turn missing facts into compliance and does not authorise operational customer action.

Agent-assessed records are eligible within the evaluation but never set `verified_by_human=true`. Every artefact reporting a compliance result must disclose the source-review composition of the obligations it used: human-verified count/proportion and authorised-agent-reviewed count/proportion. An artefact that cannot produce that disclosure is invalid.

## Consequences

All 32 current records can drive the bounded evaluation once their exact operational-review bindings validate; two are human source-reviewed and 30 are agent source-reviewed. A changed record, source, source decision or operational decision loses eligibility until a new review is recorded. This decision does not claim production legal applicability, all-state implementation equivalence, human verification of agent-reviewed records, or permission to communicate with or act on a customer.
