import pandas as pd

from .strategies import level_to_level_events
from .config import CFG
from .journal import append_event
from .safety import ExecutionLock

def _same_day_future(df,event,horizon_bars=78):
    timestamps=pd.to_datetime(df.timestamp,utc=True)
    value=event.get("timestamp") if isinstance(event,dict) else event.timestamp
    entry_timestamp=pd.to_datetime(value,utc=True)
    entry_date=entry_timestamp.tz_convert("Asia/Kolkata").date()
    local_dates=timestamps.dt.tz_convert("Asia/Kolkata").dt.date
    return df.loc[(timestamps>entry_timestamp)&(local_dates==entry_date)].sort_values("timestamp").head(horizon_bars)

def simulate_level(df,event):
    if float(event.entry)<=float(event.sl):
        return {"exit_time":None,"exit_price":None,"outcome":"SKIPPED_SL_ALREADY_BREACHED",
                "mfe":0.0,"mae":0.0,"intrabar_ambiguous":False,
                "skip_reason":"entry close is at or below the configured stop-loss"}
    d=_same_day_future(df,event)
    result={"exit_time":None,"exit_price":None,"outcome":"OPEN","mfe":0.0,"mae":0.0,
            "intrabar_ambiguous":False}
    path=[]
    for _,r in d.iterrows():
        path.append(r)
        sl=r.low<=event.sl;tg=r.high>=event.target
        if sl and tg:result.update({"exit_time":r.timestamp,"exit_price":None,"outcome":"AMBIGUOUS",
                                    "intrabar_ambiguous":True});break
        if sl:result.update({"exit_time":r.timestamp,"exit_price":event.sl,"outcome":"SL"});break
        if tg:result.update({"exit_time":r.timestamp,"exit_price":event.target,"outcome":"TARGET"});break
    if path:
        observed=pd.DataFrame(path)
        result["mfe"]=float(observed.high.max()-event.entry)
        result["mae"]=float(observed.low.min()-event.entry)
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
        row["points_gained_lost"]=(row["exit_price"]-row["entry"]
                                    if row["exit_price"] is not None and row["outcome"]!="SKIPPED_SL_ALREADY_BREACHED" else None)
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
    candles=df.copy()
    candles["timestamp"]=pd.to_datetime(candles.timestamp,utc=True)
    results=[]
    for _,event in events.iterrows():
        path=simulate_target(df,event,horizon_bars)
        event_time=pd.to_datetime(event.timestamp,utc=True)
        breakdown_time=pd.to_datetime(event.breakdown_timestamp,utc=True)
        same_day=candles[candles.timestamp.dt.tz_convert("Asia/Kolkata").dt.date==
                         event_time.tz_convert("Asia/Kolkata").date()]
        pre_entry=same_day[(same_day.timestamp>=breakdown_time)&(same_day.timestamp<=event_time)]
        entry_bar=same_day[same_day.timestamp==event_time]
        future=_same_day_future(candles,event,horizon_bars)
        structure_low=None;structure_low_time=None;breakout_low=None
        if not pre_entry.empty:
            structure_index=pre_entry.low.astype(float).idxmin()
            structure_low=float(pre_entry.loc[structure_index,"low"])
            structure_low_time=pre_entry.loc[structure_index,"timestamp"]
        if not entry_bar.empty:
            breakout_low=float(entry_bar.iloc[0].low)
        future_lows=pd.to_numeric(future.low,errors="coerce") if not future.empty else pd.Series(dtype=float)
        row=event.to_dict()
        row.update({"symbol":contract.get("symbol"),"expiry":contract.get("expiry"),
                    "strike":contract.get("strike"),"option_type":contract.get("option_type"),
                    "itm_rank":contract.get("itm_rank"),"breakout_timestamp":event.timestamp,
                    "confirmation_timestamp":event.timestamp,"target":float(event.opening_high),**path,
                    "observed_reversal_structure_low":structure_low,
                    "observed_reversal_structure_low_time":structure_low_time,
                    "structure_low_measurement":"minimum low from first opening-low break through the completed entry candle; descriptive only",
                    "breakout_candle_low":breakout_low,
                    "reversal_structure_low_revisited":bool(not future_lows.empty and structure_low is not None and (future_lows<=structure_low).any()),
                    "breakout_candle_low_revisited":bool(not future_lows.empty and breakout_low is not None and (future_lows<=breakout_low).any()),
                    "opening_low_revisited":bool(not future_lows.empty and (future_lows<=float(event.opening_low)).any())})
        # Ekalayava's opening-high touch is an observation, not a defined exit.
        # Never encode target distance as realized P&L or target time as holding time.
        row["points_gained_lost"] = None
        row["time_to_exit_minutes"] = None
        row["structural_sl_status"] = "UNDEFINED_REQUIRES_RULE"
        event_time=pd.to_datetime(row["timestamp"],utc=True).tz_convert("Asia/Kolkata")
        row["entry_hour"]=event_time.hour;row["entry_minute"]=event_time.minute
        row["before_10"]=event_time.hour<10
        results.append(row)
    return pd.DataFrame(results)

