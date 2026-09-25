from datetime import date

import pandas as pd

from app.period_research import assemble_sources, enrich_period_report


def _write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def test_assemble_sources_deduplicates_without_filling_and_records_conflicts(tmp_path):
    first = tmp_path / "first.csv"
    later = tmp_path / "later.csv"
    row1 = {"timestamp": "2026-09-01T09:15:00+05:30", "open": 100, "high": 102,
            "low": 99, "close": 101, "volume": 1, "oi": 2}
    row2 = {**row1, "timestamp": "2026-09-01T09:25:00+05:30", "open": 101,
            "high": 103, "low": 100, "close": 102}
    conflicting = {**row1, "high": 104, "close": 103}
    _write(first, [row1, row2])
    _write(later, [conflicting])

    manifest = assemble_sources([first, later], [], tmp_path / "merged")
    merged = pd.read_csv(tmp_path / "merged" / "nifty_5m.csv")

    assert len(merged) == 2
    assert merged.iloc[0].high == 104
    assert manifest["underlying"]["duplicate_timestamps"] == 1
    assert manifest["underlying"]["conflicting_duplicate_timestamps"] == 1


def test_period_report_lists_daily_strategy_and_contract_cross_product():
    trading_date = date(2026, 9, 1)
    pair_records = [{"date": str(trading_date), "option_type": kind, "itm_rank": rank,
                    "expiry": "08Sep26", "missing_intervals": 0,
                    "opening_candle_available": True,
                    "contract_day_has_candles": True,
                     "data_coverage": {"total_candles": 75}}
                    for kind in ("CE", "PE") for rank in (2, 3)]
    selection = {"trading_dates": [trading_date], "contract_eligibility": pair_records}
    result = {"metrics": {}, "events": [{"date": str(trading_date),
        "timestamp": pd.Timestamp("2026-09-01 09:30", tz="Asia/Kolkata"),
        "strategy": "LEVEL_TO_LEVEL", "option_type": "CE", "itm_rank": 2,
        "expiry": "08Sep26", "outcome": "TARGET", "points_gained_lost": 3,
        "mfe": 4, "mae": -1, "time_to_exit_minutes": 5}]}

    report = enrich_period_report(result, selection, date(2026, 4, 25), date(2026, 9, 25))

    assert report["baseline_id"] == "BASELINE-V1"
    assert report["data_coverage_status"] == "PARTIAL_DATA"
    assert len(report["daily_report"]) == 8
    assert report["daily_report"][0]["data_status"] == "AVAILABLE"
    assert report["metrics"]["total_points"] == 3
    assert len(report["trade_events"]) == 1
