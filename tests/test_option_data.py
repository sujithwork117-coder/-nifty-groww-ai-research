from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd

from app.groww_data import save_option_historical


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