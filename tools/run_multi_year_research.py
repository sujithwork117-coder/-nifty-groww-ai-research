"""Generate bounded offline L2L policy and Ekalayava observation artifacts.

Uses the existing corrected Jan-Sep 2026 event ledger and assembled option bars.
It does not authenticate, download data, call the observer, or change strategies.
"""

from collections import Counter
from datetime import date as dt_date, datetime, time, timedelta
import csv
import hashlib
import json
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from app.research_target_policies import simulate_exit_policy
from app.nse_calendar import DEFAULT_NSE_CALENDAR


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data" / "derived" / "final_jan_sep_2026"
OPTION_ROOT = DATA_ROOT / "assembled" / "options"
REPORTS = ROOT / "reports"
BASELINE_PATH = DATA_ROOT / "final_baseline.json"
L2L_PATH = REPORTS / "L2L_FINAL_VALIDATION.json"
EKA_PATH = REPORTS / "EKALAYAVA_FINAL_RESEARCH.json"
POLICIES = ((1.0, "OPENING_HIGH_BASELINE"), (.75, "TARGET_75_PERCENT"),
            (.50, "TARGET_50_PERCENT"), (.25, "TARGET_25_PERCENT"))
STOP_CANDIDATES = (2, 4, 6)
TARGET_CANDIDATES = POLICIES
COMBINED_CANDIDATES = tuple(
    (stop, target, f"SL_{stop}_TP_{int(target * 100)}")
    for stop in STOP_CANDIDATES for target, _ in TARGET_CANDIDATES
)
IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _timestamp(value):
    return pd.Timestamp(value).tz_convert("UTC")


def _period(date):
    if date <= "2026-06-30":
        return "TRAIN_JAN_JUN"
    if date <= "2026-08-31":
        return "VALIDATION_JUL_AUG"
    return "OOS_SEP_INCOMPLETE"


def _entry_bucket(hour):
    if hour < 10:
        return "09:15-09:59"
    if hour < 11:
        return "10:00-10:59"
    return "11:00"


class CandleCache:
    def __init__(self):
        self.frames = {}
        self.missing_files = set()

    def session(self, symbol, date):
        if symbol not in self.frames:
            path = OPTION_ROOT / f"{symbol}.csv"
            if not path.is_file():
                self.missing_files.add(symbol)
                self.frames[symbol] = None
            else:
                frame = pd.read_csv(path)
                frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
                local = frame["timestamp"].dt.tz_convert("Asia/Kolkata")
                frame["local_date"] = local.dt.strftime("%Y-%m-%d")
                frame["local_time"] = local.dt.time
                self.frames[symbol] = frame.sort_values("timestamp").reset_index(drop=True)
        frame = self.frames[symbol]
        if frame is None:
            return []
        frame = frame[(frame["local_date"] == date) &
                      (frame["local_time"] >= time(9, 15)) & (frame["local_time"] <= time(15, 25))]
        return [{"timestamp": stamp.to_pydatetime(), "high": float(high), "low": float(low)}
                for stamp, high, low in zip(frame["timestamp"], frame["high"], frame["low"])]


def _policy_rows(events, cache):
    rows = []
    baseline_mismatches = []
    for event in events:
        if event.get("strategy") != "LEVEL_TO_LEVEL":
            continue
        date = event["date"]
        entry = float(event["entry"])
        stop = float(event["sl"])
        opening_high = float(event.get("opening_high", event["target"]))
        entry_stamp = _timestamp(event["timestamp"])
        local_stamp = entry_stamp.tz_convert("Asia/Kolkata")
        minute = local_stamp.hour * 60 + local_stamp.minute
        setup_id = hashlib.sha256(
            f"{event['symbol']}|{date}|{event['timestamp']}".encode("utf-8")
        ).hexdigest()[:20]
        skip = None
        if event.get("outcome", "").startswith("SKIPPED"):
            skip = event["outcome"]
        elif entry <= stop:
            skip = "SKIPPED_SL_ALREADY_BREACHED"
        elif entry >= opening_high:
            # Corrected Jan 1 PE ITM2 event; the old ledger mislabeled it TARGET.
            skip = "SKIPPED_TARGET_ALREADY_REACHED"

        candles = cache.session(event["symbol"], date)
        last_session_bar = pd.Timestamp(f"{date} 15:25:00", tz="Asia/Kolkata")
        for fraction, policy in POLICIES:
            if skip:
                result = {"status": skip, "target": None, "exit_timestamp": None,
                          "exit_price": None, "points": None, "holding_minutes": None,
                          "reason": "canonical_entry_skip"}
            else:
                result = simulate_exit_policy(
                    candles, entry_timestamp=entry_stamp, entry=entry, stop=stop,
                    opening_high=opening_high, target_fraction=fraction,
                    session_last_timestamp=last_session_bar,
                )
            terminal_stamp = (_timestamp(result["exit_timestamp"])
                              if result.get("exit_timestamp") else None)
            observed_bars = [bar for bar in candles
                             if _timestamp(bar["timestamp"]) > entry_stamp
                             and (terminal_stamp is None
                                  or _timestamp(bar["timestamp"]) <= terminal_stamp)]
            observed_mfe = max([0.0] + [bar["high"] - entry for bar in observed_bars])
            observed_mae = min([0.0] + [bar["low"] - entry for bar in observed_bars])
            row = {
                "setup_id": setup_id, "policy": policy, "target_fraction": fraction,
                "date": date, "year": date[:4], "period": _period(date), "timestamp_utc": event["timestamp"],
                "entry_time_ist": local_stamp.strftime("%H:%M"),
                "entry_bucket": _entry_bucket(local_stamp.hour),
                "symbol": event["symbol"], "option_type": event["option_type"],
                "itm_rank": event["itm_rank"], "entry": entry, "stop": stop,
                "opening_high": opening_high, "baseline_target_distance": opening_high-entry,
                "candidate_target": result.get("target"), "baseline_outcome_ledger": event.get("outcome"),
                "baseline_outcome_corrected": skip or event.get("outcome"),
                "outcome": result["status"], "exit_timestamp": result.get("exit_timestamp"),
                "exit_price": result.get("exit_price"), "points": result.get("points"),
                "mfe_through_terminal_bar": None if skip else observed_mfe,
                "mae_through_terminal_bar": None if skip else observed_mae,
                "excursion_terminal_bar_order_unknown": bool(terminal_stamp),
                "holding_minutes": result.get("holding_minutes"), "reason": result.get("reason"),
                "changed_vs_corrected_baseline": (
                    not skip and result["status"] != event.get("outcome")),
                "source_bar_count": len(candles),
            }
            rows.append(row)
            if fraction == 1.0 and not skip and result["status"] != event.get("outcome"):
                baseline_mismatches.append({
                    "setup_id": setup_id, "date": date, "symbol": event["symbol"],
                    "baseline": event.get("outcome"), "replayed": result["status"],
                    "reason": result.get("reason"),
                })
    return rows, baseline_mismatches


