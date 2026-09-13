# ObligationIQ

Independent reference build for electricity compliance evidence in Australia.

**Phases 0–2 implemented:** guarded gateway and cost ledger, ten pinned regulatory PDFs, clause-preserving local corpus, persisted CPU embeddings and a 32-record versioned obligation register. No Azure model evaluation exists yet.

**Phase 2 source review complete:** all 32 records are APPROVED for source-content agreement: two explicit human decisions (OIQ-024/025) and 30 user-authorised agent reviews. Twenty drafts were corrected or clarified before approval. [Consolidated audit](docs/review-summary.md). Agent decisions never set `verified_by_human=true`. The external Delta register is registered in local Unity Catalog OSS, with schema/readback, anonymous-access refusal and restart persistence verified. [Local catalog runbook](docs/local-unity-catalog.md). ADR-007 separately admits all 32 digest-bound records to this independent synthetic evaluation after agent operational review; it does not establish production legal applicability. Every future compliance-result artefact must disclose the 2/32 human versus 30/32 agent source-review composition.

**Phase 3 complete:** 10,000 explicitly synthetic accounts are split equally between two NSW/Victorian distributor footprints. Fourteen comparisons pass: eight AER/ESC account marginals, five exact AER debt-entry bands and the separate entry-debt mean. The build uses 299 complete de-identified Ausgrid household profiles, twelve months of AEMO/BOM context and 18 isolated source-supported challenge cases. Raw and customer-level generated data remain local; only bounded source reductions and truth labels are committed. The joint structure, Victorian use of the NSW shape library and tariff eligibility are stated assumptions. No control result, risk score or Azure model result is claimed. [Method](docs/phase-3-calibration.md) · [Calibration result](docs/population-calibration.json).

> *The synthetic customer population reproduces the published quarterly marginals from the AER Retail Markets Performance Data for hardship participation, average hardship debt, and disconnection rates. The joint structure is generated. Compliance breaches are deliberately injected with known ground truth to permit measurement of detection recall and precision. No real customer data is used anywhere in this project.*

The eventual output is a source-backed evidence pack. Compliance decisions belong to deterministic controls using versioned, human-verified obligations; language models may retrieve, draft and explain evidence.

## Budget

The latest user correction sets the **total project ceiling to 10 AUD**, overriding the pasted 40 AUD instruction. The application defaults to **6 AUD lifetime / 1 AUD per UTC day**, leaving 4 AUD of headroom. Limits are ceilings, not spending targets.

**The SQLite ledger enforces application spending admission; the Azure budget only sends alerts.** Estimated model charges are not an invoice guarantee, tax calculation or control over unrelated Azure resources.

Azure budget: `obligationiq-pilot-aud-10`, scoped to `rg-obligationiq-pilot`, 1 September 2026–31 August 2027. Alerts: 5 / 7.50 / 9 / 10 AUD. The old 3 AUD budget was replaced after verifying the new record. No model deployment was created.

## Run Phase 0

Python 3.11 or newer; local validation used Python 3.14 and CI uses Python 3.12.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test]'
cp .env.example .env  # fresh checkout only; preserve an existing .env
python -m src
pytest
python scripts/check_boundaries.py
```

Installation downloads dependencies. **The subsequent dry-run application and test suite make zero network calls and incur zero model spend.** Tests deny socket connections and use local transport doubles, not operational customer data. Azure SDKs are optional and unnecessary for this path.

Empty template values use safe defaults. `src/config.py` loads strict `KEY=value` entries, supports quotes without interpolation, and applies environment-variable overrides. It validates on import. Cloud identifiers are required only for `live`, which also requires `LLM_ALLOW_LIVE=true`. Errors show key names rather than values. Databricks keys are reserved for a later phase.

## Gateway controls

- Inference is confined to `src/gateway/llm_client.py`; CI rejects SDK imports elsewhere and gateway imports in controls.
- `dry_run` returns an explicit stub, never contacts Azure, and never populates the live response cache.
- `cached` only reads existing responses; a miss raises. Cache keys bind model version, prompt after redaction, bounded parameters, endpoint and deployment. Hits create no reservation.
- `live` requires the separate enable flag, complete Azure configuration and a live-ready redactor. **The default Phase 0 redactor is a stub and refuses live traffic.**
- Paid execution is serial across clients sharing the database. `BEGIN IMMEDIATE` checks UTC-day and lifetime balance before reserving full input/output caps plus 25% headroom. Output includes reasoning tokens.
- Returned token usage settles at pinned AUD rates. Cache insertion, settlement and success logging commit together. Reasoning tokens are included in completion tokens, not added twice.
- Only confirmed pre-dispatch failures release funds. Timeouts, crashes, missing usage and uncertain outcomes retain the hold and block further calls. No automatic expiry restores balance.
- Retries default to zero, apply only to confirmed pre-dispatch failures, and reserve separately. SDK retries are disabled.
- SQLite stores structured usage logs. Raw prompts, credentials and provider exception messages are not logged. Workload and escalation reasons use fixed codes; cache contents remain private.

Default Azure bounds: 4,096 input tokens and 1,024 total output tokens. Oversized requests are rejected. The text interface accepts one message, without tools, images or arbitrary provider parameters. Azure embedding execution is deferred.

## Run Phase 1

See the [corpus runbook](docs/phase-1-corpus.md), [source inventory](data/SOURCES.md), and [generated verification](docs/phase-1-verification.json). Python 3.12 plus the optional `corpus` dependencies are required for PDF extraction and local semantic embeddings. The ordinary Phase 0 dry run still requires no model or corpus download.

Phase 1 explicitly uses a pinned Apache-2.0 MiniLM model locally, enabled only by `LOCAL_EMBEDDING_ENABLED=true`. All inference remains inside `src/gateway/llm_client.py`. Source/model acquisition is a separate download command. Repeated builds reuse the persisted index; changed inputs reuse unchanged embedding cache entries. Local execution creates no Azure charge or paid reservation.

Search defaults to a deterministic lexical baseline; semantic search is explicit and its quality is unmeasured. Every query selects a regime and snapshot date. Core clauses and contextual material remain distinguishable. Full source PDFs, extracted text and model weights stay outside Git; their terms are recorded rather than assumed to be open licences.

Before future inference, the Azure adapter checks account region, endpoint, deployment model/version and SKU against the price pin. Pins older than 31 days refuse live dispatch. Local auth uses Entra via Azure CLI, never API keys. The adapter has **not** been exercised against a deployed model.

## Models and documentation

Azure plan: GPT-5 nano by default, GPT-5 mini on explicit escalation, and future text-embedding-3-small evaluation. All are catalog-listed in `australiaeast` with Global Standard. Catalog presence does not prove quota, capacity or successful inference. Global Standard can process outside Australia. The Phase 1 local embedding choice is documented in ADR-004 and does not claim Foundry execution.

- [Public build brief](docs/build-brief.md), with Section 11 omitted.
- [Updated preflight](docs/preflight-and-delivery-plan.md).
- [Azure inventory and AUD price evidence](docs/azure-resource-inventory.md).
- [ADR-005: routing and costs](docs/adr/ADR-005-model-routing-and-cost-control.md).
- [ADR-006: cloud and local operation](docs/adr/ADR-006-cloud-target-and-local-fallback.md).
- [Limitations](docs/limitations-and-unmeasured-claims.md).

Pilot scope: electricity only; Victoria and NERL/NERR regimes remain separate. Billing recalculation, automated customer communication, disconnection decisions/recommendations and CRM writes are excluded. The future CRM interface is read-only behind an adapter with a mock implementation.
