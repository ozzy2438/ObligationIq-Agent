"""Verify the Phase 6 evidence pipeline, citation binding, PII boundary and MCP surface."""

import argparse
import asyncio
import json
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.agents.drafter import model_prompt
from src.agents.pipeline import build_evidence_pack
from src.agents.retriever import Retriever
from src.agents.timeline import build_timeline
from src.config import ROOT, settings
from src.controls.engine import evaluate_control
from src.dataplane.corpus import fingerprint
from src.dataplane.population import build
from src.gateway.llm_client import PIIRedactor
from src.register.obligations import for_controls, load_candidates


OUTPUT = ROOT / "docs/phase-6-agent-results.json"
IDENTITY = {"customer_name": "Jane Example", "address": "12 Sample Street",
            "nmi": "ABC1234567"}


def deny_network(event, args):
    if event.startswith("socket."):
        raise RuntimeError("Agent evaluation must be offline")


def cases():
    inputs = json.loads((ROOT / "data/population-inputs.json").read_text())
    inputs["operational_context"] = json.loads((ROOT / "data/operational-context.json").read_text())
    contract = json.loads((ROOT / "data/population-contract.json").read_text())
    artifacts, _ = build(inputs, contract)
    rows = [json.loads(line) for line in artifacts["control_cases"].splitlines()]
    selected = [row for row in rows if row["obligation_id"] == "OIQ-024" and
                row["case_id"] in {"CASE-94934ce7f41d3aaf", "CASE-b4e1f63411a203ad"}]
    if len(selected) != 2:
        raise ValueError("Expected Phase 6 challenge cases are missing")
    for row in selected:
        row.update(IDENTITY)
        row["business_calendar"] = {
            "calendar_id": "SYNTHETIC-WEEKDAYS-2026-08-09",
            "coverage_start": "2026-08-03", "coverage_end": row["as_of_date"],
            "public_holidays": [],
        }
    return sorted(selected, key=lambda row: row["case_id"])


async def mcp_tool_names():
    from mcp import Client
    from src.mcp_server.server import mcp
    async with Client(mcp) as client:
        return sorted(tool.name for tool in (await client.list_tools()).tools)


async def mcp_build(case):
    from mcp import Client
    from src.mcp_server.server import mcp
    async with Client(mcp) as client:
        result = await client.call_tool(
            "build_evidence_pack", {"case_json": json.dumps(case, sort_keys=True)})
    if result.is_error or len(result.content) != 1 or not hasattr(result.content[0], "text"):
        raise ValueError("MCP evidence tool failed")
    return json.loads(result.content[0].text)


