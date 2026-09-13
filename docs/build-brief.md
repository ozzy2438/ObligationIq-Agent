# ObligationIQ — Agent Build Brief

**Continuous compliance evidence for Australian energy retailers.**

> You are building a complete, defensible, production-shaped reference system. Read this entire document before writing a single line of code. Do not skip phases. Do not invent facts. When a source cannot be verified, say so in writing rather than filling the gap with plausible text.

---

## 0. What this system is

One sentence, and every design decision must serve it:

> **A system that does not tell you what a regulatory obligation says — it tells you whether you are currently meeting it, and hands you the evidence to prove it.**

Three questions kept deliberately separate, because most tools on the market collapse them:

| # | Question | Answered by | LLM involved? |
|---|---|---|---|
| 1 | What is the obligation? | Obligation Register (structured, versioned, human-verified) | Assisted extraction only |
| 2 | Are we compliant right now? | Control Engine (deterministic SQL/Python) | **Never** |
| 3 | Where is the proof? | Agent layer (retrieval, timeline, drafting, critique) | Yes |

**The single most important architectural rule in this project: the LLM never decides compliance status.** Breach detection is deterministic and reproducible. The LLM assembles, cites and explains evidence. If you find yourself writing a prompt that asks a model "is this customer compliant?", stop — that logic belongs in the Control Engine.

---

## 1. Non-negotiable principles

These override convenience, elegance, and speed. Violating any of them makes the entire deliverable worthless.

1. **No fabricated metrics.** Every number published in any artefact must trace to a computation in this repo or a cited public source. No "40% faster", no "saves X hours", no "prevents $Y in penalties" unless it was measured here.
2. **No unverified claims about real companies.** Do not assert what any named retailer does, lacks, or does badly. The regulatory obligations are public and citable; a specific company's internal state is not.
3. **Synthetic data is labelled synthetic, everywhere.** In the README, in the docs, in the notebooks, in the dashboard footer.
4. **Deterministic before probabilistic.** Every workload gets a rule-based baseline. If the ML model or the agent does not beat the baseline, publish that result and recommend the baseline. A negative result honestly reported is a stronger portfolio signal than an unverifiable positive one.
5. **Refuse rather than guess.** If evidence is insufficient, the agent outputs `insufficient_evidence` with a list of what is missing. It does not produce a confident narrative from thin data.
6. **Point-in-time correctness.** Regulation changes. Every compliance assessment must record which version of which obligation was applied, and on what date.
7. **Write the limitations document as you go**, not at the end. It is a first-class deliverable.

---

## 2. Scope

### In scope (pilot)

Two obligation families, both on the AER's published compliance and enforcement priorities, both date-triggered (therefore deterministically checkable), both with fully public source documents:

- **Life support obligations** — registration, confirmation, re-confirmation cycles, retailer↔distributor notification, de-registration protections.
- **Hardship / payment difficulty obligations** — entitlement assessment, plan establishment, minimum-standard compliance, protections while on a plan.

Two jurisdictional regimes must be modelled separately, because they genuinely differ:

- **NERL/NERR jurisdictions** (NSW, QLD, SA, ACT, TAS) under the AER
- **Victoria** under the Essential Services Commission's Energy Retail Code of Practice and Payment Difficulty Framework

> Correctly modelling that Victoria is a separate regime is a deliberate credibility signal. Do not flatten it.

### Explicitly out of scope — state this in the README

- Bill recalculation or any billing-engine integration
- Automated customer communication (the system drafts; a human sends)
- Any disconnection decision or recommendation
- Gas obligations (electricity only in the pilot)
- Writing to any CRM. **CRM access is read-only, behind an adapter interface, with a mock implementation.** Do not name or integrate a specific commercial CRM product.

---

## 3. Azure configuration contract

**The user will supply Azure credentials and resource identifiers at the start of the build.** Do not provision anything, do not guess resource names, do not hardcode endpoints, and do not proceed past Phase 0 without them.

Request exactly this set, in one message, before starting:

