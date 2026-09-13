# Phase 3 — calibrated synthetic population

Status on 13 September 2026: **complete**. The build creates 10,000 synthetic accounts, a separate 34,843-record debt-entry cohort and 18 source-supported control cases. Fourteen calibration comparisons pass. Consumption profiles come from the checksum-pinned Ausgrid household data; twelve months of AEMO demand and BOM temperature provide separately labelled seasonal context. Ground truth is committed only under `data/ground_truth/` and CI blocks controls and agents from referring to it. Phase 4 has not started.

## Generated result

The [calibration evidence](population-calibration.json) records exact inputs, four artefact fingerprints, counts, unrounded deltas and tolerances. A fixed seed creates 5,000 NSW and 5,000 Victorian accounts. The [generation contract](../data/population-contract.json) exposes the assumptions; the [input extract](../data/population-inputs.json) retains cell/row provenance.

| Region / metric | Published or derived target | Generated | Tolerance |
|---|---:|---:|---:|
| NSW hardship participation | 2.218737% | 2.220000% (111) | 0.01 percentage point |
| NSW current hardship debt, mean AUD | 2,536.664846 | 2,536.664865 | AUD 0.01 |
| NSW quarterly nonpayment disconnection rate | 0.136955% | 0.140000% (7) | 0.01 percentage point |
| NSW life support, confirmed | 2.737433% | 2.740000% (137) | 0.01 percentage point |
| NSW life support, unconfirmed | 1.239170% | 1.240000% (62) | 0.01 percentage point |
| VIC tailored-assistance participation | 3.248105% | 3.240000% (162) | 0.01 percentage point |
| VIC current tailored-assistance debt, mean AUD | 1,144.022858 | 1,144.022840 | AUD 0.01 |
| VIC quarterly nonpayment disconnection rate | 0.113620% | 0.120000% (6) | 0.01 percentage point |

Rate tolerance is half an account divided by 5,000. Cent-valued debts sum to the nearest cent of the cohort's target total. The within-cohort exponential debt shape is **assumed**, not an observed published distribution. Matching marginals demonstrates calibration, not predictive accuracy or a realistic joint distribution.

The accounts are an illustrative population in the published Ausgrid and Citipower tariff footprints, not a state-representative or AGL customer sample. State marginals are deliberately used as calibration priors for these footprints; no locality-level observed hardship or disconnection rate is claimed. There are no names, addresses, real customer identifiers or source household records in the generated data.

```sh
python scripts/prepare_calibration.py --download       # existing four AER pins
python scripts/prepare_population_inputs.py --download # six additional pins
python scripts/prepare_operational_context.py --download # Ausgrid + AEMO + BOM pins
python scripts/prepare_population_inputs.py            # join all verified inputs
python scripts/build_population.py                    # offline; persists once
python scripts/build_population.py --check            # CI: no writes or network
```

Raw sources remain in ignored `data/raw/calibration/`. The account, debt-entry and source-case records remain in ignored `.local/population/v2/`; Git holds the small generator, contracts, attributed extracts, calibration evidence and isolated truth labels. An identical rebuild preserves the existing files. A changed output refuses to overwrite them, requiring an explicit new scenario version. CI needs only committed extracts, blocks Python socket activity, rebuilds in memory, checks source/register-manifest hashes and compares every artefact fingerprint. It adds no new test file and performs no model inference.

## Victoria, geography and tariffs

Six additional files in the [context manifest](../data/context-sources.json) are byte-pinned, with public URLs and retrieval date:

- **ESC Q3 FY26 dashboard workbook:** 2,840,179 residential electricity customers, 92,252 accounts receiving tailored assistance, and 3,227 nonpayment disconnections. The customer denominator excludes the different NMI count. The AUD 1,144.022858 debt target is **derived** by weighting each published retailer/ability-category mean by its corresponding end-quarter assistance-account count. All positive counts have matching means. Published means are rounded to cents; derived precision does not remove that source rounding. The workbook supplies no Victorian life-support prevalence: every VIC value is `null`, not `false` or an AER estimate.
- **ABS 2021 SEIFA postal areas + DSS March 2026 JobSeeker counts:** 270 eligible postal areas (225 NSW, 45 VIC) join to the two tariff footprints. Areas marked by ABS for caution or crossing state borders, and unmatched DSS postcodes, are excluded. Sampling is proportional to ABS resident population, an assumed proxy for account distribution. Postal areas and postal delivery codes are not perfectly equivalent; years and populations differ. DSS counts are publisher-rounded to multiples of five; values 1–7 become five. Only JobSeeker is used, avoiding addition of overlapping benefit categories.
- **AER CDR catalogue and two v3 plan details:** NSW `AGL1055859MRE2@EME` and VIC `AGD762152MR@VEC` are residential single-rate plans effective by the frozen scenario date. The Victorian identifier originates from Victorian Energy Compare and is exposed by the public CDR endpoint. Account postcodes must be included in the selected plan's published geography. Applicable network-tariff eligibility is an explicit synthetic assumption; plan mapping is not an eligibility decision, bill estimate or recommendation. No fees are applied to protected customers.

