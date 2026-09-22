import pandas as pd

from app.paper import analyze_ekalayava


def test_ekalayava_analysis_records_setup_without_target():
    candles=pd.DataFrame([
        {"timestamp":pd.Timestamp("2026-09-01 09:15",tz="Asia/Kolkata"),"open":100,"high":105,"low":100,"close":103},
        {"timestamp":pd.Timestamp("2026-09-01 09:20",tz="Asia/Kolkata"),"open":104,"high":106,"low":101,"close":102},
        {"timestamp":pd.Timestamp("2026-09-01 09:25",tz="Asia/Kolkata"),"open":102,"high":108,"low":101,"close":107},
        {"timestamp":pd.Timestamp("2026-09-01 09:30",tz="Asia/Kolkata"),"open":107,"high":107,"low":104,"close":105},
        {"timestamp":pd.Timestamp("2026-09-01 09:35",tz="Asia/Kolkata"),"open":105,"high":106,"low":103,"close":104},
        {"timestamp":pd.Timestamp("2026-09-01 09:40",tz="Asia/Kolkata"),"open":107,"high":112,"low":106,"close":111},
        {"timestamp":pd.Timestamp("2026-09-01 09:45",tz="Asia/Kolkata"),"open":111,"high":115,"low":110,"close":114},
    ])

    result=analyze_ekalayava(candles,{"symbol":"NIFTY-PE","expiry":"2026-09-24","strike":25200,"option_type":"PE","itm_rank":3})

    assert len(result)==1
    row=result.iloc[0]
    assert row.strategy=="EKALAYAVA"
    assert "target" not in result
    assert row.breakout_timestamp==row.confirmation_timestamp==row.timestamp
    assert row.mfe==4
    assert row.mae==-1
    assert row.option_type=="PE"