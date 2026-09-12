"""Candidate obligations only. Source traceability does not confer human approval."""

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

from src.config import ROOT, settings
from src.dataplane.corpus import load_manifest

CANDIDATES = ROOT / "data/obligation-candidates.json"
LIST_FIELDS = {"jurisdiction", "evidence_required", "pending_checks"}
INTEGER_FIELDS = {"deadline_value", "source_page_start", "source_page_end"}
FIELDS = set("""obligation_id instrument jurisdiction regime clause_reference parent_clause
obligation_family trigger_event required_action deadline_value deadline_unit timing_operator
timing_anchor evidence_required applies_to_customer_segment source_id source_url source_version
source_sha256 source_clause_sha256 source_page_start source_page_end effective_from effective_to
coverage_as_of extraction_method verified_by_human verification_date pending_checks record_sha256""".split())
NULLABLE = {"deadline_value", "deadline_unit", "timing_anchor", "effective_from",
            "effective_to", "verification_date"}


class RegisterError(ValueError):
    pass


def record_hash(record):
    payload = {k: v for k, v in record.items() if k != "record_sha256"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def validate_candidates(records, manifest=None):
    """Validate draft contracts without PDFs, model calls or network access.

    Approval cannot be manufactured by toggling a JSON flag. A human attestation
    workflow and jurisdiction review are deliberately not implemented yet.
    """
    if not isinstance(records, list) or not records:
        raise RegisterError("Candidate snapshot must be a nonempty list")
    sources = {s["id"]: s for s in (manifest or load_manifest())["sources"]}
    ids = set()
    for r in records:
        if set(r) != FIELDS:
            raise RegisterError("Candidate field contract mismatch")
        for key, value in r.items():
            if value is None and key in NULLABLE:
                continue
            expected = (list if key in LIST_FIELDS else int if key in INTEGER_FIELDS
                        else bool if key == "verified_by_human" else str)
            if type(value) is not expected:
                raise RegisterError("Invalid candidate field type: " + key)
            if expected is str and not value.strip():
                raise RegisterError("Empty candidate field: " + key)
            if expected is list and (not value or any(type(v) is not str or not v.strip() for v in value)):
                raise RegisterError("Invalid candidate list: " + key)
        if r["obligation_id"] in ids:
            raise RegisterError("Duplicate obligation identity")
        ids.add(r["obligation_id"])
        if r["verified_by_human"] or r["verification_date"] is not None:
            raise RegisterError("Draft import cannot assert human approval")
        if r["record_sha256"] != record_hash(r):
            raise RegisterError("Candidate content changed without a new digest")
        if any(not re.fullmatch(r"[0-9a-f]{64}", r[k]) for k in
               ("record_sha256", "source_sha256", "source_clause_sha256")):
            raise RegisterError("Invalid provenance digest")
        s = sources.get(r["source_id"])
        if not s or any(r[k] != s[v] for k, v in {
            "instrument": "title", "source_version": "version", "source_sha256": "sha256",
            "source_url": "url", "regime": "regime", "jurisdiction": "jurisdictions",
            "effective_from": "effective_from", "coverage_as_of": "valid_from"}.items()):
            raise RegisterError("Candidate does not match pinned source metadata")
        refs = {ref for region in s["regions"] for ref in region.get("references", [])}
        if (r["parent_clause"] not in refs or not
                (r["clause_reference"] == r["parent_clause"] or
                 r["clause_reference"].startswith(r["parent_clause"] + "("))):
            raise RegisterError("Unresolvable parent clause")
        if not 1 <= r["source_page_start"] <= r["source_page_end"] <= s["pdf_pages"]:
            raise RegisterError("Invalid physical PDF page range")
        if r["obligation_family"] not in {"life_support", "hardship"}:
            raise RegisterError("Unknown obligation family")
        for key in ("effective_from", "effective_to", "coverage_as_of"):
            if r[key] is not None:
                date.fromisoformat(r[key])
        timed = r["deadline_value"] is not None
        if timed:
            if (r["deadline_value"] <= 0 or r["deadline_unit"] not in {"business_days", "months"}
                    or r["timing_operator"] not in {"at_least", "at_most"} or not r["timing_anchor"]):
                raise RegisterError("Timing must state duration, direction and trigger")
        elif (r["timing_operator"] != "not_specified" or r["deadline_unit"] is not None
              or r["timing_anchor"] is not None):
            raise RegisterError("Untimed obligation cannot imply a deadline")
    return records


def load_candidates(path=CANDIDATES):
    return validate_candidates(json.loads(Path(path).read_text()))


def for_controls(records):
    validate_candidates(records)
    raise RegisterError("Human verification and jurisdiction review pending; no candidate is usable by controls")


def materialize(records, path=settings.register_dir):
    """Local Delta snapshot; identical input is a no-op, changes create a version.

    One local writer is supported. Delta's transaction log preserves snapshots;
    this is not Unity Catalog, access control, or an approval mechanism.
    """
    validate_candidates(records)
    import pyarrow as pa
    from deltalake import DeltaTable, write_deltalake

    path = Path(path).resolve()
    table = DeltaTable(str(path)) if (path / "_delta_log").is_dir() else None
    ordered = sorted(records, key=lambda r: r["obligation_id"])
    if table is not None:
        existing = table.to_pyarrow_table().to_pylist()
        if sorted(existing, key=lambda r: r["obligation_id"]) == ordered:
            return {"version": table.version(), "written": False, "records": len(records)}
    schema = pa.schema([
        pa.field(key, pa.list_(pa.string()) if key in LIST_FIELDS else pa.int64()
                 if key in INTEGER_FIELDS else pa.bool_() if key == "verified_by_human"
                 else pa.string(), nullable=key in NULLABLE) for key in sorted(FIELDS)])
    data = pa.Table.from_pylist(ordered, schema=schema)
    write_deltalake(table if table is not None else str(path), data,
                   mode="overwrite" if table is not None else "error")
    return {"version": DeltaTable(str(path)).version(), "written": True, "records": len(records)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "materialize"))
    args = parser.parse_args()
    records = load_candidates()
    result = (materialize(records) if args.command == "materialize" else
              {"records": len(records), "human_verified": 0, "control_eligible": 0})
    print(json.dumps(result))


if __name__ == "__main__":
    main()
