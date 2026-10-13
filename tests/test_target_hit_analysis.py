import pytest

from tools.generate_target_hit_reports import (
    build_summary_rows,
    calculate_metrics,
    enrich_ekalayava_rows,
)


def _l2l(outcome, points, *, date="2026-01-05", option_type="CE", itm_rank="2"):
    return {
        "policy": "SL_4_TP_100",
        "stop_buffer_points": "4",
        "target_fraction": "1.0",
        "setup_id": f"{date}-{option_type}-{outcome}",
        "date": date,
        "month": date[:7],
        "period": "TRAIN_JAN_JUN" if date < "2026-07-01" else "VALIDATION_JUL_AUG",
        "timestamp_utc": f"{date} 04:20:00+00:00",
        "exit_timestamp": f"{date} 04:25:00+00:00" if points is not None else "",
        "option_type": option_type,
        "itm_rank": itm_rank,
        "entry_bucket": "09:15-09:59",
        "outcome": outcome,
        "points": "" if points is None else str(points),
        "source_bar_count": "75",
    }


def test_l2l_hit_metrics_keep_touch_exit_and_incomplete_path_denominators_distinct():
    rows = [
        _l2l("TARGET", 5),
        _l2l("AMBIGUOUS", None, date="2026-01-06"),
        _l2l("SL", -2, date="2026-01-07"),
        _l2l("UNRESOLVED_DATA_GAP", None, date="2026-01-08"),
        _l2l("SKIPPED_SL_ALREADY_BREACHED", None, date="2026-01-09"),
    ]

    metrics = calculate_metrics(rows, "L2L")

    assert metrics["eligible_setups"] == 5
    assert metrics["eligible_entries"] == 4
    assert metrics["complete_paths"] == 3
    assert metrics["incomplete_paths"] == 1
    assert metrics["target_touches"] == 2
    assert metrics["target_exits"] == 1
    assert metrics["ambiguous_count"] == 1
    assert metrics["unresolved_count"] == 1
    assert metrics["skipped_count"] == 1
    assert metrics["target_hit_numerator"] == 1
    assert metrics["target_hit_denominator"] == 4
    assert metrics["target_hit_rate"] == pytest.approx(0.25)
    assert metrics["target_touch_denominator"] == 3
    assert metrics["resolved_trades"] == 2
    assert metrics["gross_points"] == pytest.approx(3)


def test_ekalayava_observed_touch_is_not_counted_as_a_simulated_exit():
    observations = [
        {
            "setup_id": "obs-1", "date": "2026-01-05",
            "timestamp_utc": "2026-01-05 04:20:00+00:00",
            "symbol": "NSE-NIFTY-01Jan26-1-CE", "mfe": "12",
        },
        {
            "setup_id": "obs-2", "date": "2026-01-06",
            "timestamp_utc": "2026-01-06 04:20:00+00:00",
            "symbol": "NSE-NIFTY-01Jan26-1-PE", "mfe": "7",
        },
    ]
    policy_rows = [
        {
            "policy": "A_STRUCTURAL_TROUGH_B0_TP50", "setup_id": "policy-1",
            "date": "2026-01-05", "timestamp_utc": observations[0]["timestamp_utc"],
            "symbol": observations[0]["symbol"], "outcome": "STOP_LOSS",
            "points": "-4", "target_distance": "5", "option_type": "CE",
            "itm_rank": "2", "entry_bucket": "09:15-09:59", "period": "TRAIN_JAN_JUN",
        },
        {
            "policy": "A_STRUCTURAL_TROUGH_B0_TP50", "setup_id": "policy-2",
            "date": "2026-01-06", "timestamp_utc": observations[1]["timestamp_utc"],
            "symbol": observations[1]["symbol"], "outcome": "TARGET",
            "points": "3", "target_distance": "5", "option_type": "PE",
            "itm_rank": "3", "entry_bucket": "10:00-10:59", "period": "TRAIN_JAN_JUN",
        },
    ]
    enriched = enrich_ekalayava_rows(policy_rows, observations)

    metrics = calculate_metrics(enriched, "EKALAYAVA")

    assert metrics["target_touches"] == 2
    assert metrics["target_exits"] == 1
    assert metrics["stop_exits"] == 1
    assert metrics["target_touch_rate"] == 1
    assert metrics["target_hit_numerator"] == 1
    assert metrics["target_hit_denominator"] == 2


def test_summary_has_period_and_contract_segments_without_merging_them():
    rows = [
        _l2l("TARGET", 2, date="2026-01-05", option_type="CE", itm_rank="2"),
        _l2l("SL", -1, date="2026-07-05", option_type="PE", itm_rank="3"),
    ]

    summary = build_summary_rows(rows, [])

    train_ce = next(
        row for row in summary
        if row["period"] == "TRAIN_JAN_JUN"
        and row["segment_dimension"] == "OPTION_TYPE"
        and row["segment"] == "CE"
    )
    validation_pe = next(
        row for row in summary
        if row["period"] == "VALIDATION_JUL_AUG"
        and row["segment_dimension"] == "OPTION_TYPE"
        and row["segment"] == "PE"
    )

    assert train_ce["eligible_setups"] == 1
    assert train_ce["target_exits"] == 1
    assert validation_pe["eligible_setups"] == 1
    assert validation_pe["stop_exits"] == 1


def test_ekalayava_duplicate_policy_entry_identity_is_rejected():
    observation = {
        "setup_id": "obs", "date": "2026-01-05",
        "timestamp_utc": "2026-01-05 04:20:00+00:00",
        "symbol": "NSE-NIFTY-01Jan26-1-CE", "mfe": "10",
    }
    row = {
        "policy": "A_STRUCTURAL_TROUGH_B0_TP50", "setup_id": "same",
        "date": observation["date"], "timestamp_utc": observation["timestamp_utc"],
        "symbol": observation["symbol"], "outcome": "TARGET",
        "target_distance": "5",
    }

    with pytest.raises(ValueError, match="Duplicate Ekalayava policy/setup row"):
        enrich_ekalayava_rows([row, dict(row)], [observation])
