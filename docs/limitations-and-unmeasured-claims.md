# Limitations and unmeasured claims

Phase 0 only, 12 September 2026.

- No regulatory corpus has been acquired, interpreted or licensed for reuse. No obligation has human verification. Phase 1 has not started.
- No real or synthetic customer population, ground truth, risk model or compliance control exists. Tests are software-boundary checks, not a business evaluation.
- The PII hook is a stub, invoked for each request and blocking live dispatch by default. No working PII detection or rehydration is claimed.
- Register, data plane, controls, risk, agents, MCP and evaluation packages are empty. ADR-001 through ADR-004 retain pending choices.
- Azure catalog availability and public rates were checked. No model was deployed and no inference purchased. The Azure transport remains unvalidated against a deployed model.
- Costs are estimates using pinned retail rates and returned usage, not reconciled invoices. Taxes, contract pricing, currency changes and unrelated resources are outside the ledger.
- State is one durable local SQLite database. Deleting/replacing it or calling models through external software defeats local accounting. Protect and retain `.local/llm/`; no auto-reset or hold-expiry command is supplied.
- Paid requests are deliberately serial. A competing request refuses while a reservation is active. This is a pilot tradeoff, not a high-throughput production design.
- Ambiguous requests remain held until independent provider evidence establishes billed usage or confirmed non-dispatch. This phase does not automate reconciliation.
- Logs contain usage metadata rather than prompts/provider errors. Future cache contents must remain private. No production security, availability or compliance guarantee is claimed.
- Global Standard may process outside Australia; there is no Australia-only residency claim.
- Staff time saved, penalties avoided, customer satisfaction, production accuracy, latency improvement and business ROI remain unmeasured.

Observed Phase 0 application smoke-run ledger: zero committed micro-AUD and zero held micro-AUD. No paid model call occurred. Historical or eventual Azure invoice totals have not been reconciled.
