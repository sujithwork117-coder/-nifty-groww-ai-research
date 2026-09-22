from types import SimpleNamespace

import pandas as pd
import pytest

from app.paper import run_paper_level_to_level


def test_paper_engine_requires_safety_lock():
    config=SimpleNamespace(execution_allowed=True,paper_only=True,kill_switch=False)

    with pytest.raises(RuntimeError,match="Execution"):
        run_paper_level_to_level(pd.DataFrame(),config=config)


def test_paper_engine_journals_hypothetical_trade(tmp_path):
    config=SimpleNamespace(execution_allowed=False,paper_only=True,kill_switch=False,
                           level_sl_points=4,level_entry_start="09:15",level_entry_end="11:00",model_version="test")
    candles=pd.DataFrame([
        {"timestamp":pd.Timestamp("2026-09-01 09:15",tz="Asia/Kolkata"),"open":105,"high":110,"low":100,"close":105},
        {"timestamp":pd.Timestamp("2026-09-01 09:20",tz="Asia/Kolkata"),"open":102,"high":103,"low":99,"close":101},
        {"timestamp":pd.Timestamp("2026-09-01 09:25",tz="Asia/Kolkata"),"open":100,"high":103,"low":100,"close":102},
        {"timestamp":pd.Timestamp("2026-09-01 09:30",tz="Asia/Kolkata"),"open":103,"high":110,"low":102,"close":109},
    ])
    journal=tmp_path/"paper.csv"

    trades=run_paper_level_to_level(candles,config=config,journal_path=journal)

    assert len(trades)==1
    assert "LEVEL_TO_LEVEL" in journal.read_text()