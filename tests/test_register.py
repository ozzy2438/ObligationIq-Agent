"""Checks use the real draft register; no operational/customer population."""

from copy import deepcopy

import pytest

from src.register.obligations import (RegisterError, for_controls, load_candidates,
                                      materialize, record_hash, reviewed_records, validate_candidates)


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
    with pytest.raises(RegisterError, match="Human verification"):
        for_controls(records)
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
    assert {r["record_sha256"] for r in old} == {r["record_sha256"] for r in records}
    assert {r["record_sha256"] for r in new} == {r["record_sha256"] for r in revised}


def test_explicit_human_approval_is_scoped_to_024_only():
    records = reviewed_records(load_candidates())
    assert [r["obligation_id"] for r in records if r["verified_by_human"]] == ["OIQ-024"]
    assert next(r for r in records if r["obligation_id"] == "OIQ-024")["verification_date"] == "2026-09-12"
    assert next(r for r in records if r["obligation_id"] == "OIQ-025")["verification_date"] is None


def test_edited_approved_content_requires_fresh_review():
    records = deepcopy(load_candidates())
    row = next(r for r in records if r["obligation_id"] == "OIQ-024")
    row["deadline_value"] = 5
    row["record_sha256"] = record_hash(row)
    with pytest.raises(RegisterError, match="re-review required"):
        reviewed_records(records)


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
    assert [r["obligation_id"] for r in new if r["verified_by_human"]] == ["OIQ-024"]
