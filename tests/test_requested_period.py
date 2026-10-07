from pathlib import Path

import pandas as pd

from app.weekly_experiment import _regular_session_candles, select_requested_period


def _write_candles(path, dates):
    rows = []
    for value in dates:
        timestamp = f"{value} 09:15:00+05:30"
        rows.append({"timestamp": timestamp, "open": 10, "high": 11, "low": 9,
                     "close": 10, "volume": 1, "oi": 1})
    pd.DataFrame(rows).to_csv(path, index=False)


def _catalog():
    return {"2026-09-30": [
        "NSE-NIFTY-30Sep26-8-CE", "NSE-NIFTY-30Sep26-8.5-CE", "NSE-NIFTY-30Sep26-9-CE",
        "NSE-NIFTY-30Sep26-9.5-CE", "NSE-NIFTY-30Sep26-10.5-PE", "NSE-NIFTY-30Sep26-11-PE",
        "NSE-NIFTY-30Sep26-11.5-PE", "NSE-NIFTY-30Sep26-12-PE",
    ]}


def test_selector_keeps_requested_period_and_selects_itm_2_and_3(tmp_path):
    underlying = tmp_path / "nifty.csv"
    option_dir = tmp_path / "options"
    option_dir.mkdir()
    dates = ["2026-07-23", "2026-07-24", "2026-09-23"]
    _write_candles(underlying, dates)
    for name in ("NSE-NIFTY-30Sep26-8-CE.csv", "NSE-NIFTY-30Sep26-8.5-CE.csv",
                 "NSE-NIFTY-30Sep26-9-CE.csv", "NSE-NIFTY-30Sep26-9.5-CE.csv",
                 "NSE-NIFTY-30Sep26-10.5-PE.csv", "NSE-NIFTY-30Sep26-11-PE.csv",
                 "NSE-NIFTY-30Sep26-11.5-PE.csv", "NSE-NIFTY-30Sep26-12-PE.csv"):
        _write_candles(option_dir / name, dates)

    selection = select_requested_period(underlying, option_dir, contract_catalog=_catalog())

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

    selection = select_requested_period(underlying, option_dir, contract_catalog=_catalog())

    assert {path.stem for path in selection["eligible_by_date"][pd.Timestamp(dates[0]).date()]} == {
        "NSE-NIFTY-30Sep26-9-CE"
    }
    assert selection["eligible_by_date"][pd.Timestamp(dates[1]).date()] == []
    assert sum(len(paths) for paths in selection["eligible_by_date"].values()) == 1


def test_selector_requires_the_canonical_0915_underlying_opening_candle(tmp_path):
    underlying = tmp_path / "nifty.csv"
    option_dir = tmp_path / "options"
    option_dir.mkdir()
    pd.DataFrame([
        {"timestamp": "2026-09-01 09:00:00+05:30", "open": 10, "high": 11, "low": 9, "close": 10, "volume": 1, "oi": 1},
        {"timestamp": "2026-09-01 09:05:00+05:30", "open": 10, "high": 11, "low": 9, "close": 10, "volume": 1, "oi": 1},
    ]).to_csv(underlying, index=False)
    for name in ("NSE-NIFTY-30Sep26-8-CE.csv", "NSE-NIFTY-30Sep26-8.5-CE.csv",
                 "NSE-NIFTY-30Sep26-9-CE.csv", "NSE-NIFTY-30Sep26-9.5-CE.csv",
                 "NSE-NIFTY-30Sep26-10.5-PE.csv", "NSE-NIFTY-30Sep26-11-PE.csv",
                 "NSE-NIFTY-30Sep26-11.5-PE.csv", "NSE-NIFTY-30Sep26-12-PE.csv"):
        _write_candles(option_dir / name, ["2026-09-01"])

    selection = select_requested_period(underlying, option_dir, contract_catalog=_catalog())

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
                 "NSE-NIFTY-30Sep26-8.5-CE.csv", "NSE-NIFTY-30Sep26-8-CE.csv",
                 "NSE-NIFTY-30Sep26-10.5-PE.csv", "NSE-NIFTY-30Sep26-11-PE.csv",
                 "NSE-NIFTY-30Sep26-11.5-PE.csv", "NSE-NIFTY-30Sep26-12-PE.csv"):
        _write_candles(option_dir / name, ["2026-09-01"])

    selection = select_requested_period(underlying, option_dir, contract_catalog=_catalog())
    eligibility = selection["contract_eligibility"]

    assert selection["underlying_open"] == 10
    assert {(item["option_type"], item["itm_rank"], item["strike"]) for item in eligibility} == {
        ("CE", 2, 9.0), ("CE", 3, 8.5), ("PE", 2, 10.5), ("PE", 3, 11.0)
    }


