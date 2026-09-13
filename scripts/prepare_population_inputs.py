"""Extract a bounded NSW/VIC calibration contract from checksum-pinned public data."""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.prepare_calibration import sheet_cells
from src.config import ROOT
from src.register.obligations import for_controls, load_candidates, review_composition


def numeric(value):
    if not isinstance(value, Decimal) or not value.is_finite() or value < 0:
        raise ValueError("Missing, negative, nonnumeric or formula-derived input")
    return value


def esc_metric(path, sheet, indicator):
    cells = sheet_cells(path, sheet)
    column = "I" if sheet == "Disconnections" else "J"
    result = {}
    for ref, value in cells.items():
        if not ref.startswith("A") or value != "Electricity":
            continue
        row = ref[1:]
        if [cells.get(c + row) for c in "BCD"] != ["2025-26", "Q3", "Residential"]:
            continue
        if cells.get("G" + row) != indicator:
            continue
        category = cells.get("I" + row, "") if column == "J" else ""
        category = category.lower().replace("residential (who ", "").rstrip(")")
        key = (cells["F" + row], category)
        if key in result:
            raise ValueError("Duplicate ESC retailer/category observation")
        result[key] = dict(value=str(numeric(cells.get(column + row))), cell=column + row)
    if not result:
        raise ValueError("Missing ESC metric: " + indicator)
    return dict(source="esc.xlsx", sheet=sheet, indicator=indicator,
                observations=[dict(retailer=k[0], category=k[1], **v) for k, v in sorted(result.items())],
                value=str(sum(Decimal(v["value"]) for v in result.values())))


