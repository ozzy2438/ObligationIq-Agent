# STRIDE threat model

Scope: the local pilot, its explicit Azure model boundary, public-source acquisition and committed evaluation artefacts. Production systems and CRM are outside scope.

| Threat | Scenario | Existing mitigation | Residual risk / next control |
|---|---|---|---|
| Spoofing | Wrong Azure tenant, account or deployment receives a prompt | Tenant-bound Entra credential; ARM identity, endpoint, region, model/version and SKU checked before dispatch | Use managed identity and private network controls on a future host |
| Spoofing | Unreviewed register row appears eligible | Source/record/operational-review digests and reviewer provenance must all match | Separate approver and signed review records for production |
| Tampering | Source PDF, parser, model asset or evaluation changes silently | SHA-256 source/model pins and frozen code/data manifest | Signed release provenance and protected review rules remain absent |
| Tampering | Model narrative changes compliance result | Control status is deterministic and immutable; critic checks fixed fields | Human evidence-pack review is still needed for operational use |
| Repudiation | Paid call or escalation cannot be explained | Atomic reservation and structured call/reconciliation logs; fixed escalation codes | Local SQLite has no append-only external retention |
| Information disclosure | Customer identity reaches Azure | Allowlisted schema, recursive sensitive-key removal and NMI/address/value redaction | Unstructured prose is refused because general PII detection is unproven |
| Information disclosure | Raw sources, prompts or cache enter the public repository | Gitignore and tracked-file CI checks; public outputs retain hashes only | Local host backup/access policy is outside this build |
| Denial of service | Low TPM produces repeated 429s | Serial calls, `Retry-After`, capped backoff, six-attempt limit; reservations released | Evaluation latency rises; production needs queueing and capacity planning |
| Denial of service | Ambiguous failures consume project allowance | Maximum-five recovery policy and hard budget admission | Repeated transport loss intentionally halts rather than weakening accounting |
| Elevation of privilege | Agent bypasses controls or writes external systems | No control import of LLM; one read-only MCP evidence tool; no CRM adapter | Production requires tool authorization and least-privilege service identities |

## Abuse cases checked

- A free-form prompt cannot become live-ready.
- A missing or unknown model price cannot be reserved.
- A stale price or deployment mismatch fails before inference.
- A cache miss in cached mode does not fall through to live.
- Missing evidence cannot resolve to compliant.
- A changed source or record digest removes control eligibility.
- A complete 429 does not consume spend or the ambiguity count; a response-less failure cannot claim the same treatment.