```
AZURE_SUBSCRIPTION_ID=
AZURE_TENANT_ID=
AZURE_RESOURCE_GROUP=
AZURE_REGION=                      # e.g. australiaeast

# Azure AI Foundry / Azure OpenAI
AZURE_AI_FOUNDRY_PROJECT=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_VERSION=
AZURE_OPENAI_DEPLOYMENT_CHEAP=     # small/fast model deployment name
AZURE_OPENAI_DEPLOYMENT_STRONG=    # high-capability deployment name
AZURE_OPENAI_DEPLOYMENT_EMBED=     # embedding deployment name

# Databricks
DATABRICKS_HOST=
DATABRICKS_WAREHOUSE_ID=
DATABRICKS_CATALOG=                # Unity Catalog catalog name
DATABRICKS_SCHEMA_PREFIX=

# Optional — if absent, use local alternatives per ADR-006
AZURE_AI_SEARCH_ENDPOINT=
AZURE_APIM_GATEWAY_URL=
AZURE_STORAGE_ACCOUNT=
```

Rules:

- All values live in `.env`, loaded via a single `config.py`. **`.env` is gitignored; `.env.example` is committed with empty values.**
- No secret ever appears in a notebook, a log line, a docstring, a commit, or a diagram.
- Prefer Managed Identity / Entra ID auth over keys wherever the SDK supports it; note in the code comment where you fell back to keys and why.
- Every Azure resource the code touches must appear in `docs/azure-resource-inventory.md` with purpose, SKU assumption, and who owns it.
- If a resource is unavailable, **degrade to the documented local fallback and log it loudly** — never silently switch providers.

---

## 4. LLM usage constraints — read this twice

> ⚠️ **Azure AI Foundry and Azure OpenAI are metered. This project is self-funded. Uncontrolled token spend is the single most likely way this build fails.** Every LLM call must be deliberate, budgeted, cached and logged. Treat the model as an expensive external API, not as free compute.

### Hard controls to implement before the first live call

1. **Single choke point.** Every model call in the entire repo goes through `src/gateway/llm_client.py`. No direct SDK calls anywhere else. Enforce this with a CI grep check.
2. **Budget ceiling with a hard stop.** Config-driven daily and total token budgets per workload. On breach, the client **raises and halts** — it does not warn and continue.
3. **Dry-run mode by default.** `LLM_MODE=dry_run|cached|live`, defaulting to `dry_run`. Live mode requires an explicit environment flag. Every notebook must run end-to-end in `dry_run` without spending a cent.
4. **Response cache, on by default.** Key on `hash(model + prompt + params)`, persisted to disk. Re-running an evaluation must cost zero.
5. **Model routing, cheapest first.** Classification, routing, extraction and summarisation use the cheap deployment. The strong deployment is reserved for final evidence-pack drafting and critique. Escalation is explicit and logged with a reason.
6. **Golden set stays small.** 40–60 cases maximum for the eval harness, not thousands. Measure well on a small set rather than badly on a large one.
7. **Cost accounting is a feature.** Log prompt tokens, completion tokens, model, workload, latency and estimated AUD cost for every call to a Delta table. `docs/cost-model.md` is generated from this table, not written by hand.
8. **Local-first development.** Build and debug the full pipeline against a local open-weights model or stub responses. Switch to Foundry only for the final evaluation runs and the demo path.
9. **Batch and truncate.** Chunk documents once and persist the embeddings. Never re-embed the corpus on a re-run. Cap context length explicitly per call.
10. **Publish the spend.** The limitations document states actual total cost. It is a credibility asset, not an embarrassment.

---

## 5. Real data sources

Verify every link is live before use. If a URL has moved, find the current one on the same domain and **record the resolved URL and the access date** in `data/SOURCES.md`. Do not substitute a different dataset silently.

### 5.1 Regulatory corpus — 100% real, this is the RAG source of truth

