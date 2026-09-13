# ObligationIQ

Independent reference build for electricity compliance evidence in Australia.

**Phases 0–6 implemented; Phase 7 frozen for evaluation:** guarded gateway and cost ledger, ten pinned regulatory PDFs, clause-preserving local corpus, persisted CPU embeddings, a 32-record versioned obligation register, a calibrated synthetic population, deterministic controls, explainable risk triage and a locally verified evidence-agent/MCP pipeline. The 72-case evaluation contract is frozen; no Azure model inference has run at this status.

**Phase 2 source review complete:** all 32 records are APPROVED for source-content agreement: two explicit human decisions (OIQ-024/025) and 30 user-authorised agent reviews. Twenty drafts were corrected or clarified before approval. [Consolidated audit](docs/review-summary.md). Agent decisions never set `verified_by_human=true`. The external Delta register is registered in local Unity Catalog OSS, with schema/readback, anonymous-access refusal and restart persistence verified. [Local catalog runbook](docs/local-unity-catalog.md). ADR-007 separately admits all 32 digest-bound records to this independent synthetic evaluation after agent operational review; it does not establish production legal applicability. Every future compliance-result artefact must disclose the 2/32 human versus 30/32 agent source-review composition.

**Phase 3 complete:** 10,000 explicitly synthetic accounts are split equally between two NSW/Victorian distributor footprints. Fourteen comparisons pass: eight AER/ESC account marginals, five exact AER debt-entry bands and the separate entry-debt mean. The build uses 299 complete de-identified Ausgrid household profiles, twelve months of AEMO/BOM context and 18 isolated source-supported challenge cases. Raw and customer-level generated data remain local; only bounded source reductions and truth labels are committed. The joint structure, Victorian use of the NSW shape library and tariff eligibility are stated assumptions. No risk score or Azure model result is claimed. [Method](docs/phase-3-calibration.md) · [Calibration result](docs/population-calibration.json).

> *The synthetic customer population reproduces the published quarterly marginals from the AER Retail Markets Performance Data for hardship participation, average hardship debt, and disconnection rates. The joint structure is generated. Compliance breaches are deliberately injected with known ground truth to permit measurement of detection recall and precision. No real customer data is used anywhere in this project.*

**Phase 4 revised:** 32/32 eligible obligations have a version-bound pure control callable. On 72 frozen hard cases spanning all 32 obligations, breach recall is 100%, precision 91.18%, false-positive rate 7.32% and exact status accuracy 93.06%. Five errors remain published across jurisdiction, calendar coverage and point-in-time cases; the controls were not retuned. [Control design and limits](docs/phase-4-controls.md) · [Measured result](docs/phase-4-control-results.json).

**Phase 5 revised:** the deterministic review-priority policy inherits Phase 4's 31 true positives and three false positives: 100% recall, 91.18% precision and 7.32% FPR. A learned classifier remains ineligible because there are no longitudinal 30-day outcome labels. The score is not a forecast, probability or compliance decision. Local MLflow tracking and registration are verified. [Decision and limits](docs/phase-5-risk.md) · [Measured result](docs/phase-5-risk-results.json).

**Phase 6 complete:** the local retriever, timeline builder, drafter and critic produce digest-bound evidence packs through one official-SDK MCP tool. A flagged OIQ-024 case is correctly cited and an under-evidenced case abstains with the `deregistration_event` gap. The active gateway boundary excludes supplied name/address/NMI values and refuses nonconforming live payloads. This is a two-case acceptance check for one obligation; no model was called. [Agent/MCP design and limits](docs/phase-6-agents-and-mcp.md) · [Acceptance result](docs/phase-6-agent-results.json).

The eventual output is a source-backed evidence pack. Compliance decisions belong to deterministic controls using versioned, review-bound obligations; language models may retrieve, draft and explain evidence and cannot override status.

## Budget

The latest user correction sets the **total project ceiling to 10 AUD**, overriding the pasted 40 AUD instruction. The application defaults to **6 AUD lifetime / 1 AUD per UTC day**, leaving 4 AUD of headroom. Limits are ceilings, not spending targets.

**The SQLite ledger enforces application spending admission; the Azure budget only sends alerts.** Estimated model charges are not an invoice guarantee, tax calculation or control over unrelated Azure resources.

Azure budget: `obligationiq-pilot-aud-10`, scoped to `rg-obligationiq-pilot`, 1 September 2026–31 August 2027. Alerts: 5 / 7.50 / 9 / 10 AUD. The old 3 AUD budget was replaced. One GPT-5 nano GlobalStandard deployment exists for the bounded Phase 7 run; its existence is not evidence of inference or an Azure-deployed application.

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
- `live` requires the separate enable flag, complete Azure configuration and the active structured PII boundary. Free-form prompts are never live-ready; the agent envelope excludes customer name, address and NMI before dispatch.
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

Before inference, the Azure adapter checks account region, endpoint, deployment model/version and SKU against the price pin. Pins older than 31 days refuse live dispatch. Local auth uses Entra via Azure CLI, never API keys. At this status the adapter has not sent an inference request.

## Models and documentation

Azure plan: GPT-5 nano by default and GPT-5 mini only on explicit escalation. The current AUD Retail Prices API rounds the embedding meter to zero at its displayed precision, so Azure embedding is unpinned and blocked. Global Standard can process outside Australia. The Phase 1 local embedding choice is documented in ADR-004 and does not claim Foundry execution.

- [Public build brief](docs/build-brief.md), with Section 11 omitted.
- [Updated preflight](docs/preflight-and-delivery-plan.md).
- [Azure inventory and AUD price evidence](docs/azure-resource-inventory.md).
- [ADR-005: routing and costs](docs/adr/ADR-005-model-routing-and-cost-control.md).
- [ADR-006: cloud and local operation](docs/adr/ADR-006-cloud-target-and-local-fallback.md).
- [Limitations](docs/limitations-and-unmeasured-claims.md).

Pilot scope: electricity only; Victoria and NERL/NERR regimes remain separate. Billing recalculation, automated customer communication, disconnection decisions/recommendations and CRM writes are excluded. The future CRM interface is read-only behind an adapter with a mock implementation.
