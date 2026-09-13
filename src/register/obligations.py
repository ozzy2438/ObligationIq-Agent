"""Version-bound source review; human and authorised agent decisions stay distinct."""

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

from src.config import ROOT, settings
from src.dataplane.corpus import load_manifest

CANDIDATES = ROOT / "data/obligation-candidates.json"
REVIEWS = ROOT / "data/human-reviews.json"
SOURCE_REVIEWS = ROOT / "data/source-reviews.json"
LIST_FIELDS = {"jurisdiction", "evidence_required", "pending_checks"}
INTEGER_FIELDS = {"deadline_value", "source_page_start", "source_page_end"}
FIELDS = set("""obligation_id instrument jurisdiction regime clause_reference parent_clause
obligation_family trigger_event required_action deadline_value deadline_unit timing_operator
timing_anchor evidence_required applies_to_customer_segment source_id source_url source_version
source_sha256 source_clause_sha256 source_page_start source_page_end effective_from effective_to
coverage_as_of extraction_method verified_by_human verification_date pending_checks record_sha256""".split())
REGISTER_FIELDS = FIELDS | {"review_status", "verification_method", "reviewer",
                            "review_reasoning", "review_correction"}
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

    Draft flags cannot confer approval. Explicit human decisions are maintained
    separately, bound to the reviewed draft digest. Jurisdiction review is pending.
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


def reviewed_records(records, reviews=None):
    """Apply explicit decisions to exact drafts without mislabelling agent review.

    The Git-reviewed decision file is an audit record of conversation approvals,
    not a cryptographic identity system or permission to run compliance controls.
    """
    validate_candidates(records)
    reviews = (json.loads(REVIEWS.read_text()) + json.loads(SOURCE_REVIEWS.read_text())
               if reviews is None else reviews)
    if not isinstance(reviews, list):
        raise RegisterError("Reviews must be a list")
    by_id = {r["obligation_id"]: dict(r) for r in records}
    seen = set()
    for review in reviews:
        required = {"obligation_id", "decision", "reviewer", "verification_date",
                    "reviewed_record_sha256", "source_sha256", "basis", "scope", "recorded_by"}
        required |= {"source_url", "clause_reference", "source_version", "correction",
                     "before_record_sha256"}
        if (not isinstance(review, dict) or set(review) != required or
                any(type(v) is not str or not v.strip() for v in review.values())):
            raise RegisterError("Incomplete review decision")
        oid = review["obligation_id"]
        r = by_id.get(oid)
        if r is None or oid in seen:
            raise RegisterError("Unknown or duplicate review decision")
        seen.add(oid)
        if (review["decision"] not in {"APPROVED", "PENDING HUMAN REVIEW"} or
                review["scope"] not in {"human_content_review", "agent_source_review"}):
            raise RegisterError("Unsupported review decision or scope")
        if any(review[k] != r[k] for k in ("source_url", "clause_reference", "source_version")):
            raise RegisterError("Review citation does not match current draft")
        if not re.fullmatch(r"[0-9a-f]{64}", review["before_record_sha256"]):
            raise RegisterError("Invalid pre-review digest")
        if (review["reviewed_record_sha256"] != r["record_sha256"] or
                review["source_sha256"] != r["source_sha256"]):
            raise RegisterError("Review does not match current draft/source; re-review required")
        date.fromisoformat(review["verification_date"])
        approved = review["decision"] == "APPROVED"
        r["verified_by_human"] = approved and review["scope"] == "human_content_review"
        r["verification_date"] = review["verification_date"] if approved else None
        r["review_status"] = review["decision"]
        r["verification_method"] = review["scope"]
        r["reviewer"] = review["reviewer"]
        r["review_reasoning"] = review["basis"]
        r["review_correction"] = review.get("correction", "None; explicit human approval of the bound draft.")
    for r in by_id.values():
        if r["obligation_id"] not in seen:
            r.update(review_status="PENDING HUMAN REVIEW", verification_method="unreviewed",
                     reviewer="Unassigned", review_reasoning="No recorded decision", review_correction="None")
        r["record_sha256"] = record_hash(r)
    return list(by_id.values())


def for_controls(records):
    reviewed = reviewed_records(records)
    if any(r["review_status"] != "APPROVED" for r in reviewed):
        raise RegisterError("Source review pending; controls remain blocked")
    raise RegisterError("Control Engine and operational applicability gates are not implemented")


def materialize(records, path=settings.register_dir, reviews=None):
    """Local Delta snapshot; identical input is a no-op, changes create a version.

    One local writer is supported. Delta's transaction log preserves snapshots;
    this is not Unity Catalog, access control, or an approval mechanism.
    """
    records = reviewed_records(records, reviews)
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
                 else pa.string(), nullable=key in NULLABLE) for key in sorted(REGISTER_FIELDS)])
    data = pa.Table.from_pylist(ordered, schema=schema)
    write_deltalake(table if table is not None else str(path), data,
                   mode="overwrite" if table is not None else "error",
                   schema_mode="overwrite" if table is not None else None)
    return {"version": DeltaTable(str(path)).version(), "written": True, "records": len(records)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "materialize"))
    args = parser.parse_args()
    records = load_candidates()
    result = (materialize(records) if args.command == "materialize" else
              {"records": len(records), "approved": sum(r["review_status"] == "APPROVED"
                  for r in reviewed_records(records)), "human_verified": sum(
                  r["verified_by_human"] for r in reviewed_records(records)), "control_eligible": 0})
    print(json.dumps(result))


if __name__ == "__main__":
    main()
