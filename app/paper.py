import pandas as pd

from .strategies import level_to_level_events
from .config import CFG
from .journal import append_event
from .safety import ExecutionLock

def simulate_level(df,event):
    d=df[df.timestamp>event.timestamp].sort_values("timestamp")
    result={"exit_time":None,"exit_price":None,"outcome":"OPEN","mfe":0.0,"mae":0.0}
    if not d.empty:
        result["mfe"]=float(d.high.head(78).max()-event.entry)
        result["mae"]=float(d.low.head(78).min()-event.entry)
    for _,r in d.iterrows():
        sl=r.low<=event.sl;tg=r.high>=event.target
        if sl and tg:result.update({"exit_time":r.timestamp,"exit_price":event.sl,"outcome":"AMBIGUOUS_SL_FIRST"});return result
        if sl:result.update({"exit_time":r.timestamp,"exit_price":event.sl,"outcome":"SL"});return result
        if tg:result.update({"exit_time":r.timestamp,"exit_price":event.target,"outcome":"TARGET"});return result
    return result

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
        event_time=pd.to_datetime(row["timestamp"],utc=True).tz_convert("Asia/Kolkata")
        row["entry_hour"]=event_time.hour
        row["entry_minute"]=event_time.minute
        row["before_10"]=event_time.hour<10
        results.append(row)
    return pd.DataFrame(results)

def run_paper_level_to_level(df,contract=None,config=CFG,journal_path=None):
    ExecutionLock(config).assert_paper_only()
    trades=backtest_level_to_level(df,contract,config.level_sl_points,config.level_entry_start,config.level_entry_end)
    for _,trade in trades.iterrows():
        record=trade.to_dict();record["signal"]="LEVEL_TO_LEVEL";record["pnl_points"]=record.get("points_gained_lost")
        record["reason_for_exit"]=record.get("outcome")
        if journal_path:append_event(record,journal_path,config.model_version)
    return trades

def analyze_ekalayava(df,contract=None,start="09:15",end="15:15",horizon_bars=78):
    contract=contract or {}
    events=__import__("app.strategies",fromlist=["ekalayava_events"]).ekalayava_events(df,start,end)
    results=[]
    for _,event in events.iterrows():
        path=simulate_target(df,event,horizon_bars)
        row=event.to_dict()
        row.update({"symbol":contract.get("symbol"),"expiry":contract.get("expiry"),
                    "strike":contract.get("strike"),"option_type":contract.get("option_type"),
                    "itm_rank":contract.get("itm_rank"),"breakout_timestamp":event.timestamp,
                    "confirmation_timestamp":event.timestamp,"target":float(event.opening_high),**path})
        row["points_gained_lost"]=(row["exit_price"]-row["entry"] if row.get("exit_price") is not None else None)
        row["time_to_exit_minutes"]=((row["exit_time"]-row["timestamp"]).total_seconds()/60
                                      if row.get("exit_time") is not None else None)
        event_time=pd.to_datetime(row["timestamp"],utc=True).tz_convert("Asia/Kolkata")
        row["entry_hour"]=event_time.hour;row["entry_minute"]=event_time.minute
        row["before_10"]=event_time.hour<10
        results.append(row)
    return pd.DataFrame(results)

def simulate_target(df,event,horizon_bars=78):
    future=df[df.timestamp>event.timestamp].sort_values("timestamp").head(horizon_bars)
    entry=float(event.entry);target=float(event.opening_high)
    result={"exit_time":None,"exit_price":None,"outcome":"OPEN","mfe":0.0,"mae":0.0}
    if future.empty:return result
    result["mfe"]=float(future.high.max()-entry);result["mae"]=float(future.low.min()-entry)
    for _,row in future.iterrows():
        if row.high>=target:
            result.update({"exit_time":row.timestamp,"exit_price":target,"outcome":"TARGET"})
            break
    return result

def evaluate_paper_signal(candles,signal,horizon_bars=78):
    future=candles[candles.timestamp>pd.Timestamp(signal["timestamp"])].sort_values("timestamp").head(horizon_bars)
    entry=float(signal["entry"]);result={"signal_timestamp":signal["timestamp"],"entry":entry,
            "symbol":signal.get("symbol"),"execution":"DISABLED","mfe":0.0,"mae":0.0,"outcome":"OPEN"}
    if future.empty:return result
    result["mfe"]=float(future.high.max()-entry);result["mae"]=float(future.low.min()-entry)
    for _,row in future.iterrows():
        hit_sl="sl" in signal and row.low<=signal["sl"]
        hit_target="target" in signal and row.high>=signal["target"]
        if hit_sl and hit_target:result["outcome"]="AMBIGUOUS_SL_FIRST";result["exit_timestamp"]=row.timestamp;break
        if hit_sl:result["outcome"]="SL";result["exit_timestamp"]=row.timestamp;break
        if hit_target:result["outcome"]="TARGET";result["exit_timestamp"]=row.timestamp;break
    return result
def simulate_path(df,event,horizon_bars=78):
    d=df[df.timestamp>event.timestamp].sort_values("timestamp").head(horizon_bars);entry=float(event.entry)
    if d.empty:return {"mfe":0.0,"mae":0.0}
    return {"mfe":float(d.high.max()-entry),"mae":float(d.low.min()-entry)}
