from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

def save_setup_chart(candles,event,path,title=None):
    x=candles.sort_values("timestamp").copy()
    destination=Path(path);destination.parent.mkdir(parents=True,exist_ok=True)
    figure,axis=plt.subplots(figsize=(12,6))
    axis.plot(x.timestamp,x.close,label="close",color="black",linewidth=1)
    event_values=event.to_dict() if hasattr(event,"to_dict") else dict(event)
    lines=(("opening_high","opening high","tab:blue"),("opening_low","opening low","tab:orange"),
           ("sl","SL","tab:red"),("target","target","tab:green"),("swing_high","swing high","tab:purple"))
    for field,label,color in lines:
        if field in event_values and event_values[field] is not None:
            axis.axhline(float(event_values[field]),label=label,color=color,linestyle="--",linewidth=.8)
    for field,label,color in (("timestamp","entry","tab:green"),("breakout_timestamp","breakout","tab:purple"),
                              ("exit_time","exit","tab:red")):
        value=event_values.get(field)
        if value is not None:
            value=pd.to_datetime(value,utc=True)
            axis.axvline(value,label=label,color=color,linestyle=":",linewidth=1)
    axis.set_title(title or str(event_values.get("strategy","setup")))
    axis.set_xlabel("timestamp");axis.set_ylabel("premium")
    axis.legend(loc="best");figure.autofmt_xdate();figure.tight_layout();figure.savefig(destination,dpi=120)
    plt.close(figure)
    return destination