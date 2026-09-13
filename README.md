# ObligationIQ

ObligationIQ is an independent reference build for producing cited electricity-compliance evidence packs from versioned Australian regulatory obligations and synthetic customer state. Deterministic controls own compliance status. Language models may retrieve, draft and critique supporting evidence; they cannot change the status.

The pilot is complete through Phase 8. It is local-first, evaluation-only and not a production compliance service.

## What was built

- Ten checksum-pinned authoritative regulatory PDFs and a clause-preserving local retrieval corpus.
- A 32-record versioned obligation register with separate source and operational reviews, local Delta snapshots and local Unity Catalog OSS registration.
- A reproducible 10,000-account synthetic population plus a separately calibrated 34,843-record debt-entry cohort.
- One pure, point-in-time control callable for each eligible obligation. Missing evidence cannot become compliant.
- A deterministic review-priority baseline tracked and registered in local MLflow. No learned model was trained because no defensible longitudinal target exists.
- Retriever, timeline builder, drafter and critic components behind one read-only MCP tool and one model gateway.
- An active model-data boundary that excludes customer name, address and NMI from a fixed live schema.
- An atomic SQLite cost ledger, disk cache, pinned AUD prices and measured GPT-5 nano/mini routing.

Two obligations have explicit human source approval; 30 have owner-authorised agent review. Every compliance-result artefact reports this **6.25% human / 93.75% agent** composition. Agent review is never represented as human verification.

## Measured result

The frozen challenge set contains 72 synthetic cases across all 32 obligations, including timing boundaries, declared holidays, partial evidence, jurisdiction traps, point-in-time changes, near misses and out-of-order events.

| Arm | Recall | Precision | FPR | Exact status | Evidence completeness | Citation accuracy | Groundedness |
|---|---:|---:|---:|---:|---:|---:|---:|
| Checklist surrogate | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.6250 | 1.0000 | 1.0000 |
| Deterministic rules | 1.0000 | 0.9118 | 0.0732 | 0.9306 | 0.7500 | 1.0000 | 0.9306 |
| Rules + GPT-5 nano | 1.0000 | 0.9118 | 0.0732 | 0.9306 | 0.8750 | 1.0000 | 0.9028 |
| Rules + GPT-5 mini | 1.0000 | 0.9118 | 0.0732 | 0.9306 | 0.8750 | 1.0000 | 0.9306 |

The checklist is a programmatic label-consistency surrogate, not observed human performance. The rule/agent arms retained 31 true positives, 3 false positives, no false negatives and 38 true negatives. Five hard-case status/gap errors remain published; controls were not tuned to erase them.

Nano cost **0.005451 AUD** across 72 cases with 3.345 s mean metered response latency. Mini cost **0.030020 AUD** with 4.774 s mean latency. Mini improved groundedness and critic acceptance by 2.78 percentage points but did not improve detection, completeness, citations or refusal correctness. Nano therefore remains the default; mini requires explicit `quality_review` escalation.

Confirmed metered spend was **0.035471 AUD**. The conservative ledger total was **0.039036 AUD**, including **0.003565 AUD** retained overstatement from five Azure 429s misclassified before ADR-009. The ledger now releases a complete `rate_limit_exceeded` rejection because no inference ran; response-less failures remain conservatively ambiguous. Held balance is zero.

## Architecture and evidence

- [Solution architecture](docs/solution-architecture.md)
- [Phase 7 evaluation and routing result](docs/phase-7-evaluation.md)
- [Control error analysis](docs/phase-4-controls.md)
- [Cost model](docs/cost-model.md)
- [Security control matrix](docs/security-control-matrix.md) and [STRIDE threat model](docs/stride-threat-model.md)
- [NFRs and failure runbook](docs/non-functional-requirements.md)
- [Limitations and unmeasured claims](docs/limitations-and-unmeasured-claims.md)
- [Reproduction guide](docs/reproduction.md)
- [Source inventory](data/SOURCES.md) and [review audit](docs/review-summary.md)
- [ADR set](docs/adr/ADR-001-obligation-extraction-approach.md)

## Reproduce the public evidence

Python 3.11 or newer is required. CI uses Python 3.12.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[test,register,risk,mcp]'
cp .env.example .env
python scripts/check_boundaries.py
python scripts/build_population.py --check
python scripts/evaluate_controls.py --check
python scripts/evaluate_risk.py --check
python scripts/evaluate_agents.py --check
python scripts/evaluate.py --check
python scripts/generate_cost_model.py --check --from-results
pytest
python -m src
```

Keep `LLM_MODE=dry_run` and `LLM_ALLOW_LIVE=false`. These checks make no model call. Source/model acquisition and local corpus rebuilding are separate explicit steps in the [full reproduction guide](docs/reproduction.md). Raw PDFs, extracted corpus, vectors, Delta tables, MLflow store, model cache, ledger and raw model outputs remain outside Git.

## Gateway and budget controls

All model calls are confined to `src/gateway/llm_client.py`; CI rejects LLM SDK imports elsewhere and any control/agent access to ground truth. `dry_run` is offline, `cached` refuses a miss, and `live` needs a separate enable flag, valid Entra authentication, a fresh price pin and exact ARM deployment identity.

The SQLite ledger, rather than the Azure budget, enforces admission. Limits are 1 AUD per UTC day and 6 AUD over the application lifetime under a 10 AUD project ceiling. It reserves the maximum bounded request plus 25%, commits returned usage, and gives exact cache hits zero incremental cost. Azure budget `obligationiq-pilot-aud-10` is only an alert.

Azure contains an S0 OpenAI account and GPT-5 nano/mini Global Standard deployments in an Australia East account. Global Standard may process outside Australia. The application, data stores, MLflow, Unity Catalog OSS and MCP server run locally. No Foundry project, managed Databricks, AI Search, storage account, API Management, CRM integration or production endpoint was deployed.

## Scope

Electricity only. Victoria and NERL/NERR stay separate. No real customer data, automated communication, billing recalculation, disconnection recommendation/action, CRM write, staff-hours claim, penalties-avoided claim, customer-satisfaction claim or ROI claim is included.
