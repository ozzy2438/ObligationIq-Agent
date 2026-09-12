# ADR-002: Deterministic versus LLM boundary

## Context

The brief fixes compliance decisions in deterministic code. A model may retrieve, draft and explain evidence, never decide compliance status.

## Decision

PENDING — detailed design is deferred to its build phase.

## Consequences

CI already blocks imports from the gateway and LLM SDKs in controls; control-result schemas remain undecided.
