import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from decimal import Decimal
from threading import Barrier

import pytest
from src.gateway.ledger import BudgetError, Ledger, UnresolvedReservation
from src.gateway.llm_client import (CapacityRejected, Completion, GatewayError, LLMClient,
                                    NotSent, PIIRedactor, RedactedPrompt,
                                    classify_capacity_rejection)
from src.gateway.prices import UnknownPrice, get_price


class ReadyRedactor:
    def redact(self, prompt):
        return RedactedPrompt(prompt.replace("private-name", "CUSTOMER_1"), live_ready=True)


def fake_client(config, transport=None, recovery_run_id=None, **changes):
    cfg = replace(config, mode="live", allow_live=True, **changes)
    return LLMClient(cfg, redactor=ReadyRedactor(),
                     transport=transport or (lambda *args: Completion("LOCAL_TEST_ONLY", 20, 12, 2, 5)),
                     recovery_run_id=recovery_run_id)


def rows(client, table):
    with sqlite3.connect(client.ledger.path) as db:
        return db.execute(f"SELECT * FROM {table}").fetchall()


@pytest.mark.parametrize("daily,total,amount", [(1, 6, 1_000_001), (1, 1, 1_000_001)])
def test_refuses_insufficient_balance(tmp_path, daily, total, amount):
    ledger = Ledger(tmp_path / "ledger.db", Decimal(daily), Decimal(total))
    with pytest.raises(BudgetError, match="Insufficient"):
        ledger.reserve(amount)
    assert ledger.summary() == {"committed_microaud": 0, "held_microaud": 0}


def test_atomic_concurrent_reservations(tmp_path):
    path = tmp_path / "ledger.db"
    ledger = Ledger(path, Decimal("1"), Decimal("1"))
    barrier = Barrier(2)

    def reserve():
        other = Ledger(path, Decimal("1"), Decimal("1"))
        barrier.wait(timeout=5)
        try:
            return other.reserve(600_000)
        except BudgetError:
            return None

    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(lambda _: reserve(), range(2)))
    assert sum(r is not None for r in results) == 1
    assert ledger.summary()["held_microaud"] == 600_000


def test_cache_hit_makes_no_reservation(config, monkeypatch):
    client = fake_client(config)
    first = client.complete("private-name")
    assert len(rows(client, "reservations")) == 1

    def denied(*args):
        pytest.fail("Cache hit must not reserve or call a transport")
    monkeypatch.setattr(client.ledger, "reserve", denied)
    monkeypatch.setattr(client, "_transport", denied)
    assert client.complete("private-name") == first
    record = json.loads(rows(client, "calls")[-1][1])
    assert record["cache_hit"] and record["estimated_aud"] == "0"
    # The raw prompt is never persisted.
    assert b"private-name" not in client.ledger.path.read_bytes()


def test_unknown_price_raises_before_reservation(config):
    client = LLMClient(config)
    with pytest.raises(UnknownPrice):
        client.complete("hello", model="unpinned")
    assert rows(client, "reservations") == []


def test_dry_run_is_offline_and_does_not_poison_cache(config, monkeypatch):
    import sys
    monkeypatch.setitem(sys.modules, "openai", None)
    monkeypatch.setitem(sys.modules, "azure.identity", None)
    client = LLMClient(config, transport=lambda *a: pytest.fail("transport called"))
    assert client.complete("offline").prompt_tokens == 0
    assert rows(client, "reservations") == []
    assert rows(client, "cache") == []
    assert client.ledger.summary() == {"committed_microaud": 0, "held_microaud": 0}


def test_settlement_uses_usage_including_reasoning(config):
    client = fake_client(config)
    client.complete("hello")
    actual = get_price("gpt-5-nano").cost_microaud(20, 12, 2)
    assert client.ledger.summary() == {"committed_microaud": actual, "held_microaud": 0}
    record = json.loads(rows(client, "calls")[-1][1])
    assert record["completion_tokens"] == 12 and record["reasoning_tokens"] == 5
    assert record["estimated_aud"] == str(Decimal(actual) / 1_000_000)


