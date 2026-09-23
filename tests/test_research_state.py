import json

import pytest

from app.config import CFG
from app.research_agent import ResearchAgent
from app.research_state import ResearchState


def test_research_state_checkpoints_and_resumes(tmp_path):
    state = ResearchState(tmp_path)
    experiment_id = state.start_experiment("CE and PE differ", "sample.csv")

    assert state.load_checkpoint()["status"] == "RUNNING"
    state.finish_experiment(experiment_id, "COMPLETED", findings={"setups": 2})

    lines = state.experiment_log_path.read_text().splitlines()
    assert json.loads(lines[0])["experiment_id"] == experiment_id
    assert json.loads(lines[-1])["status"] == "COMPLETED"
    assert state.load_checkpoint()["status"] == "COMPLETED"


def test_research_state_records_and_reraises_failures(tmp_path):
    state = ResearchState(tmp_path)
    experiment_id = state.start_experiment("failure is visible", "sample.csv")

    def fail():
        raise RuntimeError("broken")

    with pytest.raises(RuntimeError, match="broken"):
        state.run(experiment_id, fail, phase="run")

    error = json.loads(state.error_log_path.read_text().splitlines()[0])
    assert error["message"] == "broken"
    assert state.load_checkpoint()["status"] == "FAILED"


def test_research_agent_enforces_paper_only_and_runs_operation(tmp_path):
    agent = ResearchAgent(ResearchState(tmp_path), CFG)

    experiment_id, result = agent.execute(
        "bounded operation succeeds", "sample.csv", lambda: {"value": 3}
    )

    assert experiment_id.startswith("EXP-")
    assert result == {"value": 3}
    assert agent.status()["status"] == "COMPLETED"