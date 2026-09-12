# ADR-006: Cloud target and local fallback

## Context

The brief targets Azure/Databricks, while the current task authorises Phase 0 only, no model deployment, and a 10 AUD total ceiling. Local development must work without fabricating cloud identifiers.

## Decision

Accepted for Phase 0. Use ordinary Python and local SQLite for the gateway ledger, response cache and call logs. Leave register, data plane, controls, risk, agents, MCP and evaluation as empty packages. Do not deploy Databricks, managed search, storage or API Management now.

Configuration loads from .env and environment overrides. All Section 3 keys remain in the empty template. Requiredness is mode-specific: dry_run/cached need no cloud credentials; live requires an independent enable flag and validated Azure identity/resource identifiers. Unused Databricks keys remain optional until the data plane exists. No silent provider fallback is allowed.

The intended tiers are GPT-5 nano, GPT-5 mini and text-embedding-3-small in an australiaeast account with Global Standard. Catalog listing and public pricing were checked; quota, capacity and live inference are unverified. No alternative region is needed from current catalog evidence. Global Standard can process outside Australia and must not be described as regional-only inference.

Use the existing Entra Azure CLI identity for a future local live evaluation; no API keys. A managed identity on a future Azure host remains a later deployment decision. Model account, endpoint, version and SKU must match the pinned price before dispatch.

## Consequences

Phase 0 can be reproduced without Azure SDKs or an Azure account. The optional Azure adapter is not evidence of a deployed Foundry system. Local SQLite is not Delta Lake or Unity Catalog; their operational and access-control guarantees are not claimed.

Before Phase 6 re-check model prices, retirement dates, capacity and subscription quota; implement and validate PII handling; then perform a small, budgeted real evaluation. No Phase 1 corpus acquisition or Phase 6 deployment/evaluation is part of this delivery.
