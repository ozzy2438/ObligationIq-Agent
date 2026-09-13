"""Render the public cost model from the gateway ledger or its committed result snapshot."""

import argparse
import json
from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import ROOT, settings
from src.gateway.ledger import Ledger

RESULTS = ROOT / "docs/phase-7-evaluation-results.json"
OUTPUT = ROOT / "docs/cost-model.md"


def aud(value):
    return f"{float(value):.6f}"


def validate(report):
    ledger = report["ledger_costs_aud"]
    execution = report["agent_execution"]
    confirmed = sum(Decimal(item["confirmed_microaud"]) for item in execution.values())
    if confirmed / Decimal(1_000_000) != Decimal(ledger["confirmed_usage_aud"]):
        raise ValueError("Model totals do not equal confirmed ledger spend")
    for item in execution.values():
        expected = Decimal(item["confirmed_microaud"]) / Decimal(72_000_000)
        if Decimal(item["confirmed_cost_per_case_aud"]) != expected:
            raise ValueError("Published per-case cost does not use confirmed spend")
    if (Decimal(ledger["worst_case_aud"]) - Decimal(ledger["confirmed_usage_aud"]) !=
            Decimal(ledger["misclassification_overstatement_aud"]) +
            Decimal(ledger["ambiguous_settled_aud"])):
        raise ValueError("Conservative ledger components do not reconcile")


def render(report):
    validate(report)
    ledger = report["ledger_costs_aud"]
    execution = report["agent_execution"]
    confirmed = ledger["confirmed_usage_aud"]
    conservative = ledger["worst_case_aud"]
    overstatement = ledger["misclassification_overstatement_aud"]
    rows = []
    for tier in ("cheap", "strong"):
        item = execution[tier]
        rows.append(
            f"| {tier} | `{item['model']}` | {item['metered_provider_responses']} | "
            f"{item['prompt_tokens']:,} | {item['completion_tokens']:,} | "
            f"{aud(float(item['confirmed_microaud']) / 1_000_000)} | "
            f"{float(item['confirmed_cost_per_case_aud']):.10f} |"
        )
    return f"""# Cost model

Generated from the durable gateway SQLite ledger on 13 September 2026. The committed Phase 7 result carries the exact public ledger summary so CI can reproduce this document without publishing the private cache or call log. Rates are pinned Australia East Azure retail estimates in AUD; this is not an invoice reconciliation.

| Figure | AUD | Meaning |
|---|---:|---|
| Confirmed metered spend | {confirmed} | Successful responses priced from returned token usage. |
| Conservative ledger total | {conservative} | Confirmed spend plus settlements retained at reserved maximum. |
| 429 misclassification overstatement | {overstatement} | Five historical capacity rejections settled before ADR-009; retained, not treated as metered spend. |
| Other ambiguous settlements | {ledger['ambiguous_settled_aud']} | Uncertain outcomes still charged at maximum. |
| Held reservations | {ledger['held_aud']} | Unresolved amount blocking admission. |

The confirmed total consumed {float(confirmed) / 6 * 100:.4f}% of the 6 AUD application limit and {float(confirmed) / 1 * 100:.4f}% of the 1 AUD daily limit. The conservative total consumed {float(conservative) / 6 * 100:.4f}% of the application limit. The separate 10 AUD project ceiling was not approached.

| Route | Model | Metered responses | Prompt tokens | Completion tokens | Confirmed AUD | Confirmed AUD / 72 cases |
|---|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

There were 72 cases per model arm and 69 metered responses per model because three exact duplicate prompts reused the disk cache. The per-case denominator remains 72. Reasoning tokens are included within completion tokens and are not charged twice. The cheap arm's conservative total is {aud(float(execution['cheap']['conservative_microaud']) / 1_000_000)} AUD because {aud(float(execution['cheap']['misclassification_overstatement_microaud']) / 1_000_000)} AUD of the known 429 overstatement is bound to nano reservations; the remaining historical settlement lacks a reliable model binding and appears only in the project total.

Capacity rejections with a complete `rate_limit_exceeded` response cost zero in the ledger: {execution['cheap']['capacity_rejections']} for nano and {execution['strong']['capacity_rejections']} for mini. A malformed response, connection drop or mid-stream timeout remains ambiguous and settles at maximum. Cache replay of all 144 model-arm case executions added 0 AUD.

Excluded: tax, negotiated Azure pricing, FX movement after the pin date, local CPU/electricity, downloads, storage outside the process, and unrelated subscription resources. Staff time saved, penalties avoided, customer satisfaction and ROI are unmeasured.
"""


def main(check=False, from_results=False):
    report = json.loads(RESULTS.read_text())
    if not from_results:
        ledger = Ledger(settings.state_dir / "gateway.sqlite3", settings.daily_limit,
                        settings.project_limit)
        live = {key.removesuffix("_microaud") + "_aud": str(Decimal(value) / Decimal(1_000_000))
                for key, value in ledger.cost_summary().items()}
        if live != report["ledger_costs_aud"]:
            raise ValueError("Local ledger differs from the committed evaluation snapshot")
    expected = render(report)
    if check:
        if OUTPUT.read_text() != expected:
            raise ValueError("Cost model differs from the committed ledger snapshot")
        print("PASS: cost model reproduces from the committed ledger snapshot")
    else:
        OUTPUT.write_text(expected)
        print(json.dumps(report["ledger_costs_aud"], sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--from-results", action="store_true",
                        help="Use the committed public ledger snapshot; intended for clean CI checkouts")
    args = parser.parse_args()
    main(args.check, args.from_results)
