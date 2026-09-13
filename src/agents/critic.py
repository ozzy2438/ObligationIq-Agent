"""Deterministic evidence-pack critic; it cannot revise a control result."""

from dataclasses import dataclass
import hashlib
import json

from src.gateway.llm_client import PIIRedactor


@dataclass(frozen=True)
class Critique:
    accepted: bool
    issues: tuple[str, ...]

    def to_dict(self):
        return {"accepted": self.accepted, "issues": list(self.issues)}


def critique(pack, obligation, case, control, source):
    issues = []
    citation = pack.citation
    expected = {
        "source_id": obligation["source_id"],
        "version": obligation["source_version"],
        "url": obligation["source_url"],
        "regime": obligation["regime"],
        "clause_reference": obligation["clause_reference"],
        "parent_clause": obligation["parent_clause"],
        "source_sha256": obligation["source_sha256"],
        "source_clause_sha256": obligation["source_clause_sha256"],
    }
    if any(citation.get(key) != value for key, value in expected.items()):
        issues.append("citation_binding_mismatch")
    if hashlib.sha256(source.text.encode()).hexdigest() != obligation["source_clause_sha256"]:
        issues.append("retrieved_text_digest_mismatch")
    if (pack.control_status != control.status or
            pack.applied_record_sha256 != control.applied_record_sha256):
        issues.append("control_result_changed")
    if tuple(pack.evidence_gaps) != tuple(control.evidence_gaps):
        issues.append("evidence_gap_mismatch")
    if control.status == "insufficient_evidence" and not pack.evidence_gaps:
        issues.append("insufficient_evidence_without_gap")
    composition = pack.review_composition
    if (composition.get("total") != 1 or
            composition.get("human_verified", 0) + composition.get("agent_reviewed", 0) != 1):
        issues.append("review_provenance_missing")
    public = json.dumps(pack.to_dict(), sort_keys=True)
    for key in PIIRedactor.SENSITIVE:
        value = case.get(key)
        if isinstance(value, str) and value and value.lower() in public.lower():
            issues.append("pii_present_in_pack")
            break
    return Critique(not issues, tuple(sorted(set(issues))))
