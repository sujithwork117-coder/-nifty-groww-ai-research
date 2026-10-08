from datetime import datetime
from types import SimpleNamespace

import pandas as pd
import pytest

from app.candle_builder import FiveMinuteCandleBuilder
from app.live_listener import completed_5m_candle, market_open_now, paper_signal, select_live_contracts
from app.paper_engine import PaperContractEngine


CONFIG = SimpleNamespace(execution_allowed=False, paper_only=True, kill_switch=False,
                         level_sl_points=4, level_entry_start="09:15", level_entry_end="11:00",
                         ek_start="09:15", ek_end="15:15", model_version="test")
CONTRACT = {"symbol": "NSE-NIFTY-01Sep26-9950-CE", "expiry": "2026-09-01",
            "strike": 9950, "option_type": "CE", "itm_rank": 2}


def candle(at, open_, high, low, close, **extra):
    return {"timestamp": pd.Timestamp(f"2026-09-01 {at}", tz="Asia/Kolkata"),
            "open": open_, "high": high, "low": low, "close": close,
            "completed": True, **extra}


def test_candle_is_not_returned_until_its_bucket_has_closed():
    ticks = [
        {"timestamp": "2026-09-01T09:15:01+05:30", "price": 100},
        {"timestamp": "2026-09-01T09:17:00+05:30", "price": 98},
        {"timestamp": "2026-09-01T09:19:59+05:30", "price": 102},
    ]
    assert completed_5m_candle(ticks, as_of="2026-09-01T09:19:59+05:30") is None
    result = completed_5m_candle(ticks, as_of="2026-09-01T09:20:00+05:30")
    assert result["timestamp"] == pd.Timestamp("2026-09-01 09:15", tz="Asia/Kolkata")
    assert result["close_time"] == pd.Timestamp("2026-09-01 09:20", tz="Asia/Kolkata")
    assert (result["open"], result["high"], result["low"], result["close"]) == (100, 102, 98, 102)
    assert result["completed"] is True
    with pytest.raises(ValueError, match="proven completed"):
        PaperContractEngine(CONTRACT, CONFIG).process_candle({k:v for k,v in result.items() if k!="completed"})


def test_builder_emits_once_reports_gaps_and_rejects_late_or_duplicate_ticks():
    builder = FiveMinuteCandleBuilder()
    ticks = [
        {"timestamp": "2026-09-01T09:15:02+05:30", "price": 100},
        {"timestamp": "2026-09-01T09:15:02+05:30", "price": 100},
        {"timestamp": "2026-09-01T09:20:02+05:30", "price": 102},
        {"timestamp": "2026-09-01T09:30:02+05:30", "price": 105},
    ]
    assert builder.add_ticks(ticks) == 3
    bars = builder.finalize("2026-09-01T09:35:00+05:30")
    assert [bar["missing_intervals_before"] for bar in bars] == [0, 0, 1]
    assert builder.finalize("2026-09-01T09:40:00+05:30") == []
    assert builder.add_tick("2026-09-01T09:30:02+05:30", 106) is False
    assert builder.duplicate_ticks == 1
    assert builder.late_ticks == 1

    restored = FiveMinuteCandleBuilder().restore(builder.snapshot())
    assert restored.finalize("2026-09-01T09:40:00+05:30") == []
    assert restored.add_tick("2026-09-01T09:30:02+05:30", 106) is False

    reordered = FiveMinuteCandleBuilder()
    reordered.add_tick("2026-09-01T09:16:00+05:30", 102)
    reordered.add_tick("2026-09-01T09:15:30+05:30", 100)
    bar = reordered.finalize("2026-09-01T09:20:00+05:30")[0]
    assert reordered.out_of_order_ticks == 1
    assert (bar["open"], bar["close"]) == (100, 102)
    assert reordered.add_tick("2026-09-01T15:30:00+05:30", 110) is False
    with pytest.raises(ValueError, match="finite positive"):
        reordered.add_tick("2026-09-01T09:20:10+05:30", float("nan"))


def test_readonly_signal_facade_requires_engine_state_and_closed_candle():
    engine = PaperContractEngine(CONTRACT, CONFIG)
    assert paper_signal(candle("09:15", 105, 110, 100, 104), engine) == []
    with pytest.raises(ValueError, match="finalized"):
        paper_signal({**candle("09:20", 102, 103, 99, 101), "completed": False}, engine)


