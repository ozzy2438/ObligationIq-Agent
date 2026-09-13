# Cost model

Generated from the durable gateway SQLite ledger on 13 September 2026. The committed Phase 7 result carries the exact public ledger summary so CI can reproduce this document without publishing the private cache or call log. Rates are pinned Australia East Azure retail estimates in AUD; this is not an invoice reconciliation.

| Figure | AUD | Meaning |
|---|---:|---|
| Confirmed metered spend | 0.035471 | Successful responses priced from returned token usage. |
| Conservative ledger total | 0.039036 | Confirmed spend plus settlements retained at reserved maximum. |
| 429 misclassification overstatement | 0.003565 | Five historical capacity rejections settled before ADR-009; retained, not treated as metered spend. |
| Other ambiguous settlements | 0 | Uncertain outcomes still charged at maximum. |
| Held reservations | 0 | Unresolved amount blocking admission. |

The confirmed total consumed 0.5912% of the 6 AUD application limit and 3.5471% of the 1 AUD daily limit. The conservative total consumed 0.6506% of the application limit. The separate 10 AUD project ceiling was not approached.

| Route | Model | Metered responses | Prompt tokens | Completion tokens | Confirmed AUD | Confirmed AUD / 72 cases |
|---|---|---:|---:|---:|---:|---:|
| cheap | `gpt-5-nano` | 69 | 21,504 | 7,046 | 0.005451 | 0.0000757083 |
| strong | `gpt-5-mini` | 69 | 21,504 | 8,094 | 0.030020 | 0.0004169444 |

There were 72 cases per model arm and 69 metered responses per model because three exact duplicate prompts reused the disk cache. The per-case denominator remains 72. Reasoning tokens are included within completion tokens and are not charged twice. The cheap arm's conservative total is 0.008303 AUD because 0.002852 AUD of the known 429 overstatement is bound to nano reservations; the remaining historical settlement lacks a reliable model binding and appears only in the project total.

Capacity rejections with a complete `rate_limit_exceeded` response cost zero in the ledger: 3 for nano and 29 for mini. A malformed response, connection drop or mid-stream timeout remains ambiguous and settles at maximum. Cache replay of all 144 model-arm case executions added 0 AUD.

Excluded: tax, negotiated Azure pricing, FX movement after the pin date, local CPU/electricity, downloads, storage outside the process, and unrelated subscription resources. Staff time saved, penalties avoided, customer satisfaction and ROI are unmeasured.
