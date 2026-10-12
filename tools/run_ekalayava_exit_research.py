"""Run fixed, bounded Ekalayava exit research and L2L entry-quality summaries.

Uses only the corrected saved Jan-Sep 2026 ledger and its exact option bars.
No Groww calls, data downloads, canonical-rule changes, or order calls occur.
"""

from collections import Counter, defaultdict
from datetime import timedelta
import json
from pathlib import Path
import statistics

import numpy as np
import pandas as pd

from app.research_ekalayava_exits import simulate_ekalayava_exit
from tools.run_multi_year_research import (
    BASELINE_PATH, CandleCache, IST, REPORTS, _entry_bucket, _period,
    _timestamp, _write_csv,
)


ANCHORS = {
    "A_STRUCTURAL_TROUGH": "observed_reversal_structure_low",
    "B_BREAKOUT_CANDLE": "breakout_candle_low",
    "D_OPENING_LOW": "opening_low",
}
ALIASES = {
    "C_RECOVERY_BASE_INVALIDATION": {
        "equivalent_policy": "A_STRUCTURAL_TROUGH",
        "reason": "The saved causal implementation records no distinct base boundary; both use the same min low from first opening-low break through the pre-breakout recovery/base, so another grid would duplicate A.",
    }
}
BUFFERS = (0.0, 2.0, 4.0)
TARGETS = ((1.0, "TP100_OPENING_HIGH"), (.75, "TP75"),
           (.50, "TP50"), (.25, "TP25"))
TRAIL_BUFFER = 2.0
TRAIN = "TRAIN_JAN_JUN"
VALIDATION = "VALIDATION_JUL_AUG"
LATER_CHECK = "OOS_SEP_INCOMPLETE"
ROOT = Path(__file__).resolve().parents[1]


def _q(values):
    vals = [float(v) for v in values if v is not None and np.isfinite(float(v))]
    if not vals:
        return {"count": 0, "mean": None, "median": None, "p25": None, "p75": None}
    return {"count": len(vals), "mean": float(np.mean(vals)),
            "median": float(np.median(vals)), "p25": float(np.quantile(vals, .25)),
            "p75": float(np.quantile(vals, .75))}


def _drawdown(values):
    equity = peak = dd = 0.0
    for value in values:
        equity += value
        peak = max(peak, equity)
        dd = max(dd, peak - equity)
    return dd


def _policy_name(anchor, buffer, target_name):
    return f"{anchor}_B{buffer:g}_{target_name}"


def _session_end(date):
    return pd.Timestamp(f"{date} 15:25:00", tz="Asia/Kolkata").tz_convert("UTC")


def _metrics(rows):
    outcomes = Counter(row["outcome"] for row in rows)
    excluded = sum(count for outcome, count in outcomes.items()
                   if outcome.startswith("EXCLUDED"))
    valid = len(rows) - excluded
    resolved = [r for r in rows if r["outcome"] in ("TARGET", "STOP_LOSS", "END_OF_SESSION")]
    ordered = sorted(resolved, key=lambda r: (r["date"], r["exit_timestamp"], r["timestamp_utc"]))
    points = [float(r["points"]) for r in ordered]
    wins = [x for x in points if x > 0]
    losses = [x for x in points if x < 0]
    durations = [r["holding_minutes"] for r in resolved if r.get("holding_minutes") is not None]
    loss_streak = longest = 0
    for value in points:
        loss_streak = loss_streak + 1 if value < 0 else 0
        longest = max(longest, loss_streak)
    mfe = [r.get("mfe_through_terminal_bar") for r in rows if r.get("mfe_through_terminal_bar") is not None]
    mae = [r.get("mae_through_terminal_bar") for r in rows if r.get("mae_through_terminal_bar") is not None]
    positive = sum(wins)
    negative = abs(sum(losses))
    total = len(rows)
    return {
        "eligible_entries": total, "valid_entries": valid, "excluded_entries": excluded,
        "target_exits": outcomes["TARGET"], "stop_exits": outcomes["STOP_LOSS"],
        "end_of_session_exits": outcomes["END_OF_SESSION"],
        "ambiguous": outcomes["AMBIGUOUS"],
        "unresolved": sum(n for k, n in outcomes.items() if k.startswith("UNRESOLVED")),
        "resolved": len(resolved),
        "target_rate_of_resolved": outcomes["TARGET"] / len(resolved) if resolved else None,
        "resolution_rate_of_valid": len(resolved) / valid if valid else None,
        "gross_points": sum(points),
        "expectancy_per_resolved": float(np.mean(points)) if points else None,
        "expectancy_per_eligible": sum(points) / total if total else None,
        "profit_factor": positive / negative if negative else (None if not positive else float("inf")),
        "mean_winner": float(np.mean(wins)) if wins else None,
        "median_winner": float(np.median(wins)) if wins else None,
        "mean_loser": float(np.mean(losses)) if losses else None,
        "median_loser": float(np.median(losses)) if losses else None,
        "max_drawdown_resolved_sequence": _drawdown(points),
        "longest_losing_streak": longest,
        "mean_holding_minutes": float(np.mean(durations)) if durations else None,
        "median_holding_minutes": float(np.median(durations)) if durations else None,
        "mfe_through_terminal_bar": _q(mfe), "mae_through_terminal_bar": _q(mae),
        "mean_stop_distance_points": float(np.mean([r["stop_distance"] for r in rows
                                                     if r.get("stop_distance") is not None
                                                     and not r["outcome"].startswith("EXCLUDED")]))
        if any(r.get("stop_distance") is not None and not r["outcome"].startswith("EXCLUDED") for r in rows) else None,
        "mean_target_distance_points": float(np.mean([r["target_distance"] for r in rows
                                                       if r.get("target_distance") is not None]))
        if any(r.get("target_distance") is not None for r in rows) else None,
    }


