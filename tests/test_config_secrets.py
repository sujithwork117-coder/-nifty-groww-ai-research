from app.config import _optional_float, _secret_file_values


def test_secret_file_supports_env_and_labeled_formats(tmp_path):
    secret_file=tmp_path/"secrets.txt"
    secret_file.write_text("GROWW_API_KEY=key\napi secret - secret\n")

    values=_secret_file_values(secret_file)

    assert values=={"GROWW_API_KEY":"key","GROWW_API_SECRET":"secret"}


def test_optional_float_leaves_ekalayava_buffer_unset_by_default(monkeypatch):
    monkeypatch.delenv("EKALAYAVA_SL_BUFFER_POINTS", raising=False)
    assert _optional_float("EKALAYAVA_SL_BUFFER_POINTS") is None
    monkeypatch.setenv("EKALAYAVA_SL_BUFFER_POINTS", "2.5")
    assert _optional_float("EKALAYAVA_SL_BUFFER_POINTS") == 2.5
