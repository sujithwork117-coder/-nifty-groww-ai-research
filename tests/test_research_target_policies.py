from datetime import datetime, timezone

from app.research_target_policies import simulate_exit_policy, target_for_fraction


T0 = datetime(2026, 1, 1, 3, 45, tzinfo=timezone.utc)


def bar(minutes, high, low):
    stamp = T0.replace(minute=T0.minute + minutes)
    return {"timestamp": stamp, "high": high, "low": low}


def run(bars, fraction=1.0, last=None):
    return simulate_exit_policy(
        bars, entry_timestamp=T0, entry=100, stop=96, opening_high=120,
        target_fraction=fraction, session_last_timestamp=last,
    )


def test_fixed_fraction_target_is_above_entry_and_exact():
    assert target_for_fraction(100, 120, 0.75) == 115
    assert target_for_fraction(100, 120, 0.5) == 110
    assert target_for_fraction(100, 120, 0.25) == 105


def test_candidate_target_can_resolve_before_baseline_stop():
    result = run([{"timestamp": T0, "high": 102, "low": 99}, bar(5, 107, 98)], 0.25)
    assert result["status"] == "TARGET"
    assert result["exit_price"] == 105
    assert result["points"] == 5


def test_same_bar_stop_and_target_is_ambiguous():
    result = run([{"timestamp": T0, "high": 102, "low": 99}, bar(5, 106, 95)], 0.25)
    assert result["status"] == "AMBIGUOUS"
    assert result["points"] is None


def test_later_target_after_a_stop_does_not_reverse_stop_outcome():
    result = run([{"timestamp": T0, "high": 102, "low": 99}, bar(5, 103, 95),
                  bar(10, 121, 98)], 1.0)
    assert result["status"] == "SL"
    assert result["points"] == -4


def test_missing_interval_before_later_touch_makes_trade_unresolved():
    result = run([{"timestamp": T0, "high": 102, "low": 99}, bar(10, 121, 98)], 1.0)
    assert result["status"] == "UNRESOLVED_DATA_GAP"
    assert result["points"] is None


def test_missing_session_tail_is_not_forced_closed():
    result = run([{"timestamp": T0, "high": 102, "low": 99}, bar(5, 104, 98)],
                 0.25, last=bar(10, 105, 97)["timestamp"])
    assert result["status"] == "UNRESOLVED_DATA_GAP"

