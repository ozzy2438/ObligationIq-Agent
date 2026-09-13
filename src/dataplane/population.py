"""Deterministic synthetic population; public marginals, generated joint structure."""

from datetime import date, timedelta
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP
import hashlib
import json
import math
import random


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def nearest(value):
    return int(value.to_integral_value(rounding=ROUND_HALF_UP))


def exact_scaled(rng, count, total):
    """Return nonnegative integers with an exact total and assumed exponential shape."""
    shape = [Decimal(str(-math.log(1 - rng.random()))) for _ in range(count)]
    shape_total = sum(shape)
    scaled = [value / shape_total * total for value in shape]
    values = [int(value.to_integral_value(rounding=ROUND_FLOOR)) for value in scaled]
    for index in sorted(range(count), key=lambda i: (scaled[i] - values[i], -i), reverse=True)[:total - sum(values)]:
        values[index] += 1
    return values


def exact_debts(rng, count, mean):
    """Assumed positive shape; integer cents preserve the target cohort mean."""
    if count < 1:
        raise ValueError("Population too small for an assistance-debt cohort")
    return exact_scaled(rng, count, nearest(mean * count * 100))


def largest_remainder(counts, total):
    source_total = sum(counts)
    raw = [Decimal(value) * total / source_total for value in counts]
    result = [int(value.to_integral_value(rounding=ROUND_FLOOR)) for value in raw]
    order = sorted(range(len(raw)), key=lambda i: (raw[i] - result[i], -i), reverse=True)
    for index in order[:total - sum(result)]:
        result[index] += 1
    return result


def build_debt_entry(inputs, contract):
    """Build a flow cohort distinct from current assistance-stock debt."""
    source = inputs["nsw"]["hardship_entry_distribution"]
    size = contract["debt_entry_cohort_size"]
    published = [band["published_count"] for band in source["bands"]]
    counts = largest_remainder(published, size)
    rng = random.Random(f"{contract['seed']}:NSW:debt-entry")
    ranges = [(1, 49999), (50001, 149999), (150001, 249999), (250001, 349999)]
    values = []
    labels = []
    for index, ((low, high), count) in enumerate(zip(ranges, counts[:4])):
        values.extend(rng.randint(low, high) for _ in range(count))
        labels.extend([index] * count)
    target_total = nearest(Decimal(source["mean_debt_aud"]) * size * 100)
    tail_floor = 350001
    tail_total = target_total - sum(values)
    minimum_tail_total = tail_floor * counts[4]
    if tail_total < minimum_tail_total:
        raise ValueError("Published entry-debt mean is incompatible with published bands")
    values.extend(tail_floor + value for value in exact_scaled(
        rng, counts[4], tail_total - minimum_tail_total))
    labels.extend([4] * counts[4])
    ordering = list(range(size))
    rng.shuffle(ordering)
    values = [values[index] for index in ordering]
    labels = [labels[index] for index in ordering]
    rows = []
    for index, (cents, band_index) in enumerate(zip(values, labels)):
        rows.append({
            "entry_id": "SYN-ENTRY-" + hashlib.sha256(f"{contract['seed']}:{index}".encode()).hexdigest()[:20],
            "synthetic": True,
            "reference_period": contract["reference_period"],
            "region": "NSW",
            "debt_cents_on_entry": cents,
            "published_band": source["bands"][band_index]["label"],
        })
    observed = [sum(row["published_band"] == source["bands"][index]["label"] for row in rows)
                for index in range(5)]
    comparisons = []
    for band, target_count, actual_count in zip(source["bands"], published, observed):
        target = Decimal(target_count) / sum(published)
        actual = Decimal(actual_count) / size
        delta = abs(actual - target)
        tolerance = Decimal(contract["rate_tolerance"])
        if delta > tolerance:
            raise ValueError("Debt-entry band outside tolerance: " + band["label"])
        comparisons.append({
            "region": "NSW",
            "metric": "hardship_entry_band_rate: " + band["label"],
            "source": "AER",
            "unit": "ratio",
            "published_or_derived": str(target),
            "generated": str(actual),
            "absolute_delta": str(delta),
            "tolerance": str(tolerance),
            "passed": True,
        })
    actual_mean = Decimal(sum(values)) / size / 100
    target_mean = Decimal(source["mean_debt_aud"])
    delta = abs(actual_mean - target_mean)
    if delta > Decimal(contract["mean_debt_tolerance_aud"]):
        raise ValueError("Debt-entry mean outside tolerance")
    comparisons.append({
        "region": "NSW",
        "metric": "hardship_entry_debt_aud",
        "source": "AER",
        "unit": "AUD",
        "published_or_derived": str(target_mean),
        "generated": str(actual_mean),
        "absolute_delta": str(delta),
        "tolerance": contract["mean_debt_tolerance_aud"],
        "passed": True,
    })
    return rows, comparisons, {
        "cohort_size": size,
        "published_source_count": sum(published),
        "generated_band_counts": observed,
        "source_cells": [band["source_cell"] for band in source["bands"]],
        "current_debt_cohort_reused": False,
    }