| Source | What it gives you | Where |
|---|---|---|
| National Energy Retail Rules (esp. **Part 7 — life support**) | Core obligation text | `aemc.gov.au` — National Energy Retail Rules |
| National Energy Retail Law | Statutory basis (enacted in SA, applied by other jurisdictions) | `legislation.sa.gov.au` |
| AER **Customer Hardship Policy Guideline** | Mandatory hardship policy minimum requirements | `aer.gov.au/industry/retail/guidelines-reviews` |
| AER **Better Bills Guideline** | Billing information obligations | same |
| AER **Compliance Procedures and Guidelines** | What must be reported, how, and when | same |
| AER **Exempt Selling Guideline** | Embedded network / exempt seller obligations | same |
| AER **Compliance and Enforcement Priorities** (annual) | Justifies the scope choice — cite the current year | `aer.gov.au` |
| ESC Victoria **Energy Retail Code of Practice** | Victorian regime | `esc.vic.gov.au` |
| ESC Victoria **Payment Difficulty Framework** | Victorian hardship obligations | `esc.vic.gov.au` |
| AEMO **Retail Electricity Market Procedures / B2B Procedures** | How life support data flows retailer ↔ distributor | `aemo.com.au` |

For each document capture: title, issuing body, version/date, jurisdiction, source URL, retrieval date, and licence/terms. Store this as structured metadata alongside the text — citations depend on it.

### 5.2 Calibration data — real published statistics used to anchor the synthetic population

| Source | What it gives you | Where |
|---|---|---|
| **AER Retail Markets Performance Data** (quarterly) | Hardship participation rates, average hardship debt, disconnection counts, life support customer counts. **This is the single most valuable file in the project.** | `aer.gov.au/industry/retail/performance-reporting` |
| **AER Annual Retail Markets Report** | Narrative context and trend direction | same |
| Energy & Water Ombudsman annual reports — **EWOV** (`ewov.com.au`), **EWON** (`ewon.com.au`), **EWOQ** (`ewoq.com.au`) | Complaint category volumes and themes | respective sites |
| **ABS SEIFA** — Socio-Economic Indexes for Areas | Postcode-level disadvantage index | `abs.gov.au` |
| **DSS Payment Demographic Data** | Postcode-level income support recipient counts | `data.gov.au` |

### 5.3 Operational / technical data — real Australian

| Source | What it gives you | Where |
|---|---|---|
| **Ausgrid Solar Home Electricity Data** | 300 real NSW households, half-hourly interval data | `ausgrid.com.au` — Data to share |
| **AER CDR Energy Product Reference Data** | Real retail tariff plans, public API, no auth required | `aer.gov.au` / CDR Energy PRD |
| **Victorian Energy Compare** offer dataset | Victorian retail offers | `data.vic.gov.au` |
| **AEMO** aggregated price and demand | Regional NEM data, 30-minute | `aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem` |
| **BOM** climate data | Temperature for consumption context | `bom.gov.au/climate/data` |

---

## 6. Synthetic data — the method matters more than the data

Customer records, life support registration events, communication logs, payment plan records, debt balances, hardship enrolments and agent notes do not exist publicly and never will. Generate them — but generate them in a way you can defend in an interview.

### The rule

> **Take the marginals from real published AER statistics. Generate only the joint structure.**

Concretely:

- Hardship program participation rate → pinned to the real rate in AER Retail Markets Performance Data
- Average and distribution of hardship debt → derived from the same published figures
- Life support customer proportion → derived from published counts
- Geographic distribution → correlated with ABS SEIFA and DSS payment data, so disadvantaged postcodes carry realistic hardship density
- Consumption profiles → sampled from real Ausgrid half-hourly interval data
- Tariffs → mapped to real plans from CDR Energy PRD
- Seasonality → aligned to real AEMO demand and BOM temperature patterns

### Deliberate breach injection

Inject a known, seeded set of violations with recorded ground truth:

- Life support written confirmation sent after the required window
- Missed annual re-confirmation cycle
- Missing or late retailer→distributor notification
- Hardship plan established without the required entitlement assessment
- Payment plan terms below the minimum standard
- Protected customer subjected to a prohibited action

Ground truth is stored in `data/ground_truth/` and is **never** visible to the Control Engine or the agent. Because you hold it, you can genuinely measure recall and precision — this is what makes the results real rather than asserted.

### Required disclosure — put this verbatim in the README

> *The synthetic customer population reproduces the published quarterly marginals from the AER Retail Markets Performance Data for hardship participation, average hardship debt, and disconnection rates. The joint structure is generated. Compliance breaches are deliberately injected with known ground truth to permit measurement of detection recall and precision. No real customer data is used anywhere in this project.*

