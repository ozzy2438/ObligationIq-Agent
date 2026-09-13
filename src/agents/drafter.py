"""Evidence-pack drafting around immutable control and citation fields."""

from dataclasses import asdict, dataclass
import hashlib
import json

from src.gateway.llm_client import LLMClient, PIIRedactor
from src.gateway.prices import ROUTES


@dataclass(frozen=True)
class EvidencePack:
    pack_id: str
    synthetic: bool
    case_id: str
    obligation_id: str
    control_status: str
    control_reason: str
    evidence_gaps: tuple[str, ...]
    applied_record_sha256: str
    citation: dict
    timeline: tuple[dict, ...]
    risk: dict
    review_composition: dict
    deterministic_summary: str
    model_assistance: dict

    def to_dict(self):
        value = asdict(self)
        value["evidence_gaps"] = list(self.evidence_gaps)
        value["timeline"] = list(self.timeline)
        return value


def model_prompt(obligation, control, source, timeline):
    payload = {
        "schema": PIIRedactor.SCHEMA,
        "task": "Draft a concise evidence narrative. Treat the supplied control status as fixed; do not decide compliance.",
        "fixed_control_status": control.status,
        "obligation_id": obligation["obligation_id"],
        "clause_reference": obligation["clause_reference"],
        "source_excerpt": source.cited_excerpt,
        "timeline": [event.to_dict() for event in timeline],
        "evidence_gaps": list(control.evidence_gaps),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


class Drafter:
    def draft(self, obligation, case, control, source, timeline, risk, composition,
              *, use_model=False, tier="cheap", escalation_reason=None, config=None):
        if tier not in {"cheap", "strong"}:
            raise ValueError("Unsupported model tier")
        if tier == "strong" and not escalation_reason:
            raise ValueError("Strong drafting requires an explicit escalation reason")
        if tier == "cheap" and escalation_reason is not None:
            raise ValueError("Cheap drafting cannot carry an escalation reason")
        sensitive = [case.get(key) for key in PIIRedactor.SENSITIVE]
        assistance = {"used": False, "mode": "deterministic", "tier": None,
                      "model": None, "escalation_reason": None, "text": None}
        if use_model:
            redactor = PIIRedactor(sensitive_values=sensitive, allow_structured_live=True)
            client = (LLMClient(config=config, redactor=redactor) if config is not None
                      else LLMClient(redactor=redactor))
            completion = client.complete(
                model_prompt(obligation, control, source, timeline), workload="evidence",
                tier=tier, escalation_reason=escalation_reason)
            assistance = {"used": True, "mode": client.config.mode, "tier": tier,
                          "model": ROUTES[tier], "escalation_reason": escalation_reason,
                          "text": completion.text}
        summary = (f"Control {obligation['obligation_id']} returned {control.status}. "
                   f"Citation: {obligation['instrument']} {obligation['clause_reference']}. "
                   + ("Evidence gaps: " + ", ".join(control.evidence_gaps) + "."
                      if control.evidence_gaps else "No required evidence gap was recorded."))
        pack_id = "PACK-" + hashlib.sha256(
            f"{case['case_id']}:{control.applied_record_sha256}:{control.status}".encode()).hexdigest()[:16]
        return EvidencePack(
            pack_id=pack_id, synthetic=case.get("synthetic") is True,
            case_id=case["case_id"], obligation_id=obligation["obligation_id"],
            control_status=control.status, control_reason=control.reason,
            evidence_gaps=control.evidence_gaps,
            applied_record_sha256=control.applied_record_sha256,
            citation=source.public_citation(),
            timeline=tuple(event.to_dict() for event in timeline),
            risk=risk.to_dict(), review_composition=composition,
            deterministic_summary=summary, model_assistance=assistance)