The assistance selection weight is an explicit design assumption: `1 + (10 - IRSD decile)/9 + 10 * min(JobSeeker count / resident population, 0.2)`. It increases sampling weight for relatively disadvantaged areas while fixing the total assistance count. It does not estimate a causal relationship or infer an individual's income, welfare receipt or vulnerability. Generated assistance accounts have lower mean area IRSD deciles than the other generated accounts in each region; this is a property of the chosen simulation, not empirical validation.

The data is a **13 September synthetic scenario** calibrated to January–March aggregate priors. Its historical quarterly disconnection marker has no invented event date and is not a compliance determination. Real January–March customer histories, current September prevalence, changes of status and joint overlap are unobserved. No current regulatory rule is retroactively applied to the reference quarter.

## Consumption and seasonal context

The [operational source manifest](../data/operational-sources.json) pins 37 raw files and the [derived context](../data/operational-context.json) retains only bounded attributed values. The Data.NSW catalogue is the authoritative route for Ausgrid's Solar Home Electricity Data. Its former direct Ausgrid binary path returned HTTP 404; the exact official-origin ZIP was recovered from the Internet Archive, SHA-256 `6949ffee7ef8e2260f229f8a7e3b992390187facaaf023bb933b811a11cd1a11`. No researcher mirror was used. The source contains 300 de-identified customers; one has only 284 GC days and is excluded without imputation, leaving 299 complete household-year profiles. Each synthetic account deterministically samples one profile ID and retains its source annual usage and 48 half-hour shares through the context lookup.

Twelve AEMO daily-archive ZIPs cover August 2025–July 2026: 17,520 half-hour actual operational-demand observations for NSW1 and 17,520 for VIC1. Twenty-four BOM products cover the same months: 363 complete daily min/max pairs for Sydney and 364 for Melbourne. Missing temperatures are not imputed. The build stores AEMO region factors, BOM mean daily temperature midpoint and Ausgrid household daily factors as separate series. It does not blend them into a claimed household causal model. Ausgrid explicitly says the solar sample is not statistically representative; using its shape library for Victoria is an identified simulation assumption.

The original creators' peer-reviewed description is Ratnam, Weller, Kellett and Murray (2017), “Residential load and rooftop PV generation: an Australian distribution network dataset”, *International Journal of Sustainable Energy* 36(8), 787–806, [doi:10.1080/14786451.2015.1100196](https://doi.org/10.1080/14786451.2015.1100196).

## Separate debt-entry cohort

Current hardship debt and debt on entry remain separate populations. The NSW Q3 2025–26 AER entry table reports 34,843 records across five bands. The local entry cohort reproduces those exact source counts and calibrates its mean to AUD 2,288.249433 within AUD 0.01. Within-band values are generated; strict published boundaries are preserved and the open-ended greater-than-AUD-3,500 tail absorbs the amount needed to match the mean.

| Entry debt band | Published count | Generated count | Published/generated share |
|---|---:|---:|---:|
| Less than AUD 500 | 13,588 | 13,588 | 38.997790% |
| Greater than AUD 500 and less than AUD 1,500 | 8,277 | 8,277 | 23.755130% |
| Greater than AUD 1,500 and less than AUD 2,500 | 4,259 | 4,259 | 12.223402% |
| Greater than AUD 2,500 and less than AUD 3,500 | 2,596 | 2,596 | 7.450564% |
| Greater than AUD 3,500 | 6,123 | 6,123 | 17.573114% |

This exact reproduction validates marginal calibration. It does not show that the generated amounts within a band or the joint structure resemble individual customers.

## Challenge cases and truth isolation

Six eligible source records drive 18 deterministic challenge cases: OIQ-002, OIQ-023, OIQ-024, OIQ-028, OIQ-030 and OIQ-032. Each contributes one compliant, one breach and one deliberately under-evidenced case. The breach cases use either a completed action after the cited business-day deadline or complete audit evidence that an untimed required action was not completed. No annual medical reconfirmation requirement is injected.

Input facts are written locally to `.local/population/v2/control-cases.jsonl`. Their labels and source-grounded reasons live separately in [data/ground_truth/control-cases.json](../data/ground_truth/control-cases.json), bound to the input SHA-256. CI rejects any `ground_truth` reference or evaluation/build import under `src/controls/` and `src/agents/`. The truth artefact discloses that the underlying 32 obligations comprise 2 human-verified records (6.25%) and 30 authorised-agent-reviewed records (93.75%).

## Acquired evidence

