import pandas as pd

from app.paper import backtest_level_to_level


def test_level_backtest_returns_deterministic_result_and_metadata():
    candles=pd.DataFrame([
        {"timestamp":pd.Timestamp("2026-09-01 09:15",tz="Asia/Kolkata"),"open":105,"high":110,"low":100,"close":105},
        {"timestamp":pd.Timestamp("2026-09-01 09:20",tz="Asia/Kolkata"),"open":102,"high":103,"low":99,"close":101},
        {"timestamp":pd.Timestamp("2026-09-01 09:25",tz="Asia/Kolkata"),"open":100,"high":103,"low":100,"close":102},
        {"timestamp":pd.Timestamp("2026-09-01 09:30",tz="Asia/Kolkata"),"open":103,"high":110,"low":102,"close":109},
    ])

    result=backtest_level_to_level(candles,{"symbol":"NIFTY-CE","expiry":"2026-09-24","strike":25000,"option_type":"CE","itm_rank":2})

    assert len(result)==1
    row=result.iloc[0]
    assert row.outcome=="TARGET"
    assert row.points_gained_lost==8
    assert row.time_to_exit_minutes==5
    assert bool(row.before_10) is True
    assert row.option_type=="CE"


def test_level_backtest_marks_same_candle_ambiguity_as_sl_first():
    candles=pd.DataFrame([
        {"timestamp":pd.Timestamp("2026-09-01 09:15",tz="Asia/Kolkata"),"open":105,"high":110,"low":100,"close":105},
        {"timestamp":pd.Timestamp("2026-09-01 09:20",tz="Asia/Kolkata"),"open":102,"high":103,"low":99,"close":101},
        {"timestamp":pd.Timestamp("2026-09-01 09:25",tz="Asia/Kolkata"),"open":100,"high":110,"low":95,"close":102},
        {"timestamp":pd.Timestamp("2026-09-01 09:30",tz="Asia/Kolkata"),"open":100,"high":110,"low":95,"close":102},
    ])

    result=backtest_level_to_level(candles)

    assert result.iloc[0].outcome=="AMBIGUOUS_SL_FIRST"
    assert result.iloc[0].exit_price==96