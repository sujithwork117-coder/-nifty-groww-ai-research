from pathlib import Path

import pandas as pd

from app.weekly_experiment import select_requested_period


def _write_candles(path, dates):
    rows = []
    for value in dates:
        timestamp = f"{value} 09:15:00+05:30"
        rows.append({"timestamp": timestamp, "open": 10, "high": 11, "low": 9,
                     "close": 10, "volume": 1, "oi": 1})
    pd.DataFrame(rows).to_csv(path, index=False)


def test_selector_keeps_requested_period_and_selects_itm_2_and_3(tmp_path):
    underlying = tmp_path / "nifty.csv"
    option_dir = tmp_path / "options"
    option_dir.mkdir()
    dates = ["2026-07-23", "2026-07-24", "2026-09-23"]
    _write_candles(underlying, dates)
    for name in ("NSE-NIFTY-30Sep26-8-CE.csv", "NSE-NIFTY-30Sep26-9-CE.csv",
                 "NSE-NIFTY-30Sep26-9.5-CE.csv", "NSE-NIFTY-30Sep26-10.5-PE.csv",
                 "NSE-NIFTY-30Sep26-11-PE.csv", "NSE-NIFTY-30Sep26-12-PE.csv"):
        _write_candles(option_dir / name, dates)

    selection = select_requested_period(underlying, option_dir)

    assert selection["trading_dates"] == [pd.Timestamp(value).date() for value in dates]
    assert selection["start"].isoformat() == "2026-07-23"
    assert selection["end"].isoformat() == "2026-09-23"
    assert {(item["option_type"], item["itm_rank"]) for item in selection["contract_eligibility"]} == {
        ("CE", 2), ("CE", 3), ("PE", 2), ("PE", 3)
    }


def test_selector_does_not_create_missing_option_candles(tmp_path):
    underlying = tmp_path / "nifty.csv"
    option_dir = tmp_path / "options"
    option_dir.mkdir()
    dates = ["2026-07-23", "2026-07-24"]
    _write_candles(underlying, dates)
    _write_candles(option_dir / "NSE-NIFTY-30Sep26-9-CE.csv", [dates[0]])

    selection = select_requested_period(underlying, option_dir)

    assert selection["eligible_by_date"][pd.Timestamp(dates[0]).date()] == []
    assert selection["eligible_by_date"][pd.Timestamp(dates[1]).date()] == []
    assert sum(len(paths) for paths in selection["eligible_by_date"].values()) == 0


def test_selector_requires_the_canonical_0915_underlying_opening_candle(tmp_path):
    underlying = tmp_path / "nifty.csv"
    option_dir = tmp_path / "options"
    option_dir.mkdir()
    pd.DataFrame([
        {"timestamp": "2026-09-01 09:00:00+05:30", "open": 10, "high": 11, "low": 9, "close": 10, "volume": 1, "oi": 1},
        {"timestamp": "2026-09-01 09:05:00+05:30", "open": 10, "high": 11, "low": 9, "close": 10, "volume": 1, "oi": 1},
    ]).to_csv(underlying, index=False)
    for name in ("NSE-NIFTY-30Sep26-8-CE.csv", "NSE-NIFTY-30Sep26-9-CE.csv",
                 "NSE-NIFTY-30Sep26-9.5-CE.csv", "NSE-NIFTY-30Sep26-10.5-PE.csv",
                 "NSE-NIFTY-30Sep26-11-PE.csv", "NSE-NIFTY-30Sep26-12-PE.csv"):
        _write_candles(option_dir / name, ["2026-09-01"])

    selection = select_requested_period(underlying, option_dir)

    assert selection["missing_underlying_opening_dates"] == ["2026-09-01"]
    assert selection["eligible_by_date"][pd.Timestamp("2026-09-01").date()] == []


def test_contract_ranks_use_0915_price_not_earlier_source_rows(tmp_path):
    underlying = tmp_path / "nifty.csv"
    option_dir = tmp_path / "options"
    option_dir.mkdir()
    pd.DataFrame([
        {"timestamp": "2026-09-01 09:00:00+05:30", "open": 100, "high": 101, "low": 99, "close": 100, "volume": 1, "oi": 1},
        {"timestamp": "2026-09-01 09:15:00+05:30", "open": 10, "high": 11, "low": 9, "close": 10, "volume": 1, "oi": 1},
    ]).to_csv(underlying, index=False)
    for name in ("NSE-NIFTY-30Sep26-9.5-CE.csv", "NSE-NIFTY-30Sep26-9-CE.csv",
                 "NSE-NIFTY-30Sep26-8-CE.csv", "NSE-NIFTY-30Sep26-10.5-PE.csv",
                 "NSE-NIFTY-30Sep26-11-PE.csv", "NSE-NIFTY-30Sep26-12-PE.csv"):
        _write_candles(option_dir / name, ["2026-09-01"])

    selection = select_requested_period(underlying, option_dir)
    eligibility = selection["contract_eligibility"]

    assert selection["underlying_open"] == 10
    assert {(item["option_type"], item["itm_rank"], item["strike"]) for item in eligibility} == {
        ("CE", 2, 9.0), ("CE", 3, 8.0), ("PE", 2, 11.0), ("PE", 3, 12.0)
    }


def test_missing_itm2_data_does_not_shift_itm3_into_the_itm2_rank(tmp_path):
    underlying = tmp_path / "nifty.csv"
    option_dir = tmp_path / "options"
    option_dir.mkdir()
    _write_candles(underlying, ["2026-09-01"])
    _write_candles(option_dir / "NSE-NIFTY-30Sep26-9.5-CE.csv", ["2026-09-01"])
    _write_candles(option_dir / "NSE-NIFTY-30Sep26-9-CE.csv", ["2026-08-31"])
    _write_candles(option_dir / "NSE-NIFTY-30Sep26-8-CE.csv", ["2026-09-01"])

    selection = select_requested_period(underlying, option_dir)
    day = pd.Timestamp("2026-09-01").date()

    assert {path.stem for path in selection["eligible_by_date"][day]} == {
        "NSE-NIFTY-30Sep26-9-CE", "NSE-NIFTY-30Sep26-8-CE"
    }
    assert selection["contract_coverage_by_date"][day]["present"] == [
        {"option_type": "CE", "itm_rank": 3}
    ]
    assert {tuple((item["option_type"], item["itm_rank"]))
            for item in selection["contract_coverage_by_date"][day]["missing"]} == {
        ("CE", 2), ("PE", 2), ("PE", 3)
    }
