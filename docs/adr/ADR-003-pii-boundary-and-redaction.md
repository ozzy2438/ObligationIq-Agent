# ADR-003: PII boundary and redaction

## Context

Names, addresses and NMIs must not reach a model. Every request invokes the redaction interface.

## Decision

Accepted for the pilot. The agent pipeline discards identity before it builds a timeline or evidence pack. Customer name, service/postal address, NMI and evidence values are not fields in the model payload. The gateway accepts live dispatch only for the versioned `obligationiq-model-boundary-v1` JSON envelope and a fixed top-level allowlist. It recursively replaces sensitive-key values, replaces the case's explicit identity values, and applies additional labelled-NMI and street-address patterns before dispatch.

The payload may contain the immutable control status, obligation/source locator, the exact bounded source excerpt, PII-minimised event types/dates and evidence-gap names. It asks only for narrative drafting. The returned text cannot modify the control result. There is no rehydration step because customer identity is unnecessary for the evidence narrative.

Free-form prompts remain usable in offline `dry_run` mode but are never live-ready. The MCP tool reaches models only through this gateway and the same envelope. The caller must still set both `LLM_MODE=live` and `LLM_ALLOW_LIVE=true`; Phase 6 does neither.

## Consequences

The verified Phase 6 cases place zero supplied customer identity values in public packs or the model envelope. This is a bounded structural control, not general named-entity recognition. A future workload that needs unstructured customer prose requires separate detection and adversarial validation before it can use live mode. No raw prompt or identity value is logged. The policy deliberately sacrifices arbitrary prompting for a smaller auditable boundary.
