"""Deterministic synthetic population; public marginal calibration, generated joint structure."""
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import math
import random


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def nearest(value):
    return int(value.to_integral_value(rounding=ROUND_HALF_UP))


def exact_debts(rng, count, mean):
    """Assumed positive shape; integer cents preserve the target cohort mean."""
    if count < 1:
        raise ValueError("Population too small for an assistance-debt cohort")
    shape = [Decimal(str(-math.log(1 - rng.random()))) for _ in range(count)]
    total = nearest(mean * count * 100)
    shape_total = sum(shape)
    scaled = [v / shape_total * total for v in shape]
    cents = [int(v) for v in scaled]
    for i in sorted(range(count), key=lambda i: (scaled[i] - cents[i], -i), reverse=True)[:total - sum(cents)]:
        cents[i] += 1
    return cents


def build(inputs, contract):
    if contract["version"] != 1 or contract["phase3_complete"]:
        raise ValueError("This generator implements only the version 1 core population")
    if contract["reference_period"] != inputs["reference_period"]:
        raise ValueError("Calibration reference period mismatch")
    rows, comparisons, geography_summary = [], [], []
    for region, size in contract["accounts_per_region"].items():
        if not isinstance(size, int) or not 1000 <= size <= 100000:
            raise ValueError("Require 1000 to 100000 accounts per regional cohort")
        source = inputs[region.lower()]
        denominator = Decimal(source["residential_customers"]["value"])
        family = "hardship" if region == "NSW" else "tailored_assistance"
        participation = Decimal(source[family + "_customers"]["value"]) / denominator
        mean = Decimal(source[family + "_current_debt_aud"]["value"])
        disconnected = Decimal(source["quarter_disconnections"]["value"]) / denominator
        plan = inputs["plans"][region]
        if plan["effective_from"][:10] > contract["scenario_as_of"] or (plan["effective_to"] and plan["effective_to"][:10] <= contract["scenario_as_of"]):
            raise ValueError("Plan outside the frozen scenario date")
        areas = [g for g in inputs["geography"] if g["region"] == region]
        if not areas or len({g["postcode"] for g in areas}) != len(areas):
            raise ValueError("Missing or duplicate regional geography")
        if any(g["postcode"] not in plan["geography"]["includedPostcodes"] for g in areas):
            raise ValueError("Postcode outside the selected tariff footprint")
        rng = random.Random(f"{contract['seed']}:{region}")
        area_draws = rng.choices(areas, weights=[g["resident_population"] for g in areas], k=size)
        weights = [1 + (10 - g["area_irsd_decile"]) / 9 + 10 * min(g["area_jobseeker_count"] / g["resident_population"], 0.2) for g in area_draws]
        ordering = sorted(range(size), key=lambda i: -math.log(1 - rng.random()) / weights[i])
        members = set(ordering[:nearest(participation * size)])
        debts = iter(exact_debts(rng, len(members), mean))
        disconnections = set(rng.sample(range(size), nearest(disconnected * size)))
        life = [None] * size
        if region == "NSW":
            indices = rng.sample(range(size), size)
            confirmed = nearest(Decimal(source["life_support_confirmed"]["value"]) / denominator * size)
            unconfirmed = nearest(Decimal(source["life_support_unconfirmed"]["value"]) / denominator * size)
            if confirmed + unconfirmed > size:
                raise ValueError("Incompatible life-support marginal counts")
            for j, index in enumerate(indices):
                life[index] = "confirmed" if j < confirmed else "unconfirmed" if j < confirmed + unconfirmed else "not_registered"
        cohort = []
        for index, area in enumerate(area_draws):
            cohort.append(dict(
                account_id="SYN-" + hashlib.sha256(f"{contract['seed']}:{region}:{index}".encode()).hexdigest()[:20],
                synthetic=True, scenario_as_of=contract["scenario_as_of"], reference_period=contract["reference_period"],
                region=region, postcode=area["postcode"], area_irsd_decile=area["area_irsd_decile"],
                area_jobseeker_count=area["area_jobseeker_count"], assistance_family=family,
                receiving_assistance=index in members, assistance_debt_cents=next(debts) if index in members else None,
                reference_quarter_nonpayment_disconnection=index in disconnections,
                life_support_status=life[index], tariff_plan_id=plan["plan_id"],
                tariff_eligibility_assumed=True, consumption_profile_id=None, seasonality_context_id=None))
        observed_members = sum(r["receiving_assistance"] for r in cohort)
        metrics = [
            (family + "_participation_rate", participation, Decimal(observed_members) / size, "ratio"),
            (family + "_current_debt_aud", mean, Decimal(sum(r["assistance_debt_cents"] or 0 for r in cohort)) / observed_members / 100, "AUD"),
            ("reference_quarter_disconnection_rate", disconnected, Decimal(sum(r["reference_quarter_nonpayment_disconnection"] for r in cohort)) / size, "ratio"),
        ]
        if region == "NSW":
            for status in ("confirmed", "unconfirmed"):
                metrics.append(("life_support_" + status + "_rate", Decimal(source["life_support_" + status]["value"]) / denominator, Decimal(sum(r["life_support_status"] == status for r in cohort)) / size, "ratio"))
        for name, target, actual, unit in metrics:
            tolerance = Decimal(contract["mean_debt_tolerance_aud"] if unit == "AUD" else contract["rate_tolerance"])
            if tolerance <= 0 or (unit == "ratio" and tolerance > Decimal("0.5") / size):
                raise ValueError("Rate tolerance cannot exceed half an account divided by cohort size")
            delta = abs(actual - target)
            if delta > tolerance:
                raise ValueError("Calibration outside tolerance: " + region + " " + name)
            comparisons.append(dict(region=region, metric=name, source="AER" if region == "NSW" else "ESC", unit=unit,
                                    published_or_derived=str(target), generated=str(actual), absolute_delta=str(delta),
                                    tolerance=str(tolerance), passed=True))
        geography_summary.append(dict(region=region, eligible_postcodes=len(areas), sampled_postcodes=len({r["postcode"] for r in cohort}),
                                      assistance_accounts=len(members), reference_quarter_disconnections=len(disconnections),
                                      mean_area_irsd_decile_assistance=sum(area_draws[i]["area_irsd_decile"] for i in members) / len(members),
                                      mean_area_irsd_decile_other=sum(area_draws[i]["area_irsd_decile"] for i in range(size) if i not in members) / (size - len(members))))
        rows.extend(cohort)
    if len({r["account_id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate synthetic account identifier")
    payload = b"".join(encode(r) for r in rows)
    report = dict(status="calibrated core only; Phase 3 incomplete", synthetic=True, phase3_complete=False,
                  scenario_as_of=contract["scenario_as_of"], reference_period=contract["reference_period"],
                  account_count=len(rows), accounts_per_region=contract["accounts_per_region"], seed=contract["seed"],
                  output_sha256=hashlib.sha256(payload).hexdigest(), output_bytes=len(payload),
                  inputs_sha256=hashlib.sha256(encode(inputs)).hexdigest(), contract_sha256=hashlib.sha256(encode(contract)).hexdigest(),
                  comparisons=comparisons, geography_summary=geography_summary,
                  remaining=contract["remaining"], unmeasured=contract["unmeasured"],
                  breach_injections=0, ground_truth_created=False, model_calls=0, model_spend_aud="0")
    return payload, report
