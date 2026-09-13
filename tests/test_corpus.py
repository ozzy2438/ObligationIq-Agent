"""Small contract tests. No fabricated customer population or provider calls."""

import json
import sqlite3
from dataclasses import replace

import pytest

from src.dataplane.corpus import (clause_blocks, digest, exact_clause, fingerprint, load_manifest,
                                  search, verified_pdf)
from src.gateway.llm_client import GatewayError, LocalEmbedder, RedactedPrompt
from scripts.acquire_corpus import acquire


def source():
    return {"id": "unit", "sha256": "a" * 64, "regions": [
        {"pages": [1, 2], "kind": "clause", "references": ["124", "124A"],
         "separator": r"[ \t]+(?=[A-Z])", "family": "life_support", "end_pattern": r"^125 Next"}]}


def test_clause_continuation_keeps_pages_and_excludes_next_clause():
    pages = ["124 Registration\n(a) first condition\n", "(b) continuation\n124A Confirmation\ntext\n125 Next\n"]
    result = clause_blocks(source(), pages)
    assert result[0]["page_start"] == 1 and result[0]["page_end"] == 2
    assert "continuation" in result[0]["text"] and "124A" not in result[0]["text"]
    assert "125 Next" not in result[1]["text"]
    assert result == clause_blocks(source(), pages)


def test_missing_or_duplicate_anchor_fails():
    with pytest.raises(ValueError, match="Missing clause anchor"):
        clause_blocks(source(), ["124 Registration", "125 Next"])
    s = source()
    s["regions"] *= 2
    with pytest.raises(ValueError, match="Duplicate clause"):
        clause_blocks(s, ["124 Registration", "124A Confirmation\n125 Next"])


def test_source_and_download_cache_verify_hash_without_network(tmp_path):
    content = b"%PDF test content"
    file = tmp_path / "unit.pdf"
    file.write_bytes(content)
    s = {"id": "unit", "sha256": digest(content)}
    assert verified_pdf(s, tmp_path) == file
    assert acquire("https://example.invalid/source.pdf", file, s["sha256"]) == "verified_cache"
    file.write_bytes(b"changed")
    with pytest.raises(ValueError, match="Missing or changed"):
        verified_pdf(s, tmp_path)
    with pytest.raises(ValueError, match="Local asset changed"):
        acquire("https://example.invalid/source.pdf", file, s["sha256"])


def test_manifest_preserves_regimes_and_real_numbering_gap():
    sources = {s["id"]: s for s in load_manifest()["sources"]}
    assert len(sources) == 10
    assert sources["esc"]["regime"] == "VIC"
    assert sources["nerr"]["regime"] == "NERL_NERR"
    assert sources["b2b"]["version"].startswith("4.01")
    assert "55" not in sources["hardship"]["regions"][0]["references"]
    assert {"54", "56"} <= set(sources["hardship"]["regions"][0]["references"])
    assert all(s["retrieved_on"] == "2026-09-12" for s in sources.values())


def test_local_embedding_opt_in_redaction_cache_and_zero_reservation(config, monkeypatch):
    with pytest.raises(GatewayError, match="LOCAL_EMBEDDING_ENABLED"):
        LocalEmbedder(config)
    config = replace(config, local_embedding_enabled=True)
    seen = []
    class Redactor:
        def redact(self, text):
            seen.append(text)
            return RedactedPrompt("public text")
    first = LocalEmbedder(config, redactor=Redactor())
    monkeypatch.setattr(first, "_run", lambda texts: ([[1.0] + [0.0] * 383 for _ in texts], 2))
    assert first.embed(["original"])[0][0] == 1
    second = LocalEmbedder(config, redactor=Redactor())
    def forbidden(*args):
        pytest.fail("Cache hit must not execute the model")
    monkeypatch.setattr(second, "_run", forbidden)
    assert second.embed(["original"])[0][0] == 1
    assert seen == ["original", "original"]
    assert second.computed == 0 and second.hits == 1
    with sqlite3.connect(config.state_dir / "gateway.sqlite3") as db:
        assert db.execute("SELECT COUNT(*) FROM reservations").fetchone()[0] == 0


def test_lexical_search_is_regime_and_snapshot_scoped(config):
    config = replace(config, corpus_dir=config.state_dir)
    with sqlite3.connect(config.corpus_dir / "corpus.sqlite3") as db:
        db.executescript("CREATE TABLE documents(id,metadata); CREATE TABLE chunks(id,source_id,metadata,vector);")
        db.execute("CREATE TABLE build_info(metadata)")
        db.execute("INSERT INTO build_info VALUES(?)", (json.dumps({"fingerprint": fingerprint()}),))
        for i, regime in enumerate(("VIC", "NERL_NERR")):
            s = dict(regime=regime, valid_from="2026-09-12", retrieved_on="2026-09-12",
                     version="unit", url="https://example.invalid", terms={})
            block = dict(reference="1", text="life support", kind="clause")
            db.execute("INSERT INTO documents VALUES (?,?)", (str(i), json.dumps(s)))
            db.execute("INSERT INTO chunks VALUES (?,?,?,?)", (str(i), str(i), json.dumps(block), "[]"))
    result = search("life support", regime="VIC", as_of="2026-09-12", config=config)
    assert len(result) == 1 and result[0]["regime"] == "VIC"
    assert search("life support", regime="VIC", as_of="2026-10-01", config=config) == []


def test_exact_clause_requires_one_digest_pinned_source(config):
    config = replace(config, corpus_dir=config.state_dir)
    pages = ["124 Registration\n(1) requirement\n125 Next\n"]
    metadata = {**source(), "title": "Unit source", "issuer": "Unit issuer",
                "version": "1", "url": "https://example.invalid/unit", "regime": "NERL_NERR",
                "valid_from": "2026-09-12", "retrieved_on": "2026-09-12", "valid_to": None,
                "terms": {"restriction": "unit-only"},
                "regions": [{"pages": [1, 1], "kind": "clause", "references": ["124"],
                             "separator": r"[ \t]+(?=[A-Z])", "family": "life_support",
                             "end_pattern": r"^125 Next"}]}
    with sqlite3.connect(config.corpus_dir / "corpus.sqlite3") as db:
        db.executescript("CREATE TABLE documents(id,metadata,pages); CREATE TABLE build_info(metadata);")
        db.execute("INSERT INTO build_info VALUES(?)", (json.dumps({"fingerprint": fingerprint()}),))
        db.execute("INSERT INTO documents VALUES (?,?,?)",
                   ("unit", json.dumps(metadata), json.dumps(pages)))
    result = exact_clause("unit", "124", as_of="2026-09-12", config=config)
    assert result["reference"] == "124" and result["text"].startswith("124 Registration")
    with pytest.raises(ValueError, match="absent or ambiguous"):
        exact_clause("unit", "999", as_of="2026-09-12", config=config)
