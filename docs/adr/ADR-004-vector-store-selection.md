# ADR-004: Vector store selection

## Context

The Phase 1 corpus has ten public regulatory documents and requires precise source citations, persisted vectors, and zero external model cost during development. The owner authorised continuation after Phase 0 within a 10 AUD total ceiling.

## Decision

Accepted for the local pilot. Store full extracted pages, source metadata and clause-linked embedding windows in SQLite. Use an exact cosine scan over the small corpus, with an explicit regime and snapshot-date filter. Default retrieval is a deterministic lexical cosine baseline; semantic retrieval is a separate option, with no quality-superiority claim.

Use `sentence-transformers/all-MiniLM-L6-v2`, revision and file hashes pinned in `src/gateway/local-model.json`, on the local CPU through ONNX Runtime. Use attention-masked mean pooling and L2 normalisation as documented by the model publisher. Each input window contains up to 224 content tokens, overlapping by 32, below the model's 256-token limit. Long clauses retain their parent reference, and no input is silently truncated.

All tokenisation and inference SDK imports stay inside the sole model-call module. Local execution requires an independent `LOCAL_EMBEDDING_ENABLED=true` flag and always calls the redaction interface. Public corpus processing does not enable or impersonate Azure live mode. Downloads are explicit, checksum-verified setup actions; model execution has no network fallback.

The embedding cache identity includes the entire model pin, pooling configuration and input after the redaction hook. Completed vectors are committed per batch and reused across source/index rebuilds. The corpus fingerprint binds source manifest, model and parser code. A repeated unchanged build reuses the persisted index without re-parsing or inference.

## Consequences

No managed search service, remote embedding charge, API key, Databricks or Unity Catalog is needed for Phase 1. CPU, electricity and download costs are unmeasured. SQLite and exact scans are suitable for this bounded corpus, not a production scalability claim. Apache-2.0 model licensing does not change the source documents' licences.

The Azure embedding route remains deferred. Later evaluation may compare local and Azure retrieval only through the budgeted gateway; vector spaces must never be mixed. No source/embedding artifact is committed, and source material with restricted terms is not granted commercial redistribution rights by this ADR. Benchmark semantic retrieval against the lexical baseline before making quality claims.
