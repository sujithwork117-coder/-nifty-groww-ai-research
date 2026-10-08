"""Candle-by-candle replay through the same engine used for paper observation."""

import pandas as pd

from .paper_engine import PaperContractEngine


def replay_contract_day(candles, contract, config=None):
    """Replay one exact contract-day in timestamp order, one completed bar at a time."""
    frame = candles.copy()
    if frame.empty:
        return {"events": [], "state": None, "candles_processed": 0}
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="raise").dt.tz_convert("Asia/Kolkata")
    frame = frame.sort_values("timestamp", kind="stable")
    days = frame.timestamp.dt.date.unique()
    if len(days) != 1:
        raise ValueError("Replay input must contain exactly one trading date")
    engine = PaperContractEngine(contract, config=config) if config is not None else PaperContractEngine(contract)
    events = []
    for row in frame.to_dict("records"):
        candle = {key: row[key] for key in ("timestamp", "open", "high", "low", "close")}
        candle["completed"] = True
        events.extend(engine.process_candle(candle))
    return {"events": events, "state": engine.snapshot(), "candles_processed": len(frame)}
