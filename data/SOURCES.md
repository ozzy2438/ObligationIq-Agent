# Regulatory sources

Verified snapshot: **12 September 2026**. All ten PDF source documents were downloaded from their issuing institutions and SHA-256 pinned. This inventory covers the Phase 1 regulatory corpus, not the later calibration or customer datasets.

Full structured metadata, exact extraction ranges and hashes are in [source-manifest.json](source-manifest.json). All raw PDFs and derived text remain local. Physical PDF page numbers are one-based.

| Source | Issuer / regime | Version | Retrieved | Resolved PDF | Licence / terms |
|---|---|---|---|---|---|
| National Energy Retail Rules | AEMC / NERL_NERR | 51 | 2026-09-12 | [PDF](https://aemc-dra-production-s3.s3.ap-southeast-2.amazonaws.com/rules/ee0c0f923d57687aba955f6f97a974077ed27515/assets/files/NERR%20-%20v51%20-%20Full.pdf) | [AEMC copyright; personal non-commercial unaltered reproduction terms; no open licence asserted](https://www.aemc.gov.au/disclaimer-and-copyright) |
| National Energy Retail Law (South Australia) Act 2011, Schedule: National Energy Retail Law | State of South Australia / NERL_NERR | 18 December 2025 consolidation | 2026-09-12 | [PDF](https://legislation.sa.gov.au/_legislation-documents/lz/c/a/national-energy-retail-law-south-australia-act-2011/current/2011.6.auth.pdf) | [CC BY 4.0; SA additional attribution and publication disclaimer](https://www.legislation.sa.gov.au/copyright) |
| Energy Retail Code of Practice | Essential Services Commission Victoria / VIC | 6 | 2026-09-12 | [PDF](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf) | [Copyright Essential Services Commission 2026; no open licence stated in code](https://www.esc.vic.gov.au/sites/default/files/documents/Energy%20Retail%20Code%20of%20Practice%20%28version%206%29_2.pdf#page=2) |
| Customer Hardship Policy Guideline | AER / NERL_NERR | 1, March 2019 | 2026-09-12 | [PDF](https://www.aer.gov.au/system/files/2025-02/AER%20-%20Customer%20Hardship%20Policy%20Guideline%20March%202019.pdf) | [CC BY 3.0 AU](https://www.aer.gov.au/system/files/2025-02/AER%20-%20Customer%20Hardship%20Policy%20Guideline%20March%202019.pdf#page=2) |
| Better Bills Guideline | AER / NERL_NERR | 2, 30 January 2023 | 2026-09-12 | [PDF](https://www.aer.gov.au/system/files/AER%20-%20Better%20Bills%20Guideline%20(Version%202)%20-%20January%202023_0.pdf) | [CC BY 4.0](https://www.aer.gov.au/system/files/AER%20-%20Better%20Bills%20Guideline%20(Version%202)%20-%20January%202023_0.pdf#page=2) |
| Compliance Procedures and Guidelines: National Energy Retail Law, Retail Rules and Regulations | AER / NERL_NERR | 7, July 2024 | 2026-09-12 | [PDF](https://www.aer.gov.au/system/files/2024-07/Final%20%28Retail%20Law%29%20Compliance%20procedures%20and%20guidelines.pdf) | [CC BY 4.0](https://www.aer.gov.au/system/files/2024-07/Final%20%28Retail%20Law%29%20Compliance%20procedures%20and%20guidelines.pdf#page=2) |
| Retail Exempt Selling Guideline | AER / NERL_NERR | 7, August 2025 | 2026-09-12 | [PDF](https://www.aer.gov.au/system/files/2025-10/Retail%20Exempt%20Selling%20Guideline%20%28version%207%29.pdf) | [CC BY 3.0 AU](https://www.aer.gov.au/system/files/2025-10/Retail%20Exempt%20Selling%20Guideline%20%28version%207%29.pdf#page=2) |
| Payment Difficulty Framework Guideline | Essential Services Commission Victoria / VIC | 24 July 2024 | 2026-09-12 | [PDF](https://www.esc.vic.gov.au/sites/default/files/documents/GL%20-%20PDF%20Guideline%20-%20FINAL%20-%2020240724.pdf) | [CC BY 4.0](https://www.esc.vic.gov.au/sites/default/files/documents/GL%20-%20PDF%20Guideline%20-%20FINAL%20-%2020240724.pdf#page=2) |
| B2B Procedure: Customer and Site Details Notification Process | AEMO / NEM_CONTEXT | 4.01; final 5 May 2026 | 2026-09-12 | [PDF](https://aemo.com.au/-/media/files/electricity/nem/retail_and_metering/b2b/2026/b2b-procedure-customer-and-site-details-notification-process-v401.pdf?rev=0593fd16fba2484e879ef873cdc600c5&sc_lang=en) | [AEMO public material: reuse with accurate attribution](https://www.aemo.com.au/privacy-and-legal-notices/copyright-permissions) |
| Compliance and Enforcement Priorities 2026–2027 | AER / NERL_NERR | June 2026; 2026–27 annual priorities | 2026-09-12 | [PDF](https://www.aer.gov.au/system/files/2026-06/AER%20compliance%20and%20enforcement%20priorities%20-%202026-2027.pdf) | [CC BY 4.0](https://www.aer.gov.au/about/policies/disclaimer-copyright) |

## Source decisions and date traps

- **nerr**: Current approved, non-archived API record 817; other records with version 51 are archived. Index covers r33, Part 3 and Part 7; whole document retained locally.
- **nerl**: Statutory foundation from the SA Schedule; application laws and jurisdiction-specific modifications still require Phase 2 verification. www host returned 403; same official non-www host served the pinned PDF.
- **esc**: Index covers Parts 6 and 8. Version 7 changes commence 1 October 2026; draft life support reforms are not used.
- **hardship**: Publication date is March 2019; a blanket instrument commencement date was not inferred. Transitional policy submission requirements remain clause-specific. Printed pages 14–15 (PDF pages 13–14) skip clause 55; visually verified, no missing text invented.
- **bills**: Context only. Transitional provisions and exceptions exist; do not treat every historical clause as operative today. Billing engine remains out of scope.
- **compliance**: Cover says published July 2024, effective 1 April 2025. PDF licence wording says 4.0 Australia; hyperlink resolves to CC BY 4.0.
- **exempt**: Context only; staged 2025/2026 commencement and exemption-class applicability must be checked per condition.
- **payment**: 2024 guideline is current as of snapshot. Published replacement starts 1 October 2026 and is excluded. Guidance is not interchangeable with the Code.
- **b2b**: Current operational listing and PDF agree on v4.01 effective 1 July 2026. Replaces the initially researched v3.91. The v4.0 consultation copy has mixed revision text and is not used. NSW B2B procedures and referenced instruments remain additional applicability checks before operational use.
- **priorities**: Hardship access is an annual priority; life support is described as continuing vulnerability enforcement outside the five priorities. No claim that both are separate annual priorities.

## Attribution and use

- **nerr**: Australian Energy Market Commission, National Energy Retail Rules version 51. Local research only. Raw PDF, extracted clauses and vectors are not redistributed. Commercial/public reuse requires separate rights assessment.
- **nerl**: State of South Australia. Based on content from the South Australian Legislation website at 12 September 2026. For the latest information on South Australian Government legislation, please go to www.legislation.sa.gov.au/. Despite any headers, footers or other markings, this legislation is NOT published under the Legislation Revision and Publication Act 2002. To access legislation that is published under the Legislation Revision and Publication Act 2002, please go to www.legislation.sa.gov.au/.
- **esc**: Essential Services Commission, Energy Retail Code of Practice, 2026. Local legal research only. No redistribution of full text, PDFs or vectors; no commercial reuse permission claimed.
- **hardship**: Source: AER © Commonwealth of Australia. Text extracted and segmented for local research. Coat of Arms, logos and third-party graphics excluded; full source material is not redistributed.
- **bills**: Source: AER © Commonwealth of Australia. Text extracted and segmented for local research. Coat of Arms, logos and third-party graphics excluded; full source material is not redistributed.
- **compliance**: Source: AER © Commonwealth of Australia. Text extracted and segmented for local research. Coat of Arms, logos and third-party graphics excluded; full source material is not redistributed.
- **exempt**: Source: AER © Commonwealth of Australia. Text extracted and segmented for local research. Coat of Arms, logos and third-party graphics excluded; full source material is not redistributed.
- **payment**: Essential Services Commission 2024, Payment Difficulty Framework Guideline, 24 July 2024. Extracted and segmented for research. Logos, images and photographs excluded from licence.
- **b2b**: Australian Energy Market Operator, B2B Procedure: Customer and Site Details Notification Process, v4.01. Publicly published final procedure bears a For Official use only marking. Preserve provenance; no confidential or third-party commissioned documents included.
- **priorities**: Source: AER © Commonwealth of Australia. Text extracted and segmented for local research. Coat of Arms, logos and third-party graphics excluded; full source material is not redistributed.

## Reproduction

Run `python scripts/acquire_corpus.py --model`, then follow [the Phase 1 runbook](../docs/phase-1-corpus.md). Downloads fail on changed bytes instead of silently selecting a new version. Every listed document has been acquired; none was substituted with a third-party summary. Original `www` endpoints for SA/AEMO returned HTTP 403 in the local downloader; the same institutions’ non-`www` PDF endpoints returned the recorded bytes.

The operational AEMO [current-version listing](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/market-operations/retail-and-metering/business-to-business-procedures) identifies v4.01 as effective 1 July 2026. Earlier v3.91 and a v4.0 consultation PDF with mixed revision text were excluded. The [ESC guideline listing](https://www.esc.vic.gov.au/electricity-and-gas/electricity-and-gas-codes-guidelines-and-policies/energy-guidelines/payment-difficulty-framework) separates the current July 2024 guideline from its October 2026 replacement.

AEMC/ESC code redistribution rights are not inferred from public availability. Source files and extracted corpus are excluded from Git; this is local research use, not a grant for commercial reuse. Logos, third-party artwork and government marks are not reproduced.

## Supplemental Phase 2 review source

The ten-document embedded corpus remains unchanged. The source review additionally acquired the [Electricity Industry Act 2000, authorised version 107](https://www.legislation.vic.gov.au/in-force/acts/electricity-industry-act-2000/107), effective 9 September 2026 and retrieved 12 September 2026, to resolve sections 40SG(1)/40SH(1) referenced by OIQ-021/022. The 329-page PDF is retained locally as `data/raw/vic-eia.pdf`; metadata, resolved URL and checksum are in [review-sources.json](review-sources.json). It was read for review, not embedded. No full text is redistributed. Acquire it with `python scripts/acquire_corpus.py --review-sources`.
