from pathlib import Path
import csv
import json
import os
import threading

_PAPER_JOURNAL_LOCK = threading.RLock()
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
    "record_id", "event_id", "setup_id", "event_type", "model_version", "strategy_version",
    "simulation_mode", "exit_model_version", "recorded_at", "entry_reason", "candle_type",
    "date", "timestamp", "close_time", "strategy", "symbol", "expiry", "strike",
    "option_type", "itm_rank", "nifty_price", "entry", "entry_timestamp", "sl",
    "candidate_sl", "candidate_sl_status", "structural_sl_anchor", "structural_low_price",
    "structural_low_distance_points",
    "sl_buffer_points", "target", "opening_high", "opening_low",
    "red_break_timestamp", "first_green_timestamp", "breakdown_timestamp",
    "reversal_structure", "structural_low_candidate", "structural_low_timestamp",
    "swing_high", "swing_high_timestamp", "breakout_timestamp", "breakout_candle_low",
    "status", "outcome", "mfe", "mae", "time_to_mfe_minutes", "time_to_mae_minutes",
    "holding_time_minutes",
    "open", "high", "low", "close", "volume", "oi",
    "data_provenance", "source_retrieved_at", "quote_timestamp", "bid", "ask",
    "spread_points", "fill_assumption", "cost_points", "cost_provenance",
    "stop_updates_json", "stop_update_timestamp", "stop_active_from_timestamp",
    "target_touch_timestamp", "time_to_target_minutes", "exit_timestamp",
    "exit_reason", "exit_price", "points_gained_lost", "structural_low_revisited",
    "breakout_candle_low_revisited", "opening_low_revisited", "target_and_candidate_low_same_candle",
    "realized_pnl", "data_quality_status", "missing_intervals", "execution", "paper_only",
    "stream", "reason", "error_type", "last_completed_candle", "retry_after_seconds",
    "suppressed_candle_count",
    "selection_timestamp", "underlying_reference_price",
    "underlying_reference_candle_timestamp", "contract_catalog_retrieved_at",
    "selection_rationale", "selected_contracts_json", "expected_strikes_json",
    "observed_strike_step",
    "candidate_id", "candidate_state_json", "hypothetical_stop",
    "hypothetical_target", "hypothetical_exit_price", "hypothetical_points",
    "source_candle_timestamp",
)


def append_paper_record(event, path, model_version):
    """Append an immutable JSONL snapshot, idempotent by record_id."""
    from datetime import datetime, timezone

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    record_id = event.get("record_id")
    if not record_id:
        raise ValueError("Paper journal records require a stable record_id")
    row = {key: event.get(key) for key in PAPER_RECORD_FIELDS}
    row["recorded_at"] = datetime.now(timezone.utc).isoformat()
    row["model_version"] = model_version
    row["paper_only"] = True
    payload = (json.dumps(row, sort_keys=True, default=str) + "\n").encode("utf-8")
    # Serialize same-process writers, append one complete encoded record, and
    # flush it to disk before returning so a restart can rely on the journal.
    with _PAPER_JOURNAL_LOCK:
        separator = b""
        if destination.exists():
            with destination.open("r", encoding="utf-8") as stream:
                for line in stream:
                    try:
                        if json.loads(line).get("record_id") == record_id:
                            return False
                    except (json.JSONDecodeError, AttributeError):
                        continue
            if destination.stat().st_size:
                with destination.open("rb") as stream:
                    stream.seek(-1, os.SEEK_END)
                    if stream.read(1) not in (b"\n", b"\r"):
                        separator = b"\n"
        payload = separator + payload
        descriptor = os.open(destination, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
        try:
            remaining = memoryview(payload)
            while remaining:
                written = os.write(descriptor, remaining)
                if written <= 0:
                    raise OSError("Paper journal append made no progress")
                remaining = remaining[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    return True
