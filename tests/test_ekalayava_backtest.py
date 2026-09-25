import pandas as pd

from app.paper import analyze_ekalayava
from app.strategies import ekalayava_events


def test_ekalayava_analysis_targets_opening_high():
    candles=pd.DataFrame([
        {"timestamp":pd.Timestamp("2026-09-01 09:15",tz="Asia/Kolkata"),"open":103,"high":105,"low":100,"close":102},
        {"timestamp":pd.Timestamp("2026-09-01 09:20",tz="Asia/Kolkata"),"open":102,"high":101,"low":99,"close":99.5},
        {"timestamp":pd.Timestamp("2026-09-01 09:25",tz="Asia/Kolkata"),"open":99.5,"high":102,"low":99,"close":101},
        {"timestamp":pd.Timestamp("2026-09-01 09:30",tz="Asia/Kolkata"),"open":101,"high":103,"low":100,"close":102},
        {"timestamp":pd.Timestamp("2026-09-01 09:35",tz="Asia/Kolkata"),"open":102,"high":104,"low":101,"close":103.5},
        {"timestamp":pd.Timestamp("2026-09-01 09:40",tz="Asia/Kolkata"),"open":103,"high":106,"low":102,"close":105},
        {"timestamp":pd.Timestamp("2026-09-01 09:45",tz="Asia/Kolkata"),"open":105,"high":180,"low":90,"close":150},
        {"timestamp":pd.Timestamp("2026-09-02 09:15",tz="Asia/Kolkata"),"open":150,"high":200,"low":50,"close":180},
    ])

    result=analyze_ekalayava(candles,{"symbol":"NIFTY-PE","expiry":"2026-09-24","strike":25200,"option_type":"PE","itm_rank":3})

    assert len(result)==1
    row=result.iloc[0]
    assert row.strategy=="EKALAYAVA"
    assert row.target==105
    assert row.outcome=="TARGET"
    assert row.breakout_timestamp==row.confirmation_timestamp==row.timestamp
    assert row.mfe==2.5
    assert row.mae==-1.5
    assert row.option_type=="PE"


def test_ekalayava_requires_prior_break_below_opening_low():
    candles=pd.DataFrame([
        {"timestamp":pd.Timestamp("2026-09-01 09:15",tz="Asia/Kolkata"),"open":103,"high":105,"low":100,"close":102},
        {"timestamp":pd.Timestamp("2026-09-01 09:20",tz="Asia/Kolkata"),"open":102,"high":103,"low":100,"close":101},
        {"timestamp":pd.Timestamp("2026-09-01 09:25",tz="Asia/Kolkata"),"open":101,"high":104,"low":100.5,"close":103},
        {"timestamp":pd.Timestamp("2026-09-01 09:30",tz="Asia/Kolkata"),"open":103,"high":104.5,"low":102,"close":104},
    ])

    assert ekalayava_events(candles).empty


def test_ekalayava_does_not_enter_when_target_was_reached_before_breakout():
    candles=pd.DataFrame([
        {"timestamp":pd.Timestamp("2026-09-01 09:15",tz="Asia/Kolkata"),"open":103,"high":105,"low":100,"close":102},
        {"timestamp":pd.Timestamp("2026-09-01 09:20",tz="Asia/Kolkata"),"open":102,"high":101,"low":99,"close":99.5},
        {"timestamp":pd.Timestamp("2026-09-01 09:25",tz="Asia/Kolkata"),"open":99.5,"high":102,"low":99,"close":101},
        {"timestamp":pd.Timestamp("2026-09-01 09:30",tz="Asia/Kolkata"),"open":101,"high":105,"low":100,"close":104},
        {"timestamp":pd.Timestamp("2026-09-01 09:35",tz="Asia/Kolkata"),"open":104,"high":106,"low":103,"close":105.5},
    ])

    assert ekalayava_events(candles).empty
