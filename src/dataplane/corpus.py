"""Offline, source-pinned corpus. Text is evidence, never executable instructions."""

import hashlib
import json
import re
import sqlite3
from pathlib import Path

from src.config import ROOT, settings

MANIFEST = ROOT / "data/source-manifest.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fingerprint():
    files = [MANIFEST, Path(__file__), ROOT / "src/gateway/local-model.json",
             ROOT / "src/gateway/llm_client.py"]
    return digest(b"".join(f.read_bytes() for f in files))


def load_manifest(path=MANIFEST):
    manifest = json.loads(path.read_text())
    sources = manifest["sources"]
    if len({s["id"] for s in sources}) != len(sources):
        raise ValueError("Duplicate source identity")
    for source in sources:
        for key in ("title", "issuer", "version", "regime", "jurisdictions", "url",
                    "retrieved_on", "terms", "sha256", "regions"):
            if not source.get(key):
                raise ValueError(f"Incomplete source metadata: {source['id']} / {key}")
        if not re.fullmatch(r"[0-9a-f]{64}", source["sha256"]):
            raise ValueError("Invalid source checksum")
    return manifest


def verified_pdf(source, raw_dir=ROOT / "data/raw"):
    file = raw_dir / (source["id"] + ".pdf")
    if not file.is_file() or digest(file.read_bytes()) != source["sha256"]:
        raise ValueError(f"Missing or changed source: {source['id']}; run acquisition")
    return file


def extract_pages(file):
    from pypdf import PdfReader
    pages = [p.extract_text() or "" for p in PdfReader(file).pages]
    if not pages or any(len(t.strip()) < 20 for t in pages):
        raise ValueError("Empty/image-only PDF page requires explicit extraction review")
    return pages


def clause_blocks(source, pages):
    """Curated ranges avoid TOCs and numbering collisions between instruments.

    Exact, ordered references must all resolve. No fuzzy match or invented clause.
    Broader guidance uses explicitly labelled page context, never a clause claim.
    Text, including footnotes, stays unchanged; page offsets trace back to extraction.
    """
    blocks = []
    for region in source["regions"]:
        first, last = region["pages"]
        if not 1 <= first <= last <= len(pages):
            raise ValueError("Invalid source page bounds")
        selected = pages[first - 1:last]
        offsets, total = [], 0
        for page in selected:
            offsets.append(total)
            total += len(page) + 1
        text = "\n".join(selected)
        if region["kind"] == "page_context":
            for page_no, page in enumerate(selected, first):
                blocks.append({"reference": f"PDF page {page_no}", "kind": "page_context",
                               "page_start": page_no, "page_end": page_no, "text": page,
                               "family": region["family"]})
            continue
        starts, cursor = [], 0
        if region.get("start_pattern"):
            opening = re.search(region["start_pattern"], text, re.M)
            if not opening:
                raise ValueError(f"Missing opening anchor: {source['id']}")
            cursor = opening.start()
        for ref in region["references"]:
            pattern = r"(?m)^[ \t]*" + re.escape(ref) + region["separator"]
            match = re.compile(pattern).search(text, cursor)
            if not match:
                raise ValueError(f"Missing clause anchor: {source['id']} / {ref}")
            starts.append((ref, match.start()))
            cursor = match.end()
        end = len(text)
        if region.get("end_pattern"):
            match = re.compile(region["end_pattern"], re.M).search(text, cursor)
            if not match:
                raise ValueError(f"Missing end anchor: {source['id']}")
            end = match.start()
        for i, (ref, start) in enumerate(starts):
            stop = starts[i + 1][1] if i + 1 < len(starts) else end
            page_at = lambda pos: first + max(j for j, off in enumerate(offsets) if off <= pos)
            blocks.append({"reference": ref, "kind": "clause", "family": region["family"],
                           "page_start": page_at(start), "page_end": page_at(stop - 1),
                           "text": text[start:stop]})
    keys = [(b["kind"], b["reference"]) for b in blocks]
    if len(keys) != len(set(keys)):
        raise ValueError(f"Duplicate clause reference: {source['id']}")
    for block in blocks:
        block["id"] = digest(json.dumps([source["id"], source["sha256"], block], sort_keys=True).encode())
    return blocks