def evaluate(discovered_tools=None, mcp_result=None):
    obligations = for_controls(load_candidates())
    retrieved = [Retriever().retrieve(obligation) for obligation in obligations]
    if any(not item.cited_excerpt for item in retrieved):
        raise ValueError("A reviewed obligation lacks an exact cited excerpt")
    packs = []
    for case in cases():
        pack, review = build_evidence_pack(case)
        public = json.dumps(pack.to_dict(), sort_keys=True).lower()
        if any(value.lower() in public for value in IDENTITY.values()):
            raise ValueError("Evidence pack retained customer identity")
        packs.append({"evidence_pack": pack.to_dict(), "critic": review.to_dict()})
    by_status = {row["evidence_pack"]["control_status"]: row for row in packs}
    if set(by_status) != {"breach", "insufficient_evidence"}:
        raise ValueError("Phase 6 result statuses changed")
    if by_status["insufficient_evidence"]["evidence_pack"]["evidence_gaps"] != ["deregistration_event"]:
        raise ValueError("Under-evidenced case gap changed")
    if mcp_result is not None and mcp_result != by_status["breach"]:
        raise ValueError("MCP wrapper output differs from the working pipeline")

    # Exercise the exact payload sent at the model boundary without dispatching it.
    obligation = next(row for row in obligations if row["obligation_id"] == "OIQ-024")
    under = next(row for row in cases() if row["case_id"] == "CASE-b4e1f63411a203ad")
    control = evaluate_control(obligation, under, under["as_of_date"])
    source = Retriever().retrieve(obligation)
    prompt = model_prompt(obligation, control, source, build_timeline(under))
    safe = PIIRedactor(IDENTITY.values(), allow_structured_live=True).redact(prompt)
    if not safe.live_ready or any(value.lower() in safe.text.lower() for value in IDENTITY.values()):
        raise ValueError("PII boundary did not produce a live-ready redacted envelope")

    tools = discovered_tools if discovered_tools is not None else asyncio.run(mcp_tool_names())
    if tools != ["build_evidence_pack"]:
        raise ValueError("MCP tool surface changed")
    return {
        "status": "Phase 6 complete: cited evidence pipeline and local MCP surface verified",
        "synthetic_evaluation": True,
        "evaluated_on": "2026-09-13",
        "cases": 2,
        "flagged_case": by_status["breach"],
        "under_evidenced_case": by_status["insufficient_evidence"],
        "measurements": {
            "critic_acceptance_rate": 1.0,
            "citation_binding_rate": 1.0,
            "under_evidenced_gap_recall": 1.0,
            "customer_identity_values_in_public_packs": 0,
            "mcp_tools_discovered": tools,
            "mcp_pipeline_calls_verified": 1 if mcp_result is not None else 0,
            "exact_clause_retrieval_coverage": len(retrieved) / len(obligations),
            "exact_clause_retrieval_count": len(retrieved),
            "maximum_cited_excerpt_bytes": max(len(item.cited_excerpt.encode()) for item in retrieved),
        },
        "pii_boundary": {
            "active": True,
            "structured_live_envelope_required": True,
            "excluded_fields": ["customer_name", "name", "address", "service_address", "nmi"],
            "model_dispatches_in_phase_6": 0,
        },
        "source_text": "Verified against the local pinned clause digest; omitted from this public result under the recorded source terms.",
        "scope_limit": "Two synthetic cases exercise one human-verified Victorian obligation. This is pipeline acceptance evidence, not broad agent-quality evaluation.",
        "model_calls": 0,
        "model_spend_aud": 0,
    }


def validate_public_report(report):
    obligations = {row["obligation_id"]: row for row in for_controls(load_candidates())}
    for label in ("flagged_case", "under_evidenced_case"):
        pack = report[label]["evidence_pack"]
        obligation = obligations[pack["obligation_id"]]
        citation = pack["citation"]
        expected = {
            "source_id": obligation["source_id"], "version": obligation["source_version"],
            "url": obligation["source_url"], "regime": obligation["regime"],
            "clause_reference": obligation["clause_reference"],
            "source_sha256": obligation["source_sha256"],
            "source_clause_sha256": obligation["source_clause_sha256"],
        }
        if any(citation.get(key) != value for key, value in expected.items()):
            raise ValueError("Committed evidence pack citation is stale")
        if report[label]["critic"] != {"accepted": True, "issues": []}:
            raise ValueError("Committed evidence pack lacks critic acceptance")
    if report["under_evidenced_case"]["evidence_pack"]["evidence_gaps"] != ["deregistration_event"]:
        raise ValueError("Committed evidence gap is stale")


def corpus_is_current():
    path = settings.corpus_dir / "corpus.sqlite3"
    if not path.is_file():
        return False
    try:
        with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
            saved = db.execute("SELECT metadata FROM build_info").fetchone()
        return bool(saved and json.loads(saved[0])["fingerprint"] == fingerprint())
    except (sqlite3.Error, KeyError, json.JSONDecodeError):
        return False


def main(check=False):
    current_corpus = corpus_is_current()
    tools = asyncio.run(mcp_tool_names())
    mcp_result = asyncio.run(mcp_build(cases()[0])) if current_corpus else None
    sys.addaudithook(deny_network)
    if check:
        committed = json.loads(OUTPUT.read_text())
        validate_public_report(committed)
        if tools != ["build_evidence_pack"]:
            raise ValueError("MCP tool surface changed")
        if current_corpus and evaluate(tools, mcp_result) != committed:
            raise ValueError("Agent evaluation differs from committed evidence")
        print("PASS: evidence citations/provenance and MCP contract verified; full local replay when corpus available; network disabled")
    else:
        report = evaluate(tools, mcp_result)
        validate_public_report(report)
        OUTPUT.write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report["measurements"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    main(parser.parse_args().check)