That paragraph converts "I used synthetic data" from an apology into a methodology statement. Do not weaken it.

---

## 7. Architecture

```
Regulatory PDFs ──▶ [1] Obligation Register (Delta, versioned, human-verified)
                              │
Operational data ──▶ [2] Data Plane (Databricks medallion, Unity Catalog)
                              │
                              ▼
                     [3] Control Engine  ── deterministic, no LLM
                              │  compliant / at_risk / breach
                              ▼
                     [4] Risk Model (MLflow) ── ranks 30-day breach risk
                              │
                              ▼
                     [5] Agent Layer ── retriever │ timeline │ drafter │ critic
                              │
                     [6] MCP Server ── tools exposed via Model Context Protocol
                              │
                     [7] AI Gateway ── routing │ budget │ PII │ safety │ logging
                              │
                     [8] Eval Harness ── golden set + injected breaches, in CI
```

### [1] Obligation Register — the differentiating layer

Structured, machine-readable obligation records extracted from regulatory text:

```
obligation_id, instrument, jurisdiction, clause_reference,
obligation_family, trigger_event, required_action,
deadline_value, deadline_unit, evidence_required[],
applies_to_customer_segment, source_url, source_version,
effective_from, effective_to, extraction_method,
verified_by_human (bool), verification_date
```

Extraction is LLM-assisted but **every record must be human-verified before use**, and the register itself is versioned in Delta. `extraction_method` and `verified_by_human` are mandatory fields — an unverified record cannot be used by the Control Engine.

### [2] Data Plane

Bronze → Silver → Gold on Delta Lake. Entities: customer master, life support registration events, communication log, payment plan events, hardship enrolment, meter reads, distributor notifications. Unity Catalog for access control, lineage and row-level security. Sensitive columns tagged.

### [3] Control Engine — deterministic

One pure function per obligation, signature `(obligation, customer_state, as_of_date) -> ControlResult`. Returns `compliant | at_risk | breach`, the triggering event, the applicable clause, and the point-in-time obligation version used. Fully unit-tested. **No model call may appear in this module** — enforce with a CI check.

### [4] Risk Model

Gradient-boosted classifier predicting 30-day breach risk, tracked in MLflow with model registry and drift monitoring. **Compared against a rule-based baseline. If it does not beat the baseline, publish that and do not ship it.**

### [5] Agent Layer — multi-agent, Azure AI Foundry

- **Retriever** — pulls the relevant obligation text and citation metadata
- **Timeline builder** — reconstructs the ordered event sequence from the data plane
- **Drafter** — writes the evidence pack with inline citations
- **Critic** — checks completeness against `evidence_required[]`; returns `insufficient_evidence` with a gap list when the pack cannot be supported

### [6] MCP Server

Expose obligation lookup, control status, timeline retrieval and evidence retrieval as Model Context Protocol tools. Document the tool schemas. This is explicitly requested in the target role and is also what makes the asset pluggable into a client's existing assistant.

### [7] AI Gateway

Azure API Management GenAI gateway capabilities where available; a local equivalent otherwise. Responsibilities: model routing, per-workload token budgets, **PII redaction before the model call** (customer name, address and NMI never reach the LLM — redact to stable pseudonymous tokens and re-hydrate after), content safety, full prompt/response logging, retry and fallback. **The interface is provider-agnostic** so the gateway can be pointed elsewhere without touching workload code.

### [8] Eval Harness

Golden question set plus the injected breach set. Runs in CI on every prompt or model change. Fails the build on regression beyond a configured threshold.

---

## 8. Build phases

Each phase has a definition of done. **Do not start a phase before the previous one meets it.**

### Phase 0 — Setup and contracts
Collect Azure credentials (Section 3). Scaffold the repo. Implement `config.py`, `.env.example`, gitignore. Implement `llm_client.py` with dry-run mode, cache, budget ceiling and cost logging **before any other code**. Write ADR-001 through ADR-006 as stubs.
**Done when:** the repo runs end-to-end in `dry_run` with zero spend, and no secret is committed.

### Phase 1 — Corpus acquisition
Download the regulatory corpus. Capture full source metadata. Chunk with clause-level granularity, preserving clause references — citation accuracy depends entirely on this. Embed once, persist.
**Done when:** `data/SOURCES.md` lists every document with resolved URL, version and retrieval date; embeddings are persisted and re-runnable at zero cost.

