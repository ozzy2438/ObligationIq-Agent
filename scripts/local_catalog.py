"""Explicit local Unity Catalog setup and verification; no cloud or model traffic."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT, settings
from src.register.obligations import load_candidates, operational_records

PIN = json.loads((ROOT / "data/catalog-runtime.json").read_text())
LABEL = "org.obligationiq.component"


def docker(*args, required=True):
    result = subprocess.run(["docker", *args], capture_output=True, text=True, timeout=60)
    if required and result.returncode:
        raise RuntimeError("Local Docker operation failed; inspect the local container, not cloud credentials")
    return result


def container():
    result = docker("inspect", PIN["container"], required=False)
    if result.returncode:
        return None
    info = json.loads(result.stdout)[0]
    if (info["Config"]["Labels"].get(LABEL) != "catalog" or
            info["Config"]["Image"] != PIN["image"]):
        raise RuntimeError("Container name is occupied by an unrelated or unpinned instance")
    return info


def start():
    settings.catalog_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    conf = settings.catalog_dir / "server.properties"
    conf.write_text("server.env=dev\nserver.authorization=enable\nserver.managed-table.enabled=false\n")
    info = container()
    if info is None:
        # No cloud identity is passed in. Internal bootstrap keys remain in a dedicated volume.
        docker("run", "-d", "--name", PIN["container"], "--label", LABEL + "=catalog",
               "--memory=1g", "--cpus=2", "--publish", "127.0.0.1:8087:8080",
               "--mount", f"type=volume,source={PIN['volume']},target=/home/unitycatalog/etc",
               "--mount", f"type=bind,source={conf},target=/home/unitycatalog/etc/conf/server.properties,readonly",
               "--mount", f"type=bind,source={settings.register_dir},target={settings.register_dir},readonly",
               PIN["image"])
    elif not info["State"]["Running"]:
        docker("start", PIN["container"])
    for _ in range(20):
        try:
            if request("GET", "/catalogs", authenticated=False)[0] in (401, 403):
                print("Local Unity Catalog is ready; anonymous access refused")
                return
        except (OSError, urllib.error.URLError):
            pass
        time.sleep(1)
    raise RuntimeError("Local catalog did not become ready within 20 seconds")


def request(method, route, payload=None, *, authenticated=True):
    if settings.catalog_url != "http://127.0.0.1:8087":
        raise ValueError("Only the explicit loopback catalog is supported")
    headers = {"Content-Type": "application/json"}
    if authenticated:
        token_file = settings.catalog_dir / "token.txt"
        token_file.touch(mode=0o600, exist_ok=True)
        docker("cp", PIN["container"] + ":/home/unitycatalog/etc/conf/token.txt", str(token_file))
        token_file.chmod(0o600)
        headers["Authorization"] = "Bearer " + token_file.read_text().strip()
    req = urllib.request.Request(settings.catalog_url + "/api/2.1/unity-catalog" + route,
                                 data=json.dumps(payload, separators=(",", ":")).encode() if payload is not None else None,
                                 headers=headers, method=method)
    # Loopback traffic must not flow through a machine-wide HTTP proxy or follow redirects.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(req, timeout=10) as response:
            raw = response.read()
            try:
                body = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                body = None
            return response.status, body
    except urllib.error.HTTPError as error:
        return error.code, None  # Do not surface provider responses or authentication material.


def require(status, allowed=(200,)):
    if status not in allowed:
        raise RuntimeError(f"Local catalog operation refused (HTTP {status})")


def columns_from_delta(schema):
    columns = []
    names = {"string": "STRING", "long": "LONG", "boolean": "BOOLEAN"}
    for position, field in enumerate(json.loads(schema.to_json())["fields"]):
        value = field["type"]
        if isinstance(value, dict) and value.get("type") == "array" and value.get("elementType") == "string":
            name, text = "ARRAY", "array<string>"
        elif isinstance(value, str) and value in names:
            name, text = names[value], value
        else:
            raise ValueError("Unreviewed Delta column type")
        columns.append(dict(name=field["name"], type_name=name, type_text=text,
                            type_json=json.dumps(field), position=position, nullable=field["nullable"]))
    return columns


def delta_api_schema(schema):
    """UC Delta API uses kebab-case array keys; the Delta log uses camelCase."""
    result = json.loads(schema.to_json())
    for field in result["fields"]:
        kind = field["type"]
        if isinstance(kind, dict) and kind.get("type") == "array":
            kind["element-type"] = kind.pop("elementType")
            kind["contains-null"] = kind.pop("containsNull")
    return result


def validate_table(saved, location, columns):
    if (saved["storage_location"].rstrip("/") != location.rstrip("/") or
            saved["data_source_format"] != "DELTA" or saved["table_type"] != "EXTERNAL"):
        raise ValueError("Catalog table points to an unexpected location or format")
    for stored, wanted in zip(saved["columns"], columns, strict=True):
        if (any(stored[key] != wanted[key] for key in ("name", "type_name", "nullable", "position"))
                or json.loads(stored["type_json"]) != json.loads(wanted["type_json"])):
            raise ValueError("Catalog schema differs from Delta schema")


def sync():
    from deltalake import DeltaTable
    if container() is None:
        raise RuntimeError("Start the pinned local catalog first")
    expected = operational_records(load_candidates())
    table = DeltaTable(str(settings.register_dir))
    actual = table.to_pyarrow_table().to_pylist()
    if sorted(actual, key=lambda r: r["obligation_id"]) != sorted(expected, key=lambda r: r["obligation_id"]):
        raise ValueError("Delta snapshot differs from reviewed register; materialize it first")
    created = 0
    for route, name, body in (
        ("catalogs", PIN["catalog"], {"name": PIN["catalog"], "comment": "Local ObligationIQ pilot"}),
        ("schemas", PIN["catalog"] + "." + PIN["schema"],
         {"name": PIN["schema"], "catalog_name": PIN["catalog"]}),
    ):
        status, _ = request("GET", f"/{route}/{name}")
        if status == 404:
            require(request("POST", "/" + route, body)[0]); created += 1
        else:
            require(status)
    name = ".".join(PIN[k] for k in ("catalog", "schema", "table"))
    location = settings.register_dir.as_uri()
    columns = columns_from_delta(table.schema())
    status, saved = request("GET", "/tables/" + name)
    if status == 404:
        protocol = table.protocol()
        body = {
            "name": PIN["table"], "location": location, "table-type": "EXTERNAL",
            "columns": delta_api_schema(table.schema()),
            "protocol": {"min-reader-version": protocol.min_reader_version,
                         "min-writer-version": protocol.min_writer_version,
                         "reader-features": protocol.reader_features or [],
                         "writer-features": protocol.writer_features or []},
            "properties": table.metadata().configuration,
            "partition-columns": table.metadata().partition_columns,
            "last-commit-timestamp-ms": DeltaTable(str(settings.register_dir), version=0).history()[0]["timestamp"],
            "comment": "Reviewed source requirements; no customer data",
        }
        route = f"/delta/v1/catalogs/{PIN['catalog']}/schemas/{PIN['schema']}/tables"
        require(request("POST", route, body)[0]); created += 1
        status, saved = request("GET", "/tables/" + name)
    require(status)
    validate_table(saved, location, columns)
    # Resolve the table location through UC, then read that exact Delta snapshot.
    resolved = DeltaTable(saved["storage_location"], version=table.version())
    if resolved.to_pyarrow_table().to_pylist() != actual:
        raise ValueError("Catalog-resolved Delta read mismatch")
    require(request("GET", "/catalogs", authenticated=False)[0], (401, 403))
    return {"catalog": name, "catalog_table_id": saved["table_id"], "created_objects": created, "delta_version": table.version(),
            "rows": len(actual), "columns": len(columns), "anonymous_access_denied": True,
            "catalog_resolved_read_matches": True, "storage_location_matches": True}


def refresh_schema():
    """Replace exact local external-table metadata; Delta bytes and history are untouched."""
    name = ".".join(PIN[k] for k in ("catalog", "schema", "table"))
    status, saved = request("GET", "/tables/" + name)
    if status == 404:
        return sync()
    require(status)
    location = settings.register_dir.as_uri()
    if (saved["storage_location"].rstrip("/") != location.rstrip("/") or
            saved["data_source_format"] != "DELTA" or saved["table_type"] != "EXTERNAL"):
        raise ValueError("Refusing to replace unrelated catalog metadata")
    require(request("DELETE", "/tables/" + name)[0])
    return sync()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("start", "verify", "refresh-schema", "stop"))
    args = parser.parse_args()
    if args.command == "start":
        start()
    elif args.command == "stop":
        if container():
            docker("stop", PIN["container"])
        print("Local catalog stopped; volume and Delta history retained")
    elif args.command == "refresh-schema":
        print(json.dumps(refresh_schema()))
    else:
        first = sync()
        docker("restart", PIN["container"])
        start()
        repeat = sync()
        if first["catalog_table_id"] != repeat["catalog_table_id"]:
            raise RuntimeError("Catalog identity changed across restart")
        from deltalake import DeltaTable
        history = {v: len(DeltaTable(str(settings.register_dir), version=v).to_pyarrow_table())
                   for v in range(repeat["delta_version"] + 1)}
        if repeat["created_objects"]:
            raise RuntimeError("Repeated catalog sync must not mutate metadata")
        report = dict(repeat, verified_at_utc=datetime.now(timezone.utc).isoformat(),
                      initial_created_objects=first["created_objects"],
                      persisted_across_restart=True, historical_delta_rows=history, implementation=PIN["implementation"],
                      version=PIN["version"], image=PIN["image"], cloud_resources_created=0,
                      managed_databricks=False, row_level_security_verified=False,
                      automatic_lineage_verified=False)
        (ROOT / "docs/catalog-verification.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report))


if __name__ == "__main__":
    main()