def _summaries(rows):
    dimensions = {
        "ALL": lambda r: "ALL", "CHRONOLOGICAL_PERIOD": lambda r: r["period"],
        "YEAR": lambda r: r["year"], "MONTH": lambda r: r["month"],
        "OPTION_TYPE": lambda r: r["option_type"], "ITM_RANK": lambda r: r["itm_rank"],
        "ENTRY_TIME": lambda r: r["entry_bucket"],
    }
    policies = sorted({r["policy"] for r in rows})
    out = []
    for policy in policies:
        selected = [r for r in rows if r["policy"] == policy]
        for dimension, key_fn in dimensions.items():
            groups = defaultdict(list)
            for row in selected:
                groups[str(key_fn(row))].append(row)
            for group, items in groups.items():
                out.append({"policy": policy, "dimension": dimension, "group": group,
                            **_metrics(items)})
    return out


def _candidate_rows(events, cache):
    output = []
    for event in events:
        if event.get("strategy") != "EKALAYAVA":
            continue
        date = event["date"]
        entry_stamp = _timestamp(event["timestamp"])
        local = entry_stamp.tz_convert(IST)
        entry = float(event["entry"])
        target = float(event.get("opening_high", event["target"]))
        bars = cache.session(event["symbol"], date)
        event_anchors = {
            "A_STRUCTURAL_TROUGH": event.get("observed_reversal_structure_low"),
            "B_BREAKOUT_CANDLE": event.get("breakout_candle_low"),
            "D_OPENING_LOW": event.get("opening_low"),
        }
        for anchor_name, source_field in ANCHORS.items():
            anchor = event_anchors[anchor_name]
            for buffer in BUFFERS:
                stop = None if anchor is None else float(anchor) - buffer
                for fraction, target_name in TARGETS:
                    policy = _policy_name(anchor_name, buffer, target_name)
                    candidate_target = entry + fraction * (target-entry)
                    if anchor is None:
                        result = {"outcome": "EXCLUDED_ANCHOR_UNAVAILABLE",
                                  "reason": "required_causal_anchor_missing"}
                    else:
                        result = simulate_ekalayava_exit(
                            bars, entry_timestamp=entry_stamp, entry=entry,
                            initial_stop=stop, target=candidate_target,
                            expected_last_timestamp=_session_end(date))
                    output.append({
                        "policy": policy, "policy_family": anchor_name,
                        "anchor_alias": "C_RECOVERY_BASE_INVALIDATION" if anchor_name == "A_STRUCTURAL_TROUGH" else None,
                        "anchor_source_field": source_field, "anchor_price": anchor,
                        "buffer_points": buffer, "stop": stop,
                        "stop_distance": None if stop is None else entry-stop,
                        "target_policy": target_name, "target_fraction": fraction,
                        "target": candidate_target, "target_distance": candidate_target-entry,
                        "setup_id": event.get("baseline_id") or f"{event['symbol']}|{date}|{event['timestamp']}",
                        "date": date, "year": date[:4], "month": date[:7], "period": _period(date),
                        "timestamp_utc": event["timestamp"], "entry_time_ist": local.strftime("%H:%M"),
                        "entry_bucket": _entry_bucket(local.hour), "symbol": event["symbol"],
                        "option_type": event["option_type"], "itm_rank": event["itm_rank"],
                        "entry": entry, "opening_high": target, "opening_low": event.get("opening_low"),
                        "breakdown_timestamp_utc": event.get("breakdown_timestamp"),
                        "swing_high": event.get("swing_high"),
                        "swing_high_timestamp_utc": event.get("swing_high_timestamp"),
                        "breakout_timestamp_utc": event.get("breakout_timestamp"),
                        "breakout_candle_low": event.get("breakout_candle_low"),
                        "outcome": result["outcome"], "reason": result.get("reason"),
                        "exit_timestamp": result.get("exit_timestamp"),
                        "exit_price": result.get("exit_price"), "points": result.get("points"),
                        "holding_minutes": result.get("holding_minutes"),
                        "active_stop_at_exit": result.get("active_stop_at_exit"),
                        "stop_updates_json": json.dumps(result.get("stop_updates", []), separators=(",", ":")),
                        "mfe_through_terminal_bar": result.get("mfe_through_terminal_bar"),
                        "mae_through_terminal_bar": result.get("mae_through_terminal_bar"),
                        "terminal_bar_excursion_order_unknown": result.get("terminal_bar_excursion_order_unknown"),
                        "source_bar_count": len(bars),
                    })

        # Trailing comparison is deliberately separate: A trough minus 2,
        # Opening High target, tighten only after completed lower-low vs 2 bars.
        anchor = event_anchors["A_STRUCTURAL_TROUGH"]
        stop = None if anchor is None else float(anchor)-TRAIL_BUFFER
        trail_policy = "TRAIL_CAUSAL_LOWER_LOW_B2_TP100"
        if anchor is None:
            result = {"outcome": "EXCLUDED_ANCHOR_UNAVAILABLE", "reason": "structural_anchor_missing"}
        else:
            result = simulate_ekalayava_exit(
                bars, entry_timestamp=entry_stamp, entry=entry, initial_stop=stop,
                target=target, expected_last_timestamp=_session_end(date), trailing=True,
                trail_buffer=TRAIL_BUFFER)
        output.append({
            "policy": trail_policy, "policy_family": "TRAILING_SEPARATE",
            "anchor_alias": None, "anchor_source_field": ANCHORS["A_STRUCTURAL_TROUGH"],
            "anchor_price": anchor, "buffer_points": TRAIL_BUFFER, "stop": stop,
            "stop_distance": None if stop is None else entry-stop,
            "target_policy": "TP100_OPENING_HIGH", "target_fraction": 1.0,
            "target": target, "target_distance": target-entry,
            "setup_id": event.get("baseline_id") or f"{event['symbol']}|{date}|{event['timestamp']}",
            "date": date, "year": date[:4], "month": date[:7], "period": _period(date),
            "timestamp_utc": event["timestamp"], "entry_time_ist": local.strftime("%H:%M"),
            "entry_bucket": _entry_bucket(local.hour), "symbol": event["symbol"],
            "option_type": event["option_type"], "itm_rank": event["itm_rank"],
            "entry": entry, "opening_high": target, "opening_low": event.get("opening_low"),
            "breakdown_timestamp_utc": event.get("breakdown_timestamp"),
            "swing_high": event.get("swing_high"),
            "swing_high_timestamp_utc": event.get("swing_high_timestamp"),
            "breakout_timestamp_utc": event.get("breakout_timestamp"),
            "breakout_candle_low": event.get("breakout_candle_low"),
            "outcome": result["outcome"], "reason": result.get("reason"),
            "exit_timestamp": result.get("exit_timestamp"), "exit_price": result.get("exit_price"),
            "points": result.get("points"), "holding_minutes": result.get("holding_minutes"),
            "active_stop_at_exit": result.get("active_stop_at_exit"),
            "stop_updates_json": json.dumps(result.get("stop_updates", []), separators=(",", ":")),
            "mfe_through_terminal_bar": result.get("mfe_through_terminal_bar"),
            "mae_through_terminal_bar": result.get("mae_through_terminal_bar"),
            "terminal_bar_excursion_order_unknown": result.get("terminal_bar_excursion_order_unknown"),
            "source_bar_count": len(bars),
        })
    return output


