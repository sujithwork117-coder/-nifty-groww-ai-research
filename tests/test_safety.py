from app.config import CFG
from app.safety import ExecutionLock
def test_execution_locked():
    assert CFG.execution_allowed is False
    assert CFG.paper_only is True
    assert ExecutionLock(CFG).assert_paper_only()