def _max_drawdown(points):
    equity = peak = drawdown = 0.0
    for value in points:
        equity += value
        peak = max(peak, equity)
        drawdown = max(drawdown, peak - equity)
    return drawdown


def _longest_losing_streak(rows):
    longest = current = 0
    resolved = sorted((row for row in rows if row["outcome"] in ("TARGET", "SL")),
                      key=lambda row: (row["date"], row.get("exit_timestamp") or row["timestamp_utc"],
                                       row["timestamp_utc"]))
    for row in resolved:
        current = current + 1 if row["outcome"] == "SL" else 0
        longest = max(longest, current)
    return longest


def _metrics(rows):
    outcomes = Counter(row["outcome"] for row in rows)
    resolved_rows = [row for row in rows if row["outcome"] in ("TARGET", "SL")]
    wins = [float(row["points"]) for row in resolved_rows if row["outcome"] == "TARGET"]
    losses = [float(row["points"]) for row in resolved_rows if row["outcome"] == "SL"]
    points = [float(row["points"]) for row in sorted(
        resolved_rows, key=lambda row: (row["date"], row.get("exit_timestamp") or row["timestamp_utc"],
                                        row["timestamp_utc"]))]
    durations = [float(row["holding_minutes"]) for row in resolved_rows
                 if row["holding_minutes"] is not None]
    mfe = [float(row.get("mfe_through_terminal_bar")) for row in rows
           if row.get("mfe_through_terminal_bar") is not None]
    mae = [float(row.get("mae_through_terminal_bar")) for row in rows
           if row.get("mae_through_terminal_bar") is not None]
    total = len(rows)
    resolved = len(resolved_rows)
    return {
        "setups": total,
        "entered": total - sum(count for key, count in outcomes.items() if key.startswith("SKIPPED")),
        "target": outcomes["TARGET"], "stop_loss": outcomes["SL"],
        "ambiguous": outcomes["AMBIGUOUS"],
        "unresolved": sum(count for key, count in outcomes.items() if key.startswith("UNRESOLVED")),
        "skipped": sum(count for key, count in outcomes.items() if key.startswith("SKIPPED")),
        "resolved": resolved,
        "target_rate_resolved": outcomes["TARGET"] / resolved if resolved else None,
        "resolved_rate_all_setups": resolved / total if total else None,
        "gross_points": sum(points),
        "mean_points_resolved": float(np.mean(points)) if points else None,
        "mean_points_per_setup": sum(points) / total if total else None,
        "mean_winner": float(np.mean(wins)) if wins else None,
        "median_winner": float(np.median(wins)) if wins else None,
        "mean_loser": float(np.mean(losses)) if losses else None,
        "median_loser": float(np.median(losses)) if losses else None,
        "profit_factor": sum(wins) / abs(sum(losses)) if losses and sum(losses) else None,
        "max_drawdown_equal_unit_resolved_sequence": _max_drawdown(points),
        "longest_consecutive_loss_streak_resolved_sequence": _longest_losing_streak(rows),
        "mean_holding_minutes": float(np.mean(durations)) if durations else None,
        "median_holding_minutes": float(np.median(durations)) if durations else None,
        "mean_mfe_through_terminal_bar": float(np.mean(mfe)) if mfe else None,
        "median_mfe_through_terminal_bar": float(np.median(mfe)) if mfe else None,
        "mean_mae_through_terminal_bar": float(np.mean(mae)) if mae else None,
        "median_mae_through_terminal_bar": float(np.median(mae)) if mae else None,
        "changed_vs_baseline": sum(bool(row["changed_vs_corrected_baseline"]) for row in rows),
    }


def _summary_rows(policy_rows, policy_names=None):
    summaries = []
    groupers = [
        ("ALL", lambda row: "ALL"),
        ("CHRONOLOGICAL_PERIOD", lambda row: row["period"]),
        ("YEAR", lambda row: row["year"]),
        ("MONTH", lambda row: row["date"][:7]),
        ("OPTION_TYPE", lambda row: row["option_type"]),
        ("ITM_RANK", lambda row: f"ITM{row['itm_rank']}"),
        ("ENTRY_TIME", lambda row: row["entry_bucket"]),
    ]
    policy_names = policy_names or [policy for _, policy in POLICIES]
    for policy in policy_names:
        selected = [row for row in policy_rows if row["policy"] == policy]
        for dimension, key_fn in groupers:
            buckets = {}
            for row in selected:
                buckets.setdefault(key_fn(row), []).append(row)
            for key, rows in buckets.items():
                summaries.append({"policy": policy, "dimension": dimension, "group": key,
                                  **_metrics(rows)})
    return summaries


