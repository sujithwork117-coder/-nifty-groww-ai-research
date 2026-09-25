import numpy as np
import pandas as pd
def add_features(df):
    x=df.copy().sort_values("timestamp").reset_index(drop=True)
    x["body"]=x.close-x.open;x["range"]=x.high-x.low;x["body_abs"]=x.body.abs()
    x["upper_wick"]=x.high-x[["open","close"]].max(axis=1)
    x["lower_wick"]=x[["open","close"]].min(axis=1)-x.low
    x["green"]=x.close>x.open;x["red"]=x.close<x.open
    x["return_1"]=x.close.pct_change();x["return_3"]=x.close.pct_change(3)
    x["range_pct"]=x["range"]/x.close.replace(0,np.nan)
    x["volatility_10"]=x.return_1.rolling(10).std()
    x["ema9"]=x.close.ewm(span=9,adjust=False).mean()
    x["ema21"]=x.close.ewm(span=21,adjust=False).mean()
    if "volume" in x:x["volume_change"]=x.volume.pct_change(fill_method=None)
    if "oi" in x:x["oi_change"]=x.oi.diff()
    return x
def add_opening_levels(df):
    x=df.copy(); local=x.timestamp.dt.tz_convert("Asia/Kolkata")
    x["date"]=local.dt.date;x["time"]=local.dt.strftime("%H:%M")
    op=x[local.dt.strftime("%H:%M")=="09:15"][["date","high","low"]].rename(columns={"high":"opening_high","low":"opening_low"})
    x=x.merge(op,on="date",how="left")
    x["below_opening_low"]=x.low<x.opening_low;x["above_opening_high"]=x.high>x.opening_high
    return x
