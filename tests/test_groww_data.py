from pathlib import Path

import pandas as pd
import pytest

from app.groww_data import save_historical, validate_candles


def candles():
    return pd.DataFrame([
        {"timestamp": "2026-01-01T09:20:00Z", "open": 101, "high": 103, "low": 100, "close": 102, "volume": 10, "oi": 20},
        {"timestamp": "2026-01-01T09:15:00Z", "open": 99, "high": 102, "low": 98, "close": 101, "volume": 11, "oi": 21},
    ])


def test_validate_candles_sorts_and_normalizes_timestamps():
    result = validate_candles(candles())

    assert result["timestamp"].is_monotonic_increasing
    assert str(result.loc[0, "timestamp"]) == "2026-01-01 09:15:00+00:00"


def test_validate_candles_rejects_invalid_ohlc():
    data = candles()
    data.loc[0, "low"] = 104

    with pytest.raises(ValueError, match="OHLC"):
        validate_candles(data)


def test_validate_candles_rejects_duplicate_timestamps():
    data = candles()
    data.loc[1, "timestamp"] = data.loc[0, "timestamp"]

    with pytest.raises(ValueError, match="Duplicate"):
        validate_candles(data)


def test_save_historical_creates_parent_and_csv(tmp_path):
    destination = Path(tmp_path) / "raw" / "nifty.csv"

    result = save_historical(candles(), destination)

    assert result == destination
    saved = pd.read_csv(destination)
    assert list(saved.columns) == ["timestamp", "open", "high", "low", "close", "volume", "oi"]
    assert len(saved) == 2