def business_day_after(start, count):
    current = start
    remaining = count
    while remaining:
        current += timedelta(days=1)
        if current.weekday() < 5:
            remaining -= 1
    return current


def build_control_cases(rows, inputs, contract):
    obligations = {record["obligation_id"]: record for record in inputs["injection_obligations"]}
    expected = set(contract["injection_obligation_ids"])
    if set(obligations) != expected:
        raise ValueError("Injection obligation set changed")
    accounts = {region: [row for row in rows if row["region"] == region] for region in ("NSW", "VIC")}
    cases, truth = [], []
    base = date(2026, 8, 3)
    variants = ("compliant", "breach", "insufficient_evidence")
    for obligation_index, obligation_id in enumerate(sorted(obligations)):
        obligation = obligations[obligation_id]
        region = "NSW" if obligation["regime"] == "NERL_NERR" else "VIC"
        for variant_index, variant in enumerate(variants):
            account = accounts[region][obligation_index * len(variants) + variant_index]
            case_id = "CASE-" + hashlib.sha256(
                f"{contract['seed']}:{obligation_id}:{variant}".encode()).hexdigest()[:16]
            timed = obligation["deadline_value"] is not None
            action_at = None
            action_completed = None
            non_completion_confirmed_at = None
            if variant == "compliant":
                action_completed = True
                action_at = business_day_after(base, obligation["deadline_value"] if timed else 0).isoformat()
            elif variant == "breach":
                if timed:
                    action_completed = True
                    action_at = business_day_after(base, obligation["deadline_value"] + 1).isoformat()
                else:
                    action_completed = False
                    non_completion_confirmed_at = contract["scenario_as_of"]
            evidence = {
                name: {"present": variant != "insufficient_evidence" or index != 0,
                       "value": (False if variant == "breach" and not timed and index == len(obligation["evidence_required"]) - 1 else True)}
                for index, name in enumerate(obligation["evidence_required"])
            }
            cases.append({
                "case_id": case_id,
                "account_id": account["account_id"],
                "synthetic": True,
                "obligation_id": obligation_id,
                "regime": obligation["regime"],
                "as_of_date": contract["scenario_as_of"],
                "trigger_occurred": True,
                "trigger_at": base.isoformat(),
                "action_completed": action_completed,
                "action_at": action_at,
                "non_completion_confirmed_at": non_completion_confirmed_at,
                "evidence": evidence,
            })
            truth.append({
                "case_id": case_id,
                "obligation_id": obligation_id,
                "source_clause": obligation["clause_reference"],
                "source_sha256": obligation["source_sha256"],
                "expected_status": variant,
                "reason": (
                    "Required action completed within the source deadline."
                    if variant == "compliant" and timed else
                    "Required action is affirmatively evidenced."
                    if variant == "compliant" else
                    "Required action completed after the source deadline."
                    if variant == "breach" and timed else
                    "Complete audit evidence confirms the required action was not completed."
                    if variant == "breach" else
                    "At least one source-required evidence item is absent."
                ),
            })
    case_payload = b"".join(encode(row) for row in cases)
    truth_document = {
        "synthetic": True,
        "scenario_as_of": contract["scenario_as_of"],
        "input_cases_sha256": hashlib.sha256(case_payload).hexdigest(),
        "review_composition": inputs["review_composition"],
        "cases": truth,
    }
    return cases, truth_document