def _select_candidates(summaries):
    families = {
        "A_STRUCTURAL_TROUGH": "A_STRUCTURAL_TROUGH",
        "B_BREAKOUT_CANDLE": "B_BREAKOUT_CANDLE",
        "D_OPENING_LOW": "D_OPENING_LOW",
        "TRAILING_SEPARATE": "TRAIL_CAUSAL_LOWER_LOW_B2_TP100",
    }
    baseline_entries = 191
    selections = {}
    for family, policy_prefix in families.items():
        candidates = [r for r in summaries if r["dimension"] == "CHRONOLOGICAL_PERIOD"
                      and r["group"] == TRAIN and r["policy"].startswith(policy_prefix)]
        if family == "TRAILING_SEPARATE":
            candidates = [r for r in candidates if r["policy"] == policy_prefix]
        candidate = max(candidates, key=lambda r: (
            r["expectancy_per_eligible"] if r["expectancy_per_eligible"] is not None else float("-inf"),
            -(r["max_drawdown_resolved_sequence"] or 0), -r["longest_losing_streak"])) if candidates else None
        if candidate is None:
            selections[family] = {"selection": None, "validation": "NO_TRAIN_DATA"}
            continue
        val = next(r for r in summaries if r["policy"] == candidate["policy"]
                   and r["dimension"] == "CHRONOLOGICAL_PERIOD" and r["group"] == VALIDATION)
        checks = {
            "minimum_25_validation_entries": val["valid_entries"] >= 25,
            "positive_validation_expectancy_per_eligible_entry":
                (val["expectancy_per_eligible"] or 0) > 0,
            "validation_profit_factor_above_one": (val["profit_factor"] or 0) > 1,
            "validation_resolution_rate_at_least_90_percent":
                (val["resolution_rate_of_valid"] or 0) >= .90,
            "ambiguous_fraction_below_10_percent":
                (val["ambiguous"] / val["valid_entries"] if val["valid_entries"] else 1) < .10,
        }
        selections[family] = {
            "selected_using_train_only": candidate,
            "validation_metrics": val,
            "validation_checks": checks,
            "validation_decision": "SURVIVES_SCREEN" if all(checks.values()) else "REJECTED",
            "later_incomplete_sep_check": next((r for r in summaries
                if r["policy"] == candidate["policy"] and r["dimension"] == "CHRONOLOGICAL_PERIOD"
                and r["group"] == LATER_CHECK), None),
        }
    return {
        "data_scope": "saved 2026-01-01 through 2026-09-29 only; requested 2025-H2 unavailable and no supported bounded historical retrieval was attempted",
        "chronological_development": "2026-01-01 through 2026-06-30",
        "chronological_validation": "2026-07-01 through 2026-08-31",
        "later_period_check_not_untouched_holdout": "2026-09-01 through 2026-09-30; Sep 30 underlying absent and option coverage incomplete",
        "predeclared_family_selection_rule": "For each predefined family, maximize gross points per eligible entry in Jan-Jun only; tie-break by lower resolved-sequence drawdown then shorter loss streak. No later period used for selection.",
            "predeclared_validation_rejection_rule": "Require >=25 valid validation entries, positive gross points per eligible entry, PF>1, >=90% of valid entries resolved, and <10% ambiguity; no replacement selected from validation or Sep.",
        "policy_formulae": {
            "A_STRUCTURAL_TROUGH": "pre-entry min low from first opening-low breakdown through the completed bar immediately before breakout; stop = anchor - buffer",
            "B_BREAKOUT_CANDLE": "completed breakout candle low; stop = low - buffer; activates only after entry close",
            "C_RECOVERY_BASE_INVALIDATION": "same recorded causal trough as A because no distinct base boundary is encoded; aliases A; no duplicate simulation",
            "D_OPENING_LOW": "option premium Opening Low; stop = opening_low - buffer",
            "buffers_points": list(BUFFERS),
            "targets": [{"name": n, "fraction": f} for f, n in TARGETS],
            "gap_execution": "open <= active stop fills at open; intrabar stop touch fills at stop; target fills at target; same bar both ambiguous unless open establishes first touch",
            "end_of_session": "if path is complete and neither barrier touched, close at 15:25 candle close; missing interval or missing final candle is unresolved",
            "trailing": "separate A-buffer-2 initial stop; after each completed post-entry bar, if low < prior two completed lows, update to max(old stop, low - 2); updated stop first active on next bar; target Opening High",
        },
        "families": selections,
        "canonical_exit_adoption": "NONE; experimental policies are not canonical or production changes",
    }


