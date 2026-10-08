from pathlib import Path
import csv
import json
FIELDS=["recorded_at","model_version","strategy","date","timestamp","entry","sl","target","opening_high","opening_low","swing_high","candle_type","mfe","mae","outcome","paper_only"]
def append_event(event,path,model_version):
    from datetime import datetime,timezone
    Path(path).parent.mkdir(parents=True,exist_ok=True);exists=Path(path).exists()
    row={k:event.get(k) for k in FIELDS};row["recorded_at"]=datetime.now(timezone.utc).isoformat();row["model_version"]=model_version;row["paper_only"]=True
    with open(path,"a",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        if not exists:w.writeheader()
        w.writerow(row)


PAPER_RECORD_FIELDS = (
    "record_id", "event_id", "event_type", "model_version", "recorded_at", "entry_reason", "candle_type",
    "date", "timestamp", "close_time", "strategy", "symbol", "expiry", "strike",
    "option_type", "itm_rank", "nifty_price", "entry", "entry_timestamp", "sl",
    "candidate_sl", "candidate_sl_status", "target", "opening_high", "opening_low",
    "red_break_timestamp", "first_green_timestamp", "breakdown_timestamp",
    "reversal_structure", "structural_low_candidate", "structural_low_timestamp",
    "swing_high", "swing_high_timestamp", "breakout_timestamp", "breakout_candle_low",
    "status", "outcome", "mfe", "mae", "time_to_mfe_minutes", "time_to_mae_minutes",
    "target_touch_timestamp", "time_to_target_minutes", "exit_timestamp",
    "exit_reason", "exit_price", "points_gained_lost", "structural_low_revisited",
    "breakout_candle_low_revisited", "opening_low_revisited", "target_and_candidate_low_same_candle",
    "realized_pnl", "data_quality_status", "missing_intervals", "execution", "paper_only",
)


def append_paper_record(event, path, model_version):
    """Append an immutable JSONL snapshot, idempotent by record_id."""
    from datetime import datetime, timezone

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    record_id = event.get("record_id")
    if not record_id:
        raise ValueError("Paper journal records require a stable record_id")
    if destination.exists():
        with destination.open("r", encoding="utf-8") as stream:
            for line in stream:
                try:
                    if json.loads(line).get("record_id") == record_id:
                        return False
                except (json.JSONDecodeError, AttributeError):
                    continue
    row = {key: event.get(key) for key in PAPER_RECORD_FIELDS}
    row["recorded_at"] = datetime.now(timezone.utc).isoformat()
    row["model_version"] = model_version
    row["paper_only"] = True
    with destination.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(row, sort_keys=True, default=str) + "\n")
    return True
