"""Working local evidence pipeline. Deterministic controls retain authority."""

import re

from src.agents.critic import critique
from src.agents.drafter import Drafter
from src.agents.retriever import Retriever
from src.agents.timeline import build_timeline
from src.controls.engine import evaluate_control
from src.register.obligations import for_controls, load_candidates, review_composition
from src.risk.baseline import rank_control_result


def build_evidence_pack(case, *, use_model=False, tier="cheap", escalation_reason=None,
                        clause_loader=None, config=None, max_output_tokens=None, strict=True):
    if not isinstance(case, dict) or not re.fullmatch(r"CASE-[0-9a-f]{16}", str(case.get("case_id", ""))):
        raise ValueError("Case requires a pseudonymous CASE identifier")
    obligations = {row["obligation_id"]: row for row in for_controls(load_candidates())}
    try:
        obligation = obligations[case["obligation_id"]]
    except (KeyError, TypeError):
        raise ValueError("Case does not identify an eligible obligation") from None
    control = evaluate_control(obligation, case, case.get("as_of_date"))
    risk = rank_control_result(control)
    retriever = Retriever(clause_loader) if clause_loader is not None else Retriever()
    source = retriever.retrieve(obligation)
    timeline = build_timeline(case)
    pack = Drafter().draft(
        obligation, case, control, source, timeline, risk, review_composition([obligation]),
        use_model=use_model, tier=tier, escalation_reason=escalation_reason, config=config,
        max_output_tokens=max_output_tokens)
    review = critique(pack, obligation, case, control, source)
    if strict and not review.accepted:
        raise ValueError("Evidence critic rejected pack: " + ", ".join(review.issues))
    return pack, review
