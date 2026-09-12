# ADR-005: Model routing and cost control

## Context

The project ceiling is 10 AUD. Azure budgets are delayed alerts rather than admission controls. Model reasoning, duplicate requests, retries and ambiguous responses must be bounded before spending.

## Decision

Accepted for Phase 0. Use GPT-5 nano by default; GPT-5 mini requires a fixed escalation reason code. Pin AUD model/version/region/SKU prices and source metadata. Development defaults to dry_run, with no network or real-cache writes. Cached mode never falls through to live.

Use one SQLite database for reservations, cache and logs. Defaults: 6 AUD lifetime, 1 AUD per UTC day. BEGIN IMMEDIATE serialises reservation checks and insertion. Only one paid reservation can be active across clients using the same database. Another request refuses until it is resolved. Lifetime totals never reset at midnight.

Reserve full configured input/output token bounds at uncached rates plus 25% headroom. Use integer micro-AUD rounded upward. Output bounds and returned completion usage include reasoning tokens; never add them twice. Returned cached-input counts can lower settled cost. Successful settlement, cache insertion and audit logging share a transaction.

Release only when the adapter confirms no inference request was dispatched. A timeout, crash, invalid usage or unknown response holds the reservation and halts further requests. Retry only confirmed non-dispatch, with a new reservation; default zero retries. Disable SDK retries. No automated hold expiry or ledger reset is provided.

Cache keys cover pinned model identity, prompt after redaction and bounded parameters including endpoint and deployment scope. The cache persists on disk in the same private database. Cache hits create no reservation and log zero incremental usage cost.

Before inference the Azure adapter verifies deployment identity against the pin. Prices older than 31 days refuse live dispatch. The adapter is implemented but unvalidated against a deployed model. The default redactor blocks live use.

## Consequences

Concurrent paid throughput is deliberately sacrificed for simple, auditable crash behaviour. Tests cover competing reservations, restart ambiguity and retry isolation. A held reservation can require manual investigation; independent billing evidence is needed before controlled repair. Deleting the database invalidates the cost history.

Ledger amounts estimate actual token usage using pinned public rates. They do not reconcile an invoice, include taxes, or constrain unrelated resources. The 4 AUD headroom is a margin, not a billing guarantee. No real Azure inference was performed in Phase 0.