def _candidate_rows(events, cache, candidates, *, stage):
    """Re-evaluate the fixed L2L event ledger for one predefined policy grid."""
    rows = []
    for event in events:
        if event.get("strategy") != "LEVEL_TO_LEVEL":
            continue
        date = event["date"]
        entry = float(event["entry"])
        opening_high = float(event.get("opening_high", event["target"]))
        opening_low = float(event["opening_low"])
        entry_stamp = _timestamp(event["timestamp"])
        local_stamp = entry_stamp.tz_convert(IST)
        setup_id = hashlib.sha256(
            f"{event['symbol']}|{date}|{event['timestamp']}".encode("utf-8")
        ).hexdigest()[:20]
        candles = cache.session(event["symbol"], date)
        last_session_bar = pd.Timestamp(f"{date} 15:25:00", tz="Asia/Kolkata")
        for stop_points, target_fraction, policy in candidates:
            stop = opening_low - float(stop_points)
            if entry >= opening_high:
                skip = "SKIPPED_TARGET_ALREADY_REACHED"
            elif entry <= stop:
                skip = "SKIPPED_SL_ALREADY_BREACHED"
            else:
                skip = None
            if skip:
                result = {"status": skip, "target": None, "exit_timestamp": None,
                          "exit_price": None, "points": None, "holding_minutes": None,
                          "reason": "entry_not_executable_under_candidate_levels"}
            else:
                result = simulate_exit_policy(
                    candles, entry_timestamp=entry_stamp, entry=entry, stop=stop,
                    opening_high=opening_high, target_fraction=target_fraction,
                    session_last_timestamp=last_session_bar,
                )
            terminal = result.get("exit_timestamp")
            terminal_stamp = _timestamp(terminal) if terminal else None
            observed = [bar for bar in candles if _timestamp(bar["timestamp"]) > entry_stamp
                        and (terminal_stamp is None or _timestamp(bar["timestamp"]) <= terminal_stamp)]
            mfe = max([0.0] + [bar["high"] - entry for bar in observed])
            mae = min([0.0] + [bar["low"] - entry for bar in observed])
            rows.append({
                "stage": stage, "policy": policy, "stop_buffer_points": stop_points,
                "target_fraction": target_fraction, "setup_id": setup_id,
                "date": date, "year": date[:4], "period": _period(date),
                "month": date[:7], "timestamp_utc": event["timestamp"],
                "entry_time_ist": local_stamp.strftime("%H:%M"),
                "entry_bucket": _entry_bucket(local_stamp.hour),
                "symbol": event["symbol"], "option_type": event["option_type"],
                "itm_rank": event["itm_rank"], "entry": entry,
                "opening_low": opening_low, "opening_high": opening_high,
                "stop": stop, "target": result.get("target"),
                "target_distance": (result.get("target") - entry
                                    if result.get("target") is not None else None),
                "baseline_outcome_ledger": event.get("outcome"),
                "changed_vs_corrected_baseline": result["status"] != (
                    "SKIPPED_TARGET_ALREADY_REACHED" if entry >= opening_high else
                    "SKIPPED_SL_ALREADY_BREACHED" if entry <= opening_low - 4 else
                    event.get("outcome")),
                "outcome": result["status"], "exit_timestamp": terminal,
                "exit_price": result.get("exit_price"), "points": result.get("points"),
                "holding_minutes": result.get("holding_minutes"),
                "holding_minutes_from_entry_bar_start": result.get("holding_minutes"),
                "mfe_through_terminal_bar": mfe, "mae_through_terminal_bar": mae,
                "mfe_observed": None if skip else mfe, "mae_observed": None if skip else mae,
                "excursion_terminal_bar_order_unknown": bool(terminal_stamp),
                "reason": result.get("reason"), "source_bar_count": len(candles),
            })
    return rows


def _quantiles(values):
    clean = [float(value) for value in values if value is not None and np.isfinite(value)]
    if not clean:
        return {"count": 0, "mean": None, "median": None, "p25": None, "p75": None,
                "p90": None}
    return {"count": len(clean), "mean": float(np.mean(clean)),
            "median": float(np.median(clean)), "p25": float(np.quantile(clean, .25)),
            "p75": float(np.quantile(clean, .75)), "p90": float(np.quantile(clean, .90))}


