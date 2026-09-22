import pandas as pd

from app.learning import enrich_events,split_time


def test_learning_enrichment_records_required_time_and_setup_features():
    candles=pd.DataFrame([
        {"timestamp":pd.Timestamp("2026-09-01 09:15",tz="Asia/Kolkata"),"date":pd.Timestamp("2026-09-01").date(),"high":110,"low":100,"close":105,"volatility_10":0.2,"premium_change":1,"candle_type":"strong_green","lower_wick":1,"upper_wick":1,"range":10,"above_opening_high":False},
        {"timestamp":pd.Timestamp("2026-09-01 09:20",tz="Asia/Kolkata"),"date":pd.Timestamp("2026-09-01").date(),"high":112,"low":104,"close":111,"volatility_10":0.3,"premium_change":2,"candle_type":"normal","lower_wick":1,"upper_wick":1,"range":8,"above_opening_high":True},
    ])
    events=pd.DataFrame([{"date":"2026-09-01","timestamp":candles.timestamp.iloc[0],"entry":105,"sl":96,"target":110}])

    result=enrich_events(events,candles)
    row=result.iloc[0]

    assert row.entry_before_10
    assert row.weekday==1
    assert row.volatility_10==0.2
    assert row.rejection_characteristic=="strong_green"
    assert row.time_to_target_minutes==5


def test_split_time_preserves_chronological_order():
    events=pd.DataFrame({"timestamp":pd.to_datetime(["2026-01-03","2026-01-01","2026-01-02"])})

    train,validation=split_time(events,frac=2/3)

    assert list(train.timestamp.dt.day)==[1,2]
    assert list(validation.timestamp.dt.day)==[3]