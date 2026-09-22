import pandas as pd

from app.learning import setup_quality_report


def test_setup_quality_report_emits_factual_groups_without_best_score():
    events=pd.DataFrame([
        {"entry_before_10":True,"option_type":"CE","itm_rank":2,"entry_hour":9,"weekday":0,"mfe":8,"mae":-2,"outcome":"TARGET","false_breakout":False},
        {"entry_before_10":False,"option_type":"PE","itm_rank":3,"entry_hour":10,"weekday":1,"mfe":3,"mae":-5,"outcome":"SL","false_breakout":True},
    ])

    report=setup_quality_report(events)

    assert report["events"]==2
    assert len(report["groups"]["option_type"])==2
    assert report["groups"]["option_type"][0]["n"]==1
    assert "best_setup" not in report
    assert "profitability" not in report