Four official AER workbooks cover January–March 2026 (Q3 2025–26), released 24 June 2026. The [source manifest](../data/calibration-sources.json) pins URLs, SHA-256 hashes, period, issuer and reuse terms. Source: AER © Commonwealth of Australia. This is a selected historical calibration period, not a September 2026 customer snapshot.

The [extracted aggregates](../data/calibration-aggregates.json) contain 66 published cells: 11 metrics for ACT, NSW, Queensland, South Australia, Tasmania and the AER national total. Each value includes its workbook, sheet, cell, period cell and published definition. The four raw workbooks remain ignored. No retailer-level or personal customer data is committed.

Selected national electricity residential inputs, all for Q3 2025–26:

| Metric | Published value | Schedule / sheet / cell |
|---|---:|---|
| Residential customers | 7,060,625 | 2 / ResElec Cust#s & Mkt Contr / F91 |
| Hardship customers | 150,486 | 4 / Hardship numbers / F91 |
| Hardship participation | 2.131341% | 4 / Hardship numbers / K91 |
| Current hardship debt, average AUD | 2,438.18 | 4 / Hardship Avg & Entry Debt / L91 |
| Debt on hardship entry, average AUD | 2,246.75 | 4 / Hardship Avg & Entry Debt / F91 |
| Customers disconnected during quarter | 8,724 | 3 / Disconnections Resi / F77 |
| Quarterly disconnection rate | 0.123558% | 3 / Disconnections Resi / L77 |
| Life support with medical confirmation | 160,132 | 6 / Life support electricity cust#s / F72 |
| Life support without medical confirmation | 77,670 | 6 / Life support electricity cust#s / K72 |

Values above are rounded for display only. The JSON preserves numeric cell text, including full rate precision. This national table is an input audit; the generated comparison above uses NSW and separate ESC Victoria inputs.

## Checks performed

All workbook bytes match their pins. All 66 cells were independently compared with an openpyxl read of the originals. The 12 published hardship/disconnection rates reconcile to the matching residential count at absolute ratio tolerance 1e-12. Every extracted additive national count equals the five state/territory totals. No Excel formulas were executed: selected inputs must be finite nonnegative numeric literals; formula-based and missing inputs are refused.

The additional 270 geography joins and 194 ESC observations were independently compared with openpyxl reads of the pinned originals. Every positive Victorian assistance-count weight resolves to its matching retailer/category debt mean. The generated population is reproduced by the dependency-free build and checked against the committed fingerprint in CI.

```sh
python scripts/prepare_calibration.py --download  # explicit network acquisition if missing
python scripts/prepare_calibration.py             # offline, no model, same output
```

## Decisions that prevent misleading generation

- AER's national total here is ACT/NSW/QLD/SA/TAS, not all Australia. It contains no Victoria calibration. Victorian tailored-assistance definitions must be handled with ESC evidence, not relabelled AER hardship metrics.
- Current hardship debt and entry debt are different cohorts. The workbook's debt bands describe **entry**; they do not establish the current portfolio's debt distribution. Any generated within-band shape or joint dependency must be labelled an assumption.
- Current life-support counts and registrations/deregistrations during a quarter are different measures. NSW prevalence uses the confirmed/unconfirmed counts from the explicitly residential-electricity sheet divided by residential customers; quarterly registrations and deregistrations are excluded. This calibration ratio does not determine legal registration status for an actual account.
- The brief's suggested annual medical reconfirmation breach has no established mandatory source in the reviewed register. It will not be injected as a legal breach. Use only source-supported obligations and retain this correction in the eventual injection manifest.
- Calibration-period statistics are not proof of regulations in force in that period. The register is verified for the September 2026 snapshot. A later simulation needs explicit scenario dates and source applicability; it must not backdate those rules into January–March.
- Population marginal calibration and an intentionally enriched breach evaluation set need distinct labels. Injection must not silently change the published-rate comparison population or leak labels to controls/agents.

## Completion checks

The seed rebuilds all four artefacts byte-for-byte. Fourteen comparisons pass: eight account marginals, five entry-debt bands and the entry-debt mean. The population uses 299 source profiles; regional seasonal context covers twelve months, 17,520 AEMO intervals per region and 363/364 complete BOM days. Eighteen challenge cases contain six breaches, six compliant outcomes and six insufficient-evidence outcomes. No login, network call during replay, model call or Azure spend is required.

> *The synthetic customer population reproduces the published quarterly marginals from the AER Retail Markets Performance Data for hardship participation, average hardship debt, and disconnection rates. The joint structure is generated. Compliance breaches are deliberately injected with known ground truth to permit measurement of detection recall and precision. No real customer data is used anywhere in this project.*

The correction to the original source-unavailable conclusion and the obsolete URL evidence remain in [the acquisition audit](calibration-acquisition-gaps.json). The control, risk, agent, MCP and evaluation phases remain unstarted.
