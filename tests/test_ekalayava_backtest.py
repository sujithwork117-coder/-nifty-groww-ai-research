import pandas as pd

from app.paper import analyze_ekalayava


def test_ekalayava_analysis_targets_opening_high():
    candles=pd.DataFrame([
        {"timestamp":pd.Timestamp("2026-09-01 09:15",tz="Asia/Kolkata"),"open":103,"high":105,"low":100,"close":102},
        {"timestamp":pd.Timestamp("2026-09-01 09:20",tz="Asia/Kolkata"),"open":102,"high":101,"low":99,"close":99.5},
        {"timestamp":pd.Timestamp("2026-09-01 09:25",tz="Asia/Kolkata"),"open":99.5,"high":102,"low":99,"close":101},
        {"timestamp":pd.Timestamp("2026-09-01 09:30",tz="Asia/Kolkata"),"open":101,"high":103,"low":100,"close":102},
        {"timestamp":pd.Timestamp("2026-09-01 09:35",tz="Asia/Kolkata"),"open":102,"high":104,"low":101,"close":103},
        {"timestamp":pd.Timestamp("2026-09-01 09:40",tz="Asia/Kolkata"),"open":103,"high":106,"low":102,"close":105},
    ])

    result=analyze_ekalayava(candles,{"symbol":"NIFTY-PE","expiry":"2026-09-24","strike":25200,"option_type":"PE","itm_rank":3})

    assert len(result)==1
    row=result.iloc[0]
    assert row.strategy=="EKALAYAVA"
    assert row.target==105
    assert row.outcome=="TARGET"
    assert row.breakout_timestamp==row.confirmation_timestamp==row.timestamp
    assert row.mfe==3
    assert row.mae==-1
    assert row.option_type=="PE"