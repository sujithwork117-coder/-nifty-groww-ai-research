from dataclasses import replace

import pytest

from app.config import CFG, _optional_float, _secret_file_values


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


def test_ekalayava_candidate_simulation_requires_explicit_opt_in_and_valid_buffer():
    observation = replace(CFG, ekalayava_sl_buffer_points=None,
                          ekalayava_experimental_exit_simulation=False)
    assert observation.ekalayava_sl_buffer_points is None
    assert observation.ekalayava_experimental_exit_simulation is False
    with pytest.raises(ValueError, match="explicit buffer"):
        replace(observation, ekalayava_experimental_exit_simulation=True)
    with pytest.raises(ValueError, match="EXPERIMENTAL_EXIT_SIMULATION=true"):
        replace(observation, ekalayava_sl_buffer_points=2.0)
    with pytest.raises(ValueError, match="finite and nonnegative"):
        replace(observation, ekalayava_sl_buffer_points=-1.0,
                ekalayava_experimental_exit_simulation=True)
    candidate = replace(observation, ekalayava_sl_buffer_points=2.0,
                        ekalayava_experimental_exit_simulation=True)
    assert candidate.ekalayava_sl_buffer_points == 2.0
