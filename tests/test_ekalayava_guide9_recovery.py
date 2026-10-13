from datetime import date

import pandas as pd
import pytest

from tools.recover_ekalayava_guide9_paths import _request_plan


def test_request_plan_keeps_only_missing_exact_symbol_sessions():
    coverage = pd.DataFrame([
        {
            "symbol": "NSE-NIFTY-06Jan26-26100-CE",
            "date": "2026-01-01",
            "path_status": "NO_USABLE_POST_ENTRY_PATH",
        },
        {
            "symbol": "NSE-NIFTY-04Aug26-23000-CE",
            "date": "2026-08-03",
            "path_status": "COMPLETE_POST_ENTRY_PATH",
        },
    ])

    assert _request_plan(coverage) == [
        ("NSE-NIFTY-06Jan26-26100-CE", date(2026, 1, 1)),
    ]


def test_request_plan_rejects_non_exact_symbols():
    coverage = pd.DataFrame([{
        "symbol": "NSE-NIFTY-NEIGHBOR-26100-CE",
        "date": "2026-01-01",
        "path_status": "NO_USABLE_POST_ENTRY_PATH",
    }])

    with pytest.raises(ValueError, match="Unexpected exact-contract symbol"):
        _request_plan(coverage)


def test_request_plan_enforces_bounded_request_limit():
    dates = pd.date_range("2026-01-01", periods=254, freq="D")
    coverage = pd.DataFrame([
        {
            "symbol": "NSE-NIFTY-06Jan26-26100-CE",
            "date": trading_date.date().isoformat(),
            "path_status": "NO_USABLE_POST_ENTRY_PATH",
        }
        for trading_date in dates
    ])

    with pytest.raises(ValueError, match="bounded 253-session limit"):
        _request_plan(coverage)
