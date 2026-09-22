import pandas as pd

from app.learning import anti_overfit_report,build_report


def test_anti_overfit_report_flags_small_chronological_samples():
    events=pd.DataFrame({"timestamp":pd.date_range("2026-01-01",periods=4),"mfe":[1,2,3,4],"mae":[-1,-2,-1,-3]})

    report=anti_overfit_report(events,min_train=3,min_validation=2)

    assert report["chronological_split"] is True
    assert report["insufficient_samples"] is True
    assert report["future_features_excluded"] is True


def test_model_report_does_not_use_future_mfe_or_mae_features():
    events=pd.DataFrame({"timestamp":pd.date_range("2026-01-01",periods=2),"outcome":["TARGET","SL"],"mfe":[2,3],"mae":[-1,-2],"entry_hour":[9,10]})

    report=build_report(events)

    assert "mfe" not in report["classifier"].get("features",[])
    assert "mae" not in report["classifier"].get("features",[])