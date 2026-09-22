from datetime import timedelta
from pathlib import Path
import re
import pandas as pd
from tenacity import retry,stop_after_attempt,wait_exponential

OHLC_COLUMNS=["open","high","low","close"]
DATA_COLUMNS=["timestamp",*OHLC_COLUMNS,"volume","oi"]

def _groww_symbol(exchange,symbol):
    return symbol if "-" in symbol else f"{exchange}-{symbol}"

def _parse_timestamp(value):
    if isinstance(value,(int,float)):
        return pd.to_datetime(value,unit="s",utc=True).tz_convert("Asia/Kolkata")
    parsed=pd.to_datetime(value)
    if parsed.tzinfo is None:
        return parsed.tz_localize("Asia/Kolkata")
    return parsed.tz_convert("Asia/Kolkata")

def _df(payload):
    candles=payload.get("candles",payload) if isinstance(payload,dict) else payload
    rows=[]
    for c in candles or []:
        if len(c)>=5:
            rows.append({"timestamp":_parse_timestamp(c[0]),
                         "open":float(c[1]),"high":float(c[2]),"low":float(c[3]),"close":float(c[4]),
                         "volume":float(c[5]) if len(c)>5 and c[5] is not None else None,
                         "oi":float(c[6]) if len(c)>6 and c[6] is not None else None})
    return pd.DataFrame(rows,columns=DATA_COLUMNS)

def validate_candles(df):
    missing=[column for column in DATA_COLUMNS if column not in df]
    if missing: raise ValueError(f"Missing candle columns: {', '.join(missing)}")
    x=df.copy()
    x["timestamp"]=pd.to_datetime(x["timestamp"],utc=True,errors="coerce")
    if x["timestamp"].isna().any(): raise ValueError("Invalid candle timestamp")
    if x["timestamp"].duplicated().any(): raise ValueError("Duplicate candle timestamp")
    for column in OHLC_COLUMNS:
        x[column]=pd.to_numeric(x[column],errors="coerce")
    if x[OHLC_COLUMNS].isna().any().any(): raise ValueError("Invalid OHLC value")
    if ((x["low"]>x["high"]) | (x["open"]<x["low"]) | (x["open"]>x["high"]) |
        (x["close"]<x["low"]) | (x["close"]>x["high"])).any():
        raise ValueError("OHLC values are inconsistent")
    x=x.sort_values("timestamp").reset_index(drop=True)
    if not x["timestamp"].is_monotonic_increasing: raise ValueError("Candles are not chronological")
    return x[DATA_COLUMNS]

@retry(stop=stop_after_attempt(4),wait=wait_exponential(multiplier=1,min=1,max=8))
def _fetch(groww,symbol,start,end,segment):
    return groww.get_historical_candles(exchange=groww.EXCHANGE_NSE,segment=segment,
        groww_symbol=_groww_symbol(groww.EXCHANGE_NSE,symbol),start_time=start.strftime("%Y-%m-%d %H:%M:%S"),
        end_time=end.strftime("%Y-%m-%d %H:%M:%S"),candle_interval="5minute")

def get_historical(groww,symbol,start,end,chunk_days=14,segment=None):
    segment=segment or groww.SEGMENT_FNO
    out=[]; cur=start
    while cur<end:
        nxt=min(cur+timedelta(days=chunk_days),end)
        try: out.append(_df(_fetch(groww,symbol,cur,nxt,segment)))
        except Exception as e: print("[WARN]",symbol,e)
        cur=nxt
    if not out: return pd.DataFrame(columns=DATA_COLUMNS)
    merged=pd.concat(out,ignore_index=True).drop_duplicates("timestamp")
    return validate_candles(merged)

def save_historical(df,path):
    validated=validate_candles(df)
    destination=Path(path)
    destination.parent.mkdir(parents=True,exist_ok=True)
    validated.to_csv(destination,index=False)
    return destination

def save_option_historical(groww,contracts,start,end,output_dir="data/raw/options",chunk_days=14):
    output=Path(output_dir);output.mkdir(parents=True,exist_ok=True);saved=[]
    for contract in contracts:
        candles=get_historical(groww,contract["symbol"],start,end,chunk_days,groww.SEGMENT_FNO)
        for field in ("underlying","expiry","strike","option_type","itm_rank"):
            candles[field]=contract.get(field)
        filename=re.sub(r"[^A-Za-z0-9_.-]+","_",contract["symbol"])+".csv"
        destination=output/filename
        candles.to_csv(destination,index=False)
        saved.append(destination)
    return saved

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
    ltp_symbols=tuple(symbol.replace("-","_").upper() for symbol in symbols)
    return groww.get_ltp(segment=groww.SEGMENT_FNO,exchange_trading_symbols=ltp_symbols)
