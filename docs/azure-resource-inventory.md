# Azure resource and model inventory

Verified 12 September 2026. Owner: Osman Orka, independent pilot. Subscription identifiers and full management responses remain private under gitignored `.local/`.

## Resources touched during setup

| Resource | Purpose and state | SKU / cost assumption | Owner |
|---|---|---|---|
| `rg-obligationiq-pilot`, `australiaeast` | Project group; no billable workload resources deployed | ARM container, no running compute | Project owner |
| `obligationiq-pilot-aud-10` | Created and independently read back; 10 AUD annual budget | Alert, not a spending switch | Project owner |
| `obligationiq-pilot-aud-3` | Superseded and deleted after verifying replacement | Previous alert only | Project owner |
| Existing `procurelens-demo-usd-2` | Read-only inspection; unchanged; actual currency AUD | 2 AUD monthly subscription alert | Existing project owner |
| Existing `tradeops-sentinel-ai-0805`, `eastus` | Seen in subscription inventory; not used | Cognitive Services S0 | Existing project owner |
| Existing `NetworkWatcher_australiaeast` | Seen in inventory; unchanged | No workload deployed by this project | Subscription owner |

Budget: 2026-09-01 through 2027-08-31; alerts at 5, 7.50, 9 and 10 AUD. Application defaults: 6 AUD lifetime / 1 AUD daily. The budget readback reported zero AUD current spend; this delayed value is not invoice reconciliation.

## Intended models — no deployments created

The subscription-scoped Resource Manager endpoint `Microsoft.CognitiveServices/locations/australiaeast/models?api-version=2025-06-01` returned these entries. The public [regional availability table](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure-region-availability) also lists them.

| Tier | Model / version | Intended type and account region | Catalog status | Input / cached input / output AUD per 1M tokens |
|---|---|---|---|---|
| cheap, default | `gpt-5-nano` / `2025-08-07` | GlobalStandard, australiaeast | GenerallyAvailable | 0.069527 / 0.006953 / 0.556212 |
| strong, explicit escalation | `gpt-5-mini` / `2025-08-07` | GlobalStandard, australiaeast | GenerallyAvailable | 0.347633 / 0.034763 / 2.781061 |
| embed, later phase | `text-embedding-3-small` / `1` | GlobalStandard, australiaeast | GenerallyAvailable | 0.028 / not applicable / not applicable |

All intended tiers are listed in `australiaeast`; **no alternative account region is currently required**. This is catalog evidence, not proof of allocated quota, deployment capacity or successful inference. Re-check before Phase 6. Catalog inference retirement dates were 2027-02-09 for GPT-5 nano/mini and 2028-02-09 for the embedding model.

Global Standard may process in other Azure regions. An Australia East account does **not** establish Australia-only processing. No real customer PII is authorised for this pilot. If Australian processing becomes mandatory, select and reprice a suitable regional offering. GPT-4.1-mini Regional Standard was also listed, but is not a selected route or automatic fallback.

GPT-5 nano has lower published input/output prices than the newer GPT-5 tiers, but quality and total case cost are unmeasured. GPT-5 mini is an escalation candidate, not a claim that it is Azure's strongest model. Reasoning usage can affect total cost; future evaluation must compare measured cost and quality under the same caps.

## Pricing provenance

Rates were retrieved in **AUD** from the public [Azure Retail Prices API](https://prices.azure.com/api/retail/prices), filtering `armRegionName eq 'australiaeast' and contains(productName, 'OpenAI')`. The query returned 628 records under service `Foundry Models`. Seven selected, unmodified public meter records are in [azure-price-snapshot.json](azure-price-snapshot.json), excluding batch, priority, fine-tuning and reserved-capacity pricing.

| Model | Input meter | Cached input meter | Output meter |
|---|---|---|---|
| GPT-5 nano | `d2d9900d-1261-5c9b-853b-d06eeb4eadc6` | `94555e06-2baa-523d-8ed8-788d30b17bd1` | `d8c3f6ce-cd07-50ae-8e9a-9a2445006675` |
| GPT-5 mini | `ab602fda-d355-58b8-807f-8fb285ff7b92` | `9aec16ba-cad6-5719-a78e-331f3adbf2e6` | `5f65e7f0-17ee-5f84-b26e-3961f58df137` |
| Embedding small | `6969beab-83cb-5a0c-ada9-c60c9eadbcc6` | — | — |

GPT-5 units are 1M tokens. Embedding is 0.000028 AUD per 1K, normalised to 0.028 AUD per 1M. No invented FX rate is used. Retail estimates can differ from billing-agreement prices, currency updates and taxes. Reverify before evaluation; the adapter refuses pins older than 31 days.

The [Azure OpenAI pricing page](https://azure.microsoft.com/en-us/pricing/details/azure-openai/) is general context; numerical pins come from the meter records. [Microsoft reasoning documentation](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/reasoning) documents output bounds and reasoning usage; total completion tokens are billed once.

## Deliberately absent resources

No project Azure OpenAI account/deployment, Foundry project, Databricks workspace, warehouse, Unity Catalog, storage, AI Search or API Management instance was created. SQLite and empty packages are not evidence of those cloud services. Deployment names and endpoints remain empty until real resources are selected in a later authorised phase.
