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
    assert row.target==110


def test_level_backtest_marks_same_candle_ambiguity_without_inventing_exit_price():
    candles=pd.DataFrame([
        {"timestamp":pd.Timestamp("2026-09-01 09:15",tz="Asia/Kolkata"),"open":105,"high":110,"low":100,"close":105},
        {"timestamp":pd.Timestamp("2026-09-01 09:20",tz="Asia/Kolkata"),"open":102,"high":103,"low":99,"close":101},
        {"timestamp":pd.Timestamp("2026-09-01 09:25",tz="Asia/Kolkata"),"open":100,"high":110,"low":95,"close":102},
        {"timestamp":pd.Timestamp("2026-09-01 09:30",tz="Asia/Kolkata"),"open":100,"high":110,"low":95,"close":102},
    ])

    result=backtest_level_to_level(candles)

    assert result.iloc[0].outcome=="AMBIGUOUS"
    assert pd.isna(result.iloc[0].exit_price)


def test_level_metrics_stop_at_exit_and_at_end_of_entry_day():
    candles=pd.DataFrame([
        {"timestamp":pd.Timestamp("2026-09-01 09:15",tz="Asia/Kolkata"),"open":105,"high":110,"low":100,"close":105},
        {"timestamp":pd.Timestamp("2026-09-01 09:20",tz="Asia/Kolkata"),"open":102,"high":103,"low":99,"close":101},
        {"timestamp":pd.Timestamp("2026-09-01 09:25",tz="Asia/Kolkata"),"open":100,"high":103,"low":100,"close":102},
        {"timestamp":pd.Timestamp("2026-09-01 09:30",tz="Asia/Kolkata"),"open":103,"high":110,"low":102,"close":109},
        {"timestamp":pd.Timestamp("2026-09-01 09:35",tz="Asia/Kolkata"),"open":109,"high":150,"low":108,"close":149},
        {"timestamp":pd.Timestamp("2026-09-02 09:15",tz="Asia/Kolkata"),"open":149,"high":200,"low":140,"close":190},
    ])

    result=backtest_level_to_level(candles)

    assert result.iloc[0].outcome=="TARGET"
    assert result.iloc[0].mfe==8
    assert result.iloc[0].mae==0


def test_level_signal_is_skipped_if_entry_close_is_already_below_its_stop():
    candles=pd.DataFrame([
        {"timestamp":pd.Timestamp("2026-09-01 09:15",tz="Asia/Kolkata"),"open":105,"high":110,"low":100,"close":105},
        {"timestamp":pd.Timestamp("2026-09-01 09:20",tz="Asia/Kolkata"),"open":100,"high":103,"low":99,"close":99},
        {"timestamp":pd.Timestamp("2026-09-01 09:25",tz="Asia/Kolkata"),"open":88,"high":92,"low":87,"close":90},
        {"timestamp":pd.Timestamp("2026-09-01 09:30",tz="Asia/Kolkata"),"open":90,"high":100,"low":89,"close":99},
    ])

    result=backtest_level_to_level(candles)

    assert len(result)==1
    assert result.iloc[0].outcome=="SKIPPED_SL_ALREADY_BREACHED"
    assert pd.isna(result.iloc[0].points_gained_lost)
    assert result.iloc[0].skip_reason=="entry close is at or below the configured stop-loss"