def prepare(download=False):
    manifest = json.loads((ROOT / "data/context-sources.json").read_text())
    paths = {}
    for source in manifest["sources"]:
        path = ROOT / "data/raw/calibration" / source["id"]
        if not path.exists() and download:
            with urlopen(Request(source["url"], headers=source.get("headers", {})), timeout=45) as response:
                body = response.read(source["bytes"] + 1)
            if len(body) != source["bytes"] or hashlib.sha256(body).hexdigest() != source["sha256"]:
                raise ValueError("Source changed; review a new pin: " + source["id"])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError("Missing or changed source: " + source["id"])
        paths[source["id"]] = path

    aer = json.loads((ROOT / "data/calibration-aggregates.json").read_text())
    nsw = {r["metric"]: r for r in aer["records"] if r["region"] == "NSW"}
    schedule4 = ROOT / "data/raw/calibration/aer-schedule-4.xlsx"
    schedule4_pin = next(s for s in json.loads((ROOT / "data/calibration-sources.json").read_text())["sources"]
                         if s["id"] == "aer-schedule-4")
    if (not schedule4.exists() or hashlib.sha256(schedule4.read_bytes()).hexdigest() != schedule4_pin["sha256"]):
        raise ValueError("Missing or changed AER schedule 4 for debt-entry distribution")
    entry_cells = sheet_cells(schedule4, "Hardship debt on entering")
    band_columns = "VWXYZ"
    if entry_cells.get("V4") != "Q3 2025-26" or entry_cells.get("A220") != "NSW Total":
        raise ValueError("AER debt-entry band anchors changed")
    entry_bands = []
    for column in band_columns:
        value = numeric(entry_cells.get(column + "220"))
        entry_bands.append({
            "label": entry_cells[column + "6"],
            "published_count": int(value),
            "source_cell": column + "220",
        })
    nsw["hardship_entry_distribution"] = {
        "source": "aer-schedule-4",
        "sheet": "Hardship debt on entering",
        "period_cell": "V4",
        "bands": entry_bands,
        "published_count": sum(item["published_count"] for item in entry_bands),
        "mean_debt_aud": nsw["hardship_entry_debt_aud"]["value"],
        "mean_source_cell": nsw["hardship_entry_debt_aud"]["cell"],
        "cohort_note": "Entry-flow distribution; separate from the current hardship-stock debt cohort.",
    }
    esc = paths["esc.xlsx"]
    vic = {
        "residential_customers": esc_metric(esc, "Overview", "Electricity Customers"),
        "tailored_assistance_customers": esc_metric(esc, "Receiving Assistance", "Accounts receiving tailored assistance"),
        "quarter_disconnections": esc_metric(esc, "Disconnections", "Disconnection for non-payment (residential accounts)"),
    }
    debt = esc_metric(esc, "TA Arrears", "Average total arrears of residential accounts receiving tailored assistance ($)")
    # Retailer means cannot be summed or averaged without their matching category weights.
    means = {(r["retailer"], r["category"]): Decimal(r["value"]) for r in debt["observations"]}
    weighted = Decimal(0)
    for r in vic["tailored_assistance_customers"]["observations"]:
        count = Decimal(r["value"])
        if count:
            weighted += count * means[r["retailer"], r["category"]]
    debt["value"] = str(weighted / Decimal(vic["tailored_assistance_customers"]["value"]))
    debt["derivation"] = "Sum(retailer/category mean * matching end-quarter count) / total tailored-assistance accounts; published means rounded to cents."
    vic["tailored_assistance_current_debt_aud"] = debt

    plans = {}
    catalogue = {r["planId"]: r for r in json.loads(paths["cdr-agl-plans.json"].read_text())["data"]["plans"]}
    for region, file in [("NSW", "cdr-AGL1055859MRE2.json"), ("VIC", "cdr-AGD762152MR.json")]:
        plan = json.loads(paths[file].read_text())["data"]
        contract = plan["electricityContract"]
        if plan["fuelType"] != "ELECTRICITY" or plan["customerType"] != "RESIDENTIAL" or contract["pricingModel"] != "SINGLE_RATE":
            raise ValueError("Unexpected plan scope")
        if catalogue[plan["planId"]]["geography"] != plan["geography"]:
            raise ValueError("Catalogue/detail geography mismatch")
        plans[region] = dict(source=file, plan_id=plan["planId"], display_name=plan["displayName"],
                             effective_from=plan["effectiveFrom"], effective_to=plan.get("effectiveTo"),
                             geography=plan["geography"], pricing_model=contract["pricingModel"],
                             eligibility_assumption="Applicable single-rate network tariff and service area; no real customer's eligibility has been assessed.")

    seifa = sheet_cells(paths["seifa.xlsx"], "Table 1")
    dss = sheet_cells(paths["dss.xlsx"], "Postcode")
    if seifa.get("A6") != "2021 Postal Area (POA) Code" or dss.get("O3") != "JobSeeker Payment":
        raise ValueError("Geography headers changed")
    payments = {}
    for ref, value in dss.items():
        if ref.startswith("A") and isinstance(value, Decimal) and value == int(value) and 0 < value < 10000:
            postcode = str(int(value)).zfill(4)
            if postcode in payments:
                raise ValueError("Duplicate DSS postcode")
            payments[postcode] = (numeric(dss.get("O" + ref[1:])), "O" + ref[1:])
    geography = []
    for ref, value in seifa.items():
        if not ref.startswith("A") or not isinstance(value, str) or len(value) != 4 or not value.isdigit():
            continue
        row = ref[1:]
        if seifa.get("K" + row) == "Y" or seifa.get("L" + row) == "Y" or value not in payments:
            continue
        for region, plan in plans.items():
            if value not in plan["geography"]["includedPostcodes"]:
                continue
            population, decile = numeric(seifa.get("J" + row)), numeric(seifa.get("C" + row))
            if not population or not 1 <= decile <= 10:
                continue
            geography.append(dict(region=region, postcode=value, resident_population=int(population),
                                  area_irsd_decile=int(decile), area_jobseeker_count=int(payments[value][0]),
                                  seifa_row=int(row), dss_cell=payments[value][1]))
    if any(not any(g["region"] == r for g in geography) for r in plans):
        raise ValueError("Empty eligible geography")
    operational_path = ROOT / "data/operational-context.json"
    operational = json.loads(operational_path.read_text())
    if operational.get("profile_count") != len(operational.get("profiles", [])) or not operational.get("seasonality_contexts"):
        raise ValueError("Incomplete operational context")
    eligible = for_controls(load_candidates())
    injection_ids = {"OIQ-002", "OIQ-023", "OIQ-024", "OIQ-028", "OIQ-030", "OIQ-032"}
    injection_obligations = [record for record in eligible if record["obligation_id"] in injection_ids]
    if {record["obligation_id"] for record in injection_obligations} != injection_ids:
        raise ValueError("A source-reviewed injection obligation lost eligibility")
    register_inputs = {
        name: hashlib.sha256((ROOT / "data" / name).read_bytes()).hexdigest()
        for name in ("obligation-candidates.json", "human-reviews.json", "source-reviews.json", "operational-reviews.json")
    }
    result = dict(reference_period=aer["period"], nsw=nsw, vic=vic, plans=plans,
                  geography=sorted(geography, key=lambda g: (g["region"], g["postcode"])),
                  operational_context_summary={
                      "profile_count": operational["profile_count"],
                      "context_ids": {region: context["context_id"]
                                      for region, context in operational["seasonality_contexts"].items()},
                  },
                  operational_context_sha256=hashlib.sha256(operational_path.read_bytes()).hexdigest(),
                  operational_source_manifest_sha256=hashlib.sha256((ROOT / "data/operational-sources.json").read_bytes()).hexdigest(),
                  injection_obligations=sorted(injection_obligations, key=lambda record: record["obligation_id"]),
                  review_composition=review_composition(eligible),
                  register_inputs_sha256=register_inputs,
                  source_manifest_sha256=hashlib.sha256((ROOT / "data/context-sources.json").read_bytes()).hexdigest(),
                  aer_source_manifest_sha256=hashlib.sha256((ROOT / "data/calibration-sources.json").read_bytes()).hexdigest(),
                  aer_aggregates_sha256=hashlib.sha256((ROOT / "data/calibration-aggregates.json").read_bytes()).hexdigest())
    target = ROOT / "data/population-inputs.json"
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(dict(verified_context_sources=len(paths), eligible_postcodes=len(geography), output=str(target.relative_to(ROOT)))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Acquire missing pinned sources; changed upstream bytes are refused")
    prepare(parser.parse_args().download)