def build(config=settings):
    from src.gateway.llm_client import LocalEmbedder
    manifest = load_manifest()
    engine = LocalEmbedder(config)
    config.corpus_dir.mkdir(parents=True, exist_ok=True)
    database = config.corpus_dir / "corpus.sqlite3"
    for source in manifest["sources"]:
        verified_pdf(source)
    if database.is_file():
        with sqlite3.connect(database) as db:
            exists = db.execute("SELECT 1 FROM sqlite_master WHERE name='build_info'").fetchone()
            saved = db.execute("SELECT metadata FROM build_info").fetchone() if exists else None
            if saved and json.loads(saved[0])["fingerprint"] == fingerprint():
                result = json.loads(saved[0])["result"]
                count = db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
                if count != result["chunks"] or db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                    raise ValueError("Persisted corpus failed integrity checks")
                result.update(embedded=0, cache_hits=count, index_reused=True)
                (config.corpus_dir / "last-build.json").write_text(json.dumps(result, indent=2) + "\n")
                return result
    # An interrupted build never replaces a complete searchable corpus.
    rows, documents = [], []
    for source in manifest["sources"]:
        pages = extract_pages(verified_pdf(source))
        blocks = clause_blocks(source, pages)
        documents.append((source["id"], json.dumps(source), json.dumps(pages)))
        for block in blocks:
            for part, window in enumerate(engine.windows(block["text"])):
                rows.append((digest((block["id"] + str(part)).encode()), source["id"],
                             json.dumps({**block, "text": window, "segment": part})))
    vectors = engine.embed([json.loads(row[2])["text"] for row in rows])
    result = {"manifest_sha256": digest(MANIFEST.read_bytes()), "documents": len(documents),
              "chunks": len(rows), "embedded": engine.computed, "cache_hits": engine.hits,
              "model": engine.pin["model"], "model_revision": engine.pin["revision"],
              "estimated_aud": "0", "azure_calls": 0, "network_required": False,
              "index_reused": False}
    with sqlite3.connect(database) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY, metadata TEXT, pages TEXT);
            CREATE TABLE IF NOT EXISTS chunks(id TEXT PRIMARY KEY, source_id TEXT, metadata TEXT, vector TEXT);
            CREATE TABLE IF NOT EXISTS build_info(metadata TEXT);
        """)
        db.execute("BEGIN IMMEDIATE")
        db.execute("DELETE FROM documents")
        db.execute("DELETE FROM chunks")
        db.execute("DELETE FROM build_info")
        db.executemany("INSERT INTO documents VALUES(?,?,?)", documents)
        db.executemany("INSERT INTO chunks VALUES(?,?,?,?)",
                       [(*row, json.dumps(vector)) for row, vector in zip(rows, vectors, strict=True)])
        db.execute("INSERT INTO build_info VALUES(?)", (json.dumps({"fingerprint": fingerprint(), "result": result}),))
    (config.corpus_dir / "last-build.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def search(query, *, regime, as_of, limit=5, method="lexical", config=settings):
    """Small exact vector scan. No agent, compliance decision, or managed search claim."""
    from datetime import date
    import math
    from collections import Counter
    when = date.fromisoformat(as_of)
    if regime not in {"NERL_NERR", "VIC"} or not 1 <= limit <= 20:
        raise ValueError("Explicit supported regime and bounded limit required")
    if method not in {"lexical", "semantic"} or not query or not query.strip():
        raise ValueError("Nonempty query and supported retrieval method required")
    path = config.corpus_dir / "corpus.sqlite3"
    if not path.is_file():
        raise ValueError("Build the corpus first")
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
        exists = db.execute("SELECT 1 FROM sqlite_master WHERE name='build_info'").fetchone()
        saved = db.execute("SELECT metadata FROM build_info").fetchone() if exists else None
        if not saved or json.loads(saved[0])["fingerprint"] != fingerprint():
            raise ValueError("Corpus, model or parser pin changed; rebuild before searching")
    vector = None
    if method == "semantic":
        from src.gateway.llm_client import LocalEmbedder
        engine = LocalEmbedder(config)
        if len(engine.windows(query)) != 1:
            raise ValueError("Query exceeds local embedding window")
        vector = engine.embed([query])[0]
    query_terms = Counter(re.findall(r"[a-z]+", query.lower()))
    matches = []
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
        sources = {i: json.loads(m) for i, m in db.execute("SELECT id, metadata FROM documents")}
        for identifier, source_id, metadata, raw_vector in db.execute("SELECT * FROM chunks"):
            s = sources[source_id]
            if s["regime"] not in {regime, "NEM_CONTEXT"}:
                continue
            # Snapshot is not a legal history service or evidence of future currency.
            if (when > date.fromisoformat(s["retrieved_on"]) or
                    when < date.fromisoformat(s["valid_from"]) or
                    (s.get("valid_to") and when > date.fromisoformat(s["valid_to"]))):
                continue
            block = json.loads(metadata)
            if vector is not None:
                score = sum(a * b for a, b in zip(vector, json.loads(raw_vector), strict=True))
            else:
                terms = Counter(re.findall(r"[a-z]+", block["text"].lower()))
                denominator = math.sqrt(sum(n*n for n in terms.values()) * sum(n*n for n in query_terms.values()))
                score = sum(n * terms[t] for t, n in query_terms.items()) / denominator if denominator else 0
            matches.append({"score": score, "chunk_id": identifier, "source_id": source_id,
                            "version": s["version"], "url": s["url"], "regime": s["regime"],
                            "terms": s["terms"], **block})
    # Return different clauses rather than five overlapping windows of one clause.
    result, seen = [], set()
    for item in sorted(matches, key=lambda x: (-x["score"], x["chunk_id"])):
        key = item["source_id"], item["reference"]
        if key not in seen:
            seen.add(key)
            result.append(item)
        if len(result) == limit:
            break
    return result


def exact_clause(source_id, reference, *, as_of, config=settings):
    """Read one exact, source-pinned clause from the local corpus."""
    from datetime import date
    when = date.fromisoformat(as_of)
    path = config.corpus_dir / "corpus.sqlite3"
    if not path.is_file():
        raise ValueError("Build the corpus first")
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
        saved = db.execute("SELECT metadata FROM build_info").fetchone()
        if not saved or json.loads(saved[0])["fingerprint"] != fingerprint():
            raise ValueError("Corpus, model or parser pin changed; rebuild before retrieval")
        row = db.execute("SELECT metadata, pages FROM documents WHERE id=?", (source_id,)).fetchone()
    if row is None:
        raise ValueError("Exact source is absent from the corpus")
    source, pages = json.loads(row[0]), json.loads(row[1])
    if (when < date.fromisoformat(source["valid_from"]) or
            when > date.fromisoformat(source["retrieved_on"]) or
            (source.get("valid_to") and when > date.fromisoformat(source["valid_to"]))):
        raise ValueError("Exact source is unavailable for the requested snapshot")
    matches = [block for block in clause_blocks(source, pages)
               if block["kind"] == "clause" and block["reference"] == reference]
    if len(matches) != 1:
        raise ValueError("Exact clause is absent or ambiguous")
    return {**matches[0], "source_id": source_id, "version": source["version"],
            "url": source["url"], "regime": source["regime"],
            "source_sha256": source["sha256"], "title": source["title"],
            "issuer": source["issuer"], "terms": source["terms"]}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["build", "search"])
    parser.add_argument("--query")
    parser.add_argument("--regime", choices=["NERL_NERR", "VIC"])
    parser.add_argument("--as-of")
    parser.add_argument("--method", choices=["lexical", "semantic"], default="lexical")
    args = parser.parse_args()
    if args.action == "search" and not all((args.query, args.regime, args.as_of)):
        parser.error("search requires --query, --regime and --as-of")
    print(json.dumps(build() if args.action == "build" else
                     search(args.query, regime=args.regime, as_of=args.as_of, method=args.method), indent=2))
