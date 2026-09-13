# Security control matrix

| Objective | Implemented pilot control | Evidence | Residual limitation |
|---|---|---|---|
| Keep secrets out of Git | `.env` and local state ignored; CI rejects committed `.env*` except `.env.example` | `scripts/check_boundaries.py`; GitHub checks | Developer machine and Azure CLI token-store security are external |
| Minimise model data | Versioned allowlisted JSON envelope; identity fields removed; explicit name/address/NMI and patterns redacted | ADR-003; gateway tests; Phase 6 pack | Not general NER for arbitrary prose |
| Prevent model authority | Status computed by controls and treated as immutable by drafter/critic | ADR-002; Phase 6/7 results | Source interpretation and operational applicability still require governance |
| Confine inference | SDK imports and calls allowed only in `src/gateway/`; controls cannot import gateway | CI boundary script | External tools can bypass the local process |
| Enforce spend | Atomic reserve/commit ledger; daily/lifetime limits; unknown/stale price hard stop | ADR-005, ADR-008, ADR-009; cost model | Retail estimate is not invoice control; deleting ledger defeats continuity |
| Separate failure outcomes | Complete 429 releases; uncertain transport outcome settles at maximum | ADR-009; tests | Provider error-schema changes can turn a rejection into conservative ambiguity |
| Authenticate Azure | Entra Azure CLI token; account/deployment identity checked through ARM before dispatch | Gateway adapter; Azure inventory | Local interactive identity, not managed workload identity |
| Protect local data | Raw PDFs, cache, ledger, Delta, vectors and raw model outputs remain gitignored | `.gitignore`; boundary check | No encryption-at-rest control beyond host facilities is asserted |
| Preserve provenance | SHA-256 pins for sources, clauses, records, reviews, model assets and evaluation manifest | Source inventory; ADR-001/004/007 | Hashes prove identity, not legal correctness |
| Isolate labels | Ground truth under `data/ground_truth/`; CI blocks controls/agents from importing or reading it | Boundary check | Repository maintainers can change both code and benchmark |
| Restrict jurisdiction | Explicit regime and effective-date fields; mismatches are challenge cases | ADR-002/007; Phase 4 error analysis | Two jurisdiction false positives remain published |
| Limit external action | MCP surface is read-only evidence generation; no customer message, CRM write or disconnection action | Phase 6 design | No production authorization framework exists |
| Audit decisions | Structured logs record model, tokens, cost, mode, cache, latency and escalation reason without prompts | Gateway ledger; Phase 7 results | Logs are local and lack central retention/alerting |
| Dependency integrity | Exact dependency versions for optional stacks; local model files checksum-pinned | `pyproject.toml`; local model pin | No SBOM, signing or vulnerability SLA |
