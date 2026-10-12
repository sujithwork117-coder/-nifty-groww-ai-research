from datetime import datetime, timedelta, timezone

from app.research_ekalayava_exits import simulate_ekalayava_exit


T0 = datetime(2026, 1, 1, 4, 20, tzinfo=timezone.utc)
LAST = T0 + timedelta(minutes=10)


def bar(minutes, *, open_=100, high=102, low=99, close=101):
    return {"timestamp": T0 + timedelta(minutes=minutes), "open": open_,
            "high": high, "low": low, "close": close}


def simulate(bars, **kwargs):
    return simulate_ekalayava_exit(
        [bar(0), *bars], entry_timestamp=T0, entry=100, initial_stop=95,
        target=110, expected_last_timestamp=LAST, **kwargs)


def test_target_resolves_before_later_stop():
    result = simulate([bar(5, high=111, low=98), bar(10, high=105, low=90)])
    assert result["outcome"] == "TARGET"
    assert result["points"] == 10


def test_same_bar_stop_and_target_is_ambiguous():
    result = simulate([bar(5, high=111, low=94), bar(10)])
    assert result["outcome"] == "AMBIGUOUS"
    assert result["points"] is None


def test_gap_through_stop_fills_at_open():
    result = simulate([bar(5, open_=92, high=103, low=90, close=95), bar(10)])
    assert result["outcome"] == "STOP_LOSS"
    assert result["exit_price"] == 92
    assert result["reason"] == "gap_through_stop_filled_at_open"


def test_missing_interval_is_unresolved():
    result = simulate([bar(10, high=111, low=99)])
    assert result["outcome"] == "UNRESOLVED_DATA_GAP"


def test_full_no_touch_path_exits_at_last_session_close():
    result = simulate([bar(5, close=101), bar(10, high=104, low=99, close=103)])
    assert result["outcome"] == "END_OF_SESSION"
    assert result["exit_price"] == 103
    assert result["points"] == 3


def test_trailing_update_is_active_only_after_completed_bar():
    bars = [bar(5, high=105, low=98, close=103),
            bar(10, high=105, low=97, close=102),
            bar(15, high=104, low=96, close=101),
            bar(20, open_=97, high=103, low=93, close=96)]
    result = simulate_ekalayava_exit(
        [bar(0), *bars], entry_timestamp=T0, entry=100, initial_stop=90,
        target=110, expected_last_timestamp=T0 + timedelta(minutes=20),
        trailing=True, trail_buffer=2)
    assert result["stop_updates"]
    assert result["stop_updates"][0]["timestamp"] == (T0 + timedelta(minutes=15)).isoformat()
    assert result["outcome"] == "STOP_LOSS"
    assert result["exit_timestamp"] == (T0 + timedelta(minutes=20)).isoformat()


def test_invalid_stop_at_or_above_entry_is_excluded():
    result = simulate_ekalayava_exit(
        [bar(0), bar(5), bar(10)], entry_timestamp=T0, entry=100,
        initial_stop=100, target=110, expected_last_timestamp=LAST)
    assert result["outcome"] == "EXCLUDED_INVALID_STOP"
