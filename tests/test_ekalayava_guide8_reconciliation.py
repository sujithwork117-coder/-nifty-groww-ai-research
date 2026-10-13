from tools.run_ekalayava_guide8_reconciliation import (
    ARCHIVED_TP25,
    _candidate_counts,
    _classify_target_touch,
    _target,
)


def test_archived_tp25_is_fraction_of_opening_high_distance():
    assert _target(ARCHIVED_TP25, 100.0, 80.0, 160.0) == 115.0


def test_target_touch_classification_distinguishes_exit_and_later_touch():
    bars = [
        {"timestamp": "2025-07-01T04:25:00+00:00", "high": 109.0},
        {"timestamp": "2025-07-01T04:30:00+00:00", "high": 115.0},
    ]
    target_exit = {
        "outcome": "TARGET",
        "exit_timestamp": "2025-07-01T04:30:00+00:00",
    }
    assert _classify_target_touch(
        bars, "2025-07-01T04:20:00+00:00", 115.0,
        target_exit, "COMPLETE_POST_ENTRY_PATH",
    ) == ("TOUCHED_WHILE_OPEN_TARGET_EXIT", "2025-07-01T04:30:00+00:00")

    stop_exit = {
        "outcome": "STOP_LOSS",
        "exit_timestamp": "2025-07-01T04:25:00+00:00",
    }
    assert _classify_target_touch(
        bars, "2025-07-01T04:20:00+00:00", 115.0,
        stop_exit, "COMPLETE_POST_ENTRY_PATH",
    ) == ("TOUCHED_AFTER_EXIT", "2025-07-01T04:30:00+00:00")


def test_target_touch_on_ambiguous_exit_bar_is_not_ordered():
    bars = [{"timestamp": "2025-07-01T04:25:00+00:00", "high": 115.0}]
    assert _classify_target_touch(
        bars,
        "2025-07-01T04:20:00+00:00",
        115.0,
        {"outcome": "AMBIGUOUS", "exit_timestamp": "2025-07-01T04:25:00+00:00"},
        "COMPLETE_POST_ENTRY_PATH",
    ) == ("ORDER_AMBIGUOUS_ON_EXIT_BAR", "2025-07-01T04:25:00+00:00")


def test_incomplete_path_without_a_touch_is_not_misreported_as_no_touch():
    assert _classify_target_touch(
        [],
        "2025-07-01T04:20:00+00:00",
        115.0,
        {"outcome": "UNRESOLVED_DATA_GAP"},
        "PARTIAL_POST_ENTRY_PATH",
    ) == ("UNVERIFIABLE_INCOMPLETE_PATH", None)


def test_candidate_counts_reconcile_entries_and_simulations():
    rows = [
        {
            "simulation_attempted": True, "outcome": "TARGET", "points": 20.0,
            "date": "2025-07-01", "entry_timestamp_utc": "2025-07-01T04:20:00+00:00",
            "exit_timestamp": "2025-07-01T04:25:00+00:00", "initial_risk": 10.0,
            "target_touch_class": "TOUCHED_WHILE_OPEN_TARGET_EXIT",
        },
        {
            "simulation_attempted": True, "outcome": "UNRESOLVED_DATA_GAP",
            "points": "", "date": "2025-07-01",
            "entry_timestamp_utc": "2025-07-01T04:30:00+00:00",
            "exit_timestamp": "", "initial_risk": 10.0,
            "target_touch_class": "UNVERIFIABLE_INCOMPLETE_PATH",
        },
        {
            "simulation_attempted": False, "outcome": "UNRESOLVED_NO_EXACT_PATH",
            "points": "", "date": "2026-01-01",
            "entry_timestamp_utc": "2026-01-01T04:30:00+00:00",
            "exit_timestamp": "", "initial_risk": "",
            "target_touch_class": "UNVERIFIABLE_NO_EXACT_PATH",
        },
    ]
    counts = _candidate_counts(rows, eligible=3)
    assert counts["simulated_entries_with_exact_path"] == 2
    assert counts["unresolved_entries"] == 2
    assert counts["eligible_outcome_reconciliation_delta"] == 0
    assert counts["simulated_outcome_reconciliation_delta"] == 0
    assert counts["target_exits"] == 1
