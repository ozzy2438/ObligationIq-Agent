# ADR-001: Obligation extraction approach

## Context

Extraction must preserve jurisdiction, instrument version and clause provenance. Only human-verified records can be used by controls.

## Decision

Accepted for candidate preparation: read pinned source clauses, paraphrase requirements into the brief schema, and bind source PDF, extracted parent clause and complete record with separate SHA-256 digests. Label the method `agent_assisted_source_reading`; no Azure or application extraction call is claimed. Store minimum/maximum timing direction and its event anchor explicitly.

Human approval is recorded per exact candidate version; unreviewed candidates and clause-level jurisdiction applicability remain PENDING. Draft import requires false/null verification fields. The Git-tracked human-review log binds explicit user decisions to reviewer, date, draft digest and source digest. The resolved register applies only matching decisions and rejects changed content. The control access function still refuses use pending the remaining phase and jurisdiction gates. Changing a draft flag is not an approval path.

## Consequences

Phase 2 supplies 32 candidates and checks every parent clause against its acquired PDF. These checks establish traceability, not legal correctness or human approval. No full source text or medical data is redistributed in the register. Local Delta retains draft snapshots; Unity Catalog is outstanding. No Phase 3 population is created before the remaining gates are resolved.
