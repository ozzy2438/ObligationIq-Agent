# Limitations and unmeasured claims

Status at Phase 8, 13 September 2026.

## Evidence and legal scope

- The build covers 32 electricity obligations from ten pinned regulatory PDFs. OIQ-024/025 have explicit human source approval; 30 records have owner-authorised agent review. The review composition is **6.25% human / 93.75% agent** and appears on every compliance-result artefact. Agent review is never labelled human verification.
- Source-content agreement and operational evaluation eligibility are separate decisions. Neither is legal advice or proof that an obligation applies to a real customer. A changed source or record digest removes eligibility.
- Victoria remains a separate regime from NERL/NERR. The hard set found two jurisdiction false positives. Cross-references, exemptions, staged commencements and future amendments still require legal and operational review.
- The snapshot is fixed to 12–13 September 2026. Victoria's published October 2026 changes are excluded. The AER hardship instrument's numbering gap at clause 55 was confirmed rather than filled. AEMO v4.01 replaced superseded versions during acquisition. NSW B2B overlays are not included.
- Source licences differ. The repository does not claim blanket open licensing or commercial redistribution rights over source text.

## Data and calibration

- All customer and challenge data are synthetic. No named company's internal practice, customer record or breach prevalence is represented.
- The 10,000-account population matches eight published AER/ESC marginals within declared tolerances. A separate 34,843-record debt-entry cohort matches five published bands and the reported mean. Matching marginals does not validate the generated joint distribution.
- The 299 complete Ausgrid profiles are a non-representative NSW solar-household sample. Their use as a Victorian load-shape prior is a documented simulation. Distributor footprint priors and tariff eligibility are assumptions. AEMO demand and BOM temperature provide context, not customer-level causal calibration. Victorian life-support prevalence is unmeasured.

## Measured system performance

- The 72-case hard set covers all 32 obligations but is authored, synthetic and small. It demonstrates implementation behavior, not production accuracy. The deterministic engine produced recall 1.0000, precision 0.9118, FPR 0.0732 and exact status accuracy 0.9306. Five status/gap errors remain: two jurisdiction traps, two incomplete business-calendar cases and one point-in-time version case.
- The programmatic checklist baseline exactly reproduces authored labels. It is not a human baseline and supplies no human latency or error measurement.
- Both model arms inherit the rule engine's status. Agents improved evidence-pack completeness from 0.7500 to 0.8750 but did not improve detection or under-evidenced refusal. Nano groundedness was 0.9028; mini was 0.9306. These bounded structured checks are not general factuality guarantees.
- The risk component is a deterministic review-priority policy. There is no longitudinal 30-day target, learned classifier, forecast probability or causal validation. MLflow runs locally.

## Privacy, security and operations

- The live boundary excludes known customer name, address and NMI fields from a fixed schema and refuses arbitrary prose. It is not general named-entity recognition. Unstructured customer content is unsupported.
- Raw PDFs, vectors, Delta tables, model outputs, cache and ledger remain local and gitignored. Host encryption, backups, malware protection and access governance are outside the build.
- Local Unity Catalog OSS registration/readback is verified. It is not managed Databricks and does not prove multi-user policy enforcement, row-level security, automatic lineage or protected direct file access.
- The MCP surface is one local read-only evidence tool. No CRM integration, customer communication, billing recalculation, disconnection recommendation/action or production endpoint exists.
- Azure Global Standard can process outside Australia. An Australia East account is not an Australia-only data-residency guarantee.
- No high availability, recovery objective, load test, percentile latency SLA, central log retention, SBOM, signed release, penetration test or production IAM/network design is claimed.

## Cost and routing

- Confirmed metered model spend is **0.035471 AUD**; conservative ledger total is **0.039036 AUD**. The **0.003565 AUD** difference is retained overstatement from five 429 capacity rejections misclassified before ADR-009. Held reservations are zero. Figures use pinned public retail rates and provider token usage, not an Azure invoice; tax, negotiated rates and unrelated resources are excluded.
- Nano cost 0.005451 AUD and mini 0.030020 AUD over 72 cases each. Mini was 5.51 times more expensive and 42.7% slower by mean metered response latency. It improved two bounded quality rates by 2.78 points, so nano remains the default and mini is limited to explicit quality review.
- Both deployments had 10,000 TPM. Serial execution still encountered 3 nano and 29 mini structured capacity rejections. Retry completed the run, but this is not production throughput evidence.
- The ledger controls only calls made through this local gateway. Deleting/replacing its database or using another client bypasses lifetime accounting. Azure budgets are delayed alerts.

## Explicitly unmeasured

Staff hours saved, penalties avoided, customer satisfaction, ROI, production breach prevalence, production precision/recall, real reviewer performance, adoption, availability, Australian-only processing, and realised invoice cost are unmeasured and must not be inferred from this pilot.
