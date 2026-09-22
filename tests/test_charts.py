import pandas as pd

from app.charts import save_setup_chart


def test_save_setup_chart_creates_report_image(tmp_path):
    candles=pd.DataFrame({
        "timestamp":pd.date_range("2026-09-01 09:15",periods=3,freq="5min",tz="Asia/Kolkata"),
        "close":[100,102,105],
    })
    event={"strategy":"LEVEL_TO_LEVEL","timestamp":candles.timestamp.iloc[1],"opening_high":106,"opening_low":98,"sl":94,"target":106}
    destination=save_setup_chart(candles,event,tmp_path/"charts"/"setup.png")

    assert destination.exists()
    assert destination.stat().st_size>0