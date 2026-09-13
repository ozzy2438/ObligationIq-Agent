# Phase 6 — agents, MCP and model boundary

Status on 13 September 2026: **complete for the local independent pilot**. Retriever, timeline builder, drafter and critic run as a narrow evidence pipeline. The retriever resolves the exact parent clause from the pinned local corpus and requires its digest, source version, regime and page range to match the reviewed obligation. The timeline retains event types, dates and evidence presence while discarding customer identity and evidence values. The drafter copies the immutable control result into a source-cited pack; the critic rejects citation, digest, status, gap or provenance drift. [Machine-readable evidence](phase-6-agent-results.json).

## Acceptance result

Two synthetic OIQ-024 cases were replayed against the locally retained Energy Retail Code of Practice version 6 clause 166 source block:

| Check | Result |
|---|---:|
| Exact reviewed-clause retrieval | 32 / 32 |
| Flagged breach pack accepted by critic | 1 / 1 |
| Under-evidenced pack accepted by critic | 1 / 1 |
| Citation binding | 2 / 2 |
| Under-evidenced gap recovered | 1 / 1 (`deregistration_event`) |
| Supplied name/address/NMI values in public packs | 0 |
| MCP wrapper calls matching the core pipeline | 1 / 1 |
| Model calls / spend | 0 / 0 AUD |

Each pack cites clause 166(2)(b), PDF pages 117–120, source version 6 and the reviewed source/clause digests. The source text is checked locally and excluded from the committed result under the recorded reuse terms. OIQ-024 is human-verified, so each pack reports one of one underlying obligations human-verified and zero agent-reviewed. These two cases establish pipeline acceptance for one obligation; they do not measure broad agent quality.

## Model and PII boundary

Deterministic drafting is the Phase 6 default. Optional narrative generation builds a versioned, allowlisted JSON envelope containing only the fixed control status, source locator and bounded excerpt, PII-minimised timeline, and evidence-gap names. The gateway removes sensitive-key values, explicit case identity values, labelled NMIs and street-address patterns. Any free-form or nonconforming payload is not live-ready.

The cheap GPT-5 nano route is the default. GPT-5 mini requires an approved explicit escalation reason and the gateway records it. This routing code is present and tested; Phase 6 made no model call, created no deployment and spent nothing. The language model may draft prose and cannot decide or change compliance status.

## MCP surface

The official Python MCP SDK is pinned at `mcp==2.2.0`. A local stdio server exposes one tool, `build_evidence_pack`, which calls the same pipeline. In-memory protocol discovery verified the tool contract, and one protocol call returned the same accepted pack as the core pipeline. No external MCP endpoint, authentication service or production deployment exists.

```sh
python -m pip install -e '.[mcp]'
python scripts/evaluate_agents.py --check
python -m src.mcp_server.server  # starts the local stdio server
```

The portable check validates the committed pack against the current reviewed register and discovers the MCP tool in memory. A checkout that has the rights-restricted local corpus also replays both cases and their source digests. Socket networking is disabled during pipeline evaluation.