def _l2l_entry_quality(events, cache):
    rows = []
    for event in events:
        if event.get("strategy") != "LEVEL_TO_LEVEL":
            continue
        date, symbol = event["date"], event["symbol"]
        entry_stamp = _timestamp(event["timestamp"])
        local = entry_stamp.tz_convert(IST)
        bars = cache.session(symbol, date)
        idx = next((i for i, bar in enumerate(bars) if bar["timestamp"] == entry_stamp), None)
        source_outcome = event.get("outcome")
        corrected_outcome = source_outcome
        if float(event["entry"]) >= float(event["opening_high"]):
            # The existing baseline replay counted one entry at/above its
            # Opening High target as a TARGET. Preserve the source label but
            # classify it as skipped for entry-quality denominators.
            corrected_outcome = "SKIPPED_TARGET_ALREADY_REACHED"
        row = {
            "date": date, "year": date[:4], "month": date[:7], "period": _period(date),
            "timestamp_utc": event["timestamp"], "entry_time_ist": local.strftime("%H:%M"),
            "entry_bucket": _entry_bucket(local.hour), "symbol": symbol,
            "option_type": event["option_type"], "itm_rank": event["itm_rank"],
            "entry": float(event["entry"]), "opening_high": float(event["opening_high"]),
            "opening_low": float(event["opening_low"]), "target_distance": float(event["opening_high"])-float(event["entry"]),
            "opening_range_size": float(event["opening_high"])-float(event["opening_low"]),
            "baseline_outcome": corrected_outcome, "source_baseline_outcome": source_outcome,
            "points": None if corrected_outcome.startswith("SKIPPED") else event.get("points_gained_lost"),
            "mfe": event.get("mfe"), "mae": event.get("mae"),
            "time_to_exit_minutes_source": None if corrected_outcome.startswith("SKIPPED") else event.get("time_to_exit_minutes"),
            "first_post_entry_bar_adverse": None, "pre_entry_low": None,
            "pre_entry_high": None, "pre_entry_trough": None,
            "entry_minus_opening_close": None, "entry_minus_breakdown_close": None,
            "rebound_from_pre_entry_trough": None,
            "mfe_before_stop_bar": None, "mfe_fraction_target_before_stop": None,
            "source_bar_count": len(bars), "entry_bar_available": idx is not None,
        }
        if idx is not None and bars:
            opening = bars[0]
            before = bars[:idx+1]
            event_bars = bars[idx+1:]
            row["pre_entry_low"] = min(float(x["low"]) for x in before)
            row["pre_entry_high"] = max(float(x["high"]) for x in before)
            row["pre_entry_trough"] = row["pre_entry_low"]
            row["entry_minus_opening_close"] = float(event["entry"])-float(opening["close"])
            breakdown = next((b for b in before[1:] if float(b["low"]) < float(event["opening_low"])
                              and float(b["close"]) < float(b["open"])), None)
            if breakdown is not None:
                row["breakdown_timestamp_utc"] = breakdown["timestamp"].isoformat()
                row["entry_minus_breakdown_close"] = float(event["entry"])-float(breakdown["close"])
            row["rebound_from_pre_entry_trough"] = float(event["entry"])-row["pre_entry_trough"]
            if event_bars:
                row["first_post_entry_bar_adverse"] = float(event_bars[0]["low"]) < float(event["entry"])
            if event.get("outcome") == "SL" and event.get("exit_time"):
                stop_stamp = _timestamp(event["exit_time"])
                stop_idx = next((i for i,b in enumerate(bars) if b["timestamp"] == stop_stamp), None)
                if stop_idx is not None:
                    strict = bars[idx+1:stop_idx]
                    best = max([0.0]+[float(b["high"])-float(event["entry"]) for b in strict])
                    row["mfe_before_stop_bar"] = best
                    distance = float(event["opening_high"])-float(event["entry"])
                    row["mfe_fraction_target_before_stop"] = best/distance if distance>0 else None
        rows.append(row)
    return rows


