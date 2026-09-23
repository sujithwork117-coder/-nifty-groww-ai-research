import pytest

from app.experiment_spec import ExperimentSpecError, validate_experiment_spec, validate_result_completeness


def spec(**overrides):
    value = {
        "hypothesis": "Level-to-Level and Ekalayava have different CE and PE outcomes",
        "strategy_scope": ["LEVEL_TO_LEVEL", "EKALAYAVA"],
        "dataset_period": "completed week",
        "comparison_dimension": "option_type",
        "required_metrics": ["strategy_breakdown", "ce_pe_breakdown"],
        "required_groupings": ["strategy", "option_type"],
        "statistical_test": None,
        "minimum_data_requirements": ["completed 5-minute candles", "ITM 2 and 3 CE/PE"],
        "reason": "Bounded canonical comparison",
    }
    value.update(overrides)
    return value


def selection():
    return {"option_files": ["a", "b", "c", "d"]}


def test_rejects_indicator_strategy_and_interpolation(tmp_path):
    dataset = tmp_path / "data.csv"
    dataset.write_text("timestamp\n")
    with pytest.raises(ExperimentSpecError, match="forbidden"):
        validate_experiment_spec(spec(hypothesis="Test SMA with interpolation"), dataset, selection())


def test_rejects_unsupported_metric(tmp_path):
    dataset = tmp_path / "data.csv"
    dataset.write_text("timestamp\n")
    with pytest.raises(ExperimentSpecError, match="unsupported metrics"):
        validate_experiment_spec(spec(required_metrics=["sharpe_ratio"]), dataset, selection())


def test_result_completeness_requires_requested_metric():
    from app.experiment_spec import ExperimentSpec
    experiment = ExperimentSpec.from_payload(spec(required_metrics=["average_daily_points_by_strategy"]))
    with pytest.raises(ExperimentSpecError, match="RESULT_INCOMPLETE"):
        validate_result_completeness(experiment, {"metrics": {"by_strategy": {}}})


def test_result_completeness_accepts_actual_metrics():
    from app.experiment_spec import ExperimentSpec
    experiment = ExperimentSpec.from_payload(spec(required_metrics=["average_daily_points_by_strategy"]))
    result = {"metrics": {"by_strategy": {
        "LEVEL_TO_LEVEL": {"average_daily_points": 1.0},
        "EKALAYAVA": {"average_daily_points": 2.0},
    }}}
    assert validate_result_completeness(experiment, result)["status"] == "PASS"