def test_ambiguous_outcome_settles_at_maximum_and_run_continues(config):
    calls = []
    def transport(*args):
        calls.append(1)
        if len(calls) == 1:
            raise TimeoutError("private-provider-detail")
        return Completion("recovered", 10, 5)
    client = fake_client(config, transport, recovery_run_id="test-recovery-run")
    result = client.complete("hello", max_output_tokens=100)
    reservations = rows(client, "reservations")
    assert result.text == "recovered" and [row[4] for row in reservations] == ["committed", "committed"]
    assert reservations[0][3] == reservations[0][2]
    costs = client.ledger.cost_summary()
    assert costs["ambiguous_settled_microaud"] == reservations[0][2]
    assert costs["worst_case_microaud"] > costs["confirmed_usage_microaud"]
    logs = [json.loads(row[1]) for row in rows(client, "calls")]
    assert any(row.get("reason") == "ambiguous_settlement" for row in logs)
    assert all("private-provider-detail" not in json.dumps(row) for row in logs)


def test_well_formed_429_releases_retries_and_malformed_body_does_not(config):
    class Response:
        headers = {"retry-after": "0"}
    class Error:
        status_code = 429
        body = {"code": "rate_limit_exceeded", "message": "capacity"}
        response = Response()
    assert classify_capacity_rejection(Error()) == (True, 0.0)
    Error.body = {"code": "unknown", "message": "capacity"}
    assert classify_capacity_rejection(Error()) == (False, None)

    attempts = []
    def transport(*args):
        attempts.append(1)
        if len(attempts) < 3:
            raise CapacityRejected(0)
        return Completion("accepted", 10, 5)
    client = fake_client(config, transport, recovery_run_id="capacity-run")
    assert client.complete("hello").text == "accepted"
    reservations = rows(client, "reservations")
    assert [row[4] for row in reservations] == ["released", "released", "committed"]
    logs = [json.loads(row[1]) for row in rows(client, "calls")]
    assert sum(row.get("status") == "capacity_rejected" for row in logs) == 2
    assert client.ledger.cost_summary()["misclassification_overstatement_microaud"] == 0


def test_crash_after_reservation_blocks_new_client(config):
    client = fake_client(config)
    client.ledger.reserve(100)
    with pytest.raises(UnresolvedReservation):
        fake_client(config).complete("restart")


def test_retry_releases_only_confirmed_not_sent_and_reserves_again(config):
    calls = []
    def transport(*args):
        calls.append(1)
        if len(calls) == 1:
            raise NotSent("not dispatched")
        return Completion("ok", 10, 5)
    client = fake_client(config, transport, max_retries=1)
    client.complete("retry")
    attempts = rows(client, "reservations")
    assert [r[4] for r in attempts] == ["released", "committed"]
    assert attempts[0][0] != attempts[1][0]
    assert client.ledger.summary()["held_microaud"] == 0


def test_cached_mode_miss_and_parameter_change_never_call(config):
    live = fake_client(config)
    live.complete("seed", max_output_tokens=100)
    cached = LLMClient(replace(live.config, mode="cached"), redactor=ReadyRedactor(),
                       transport=lambda *a: pytest.fail("cached mode called transport"))
    assert cached.complete("seed", max_output_tokens=100).text == "LOCAL_TEST_ONLY"
    with pytest.raises(GatewayError, match="Cache miss"):
        cached.complete("seed", max_output_tokens=101)
    assert len(rows(live, "reservations")) == 1


def test_strong_requires_reason_and_logs_it(config):
    client = fake_client(config)
    with pytest.raises(GatewayError, match="reason"):
        client.complete("hello", tier="strong")
    client.complete("hello", tier="strong", escalation_reason="completeness_critique")
    log = json.loads(rows(client, "calls")[-1][1])
    assert log["model"] == "gpt-5-mini"
    assert log["escalation_reason"] == "completeness_critique"


