"""Generate the public, paraphrased human-review pack from candidate records."""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT
from src.register.obligations import CANDIDATES, load_candidates, reviewed_records


def render(records):
    records = reviewed_records(records)
    approved = sum(r["verified_by_human"] for r in records)
    snapshot = hashlib.sha256(CANDIDATES.read_bytes()).hexdigest()
    lines = ["# Phase 2 — human review required", "",
             f"**{len(records)} candidates; {approved} human approvals; 0 records eligible for controls.**", "",
             "These are paraphrases for review, not legal conclusions. The linked PDF opens at the physical page containing the parent clause; read the full subclause and its exceptions. Jurisdictional applicability is still pending. This pack does not authorise disconnection or deregistration.", "",
             "For each record, confirm or correct its trigger, action, timing direction, exceptions, jurisdiction and proposed evidence. Report the obligation ID and corrections; approval must identify the reviewer and date and bind the reviewed content. A source-trace check alone is not approval. No blanket approval is inferred from continuing the build.", "",
             f"Candidate snapshot SHA-256: `{snapshot}`.", "",
             "[Immutable candidate drafts](../data/obligation-candidates.json) · [Human decisions](../data/human-reviews.json) · [Implementation and outstanding gates](phase-2-register.md)", ""]
    for r in records:
        unit = r['deadline_unit'].replace('_', ' ') if r['deadline_unit'] else ''
        if r['deadline_value'] == 1:
            unit = unit.removesuffix('s')
        duration = ("No numerical deadline asserted." if r["deadline_value"] is None else
                    f"{r['timing_operator'].replace('_', ' ')} {r['deadline_value']} "
                    f"{unit}; anchor: {r['timing_anchor']}.")
        source = f"{r['source_url']}#page={r['source_page_start']}"
        lines.extend([f"## {r['obligation_id']} — {r['regime']} / {r['obligation_family'].replace('_', ' ')}", "",
                      f"**Trigger:** {r['trigger_event']}", "",
                      f"**Action:** {r['required_action']}", "",
                      f"**Timing:** {duration}", "",
                      f"**Source:** [{r['instrument']}, version {r['source_version']}, clause {r['clause_reference']}]({source}); physical PDF pages {r['source_page_start']}–{r['source_page_end']}.", "",
                      "**Proposed evidence:** " + ", ".join(r["evidence_required"]) + ".", "",
                      "**Review checks:** " + " ".join(r["pending_checks"]), "",
                      (f"**Human decision:** APPROVED — {r['verification_date']}; exact-version content review. Operational gates remain open."
                       if r["verified_by_human"] else "**Human decision:** PENDING."), ""])
    return "\n".join(lines)


if __name__ == "__main__":
    (ROOT / "docs/phase-2-review.md").write_text(render(load_candidates()))
