"""Verify acquired local assets, source citations and zero-compute replay offline."""

import json
from pathlib import Path
import socket
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT, settings
from src.dataplane.corpus import build, clause_blocks, extract_pages, load_manifest, search, verified_pdf
from src.gateway.llm_client import LocalEmbedder


def deny(*args, **kwargs):
    raise AssertionError("Verification must not access a network or execute the embedding model")


def main():
    # Independent expected PDF page locations; these are citation checks, not human legal approval.
    expected = {("nerr", "124"): 117, ("nerr", "124A"): 121, ("nerr", "125"): 124,
                ("nerl", "44"): 60, ("nerl", "50"): 62, ("esc", "128"): 99,
                ("esc", "129"): 101, ("esc", "163"): 114, ("esc", "166"): 117,
                ("hardship", "37"): 10}
    checks, counts = [], []
    with patch.object(socket.socket, "connect", deny), patch.object(socket, "create_connection", deny), \
            patch.object(socket, "getaddrinfo", deny):
        for source in load_manifest()["sources"]:
            pages = extract_pages(verified_pdf(source))
            assert len(pages) == source["pdf_pages"]
            blocks = clause_blocks(source, pages)
            counts.append({"source": source["id"], "pdf_pages": len(pages), "blocks": len(blocks),
                           "clauses": sum(b["kind"] == "clause" for b in blocks)})
            for b in blocks:
                key = source["id"], b["reference"]
                if key in expected:
                    assert b["page_start"] == expected[key], key
                    assert b["text"].lstrip().startswith(b["reference"]), key
                    checks.append({"source": key[0], "reference": key[1], "pdf_page": expected[key],
                                   "source_sha256": source["sha256"], "result": "pass"})
        assert len(checks) == 10
        # Changed parser pins may require a first rebuild, using existing vector cache.
        build()
        with patch.object(LocalEmbedder, "_run", deny):
            replay = build()
            assert replay["embedded"] == 0 and replay["index_reused"]
            national = search("life support registration medical confirmation", regime="NERL_NERR", as_of="2026-09-12")
            victorian = search("minimum assistance payment difficulties", regime="VIC", as_of="2026-09-12")
        assert national and all(x["regime"] != "VIC" for x in national)
        assert victorian and all(x["regime"] != "NERL_NERR" for x in victorian)
    report = {"status": "passed", "source_counts": counts, "citation_checks": checks,
              "offline_replay": replay, "network_calls": 0, "azure_calls": 0,
              "human_legal_verification": False, "retrieval_quality_evaluated": False}
    (ROOT / "docs/phase-1-verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"sources": len(counts), "citation_checks": len(checks),
                      "chunks": replay["chunks"], "replay_model_calls": 0, "network_calls": 0}))


if __name__ == "__main__":
    main()