def build(inputs, contract):
    if contract["version"] != 2 or not contract["phase3_complete"]:
        raise ValueError("This generator implements the completed version 2 population")
    if contract["reference_period"] != inputs["reference_period"]:
        raise ValueError("Calibration reference period mismatch")
    profiles = inputs["operational_context"]["profiles"]
    contexts = inputs["operational_context"]["seasonality_contexts"]
    if len(profiles) != 299 or set(contexts) != {"NSW", "VIC"}:
        raise ValueError("Operational profile/context contract changed")
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
            profile = profiles[rng.randrange(len(profiles))]
            cohort.append({
                "account_id": "SYN-" + hashlib.sha256(f"{contract['seed']}:{region}:{index}".encode()).hexdigest()[:20],
                "synthetic": True,
                "scenario_as_of": contract["scenario_as_of"],
                "reference_period": contract["reference_period"],
                "region": region,
                "postcode": area["postcode"],
                "area_irsd_decile": area["area_irsd_decile"],
                "area_jobseeker_count": area["area_jobseeker_count"],
                "assistance_family": family,
                "receiving_assistance": index in members,
                "assistance_debt_cents": next(debts) if index in members else None,
                "reference_quarter_nonpayment_disconnection": index in disconnections,
                "life_support_status": life[index],
                "tariff_plan_id": plan["plan_id"],
                "tariff_eligibility_assumed": True,
                "consumption_profile_id": profile["profile_id"],
                "profile_annual_consumption_kwh": profile["annual_consumption_kwh"],
                "seasonality_context_id": contexts[region]["context_id"],
            })
        observed_members = sum(row["receiving_assistance"] for row in cohort)
        metrics = [
            (family + "_participation_rate", participation, Decimal(observed_members) / size, "ratio"),
            (family + "_current_debt_aud", mean, Decimal(sum(row["assistance_debt_cents"] or 0 for row in cohort)) / observed_members / 100, "AUD"),
            ("reference_quarter_disconnection_rate", disconnected, Decimal(sum(row["reference_quarter_nonpayment_disconnection"] for row in cohort)) / size, "ratio"),
        ]
        if region == "NSW":
            for status in ("confirmed", "unconfirmed"):
                metrics.append(("life_support_" + status + "_rate", Decimal(source["life_support_" + status]["value"]) / denominator, Decimal(sum(row["life_support_status"] == status for row in cohort)) / size, "ratio"))
        for name, target, actual, unit in metrics:
            tolerance = Decimal(contract["mean_debt_tolerance_aud"] if unit == "AUD" else contract["rate_tolerance"])
            if tolerance <= 0 or (unit == "ratio" and tolerance > Decimal("0.5") / size):
                raise ValueError("Rate tolerance cannot exceed half an account divided by cohort size")
            delta = abs(actual - target)
            if delta > tolerance:
                raise ValueError("Calibration outside tolerance: " + region + " " + name)
            comparisons.append({
                "region": region,
                "metric": name,
                "source": "AER" if region == "NSW" else "ESC",
                "unit": unit,
                "published_or_derived": str(target),
                "generated": str(actual),
                "absolute_delta": str(delta),
                "tolerance": str(tolerance),
                "passed": True,
            })
        geography_summary.append({
            "region": region,
            "eligible_postcodes": len(areas),
            "sampled_postcodes": len({row["postcode"] for row in cohort}),
            "assistance_accounts": len(members),
            "reference_quarter_disconnections": len(disconnections),
            "mean_area_irsd_decile_assistance": sum(area_draws[i]["area_irsd_decile"] for i in members) / len(members),
            "mean_area_irsd_decile_other": sum(area_draws[i]["area_irsd_decile"] for i in range(size) if i not in members) / (size - len(members)),
            "consumption_profiles_used": len({row["consumption_profile_id"] for row in cohort}),
            "seasonality_context_id": contexts[region]["context_id"],
        })
        rows.extend(cohort)
    if len({row["account_id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate synthetic account identifier")

    debt_rows, debt_comparisons, debt_summary = build_debt_entry(inputs, contract)
    comparisons.extend(debt_comparisons)
    cases, truth = build_control_cases(rows, inputs, contract)
    artifacts = {
        "accounts": b"".join(encode(row) for row in rows),
        "debt_entries": b"".join(encode(row) for row in debt_rows),
        "control_cases": b"".join(encode(row) for row in cases),
        "ground_truth": (json.dumps(truth, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode(),
    }
    report = {
        "status": "Phase 3 complete: calibrated synthetic population and isolated challenge set",
        "synthetic": True,
        "phase3_complete": True,
        "scenario_as_of": contract["scenario_as_of"],
        "reference_period": contract["reference_period"],
        "account_count": len(rows),
        "accounts_per_region": contract["accounts_per_region"],
        "seed": contract["seed"],
        "output_sha256": hashlib.sha256(artifacts["accounts"]).hexdigest(),
        "output_bytes": len(artifacts["accounts"]),
        "artifact_sha256": {name: hashlib.sha256(payload).hexdigest() for name, payload in artifacts.items()},
        "artifact_bytes": {name: len(payload) for name, payload in artifacts.items()},
        "inputs_sha256": hashlib.sha256(encode(inputs)).hexdigest(),
        "contract_sha256": hashlib.sha256(encode(contract)).hexdigest(),
        "comparisons": comparisons,
        "passed_comparisons": sum(item["passed"] for item in comparisons),
        "geography_summary": geography_summary,
        "source_profiles": {
            "source_customer_count": inputs["operational_context"]["source_customer_count"],
            "complete_profile_count": len(profiles),
            "excluded_incomplete_profile_count": inputs["operational_context"]["excluded_incomplete_profile_count"],
        },
        "seasonality_coverage": {
            region: {
                "aemo_intervals": sum(month["aemo_interval_count"] for month in context["months"]),
                "bom_temperature_days": sum(month["bom_temperature_day_count"] for month in context["months"]),
                "months": len(context["months"]),
            } for region, context in contexts.items()
        },
        "debt_entry": debt_summary,
        "breach_injections": sum(item["expected_status"] == "breach" for item in truth["cases"]),
        "challenge_cases": len(cases),
        "challenge_case_mix": {variant: sum(item["expected_status"] == variant for item in truth["cases"])
                               for variant in ("compliant", "breach", "insufficient_evidence")},
        "ground_truth_created": True,
        "ground_truth_visible_to_controls_or_agents": False,
        "review_composition": inputs["review_composition"],
        "unmeasured": contract["unmeasured"],
        "model_calls": 0,
        "model_spend_aud": "0",
    }
    return artifacts, report
