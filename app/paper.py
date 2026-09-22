import pandas as pd

from .strategies import level_to_level_events

def simulate_level(df,event):
    d=df[df.timestamp>event.timestamp].sort_values("timestamp")
    for _,r in d.iterrows():
        sl=r.low<=event.sl;tg=r.high>=event.target
        if sl and tg:return {"exit_time":r.timestamp,"exit_price":event.sl,"outcome":"AMBIGUOUS_SL_FIRST"}
        if sl:return {"exit_time":r.timestamp,"exit_price":event.sl,"outcome":"SL"}
        if tg:return {"exit_time":r.timestamp,"exit_price":event.target,"outcome":"TARGET"}
    return {"exit_time":None,"exit_price":None,"outcome":"OPEN"}

def backtest_level_to_level(df,contract=None,sl_points=4,start="09:15",end="11:00"):
    contract=contract or {}
    events=level_to_level_events(df,sl_points,start,end)
    results=[]
    for _,event in events.iterrows():
        result=simulate_level(df,event)
        row=event.to_dict()
        row.update({"symbol":contract.get("symbol"),"expiry":contract.get("expiry"),
                    "strike":contract.get("strike"),"option_type":contract.get("option_type"),
                    "itm_rank":contract.get("itm_rank"),**result})
        row["points_gained_lost"]=(row["exit_price"]-row["entry"] if row["exit_price"] is not None else None)
        row["time_to_exit_minutes"]=(
            (row["exit_time"]-row["timestamp"]).total_seconds()/60
            if row["exit_time"] is not None else None
        )
        row["entry_hour"]=row["timestamp"].hour
        row["entry_minute"]=row["timestamp"].minute
        row["before_10"]=row["timestamp"].hour<10
        results.append(row)
    return pd.DataFrame(results)
def simulate_path(df,event,horizon_bars=78):
    d=df[df.timestamp>event.timestamp].sort_values("timestamp").head(horizon_bars);entry=float(event.entry)
    if d.empty:return {"mfe":0.0,"mae":0.0}
    return {"mfe":float(d.high.max()-entry),"mae":float(d.low.min()-entry)}
