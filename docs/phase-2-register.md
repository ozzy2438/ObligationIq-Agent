# Phase 2 — draft obligation register

Status: **Phase 2 complete using the documented local Unity Catalog OSS fallback**. Snapshot: 12 September 2026.

The [review pack](phase-2-review.md) contains 32 source-reviewed records across both families and regimes. OIQ-024 and OIQ-025 have explicit human approvals. The owner subsequently authorised autonomous source review; the other 30 were approved by the agent after comparison and correction where needed. See the [consolidated audit](review-summary.md). Drafts remain versioned and review decisions bind exact content; the resolved register and Delta snapshot carry status, reviewer type and verification date. Phase 3 has not started.

## Implemented

`data/obligation-candidates.json` contains every brief schema field, plus timing direction and anchor, physical PDF page range, source and clause SHA-256 digests, a complete-record digest, and explicit outstanding checks. Candidate text is an agent-assisted paraphrase of acquired sources. No application model extraction call or Azure inference is claimed. Human content decisions are recorded only where the owner explicitly supplied them.

`src/register/obligations.py` validates the draft contract against the pinned source manifest. A changed source, stale record digest, missing clause anchor or ambiguous timing fails. Draft imports cannot assert human approval by changing a flag. `reviewed_records()` applies explicit, version-bound decisions from the human and authorised-agent review logs. Unknown or duplicate decisions and changed approved content fail closed. The logs distinguish user decisions from authorised agent judgments; they are not cryptographic identity verification. ADR-007 adds a separate operational review bound to every approved record and source digest. `for_controls()` admits the 32 current records only to the independent synthetic evaluation, with NERL/NERR limited to matching NSW cases and the Victorian Code limited to matching Victorian cases. Direct Python access to a file is not a security boundary; control consumers must use the register contract and report the review composition.

Optional delta-rs and PyArrow dependencies persist full structured records in local Delta Lake at `.local/register/obligations`. Identical input produces no write; changed content produces a new snapshot version. A real Delta test verifies version 0 is still readable after a revision. This is a single-writer local build. Schema evolution adds review provenance without deleting historical snapshots. Keep the transaction log and data files; no vacuum or cleanup policy has been applied. Delta history is not tamper-proof storage, human approval or Unity Catalog governance.

## Reproduce

Use Python 3.12 for the full optional stack; the base dry run remains lightweight.

```sh
python -m pip install -e '.[test,register]'
python -m src.register.obligations validate
python -m src.register.obligations materialize
python scripts/render_register_review.py
pytest
python scripts/check_boundaries.py
```

For a trace check against actual PDFs, acquire the pinned sources using the Phase 1 instructions, install the optional `corpus` dependencies, then run:

```sh
python scripts/acquire_corpus.py --review-sources
python scripts/verify_register.py
```

Dependency installation and source acquisition use the network. The subsequent verification denies socket connections, runs no model and checks all 32 records against re-extracted parent clauses and source hashes. The [generated report](phase-2-verification.json) records the latest local Delta version and an unchanged repeat. Version 0 retains the original unapproved snapshot. Automated parent-clause matching does **not** prove semantic correctness of a subclause or legal applicability. It does not fulfil human verification.

## Material findings for review

- NERR 124A and Victorian clause 164 set minimum 50-day confirmation windows, minimum 15-day reminder intervals and minimum 25-day extensions, in business days. Treating these as maximum response deadlines would invert the protection. Business-day calendars and counting conventions remain unimplemented.
- Victorian clause 129(2) uses arrears **greater than AUD 55 including GST** and a 21-business-day contact period. Clause 129(3) gives at least six business days for consideration. These have different timing directions.
- Current Victorian clause 125(2) requires at least **three** of four standard-assistance options. The clause 128 initial six-month assistance period is a minimum, not a maximum payment-plan term.
- Current Victorian clause 163 refers to the Electricity Industry Act for registration duties. A NERR five-day information deadline cannot simply be transplanted into that Code clause. No such transplanted candidate is included. Candidates from clause 165 explicitly retain their Act registration-pathway dependency; those Act provisions have now been acquired and checked in authorised version 107; concrete customer applicability still requires actual facts.
- No mandatory annual medical reconfirmation obligation has been established from the selected provisions. Optional requests to reconfirm are not evidence of an annual duty. No annual breach control was invented.
- Deregistration notification and recordkeeping candidates concern completed events; they never determine permission to deregister or disconnect. Lawful-pathway assessment remains a prerequisite.

## Completion and downstream gates

1. Source-content review is complete under the owner's revised authorisation. Two human approvals and 30 authorised agent approvals are separately labelled. Only explicit human decisions set `verified_by_human=true`; both review methods can set `review_status=APPROVED` and `verification_date`. Agent judgments are not represented as human review.
2. ADR-007 records the agent operational applicability assessment for this independent NSW/Victoria synthetic evaluation. The specific Victorian Act dependencies for OIQ-021/022 are verified against a pinned supplemental source. The SA consolidated National Law is not proof of identical state implementation. Snapshot coverage is not clause-level commencement history, and production customer use remains outside scope.
3. Actual Unity Catalog OSS now registers and resolves the external Delta table. Authorization, schema fidelity, repeat reads and restart persistence are verified in the [local catalog runbook](local-unity-catalog.md). Section 3 of the brief already permits an explicit local fallback when cloud resources are unavailable. No managed Databricks, row-level security or automatic lineage is claimed.

The Phase 2 source-trace and versioned-register acceptance criteria are met, with the owner-authorised review amendment and explicit local catalog fallback. Operational applicability remains a downstream prerequisite to customer-level controls, not a claim established by source approval. Phase 3 calibration/population work can now begin; no operational compliance output, risk model or agent/MCP implementation exists.
