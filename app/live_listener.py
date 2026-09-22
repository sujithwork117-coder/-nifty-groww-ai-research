from datetime import datetime
from zoneinfo import ZoneInfo
import time
import pandas as pd
from .safety import ExecutionLock
from .config import CFG
IST=ZoneInfo("Asia/Kolkata")

def completed_5m_candle(ticks):
    frame=pd.DataFrame(ticks)
    if frame.empty:return None
    frame["timestamp"]=pd.to_datetime(frame["timestamp"],utc=True)
    frame=frame.sort_values("timestamp")
    bucket=frame.timestamp.dt.floor("5min")
    group=frame.groupby(bucket,sort=True).agg(open=("price","first"),high=("price","max"),low=("price","min"),close=("price","last"),timestamp=("timestamp","max"))
    if group.empty:return None
    row=group.iloc[-1].to_dict();row["timestamp"]=row["timestamp"].tz_convert(IST)
    return row

def paper_signal(candle,opening_high,opening_low,sl_points=4,config=CFG):
    ExecutionLock(config).assert_paper_only()
    if candle["low"]<opening_low and candle["close"]>candle["open"]:
        return {"strategy":"LEVEL_TO_LEVEL","timestamp":candle["timestamp"],"entry":candle["close"],
                "sl":opening_low-sl_points,"target":opening_high,"execution":"DISABLED","paper_only":True}
    return None

def market_open_now():
    n=datetime.now(IST)
    return n.weekday()<5 and "09:15"<=n.strftime("%H:%M")<="15:30"
def observe_ltp(groww,symbols,poll_seconds=5,on_tick=None):
    ExecutionLock(CFG).assert_paper_only()
    ltp_symbols=tuple(symbol.replace("-","_").upper() for symbol in symbols)
    while market_open_now():
        try:
            payload=groww.get_ltp(segment=groww.SEGMENT_FNO,exchange_trading_symbols=ltp_symbols)
            tick={"ts":datetime.now(IST).isoformat(),"ltp":payload}
            if on_tick:on_tick(tick)
        except Exception as e:print("[LIVE WARN]",e)
        time.sleep(poll_seconds)
