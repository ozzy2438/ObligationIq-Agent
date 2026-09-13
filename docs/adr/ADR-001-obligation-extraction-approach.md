# ADR-001: Obligation extraction approach

## Context

Extraction must preserve jurisdiction, instrument version and clause provenance. Only human-verified records can be used by controls.

## Decision

Accepted for candidate preparation: read pinned source clauses, paraphrase requirements into the brief schema, and bind source PDF, extracted parent clause and complete record with separate SHA-256 digests. Label the method `agent_assisted_source_reading`; no Azure or application extraction call is claimed. Store minimum/maximum timing direction and its event anchor explicitly.

The owner explicitly authorised autonomous approval and correction when source requirements are unambiguous, superseding the earlier per-record human gate. Preserve human approvals separately from authorised agent source reviews, each bound to reviewer, date, draft digest and source digest. Only explicit human decisions set `verified_by_human=true`. The resolved register adds `review_status` and `verification_method`; approved rows have a verification date. Changed content requires a new matching review. The control access function still refuses execution before operational applicability and the Control Engine exist.

## Consequences

Phase 2 supplies 32 candidates and checks every parent clause against its acquired PDF. Hash checks establish traceability; explicit semantic review decisions are recorded separately and do not establish customer-level legal applicability. No full source text or medical data is redistributed in the register. Local Delta retains draft snapshots; Unity Catalog is outstanding. No Phase 3 population is created before the remaining gates are resolved.
