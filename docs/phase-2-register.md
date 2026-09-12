# Phase 2 — draft obligation register

Status: **prepared for human review, not complete**. Snapshot: 12 September 2026.

The [review pack](phase-2-review.md) contains 32 candidates across life support and hardship/payment difficulty, covering NERL/NERR and Victoria. All have `verified_by_human=false` and a null verification date. Phase 3 has not started.

## Implemented

`data/obligation-candidates.json` contains every brief schema field, plus timing direction and anchor, physical PDF page range, source and clause SHA-256 digests, a complete-record digest, and explicit outstanding checks. Candidate text is an agent-assisted paraphrase of acquired sources. No application model extraction call, Azure inference or human legal verification is claimed.

`src/register/obligations.py` validates the draft contract against the pinned source manifest. A changed source, stale record digest, missing clause anchor or ambiguous timing fails. Draft imports cannot assert human approval by changing a flag. `for_controls()` refuses every candidate until a separate human-attestation workflow and jurisdiction review are implemented. Direct Python access to a file is not a security boundary; future control consumers must use the register contract.

Optional delta-rs and PyArrow dependencies persist full structured records in local Delta Lake at `.local/register/obligations`. Identical input produces no write; changed content produces a new snapshot version. A real Delta test verifies version 0 is still readable after a revision. This is a single-writer local build. Keep the transaction log and data files; no vacuum or cleanup policy has been applied. Delta history is not tamper-proof storage, human approval or Unity Catalog governance.

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
python scripts/verify_register.py
```

Dependency installation and source acquisition use the network. The subsequent verification denies socket connections, runs no model and checks all 32 records against re-extracted parent clauses and source hashes. The [generated report](phase-2-verification.json) records local Delta version 0 and an unchanged repeat. Automated parent-clause matching does **not** prove semantic correctness of a subclause or legal applicability. It does not fulfil human verification.

## Material findings for review

- NERR 124A and Victorian clause 164 set minimum 50-day confirmation windows, minimum 15-day reminder intervals and minimum 25-day extensions, in business days. Treating these as maximum response deadlines would invert the protection. Business-day calendars and counting conventions remain unimplemented.
- Victorian clause 129(2) uses arrears **greater than AUD 55 including GST** and a 21-business-day contact period. Clause 129(3) gives at least six business days for consideration. These have different timing directions.
- Current Victorian clause 125(2) requires at least **three** of four standard-assistance options. The clause 128 initial six-month assistance period is a minimum, not a maximum payment-plan term.
- Current Victorian clause 163 refers to the Electricity Industry Act for registration duties. A NERR five-day information deadline cannot simply be transplanted into that Code clause. No such transplanted candidate is included. Candidates from clause 165 explicitly retain their Act registration-pathway dependency; those Act provisions still require acquisition and applicability review.
- No mandatory annual medical reconfirmation obligation has been established from the selected provisions. Optional requests to reconfirm are not evidence of an annual duty. No annual breach control was invented.
- Deregistration notification and recordkeeping candidates concern completed events; they never determine permission to deregister or disconnect. Lawful-pathway assessment remains a prerequisite.

## Outstanding Phase 2 gates

1. Human review of **each** candidate: content, definitions, exceptions, evidence sufficiency and applicable jurisdiction. Record reviewer identity, date and the exact approved record digest in a controlled attestation workflow. No approvals are supplied by the agent.
2. Resolve jurisdictional application instruments and Victorian Act dependencies; add sources before claiming those dependencies were verified. The SA consolidated National Law is not proof of identical state implementation. Snapshot coverage is not clause-level commencement history.
3. Decide and validate Unity Catalog governance, or explicitly accept the local fallback as a scope change. No Databricks resource has been created under the 10 AUD ceiling, and local Delta does not satisfy the brief's Unity Catalog requirement.

Until these gates are resolved, the register is a reviewable draft. There is no operational compliance output, synthetic population, risk model or agent/MCP implementation. This deliberately stops before Phase 3.
