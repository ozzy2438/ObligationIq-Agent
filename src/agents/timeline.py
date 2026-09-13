"""PII-minimising timeline construction from explicit case evidence."""

from dataclasses import asdict, dataclass
from datetime import date


@dataclass(frozen=True)
class TimelineEvent:
    occurred_on: str
    event_type: str
    evidence_item: str | None = None
    present: bool | None = None

    def to_dict(self):
        return asdict(self)


def _day(value, field):
    try:
        return date.fromisoformat(value).isoformat()
    except (TypeError, ValueError):
        raise ValueError("Invalid or missing timeline date: " + field) from None


def build_timeline(case):
    """Discard identity and evidence values; retain dates, event types and presence."""
    as_of = _day(case.get("as_of_date"), "as_of_date")
    events = []
    if case.get("trigger_occurred") is True:
        events.append(TimelineEvent(_day(case.get("trigger_at"), "trigger_at"), "trigger"))
    if case.get("action_at"):
        events.append(TimelineEvent(_day(case["action_at"], "action_at"), "action_completed"))
    if case.get("non_completion_confirmed_at"):
        events.append(TimelineEvent(
            _day(case["non_completion_confirmed_at"], "non_completion_confirmed_at"),
            "non_completion_confirmed"))
    evidence = case.get("evidence")
    if isinstance(evidence, dict):
        for name, item in sorted(evidence.items()):
            present = item.get("present") is True if isinstance(item, dict) else False
            events.append(TimelineEvent(as_of, "evidence_observed", str(name), present))
    return tuple(sorted(events, key=lambda item: (item.occurred_on, item.event_type,
                                                   item.evidence_item or "")))
