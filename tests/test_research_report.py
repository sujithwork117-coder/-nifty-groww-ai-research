import pandas as pd

from app.learning import build_research_report


def test_research_report_contains_supported_statistics():
    events=pd.DataFrame([
        {"outcome":"TARGET","points_gained_lost":8,"mfe":9,"mae":-2,"time_to_exit_minutes":5,"entry_hour":9,"entry_before_10":True,"option_type":"CE","itm_rank":2,"strategy":"LEVEL_TO_LEVEL","false_breakout":False},
        {"outcome":"SL","points_gained_lost":-4,"mfe":2,"mae":-5,"time_to_exit_minutes":10,"entry_hour":10,"entry_before_10":False,"option_type":"PE","itm_rank":3,"strategy":"LEVEL_TO_LEVEL","false_breakout":True},
    ])

    report=build_research_report(events,{"invalid_ohlc_count":0})

    assert report["total_setups"]==2
    assert report["target_hits"]==1
    assert report["sl_hits"]==1
    assert report["average_points"]==2
    assert report["median_points"]==2
    assert report["data_quality"]["invalid_ohlc_count"]==0
    assert report["option_type_distribution"]["CE"]==1