def test_l2l_requires_red_break_then_first_subsequent_green_and_deduplicates():
    engine = PaperContractEngine(CONTRACT, CONFIG)
    assert engine.process_candle(candle("09:15", 105, 110, 100, 104)) == []
    # A green candle before the red break cannot trigger an entry.
    assert engine.process_candle(candle("09:20", 100, 104, 99, 103)) == []
    assert engine.process_candle(candle("09:25", 103, 104, 98, 101)) == []
    events = engine.process_candle(candle("09:30", 100, 104, 99, 102))
    signals = [event for event in events if event["event_type"] == "SIGNAL"]
    assert len(signals) == 1
    assert signals[0]["red_break_timestamp"] == "2026-09-01T09:25:00+05:30"
    assert signals[0]["first_green_timestamp"] == "2026-09-01T09:30:00+05:30"
    assert signals[0]["entry"] == 102
    assert signals[0]["sl"] == 96
    assert signals[0]["target"] == 110
    assert engine.process_candle(candle("09:30", 100, 104, 99, 102)) == []
    engine.process_candle(candle("09:35", 102, 110, 101, 109))
    assert engine.state["l2l"]["trade"]["status"] == "TARGET"
    assert engine.state["l2l"]["trade"]["exit_price"] == 110
    assert engine.state["l2l"]["daily_entry_used"] is True


def test_l2l_marks_sl_ambiguous_and_entry_already_breached_without_fake_exit():
    def prepared():
        engine = PaperContractEngine(CONTRACT, CONFIG)
        engine.process_candle(candle("09:15", 105, 110, 100, 104))
        engine.process_candle(candle("09:20", 102, 103, 99, 101))
        engine.process_candle(candle("09:25", 100, 103, 98, 102))
        return engine

    stopped = prepared()
    stopped.process_candle(candle("09:30", 100, 105, 95, 101))
    assert stopped.state["l2l"]["trade"]["status"] == "SL"

    ambiguous = prepared()
    ambiguous.process_candle(candle("09:30", 100, 110, 95, 102))
    assert ambiguous.state["l2l"]["trade"]["status"] == "AMBIGUOUS"
    assert ambiguous.state["l2l"]["trade"]["exit_price"] is None

    skipped = PaperContractEngine(CONTRACT, CONFIG)
    skipped.process_candle(candle("09:15", 105, 110, 100, 104))
    skipped.process_candle(candle("09:20", 100, 103, 95, 95))
    events = skipped.process_candle(candle("09:25", 89, 93, 89, 90))
    signal = next(event for event in events if event["event_type"] == "SIGNAL")
    assert signal["status"] == "SKIPPED_SL_ALREADY_BREACHED"
    assert skipped.state["l2l"]["trade"] is None


def test_missing_candle_invalidates_unentered_setup_and_out_of_order_fails_closed():
    engine = PaperContractEngine(CONTRACT, CONFIG)
    engine.process_candle(candle("09:15", 105, 110, 100, 104))
    engine.process_candle(candle("09:20", 102, 103, 99, 101))
    engine.process_candle(candle("09:30", 100, 104, 99, 102))
    assert engine.state["entries_disabled"] is True
    assert engine.state["l2l"]["phase"] == "INVALIDATED_BY_DATA_GAP"
    assert not [event for event in engine.state.values() if isinstance(event, dict) and event.get("event_type") == "SIGNAL"]
    with pytest.raises(ValueError, match="Out-of-order"):
        engine.process_candle(candle("09:25", 100, 102, 99, 101))


def test_l2l_does_not_enter_after_1100_and_keeps_end_of_session_open_unrealized():
    late = PaperContractEngine(CONTRACT, CONFIG)
    bars = pd.date_range("2026-09-01 09:15", "2026-09-01 11:05", freq="5min", tz="Asia/Kolkata")
    for stamp in bars:
        at = stamp.strftime("%H:%M")
        if at == "09:15": values = (105, 110, 100, 104)
        elif at == "10:55": values = (102, 103, 99, 101)
        elif at == "11:05": values = (100, 104, 99, 102)
        else: values = (102, 104, 101, 102)
        late.process_candle({"timestamp": stamp, "open": values[0], "high": values[1],
                             "low": values[2], "close": values[3], "completed": True})
    assert late.state["l2l"]["signal"] is None

    open_trade = PaperContractEngine(CONTRACT, CONFIG)
    open_trade.process_candle(candle("09:15", 105, 110, 100, 104))
    open_trade.process_candle(candle("09:20", 102, 103, 99, 101))
    open_trade.process_candle(candle("09:25", 100, 106, 99, 105))
    for stamp in pd.date_range("2026-09-01 09:30", "2026-09-01 15:25", freq="5min", tz="Asia/Kolkata"):
        open_trade.process_candle({"timestamp": stamp, "open": 105, "high": 109,
                                   "low": 97, "close": 105, "completed": True})
    trade = open_trade.state["l2l"]["trade"]
    assert trade["status"] == "OPEN_AT_SESSION_END"
    assert trade["exit_timestamp"] is None
    assert trade.get("exit_price") is None


