# ADR-009: Capacity rejection classification and retry

## Context

During Phase 7, Azure returned structured HTTP 429 `rate_limit_exceeded` responses after the GPT-5 nano deployment exhausted its allocated throughput. The gateway classified every post-dispatch exception as ambiguous, conservatively settled five rejected requests at 713 micro-AUD each, and then halted at the per-run ambiguity limit. The provider had returned a complete rejection before inference, so this classification overstated ledger cost by 3,565 micro-AUD.

## Decision

Accepted on 13 September 2026. A 429 is `capacity_rejected` only when the SDK exposes HTTP status 429 and a well-formed response body with code `rate_limit_exceeded` and a non-empty message. The reservation is released in full and does not count toward ADR-008's ambiguous-settlement limit.

The gateway runs serially. It honours numeric `Retry-After` or `retry-after-ms`; otherwise it uses exponential backoff with jitter, capped at 60 seconds. Six total attempts are allowed for one call. A sixth rejection releases its reservation and stops that call. A malformed 429, mid-stream timeout or connection drop without a complete response remains ambiguous and is settled at maximum under ADR-008.

The five historical settlements are not reversed. Their reconciliation reason is `overstated_due_to_misclassification`; confirmed metered usage, conservative ledger total and this known overstatement are reported separately.

## Consequences

Capacity pressure no longer consumes the ambiguity budget or silently inflates per-case unit cost. Response-body validation prevents a network failure from masquerading as a safe rejection. The deployment remains at 10,000 allocated tokens per minute and evaluation concurrency remains one. Retry can increase latency; it cannot exceed six attempts for a call.
