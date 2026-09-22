from datetime import datetime
from zoneinfo import ZoneInfo
import time
from .safety import ExecutionLock
from .config import CFG
IST=ZoneInfo("Asia/Kolkata")
def market_open_now():
    n=datetime.now(IST)
    return n.weekday()<5 and "09:15"<=n.strftime("%H:%M")<="15:30"
def observe_ltp(groww,symbols,poll_seconds=5,on_tick=None):
    ExecutionLock(CFG).assert_paper_only()
    while market_open_now():
        try:
            payload=groww.get_ltp(segment=groww.SEGMENT_FNO,exchange_trading_symbols=tuple(symbols))
            tick={"ts":datetime.now(IST).isoformat(),"ltp":payload}
            if on_tick:on_tick(tick)
        except Exception as e:print("[LIVE WARN]",e)
        time.sleep(poll_seconds)
