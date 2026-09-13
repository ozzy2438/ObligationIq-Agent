# Limitations and unmeasured claims

Phases 0–2 with a local catalog fallback and a partial Phase 3 population, 13 September 2026.

- Ten regulatory PDFs are acquired and source-pinned; core pilot clauses and contextual guidance are indexed locally. OIQ-024/025 have explicit human content approvals; the other 30 have authorised agent source approvals. Source reuse terms differ, and no blanket open licence or commercial redistribution permission is claimed.
- A 10,000-account **synthetic** population reproduces eight AER/ESC account marginals; a separate 34,843-record entry cohort reproduces five published NSW debt bands and the entry mean. Its joint structure, tariff eligibility and use of state priors for two distributor footprints are assumptions. The 299 complete Ausgrid profiles come from a non-representative NSW solar-household sample; reuse as a Victorian shape prior is simulated. AEMO system demand and BOM city temperature are context, not customer-level causal calibration. Eighteen challenge cases are injected across six obligations and do not estimate real breach prevalence. No real customer records, risk model or measured control performance exist yet. Victorian life-support prevalence remains unmeasured.
- The PII hook is a stub, invoked for each request and blocking live dispatch by default. No working PII detection or rehydration is claimed.
- The register contains 32 reviewed records, two human and 30 authorised agent approvals, and local Delta versioning. Controls, risk, agents, MCP and evaluation packages remain empty. The data plane contains corpus and deterministic population modules. ADR-001 records the candidate and authorised review methods; ADR-002/003 retain pending choices. Local Unity Catalog OSS registration, schema/readback and restart persistence are verified. Managed Databricks, multi-user governance, row-level security, automatic lineage and jurisdiction-specific operational application checks remain unverified.
- Azure catalog availability and public rates were checked. No model was deployed and no inference purchased. The Azure transport remains unvalidated against a deployed model.
- Costs are estimates using pinned retail rates and returned usage, not reconciled invoices. Taxes, contract pricing, currency changes and unrelated resources are outside the ledger.
- Paid-call accounting resides in a durable local SQLite database. Deleting/replacing it or calling models through external software defeats local accounting. Protect and retain `.local/llm/`; no auto-reset or hold-expiry command is supplied. Corpus and register state are separate local artifacts.
- Paid requests are deliberately serial. A competing request refuses while a reservation is active. This is a pilot tradeoff, not a high-throughput production design.
- Ambiguous requests remain held until independent provider evidence establishes billed usage or confirmed non-dispatch. This phase does not automate reconciliation.
- Logs contain usage metadata rather than prompts/provider errors. Future cache contents must remain private. No production security, availability or compliance guarantee is claimed.
- Global Standard may process outside Australia; there is no Australia-only residency claim.
- Staff time saved, penalties avoided, customer satisfaction, production accuracy, latency improvement and business ROI remain unmeasured.

Observed Phase 0 application smoke-run ledger: zero committed micro-AUD and zero held micro-AUD. No paid model call occurred. Historical or eventual Azure invoice totals have not been reconciled.

Phase 1 local embedding calls log zero external AUD charges and use no paid reservations. Their CPU, electricity and download costs are unmeasured. Generated [verification evidence](phase-1-verification.json) demonstrates repeat execution with no network or embedding inference. It does not measure semantic retrieval accuracy, legal interpretation, control precision/recall or business outcomes.

This corpus supports only the verified 12 September 2026 snapshot. Historical applications and future amendments require new source versions and clause-level applicability review. Source pagination, tables, footnotes, cross-references, exemptions and staged commencements must be checked before converting text into an executable obligation. The SA consolidation does not prove identical state implementation, and NSW B2B overlays are not yet acquired.

AER hardship source numbering skips clause 55, confirmed visually; no replacement text was invented. AEMO v3.91 and the v4.0 consultation copy were superseded during research by the current operational v4.01. Victoria's published October 2026 changes are excluded from this September snapshot. These are source curation findings, not compliance determinations.
