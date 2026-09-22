from pathlib import Path
import csv
FIELDS=["recorded_at","model_version","strategy","date","timestamp","entry","sl","target","opening_high","opening_low","swing_high","candle_type","mfe","mae","outcome","paper_only"]
def append_event(event,path,model_version):
    from datetime import datetime
    Path(path).parent.mkdir(parents=True,exist_ok=True);exists=Path(path).exists()
    row={k:event.get(k) for k in FIELDS};row["recorded_at"]=datetime.utcnow().isoformat();row["model_version"]=model_version;row["paper_only"]=True
    with open(path,"a",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        if not exists:w.writeheader()
        w.writerow(row)
