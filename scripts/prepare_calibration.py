"""Extract pinned AER aggregates with cell provenance. No synthetic population is generated."""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT

NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REGIONS = ("National", "ACT", "NSW", "QLD", "SA", "TAS")
# metric, schedule, sheet, latest-quarter column, metric-header cell
METRICS = (
    ("residential_customers", 2, "ResElec Cust#s & Mkt Contr", "F", "B4"),
    ("hardship_customers", 4, "Hardship numbers", "F", "B4"),
    ("hardship_rate", 4, "Hardship numbers", "K", "G4"),
    ("hardship_entry_debt_aud", 4, "Hardship Avg & Entry Debt", "F", "B4"),
    ("hardship_current_debt_aud", 4, "Hardship Avg & Entry Debt", "L", "H4"),
    ("quarter_disconnections", 3, "Disconnections Resi", "F", "B4"),
    ("quarter_disconnection_rate", 3, "Disconnections Resi", "L", "H4"),
    ("life_support_confirmed", 6, "Life support electricity cust#s", "F", "B4"),
    ("life_support_unconfirmed", 6, "Life support electricity cust#s", "K", "G4"),
    ("quarter_life_support_registrations", 6, "Life support electricity cust#s", "P", "L4"),
    ("quarter_life_support_deregistrations", 6, "Life support electricity cust#s", "U", "Q4"),
)


def sheet_cells(path, name):
    """Read published literals without Excel execution or stale formula caches."""
    with ZipFile(path) as z:
        strings = ["".join(e.itertext()) for e in ET.fromstring(z.read("xl/sharedStrings.xml"))]
        rels = {r.attrib["Id"]: r.attrib["Target"] for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
        sheets = ET.fromstring(z.read("xl/workbook.xml")).find("s:sheets", NS)
        sheet = next(s for s in sheets if s.attrib["name"] == name)
        rid = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        target = rels[rid]
        target = target.lstrip("/") if target.startswith("/") else "xl/" + target
        cells = {}
        for cell in ET.fromstring(z.read(target)).findall(".//s:sheetData/s:row/s:c", NS):
            value = cell.find("s:v", NS)
            if cell.find("s:f", NS) is not None:
                cells[cell.attrib["r"]] = {"formula": True}
            elif value is not None:
                cells[cell.attrib["r"]] = strings[int(value.text)] if cell.attrib.get("t") == "s" else Decimal(value.text)
        return cells


def prepare(download=False):
    manifest = json.loads((ROOT / "data/calibration-sources.json").read_text())
    paths = {}
    for source in manifest["sources"]:
        path = ROOT / "data/raw/calibration" / (source["id"] + ".xlsx")
        if not path.exists() and download:
            path.parent.mkdir(parents=True, exist_ok=True)
            with urlopen(source["url"], timeout=45) as response:
                content = response.read(8 * 1024 * 1024 + 1)
            if len(content) != source["bytes"] or hashlib.sha256(content).hexdigest() != source["sha256"]:
                raise ValueError("Downloaded calibration source differs from pin: " + source["id"])
            path.write_bytes(content)
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError("Missing or changed calibration source: " + source["id"])
        paths[int(source["id"].split("-")[-1])] = path
    cache, records = {}, []
    for metric, schedule, sheet, col, header in METRICS:
        key = (schedule, sheet)
        if key not in cache:
            cache[key] = sheet_cells(paths[schedule], sheet)
        cells = cache[key]
        if cells.get(col + "5") != "Q3 2025-26" or "Residential" not in cells.get("B3", ""):
            raise ValueError("Quarter or residential electricity header changed")
        for region in REGIONS:
            rows = [ref[1:] for ref, value in cells.items() if ref.startswith("A") and ref[1:].isdigit() and value == region + " Total"]
            if len(rows) != 1:
                raise ValueError("Missing or ambiguous region total")
            ref = col + rows[0]
            value = cells.get(ref)
            if not isinstance(value, Decimal) or not value.is_finite() or value < 0:
                raise ValueError("Missing, nonnumeric or formula-derived source value")
            records.append(dict(metric=metric, region=region, value=str(value), source=f"aer-schedule-{schedule}", sheet=sheet, cell=ref, period_cell=col+"5", definition=cells[header]))
    values = {(r["region"], r["metric"]): Decimal(r["value"]) for r in records}
    checks = []
    for region in REGIONS:
        for num, rate in [("hardship_customers", "hardship_rate"), ("quarter_disconnections", "quarter_disconnection_rate")]:
            difference = abs(values[region, num] / values[region, "residential_customers"] - values[region, rate])
            if difference > Decimal("0.000000000001"):
                raise ValueError("Published rate does not reconcile to its denominator")
            checks.append(dict(region=region, rate=rate, matches_counts=True))
    for metric, *_ in METRICS:
        if metric.endswith(("_rate", "_aud")):
            continue
        if sum(values[r, metric] for r in REGIONS[1:]) != values["National", metric]:
            raise ValueError("State counts do not reconcile to published national count")
    result = dict(period="Q3 2025-26", extraction="Published literal cells; source bytes checksum-verified", records=records, rate_checks=checks,
                  national_count_reconciliation=True, population_generated=False,
                  limitation="Not a calibration-versus-generated-population result. Victoria and other Section 6 sources remain outstanding.")
    (ROOT / "data/calibration-aggregates.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(dict(source_workbooks=len(paths), aggregate_cells=len(records), reconciled_rates=len(checks), population_generated=False)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Explicitly acquire missing pinned workbooks")
    prepare(parser.parse_args().download)
