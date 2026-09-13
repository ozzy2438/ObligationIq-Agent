# Non-functional requirements and runbook controls

| Area | Pilot requirement | Evidence / measured result | Production gap |
|---|---|---|---|
| Correctness | All 32 eligible obligations have a version-bound control; missing evidence cannot become compliant | 72-case result: recall 1.0000, precision 0.9118, FPR 0.0732, exact status 0.9306 | Five hard-case errors remain; legal and operational validation required |
| Reproducibility | Fixed seed, source/code hashes and offline replay | Population reproduces exactly; CI replays Phases 3–7 | Upstream downloads and external Azure service behavior can drift |
| Cost | Hard 1 AUD/day, 6 AUD application lifetime, 10 AUD ceiling | Confirmed 0.035471 AUD; conservative 0.039036 AUD; held 0 | Ledger does not govern other clients/resources or reconcile invoices |
| Latency | Measure, do not promise | Nano mean 3.345 s; mini 4.774 s over 69 metered responses each | No percentile SLA, load or availability test |
| Capacity handling | Serial execution; release deterministic pre-execution rejection; bounded retry | 3 nano and 29 mini 429s released at zero; run completed | 10,000 TPM remained unchanged; throughput is unsuitable for production |
| Privacy | Customer name, address and NMI do not enter model payload | Active schema boundary and Phase 6 verification | Unstructured customer prose unsupported |
| Auditability | Bind result to obligation/source version and disclose review composition | Every result carries digests; 2/32 human, 30/32 agent reviewed | Local logs lack central retention and independent attestation |
| Availability | Offline controls and cache remain usable without Azure | Dry-run and cached tests deny/fail closed on network use | No HA, backup, restore-time or disaster-recovery target |
| Security | No secret in Git; model calls only through gateway | CI boundary checks and GitGuardian passed | No production IAM, network isolation or penetration test |
| Portability | Python 3.11+; local SQLite/Delta/MLflow/MCP | CI on Python 3.12; local verification on 3.14 | Native optional dependencies may vary by platform |

## Failure runbook

1. **Structured 429:** verify status 429 and complete `rate_limit_exceeded` body. Release reservation, retain zero-cost log, obey `Retry-After`, continue serially for at most six attempts. Do not raise TPM without owner awareness.
2. **No response or mid-stream loss:** classify ambiguous, settle at reserved maximum, log `ambiguous_settlement`, and rerun. Halt on the sixth ambiguous settlement in one run or before a budget breach.
3. **Pre-dispatch failure:** release the reservation. Recheck Entra login, ARM readback, endpoint, deployment identity and price age before retrying.
4. **Digest mismatch:** stop eligibility. Reacquire or review the exact changed source/record; never substitute a nearby document silently.
5. **Ledger refusal:** stop. Inspect held/reserved rows and provider evidence; never delete or edit the database to create headroom.
6. **Price drift:** re-pin upward at stored precision. Halt only when the planned maximum reservation changes by more than 10% or the requested model price is absent.

The Phase 7 defect demonstrates why step 1 is an NFR rather than bookkeeping detail. Five deterministic capacity rejections were treated as uncertain execution, adding 0.003565 AUD to conservative cost and exhausting the ambiguity gate. Cost-control correctness therefore depends on classifying whether provider execution could have occurred.