def test_unstructured_prompt_and_disabled_live_flag_refuse_network(config):
    with pytest.raises(GatewayError, match="enable flag"):
        LLMClient(replace(config, mode="live", allow_live=False))
    client = LLMClient(replace(config, mode="live", allow_live=True),
                       transport=lambda *a: pytest.fail("PII boundary allowed unstructured live input"))
    with pytest.raises(GatewayError, match="PII boundary"):
        client.complete("private-name")
    assert rows(client, "reservations") == []


def test_active_pii_boundary_redacts_identity_and_requires_schema(config):
    values = ("Jane Example", "12 Sample Street", "ABC1234567")
    payload = json.dumps({
        "schema": PIIRedactor.SCHEMA,
        "task": "Summarise Jane Example at 12 Sample Street with NMI: ABC1234567",
        "fixed_control_status": "insufficient_evidence",
        "obligation_id": "OIQ-024", "clause_reference": "166(2)(b)",
        "source_excerpt": "public source", "timeline": [], "evidence_gaps": ["event"],
    })
    safe = PIIRedactor(values, allow_structured_live=True).redact(payload)
    assert safe.live_ready
    assert all(value.lower() not in safe.text.lower() for value in values)
    seen = []
    client = LLMClient(
        replace(config, mode="live", allow_live=True),
        redactor=PIIRedactor(values, allow_structured_live=True),
        transport=lambda price, text, cap, tier: (
            seen.append(text) or Completion("redacted boundary test", 20, 10)))
    client.complete(payload, workload="evidence")
    assert len(seen) == 1 and all(value.lower() not in seen[0].lower() for value in values)
    assert PIIRedactor(values).redact(payload).live_ready is False
    assert PIIRedactor(values).redact("Jane Example").live_ready is False


@pytest.mark.parametrize("response", [Completion("bad", 10, 1025), Completion("bad", 10, 5, 0, 6)])
def test_invalid_usage_halts_and_keeps_money_reserved(config, response):
    client = fake_client(config, lambda *a: response)
    with pytest.raises(UnresolvedReservation):
        client.complete("hello")
    assert client.ledger.summary()["held_microaud"] > 0


def test_lifetime_limit_survives_day_change(config, monkeypatch):
    from datetime import datetime, timezone
    import src.gateway.ledger as module
    ledger = Ledger(config.state_dir / "limits.db", Decimal("1"), Decimal("1"))
    identifier = ledger.reserve(900_000)
    ledger.finish(identifier, 900_000, "a", {}, {})
    monkeypatch.setattr(module, "utc_now", lambda: datetime(2030, 1, 1, tzinfo=timezone.utc))
    with pytest.raises(BudgetError, match="Insufficient"):
        ledger.reserve(200_000)


def test_input_and_output_bounds_reject_before_reservation(config):
    client = fake_client(config)
    for prompt, cap in [("x" * 4096, 10), ("x", 0), ("x", 4097)]:
        with pytest.raises(GatewayError):
            client.complete(prompt, max_output_tokens=cap)
    assert rows(client, "reservations") == []


def test_pinned_rates_match_published_meter_units():
    from pathlib import Path
    snapshot = json.loads((Path(__file__).parents[1] / "docs/azure-price-snapshot.json").read_text())
    meters = {row["skuName"]: row for row in snapshot["items"]}
    selections = {
        "gpt-5-nano": ("GPT 5 Nano Inpt Glbl", "GPT 5 Nano outpt Glbl", "GPT 5 Nano cchd Inpt Glbl"),
        "gpt-5-mini": ("GPT 5 Mini Inpt Glbl", "GPT 5 Mini outpt Glbl", "GPT 5 Mini cchd Inpt Glbl"),
    }
    for model, names in selections.items():
        price = get_price(model)
        assert all(meters[name]["currencyCode"] == price.currency for name in names)
        assert all(meters[name]["unitOfMeasure"] == "1M" for name in names)
        rates = tuple(Decimal(str(meters[name]["retailPrice"])) for name in names)
        assert rates == (price.input_per_million, price.output_per_million, price.cached_input_per_million)
    embedding = meters["text-embedding-3-small-glbl"]
    assert embedding["unitOfMeasure"] == "1K" and embedding["retailPrice"] == 0
    with pytest.raises(UnknownPrice):
        get_price("text-embedding-3-small")
