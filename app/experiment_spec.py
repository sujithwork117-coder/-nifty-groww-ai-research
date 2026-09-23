from dataclasses import dataclass
from pathlib import Path


CANONICAL_STRATEGIES = {"LEVEL_TO_LEVEL", "EKALAYAVA"}
ALLOWED_GROUPINGS = {"strategy", "option_type", "itm_rank", "entry_hour"}
SUPPORTED_METRICS = {
    "setup_count", "valid_setups", "target_hits", "sl_hits", "open_outcomes",
    "points", "average_points", "median_points", "mfe", "mae", "holding_time",
    "drawdown", "streaks", "strategy_breakdown", "ce_pe_breakdown", "itm_breakdown",
    "entry_time_breakdown", "average_daily_points_by_strategy",
}
FORBIDDEN_TERMS = {
    "sma", "ema", "rsi", "macd", "vwap", "momentum", "interpolate",
    "forward-fill", "forward fill", "fabricate", "synthetic",
}


class ExperimentSpecError(ValueError):
    pass


@dataclass(frozen=True)
class ExperimentSpec:
    hypothesis: str
    strategy_scope: tuple
    dataset_period: str
    comparison_dimension: str
    required_metrics: tuple
    required_groupings: tuple
    statistical_test: str | None
    minimum_data_requirements: tuple
    reason: str

    @classmethod
    def from_payload(cls, payload):
        if not isinstance(payload, dict):
            raise ExperimentSpecError("EXPERIMENT_SPEC_INVALID: response must be an object")
        required = ("hypothesis", "strategy_scope", "dataset_period", "comparison_dimension",
                    "required_metrics", "required_groupings", "statistical_test",
                    "minimum_data_requirements", "reason")
        missing = [key for key in required if key not in payload]
        if missing:
            raise ExperimentSpecError(f"EXPERIMENT_SPEC_INVALID: missing keys {missing}")
        values = {key: payload[key] for key in required}
        for key in ("hypothesis", "dataset_period", "comparison_dimension", "reason"):
            if not isinstance(values[key], str) or not values[key].strip():
                raise ExperimentSpecError(f"EXPERIMENT_SPEC_INVALID: {key} must be non-empty text")
        for key in ("strategy_scope", "required_metrics", "required_groupings", "minimum_data_requirements"):
            if not isinstance(values[key], list):
                raise ExperimentSpecError(f"EXPERIMENT_SPEC_INVALID: {key} must be a list")
        return cls(
            hypothesis=values["hypothesis"].strip(),
            strategy_scope=tuple(values["strategy_scope"]),
            dataset_period=values["dataset_period"].strip(),
            comparison_dimension=values["comparison_dimension"].strip(),
            required_metrics=tuple(values["required_metrics"]),
            required_groupings=tuple(values["required_groupings"]),
            statistical_test=values["statistical_test"],
            minimum_data_requirements=tuple(values["minimum_data_requirements"]),
            reason=values["reason"].strip(),
        )

    def as_dict(self):
        return {
            "hypothesis": self.hypothesis,
            "strategy_scope": list(self.strategy_scope),
            "dataset_period": self.dataset_period,
            "comparison_dimension": self.comparison_dimension,
            "required_metrics": list(self.required_metrics),
            "required_groupings": list(self.required_groupings),
            "statistical_test": self.statistical_test,
            "minimum_data_requirements": list(self.minimum_data_requirements),
            "reason": self.reason,
        }


