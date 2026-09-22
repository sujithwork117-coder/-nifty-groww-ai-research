from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.main import verify_read_only


def test_verify_read_only_uses_user_profile_only(capsys):
    config = SimpleNamespace(
        execution_allowed=False,
        paper_only=True,
        kill_switch=False,
    )
    groww = Mock()
    groww.get_user_profile.return_value = {"active_segments": ["FNO"]}

    with patch("app.main.CFG", config), patch("app.main.authenticate", return_value=groww):
        verify_read_only()

    groww.get_user_profile.assert_called_once_with()
    groww.assert_not_called()
    output = capsys.readouterr().out
    assert "Groww authentication: SUCCESS" in output
    assert "Read-only API: SUCCESS" in output
    assert "Order execution: DISABLED" in output