def _stop_forensics(events, cache):
    stop_rows = []
    for event in events:
        if event.get("strategy") != "LEVEL_TO_LEVEL" or event.get("outcome") != "SL":
            continue
        date, symbol = event["date"], event["symbol"]
        entry_stamp, stop_stamp = _timestamp(event["timestamp"]), _timestamp(event["exit_time"])
        bars = cache.session(symbol, date)
        entry_index = next((i for i, b in enumerate(bars) if b["timestamp"] == entry_stamp), None)
        stop_index = next((i for i, b in enumerate(bars) if b["timestamp"] == stop_stamp), None)
        if entry_index is None or stop_index is None or stop_index <= entry_index:
            stop_rows.append({"date": date, "symbol": symbol, "status": "SOURCE_BAR_MISSING"})
            continue
        before = bars[entry_index + 1:stop_index]
        after = bars[stop_index + 1:]
        entry, opening_high = float(event["entry"]), float(event["opening_high"])
        target_distance = opening_high-entry
        pre_mfe = max([0.0] + [bar["high"]-entry for bar in before])
        pre_mae = min([0.0] + [bar["low"]-entry for bar in before])
        stop_bar = bars[stop_index]
        post_mfe = max([0.0] + [bar["high"]-entry for bar in after])
        post_mae = min([0.0] + [bar["low"]-entry for bar in after])
        post_target = next((bar for bar in after if bar["high"] >= opening_high), None)

        def contiguous(path, previous):
            for bar in path:
                stamp = bar["timestamp"]
                if stamp - previous != timedelta(minutes=5):
                    return False
                previous = stamp
            return True

        pre_contiguous = contiguous(before, entry_stamp)
        post_contiguous = contiguous(after, stop_stamp)
        last_bar = bars[-1]["timestamp"] if bars else stop_stamp
        last_expected = pd.Timestamp(f"{date} 15:25:00", tz="Asia/Kolkata").tz_convert("UTC")
        post_complete_to_close = post_contiguous and last_bar >= last_expected
        first_after = bars[entry_index + 1] if entry_index + 1 < len(bars) else None
        stop_rows.append({
            "setup_id": hashlib.sha256(f"{symbol}|{date}|{event['timestamp']}".encode()).hexdigest()[:20],
            "date": date, "year": date[:4], "month": date[:7], "period": _period(date),
            "timestamp_utc": event["timestamp"], "entry_time_ist": _timestamp(event["timestamp"]).tz_convert(IST).strftime("%H:%M"),
            "entry_bucket": _entry_bucket(_timestamp(event["timestamp"]).tz_convert(IST).hour),
            "symbol": symbol, "option_type": event["option_type"], "itm_rank": event["itm_rank"],
            "entry": entry, "stop": float(event["sl"]), "opening_high": opening_high,
            "stop_distance_from_entry": entry-float(event["sl"]),
            "opening_low": float(event["opening_low"]),
            "target_distance": target_distance, "stop_time_utc": event["exit_time"],
            "minutes_to_stop_from_entry_close": (stop_stamp-entry_stamp).total_seconds()/60,
            "stop_touch_elapsed_lower_bound_minutes": max(
                0.0, (stop_stamp-entry_stamp).total_seconds()/60-5.0),
            "stop_touch_elapsed_upper_bound_minutes": (stop_stamp-entry_stamp).total_seconds()/60,
            "bars_before_stop_bar": len(before), "pre_stop_mfe_before_stop_bar": pre_mfe,
            "pre_stop_mfe_fraction_target": pre_mfe/target_distance if target_distance>0 else None,
            "pre_stop_mae_before_stop_bar": pre_mae,
            "pre_stop_path_contiguous": pre_contiguous,
            "first_post_entry_bar_moved_below_entry": bool(first_after and first_after["low"] < entry),
            "stop_bar_high_excursion_intrabar_order_unknown": stop_bar["high"]-entry,
            "stop_bar_high_touched_opening_high": stop_bar["high"] >= opening_high,
            "stop_bar_low_excursion_intrabar_order_unknown": stop_bar["low"]-entry,
            "post_stop_mfe_observed": post_mfe, "post_stop_mae_observed": post_mae,
            "post_stop_any_favorable_high_above_entry": any(bar["high"] > entry for bar in after),
            "post_stop_opening_high_touch_observed": post_target is not None,
            "post_stop_first_observed_target_timestamp_utc": post_target["timestamp"].isoformat() if post_target else None,
            "post_stop_observed_candles": len(after),
            "post_stop_path_contiguous_to_close": post_complete_to_close,
            "post_stop_no_target_can_be_asserted": post_complete_to_close and post_target is None,
        })
    return stop_rows


def _ekalayava_rows(events):
    rows = []
    for event in events:
        if event.get("strategy") != "EKALAYAVA":
            continue
        stamp = _timestamp(event["timestamp"]).tz_convert(IST)
        date = event["date"]
        target_touch = bool(event.get("target_touched", event.get("outcome") == "TARGET_TOUCH"))
        rows.append({
            "setup_id": hashlib.sha256(
                f"{event['symbol']}|{date}|{event['timestamp']}".encode("utf-8")
            ).hexdigest()[:20],
            "date": date, "year": date[:4], "month": date[:7], "period": _period(date),
            "timestamp_utc": event["timestamp"], "entry_time_ist": stamp.strftime("%H:%M"),
            "entry_bucket": _entry_bucket(stamp.hour), "symbol": event["symbol"],
            "option_type": event["option_type"], "itm_rank": event["itm_rank"],
            "entry": event["entry"], "opening_high": event["opening_high"],
            "opening_low": event["opening_low"], "swing_high": event.get("swing_high"),
            "target_distance": float(event["opening_high"])-float(event["entry"]),
            "breakdown_timestamp_utc": event.get("breakdown_timestamp"),
            "swing_high_timestamp_utc": event.get("swing_high_timestamp"),
            "breakout_timestamp_utc": event.get("breakout_timestamp"),
            "target_touched": target_touch,
            "target_touch_time_utc": event.get("target_touch_time"),
            "time_to_target_minutes_source": event.get("time_to_target_minutes"),
            "mfe": event.get("mfe"), "mae": event.get("mae"),
            "time_to_mfe_minutes": event.get("time_to_mfe_minutes"),
            "time_to_mae_minutes": event.get("time_to_mae_minutes"),
            "observation_end_time_utc": event.get("observation_end_time"),
            "observation_bars": event.get("observation_bars"),
            "structural_low_candidate": event.get("observed_reversal_structure_low"),
            "breakout_candle_low": event.get("breakout_candle_low"),
            "reversal_structure_low_revisited": event.get("reversal_structure_low_revisited"),
            "breakout_candle_low_revisited": event.get("breakout_candle_low_revisited"),
            "opening_low_revisited": event.get("opening_low_revisited"),
            "canonical_lifecycle": "UNRESOLVED_NO_APPROVED_EXIT_RULE",
            "realized_pnl": None,
        })
    return rows


