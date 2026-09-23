import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .safety import ExecutionLock


class ResearchState:
    """Persist experiment checkpoints without changing research results."""

    def __init__(self, root="data/agent_state"):
        self.root = Path(root)
        self.checkpoint_path = self.root / "checkpoint.json"
        self.experiment_log_path = self.root / "experiments.jsonl"
        self.error_log_path = self.root / "errors.jsonl"

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat()

    def _write_json(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(path)

    def _append_json(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(value, sort_keys=True, default=str) + "\n")

    def load_checkpoint(self):
        if not self.checkpoint_path.exists():
            return None
        return json.loads(self.checkpoint_path.read_text(encoding="utf-8"))

    def save_checkpoint(self, experiment_id, status, **details):
        checkpoint = {
            "experiment_id": experiment_id,
            "status": status,
            "updated_at": self._now(),
            **details,
        }
        self._write_json(self.checkpoint_path, checkpoint)
        return checkpoint

    def start_experiment(self, hypothesis, dataset, strategy_version="baseline-v1", **details):
        experiment_id = details.pop("experiment_id", None) or f"EXP-{uuid4().hex[:10]}"
        record = {
            "experiment_id": experiment_id,
            "status": "RUNNING",
            "started_at": self._now(),
            "hypothesis": hypothesis,
            "dataset": dataset,
            "strategy_version": strategy_version,
            **details,
        }
        self._append_json(self.experiment_log_path, record)
        self.save_checkpoint(experiment_id, "RUNNING", hypothesis=hypothesis, dataset=dataset,
                             strategy_version=strategy_version)
        return experiment_id

    def finish_experiment(self, experiment_id, status, **details):
        if status not in {"COMPLETED", "FAILED", "REJECTED", "NEEDS_MORE_DATA"}:
            raise ValueError(f"Unsupported experiment status: {status}")
        record = {"experiment_id": experiment_id, "status": status,
                  "finished_at": self._now(), **details}
        self._append_json(self.experiment_log_path, record)
        return self.save_checkpoint(experiment_id, status, **details)

    def record_error(self, experiment_id, error, context=None, recoverable=False):
        record = {
            "experiment_id": experiment_id,
            "recorded_at": self._now(),
            "error_type": type(error).__name__,
            "message": str(error),
            "context": context or {},
            "recoverable": recoverable,
        }
        self._append_json(self.error_log_path, record)
        return record

    def run(self, experiment_id, operation, **context):
        """Run one operation, checkpoint failures, and re-raise the real error."""
        try:
            result = operation()
        except Exception as error:
            self.record_error(experiment_id, error, context=context)
            self.finish_experiment(experiment_id, "FAILED", error=str(error))
            raise
        self.finish_experiment(experiment_id, "COMPLETED", result=result)
        return result

    def assert_safe(self, config):
        return ExecutionLock(config).assert_paper_only()