### Phase 2 — Obligation Register
Extract 25–40 obligation records across the two families and both regimes. Human-verify each. Version in Delta under Unity Catalog.
**Done when:** every record has a resolvable clause reference, and a spot-check of 10 records traces cleanly back to source text.

### Phase 3 — Synthetic population
Acquire calibration data. Generate the population per Section 6. Inject seeded breaches with ground truth held separately.
**Done when:** a calibration report compares your generated marginals against the published AER figures side by side, and the deltas are within a stated tolerance.

### Phase 4 — Control Engine
Implement one control function per obligation. Unit test each against handcrafted edge cases.
**Done when:** the engine runs against the population, and recall/precision against injected ground truth is computed and recorded.

### Phase 5 — Risk Model
Feature engineering, baseline, model, MLflow tracking and registry, honest comparison.
**Done when:** the baseline-vs-model comparison is published — whichever wins.

### Phase 6 — Agent layer, MCP, Gateway
Build the four agents, the MCP server and the gateway. Cheap model by default; escalation logged with reason.
**Done when:** an evidence pack is produced for a flagged case with correct citations, and a deliberately under-evidenced case returns `insufficient_evidence`.

### Phase 7 — Evaluation
Run the three arms on the same held-out cases: **manual baseline → deterministic rule engine → rules + agent evidence pack.**

Measure: breach detection recall and precision; false positive rate; evidence pack completeness against a published rubric; citation accuracy; groundedness; cost per case (tokens + DBU); latency.

**Do not measure, and explicitly do not claim:** staff hours saved, penalties avoided, customer satisfaction impact. List these under "Unmeasured" in the limitations document.
**Done when:** results are published including any negative result, with the recommendation that honestly follows from them.

### Phase 8 — Documentation and packaging
Produce the deliverables in Section 9.
**Done when:** an engineer who has never seen the project could build it from `docs/` alone.

---

## 9. Deliverables

Documents first in the repo root; code second. This ordering is deliberate — it is what distinguishes an architecture portfolio from a demo.

```
README.md
docs/
  solution-architecture-document.md     # 10–12 pages, engineering-ready
  adr/
    ADR-001-obligation-extraction-approach.md
    ADR-002-deterministic-vs-llm-boundary.md
    ADR-003-pii-boundary-and-redaction.md
    ADR-004-vector-store-selection.md
    ADR-005-model-routing-and-cost-control.md
    ADR-006-cloud-target-and-local-fallback.md
  security-control-matrix.md
  threat-model-stride.md
  nfr-table.md                          # latency, availability, groundedness thresholds
  cost-model.md                         # generated from the cost log, not hand-written
  azure-resource-inventory.md
  limitations-and-unmeasured-claims.md  # first-class deliverable
  evaluation-results.md
data/
  SOURCES.md
  ground_truth/
src/
  gateway/        # llm_client.py — the single choke point
  register/
  dataplane/
  controls/       # no LLM imports permitted
  risk/
  agents/
  mcp_server/
  eval/
reference-build/  # the working thin slice
tests/
```

The Solution Architecture Document must cover: context and drivers, scope and non-goals, logical and physical architecture, data flows, integration and API design, security controls and PII boundary, deployment model, operational support and runbook, cost model, NFRs, risks and mitigations.

---

## 10. Anti-patterns — do not do these

- Do not let the LLM classify compliance status. Ever.
- Do not build a chat interface as the primary output. The output is an evidence pack.
- Do not claim measured business value that was not measured here.
- Do not assert anything about a named company's internal practices.
- Do not present synthetic data as real, or Portuguese/US data as Australian.
- Do not flatten Victoria into the NERL regime.
- Do not integrate a named commercial CRM. Adapter interface, mock implementation.
- Do not expand scope to gas, billing recalculation, or automated customer contact.
- Do not call a model outside `llm_client.py`.
- Do not re-embed the corpus on a re-run.
- Do not ship a model that loses to its baseline.
- Do not hide a negative result. Publishing it is the point.

---

Section 11 omitted: private positioning and commercial framing.
