"""Checks use the real draft register; no operational/customer population."""

from copy import deepcopy

import pytest

from src.register.obligations import (OPERATIONAL_REVIEWS, RegisterError, for_controls, load_candidates,
                                      materialize, operational_records, record_hash,
                                      review_composition, reviewed_records, validate_candidates)


def changed(key, value):
    row = deepcopy(load_candidates()[0])
    row[key] = value
    row["record_sha256"] = record_hash(row)
    return [row]


def test_real_register_scope_and_gate():
    records = load_candidates()
    assert 25 <= len(records) <= 40
    assert {(r["regime"], r["obligation_family"]) for r in records} == {
        (regime, family) for regime in ("VIC", "NERL_NERR")
        for family in ("life_support", "hardship")}
    eligible = for_controls(records)
    assert len(eligible) == 32
    assert review_composition(eligible) == {
        "total": 32, "human_verified": 2, "human_verified_proportion": 0.0625,
        "agent_reviewed": 30, "agent_reviewed_proportion": 0.9375}
    with pytest.raises(RegisterError, match="cannot assert human"):
        for_controls(changed("verified_by_human", True))


def test_changed_content_source_or_reference_refused():
    records = deepcopy(load_candidates())
    records[0]["required_action"] = "changed"
    with pytest.raises(RegisterError, match="content changed"):
        validate_candidates(records)
    with pytest.raises(RegisterError, match="pinned source"):
        validate_candidates(changed("source_sha256", "0" * 64))
    with pytest.raises(RegisterError, match="Unresolvable"):
        validate_candidates(changed("parent_clause", "999"))
    with pytest.raises(RegisterError, match="nonempty"):
        validate_candidates([])


def test_minimum_periods_cannot_be_ambiguous():
    records = load_candidates()
    minimum = [r for r in records if r["clause_reference"] in {"124A(1)(a)", "164(1)(a)"}]
    assert len(minimum) == 2
    assert all(r["deadline_value"] == 50 and r["timing_operator"] == "at_least" for r in minimum)
    with pytest.raises(RegisterError, match="Timing must"):
        validate_candidates(changed("deadline_value", 5))


def test_delta_repeat_is_free_of_writes_and_history_retains_old_draft(tmp_path):
    pytest.importorskip("deltalake")
    from deltalake import DeltaTable
    records = load_candidates()
    first = materialize(records, tmp_path / "register", reviews=[])
    assert first == {"version": 0, "written": True, "records": len(records)}
    assert materialize(records, tmp_path / "register", reviews=[])["written"] is False
    revised = deepcopy(records)
    revised[0]["pending_checks"].append("Additional human review note")
    revised[0]["record_sha256"] = record_hash(revised[0])
    assert materialize(revised, tmp_path / "register", reviews=[])["version"] == 1
    old = DeltaTable(str(tmp_path / "register"), version=0).to_pyarrow_table().to_pylist()
    new = DeltaTable(str(tmp_path / "register")).to_pyarrow_table().to_pylist()
    assert {r["record_sha256"] for r in old} == {r["record_sha256"] for r in operational_records(records, reviews=[])}
    assert {r["record_sha256"] for r in new} == {r["record_sha256"] for r in operational_records(revised, reviews=[])}


def test_human_and_agent_approval_provenance_stays_distinct():
    records = reviewed_records(load_candidates())
    assert [r["obligation_id"] for r in records if r["verified_by_human"]] == ["OIQ-024", "OIQ-025"]
    assert next(r for r in records if r["obligation_id"] == "OIQ-024")["verification_date"] == "2026-09-12"
    assert next(r for r in records if r["obligation_id"] == "OIQ-025")["verification_date"] == "2026-09-12"
    assert all(r["review_status"] == "APPROVED" and r["verification_date"] for r in records)
    assert sum(r["verification_method"] == "agent_source_review" for r in records) == 30


def test_edited_approved_content_requires_fresh_review():
    records = deepcopy(load_candidates())
    row = next(r for r in records if r["obligation_id"] == "OIQ-024")
    row["deadline_value"] = 5
    row["record_sha256"] = record_hash(row)
    with pytest.raises(RegisterError, match="re-review required"):
        reviewed_records(records)


def test_operational_review_is_separate_and_digest_bound():
    records = operational_records(load_candidates())
    assert all(r["operational_review_status"] == "ELIGIBLE_FOR_EVALUATION" for r in records)
    assert all(r["operational_verification_method"] == "agent_operational_review" for r in records)
    assert [r["obligation_id"] for r in records if r["verified_by_human"]] == ["OIQ-024", "OIQ-025"]
    decision = __import__("json").loads(OPERATIONAL_REVIEWS.read_text())
    decision["bindings"]["OIQ-001"][0] = "0" * 64
    with pytest.raises(RegisterError, match="re-review required"):
        operational_records(load_candidates(), operational_review=decision)


def test_delta_human_decision_preserves_unapproved_history(tmp_path):
    pytest.importorskip("deltalake")
    from deltalake import DeltaTable
    records = load_candidates()
    path = tmp_path / "register"
    materialize(records, path, reviews=[])
    assert materialize(records, path)["version"] == 1
    assert materialize(records, path)["written"] is False
    old = DeltaTable(str(path), version=0).to_pyarrow_table().to_pylist()
    new = DeltaTable(str(path)).to_pyarrow_table().to_pylist()
    assert not any(r["verified_by_human"] for r in old)
    assert [r["obligation_id"] for r in new if r["verified_by_human"]] == ["OIQ-024", "OIQ-025"]
    assert sum(r["review_status"] == "APPROVED" for r in new) == 32


def test_agent_decision_cannot_silently_cover_changed_content_or_citation():
    import json
    from src.register.obligations import SOURCE_REVIEWS
    records = deepcopy(load_candidates())
    records[0]["required_action"] = "Changed after review"
    records[0]["record_sha256"] = record_hash(records[0])
    with pytest.raises(RegisterError, match="re-review required"):
        reviewed_records(records)
    decisions = json.loads(SOURCE_REVIEWS.read_text())
    decisions[0]["clause_reference"] = "999"
    with pytest.raises(RegisterError, match="citation does not match"):
        reviewed_records(load_candidates(), decisions)


def test_pending_agent_review_never_sets_a_verification_date():
    import json
    from src.register.obligations import SOURCE_REVIEWS
    decisions = json.loads(SOURCE_REVIEWS.read_text())[:1]
    decisions[0]["decision"] = "PENDING HUMAN REVIEW"
    decisions[0]["basis"] = "Unit mutation: source evidence missing"
    records = reviewed_records(load_candidates(), decisions)
    assert all(not r["verified_by_human"] and r["verification_date"] is None for r in records)
    assert all(r["review_status"] == "PENDING HUMAN REVIEW" for r in records)
