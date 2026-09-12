"""Offline source trace check; never substitutes for human legal verification."""

import hashlib
import json
import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT
from src.dataplane.corpus import clause_blocks, extract_pages, load_manifest, verified_pdf
from src.register.obligations import REVIEWS, load_candidates, materialize, reviewed_records


def verify_sources(records):
    sources = {s["id"]: s for s in load_manifest()["sources"]}
    blocks = {}
    for sid in {r["source_id"] for r in records}:
        source = sources[sid]
        blocks[sid] = {b["reference"]: b for b in clause_blocks(
            source, extract_pages(verified_pdf(source)))}
    checks = []
    for r in records:
        b = blocks[r["source_id"]][r["parent_clause"]]
        if (hashlib.sha256(b["text"].encode()).hexdigest() != r["source_clause_sha256"]
                or b["page_start"] != r["source_page_start"]
                or b["page_end"] != r["source_page_end"]):
            raise ValueError("Clause provenance changed: " + r["obligation_id"])
        checks.append({"obligation_id": r["obligation_id"], "source": r["source_id"],
                       "parent_clause": b["reference"], "physical_pdf_page": b["page_start"],
                       "parent_text_hash_matches": True})
    return checks


def denied(*args, **kwargs):
    raise AssertionError("Register verification must stay offline")


def main():
    socket.socket.connect = socket.socket.connect_ex = denied
    socket.create_connection = socket.getaddrinfo = denied
    records = load_candidates()
    checks = verify_sources(records)
    first = materialize(records)
    repeat = materialize(records)
    if repeat["written"] or first["version"] != repeat["version"]:
        raise AssertionError("Repeated Delta materialization must be a no-op")
    report = {"snapshot_date": "2026-09-12", "records": len(records),
              "candidate_file_sha256": hashlib.sha256((ROOT / "data/obligation-candidates.json").read_bytes()).hexdigest(),
              "human_reviews_sha256": hashlib.sha256(REVIEWS.read_bytes()).hexdigest(),
              "source_trace_checks": checks, "delta_version": repeat["version"],
              "repeat_delta_writes": 0, "network_connections": 0, "model_calls": 0,
              "human_verified_records": sum(r["verified_by_human"] for r in reviewed_records(records)), "control_eligible_records": 0,
              "unity_catalog_verified": False,
              "limit": "Automated checks establish parent-clause traceability only. Human decisions are separately recorded; unapproved records and operational gates remain pending."}
    (ROOT / "docs/phase-2-verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "source_trace_checks"}))


if __name__ == "__main__":
    main()
