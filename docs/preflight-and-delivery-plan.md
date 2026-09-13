# Preflight and Phase 0 decisions

Updated 12 September 2026, Australia/Melbourne.

## Corrections and scope

The user's Turkish correction, “40 değil de 10”, overrides the pasted 40 AUD ceiling and incompatible 25 AUD application allowance. The ceiling is **10 AUD**, with application defaults of **6 AUD lifetime / 1 AUD per UTC day**. Four AUD remains as headroom; there is no requirement to spend the allowance.

The [public build brief](build-brief.md) excludes Section 11 entirely. The original private file is unchanged. This work implements **Phase 0 only**; it does not acquire a regulatory corpus or generate customer data.

## Verified Azure setup

Azure CLI authentication and live Resource Manager access were verified. Another login is unnecessary for current management operations. Tokens and keys were not copied into the repository.

The budget is now `obligationiq-pilot-aud-10`, scoped to `rg-obligationiq-pilot` in `australiaeast`. The replacement was created and read back before deleting `obligationiq-pilot-aud-3`; the resource name is replaced rather than edited in place. Amount: 10 AUD. Annual period: 1 September 2026–31 August 2027. Actual-cost email alerts: 50%, 75%, 90%, 100%. Unrelated resources and budgets are unchanged.

The annual period avoids monthly resets during this build. It expires on the stated date. Application lifetime accounting is independent of that period. Azure budgets do not stop consumption and reported costs arrive with a delay; neither the budget nor this gateway controls unrelated charges or invoice adjustments.

Read-only catalog queries confirmed the intended cheap, strong and embedding tiers in `australiaeast`. Microsoft retail-price records supply the pinned AUD rates; see [the inventory](azure-resource-inventory.md). No model account/deployment, Databricks warehouse, storage, search service or API Management instance was provisioned.

## Phase 0 decisions

1. Safe offline defaults require no invented identifiers. Live requirements are validated on import with a separate enable flag. Unused Databricks credentials are not required.
2. One gateway owns model dispatch. SQLite stores reservations, response cache and usage logs. Atomic reservations and serial paid execution prevent competing requests overspending the allowance.
3. Reserve bounded uncached input and total output cost, including reasoning, plus 25% headroom. Settle using returned usage and integer micro-AUD. This is a retail-rate estimate of actual usage, not a reconciled invoice.
4. Cache hits reserve nothing. Dry-run stubs never enter the real response cache.
5. Unknown prices, insufficient balance and unresolved reservations raise. Settlement, cache insertion and success logging share a transaction.
6. Release only confirmed pre-dispatch failures. Timeouts may conceal billed requests: retain the reservation and halt.
7. The PII interface is invoked. Its default stub blocks live dispatch. Entra authentication and deployment identity checks exist in the unvalidated Azure adapter.

## Disagreements and deliberate boundaries

- Blanket “release on failure” is unsafe after timeouts or crashes. Such holds require independent reconciliation; no auto-expiry or ledger reset command is supplied.
- Requiring every cloud key for dry-run imports would force fake endpoints or unused services. Requiredness is mode-specific; every Section 3 key remains empty in the committed template.
- 25 AUD cannot be the application allowance under the corrected 10 AUD ceiling. The chosen application default is 6 AUD.
- Catalog-listed is not deployed or evaluated. No validated Azure inference or Foundry orchestration is claimed.
- SQLite implements the Phase 0 ledger/log. Delta, Unity Catalog, embeddings, obligation records, control implementations, risk models, agents, MCP and an evaluation corpus remain later work.

## Verification and next gate

Run `pytest`, `python scripts/check_boundaries.py` and `python -m src`. Tests deny network connections and cover competing reservations, restart ambiguity, usage settlement, retries, caching, configuration errors and import boundaries.

Before Phase 6: re-check prices, retirement dates, subscription quota/capacity and deployment identity; replace and validate the PII stub; then run a bounded live evaluation. None of that evaluation is part of Phase 0.

Sources checked 12 September 2026: [Azure budgets](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets), [spending limits](https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/spending-limit), [budget API](https://learn.microsoft.com/en-us/rest/api/consumption/budgets/create-or-update?view=rest-consumption-2024-08-01).
