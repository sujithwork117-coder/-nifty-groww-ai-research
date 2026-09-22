from datetime import timedelta
import pandas as pd
from tenacity import retry,stop_after_attempt,wait_exponential

def _df(payload):
    candles=payload.get("candles",payload) if isinstance(payload,dict) else payload
    rows=[]
    for c in candles or []:
        if len(c)>=5:
            rows.append({"timestamp":pd.to_datetime(c[0],unit="s",utc=True).tz_convert("Asia/Kolkata"),
                         "open":float(c[1]),"high":float(c[2]),"low":float(c[3]),"close":float(c[4]),
                         "volume":float(c[5]) if len(c)>5 and c[5] is not None else None,
                         "oi":float(c[6]) if len(c)>6 and c[6] is not None else None})
    return pd.DataFrame(rows)

@retry(stop=stop_after_attempt(4),wait=wait_exponential(multiplier=1,min=1,max=8))
def _fetch(groww,symbol,start,end,segment):
    return groww.get_historical_candles(exchange=groww.EXCHANGE_NSE,segment=segment,
        groww_symbol=symbol,start_time=start.strftime("%Y-%m-%d %H:%M:%S"),
        end_time=end.strftime("%Y-%m-%d %H:%M:%S"),candle_interval="5minute")

def get_historical(groww,symbol,start,end,chunk_days=14,segment=None):
    segment=segment or groww.SEGMENT_FNO
    out=[]; cur=start
    while cur<end:
        nxt=min(cur+timedelta(days=chunk_days),end)
        try: out.append(_df(_fetch(groww,symbol,cur,nxt,segment)))
        except Exception as e: print("[WARN]",symbol,e)
        cur=nxt
    if not out: return pd.DataFrame(columns=["timestamp","open","high","low","close","volume","oi"])
    return pd.concat(out,ignore_index=True).drop_duplicates("timestamp").sort_values("timestamp").reset_index(drop=True)

def get_expiries(groww,underlying="NIFTY",year=None,month=None):
    kw={"exchange":groww.EXCHANGE_NSE,"underlying_symbol":underlying}
    if year is not None: kw["year"]=year
    if month is not None: kw["month"]=month
    return groww.get_expiries(**kw)

def get_contracts(groww,expiry_date,underlying="NIFTY"):
    return groww.get_contracts(exchange=groww.EXCHANGE_NSE,underlying_symbol=underlying,expiry_date=expiry_date)

def live_quote(groww,trading_symbol):
    return groww.get_quote(exchange=groww.EXCHANGE_NSE,segment=groww.SEGMENT_FNO,trading_symbol=trading_symbol)

def live_ltp(groww,symbols):
    return groww.get_ltp(segment=groww.SEGMENT_FNO,exchange_trading_symbols=tuple(symbols))
