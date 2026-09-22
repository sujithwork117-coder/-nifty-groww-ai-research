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
    cols=[c for c in ["entry_hour","entry_minute","entry_before_10","entry_after_10","weekday",
                      "volatility_10","premium_change","lower_wick","upper_wick","range"] if c in tr]
    if "outcome" in tr and len(tr)>=30 and tr.outcome.nunique()>1 and len(va)>=10:
        m=RandomForestClassifier(n_estimators=200,random_state=42,min_samples_leaf=5,class_weight="balanced")
        train_features=tr[cols].apply(pd.to_numeric,errors="coerce").fillna(0)
        validation_features=va[cols].apply(pd.to_numeric,errors="coerce").fillna(0)
        m.fit(train_features,tr.outcome.astype(str));pred=m.predict(validation_features)
        clf={"enabled":True,"features":cols,"validation_accuracy":float(accuracy_score(va.outcome.astype(str),pred))}
    date_values=events["date"] if "date" in events else events["timestamp"]
    return {"events":len(events),"date_min":str(date_values.min()),"date_max":str(date_values.max()),
            "train":stats(tr),"validation":stats(va),"classifier":clf,
            "anti_overfit":"Chronological validation; validation data is not used for fitting."}

def anti_overfit_report(events,model_version="v001",min_train=30,min_validation=10):
    train,validation=split_time(events)
    feature_set=[column for column in ("entry_hour","entry_minute","entry_before_10","entry_after_10","weekday",
                                       "volatility_10","premium_change","lower_wick","upper_wick","range") if column in events]
    return {"model_version":model_version,"sample_size":int(len(events)),"training_statistics":{"n":int(len(train))},
            "validation_statistics":{"n":int(len(validation))},"feature_set":feature_set,
            "date_range":{"min":str(events.timestamp.min()) if not events.empty else None,
                           "max":str(events.timestamp.max()) if not events.empty else None},
            "insufficient_samples":len(train)<min_train or len(validation)<min_validation,
            "chronological_split":True,"future_features_excluded":not any(column in feature_set for column in ("mfe","mae"))}

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

def build_research_report(events,data_quality=None):
    x=events.copy()
    report={"total_setups":int(len(x)),"data_quality":data_quality or {}}
    if x.empty:return report
    if "outcome" in x:
        report.update({"valid_setups":int((x.outcome!="OPEN").sum()),
                       "skipped_setups":int((x.outcome=="OPEN").sum()),
                       "ambiguous_setups":int((x.outcome=="AMBIGUOUS_SL_FIRST").sum()),
                       "target_hits":int((x.outcome=="TARGET").sum()),
                       "sl_hits":int(x.outcome.isin(["SL","AMBIGUOUS_SL_FIRST"]).sum())})
    else:report["valid_setups"]=int(len(x))
    for source,target in (("points_gained_lost","average_points"),("mfe","maximum_favorable_excursion"),
                          ("mae","maximum_adverse_excursion"),("time_to_exit_minutes","average_holding_time_minutes")):
        if source in x:
            values=pd.to_numeric(x[source],errors="coerce").dropna()
            if not values.empty:
                if target.startswith("average"):report[target]=float(values.mean())
                elif target=="maximum_adverse_excursion":report[target]=float(values.min())
                elif target.endswith("excursion"):report[target]=float(values.max())
    if "points_gained_lost" in x:
        values=pd.to_numeric(x.points_gained_lost,errors="coerce").dropna()
        if not values.empty:report["median_points"]=float(values.median())
    for dimension in ("entry_hour","entry_before_10","option_type","itm_rank","strategy","false_breakout"):
        if dimension in x:report[f"{dimension}_distribution"]={str(k):int(v) for k,v in x[dimension].value_counts(dropna=False).items()}
    report["setup_quality"]=setup_quality_report(x)
    return report
def save_report(report,path):
    Path(path).parent.mkdir(parents=True,exist_ok=True);Path(path).write_text(json.dumps(report,indent=2,default=str))
