def swing_highs(df,left=2,right=2):
    x=df.copy();x["swing_high"]=False;h=x.high.to_numpy()
    for i in range(left,len(x)-right):
        if h[i]>h[i-left:i].max() and h[i]>=h[i+1:i+right+1].max():x.loc[x.index[i],"swing_high"]=True
    return x
def premium_features(df):
    x=df.copy();x["premium_change"]=x.close.diff();x["premium_change_pct"]=x.close.pct_change()
    x["distance_from_day_high"]=x.high.cummax()-x.close;x["distance_from_day_low"]=x.close-x.low.cummin()
    x["reversal_from_recent_low"]=x.close-x.low.rolling(6,min_periods=1).min()
    return swing_highs(x)
