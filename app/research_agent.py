import argparse
import json

from .config import CFG
from .research_state import ResearchState


class ResearchAgent:
    """Coordinate inspect/run/validate/save steps for one bounded experiment."""

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


def main():
    parser = argparse.ArgumentParser(description="Manage bounded paper-only research experiments.")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    agent = ResearchAgent()
    if args.status:
        print(json.dumps(agent.status(), indent=2, sort_keys=True))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()