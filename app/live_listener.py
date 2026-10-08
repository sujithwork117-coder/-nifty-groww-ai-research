"""Read-only live observation primitives; no order APIs are used here."""

from datetime import date, datetime, time
from zoneinfo import ZoneInfo
import time as sleep_time

from .candle_builder import FiveMinuteCandleBuilder, completed_5m_candle
from .config import CFG
from .contract_selection import select_daily_itm_contracts
from .paper_engine import PaperContractEngine
from .safety import ExecutionLock

IST = ZoneInfo("Asia/Kolkata")


def paper_signal(candle, engine, nifty_price=None):
    """Forward one finalized candle into the stateful paper-only engine."""
    ExecutionLock(engine.config).assert_paper_only()
    if candle.get("completed") is not True:
        raise ValueError("paper_signal accepts only a finalized 5-minute candle")
    return engine.process_candle(candle, nifty_price=nifty_price)


def select_live_contracts(groww, opening_candle, trading_date=None):
    """Select today's exact catalog contracts from the completed 09:15 NIFTY bar."""
    if opening_candle.get("completed") is not True:
        raise ValueError("Daily contracts require the completed NIFTY opening candle")
    import pandas as pd
    stamp = pd.Timestamp(opening_candle["timestamp"])
    local = stamp.tz_localize(IST) if stamp.tzinfo is None else stamp.tz_convert(IST)
    if local.strftime("%H:%M") != "09:15":
        raise ValueError("Daily contract selection requires the NIFTY 09:15 candle")
    if "close_time" in opening_candle:
        close_time = pd.Timestamp(opening_candle["close_time"])
        close_time = close_time.tz_localize(IST) if close_time.tzinfo is None else close_time.tz_convert(IST)
        if close_time != local + pd.Timedelta(minutes=5):
            raise ValueError("NIFTY opening candle has not closed at its correct five-minute boundary")
    day = date.fromisoformat(trading_date) if isinstance(trading_date, str) else trading_date or local.date()
    if day != local.date():
        raise ValueError("Requested contract date must match the 09:15 NIFTY candle date")
    return select_daily_itm_contracts(groww, opening_candle["open"], day)


def market_open_now(now=None):
    current = now or datetime.now(IST)
    if current.tzinfo is None:
        current = current.replace(tzinfo=IST)
    current = current.astimezone(IST)
    return current.weekday() < 5 and time(9, 15) <= current.time().replace(tzinfo=None) < time(15, 30)


def observe_ltp(groww, symbols, poll_seconds=5, on_tick=None, stop_requested=None):
    """Read LTPs only. Caller owns candle builders and must resume from persisted state."""
    ExecutionLock(CFG).assert_paper_only()
    ltp_symbols = tuple(symbol.replace("-", "_").upper() for symbol in symbols)
    while market_open_now() and not (stop_requested and stop_requested()):
        try:
            payload = groww.get_ltp(segment=groww.SEGMENT_FNO,
                                    exchange_trading_symbols=ltp_symbols)
            tick = {"timestamp": datetime.now(IST).isoformat(), "ltp": payload}
            if on_tick:
                on_tick(tick)
        except Exception as error:
            # No synthetic tick or candle is produced after a failure.
            if on_tick:
                on_tick({"event": "DATA_ERROR", "timestamp": datetime.now(IST).isoformat(),
                         "error_type": type(error).__name__})
        sleep_time.sleep(poll_seconds)


__all__ = ["FiveMinuteCandleBuilder", "PaperContractEngine", "completed_5m_candle",
           "market_open_now", "observe_ltp", "paper_signal", "select_live_contracts"]
