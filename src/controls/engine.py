"""Pure, version-bound obligation controls. This module performs no I/O or inference."""

from dataclasses import asdict, dataclass
from datetime import date, timedelta
from typing import Any, Callable


STATUSES = {"compliant", "at_risk", "breach", "insufficient_evidence", "not_applicable"}
MINIMUM_WAIT_CONTROLS = {
    "OIQ-003", "OIQ-005", "OIQ-006", "OIQ-016", "OIQ-017", "OIQ-018", "OIQ-029"
}


@dataclass(frozen=True)
class ControlResult:
    case_id: str
    obligation_id: str
    status: str
    reason: str
    evidence_gaps: tuple[str, ...]
    evaluated_as_of: str
    applied_record_sha256: str
    applied_source_sha256: str
    applied_source_version: str
    applied_clause_reference: str
    applied_effective_from: str | None
    applied_effective_to: str | None
    source_review_method: str
    source_verified_by_human: bool
    operational_review_method: str
    business_calendar_id: str | None

    def to_dict(self):
        result = asdict(self)
        result["evidence_gaps"] = list(self.evidence_gaps)
        return result


def parse_date(value: Any, field: str):
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
    raise ValueError("Invalid ISO date field: " + field)


def add_months(value: date, months: int):
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    days = [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
            31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return date(year, month, min(value.day, days[month - 1]))


def add_business_days(value: date, count: int, holidays: set[date]):
    current = value
    remaining = count
    while remaining:
        current += timedelta(days=1)
        if current.weekday() < 5 and current not in holidays:
            remaining -= 1
    return current


def result(obligation, state, as_of, status, reason, gaps=(), calendar_id=None):
    if status not in STATUSES:
        raise ValueError("Unknown control status")
    return ControlResult(
        case_id=str(state.get("case_id", "UNSPECIFIED")),
        obligation_id=obligation["obligation_id"],
        status=status,
        reason=reason,
        evidence_gaps=tuple(sorted(gaps)),
        evaluated_as_of=as_of.isoformat(),
        applied_record_sha256=obligation["record_sha256"],
        applied_source_sha256=obligation["source_sha256"],
        applied_source_version=obligation["source_version"],
        applied_clause_reference=obligation["clause_reference"],
        applied_effective_from=obligation["effective_from"],
        applied_effective_to=obligation["effective_to"],
        source_review_method=obligation["verification_method"],
        source_verified_by_human=obligation["verified_by_human"],
        operational_review_method=obligation["operational_verification_method"],
        business_calendar_id=calendar_id,
    )


def _evaluate(expected_id, obligation, customer_state, as_of_date, policy="required"):
    """Evaluate only supplied facts; callers retain ownership of applicability inputs."""
    if obligation["obligation_id"] != expected_id:
        raise ValueError("Control/obligation identity mismatch")
    if obligation.get("operational_review_status") != "ELIGIBLE_FOR_EVALUATION":
        raise ValueError("Obligation is not eligible for evaluation")
    if customer_state.get("obligation_id") != expected_id:
        raise ValueError("Customer state belongs to a different obligation")
    as_of = parse_date(as_of_date, "as_of_date")
    effective_from = parse_date(obligation["effective_from"], "effective_from") if obligation["effective_from"] else None
    effective_to = parse_date(obligation["effective_to"], "effective_to") if obligation["effective_to"] else None
    if (effective_from and as_of < effective_from) or (effective_to and as_of >= effective_to):
        return result(obligation, customer_state, as_of, "not_applicable",
                      "The supplied date is outside this exact obligation version's effective interval.")

    trigger = customer_state.get("trigger_occurred")
    if trigger is None:
        return result(obligation, customer_state, as_of, "insufficient_evidence",
                      "Trigger occurrence is not evidenced.", ("trigger_occurred",))
    if trigger is not True:
        return result(obligation, customer_state, as_of, "not_applicable",
                      "The obligation trigger is affirmatively absent.")
    evidence = customer_state.get("evidence")
    if not isinstance(evidence, dict):
        return result(obligation, customer_state, as_of, "insufficient_evidence",
                      "The required evidence map is absent.", tuple(obligation["evidence_required"]))
    gaps = tuple(name for name in obligation["evidence_required"]
                 if not isinstance(evidence.get(name), dict) or evidence[name].get("present") is not True)
    if gaps:
        return result(obligation, customer_state, as_of, "insufficient_evidence",
                      "One or more source-required evidence items are absent.", gaps)

    completed = customer_state.get("action_completed")
    deadline_value = obligation["deadline_value"]
    if deadline_value is None:
        if completed is True:
            return result(obligation, customer_state, as_of, "compliant",
                          "Complete evidence shows the required action occurred; the source sets no standalone numerical deadline.")
        if completed is False and customer_state.get("non_completion_confirmed_at"):
            confirmed = parse_date(customer_state["non_completion_confirmed_at"], "non_completion_confirmed_at")
            if confirmed <= as_of:
                return result(obligation, customer_state, as_of, "breach",
                              "Complete audit evidence confirms the required action did not occur.")
        return result(obligation, customer_state, as_of, "insufficient_evidence",
                      "Completion or affirmative non-completion is not evidenced.", ("action_completion",))

    try:
        anchor = parse_date(customer_state.get("trigger_at"), "trigger_at")
    except ValueError:
        return result(obligation, customer_state, as_of, "insufficient_evidence",
                      "The timing anchor is absent or invalid.", ("trigger_at",))
    calendar_id = None
    if obligation["deadline_unit"] == "business_days":
        calendar = customer_state.get("business_calendar")
        if not isinstance(calendar, dict):
            return result(obligation, customer_state, as_of, "insufficient_evidence",
                          "A bounded business-day calendar is required.", ("business_calendar",))
        try:
            coverage_start = parse_date(calendar.get("coverage_start"), "business_calendar.coverage_start")
            coverage_end = parse_date(calendar.get("coverage_end"), "business_calendar.coverage_end")
            holidays = {parse_date(day, "business_calendar.public_holidays")
                        for day in calendar.get("public_holidays", [])}
        except (TypeError, ValueError):
            return result(obligation, customer_state, as_of, "insufficient_evidence",
                          "The business-day calendar is invalid.", ("business_calendar",))
        if coverage_start > anchor or coverage_end < as_of or not calendar.get("calendar_id"):
            return result(obligation, customer_state, as_of, "insufficient_evidence",
                          "The business-day calendar does not cover the evaluation interval.", ("business_calendar",))
        deadline = add_business_days(anchor, deadline_value, holidays)
        calendar_id = str(calendar["calendar_id"])
    elif obligation["deadline_unit"] == "months":
        deadline = add_months(anchor, deadline_value)
    else:
        raise ValueError("Unsupported obligation deadline unit")

    action_at = None
    if completed is True:
        try:
            action_at = parse_date(customer_state.get("action_at"), "action_at")
        except ValueError:
            return result(obligation, customer_state, as_of, "insufficient_evidence",
                          "Action completion lacks a valid date.", ("action_at",), calendar_id)
    if obligation["timing_operator"] == "at_most":
        if completed is True:
            status = "compliant" if action_at <= deadline else "breach"
            reason = ("The required action occurred by the source deadline." if status == "compliant"
                      else "The required action occurred after the source deadline.")
            return result(obligation, customer_state, as_of, status, reason, calendar_id=calendar_id)
        if completed is False and customer_state.get("non_completion_confirmed_at"):
            confirmed = parse_date(customer_state["non_completion_confirmed_at"], "non_completion_confirmed_at")
            if confirmed <= as_of and as_of > deadline:
                return result(obligation, customer_state, as_of, "breach",
                              "Affirmative non-completion evidence remains after the source deadline.", calendar_id=calendar_id)
            if as_of <= deadline:
                return result(obligation, customer_state, as_of, "at_risk",
                              "The action is incomplete but the source deadline has not passed.", calendar_id=calendar_id)
        return result(obligation, customer_state, as_of, "insufficient_evidence",
                      "Completion or affirmative non-completion is not evidenced.", ("action_completion",), calendar_id)

    if obligation["timing_operator"] != "at_least":
        raise ValueError("Unsupported obligation timing operator")
    if completed is True:
        status = "compliant" if action_at >= deadline else "breach"
        reason = ("The minimum source period was met." if status == "compliant"
                  else "The recorded action occurred before the minimum source period elapsed.")
        return result(obligation, customer_state, as_of, status, reason, calendar_id=calendar_id)
    if policy == "minimum_wait" and completed is False and customer_state.get("non_completion_confirmed_at"):
        return result(obligation, customer_state, as_of, "compliant",
                      "Complete evidence shows no restricted action occurred before the minimum period.", calendar_id=calendar_id)
    if completed is False and customer_state.get("non_completion_confirmed_at"):
        confirmed = parse_date(customer_state["non_completion_confirmed_at"], "non_completion_confirmed_at")
        if confirmed <= as_of and as_of >= deadline:
            return result(obligation, customer_state, as_of, "breach",
                          "The minimum required duration was not provided.", calendar_id=calendar_id)
        return result(obligation, customer_state, as_of, "at_risk",
                      "The minimum required duration is still in progress.", calendar_id=calendar_id)
    return result(obligation, customer_state, as_of, "insufficient_evidence",
                  "Completion or affirmative non-completion is not evidenced.", ("action_completion",), calendar_id)


def _control(identifier):
    def evaluate(obligation, customer_state, as_of_date):
        return _evaluate(identifier, obligation, customer_state, as_of_date,
                         "minimum_wait" if identifier in MINIMUM_WAIT_CONTROLS else "required")
    evaluate.__name__ = "control_" + identifier.lower().replace("-", "_")
    return evaluate


# A distinct bound pure callable exists for every approved pilot obligation.
control_oiq_001 = _control("OIQ-001")
control_oiq_002 = _control("OIQ-002")
control_oiq_003 = _control("OIQ-003")
control_oiq_004 = _control("OIQ-004")
control_oiq_005 = _control("OIQ-005")
control_oiq_006 = _control("OIQ-006")
control_oiq_007 = _control("OIQ-007")
control_oiq_008 = _control("OIQ-008")
control_oiq_009 = _control("OIQ-009")
control_oiq_010 = _control("OIQ-010")
control_oiq_011 = _control("OIQ-011")
control_oiq_012 = _control("OIQ-012")
control_oiq_013 = _control("OIQ-013")
control_oiq_014 = _control("OIQ-014")
control_oiq_015 = _control("OIQ-015")
control_oiq_016 = _control("OIQ-016")
control_oiq_017 = _control("OIQ-017")
control_oiq_018 = _control("OIQ-018")
control_oiq_019 = _control("OIQ-019")
control_oiq_020 = _control("OIQ-020")
control_oiq_021 = _control("OIQ-021")
control_oiq_022 = _control("OIQ-022")
control_oiq_023 = _control("OIQ-023")
control_oiq_024 = _control("OIQ-024")
control_oiq_025 = _control("OIQ-025")
control_oiq_026 = _control("OIQ-026")
control_oiq_027 = _control("OIQ-027")
control_oiq_028 = _control("OIQ-028")
control_oiq_029 = _control("OIQ-029")
control_oiq_030 = _control("OIQ-030")
control_oiq_031 = _control("OIQ-031")
control_oiq_032 = _control("OIQ-032")

CONTROL_FUNCTIONS: dict[str, Callable[..., ControlResult]] = {
    f"OIQ-{index:03d}": globals()[f"control_oiq_{index:03d}"] for index in range(1, 33)
}


def evaluate_control(obligation, customer_state, as_of_date):
    try:
        control = CONTROL_FUNCTIONS[obligation["obligation_id"]]
    except KeyError as error:
        raise ValueError("No deterministic control for obligation") from error
    return control(obligation, customer_state, as_of_date)
