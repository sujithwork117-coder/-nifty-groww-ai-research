from .features import add_features,add_opening_levels
from .price_action import add_price_action
from .premium_swing import premium_features
def prepare(df):
    return premium_features(add_price_action(add_opening_levels(add_features(df))))
def level_to_level_events(df,sl_points=4,start="09:15",end="11:00"):
    x=prepare(df);events=[]
    for date,d in x.groupby("date"):
        d=d.sort_values("timestamp").reset_index(drop=True)
        if d.empty or d.opening_high.isna().all():continue
        armed=False;entered=False
        for _,r in d.iterrows():
            if r.time<start or r.time>end:continue
            if not armed and r.low<r.opening_low:armed=True;continue
            if armed and not entered and r.green:
                events.append({"date":str(date),"timestamp":r.timestamp,"strategy":"LEVEL_TO_LEVEL",
                    "entry":float(r.close),"sl":float(r.opening_low-sl_points),"target":float(r.opening_high),
                    "opening_high":float(r.opening_high),"opening_low":float(r.opening_low),"candle_type":r.candle_type})
                entered=True
    return __import__("pandas").DataFrame(events)
def ekalayava_events(df,start="09:15",end="15:15"):
    x=prepare(df);events=[]
    for date,d in x.groupby("date"):
        d=d.sort_values("timestamp").reset_index(drop=True)
        if d.empty or d.opening_high.isna().all():continue
        swing_seen=None
        for _,r in d.iterrows():
            if r.time<start or r.time>end:continue
            if r.swing_high:swing_seen=float(r.high)
            if swing_seen is not None and r.high>swing_seen and r.close>r.opening_high:
                events.append({"date":str(date),"timestamp":r.timestamp,"strategy":"EKALAYAVA","entry":float(r.close),
                    "opening_high":float(r.opening_high),"opening_low":float(r.opening_low),
                    "swing_high":swing_seen,"candle_type":r.candle_type})
                break
    return __import__("pandas").DataFrame(events)