def validate_experiment_spec(payload, dataset, selection):
    spec = ExperimentSpec.from_payload(payload)
    if set(spec.strategy_scope) - CANONICAL_STRATEGIES:
        raise ExperimentSpecError("EXPERIMENT_SPEC_INVALID: non-canonical strategy requested")
    if not spec.strategy_scope:
        raise ExperimentSpecError("EXPERIMENT_SPEC_INVALID: strategy_scope cannot be empty")
    if set(spec.required_metrics) - SUPPORTED_METRICS:
        unsupported = sorted(set(spec.required_metrics) - SUPPORTED_METRICS)
        raise ExperimentSpecError(f"EXPERIMENT_SPEC_INVALID: unsupported metrics {unsupported}")
    if set(spec.required_groupings) - ALLOWED_GROUPINGS:
        unsupported = sorted(set(spec.required_groupings) - ALLOWED_GROUPINGS)
        raise ExperimentSpecError(f"EXPERIMENT_SPEC_INVALID: unsupported groupings {unsupported}")
    if spec.statistical_test not in (None, "", "null"):
        raise ExperimentSpecError("EXPERIMENT_SPEC_INVALID: statistical tests are not supported by baseline-v1")
    text = " ".join((spec.hypothesis, spec.comparison_dimension, spec.reason,
                      " ".join(spec.minimum_data_requirements))).lower()
    for allowed_phrase in ("no interpolation", "without interpolation", "do not interpolate",
                           "never interpolate", "no sma", "no ema", "no rsi", "no macd", "no vwap"):
        text = text.replace(allowed_phrase, "")
    forbidden = sorted(term for term in FORBIDDEN_TERMS if term in text)
    if forbidden:
        raise ExperimentSpecError(f"EXPERIMENT_SPEC_INVALID: forbidden data or strategy treatment {forbidden}")
    if not Path(dataset).is_file():
        raise ExperimentSpecError(f"EXPERIMENT_SPEC_INVALID: dataset does not exist: {dataset}")
    requested_start = selection.get("requested_start", selection.get("start"))
    requested_end = selection.get("requested_end", selection.get("end"))
    if requested_start is not None and requested_end is not None:
        period = spec.dataset_period.replace(" ", "")
        if str(requested_start) not in period or str(requested_end) not in period:
            raise ExperimentSpecError(
                f"EXPERIMENT_SPEC_INVALID: dataset_period must cover {requested_start} through {requested_end}"
            )
    if len(selection.get("option_files", [])) < 4:
        raise ExperimentSpecError("EXPERIMENT_SPEC_INVALID: fewer than four eligible option contracts")
    eligibility = selection.get("contract_eligibility", [])
    if eligibility:
        if any(not item.get("eligible") or item.get("itm_rank") not in (2, 3) for item in eligibility):
            raise ExperimentSpecError("EXPERIMENT_SPEC_INVALID: contract eligibility contains non-ITM-2/3 data")
        pairs = {(item.get("option_type"), item.get("itm_rank")) for item in eligibility}
        if pairs != {("CE", 2), ("CE", 3), ("PE", 2), ("PE", 3)}:
            raise ExperimentSpecError("EXPERIMENT_SPEC_INVALID: required CE/PE ITM 2/3 contracts are incomplete")
    return spec


def validate_result_completeness(spec, result):
    metrics = result.get("metrics", {})
    paths = {
        "setup_count": "setup_count", "valid_setups": "valid_setups", "target_hits": "target_hits",
        "sl_hits": "sl_hits", "open_outcomes": "outcomes", "points": "average_points",
        "average_points": "average_points", "median_points": "median_points", "mfe": "average_mfe",
        "mae": "average_mae", "holding_time": "average_holding_time_minutes",
        "drawdown": "maximum_drawdown_points", "streaks": "maximum_winning_streak",
        "strategy_breakdown": "by_strategy", "ce_pe_breakdown": "by_option_type",
        "itm_breakdown": "by_itm_rank", "entry_time_breakdown": "by_entry_hour",
        "average_daily_points_by_strategy": "by_strategy",
    }
    missing = [metric for metric in spec.required_metrics if paths.get(metric) not in metrics]
    if "average_daily_points_by_strategy" in spec.required_metrics:
        for strategy in spec.strategy_scope:
            if strategy not in metrics.get("by_strategy", {}) or "average_daily_points" not in metrics["by_strategy"][strategy]:
                missing.append(f"average_daily_points_by_strategy.{strategy}")
    if missing:
        raise ExperimentSpecError(f"RESULT_INCOMPLETE: missing metrics {sorted(set(missing))}")
    return {"status": "PASS", "required_metrics": list(spec.required_metrics), "missing_metrics": []}