def _ekalayava_summary(rows):
    result = []
    dimensions = [("ALL", lambda row: "ALL"),
                  ("CHRONOLOGICAL_PERIOD", lambda row: row["period"]),
                  ("YEAR", lambda row: row["year"]),
                  ("MONTH", lambda row: row["month"]),
                  ("OPTION_TYPE", lambda row: row["option_type"]),
                  ("ITM_RANK", lambda row: f"ITM{row['itm_rank']}"),
                  ("ENTRY_TIME", lambda row: row["entry_bucket"])]
    for dimension, key_fn in dimensions:
        groups = {}
        for row in rows:
            groups.setdefault(key_fn(row), []).append(row)
        for key, group in groups.items():
            target = [row for row in group if row["target_touched"]]
            result.append({
                "dimension": dimension, "group": key, "entries": len(group),
                "target_touches": len(target),
                "target_touch_rate": len(target)/len(group) if group else None,
                "canonical_lifecycle_resolved": 0,
                "unresolved_entries": len(group),
                "mfe": _quantiles([row["mfe"] for row in group]),
                "mae": _quantiles([row["mae"] for row in group]),
                "target_distance": _quantiles([row["target_distance"] for row in group]),
                "time_to_mfe_minutes": _quantiles([row["time_to_mfe_minutes"] for row in group]),
                "time_to_mae_minutes": _quantiles([row["time_to_mae_minutes"] for row in group]),
                "time_to_target_minutes_touch_only": _quantiles(
                    [row["time_to_target_minutes_source"] for row in target]),
                "max_mfe_time_before_max_mae_time": sum(
                    row["time_to_mfe_minutes"] < row["time_to_mae_minutes"]
                    for row in group if row["time_to_mfe_minutes"] is not None
                    and row["time_to_mae_minutes"] is not None),
            })
    return result


def _forensic_summary(stop_rows):
    result = []
    dims = [("ALL", lambda r: "ALL"), ("YEAR", lambda r: r.get("year")),
            ("MONTH", lambda r: r.get("month")),
            ("CHRONOLOGICAL_PERIOD", lambda r: r.get("period")),
            ("OPTION_TYPE", lambda r: r.get("option_type")),
            ("ITM_RANK", lambda r: f"ITM{r.get('itm_rank')}"),
            ("ENTRY_TIME", lambda r: r.get("entry_bucket"))]
    usable = [row for row in stop_rows if row.get("status") != "SOURCE_BAR_MISSING"]
    for dimension, group_fn in dims:
        groups = {}
        for row in usable:
            groups.setdefault(group_fn(row), []).append(row)
        for name, rows in groups.items():
            mfe = [r["pre_stop_mfe_before_stop_bar"] for r in rows]
            frac = [r["pre_stop_mfe_fraction_target"] for r in rows]
            durations = [r["minutes_to_stop_from_entry_close"] for r in rows]
            lower_durations = [r["stop_touch_elapsed_lower_bound_minutes"] for r in rows]
            upper_durations = [r["stop_touch_elapsed_upper_bound_minutes"] for r in rows]
            result.append({
                "dimension": dimension, "group": name, "stop_trades": len(rows),
                "strictly_positive_pre_stop_mfe_count": sum(x > 0 for x in mfe),
                "zero_pre_stop_mfe_count": sum(x == 0 for x in mfe),
                "pre_stop_mfe_at_least_75pct_target_count": sum(x >= .75 for x in frac),
                "pre_stop_mfe_at_least_100pct_target_count": sum(x >= 1.0 for x in frac),
                "pre_stop_mfe_below_25pct_target_count": sum(x < .25 for x in frac),
                "pre_stop_mfe_points": _quantiles(mfe),
                "pre_stop_mfe_fraction_target": _quantiles(frac),
                "pre_stop_target_fraction_ge_25pct": sum(x >= .25 for x in frac)/len(frac) if frac else None,
                "pre_stop_target_fraction_ge_50pct": sum(x >= .50 for x in frac)/len(frac) if frac else None,
                "pre_stop_target_fraction_ge_75pct": sum(x >= .75 for x in frac)/len(frac) if frac else None,
                "pre_stop_target_fraction_ge_100pct": sum(x >= 1.0 for x in frac)/len(frac) if frac else None,
                "immediate_adverse_first_bar_count": sum(r["first_post_entry_bar_moved_below_entry"] for r in rows),
                "stop_within_5min_count": sum(r["minutes_to_stop_from_entry_close"] <= 5 for r in rows),
                "minutes_to_stop": _quantiles(durations),
                "stop_touch_elapsed_lower_bound_minutes": _quantiles(lower_durations),
                "stop_touch_elapsed_upper_bound_minutes": _quantiles(upper_durations),
                "post_stop_observed_opening_high_touches": sum(r["post_stop_opening_high_touch_observed"] for r in rows),
                "post_stop_any_favorable_high_count": sum(r["post_stop_any_favorable_high_above_entry"] for r in rows),
                "post_stop_mfe_points": _quantiles([r["post_stop_mfe_observed"] for r in rows]),
                "post_stop_complete_no_touch_paths": sum(r["post_stop_no_target_can_be_asserted"] for r in rows),
                "pre_stop_paths_with_gaps": sum(not r["pre_stop_path_contiguous"] for r in rows),
            })
    return result