def _quality_summaries(rows):
    dims = {"ALL":lambda r:"ALL", "MONTH":lambda r:r["month"],
            "OPTION_TYPE":lambda r:r["option_type"], "ITM_RANK":lambda r:r["itm_rank"],
            "ENTRY_TIME":lambda r:r["entry_bucket"], "PERIOD":lambda r:r["period"]}
    output=[]
    entered=[r for r in rows if not str(r["baseline_outcome"]).startswith("SKIPPED")]
    for name,keyfn in dims.items():
        groups=defaultdict(list)
        for r in entered: groups[str(keyfn(r))].append(r)
        for group,items in groups.items():
            output.append({"dimension":name,"group":group,"entries":len(items),
                "targets":sum(r["baseline_outcome"]=="TARGET" for r in items),
                "stops":sum(r["baseline_outcome"]=="SL" for r in items),
                "mean_opening_range":_q([r["opening_range_size"] for r in items])["mean"],
                "median_target_distance":_q([r["target_distance"] for r in items])["median"],
                "mean_entry_minus_opening_close":_q([r["entry_minus_opening_close"] for r in items])["mean"],
                "mean_rebound_from_pre_entry_trough":_q([r["rebound_from_pre_entry_trough"] for r in items])["mean"],
                "mean_mfe":_q([r["mfe"] for r in items])["mean"],
                "median_mfe":_q([r["mfe"] for r in items])["median"],
                "mean_mae":_q([r["mae"] for r in items])["mean"],
                "median_mae":_q([r["mae"] for r in items])["median"],
                "first_post_entry_adverse_count":sum(r["first_post_entry_bar_adverse"] is True for r in items),
                "first_post_entry_adverse_fraction":sum(r["first_post_entry_bar_adverse"] is True for r in items)/len(items),
                "mean_pre_stop_mfe_fraction_of_target":_q([r["mfe_fraction_target_before_stop"] for r in items if r["baseline_outcome"]=="SL"])["mean"]})
    return output


