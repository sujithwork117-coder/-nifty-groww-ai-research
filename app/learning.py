import json
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
def enrich_events(events,candles):
    rows=[]
    for _,e in events.iterrows():
        d=candles[candles.date.astype(str)==str(e.date)].sort_values("timestamp");f=d[d.timestamp>e.timestamp].head(78)
        if f.empty:continue
        r=e.to_dict();entry_rows=d[d.timestamp==e.timestamp]
        entry=entry_rows.iloc[0] if not entry_rows.empty else None
        r.update({"mfe":float(f.high.max()-e.entry),"mae":float(f.low.min()-e.entry),
            "entry_hour":e.timestamp.hour,"entry_minute":e.timestamp.minute,
            "entry_before_10":e.timestamp.hour<10,"entry_after_10":e.timestamp.hour>=10,
            "weekday":e.timestamp.weekday()})
        if entry is not None:
            for field in ("volatility_10","premium_change","candle_type","lower_wick","upper_wick","range"):
                if field in entry:r[field]=entry[field]
            r["rejection_characteristic"]=entry.get("candle_type")
            r["breakout_characteristic"]=bool(entry.get("above_opening_high",False))
        if "target" in e and pd.notna(e.get("target")):
            outcome="OPEN"
            exit_time=None
            for _,z in f.iterrows():
                sl=z.low<=e.sl;tg=z.high>=e.target
                if sl and tg:outcome="AMBIGUOUS_SL_FIRST";exit_time=z.timestamp;break
                if sl:outcome="SL";exit_time=z.timestamp;break
                if tg:outcome="TARGET";exit_time=z.timestamp;break
            r.update({"outcome":outcome,"false_breakout":outcome in ("SL","AMBIGUOUS_SL_FIRST"),
                      "time_to_target_minutes":((exit_time-e.timestamp).total_seconds()/60 if outcome=="TARGET" else None)})
        rows.append(r)
    return pd.DataFrame(rows)
def split_time(events,frac=.70):
    x=events.sort_values("timestamp").reset_index(drop=True);cut=int(len(x)*frac);return x.iloc[:cut].copy(),x.iloc[cut:].copy()
def build_report(events):
    if events.empty:return {"events":0,"message":"No qualifying events found."}
    tr,va=split_time(events)
    def stats(d):
        o={"n":int(len(d))}
        if "outcome" in d:o.update(target_rate=float((d.outcome=="TARGET").mean()),sl_rate=float(d.outcome.isin(["SL","AMBIGUOUS_SL_FIRST"]).mean()))
        o.update(avg_mfe=float(d.mfe.mean()),avg_mae=float(d.mae.mean()))
        return o
    clf={"enabled":False}
    cols=[c for c in ["mfe","mae","entry_hour","entry_minute","entry_before_10"] if c in tr]
    if "outcome" in tr and len(tr)>=30 and tr.outcome.nunique()>1 and len(va)>=10:
        m=RandomForestClassifier(n_estimators=200,random_state=42,min_samples_leaf=5,class_weight="balanced")
        m.fit(tr[cols],tr.outcome.astype(str));pred=m.predict(va[cols])
        clf={"enabled":True,"features":cols,"validation_accuracy":float(accuracy_score(va.outcome.astype(str),pred))}
    return {"events":len(events),"date_min":str(events.date.min()),"date_max":str(events.date.max()),
            "train":stats(tr),"validation":stats(va),"classifier":clf,
            "anti_overfit":"Chronological validation; validation data is not used for fitting."}

def setup_quality_report(events):
    if events.empty:return {"events":0,"groups":{}}
    dimensions=["entry_before_10","option_type","itm_rank","entry_hour","weekday",
                "volatility_10","premium_change","candle_type","rejection_characteristic",
                "false_breakout"]
    groups={}
    for dimension in dimensions:
        if dimension not in events:continue
        grouped=[]
        for value,subset in events.groupby(dimension,dropna=False):
            row={"value":None if pd.isna(value) else str(value),"n":int(len(subset)),
                 "avg_mfe":float(subset.mfe.mean()) if "mfe" in subset else None,
                 "avg_mae":float(subset.mae.mean()) if "mae" in subset else None}
            if "outcome" in subset:row["target_rate"]=float((subset.outcome=="TARGET").mean())
            if "time_to_target_minutes" in subset:row["avg_time_to_target_minutes"]=float(subset.time_to_target_minutes.mean())
            grouped.append(row)
        groups[dimension]=grouped
    return {"events":int(len(events)),"groups":groups,
            "note":"Factual historical distributions; no composite setup score or profitability claim."}
def save_report(report,path):
    Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_text(json.dumps(report,indent=2,default=str))
