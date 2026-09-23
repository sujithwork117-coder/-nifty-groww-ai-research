import json

import app.research_agent as research_agent
from app.research_agent import ResearchAgent
from app.research_state import ResearchState


class FakeProvider:
    provider = "fake-test-provider"
    model = "fake-test-model"

    def __init__(self):
        self.prompts = []

    def complete(self, system, user):
        self.prompts.append(user)
        if len(self.prompts) == 1:
            return json.dumps({
                "hypothesis": "PE and CE outcomes differ by entry time",
                "strategy_scope": ["LEVEL_TO_LEVEL", "EKALAYAVA"],
                "dataset_period": "2026-07-23 to 2026-09-23",
                "comparison_dimension": "option_type and entry_hour",
                "required_metrics": [],
                "required_groupings": ["option_type", "entry_hour"],
                "statistical_test": None,
                "minimum_data_requirements": ["completed 5-minute candles", "ITM 2/3 CE/PE"],
                "reason": "The available contract data supports a bounded segment comparison.",
            })
        return json.dumps({
            "decision": "NEED_MORE_DATA",
            "supported_evidence": ["The bounded result was computed from baseline-v1."],
            "contradictory_evidence": [],
            "data_limitations": ["One week is insufficient for out-of-sample validation."],
            "strategy_change_proposed": False,
            "next_question": "Does the segment difference persist in another week?",
        })


def test_autonomous_loop_uses_ai_plan_and_decision(tmp_path, monkeypatch):
    selection = {"start": "2026-07-23", "end": "2026-09-23",
                 "trading_dates": ["2026-07-23", "2026-09-23"],
                 "option_files": ["a", "b", "c", "d"]}
    result = {"setup_count": 4, "valid_setups": 4, "target_hits": 1, "sl_hits": 3,
              "lookahead_check": "PASS"}
    monkeypatch.setattr(research_agent, "select_latest_completed_week", lambda *_: selection)
    monkeypatch.setattr(research_agent, "run_baseline_week", lambda *_: result)
    provider = FakeProvider()

    output = ResearchAgent(ResearchState(tmp_path)).run_autonomous(provider=provider)

    assert output["interpretation"]["decision"] == "NEED_MORE_DATA"
    assert output["plan"]["hypothesis"].startswith("PE and CE")
    assert len(provider.prompts) == 2
    assert ResearchState(tmp_path).load_checkpoint()["status"] == "NEED_MORE_DATA"