def test_ekalayava_entry_is_causal_and_keeps_structural_candidate_observational():
    engine = PaperContractEngine(CONTRACT, CONFIG)
    engine.process_candle(candle("09:15", 103, 110, 100, 102))
    engine.process_candle(candle("09:20", 102, 103, 99, 100))  # breakdown
    engine.process_candle(candle("09:25", 100, 104, 99, 103))
    assert engine.state["ekalayava"]["swing_high"] is None
    engine.process_candle(candle("09:30", 103, 105, 102, 104))  # causal swing high
    assert engine.state["ekalayava"]["swing_high"] == 105
    events = engine.process_candle(candle("09:35", 104, 106, 98, 105.5))  # breakout
    signal = next(event for event in events if event["strategy"] == "EKALAYAVA" and event["event_type"] == "SIGNAL")
    assert signal["entry"] == 105.5
    assert signal["target"] == 110
    assert signal["candidate_sl"] == 98
    assert signal["candidate_sl_status"] == "OBSERVATION_ONLY_UNAPPROVED"
    assert signal["realized_pnl"] is None

    updates = engine.process_candle(candle("09:40", 105, 111, 97, 108))
    assert any(event["event_type"] == "OBSERVATION_UPDATE" for event in updates)
    trade = engine.state["ekalayava"]["trade"]
    assert trade["status"] == "UNRESOLVED"
    assert trade["target_touch_timestamp"] == "2026-09-01T09:40:00+05:30"
    assert trade["structural_low_revisited"] is True
    assert trade["breakout_candle_low_revisited"] is True
    assert trade["target_and_candidate_low_same_candle"] is True


def test_engine_restart_persists_state_and_journal_is_idempotent(tmp_path):
    journal = tmp_path / "paper.jsonl"
    state = tmp_path / "state.json"
    engine = PaperContractEngine(CONTRACT, CONFIG, journal, state)
    engine.process_candle(candle("09:15", 105, 110, 100, 104))
    engine.process_candle(candle("09:20", 102, 103, 99, 101))
    entry = candle("09:25", 100, 104, 99, 102)
    engine.process_candle(entry)
    restored = PaperContractEngine(CONTRACT, CONFIG, journal, state)
    assert restored.process_candle(entry) == []
    restored.process_candle(candle("09:30", 103, 110, 102, 109))
    rows = [line for line in journal.read_text().splitlines() if line]
    ids = [__import__("json").loads(line)["record_id"] for line in rows]
    assert len(ids) == len(set(ids))
    assert restored.state["l2l"]["trade"]["status"] == "TARGET"

    changed = SimpleNamespace(**{**CONFIG.__dict__, "level_sl_points": 3})
    with pytest.raises(ValueError, match="strategy parameters"):
        PaperContractEngine(CONTRACT, changed, journal, state)


def test_live_contract_selection_requires_completed_open_and_rolls_exact_expiry():
    class Groww:
        EXCHANGE_NSE = "NSE"

        def __init__(self):
            self.get_contracts_calls = []

        def get_expiries(self, **kwargs):
            return {"expiries": ["2026-09-08", "2026-09-01"]}

        def get_contracts(self, **kwargs):
            self.get_contracts_calls.append(kwargs)
            return {"contracts": [
                f"NSE-NIFTY-01Sep26-{strike}-{kind}"
                for strike in (9900, 9950, 10000, 10050, 10100, 10150)
                for kind in ("CE", "PE")
            ]}

    groww = Groww()
    opening = candle("09:15", 10020, 10040, 10000, 10030)
    with pytest.raises(ValueError, match="completed"):
        select_live_contracts(groww, {**opening, "completed": False})
    selected = select_live_contracts(groww, opening)
    assert selected["expiry"] == "2026-09-01"
    assert {(item["option_type"], item["itm_rank"], item["strike"]) for item in selected["contracts"]} == {
        ("CE", 2, 9950), ("CE", 3, 9900), ("PE", 2, 10100), ("PE", 3, 10150)
    }
    assert len(groww.get_contracts_calls) == 1
    assert groww.get_contracts_calls[0]["expiry_date"] == "2026-09-01"


def test_market_hours_use_ist_session_bounds():
    assert market_open_now(datetime.fromisoformat("2026-09-01T09:15:00+05:30"))
    assert not market_open_now(datetime.fromisoformat("2026-09-01T15:30:00+05:30"))
    assert not market_open_now(datetime.fromisoformat("2026-09-05T10:00:00+05:30"))
