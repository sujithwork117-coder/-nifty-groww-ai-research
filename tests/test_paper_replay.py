import pandas as pd

from app.paper import analyze_ekalayava, backtest_level_to_level
from app.paper_replay import replay_contract_day


CONTRACT = {"symbol": "NSE-NIFTY-01Sep26-9950-CE", "expiry": "2026-09-01",
            "strike": 9950, "option_type": "CE", "itm_rank": 2}


def _frame():
    rows = [
        ("09:15", 105, 110, 100, 104),
        ("09:20", 102, 103, 99, 101),  # red breakdown
        ("09:25", 100, 104, 99, 102),  # first following green: entry
        ("09:30", 103, 110, 102, 109),  # target
        ("09:35", 109, 150, 108, 149),  # later data must not affect resolved trade
    ]
    return pd.DataFrame([{"timestamp": pd.Timestamp(f"2026-09-01 {t}", tz="Asia/Kolkata"),
                          "open": o, "high": h, "low": l, "close": c,
                          "volume": 1, "oi": 1} for t, o, h, l, c in rows])


def test_candle_by_candle_replay_matches_canonical_l2l_entry_and_exit():
    candles = _frame()
    expected = backtest_level_to_level(candles, CONTRACT)
    replay = replay_contract_day(candles, CONTRACT)
    signals = [event for event in replay["events"]
               if event["strategy"] == "LEVEL_TO_LEVEL" and event["event_type"] == "SIGNAL"]

    assert len(expected) == len(signals) == 1
    assert signals[0]["timestamp"] == expected.iloc[0].timestamp.tz_convert("Asia/Kolkata").isoformat()
    assert signals[0]["entry"] == expected.iloc[0].entry
    assert signals[0]["sl"] == expected.iloc[0].sl
    assert signals[0]["target"] == expected.iloc[0].target
    assert replay["state"]["l2l"]["trade"]["status"] == expected.iloc[0].outcome == "TARGET"
    assert replay["state"]["l2l"]["trade"]["exit_timestamp"] == expected.iloc[0].exit_time.tz_convert("Asia/Kolkata").isoformat()


def test_prefix_replay_cannot_see_or_emit_signal_from_future_candles():
    candles = _frame()
    before_entry = replay_contract_day(candles.iloc[:2], CONTRACT)
    at_entry = replay_contract_day(candles.iloc[:3], CONTRACT)
    full = replay_contract_day(candles, CONTRACT)
    prefix_signals = [event for event in before_entry["events"] if event["event_type"] == "SIGNAL"]
    entry_signals = [event for event in at_entry["events"]
                     if event["strategy"] == "LEVEL_TO_LEVEL" and event["event_type"] == "SIGNAL"]
    full_l2l = [event for event in full["events"]
                if event["strategy"] == "LEVEL_TO_LEVEL" and event["event_type"] == "SIGNAL"]

    assert not [event for event in prefix_signals if event["strategy"] == "LEVEL_TO_LEVEL"]
    assert len(full_l2l) == len(entry_signals) == 1
    assert full_l2l[0]["timestamp"] == entry_signals[0]["timestamp"]
    assert full_l2l[0]["timestamp"].endswith("09:25:00+05:30")
    assert before_entry["state"]["last_timestamp"].endswith("09:20:00+05:30")


def test_ekalayava_replay_matches_causal_entry_and_never_marks_touch_as_exit():
    rows = [
        ("09:15", 103, 110, 100, 102),
        ("09:20", 102, 103, 99, 100),
        ("09:25", 100, 104, 99, 103),
        ("09:30", 103, 105, 102, 104),
        ("09:35", 104, 106, 98, 105.5),
        ("09:40", 105, 111, 97, 108),
        ("09:45", 108, 112, 104, 110),
    ]
    candles = pd.DataFrame([{"timestamp": pd.Timestamp(f"2026-09-01 {t}", tz="Asia/Kolkata"),
                             "open": o, "high": h, "low": l, "close": c,
                             "volume": 1, "oi": 1} for t, o, h, l, c in rows])
    expected = analyze_ekalayava(candles, CONTRACT)
    replay = replay_contract_day(candles, CONTRACT)
    signals = [event for event in replay["events"]
               if event["strategy"] == "EKALAYAVA" and event["event_type"] == "SIGNAL"]
    trade = replay["state"]["ekalayava"]["trade"]

    assert len(expected) == len(signals) == 1
    assert signals[0]["timestamp"] == expected.iloc[0].timestamp.tz_convert("Asia/Kolkata").isoformat()
    assert signals[0]["entry"] == expected.iloc[0].entry
    assert signals[0]["swing_high"] == expected.iloc[0].swing_high
    assert trade["target_touch_timestamp"] == expected.iloc[0].target_touch_time.tz_convert("Asia/Kolkata").isoformat()
    assert trade["status"] == "UNRESOLVED"
    assert trade["realized_pnl"] is None
    assert signals[0]["candidate_sl_status"] == "OBSERVATION_ONLY_UNAPPROVED"
