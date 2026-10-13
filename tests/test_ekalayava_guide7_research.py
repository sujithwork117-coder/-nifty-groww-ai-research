import pandas as pd

from tools.run_ekalayava_guide7_research import (
    POLICIES,
    _metrics,
    _path_status,
    _period_2025,
    _target_for,
)


def test_guide7_candidate_set_is_fixed_and_small():
    assert len(POLICIES) == 6
    assert len({policy["policy_id"] for policy in POLICIES}) == 6
    assert {policy["target_kind"] for policy in POLICIES} == {
        "FIXED_25", "OPENING_HIGH", "RR",
    }
    assert {policy["target_parameter"] for policy in POLICIES
            if policy["target_kind"] == "RR"} == {1.0, 1.5, 2.0}


def test_2025_periods_are_chronological_and_bounded():
    assert _period_2025("2025-07-01") == "TRAIN_2025_JUL_AUG"
    assert _period_2025("2025-08-31") == "TRAIN_2025_JUL_AUG"
    assert _period_2025("2025-09-01") == "VALIDATION_2025_SEP_OCT"
    assert _period_2025("2025-10-31") == "VALIDATION_2025_SEP_OCT"
    assert _period_2025("2025-11-01") == "TEST_2025_NOV_DEC"
    assert _period_2025("2025-12-31") == "TEST_2025_NOV_DEC"
    assert _period_2025("2026-01-01") == "OUT_OF_SCOPE"


def test_target_formulas_use_fixed_entry_risk():
    fixed = next(policy for policy in POLICIES if policy["target_kind"] == "FIXED_25")
    opening = next(policy for policy in POLICIES if policy["target_kind"] == "OPENING_HIGH")
    one_r = next(policy for policy in POLICIES
                 if policy["target_kind"] == "RR" and policy["target_parameter"] == 1.0)
    assert _target_for(fixed, 100.0, 80.0, 160.0) == 125.0
    assert _target_for(opening, 100.0, 80.0, 160.0) == 160.0
    assert _target_for(one_r, 100.0, 80.0, 160.0) == 120.0
    assert _target_for(one_r, 100.0, 100.0, 160.0) == 100.0


def test_path_status_requires_exact_full_session_for_complete():
    stamps = pd.date_range(
        "2025-07-01 09:15", "2025-07-01 15:25", freq="5min",
        tz="Asia/Kolkata",
    )
    bars = [{"timestamp": stamp.to_pydatetime()} for stamp in stamps]
    assert _path_status(bars, "2025-07-01") == "COMPLETE_POST_ENTRY_PATH"
    assert _path_status(bars[:-1], "2025-07-01") == "PARTIAL_POST_ENTRY_PATH"
    assert _path_status([], "2025-07-01") == "NO_USABLE_POST_ENTRY_PATH"


def test_metrics_orders_rows_with_entry_timestamp_when_exit_is_missing():
    metrics = _metrics([
        {
            "date": "2025-07-01", "entry_timestamp_utc": "2025-07-01T04:20:00+00:00",
            "outcome": "STOP_LOSS", "points": -10.0,
        },
        {
            "date": "2025-07-01", "entry_timestamp_utc": "2025-07-01T04:15:00+00:00",
            "outcome": "TARGET", "points": 20.0,
        },
    ])
    assert metrics["gross_points"] == 10.0
    assert metrics["longest_losing_streak"] == 1