def _write_csv(path, rows):
    if not rows:
        return
    columns = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _compact_coverage(baseline, coverage_report):
    coverage = coverage_report["data_coverage"]
    requested_start, requested_end = dt_date(2026, 1, 1), dt_date(2026, 9, 30)
    trading_dates = []
    current = requested_start
    while current <= requested_end:
        if DEFAULT_NSE_CALENDAR.session_for(current) is not None:
            trading_dates.append(current.isoformat())
        current += timedelta(days=1)
    underlying_available = set(baseline["trading_day_coverage"]["available"])
    month_rows = []
    for month in sorted({d[:7] for d in trading_dates}):
        dates = [d for d in trading_dates if d.startswith(month)]
        month_rows.append({"month": month, "expected_sessions": len(dates),
                           "underlying_sessions_available": sum(d in underlying_available for d in dates),
                           "expected_option_contract_days": len(dates)*4})
    # Per-slot completion is re-derived from the saved exact-selection ledger.
    slots = {}
    for row in baseline.get("contract_eligibility", []):
        key = (row["date"], row["symbol"])
        count = int(row.get("available_session_candles", 0))
        expected = int(row.get("expected_session_candles", 75))
        status = "complete" if count >= expected else "partial" if count else "missing"
        slots[key] = status
    day_complete = Counter()
    day_partial = Counter()
    day_missing = Counter()
    for date in trading_dates:
        rows = [status for (day, _), status in slots.items() if day == date]
        missing_slot_count = 4 - len(rows)
        day_complete[date] = sum(status == "complete" for status in rows)
        day_partial[date] = sum(status == "partial" for status in rows)
        day_missing[date] = sum(status == "missing" for status in rows) + missing_slot_count
    missing_months = {}
    for date in trading_dates:
        item = missing_months.setdefault(date[:7], {"complete": 0, "partial": 0, "missing": 0})
        item["complete"] += day_complete[date]
        item["partial"] += day_partial[date]
        item["missing"] += day_missing[date]
    for row in month_rows:
        row.update(missing_months.get(row["month"], {}))
    return {
        "local_inventory": {
            "tracked_or_ignored_market_files_are_not_published": True,
            "authoritative_dataset": "data/derived/final_jan_sep_2026/assembled",
            "underlying_file": "data/derived/final_jan_sep_2026/assembled/nifty_5m.csv",
            "option_symbol_files": len(list(OPTION_ROOT.glob("NSE-NIFTY-*.csv"))),
            "authoritative_underlying_bars": coverage["underlying_bars"],
            "authoritative_option_bars": coverage["option_bars_available"],
            "date_range_requested": ["2026-01-01", "2026-09-30"],
            "date_range_with_underlying": ["2026-01-01", "2026-09-29"],
            "earlier_years_2022_2025_local_data": "none found in repository market-data directories",
            "all_local_csv_snapshot": {
                "snapshot_date": "2026-10-12",
                "csv_files_inspected": 1755,
                "timestamped_rows_across_duplicate_caches": 347783,
                "earliest_timestamp_utc": "2026-01-01 03:30:00+00:00",
                "latest_timestamp_utc": "2026-09-29 08:30:00+00:00",
                "years_present": [2026],
                "note": "Counts include duplicate run/cache copies; they are not unique bars or additional coverage.",
            },
            "calendar": "NSECalendar 2026 session list; includes 2026-02-01 Budget Sunday session",
        },
        "periods": {
            "2022": {"status": "UNAVAILABLE", "reason": "no local 5-minute datasets; Groww 5-minute history is documented as last 3 months"},
            "2023": {"status": "UNAVAILABLE", "reason": "no local 5-minute datasets; Groww 5-minute history is documented as last 3 months"},
            "2024": {"status": "UNAVAILABLE", "reason": "no local 5-minute datasets; Groww 5-minute history is documented as last 3 months"},
            "2025": {"status": "UNAVAILABLE", "reason": "no local 5-minute datasets; Groww 5-minute history is documented as last 3 months"},
            "2026-01-01_to_2026-09-30": {
                "expected_sessions": coverage["sessions"],
                "underlying_sessions_available": coverage["underlying_days_available"],
                "underlying_bars": coverage["underlying_bars"],
                "underlying_expected_bars": coverage["underlying_expected_bars"],
                "expected_option_contract_days": coverage["option_contract_days_expected"],
                "complete_contract_days": coverage["contract_days_complete"],
                "partial_contract_days": coverage["contract_days_partial"],
                "missing_or_unselectable_contract_days": coverage["contract_days_missing_or_unselectable"],
                "observed_option_bars": coverage["option_bars_available"],
                "expected_option_bars": coverage["option_bars_expected"],
                "option_coverage_fraction": coverage["option_coverage_fraction"],
                "fully_usable_days": coverage["fully_usable_days"],
                "partially_usable_days": coverage["partially_usable_days"],
                "unusable_days": coverage["unusable_days"],
                "monthly_coverage": month_rows,
                "missing_slots_manifest": baseline.get("missing_data", []),
            },
        },
    }


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    baseline = _read_json(BASELINE_PATH)
    events = baseline["trade_events"]
    cache = CandleCache()
    policy_rows, mismatches = _policy_rows(events, cache)
    summaries = _summary_rows(policy_rows)
    stop_candidates = [(points, 1.0, f"SL_{points}") for points in STOP_CANDIDATES]
    stop_policy_rows = _candidate_rows(events, cache, stop_candidates, stage="STOP_ONLY")
    stop_policy_summaries = _summary_rows(
        stop_policy_rows, [f"SL_{points}" for points in STOP_CANDIDATES])
    target_candidates = [(4, fraction, name) for fraction, name in TARGET_CANDIDATES]
    target_policy_rows = _candidate_rows(events, cache, target_candidates, stage="TARGET_ONLY")
    target_policy_summaries = _summary_rows(
        target_policy_rows, [name for _, name in TARGET_CANDIDATES])
    combined_rows = _candidate_rows(events, cache, COMBINED_CANDIDATES, stage="COMBINED")
    combined_summaries = _summary_rows(
        combined_rows, [name for _, _, name in COMBINED_CANDIDATES])
    stop_rows = _stop_forensics(events, cache)
    forensic_summary = _forensic_summary(stop_rows)
    eka_rows = _ekalayava_rows(events)
    eka_summary = _ekalayava_summary(eka_rows)

    baseline_summary = next(row for row in summaries if row["policy"] == "OPENING_HIGH_BASELINE"
                            and row["dimension"] == "ALL")
    expected = {"setups": 361, "target": 57, "stop_loss": 145, "ambiguous": 1, "skipped": 158}
    observed = {key: baseline_summary[key] for key in expected}
    if observed != expected or mismatches:
        raise AssertionError(json.dumps({"baseline_counts": observed, "expected": expected,
                                         "baseline_outcome_mismatches": mismatches,
                                         "missing_symbol_files": sorted(cache.missing_files)}, indent=2))
    combined_baseline = next(row for row in combined_summaries
                             if row["policy"] == "SL_4_TP_100"
                             and row["dimension"] == "ALL")
    if any(combined_baseline[key] != baseline_summary[key]
           for key in ("setups", "target", "stop_loss", "ambiguous", "skipped", "gross_points")):
        raise AssertionError("SL4/TP100 combined candidate does not reproduce corrected baseline")

    # Selection is frozen to Jan-Jun only. Policy values are not chosen from
    # validation or September, and all September numbers are labeled an
    # incomplete chronological check, not a fresh untouched holdout.
    def select_train_candidate(summary_rows, candidates):
        train = [row for row in summary_rows
                 if row["dimension"] == "CHRONOLOGICAL_PERIOD"
                 and row["group"] == "TRAIN_JAN_JUN"
                 and row["policy"] in candidates]
        return max(train, key=lambda row: (
            row["mean_points_per_setup"] if row["mean_points_per_setup"] is not None
            else float("-inf"),
            -(row["max_drawdown_equal_unit_resolved_sequence"] or 0.0),
            -row["longest_consecutive_loss_streak_resolved_sequence"],
        )) if train else None

    baseline_train = next(row for row in summaries
                          if row["policy"] == "OPENING_HIGH_BASELINE"
                          and row["dimension"] == "CHRONOLOGICAL_PERIOD"
                          and row["group"] == "TRAIN_JAN_JUN")
    selected_stop = select_train_candidate(stop_policy_summaries,
                                           [f"SL_{p}" for p in STOP_CANDIDATES if p != 4])
    selected_target = select_train_candidate(target_policy_summaries,
                                             [name for _, name in TARGET_CANDIDATES if name != "OPENING_HIGH_BASELINE"])
    selected_combined = select_train_candidate(combined_summaries,
                                               [name for _, _, name in COMBINED_CANDIDATES])

    def validation_screen(candidate, summary_rows):
        if not candidate:
            return {"status": "NO_TRAIN_CANDIDATE"}
        validation = next(row for row in summary_rows
                          if row["policy"] == candidate["policy"]
                          and row["dimension"] == "CHRONOLOGICAL_PERIOD"
                          and row["group"] == "VALIDATION_JUL_AUG")
        baseline = next(row for row in summaries
                        if row["policy"] == "OPENING_HIGH_BASELINE"
                        and row["dimension"] == "CHRONOLOGICAL_PERIOD"
                        and row["group"] == "VALIDATION_JUL_AUG")
        checks = {
            "gross_points_per_setup_exceeds_baseline":
                (validation["mean_points_per_setup"] or 0) > (baseline["mean_points_per_setup"] or 0),
            "drawdown_not_above_baseline":
                (validation["max_drawdown_equal_unit_resolved_sequence"] or 0)
                <= (baseline["max_drawdown_equal_unit_resolved_sequence"] or 0),
            "loss_streak_not_above_baseline":
                validation["longest_consecutive_loss_streak_resolved_sequence"]
                <= baseline["longest_consecutive_loss_streak_resolved_sequence"],
        }
        return {"status": "SURVIVES_VALIDATION_SCREEN" if all(checks.values()) else "REJECTED_AT_VALIDATION",
                "validation_policy": validation["policy"], "validation_checks": checks,
                "validation_metrics": validation}

    candidate_selection = {
        "data_period_used_for_selection": "2026-01-01 through 2026-06-30 only",
        "validation_period": "2026-07-01 through 2026-08-31",
        "chronological_oos_check": "2026-09-01 through 2026-09-30; data only through Sep 29 and option coverage incomplete",
        "holdout_caveat": "September results are an incomplete chronological diagnostic; target candidates were already evaluated in inherited research artifacts and this period is not claimed as untouched.",
        "predeclared_train_selection_rule": "Within each experiment family, maximize gross resolved points per all baseline setups in Jan-Jun; tie-break on lower equal-unit chronological resolved-sequence drawdown, then shorter longest loss streak.",
        "predeclared_validation_rejection_rule": "Reject selected candidate if validation gross resolved points per all baseline setups does not exceed baseline, or if drawdown or longest loss streak exceeds baseline. No replacement is selected on validation/September.",
        "baseline_train_metrics": baseline_train,
        "selected_by_train_only": {
            "independent_stop": selected_stop,
            "independent_target": selected_target,
            "combined_sl_tp": selected_combined,
        },
        "validation_decision": {
            "independent_stop": validation_screen(selected_stop, stop_policy_summaries),
            "independent_target": validation_screen(selected_target, target_policy_summaries),
            "combined_sl_tp": validation_screen(selected_combined, combined_summaries),
        },
        "final_recommendation": "NO RELIABLE WINNER — MORE EVIDENCE REQUIRED",
        "operational_decision": "RETAIN CANONICAL BASELINE; no production stop/target change",
    }

    _write_csv(REPORTS / "multi_year_l2l_target_policy_trades.csv", target_policy_rows)
    _write_csv(REPORTS / "multi_year_l2l_target_policy_summary.csv", target_policy_summaries)
    _write_csv(REPORTS / "multi_year_l2l_stop_loss_forensics.csv", stop_rows)
    _write_csv(REPORTS / "multi_year_l2l_stop_loss_summary.csv", forensic_summary)
    _write_csv(REPORTS / "multi_year_ekalayava_observations.csv", eka_rows)
    _write_csv(REPORTS / "multi_year_ekalayava_summary.csv", eka_summary)
    _write_csv(REPORTS / "multi_year_l2l_stop_policy_trades.csv", stop_policy_rows)
    _write_csv(REPORTS / "multi_year_l2l_stop_policy_summary.csv", stop_policy_summaries)
    _write_csv(REPORTS / "multi_year_l2l_combined_sl_tp_trades.csv", combined_rows)
    _write_csv(REPORTS / "multi_year_l2l_combined_sl_tp_summary.csv", combined_summaries)
    _write_csv(REPORTS / "multi_year_baseline_metrics.csv", [
        row for row in target_policy_summaries if row["policy"] == "OPENING_HIGH_BASELINE"
        and row["dimension"] in ("ALL", "CHRONOLOGICAL_PERIOD", "YEAR", "MONTH",
                                  "OPTION_TYPE", "ITM_RANK", "ENTRY_TIME")])
    _write_csv(REPORTS / "multi_year_period_metrics.csv", [
        row for row in target_policy_summaries + stop_policy_summaries + combined_summaries
        if row["dimension"] in ("CHRONOLOGICAL_PERIOD", "YEAR", "MONTH")])
    (REPORTS / "multi_year_candidate_selection.json").write_text(
        json.dumps(candidate_selection, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8")
    coverage_report = _read_json(L2L_PATH)
    coverage = _compact_coverage(baseline, coverage_report)
    (REPORTS / "multi_year_data_coverage.json").write_text(
        json.dumps(coverage, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    version = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    cfg = {
        "experiment": "multi_year_nifty_l2l_ekalayava_validation",
        "generated_at_ist": datetime.now(IST).isoformat(),
        "base_git_commit": version,
        "canonical_strategy_version": baseline.get("strategy_version"),
        "data_source": "existing Groww-derived local cache only; no API calls or downloads",
        "source_artifacts": {
            str(BASELINE_PATH.relative_to(ROOT)): _hash(BASELINE_PATH),
            str(L2L_PATH.relative_to(ROOT)): _hash(L2L_PATH),
            str(EKA_PATH.relative_to(ROOT)): _hash(EKA_PATH),
        },
        "research_code_sha256": {
            "tools/run_multi_year_research.py": _hash(ROOT / "tools" / "run_multi_year_research.py"),
            "app/research_target_policies.py": _hash(ROOT / "app" / "research_target_policies.py"),
        },
        "target_fractions": [{"policy": name, "fraction": fraction}
                             for fraction, name in POLICIES],
        "independent_stop_candidates_points_below_opening_low": [2, 4, 6],
        "independent_target_candidates": [
            {"policy": name, "fraction_of_entry_to_opening_high": fraction}
            for fraction, name in TARGET_CANDIDATES
        ],
        "combined_candidate_matrix": [
            {"policy": name, "stop_points_below_opening_low": stop,
             "target_fraction_of_entry_to_opening_high": fraction}
            for stop, fraction, name in COMBINED_CANDIDATES
        ],
        "train": "2026-01-01_to_2026-06-30",
        "validation": "2026-07-01_to_2026-08-31",
        "chronological_oos_check_not_untouched_holdout": "2026-09-01_to_2026-09-30; actual underlying available only through 2026-09-29; option coverage is incomplete and inherited research had already examined candidate target policies",
        "predeclared_selection_rule": "Within each experiment family, maximize gross resolved points per all baseline setups in Jan-Jun; tie-break on lower equal-unit chronological resolved-sequence drawdown, then shorter longest loss streak. No September-based selection.",
        "training_selected_research_candidate": selected_target["policy"] if selected_target else None,
        "baseline_replay_mismatches": mismatches,
        "missing_contract_files": sorted(cache.missing_files),
        "execution_allowed": False,
        "paper_only": True,
        "costs": "Not modeled; all points gross premium-point thresholds, no spread/slippage/fees/taxes",
        "candle_resolution": "Completed 5-minute OHLC; same-bar stop+target is ambiguous; missing intervals before touch remain unresolved; no forced EOD exit",
    }
    (REPORTS / "multi_year_research_config.json").write_text(
        json.dumps(cfg, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "baseline_replay": observed, "baseline_mismatch_count": len(mismatches),
        "selected_research_candidate_train_only": {
            "independent_stop": selected_stop["policy"] if selected_stop else None,
            "independent_target": selected_target["policy"] if selected_target else None,
            "combined_sl_tp": selected_combined["policy"] if selected_combined else None,
        },
        "candidate_summaries": [row for row in summaries if row["dimension"] == "ALL"],
        "stop_forensics_all": next(row for row in forensic_summary
                                    if row["dimension"] == "ALL"),
        "stop_count": sum(row.get("status") != "SOURCE_BAR_MISSING" for row in stop_rows),
        "source_missing_stop_bars": sum(row.get("status") == "SOURCE_BAR_MISSING" for row in stop_rows),
        "outputs": [
            "reports/multi_year_l2l_target_policy_trades.csv",
            "reports/multi_year_l2l_target_policy_summary.csv",
            "reports/multi_year_l2l_stop_loss_forensics.csv",
            "reports/multi_year_l2l_stop_loss_summary.csv",
            "reports/multi_year_ekalayava_observations.csv",
            "reports/multi_year_ekalayava_summary.csv",
            "reports/multi_year_data_coverage.json",
            "reports/multi_year_research_config.json",
            "reports/multi_year_l2l_stop_policy_trades.csv",
            "reports/multi_year_l2l_stop_policy_summary.csv",
            "reports/multi_year_l2l_combined_sl_tp_trades.csv",
            "reports/multi_year_l2l_combined_sl_tp_summary.csv",
            "reports/multi_year_baseline_metrics.csv",
            "reports/multi_year_period_metrics.csv",
            "reports/multi_year_candidate_selection.json",
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