def main():
    REPORTS.mkdir(exist_ok=True, parents=True)
    data=json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    events=data["trade_events"]
    cache=CandleCache()
    eka=_candidate_rows(events,cache)
    summary=_summaries(eka)
    l2l=_l2l_entry_quality(events,cache)
    l2l_summary=_quality_summaries(l2l)
    selection=_select_candidates(summary)
    _write_csv(REPORTS/"ekalayava_exit_policy_trades.csv",eka)
    _write_csv(REPORTS/"ekalayava_exit_policy_summary.csv",summary)
    _write_csv(REPORTS/"multi_year_l2l_entry_quality.csv",l2l)
    _write_csv(REPORTS/"multi_year_l2l_entry_quality_summary.csv",l2l_summary)
    (REPORTS/"ekalayava_exit_candidate_selection.json").write_text(
        json.dumps(selection,indent=2,sort_keys=True,default=str)+"\n",encoding="utf-8")
    print(json.dumps({"ekalayava_entry_count":sum(e.get("strategy")=="EKALAYAVA" for e in events),
        "ekalayava_policy_count":len({r["policy"] for r in eka}),
        "ekalayava_rows":len(eka),"l2l_entry_quality_rows":len(l2l),
        "missing_option_files":sorted(cache.missing_files),
        "selection":{k:v.get("validation_decision") for k,v in selection["families"].items()},
        "outputs":["reports/ekalayava_exit_policy_trades.csv",
                   "reports/ekalayava_exit_policy_summary.csv",
                   "reports/ekalayava_exit_candidate_selection.json",
                   "reports/multi_year_l2l_entry_quality.csv",
                   "reports/multi_year_l2l_entry_quality_summary.csv"]},indent=2))


if __name__ == "__main__":
    main()
