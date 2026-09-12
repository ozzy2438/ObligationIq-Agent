"""Offline checks for catalog schema fidelity and fail-closed local identity."""
import copy
from dataclasses import replace
import json

import pytest

from scripts import local_catalog as catalog


def test_delta_array_type_round_trip():
    from deltalake import Schema
    raw = {"type": "struct", "fields": [{"name": "evidence", "nullable": False,
           "metadata": {}, "type": {"type": "array", "elementType": "string", "containsNull": True}}]}
    schema = Schema.from_json(json.dumps(raw))
    columns = catalog.columns_from_delta(schema)
    api = catalog.delta_api_schema(schema)
    assert api["fields"][0]["type"] == {"type": "array", "element-type": "string", "contains-null": True}
    saved = {"columns": columns, "storage_location": "file:///table", "data_source_format": "DELTA", "table_type": "EXTERNAL"}
    catalog.validate_table(saved, "file:///table", columns)
    changed = copy.deepcopy(saved)
    field = json.loads(changed["columns"][0]["type_json"])
    field["type"]["elementType"] = "long"
    changed["columns"][0]["type_json"] = json.dumps(field)
    with pytest.raises(ValueError, match="schema differs"):
        catalog.validate_table(changed, "file:///table", columns)
    with pytest.raises(ValueError, match="unexpected location"):
        catalog.validate_table(saved, "file:///other", columns)


def test_catalog_rejects_nonlocal_url_before_token_or_network(monkeypatch):
    monkeypatch.setattr(catalog, "settings", replace(catalog.settings, catalog_url="https://example.com"))
    with pytest.raises(ValueError, match="loopback"):
        catalog.request("GET", "/catalogs")
