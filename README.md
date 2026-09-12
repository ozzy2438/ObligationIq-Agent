# ObligationIQ

Independent reference build for electricity compliance evidence in Australia.

**Phase 0 implemented: configuration, guarded model gateway, cost ledger, cache and offline checks. Phase 1 has not started.** No regulatory corpus, customer population, compliance determination or Azure model evaluation exists yet.

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

Default bounds: 4,096 input tokens and 1,024 total output tokens. Oversized requests are rejected. The interface accepts one text message, without tools, images or arbitrary provider parameters. Embedding prices are pinned; embedding execution is deferred.

Before future inference, the Azure adapter checks account region, endpoint, deployment model/version and SKU against the price pin. Pins older than 31 days refuse live dispatch. Local auth uses Entra via Azure CLI, never API keys. The adapter has **not** been exercised against a deployed model.

## Models and documentation

Default: GPT-5 nano. Explicit escalation: GPT-5 mini. Future embeddings: text-embedding-3-small. All are catalog-listed in `australiaeast` with Global Standard. Catalog presence does not prove quota, capacity or successful inference. Global Standard can process outside Australia.

- [Public build brief](docs/build-brief.md), with Section 11 omitted.
- [Updated preflight](docs/preflight-and-delivery-plan.md).
- [Azure inventory and AUD price evidence](docs/azure-resource-inventory.md).
- [ADR-005: routing and costs](docs/adr/ADR-005-model-routing-and-cost-control.md).
- [ADR-006: cloud and local operation](docs/adr/ADR-006-cloud-target-and-local-fallback.md).
- [Limitations](docs/limitations-and-unmeasured-claims.md).

Pilot scope: electricity only; Victoria and NERL/NERR regimes remain separate. Billing recalculation, automated customer communication, disconnection decisions/recommendations and CRM writes are excluded. The future CRM interface is read-only behind an adapter with a mock implementation.
