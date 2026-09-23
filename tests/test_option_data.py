from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd

from app.groww_data import GrowwRateLimitError, save_option_historical


def test_save_option_historical_keeps_contracts_separate(tmp_path):
    groww=Mock()
    groww.SEGMENT_FNO="FNO"
    candles=pd.DataFrame([{
        "timestamp":pd.Timestamp("2026-09-01 09:15",tz="Asia/Kolkata"),
        "open":100,"high":101,"low":99,"close":100.5,"volume":10,"oi":20,
    }])
    contracts=[
        {"symbol":"NSE-NIFTY-26SEP26-25000-CE","underlying":"NIFTY","expiry":"2026-09-24","strike":25000,"option_type":"CE","itm_rank":2},
        {"symbol":"NSE-NIFTY-26SEP26-25200-PE","underlying":"NIFTY","expiry":"2026-09-24","strike":25200,"option_type":"PE","itm_rank":2},
    ]
    with patch("app.groww_data.get_historical", return_value=candles):
        paths=save_option_historical(groww,contracts,datetime(2026,9,1,tzinfo=timezone.utc),datetime(2026,9,2,tzinfo=timezone.utc),tmp_path)

    assert len(paths)==2
    assert {Path(path).name for path in paths}=={
        "NSE-NIFTY-26SEP26-25000-CE.csv","NSE-NIFTY-26SEP26-25200-PE.csv",
    }
    saved=pd.read_csv(paths[0])
    assert {"underlying","expiry","strike","option_type","itm_rank"}.issubset(saved.columns)
    assert set(saved["option_type"])=={"CE"}


def test_save_option_historical_skips_file_covering_requested_period(tmp_path):
    destination = tmp_path / "NSE-NIFTY-26SEP26-25000-CE.csv"
    candles = pd.DataFrame([
        {"timestamp": "2026-09-01T09:15:00+05:30", "open": 100, "high": 101, "low": 99, "close": 100, "volume": 1, "oi": 1},
        {"timestamp": "2026-09-02T09:15:00+05:30", "open": 100, "high": 101, "low": 99, "close": 100, "volume": 1, "oi": 1},
    ])
    candles.to_csv(destination, index=False)
    contract = {"symbol": destination.stem, "option_type": "CE"}
    report = {}

    with patch("app.groww_data.get_historical") as fetch:
        save_option_historical(groww=Mock(SEGMENT_FNO="FNO"), contracts=[contract],
                               start=datetime(2026, 9, 1, tzinfo=timezone.utc),
                               end=datetime(2026, 9, 2, tzinfo=timezone.utc),
                               output_dir=tmp_path, report=report)

    fetch.assert_not_called()
    assert report["skipped"] == [contract["symbol"]]


def test_save_option_historical_stops_on_rate_limit_and_reports_contract(tmp_path):
    contract = {"symbol": "NSE-NIFTY-26SEP26-25000-CE", "option_type": "CE"}
    report = {}
    with patch("app.groww_data.get_historical", side_effect=GrowwRateLimitError("rate-limited")):
        try:
            save_option_historical(groww=Mock(SEGMENT_FNO="FNO"), contracts=[contract],
                                   start=datetime(2026, 9, 1, tzinfo=timezone.utc),
                                   end=datetime(2026, 9, 2, tzinfo=timezone.utc),
                                   output_dir=tmp_path, report=report)
        except GrowwRateLimitError:
            pass
        else:
            raise AssertionError("rate-limit failure must stop the resumable download")

    assert report["failed"] == [{"symbol": contract["symbol"], "error": "rate-limited"}]