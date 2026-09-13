# ADR-006: Cloud target and local fallback

## Context

The brief targets an Azure/Databricks-shaped solution, but the independent pilot must remain reproducible, cheap and truthful about what is actually deployed. Local components cannot be described as managed cloud services.

## Decision

Accepted and completed for the pilot. Use local SQLite for corpus, vectors, gateway cache/ledger/logs; local Delta for the register; digest-pinned Unity Catalog OSS for catalog registration; and local MLflow for the deterministic risk-policy registry. These components implement the bounded reference behavior without claiming Databricks, managed search or Azure hosting.

Azure is limited to an S0 OpenAI account in Australia East, GPT-5 nano and GPT-5 mini Global Standard deployments, and a 10 AUD resource-group budget alert. Live local evaluation authenticates with the existing tenant-bound Azure CLI identity and verifies ARM account/deployment metadata before dispatch. No API key is stored. Global Standard can process outside Australia.

No Foundry project, Databricks workspace, managed storage, AI Search, API Management or production application was deployed. Azure embeddings remain blocked because the current AUD retail meter cannot be pinned above zero at its published precision. There is no silent model, region or infrastructure fallback.

## Consequences

The repository can replay its tests and committed evidence without Azure credentials or paid calls. The completed 144 agent-case cache replay costs zero. Local Unity Catalog, Delta and MLflow evidence does not establish managed multi-user governance, lineage, row security, availability or support. A future production build needs managed identity, authenticated service boundaries, Australian-processing review, operational source adapters and invoice reconciliation before cloud claims can expand.
