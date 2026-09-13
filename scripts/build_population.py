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
    for name, expected in inputs["register_inputs_sha256"].items():
        if hashlib.sha256((ROOT / "data" / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Register input provenance changed: data/" + name)
    for name, key in [("data/operational-context.json", "operational_context_sha256"),
                      ("data/operational-sources.json", "operational_source_manifest_sha256")]:
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != inputs[key]:
            raise ValueError("Operational input provenance changed: " + name)
    inputs["operational_context"] = json.loads((ROOT / "data/operational-context.json").read_text())
    artifacts, report = build(inputs, contract)
    evidence = ROOT / "docs/population-calibration.json"
    destinations = {
        "accounts": ROOT / ".local/population/v2/accounts.jsonl",
        "debt_entries": ROOT / ".local/population/v2/debt-entry-cohort.jsonl",
        "control_cases": ROOT / ".local/population/v2/control-cases.jsonl",
        "ground_truth": ROOT / "data/ground_truth/control-cases.json",
    }
    if check:
        if report != json.loads(evidence.read_text()):
            raise ValueError("Rebuilt population differs from committed calibration evidence")
        for name, destination in destinations.items():
            if name == "ground_truth" or destination.exists():
                if not destination.exists() or destination.read_bytes() != artifacts[name]:
                    raise ValueError("Persisted Phase 3 artefact differs: " + str(destination.relative_to(ROOT)))
        print(f"PASS: {report['account_count']} synthetic accounts, {len(report['comparisons'])} calibration checks, {report['challenge_cases']} isolated challenge cases, exact replay; network disabled")
        return
    for name, destination in destinations.items():
        if destination.exists() and destination.read_bytes() != artifacts[name]:
            raise ValueError("Existing artefact differs; preserve it and explicitly version a new scenario: " + str(destination.relative_to(ROOT)))
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_suffix(destination.suffix + ".tmp")
            temporary.write_bytes(artifacts[name])
            temporary.replace(destination)
    evidence.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(dict(accounts=report["account_count"], calibration_checks=len(report["comparisons"]),
                          challenge_cases=report["challenge_cases"], breach_injections=report["breach_injections"],
                          output=str(destinations["accounts"].relative_to(ROOT)), phase3_complete=True)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="No writes; compare rebuilt evidence and any local population, with networking blocked")
    main(parser.parse_args().check)
