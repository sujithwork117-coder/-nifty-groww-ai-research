import pandas as pd

from app.paper import evaluate_paper_signal


def test_evaluate_paper_signal_is_read_only_and_records_path():
    candles=pd.DataFrame([
        {"timestamp":pd.Timestamp("2026-09-01 09:20",tz="Asia/Kolkata"),"high":103,"low":99},
        {"timestamp":pd.Timestamp("2026-09-01 09:25",tz="Asia/Kolkata"),"high":110,"low":100},
    ])
    signal={"timestamp":pd.Timestamp("2026-09-01 09:15",tz="Asia/Kolkata"),"entry":102,"sl":98,"target":110}

    result=evaluate_paper_signal(candles,signal)

    assert result["outcome"]=="TARGET"
    assert result["mfe"]==8
    assert result["mae"]==-3
    assert result["execution"]=="DISABLED"