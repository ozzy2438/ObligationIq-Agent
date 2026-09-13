# Consolidated obligation review

Review date: **12 September 2026**.

**32 APPROVED: 2 explicit human decisions and 30 authorised agent source reviews. 0 PENDING HUMAN REVIEW.**

The owner approved OIQ-025 and explicitly authorised autonomous approval/correction of unambiguous source matches. This supersedes the earlier requirement to wait for individual human decisions. The agent reviews are labelled as agent reviews; only OIQ-024 and OIQ-025 set verified_by_human=true. Approved rows receive their review date in the resolved register and Delta snapshot.

## Scope and evidence

All 30 remaining records were read against the pinned authoritative clauses, including relevant chapeaux, exceptions and nearby provisions. Source content, triggers, actions and timing were checked; string/hash matching alone was not treated as semantic approval. The automated verifier separately re-extracts all 32 parent clauses and checks their source hashes. Human-approved drafts were left unchanged.

APPROVED means source-content agreement for the 12 September 2026 snapshot. It does not certify actual customer facts, every jurisdictional modification, a production control or a regulatory outcome. No unresolved ambiguity remains in the reviewed atomic source requirements; customer/contract applicability, calendars and execution remain separate implementation work. No invented deadline or annual reconfirmation duty was added.

The supplemental [Electricity Industry Act 2000, authorised version 107](https://www.legislation.vic.gov.au/in-force/acts/electricity-industry-act-2000/107), effective 9 September 2026, resolves the 40SG(1)/40SH(1) registration-pathway references used in OIQ-021 and OIQ-022. It is checksum-pinned in [review-sources.json](../data/review-sources.json), retained locally and not embedded. This does not claim completion of all state-specific application-law review.

## Corrections and clarifications

Twenty of the 30 agent-reviewed drafts changed before approval; ten matched without changes. The per-record audit preserves the before/after digest and reason. Material changes include:

- OIQ-001: restored intended residents and the equipment-required date.
- OIQ-002: made the all-conditions exception and surviving information duties explicit.
- OIQ-003/004: specified the relevant medical-form pathway.
- OIQ-005/006/017/018: distinguished reminder provision from document issue while preserving the minimum 15-business-day interval.
- OIQ-009: identified communications under rules 124A and 125.
- OIQ-011–015: removed a generic licensed-retailer label; OIQ-013 now triggers on a plan offer, and OIQ-015 preserves the scoped rule 33 exceptions and affected-customer proviso.
- OIQ-021/022: resolved the Act cross-reference and made trigger/content scope explicit.
- OIQ-026: corrected retailer versus customer election and avoided inventing a full-billing-cycle extension length.
- OIQ-030/031: placed the arrears-on-hold exclusion in the trigger.
- OIQ-032: restored the right of any residential customer requesting a policy copy.

## Decision audit

Each row links to the full source, requirement, reasoning, correction and evidence description. The JSON logs retain the exact reviewed digests: [human decisions](../data/human-reviews.json) and [agent decisions](../data/source-reviews.json). The two human decisions are conversation approvals transcribed by the assistant, not independent agent assertions of human review.

| OIQ ID | Source / clause | Decision | Reviewer type | Verification date |
|---|---|---|---|---|
| [OIQ-001](phase-2-review.md#oiq-001) | nerr 124(1)(a) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-002](phase-2-review.md#oiq-002) | nerr 124(1)(b) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-003](phase-2-review.md#oiq-003) | nerr 124A(1)(a) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-004](phase-2-review.md#oiq-004) | nerr 124A(1)(b) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-005](phase-2-review.md#oiq-005) | nerr 124A(1)(c) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-006](phase-2-review.md#oiq-006) | nerr 124A(1)(d) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-007](phase-2-review.md#oiq-007) | nerr 124A(1)(e) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-008](phase-2-review.md#oiq-008) | nerr 125(2)(a) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-009](phase-2-review.md#oiq-009) | nerr 126(b) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-010](phase-2-review.md#oiq-010) | nerr 126A | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-011](phase-2-review.md#oiq-011) | nerr 72(1)(a) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-012](phase-2-review.md#oiq-012) | nerr 72(1)(b) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-013](phase-2-review.md#oiq-013) | nerr 72(2) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-014](phase-2-review.md#oiq-014) | nerl 46 | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-015](phase-2-review.md#oiq-015) | nerl 50(1)-(2) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-016](phase-2-review.md#oiq-016) | esc 164(1)(a) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-017](phase-2-review.md#oiq-017) | esc 164(1)(c) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-018](phase-2-review.md#oiq-018) | esc 164(1)(d) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-019](phase-2-review.md#oiq-019) | esc 164(1)(e) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-020](phase-2-review.md#oiq-020) | esc 164(1)(b) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-021](phase-2-review.md#oiq-021) | esc 165(1)(a) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-022](phase-2-review.md#oiq-022) | esc 165(1)(b) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-023](phase-2-review.md#oiq-023) | esc 166(2)(a) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-024](phase-2-review.md#oiq-024) | esc 166(2)(b) | APPROVED | Human | 2026-09-12 |
| [OIQ-025](phase-2-review.md#oiq-025) | esc 167(1)(b) | APPROVED | Human | 2026-09-12 |
| [OIQ-026](phase-2-review.md#oiq-026) | esc 125(2) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-027](phase-2-review.md#oiq-027) | esc 128(1)(g), (3)-(5) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-028](phase-2-review.md#oiq-028) | esc 129(2) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-029](phase-2-review.md#oiq-029) | esc 129(3) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-030](phase-2-review.md#oiq-030) | esc 130(5) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-031](phase-2-review.md#oiq-031) | esc 130(6) | APPROVED | Authorised agent | 2026-09-12 |
| [OIQ-032](phase-2-review.md#oiq-032) | esc 138(2) | APPROVED | Authorised agent | 2026-09-12 |

## Validation and remaining project work

The test suite checks stale decisions, reviewer provenance, pending decisions, replay and historical Delta snapshots, alongside the gateway cost controls. The [generated verification](phase-2-verification.json) records counts and source checks. The source-review queue is complete. ADR-007 subsequently added a separate, digest-bound operational assessment for independent synthetic evaluation; production applicability and control execution remain unverified. No Azure deployment or paid model call was made.
