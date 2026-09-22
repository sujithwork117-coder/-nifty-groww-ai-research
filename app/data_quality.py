import pandas as pd

OHLC=("open","high","low","close")

def _invalid_ohlc(df):
    values=df[list(OHLC)].apply(pd.to_numeric,errors="coerce")
    return values.isna().any(axis=1) | (values.low>values.high) | (values.open<values.low) | (values.open>values.high) | (values.close<values.low) | (values.close>values.high)

def quality_report(df,interval_minutes=5,contract_column=None):
    x=df.copy()
    timestamps=pd.to_datetime(x.get("timestamp"),utc=True,errors="coerce")
    valid=x.loc[timestamps.notna()].copy()
    valid["timestamp"]=timestamps[timestamps.notna()]
    duplicate_count=int(valid["timestamp"].duplicated().sum())
    invalid_ohlc_count=int(_invalid_ohlc(valid).sum()) if all(column in valid for column in OHLC) else len(valid)
    ordered=valid.sort_values("timestamp")
    gaps=ordered["timestamp"].diff().dropna()
    interval_seconds=interval_minutes*60
    missing_intervals=int(((gaps.dt.total_seconds()/interval_seconds).round()-1).clip(lower=0).sum())
    local_dates=ordered["timestamp"].dt.tz_convert("Asia/Kolkata").dt.date
    report={"total_candles":int(len(x)),"trading_dates":sorted({str(value) for value in local_dates}),
            "missing_intervals":missing_intervals,"duplicate_count":duplicate_count,
            "invalid_ohlc_count":invalid_ohlc_count,"contract_count":0,"date_min":None,"date_max":None}
    if not ordered.empty:
        report["date_min"]=str(ordered.timestamp.min())
        report["date_max"]=str(ordered.timestamp.max())
    if contract_column and contract_column in x:
        report["contract_count"]=int(x[contract_column].nunique(dropna=True))
    return report

def align_candles(underlying,option):
    left=underlying.copy();right=option.copy()
    left["timestamp"]=pd.to_datetime(left["timestamp"],utc=True,errors="raise")
    right["timestamp"]=pd.to_datetime(right["timestamp"],utc=True,errors="raise")
    left=left.rename(columns={column:f"underlying_{column}" for column in left.columns if column!="timestamp"})
    right=right.rename(columns={column:f"option_{column}" for column in right.columns if column!="timestamp"})
    return left.merge(right,on="timestamp",how="outer",sort=True,indicator="candle_presence")