import argparse
import json
import time
from pathlib import Path

from .config import CFG
from .experiment_spec import ExperimentSpecError, validate_experiment_spec, validate_result_completeness
from .llm import LLMConfigurationError, build_llm_provider
from .research_state import ResearchState
from .weekly_experiment import run_baseline_week, select_latest_completed_week


class ResearchAgent:
    """Coordinate inspect/run/validate/save steps for one requested-period experiment."""

    def __init__(self, state=None, config=CFG):
        self.state = state or ResearchState()
        self.config = config

    def execute(self, hypothesis, dataset, operation, strategy_version="baseline-v1", **context):
        self.state.assert_safe(self.config)
        experiment_id = self.state.start_experiment(
            hypothesis, dataset, strategy_version=strategy_version, **context
        )
        result = self.state.run(experiment_id, operation, **context)
        return experiment_id, result

    def status(self):
        return self.state.load_checkpoint()

    @staticmethod
    def _json_reply(text):
        value = text.strip()
        if value.startswith("```"):
            value = value.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        try:
            result = json.loads(value)
        except json.JSONDecodeError as error:
            raise RuntimeError("LLM response was not valid JSON") from error
        if not isinstance(result, dict):
            raise RuntimeError("LLM response must be a JSON object")
        return result

    def run_autonomous(self, provider=None, max_experiments=1, max_failures=1,
                       max_retries=0, max_runtime_seconds=900, dry_run=False,
                       dataset="data/raw/nifty_5m.csv", option_dir="data/raw/options",
                       report_dir="data/reports"):
        if max_experiments != 1:
            raise ValueError("The bounded demo supports exactly one experiment")
        self.state.assert_safe(self.config)
        started = time.monotonic()
        provider = provider or build_llm_provider()
        selection = select_latest_completed_week(dataset, option_dir)
        context = {
            "dataset": dataset,
            "requested_period": {"start": str(selection["start"]), "end": str(selection["end"]),
                                "trading_dates": [str(date) for date in selection["trading_dates"]]},
            "option_file_count": len(selection["option_files"]),
            "canonical_strategies": ["LEVEL_TO_LEVEL", "EKALAYAVA"],
            "eligible_contracts": "NIFTY ITM rank 2 and 3 for both CE and PE",
            "timeframe": "completed 5-minute candles in Asia/Kolkata",
            "missing_option_candles": "mark unavailable; never interpolate or fabricate",
            "prior_experiment": "Discard the previous SMA experiment as invalid/inconclusive for canonical project research.",
            "baseline": "baseline-v1 Level-to-Level and Ekalayava; no strategy changes",
        }
        spec_payload = self._json_reply(provider.complete(
            "You are a cautious quantitative research scientist. Return JSON only. "
            "The canonical project rules are Level-to-Level and Ekalayava for NIFTY options. "
            "Do not propose SMA, momentum, EMA, RSI, MACD, or other unapproved strategy changes. "
            "Use only ITM rank 2 and 3 CE/PE contracts. Use completed 5-minute candles in Asia/Kolkata. "
            "Missing option candles are unavailable data and must never be interpolated or fabricated. "
            "The previous SMA experiment is invalid/inconclusive and must not be used as canonical evidence.",
            "Generate exactly one structured ExperimentSpec. Do not return prose outside JSON. "
            "dataset_period must be 2026-07-23 through 2026-09-23, with actual coverage reported separately. "
            "Required JSON keys: hypothesis, strategy_scope, dataset_period, comparison_dimension, "
            "required_metrics, required_groupings, statistical_test, minimum_data_requirements, reason. "
            "Use only supported metrics and groupings; statistical_test must be null. "
            f"Context: {json.dumps(context, sort_keys=True)}"
        ))
        try:
            spec = validate_experiment_spec(spec_payload, dataset, selection)
        except ExperimentSpecError as error:
            spec = None
            correction_error = error
            for _ in range(2):
                corrected = self._json_reply(provider.complete(
                    "Return ONLY one valid JSON object, with no markdown and no prose. "
                    "Every list field must be a JSON array. Reject non-canonical strategies, indicators, "
                    "interpolation, fabricated data, unsupported metrics, and statistical tests.",
                    f"The previous specification failed validation: {correction_error}. Return exactly this shape: "
                    '{"hypothesis":"...","strategy_scope":["LEVEL_TO_LEVEL","EKALAYAVA"],'
                    '"dataset_period":"...","comparison_dimension":"strategy",'
                    '"required_metrics":["strategy_breakdown","average_daily_points_by_strategy"],'
                    '"required_groupings":["strategy"],"statistical_test":null,'
                    '"minimum_data_requirements":["completed 5-minute candles","ITM 2 and 3 CE/PE"],'
                    '"reason":"..."}. Context: '
                    f"{json.dumps(context, sort_keys=True)}"
                ))
                try:
                    spec = validate_experiment_spec(corrected, dataset, selection)
                    break
                except ExperimentSpecError as retry_error:
                    correction_error = retry_error
            if spec is None:
                raise correction_error
        if dry_run:
            return {"status": "DRY_RUN", "experiment_spec": spec.as_dict(), "context": context}
        if time.monotonic() - started > max_runtime_seconds:
            raise TimeoutError("Autonomous research runtime limit exceeded before experiment")
        experiment_id = self.state.start_experiment(
            spec.hypothesis, dataset, strategy_version="baseline-v1",
            experiment_spec=spec.as_dict(), selected_period=context["requested_period"]
        )
        failures = 0
        while True:
            try:
                result = run_baseline_week(dataset, option_dir, selection)
                break
            except Exception as error:
                failures += 1
                self.state.record_error(experiment_id, error, context={"phase": "deterministic_run"})
                if failures > max_failures or failures > max_retries:
                    self.state.finish_experiment(experiment_id, "FAILED", error=str(error))
                    raise
        if time.monotonic() - started > max_runtime_seconds:
            self.state.finish_experiment(experiment_id, "FAILED", error="runtime limit exceeded")
            raise TimeoutError("Autonomous research runtime limit exceeded")
        try:
            completeness = validate_result_completeness(spec, result)
        except ExperimentSpecError as error:
            self.state.record_error(experiment_id, error, context={"phase": "result_completeness"})
            self.state.finish_experiment(experiment_id, "FAILED", error=str(error))
            raise
        interpretation = self._json_reply(provider.complete(
            "You are a cautious quantitative research scientist. Return JSON only. "
            "Evaluate only the canonical NIFTY Level-to-Level and Ekalayava result. "
            "Treat missing option candles as a limitation; do not assume interpolation. "
            "The previous SMA experiment is invalid/inconclusive and is not evidence.",
            "Interpret this actual deterministic experiment result. Required JSON keys: decision, "
            "supported_evidence, contradictory_evidence, data_limitations, strategy_change_proposed, "
            "next_question. decision must be SUPPORTED, NOT_SUPPORTED, NEED_MORE_DATA, or INCONCLUSIVE. "
            "Use METRIC NOT AVAILABLE for anything absent; do not estimate. "
            f"ExperimentSpec: {json.dumps(spec.as_dict(), sort_keys=True)}\nResult: {json.dumps(result, sort_keys=True, default=str)}"
        ))
        decision = interpretation.get("decision")
        if decision not in {"SUPPORTED", "NOT_SUPPORTED", "NEED_MORE_DATA", "INCONCLUSIVE"}:
            raise RuntimeError(f"LLM returned unsupported decision: {decision}")
        report_path = Path(report_dir) / f"ai_experiment_{experiment_id}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report = {"experiment_id": experiment_id,
                  "research_lineage": {
                      "canonical_rules": "NIFTY Level-to-Level + Ekalayava",
                      "discarded_experiment": "Previous SMA experiment marked invalid/inconclusive",
                      "missing_option_candles": "unavailable; no interpolation or fabrication",
                  },
                  "experiment_spec": spec.as_dict(), "result_completeness": completeness,
                  "plan": spec.as_dict(), "result": result,
                  "interpretation": interpretation, "provider": provider.provider,
                  "model": provider.model}
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
        self.state.finish_experiment(experiment_id, decision, result=result,
                                     interpretation=interpretation, report=str(report_path))
        return {"experiment_id": experiment_id, "experiment_spec": spec.as_dict(),
            "plan": spec.as_dict(), "result": result,
                "interpretation": interpretation, "report": str(report_path),
                "steps": 7, "provider": provider.provider, "model": provider.model}


def main():
    parser = argparse.ArgumentParser(description="Manage bounded paper-only research experiments.")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--autonomous", action="store_true")
    parser.add_argument("--max-experiments", type=int, default=1)
    parser.add_argument("--max-failures", type=int, default=1)
    parser.add_argument("--max-retries", type=int, default=0)
    parser.add_argument("--max-runtime-seconds", type=int, default=900)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    agent = ResearchAgent()
    if args.status:
        print(json.dumps(agent.status(), indent=2, sort_keys=True))
    elif args.autonomous:
        try:
            output = agent.run_autonomous(
                max_experiments=args.max_experiments, max_failures=args.max_failures,
                max_retries=args.max_retries, max_runtime_seconds=args.max_runtime_seconds,
                dry_run=args.dry_run)
        except LLMConfigurationError as error:
            parser.error(str(error))
        else:
            print(json.dumps(output, indent=2, sort_keys=True, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()