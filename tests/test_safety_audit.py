from pathlib import Path
from types import SimpleNamespace

import pytest

from app.safety import ExecutionLock


def test_kill_switch_blocks_paper_operations():
    config=SimpleNamespace(execution_allowed=False,paper_only=True,kill_switch=True)

    with pytest.raises(RuntimeError,match="KILL SWITCH"):
        ExecutionLock(config).assert_paper_only()


def test_application_has_no_order_execution_methods():
    source="\n".join(path.read_text() for path in Path("app").glob("*.py"))

    assert "place_order(" not in source
    assert "modify_order(" not in source
    assert "cancel_order(" not in source