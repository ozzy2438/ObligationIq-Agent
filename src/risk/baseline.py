"""Explainable review priority; this module does not decide compliance."""

from dataclasses import asdict, dataclass
from typing import Protocol


POLICY_VERSION = "rule-baseline-v1"
REVIEW_HORIZON_DAYS = 30
HIGH_PRIORITY_THRESHOLD = 90
_POLICY = {
    "breach": (100, "urgent", "confirmed_control_breach"),
    "insufficient_evidence": (70, "evidence_review", "control_evidence_gap"),
    "at_risk": (60, "monitor", "open_control_before_deadline"),
    "compliant": (0, "routine", "control_compliant"),
    "not_applicable": (0, "routine", "control_not_applicable"),
}


class RankableControl(Protocol):
    case_id: str
    obligation_id: str
    status: str
    evidence_gaps: tuple[str, ...]
    applied_record_sha256: str


@dataclass(frozen=True)
class RiskAssessment:
    case_id: str
    obligation_id: str
    policy_version: str
    review_horizon_days: int
    priority_score: int
    priority_band: str
    reason_codes: tuple[str, ...]
    control_status: str
    evidence_gap_count: int
    applied_record_sha256: str
    is_compliance_decision: bool = False
    is_calibrated_probability: bool = False

    def to_dict(self):
        value = asdict(self)
        value["reason_codes"] = list(self.reason_codes)
        return value


def rank_control_result(control: RankableControl) -> RiskAssessment:
    """Place a version-bound control result in a 30-day review queue."""
    try:
        score, band, reason = _POLICY[control.status]
    except KeyError as error:
        raise ValueError("Unsupported control status") from error
    return RiskAssessment(
        case_id=control.case_id,
        obligation_id=control.obligation_id,
        policy_version=POLICY_VERSION,
        review_horizon_days=REVIEW_HORIZON_DAYS,
        priority_score=score,
        priority_band=band,
        reason_codes=(reason,),
        control_status=control.status,
        evidence_gap_count=len(control.evidence_gaps),
        applied_record_sha256=control.applied_record_sha256,
    )
