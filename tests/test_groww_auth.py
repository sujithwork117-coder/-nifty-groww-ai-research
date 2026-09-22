from types import SimpleNamespace
from unittest.mock import patch

import pytest

from app.groww_auth import authenticate


def config(**values):
    defaults = {"api_key": "key", "api_secret": "secret", "totp": ""}
    defaults.update(values)
    return SimpleNamespace(**defaults)


def test_authenticate_uses_secret():
    with patch("app.groww_auth.GrowwAPI") as client:
        client.get_access_token.return_value = "token"
        result = authenticate(config())

    client.get_access_token.assert_called_once_with(api_key="key", secret="secret", totp=None)
    client.assert_called_once_with("token")
    assert result is client.return_value


def test_authenticate_rejects_both_credential_modes():
    with pytest.raises(RuntimeError, match="only one"):
        authenticate(config(totp="123456"))


def test_authenticate_requires_credential_mode():
    with pytest.raises(RuntimeError, match="API_SECRET or GROWW_TOTP"):
        authenticate(config(api_secret=""))