def simulate_level(df,event):
    d=df[df.timestamp>event.timestamp].sort_values("timestamp")
    for _,r in d.iterrows():
        sl=r.low<=event.sl;tg=r.high>=event.target
        if sl and tg:return {"exit_time":r.timestamp,"exit_price":event.sl,"outcome":"AMBIGUOUS_SL_FIRST"}
        if sl:return {"exit_time":r.timestamp,"exit_price":event.sl,"outcome":"SL"}
        if tg:return {"exit_time":r.timestamp,"exit_price":event.target,"outcome":"TARGET"}
    return {"exit_time":None,"exit_price":None,"outcome":"OPEN"}
def simulate_path(df,event,horizon_bars=78):
    d=df[df.timestamp>event.timestamp].sort_values("timestamp").head(horizon_bars);entry=float(event.entry)
    if d.empty:return {"mfe":0.0,"mae":0.0}
    return {"mfe":float(d.high.max()-entry),"mae":float(d.low.min()-entry)}
