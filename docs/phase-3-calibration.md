# Phase 3 — calibration source preparation

Status: **started; population generation and Phase 3 acceptance remain incomplete**. This checkpoint acquires and verifies the AER inputs before generating any records. No customer population, breach injections, ground truth or claimed model/control accuracy has been produced.

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

Values above are rounded for display only. The JSON preserves numeric cell text, including full rate precision. This table is an input audit, not a generated-population calibration result.

## Checks performed

All workbook bytes match their pins. All 66 cells were independently compared with an openpyxl read of the originals. The 12 published hardship/disconnection rates reconcile to the matching residential count at absolute ratio tolerance 1e-12. Every extracted additive national count equals the five state/territory totals. No Excel formulas were executed: selected inputs must be finite nonnegative numeric literals; formula-based and missing inputs are refused.

```sh
python scripts/prepare_calibration.py --download  # explicit network acquisition if missing
python scripts/prepare_calibration.py             # offline, no model, same output
```

## Decisions that prevent misleading generation

- AER's national total here is ACT/NSW/QLD/SA/TAS, not all Australia. It contains no Victoria calibration. Victorian tailored-assistance definitions must be handled with ESC evidence, not relabelled AER hardship metrics.
- Current hardship debt and entry debt are different cohorts. The workbook's debt bands describe **entry**; they do not establish the current portfolio's debt distribution. Any generated within-band shape or joint dependency must be labelled an assumption.
- Current life-support counts and registrations/deregistrations during a quarter are different measures. Quarterly registrations cannot be substituted for prevalence. Denominator and reporting-guideline definitions must be checked before finalising the generated rate.
- The brief's suggested annual medical reconfirmation breach has no established mandatory source in the reviewed register. It will not be injected as a legal breach. Use only source-supported obligations and retain this correction in the eventual injection manifest.
- Calibration-period statistics are not proof of regulations in force in that period. The register is verified for the September 2026 snapshot. A later simulation needs explicit scenario dates and source applicability; it must not backdate those rules into January–March.
- Population marginal calibration and an intentionally enriched breach evaluation set need distinct labels. Injection must not silently change the published-rate comparison population or leak labels to controls/agents.

## Remaining Phase 3 work, in order

Complete the reporting-definition checks and separate Victorian input acquisition. Acquire and document the Section 6 geographic/consumption/tariff/seasonality inputs (ABS SEIFA, DSS, Ausgrid, CDR plans, AEMO and BOM) with their periods, coverage and join limitations. Choose a bounded population size, seed and numeric tolerance from those verified inputs. Generate once, persist the population and hold the source-supported injection ground truth separately. Produce a side-by-side published-versus-generated calibration report. Only then insert the brief's required completed-population disclosure and mark Phase 3 complete.

No login or Azure spending is needed for the acquired AER files. The control, risk, agent, MCP and evaluation phases remain unstarted.
