# ADR-002: Deterministic versus LLM boundary

## Context

The brief fixes compliance decisions in deterministic code. A model may retrieve, draft and explain evidence, never decide compliance status.

## Decision

Compliance status is produced only by a pure, deterministic control callable bound to one eligible obligation. Its inputs are the exact obligation record, customer-state facts and an explicit evaluation date. Results retain the applied record/source digests, source version, clause and effective interval. Missing trigger, action, calendar or source-required evidence resolves to `insufficient_evidence`; it can never resolve to `compliant`.

The language-model boundary may retrieve source text, arrange a timeline, draft an evidence pack and critique that draft. It receives the deterministic status as immutable evidence and cannot replace or override it. Controls cannot import the gateway, model SDKs, evaluation code or build scripts. CI enforces these imports and blocks any control or agent reference to the isolated challenge labels.

Business-day controls require a supplied, bounded calendar; no process-wide current calendar is consulted. Month deadlines use calendar-month arithmetic. A result outside the obligation version's effective interval is `not_applicable`.

## Consequences

There are 32 small bound control callables backed by a common evaluator, avoiding 32 copies of deadline and evidence logic while preserving one dispatch identity per obligation. A new eligible obligation fails the coverage check until a control is bound. The shared state schema is intentionally narrow and needs an adapter before real operational records can be evaluated.

The synthetic benchmark exercises six obligations and all five statuses are defined, but only `compliant`, `breach` and `insufficient_evidence` are measured in Phase 4. Production public-holiday calendars, source-system completeness assertions and case-specific applicability remain outside this local pilot.