def simulate_target(df,event,horizon_bars=78):
    future=_same_day_future(df,event,horizon_bars)
    entry=float(event.entry);target=float(event.opening_high)
    result={"exit_time":None,"exit_price":None,"outcome":"OPEN","target_touched":False,
            "target_touch_time":None,"time_to_target_minutes":None,"mfe":0.0,"mae":0.0,
            "time_to_mfe_minutes":None,"time_to_mae_minutes":None,
            "observation_end_time":None,"observation_bars":0}
    if future.empty:return result
    path=[]
    for _,row in future.iterrows():
        path.append(row)
        if not result["target_touched"] and row.high>=target:
            result.update({"outcome":"TARGET_TOUCH","target_touched":True,
                           "target_touch_time":row.timestamp,
                           "time_to_target_minutes":(row.timestamp-event.timestamp).total_seconds()/60})
    observed=pd.DataFrame(path)
    if not observed.empty:
        max_high=pd.to_numeric(observed.high,errors="coerce").max()
        min_low=pd.to_numeric(observed.low,errors="coerce").min()
        max_row=observed.loc[pd.to_numeric(observed.high,errors="coerce")==max_high].iloc[0]
        min_row=observed.loc[pd.to_numeric(observed.low,errors="coerce")==min_low].iloc[0]
        result.update({"mfe":float(max_high-entry),"mae":float(min_low-entry),
                       "time_to_mfe_minutes":(max_row.timestamp-event.timestamp).total_seconds()/60,
                       "time_to_mae_minutes":(min_row.timestamp-event.timestamp).total_seconds()/60,
                       "observation_end_time":observed.iloc[-1].timestamp,
                       "observation_bars":len(observed)})
    return result

def evaluate_paper_signal(candles,signal,horizon_bars=78):
    future=_same_day_future(candles,signal,horizon_bars)
    entry=float(signal["entry"]);result={"signal_timestamp":signal["timestamp"],"entry":entry,
            "symbol":signal.get("symbol"),"execution":"DISABLED","mfe":0.0,"mae":0.0,"outcome":"OPEN"}
    if future.empty:return result
    path=[]
    for _,row in future.iterrows():
        path.append(row)
        hit_sl="sl" in signal and row.low<=signal["sl"]
        hit_target="target" in signal and row.high>=signal["target"]
        if hit_sl and hit_target:result["outcome"]="AMBIGUOUS";result["exit_timestamp"]=row.timestamp;break
        if hit_sl:result["outcome"]="SL";result["exit_timestamp"]=row.timestamp;break
        if hit_target:result["outcome"]="TARGET";result["exit_timestamp"]=row.timestamp;break
    observed=pd.DataFrame(path)
    if not observed.empty:
        result["mfe"]=float(observed.high.max()-entry);result["mae"]=float(observed.low.min()-entry)
    return result
def simulate_path(df,event,horizon_bars=78):
    d=_same_day_future(df,event,horizon_bars);entry=float(event.entry)
    if d.empty:return {"mfe":0.0,"mae":0.0}
    return {"mfe":float(d.high.max()-entry),"mae":float(d.low.min()-entry)}
