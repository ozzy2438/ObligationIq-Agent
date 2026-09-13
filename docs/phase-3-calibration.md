# Phase 3 — calibrated synthetic core

Status on 13 September 2026: **10,000 synthetic accounts generated; Phase 3 remains incomplete**. The core population matches eight AER/ESC marginal comparisons and replays offline with the same SHA-256. Consumption, seasonality, debt-entry bands, event scenarios and isolated ground truth remain outstanding. Phase 4 has not started.

## Generated result

The [calibration evidence](population-calibration.json) records exact inputs, output fingerprint, counts, unrounded deltas and tolerances. A fixed seed creates 5,000 NSW and 5,000 Victorian accounts. The [generation contract](../data/population-contract.json) exposes the assumptions; the [input extract](../data/population-inputs.json) retains cell/row provenance.

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
python scripts/build_population.py                    # offline; persists once
python scripts/build_population.py --check            # CI: no writes or network
```

Raw sources remain in ignored `data/raw/calibration/`. The 10,000 account records remain in ignored `.local/population/accounts.jsonl`; Git holds the small generator, contract, attributed extracts and calibration evidence. An identical rebuild preserves the existing account file. A changed output refuses to overwrite it, requiring an explicit new scenario version. CI needs only committed extracts, blocks Python socket activity, rebuilds in memory, checks source-manifest hashes and compares the complete output/evidence fingerprint. It adds no new test file and performs no model inference.

## Victoria, geography and tariffs

Six additional files in the [context manifest](../data/context-sources.json) are byte-pinned, with public URLs and retrieval date:

- **ESC Q3 FY26 dashboard workbook:** 2,840,179 residential electricity customers, 92,252 accounts receiving tailored assistance, and 3,227 nonpayment disconnections. The customer denominator excludes the different NMI count. The AUD 1,144.022858 debt target is **derived** by weighting each published retailer/ability-category mean by its corresponding end-quarter assistance-account count. All positive counts have matching means. Published means are rounded to cents; derived precision does not remove that source rounding. The workbook supplies no Victorian life-support prevalence: every VIC value is `null`, not `false` or an AER estimate.
- **ABS 2021 SEIFA postal areas + DSS March 2026 JobSeeker counts:** 270 eligible postal areas (225 NSW, 45 VIC) join to the two tariff footprints. Areas marked by ABS for caution or crossing state borders, and unmatched DSS postcodes, are excluded. Sampling is proportional to ABS resident population, an assumed proxy for account distribution. Postal areas and postal delivery codes are not perfectly equivalent; years and populations differ. DSS counts are publisher-rounded to multiples of five; values 1–7 become five. Only JobSeeker is used, avoiding addition of overlapping benefit categories.
- **AER CDR catalogue and two v3 plan details:** NSW `AGL1055859MRE2@EME` and VIC `AGD762152MR@VEC` are residential single-rate plans effective by the frozen scenario date. The Victorian identifier originates from Victorian Energy Compare and is exposed by the public CDR endpoint. Account postcodes must be included in the selected plan's published geography. Applicable network-tariff eligibility is an explicit synthetic assumption; plan mapping is not an eligibility decision, bill estimate or recommendation. No fees are applied to protected customers.

The assistance selection weight is an explicit design assumption: `1 + (10 - IRSD decile)/9 + 10 * min(JobSeeker count / resident population, 0.2)`. It increases sampling weight for relatively disadvantaged areas while fixing the total assistance count. It does not estimate a causal relationship or infer an individual's income, welfare receipt or vulnerability. Generated assistance accounts have lower mean area IRSD deciles than the other generated accounts in each region; this is a property of the chosen simulation, not empirical validation.

The data is a **13 September synthetic scenario** calibrated to January–March aggregate priors. Its historical quarterly disconnection marker has no invented event date and is not a compliance determination. Real January–March customer histories, current September prevalence, changes of status and joint overlap are unobserved. No current regulatory rule is retroactively applied to the reference quarter.

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

## Remaining Phase 3 work

1. Recover and authenticate the Ausgrid household data. The original official 2012–13 ZIP URL returned HTTP 404; a researcher mirror is a lead, not yet verified original bytes. `consumption_profile_id` remains null.
2. Pin AEMO demand and BOM weather values and implement their explicit seasonal alignment. Direct March 2026 regional CSV/PDF downloads returned HTTP 403. Public page visibility is not a successful reproducible numeric acquisition. `seasonality_context_id` remains null. [Acquisition record](calibration-acquisition-gaps.json).
3. Calibrate an independent hardship-entry cohort to the published entry-debt bands and mean. Do not relabel entry bands as current-customer debt distribution.
4. Add source-supported dated events, then seeded challenge injections with ground truth separately held in `data/ground_truth/`. Preserve the operational applicability gate and prove that the future control/agent inputs exclude truth labels. Annual mandatory medical reconfirmation is not established by the reviewed sources and will not be invented as a breach.

The brief's required completed-population paragraph remains deferred because it would currently claim breach injections that do not exist. No source requirement or deadline was added by this population work. No login or Azure spending was needed. The control, risk, agent, MCP and evaluation phases remain unstarted.
