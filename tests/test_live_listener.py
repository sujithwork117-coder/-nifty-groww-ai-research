from types import SimpleNamespace

from app.live_listener import completed_5m_candle,paper_signal


def test_completed_candle_aggregates_ticks():
    ticks=[
        {"timestamp":"2026-09-01T09:15:01Z","price":100},
        {"timestamp":"2026-09-01T09:17:00Z","price":98},
        {"timestamp":"2026-09-01T09:19:59Z","price":102},
    ]

    candle=completed_5m_candle(ticks)

    assert candle["open"]==100
    assert candle["high"]==102
    assert candle["low"]==98
    assert candle["close"]==102


def test_paper_signal_has_execution_disabled():
    config=SimpleNamespace(execution_allowed=False,paper_only=True,kill_switch=False)
    candle={"timestamp":"2026-09-01T09:20:00+05:30","open":100,"high":103,"low":98,"close":102}

    signal=paper_signal(candle,103,99,config=config)

    assert signal["execution"]=="DISABLED"
    assert signal["paper_only"] is True
    assert signal["sl"]==95