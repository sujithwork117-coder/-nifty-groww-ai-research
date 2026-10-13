import json
from datetime import datetime, timedelta

import pytest

from app.paper_shadow import CANDIDATES, EkalayavaShadowBook


T0 = datetime.fromisoformat("2026-10-13T09:15:00+05:30")


def signal(setup_id="setup-1"):
    return {
        "event_type": "SIGNAL",
        "strategy": "EKALAYAVA",
        "event_id": setup_id,
        "setup_id": setup_id,
        "date": "2026-10-13",
        "timestamp": T0.isoformat(),
        "strategy_version": "test-v1",
        "symbol": "NSE-NIFTY-15Oct26-25000-CE",
        "expiry": "2026-10-15",
        "strike": 25000,
        "option_type": "CE",
        "itm_rank": 2,
        "entry": 100.0,
        "opening_high": 120.0,
        "structural_low_candidate": 90.0,
    }


def candle(minutes, *, open_=100, high=105, low=99, close=102, symbol=None):
    stamp = T0 + timedelta(minutes=minutes)
    return {
        "timestamp": stamp,
        "close_time": stamp + timedelta(minutes=5),
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "completed": True,
        "symbol": symbol,
    }


def test_all_seven_candidates_open_and_process_independent_exit(tmp_path):
    book = EkalayavaShadowBook(tmp_path / "shadow.json")
    assert book.observe_signal(signal())
    assert not book.observe_signal(signal())
    book.advance(candle(5, high=130, low=99, close=110))

    candidates = book.snapshot()["candidates"]
    assert len(candidates) == 7
    assert {item["candidate_id"] for item in candidates.values()} == {
        item["candidate_id"] for item in CANDIDATES
    }
    assert all(item["outcome"] == "TARGET" for item in candidates.values())
    assert all(item["points"] == item["target"] - item["entry"] for item in candidates.values())
    assert all(item["quote_timestamp"] is None and item["cost_points"] is None
               for item in candidates.values())
    assert len({item["target"] for item in candidates.values()}) > 1


def test_reused_setup_identity_with_conflicting_entry_is_rejected(tmp_path):
    book = EkalayavaShadowBook(tmp_path / "shadow.json")
    assert book.observe_signal(signal())
    conflicting = signal()
    conflicting["entry"] = 101.0

    with pytest.raises(ValueError, match="identity conflicts"):
        book.observe_signal(conflicting)


def test_trailing_update_is_not_active_until_the_next_bar_and_restart_is_idempotent(tmp_path):
    state_path = tmp_path / "shadow.json"
    journal = tmp_path / "paper_journal.jsonl"
    book = EkalayavaShadowBook(state_path, journal)
    book.observe_signal(signal())

    for bar in (
        candle(5, high=101, low=99, close=100),
        candle(10, high=101, low=98, close=100),
        candle(15, high=101, low=97, close=100),
    ):
        book.advance(bar)
    trailing = next(item for item in book.snapshot()["candidates"].values()
                    if item["candidate_id"] == "B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1")
    update = trailing["stop_updates"][0]
    assert update["source_timestamp"] == (T0 + timedelta(minutes=15)).isoformat()
    assert update["effective_from_timestamp"] == (T0 + timedelta(minutes=20)).isoformat()
    assert trailing["status"] == "OPEN"

    book.advance(candle(20, open_=96, high=98, low=94, close=95))
    state_before = book.snapshot()
    restarted = EkalayavaShadowBook(state_path, journal)
    restarted.advance(candle(20, open_=96, high=98, low=94, close=95))
    assert restarted.snapshot() == state_before
    trailing = next(item for item in restarted.snapshot()["candidates"].values()
                    if item["candidate_id"] == "B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1")
    assert trailing["outcome"] == "STOP_LOSS"
    assert trailing["exit_timestamp"] == (T0 + timedelta(minutes=20)).isoformat()
    records = [json.loads(line) for line in journal.read_text().splitlines()]
    exits = [r for r in records if r["event_type"] == "SHADOW_CANDIDATE_EXIT"]
    assert len(exits) == 1
    assert exits[0]["candidate_id"] == "B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1"
    assert len({r["record_id"] for r in records}) == len(records)


def test_same_candle_stop_and_target_is_ambiguous_and_gap_is_unresolved(tmp_path):
    book = EkalayavaShadowBook(tmp_path / "shadow.json")
    book.observe_signal(signal())
    book.advance(candle(5, high=125, low=80, close=105))
    assert {item["outcome"] for item in book.snapshot()["candidates"].values()} == {"AMBIGUOUS"}

    other = EkalayavaShadowBook(tmp_path / "gap.json")
    other.observe_signal(signal("gap-setup"))
    other.advance(candle(10, high=105, low=99, close=102))
    assert {item["outcome"] for item in other.snapshot()["candidates"].values()} == {
        "UNRESOLVED_DATA_GAP"
    }


def test_shadow_book_rejects_incomplete_or_malformed_candles(tmp_path):
    book = EkalayavaShadowBook(tmp_path / "shadow.json")
    book.observe_signal(signal())
    incomplete = candle(5)
    incomplete["completed"] = False
    try:
        book.advance(incomplete)
    except ValueError as error:
        assert "completed candle" in str(error)
    else:
        raise AssertionError("incomplete candle was accepted")

    malformed = candle(5, open_=90, low=95)
    try:
        book.advance(malformed)
    except ValueError as error:
        assert "OHLC" in str(error)
    else:
        raise AssertionError("malformed OHLC was accepted")