def test_missing_itm2_data_does_not_shift_itm3_into_the_itm2_rank(tmp_path):
    underlying = tmp_path / "nifty.csv"
    option_dir = tmp_path / "options"
    option_dir.mkdir()
    _write_candles(underlying, ["2026-09-01"])
    _write_candles(option_dir / "NSE-NIFTY-30Sep26-9.5-CE.csv", ["2026-09-01"])
    _write_candles(option_dir / "NSE-NIFTY-30Sep26-9-CE.csv", ["2026-08-31"])
    _write_candles(option_dir / "NSE-NIFTY-30Sep26-8.5-CE.csv", ["2026-09-01"])

    selection = select_requested_period(underlying, option_dir, contract_catalog=_catalog())
    day = pd.Timestamp("2026-09-01").date()

    assert {path.stem for path in selection["eligible_by_date"][day]} == {"NSE-NIFTY-30Sep26-8.5-CE"}
    assert selection["contract_coverage_by_date"][day]["present"] == [
        {"option_type": "CE", "itm_rank": 3}
    ]
    ce2 = next(item for item in selection["contract_eligibility"]
               if item["date"] == str(day) and item["option_type"] == "CE" and item["itm_rank"] == 2)
    assert ce2["symbol"] == "NSE-NIFTY-30Sep26-9-CE"
    assert not ce2["contract_day_has_candles"]
    assert {tuple((item["option_type"], item["itm_rank"]))
            for item in selection["contract_coverage_by_date"][day]["missing"]} == {
        ("CE", 2), ("PE", 2), ("PE", 3)
    }


def test_selector_requires_authoritative_contract_catalog(tmp_path):
    underlying = tmp_path / "nifty.csv"
    option_dir = tmp_path / "options"
    option_dir.mkdir()
    _write_candles(underlying, ["2026-09-01"])

    import pytest
    with pytest.raises(ValueError, match="authoritative expiry-to-contract catalog"):
        select_requested_period(underlying, option_dir)


def test_sparse_groww_catalog_does_not_substitute_farther_strikes(tmp_path):
    underlying = tmp_path / "nifty.csv"
    option_dir = tmp_path / "options"
    option_dir.mkdir()
    _write_candles(underlying, ["2026-09-01"])
    sparse = {"2026-09-30": [
        "NSE-NIFTY-30Sep26-9.5-CE", "NSE-NIFTY-30Sep26-9-CE", "NSE-NIFTY-30Sep26-8-CE",
        "NSE-NIFTY-30Sep26-10.5-PE", "NSE-NIFTY-30Sep26-11-PE", "NSE-NIFTY-30Sep26-12-PE",
    ]}

    selection = select_requested_period(underlying, option_dir, contract_catalog=sparse)
    by_pair = {(item["option_type"], item["itm_rank"]): item
               for item in selection["contract_eligibility"]}

    assert by_pair[("CE", 2)]["strike"] == 9
    assert by_pair[("CE", 3)]["symbol"] is None  # strike 8 is ITM4, not ITM3
    assert by_pair[("PE", 2)]["strike"] == 10.5
    assert by_pair[("PE", 3)]["strike"] == 11


def test_backtest_input_excludes_premarket_and_after_session_candles():
    frame = pd.DataFrame({
        "timestamp": pd.to_datetime([
            "2026-09-01 09:10:00+05:30", "2026-09-01 09:15:00+05:30",
            "2026-09-01 15:25:00+05:30", "2026-09-01 15:30:00+05:30",
        ], utc=True),
        "open": [1, 2, 3, 4], "high": [2, 3, 4, 5],
        "low": [0, 1, 2, 3], "close": [1, 2, 3, 4],
        "volume": [1, 1, 1, 1], "oi": [1, 1, 1, 1],
    })

    actual = _regular_session_candles(frame)

    assert pd.to_datetime(actual.timestamp, utc=True).dt.tz_convert("Asia/Kolkata").dt.strftime("%H:%M").tolist() == [
        "09:15", "15:25"
    ]


def test_expiry_rolls_on_expiry_date_and_never_uses_expired_chain(tmp_path):
    underlying = tmp_path / "nifty.csv"
    option_dir = tmp_path / "options"
    option_dir.mkdir()
    _write_candles(underlying, ["2026-07-07", "2026-07-08"])
    def chain(expiry):
        day = pd.Timestamp(expiry).strftime("%d%b%y")
        return [f"NSE-NIFTY-{day}-{strike}-{kind}"
                for kind, strikes in (("CE", (9.5, 9, 8)), ("PE", (10.5, 11, 12)))
                for strike in strikes]
    catalog = {"2026-07-07": chain("2026-07-07"), "2026-07-14": chain("2026-07-14")}

    selection = select_requested_period(underlying, option_dir, start=pd.Timestamp("2026-07-07").date(),
        end=pd.Timestamp("2026-07-08").date(), contract_catalog=catalog)
    by_date = {}
    for item in selection["contract_eligibility"]:
        by_date.setdefault(item["date"], set()).add(item["expiry"])
        if item["symbol"]:
            assert item["symbol"].startswith("NSE-NIFTY-" + pd.Timestamp(item["expiry"]).strftime("%d%b%y"))

    assert by_date == {"2026-07-07": {"2026-07-07"}, "2026-07-08": {"2026-07-14"}}
    # Missing strikes in the sparse expiry catalog remain explicitly unavailable.
    missing = [item for item in selection["contract_eligibility"] if item["symbol"] is None]
    assert {(item["date"], item["option_type"], item["itm_rank"]) for item in missing} == {
        ("2026-07-07", "CE", 3), ("2026-07-08", "CE", 3),
    }
