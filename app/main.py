import argparse,pandas as pd
from .config import CFG
from .safety import ExecutionLock
from .groww_auth import authenticate
from .strategies import level_to_level_events,ekalayava_events,prepare
from .learning import enrich_events,build_report,save_report
def smoke():
    ExecutionLock(CFG).assert_paper_only();g=authenticate();p=g.get_user_profile()
    print("Authenticated. Active segments:",p.get("active_segments"))
    print("Execution lock: ENABLED");print("Order placement: NOT IMPLEMENTED")
def run_csv(path):
    ExecutionLock(CFG).assert_paper_only()
    d=pd.read_csv(path);d.timestamp=pd.to_datetime(d.timestamp,utc=True).dt.tz_convert("Asia/Kolkata")
    x=prepare(d)
    for name,ev in [("level",level_to_level_events(d,CFG.level_sl_points,CFG.level_entry_start,CFG.level_entry_end)),
                    ("ekalayava",ekalayava_events(d,CFG.ek_start,CFG.ek_end))]:
        if not ev.empty:ev=enrich_events(ev,x)
        report=build_report(ev);save_report(report,f"data/reports/{name}_report.json")
        if not ev.empty:ev.to_csv(f"data/reports/{name}_events.csv",index=False)
        print(name,report)
def main():
    p=argparse.ArgumentParser();p.add_argument("--smoke",action="store_true");p.add_argument("--auth",action="store_true");p.add_argument("--csv")
    a=p.parse_args()
    if a.smoke or a.auth:smoke()
    elif a.csv:run_csv(a.csv)
    else:p.print_help()
if __name__=="__main__":main()
