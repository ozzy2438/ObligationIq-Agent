"""Pin and reduce official consumption, demand and weather sources for Phase 3."""

import argparse
import csv
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import hashlib
from html import unescape
import io
import json
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import ROOT


RAW = ROOT / "data/raw/calibration"
MANIFEST = ROOT / "data/operational-sources.json"
OUTPUT = ROOT / "data/operational-context.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_files(manifest):
    ausgrid = manifest["ausgrid"]
    yield ausgrid, ausgrid["resolved_download_url"]
    aemo = manifest["aemo"]
    for item in aemo["files"]:
        yield item, aemo["url_template"].format(month=item["month"])
    bom = manifest["bom"]
    for station in bom["stations"]:
        for item in station["files"]:
            yield item, bom["url_template"].format(
                month=item["month"], product=station["product"])


def acquire_and_verify(manifest, download):
    for item, url in source_files(manifest):
        path = RAW / item["id"]
        if not path.exists() and download:
            request = Request(url, headers={"User-Agent": "ObligationIQ source acquisition/1.0"})
            with urlopen(request, timeout=90) as response:
                body = response.read(item["bytes"] + 1)
            if len(body) != item["bytes"] or hashlib.sha256(body).hexdigest() != item["sha256"]:
                raise ValueError("Operational source changed; review a new pin: " + item["id"])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
        if not path.exists() or path.stat().st_size != item["bytes"] or sha256(path) != item["sha256"]:
            raise ValueError("Missing or changed operational source: " + item["id"])


def rounded(value, places="0.000001"):
    return str(value.quantize(Decimal(places), rounding=ROUND_HALF_UP))


def ausgrid_profiles(path):
    customers = {}
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        csv_names = [name for name in names if name.lower().endswith(".csv")]
        note_names = [name for name in names if name.lower().endswith(".pdf")]
        if len(csv_names) != 1 or len(note_names) != 1:
            raise ValueError("Unexpected Ausgrid archive contents")
        with archive.open(csv_names[0]) as binary:
            reader = csv.reader(io.TextIOWrapper(binary, encoding="utf-8-sig", newline=""))
            notice = next(reader)
            header = next(reader)
            if ("Before using this data" not in notice[0] or header[:5] !=
                    ["Customer", "Generator Capacity", "Postcode", "Consumption Category", "date"]):
                raise ValueError("Unexpected Ausgrid header")
            slots = header[5:53]
            if len(slots) != 48 or header[53] != "Row Quality":
                raise ValueError("Ausgrid half-hour columns changed")
            for row in reader:
                if len(row) < 54 or row[3] != "GC":
                    continue
                values = [Decimal(value) if value else Decimal(0) for value in row[5:53]]
                if any(value < 0 for value in values):
                    raise ValueError("Negative Ausgrid general consumption")
                when = datetime.strptime(row[4], "%d/%m/%Y").date()
                item = customers.setdefault(row[0], {
                    "slots": [Decimal(0)] * 48,
                    "months": {month: Decimal(0) for month in range(1, 13)},
                    "days": {month: 0 for month in range(1, 13)},
                })
                for index, value in enumerate(values):
                    item["slots"][index] += value
                total = sum(values)
                item["months"][when.month] += total
                item["days"][when.month] += 1
    if len(customers) != 300:
        raise ValueError("Ausgrid customer population changed")
    complete = {customer: item for customer, item in customers.items()
                if sum(item["days"].values()) == 365}
    if len(complete) != 299:
        raise ValueError("Ausgrid complete-profile count changed")
    monthly_totals = {month: sum(item["months"][month] for item in complete.values())
                      for month in range(1, 13)}
    monthly_days = {month: sum(item["days"][month] for item in complete.values())
                    for month in range(1, 13)}
    profiles = []
    for customer, item in sorted(complete.items(), key=lambda pair: int(pair[0])):
        total = sum(item["slots"])
        annual_daily = total / Decimal(365)
        if total <= 0:
            raise ValueError("Empty Ausgrid customer profile")
        profiles.append({
            "profile_id": "AUSGRID-GC-" + hashlib.sha256(("2012-13:" + customer).encode()).hexdigest()[:12],
            "annual_consumption_kwh": rounded(total, "0.001"),
            "half_hour_share": [rounded(value / total, "0.00000001") for value in item["slots"]],
            "monthly_daily_factor": {
                str(month).zfill(2): rounded((item["months"][month] / item["days"][month]) / annual_daily)
                for month in range(1, 13)
            },
        })
    aggregate_daily = sum(monthly_totals.values()) / Decimal(sum(monthly_days.values()))
    factors = {
        str(month).zfill(2): rounded((monthly_totals[month] / monthly_days[month]) / aggregate_daily)
        for month in range(1, 13)
    }
    return profiles, factors, slots


