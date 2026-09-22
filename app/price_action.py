import pandas as pd
def classify_candle(r):
    rng=r["range"]
    if not rng or pd.isna(rng): return "unknown"
    body=abs(r.close-r.open)/rng; uw=r.upper_wick/rng; lw=r.lower_wick/rng
    if body<.20 and uw>.35 and lw>.35:return "indecision"
    if lw>.45 and body<.45:return "lower_rejection"
    if uw>.45 and body<.45:return "upper_rejection"
    if r.green and body>=.65:return "strong_green"
    if r.red and body>=.65:return "strong_red"
    return "normal"
def add_price_action(df):
    x=df.copy();x["candle_type"]=x.apply(classify_candle,axis=1);return x
