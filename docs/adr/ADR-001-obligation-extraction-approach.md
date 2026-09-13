# ADR-001: Obligation extraction approach

## Context

Extraction must preserve jurisdiction, instrument version and clause provenance. Source agreement, human verification and operational evaluation eligibility must remain distinct.

## Decision

Accepted for candidate preparation: read pinned source clauses, paraphrase requirements into the brief schema, and bind source PDF, extracted parent clause and complete record with separate SHA-256 digests. Label the method `agent_assisted_source_reading`; no Azure or application extraction call is claimed. Store minimum/maximum timing direction and its event anchor explicitly.

The owner explicitly authorised autonomous approval and correction when source requirements are unambiguous, superseding the earlier per-record human gate. Preserve human approvals separately from authorised agent source reviews, each bound to reviewer, date, draft digest and source digest. Only explicit human decisions set `verified_by_human=true`. The resolved register adds `review_status` and `verification_method`; approved rows have a verification date. Changed content requires a new matching review. Control access also requires the separate digest-bound operational applicability decision defined by ADR-007.

## Consequences

The register supplies 32 reviewed records and checks every parent clause against its acquired PDF. Hashes establish traceability; review decisions do not establish customer-level legal applicability. Two records carry explicit human source approval and 30 carry authorised agent approval. Local Delta snapshots and local Unity Catalog OSS registration/readback are verified. No full source text or medical data is redistributed in the register.