def aemo_month(path):
    values = {"NSW1": [], "VIC1": []}
    with zipfile.ZipFile(path) as outer:
        for member in sorted(outer.namelist()):
            with zipfile.ZipFile(io.BytesIO(outer.read(member))) as inner:
                csv_names = [name for name in inner.namelist() if name.lower().endswith(".csv")]
                if len(csv_names) != 1:
                    raise ValueError("Unexpected AEMO daily archive contents")
                rows = csv.reader(io.TextIOWrapper(inner.open(csv_names[0]), encoding="utf-8-sig", newline=""))
                for row in rows:
                    if row and row[0] == "D" and row[1:4] == ["OPERATIONAL_DEMAND", "ACTUAL", "3"] and row[4] in values:
                        demand = Decimal(row[6])
                        if demand < 0:
                            raise ValueError("Negative AEMO operational demand")
                        values[row[4]].append(demand)
    if any(len(region) < 28 * 48 for region in values.values()):
        raise ValueError("Incomplete AEMO monthly region coverage")
    return {region: {"interval_count": len(series), "mean_mw": sum(series) / len(series)}
            for region, series in values.items()}


def bom_month(path):
    content = path.read_text(encoding="latin-1")
    matches = re.findall(r"<th[^>]*scope='row'[^>]*>(\d+)</th>(.*?)</tr>", content, re.I | re.S)
    daily = []
    for _, body in matches:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", body, re.I | re.S)
        cleaned = [unescape(re.sub(r"<[^>]+>", "", cell)).replace("\xa0", "").strip() for cell in cells]
        if len(cleaned) >= 3 and cleaned[1] and cleaned[2]:
            daily.append((Decimal(cleaned[1]) + Decimal(cleaned[2])) / 2)
    if len(daily) < 27:
        raise ValueError("Incomplete BOM daily temperature coverage: " + path.name)
    return {"day_count": len(daily), "mean_midpoint_c": sum(daily) / len(daily)}


def prepare(download=False):
    manifest = json.loads(MANIFEST.read_text())
    acquire_and_verify(manifest, download)
    profiles, household_factors, slots = ausgrid_profiles(RAW / manifest["ausgrid"]["id"])

    demand = {}
    for item in manifest["aemo"]["files"]:
        demand[item["month"]] = aemo_month(RAW / item["id"])
    weather = {"NSW": {}, "VIC": {}}
    for station in manifest["bom"]["stations"]:
        for item in station["files"]:
            weather[station["region"]][item["month"]] = bom_month(RAW / item["id"])

    region_ids = {"NSW": "NSW1", "VIC": "VIC1"}
    contexts = {}
    for region, region_id in region_ids.items():
        interval_total = sum(demand[month][region_id]["mean_mw"] * demand[month][region_id]["interval_count"] for month in demand)
        interval_count = sum(demand[month][region_id]["interval_count"] for month in demand)
        annual_mean = interval_total / interval_count
        months = []
        for month in sorted(demand):
            record = demand[month][region_id]
            observation = weather[region][month]
            months.append({
                "month": month,
                "aemo_interval_count": record["interval_count"],
                "aemo_operational_demand_mean_mw": rounded(record["mean_mw"], "0.001"),
                "aemo_operational_demand_factor": rounded(record["mean_mw"] / annual_mean),
                "bom_temperature_day_count": observation["day_count"],
                "bom_mean_daily_midpoint_c": rounded(observation["mean_midpoint_c"], "0.01"),
                "ausgrid_household_daily_factor": household_factors[month[-2:]],
            })
        contexts[region] = {
            "context_id": "AEMO-BOM-202508-202607-" + region,
            "aemo_region_id": region_id,
            "bom_product": next(s["product"] for s in manifest["bom"]["stations"] if s["region"] == region),
            "months": months,
        }

    result = {
        "version": 1,
        "synthetic": False,
        "prepared_on": manifest["retrieved_on"],
        "source_manifest_sha256": sha256(MANIFEST),
        "ausgrid_source_sha256": manifest["ausgrid"]["sha256"],
        "source_customer_count": 300,
        "excluded_incomplete_profile_count": 1,
        "profile_count": len(profiles),
        "half_hour_labels": slots,
        "profiles": profiles,
        "seasonality_contexts": contexts,
        "derivation": "Ausgrid GC rows supply de-identified household shape and month factors. AEMO regional demand and BOM city temperature remain separate observed context series; no causal relation or blended factor is asserted.",
        "limitations": [
            "The 300 solar households are not representative of all Ausgrid or state customers.",
            "The same Ausgrid household profile library is used as a shape prior for both pilot regions; Victorian consumption is not claimed to be observed.",
            "AEMO operational demand is system-level and BOM temperature is city-level context, not customer-level calibration.",
        ],
    }
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({
        "profiles": len(profiles),
        "aemo_region_intervals": {region: sum(m["aemo_interval_count"] for m in context["months"])
                                  for region, context in contexts.items()},
        "bom_days": {region: sum(m["bom_temperature_day_count"] for m in context["months"])
                     for region, context in contexts.items()},
        "output": str(OUTPUT.relative_to(ROOT)),
    }))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Acquire missing checksum-pinned official sources")
    prepare(parser.parse_args().download)
