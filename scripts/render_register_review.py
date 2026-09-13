"""Generate the public, paraphrased human-review pack from candidate records."""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT
from src.register.obligations import CANDIDATES, load_candidates, reviewed_records


def render(records):
    records = reviewed_records(records)
    human = sum(r["verified_by_human"] for r in records)
    approved = sum(r["review_status"] == "APPROVED" for r in records)
    snapshot = hashlib.sha256(CANDIDATES.read_bytes()).hexdigest()
    lines = ["# Phase 2 — source review decisions", "",
             f"**{len(records)} records; {approved} APPROVED ({human} human, {approved-human} authorised agent); {len(records)-approved} pending; 0 operational controls enabled.**", "",
             "Approval means the requirement, trigger, action and timing match the cited authoritative text in the 12 September 2026 snapshot. It is not a customer-level legal determination, proof of every jurisdictional modification, or permission to disconnect/deregister. State lists identify source coverage; concrete applicability and calendar logic remain separate implementation gates.", "",
             "The owner explicitly authorised autonomous source review after personally approving OIQ-024 and OIQ-025. Authorised agent approvals do not set verified_by_human=true. Every decision is bound to the reviewed candidate and source digests; changes require review again.", "",
             f"Candidate snapshot SHA-256: `{snapshot}`.", "",
             "[Versioned candidates](../data/obligation-candidates.json) · [Human decisions](../data/human-reviews.json) · [Agent decision audit](../data/source-reviews.json) · [Consolidated review](review-summary.md)", ""]
    for r in records:
        unit = r['deadline_unit'].replace('_', ' ') if r['deadline_unit'] else ''
        if r['deadline_value'] == 1:
            unit = unit.removesuffix('s')
        duration = ("No numerical deadline asserted." if r["deadline_value"] is None else
                    f"{r['timing_operator'].replace('_', ' ')} {r['deadline_value']} "
                    f"{unit}; anchor: {r['timing_anchor']}.")
        source = f"{r['source_url']}#page={r['source_page_start']}"
        lines.extend([f"<a id=\"{r['obligation_id'].lower()}\"></a>", "",
                      f"## {r['obligation_id']} — {r['regime']} / {r['obligation_family'].replace('_', ' ')}", "",
                      f"**Trigger:** {r['trigger_event']}", "",
                      f"**Action:** {r['required_action']}", "",
                      f"**Timing:** {duration}", "",
                      f"**Source:** [{r['instrument']}, version {r['source_version']}, clause {r['clause_reference']}]({source}); physical PDF pages {r['source_page_start']}–{r['source_page_end']}.", "",
                      "**Proposed evidence:** " + ", ".join(r["evidence_required"]) + ".", "",
                      "**Context and implementation notes:** " + " ".join(r["pending_checks"]), "",
                      f"**Decision:** {r['review_status']} — {r['verification_date'] or 'not verified'}; {r['verification_method']}; reviewer: {r['reviewer']}.", "",
                      "**Reasoning:** " + r["review_reasoning"], "",
                      "**Correction:** " + r["review_correction"], ""])
    return "\n".join(lines)


def summary(records):
    resolved = reviewed_records(records)
    human = sum(r["verified_by_human"] for r in resolved)
    agent = sum(r["review_status"] == "APPROVED" and r["verification_method"] == "agent_source_review" for r in resolved)
    pending = sum(r["review_status"] != "APPROVED" for r in resolved)
    lines = ["# Consolidated obligation review", "", "Review date: **12 September 2026**.", "",
             f"**{human+agent} APPROVED: {human} explicit human decisions and {agent} authorised agent source reviews. {pending} PENDING HUMAN REVIEW.**", "",
             "The owner approved OIQ-025 and explicitly authorised autonomous approval/correction of unambiguous source matches. This supersedes the earlier requirement to wait for individual human decisions. The agent reviews are labelled as agent reviews; only OIQ-024 and OIQ-025 set verified_by_human=true. Approved rows receive their review date in the resolved register and Delta snapshot.", "",
             "## Scope and evidence", "",
             "All 30 remaining records were read against the pinned authoritative clauses, including relevant chapeaux, exceptions and nearby provisions. Source content, triggers, actions and timing were checked; string/hash matching alone was not treated as semantic approval. The automated verifier separately re-extracts all 32 parent clauses and checks their source hashes. Human-approved drafts were left unchanged.", "",
             "APPROVED means source-content agreement for the 12 September 2026 snapshot. It does not certify actual customer facts, every jurisdictional modification, a production control or a regulatory outcome. No unresolved ambiguity remains in the reviewed atomic source requirements; customer/contract applicability, calendars and execution remain separate implementation work. No invented deadline or annual reconfirmation duty was added.", "",
             "The supplemental [Electricity Industry Act 2000, authorised version 107](https://www.legislation.vic.gov.au/in-force/acts/electricity-industry-act-2000/107), effective 9 September 2026, resolves the 40SG(1)/40SH(1) registration-pathway references used in OIQ-021 and OIQ-022. It is checksum-pinned in [review-sources.json](../data/review-sources.json), retained locally and not embedded. This does not claim completion of all state-specific application-law review.", "",
             "## Corrections and clarifications", "",
             "Twenty of the 30 agent-reviewed drafts changed before approval; ten matched without changes. The per-record audit preserves the before/after digest and reason. Material changes include:", "",
             "- OIQ-001: restored intended residents and the equipment-required date.",
             "- OIQ-002: made the all-conditions exception and surviving information duties explicit.",
             "- OIQ-003/004: specified the relevant medical-form pathway.",
             "- OIQ-005/006/017/018: distinguished reminder provision from document issue while preserving the minimum 15-business-day interval.",
             "- OIQ-009: identified communications under rules 124A and 125.",
             "- OIQ-011–015: removed a generic licensed-retailer label; OIQ-013 now triggers on a plan offer, and OIQ-015 preserves the scoped rule 33 exceptions and affected-customer proviso.",
             "- OIQ-021/022: resolved the Act cross-reference and made trigger/content scope explicit.",
             "- OIQ-026: corrected retailer versus customer election and avoided inventing a full-billing-cycle extension length.",
             "- OIQ-030/031: placed the arrears-on-hold exclusion in the trigger.",
             "- OIQ-032: restored the right of any residential customer requesting a policy copy.", "",
             "## Decision audit", "",
             "Each row links to the full source, requirement, reasoning, correction and evidence description. The JSON logs retain the exact reviewed digests: [human decisions](../data/human-reviews.json) and [agent decisions](../data/source-reviews.json). The two human decisions are conversation approvals transcribed by the assistant, not independent agent assertions of human review.", "",
             "| OIQ ID | Source / clause | Decision | Reviewer type | Verification date |",
             "|---|---|---|---|---|"]
    for r in resolved:
        anchor = r['obligation_id'].lower()
        lines.append(f"| [{r['obligation_id']}](phase-2-review.md#{anchor}) | {r['source_id']} {r['clause_reference']} | {r['review_status']} | {'Human' if r['verified_by_human'] else 'Authorised agent'} | {r['verification_date'] or '—'} |")
    lines += ["", "## Validation and remaining project work", "",
              "The test suite checks stale decisions, reviewer provenance, pending decisions, replay and historical Delta snapshots, alongside the gateway cost controls. The [generated verification](phase-2-verification.json) records counts and source checks. The source-review queue is complete; Unity Catalog and operational applicability/execution have not been implemented. Phase 3 was not started by this review task. No Azure deployment or paid model call was made.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    records = load_candidates()
    (ROOT / "docs/phase-2-review.md").write_text(render(records))
    (ROOT / "docs/review-summary.md").write_text(summary(records))
