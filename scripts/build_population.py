"""Build once locally, or verify committed calibration evidence offline in CI."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT
from src.dataplane.population import build


def deny_network(event, args):
    if event.startswith("socket."):
        raise RuntimeError("Population build must be offline")


def main(check=False):
    sys.addaudithook(deny_network)
    inputs = json.loads((ROOT / "data/population-inputs.json").read_text())
    contract = json.loads((ROOT / "data/population-contract.json").read_text())
    for name, key in [("data/context-sources.json", "source_manifest_sha256"), ("data/calibration-sources.json", "aer_source_manifest_sha256"), ("data/calibration-aggregates.json", "aer_aggregates_sha256")]:
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != inputs[key]:
            raise ValueError("Calibration input provenance changed: " + name)
    payload, report = build(inputs, contract)
    evidence = ROOT / "docs/population-calibration.json"
    destination = ROOT / ".local/population/accounts.jsonl"
    if check:
        if report != json.loads(evidence.read_text()):
            raise ValueError("Rebuilt population differs from committed calibration evidence")
        if destination.exists() and destination.read_bytes() != payload:
            raise ValueError("Persisted population differs from the deterministic build")
        print(f"PASS: {report['account_count']} synthetic accounts, {len(report['comparisons'])} marginal checks, exact replay fingerprint; network disabled")
        return
    if destination.exists() and destination.read_bytes() != payload:
        raise ValueError("Existing population differs; preserve it and explicitly version a new scenario")
    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(".tmp")
        temporary.write_bytes(payload)
        temporary.replace(destination)
    evidence.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(dict(accounts=report["account_count"], marginal_checks=len(report["comparisons"]), output=str(destination.relative_to(ROOT)), phase3_complete=False)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="No writes; compare rebuilt evidence and any local population, with networking blocked")
    main(parser.parse_args().check)
