"""Reproducible period-based, paper-only historical research runner."""

import argparse
from collections import defaultdict
from datetime import date, timedelta
import json
from pathlib import Path

import pandas as pd

from .data_quality import quality_report
from .config import CFG
from .groww_data import DATA_COLUMNS, validate_candles
from .weekly_experiment import run_baseline_week, select_requested_period


DEFAULT_START = date(2026, 4, 25)
DEFAULT_END = date(2026, 9, 25)
EXPECTED_CONTRACT_PAIRS = {(kind, rank) for kind in ("CE", "PE") for rank in (2, 3)}


def _source_rows(path):
    frame = pd.read_csv(path)
    if frame.empty:
        return frame, {"path": str(path), "rows": 0, "empty": True}
    for column in DATA_COLUMNS:
        if column not in frame:
            frame[column] = None
    raw_count = len(frame)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
    invalid_timestamps = int(frame["timestamp"].isna().sum())
    frame = frame.loc[frame.timestamp.notna(), DATA_COLUMNS].copy()
    duplicate_count = int(frame.timestamp.duplicated(keep=False).sum())
    quality = quality_report(frame)
    metadata = {"path": str(path), "rows": raw_count, "invalid_timestamps": invalid_timestamps,
                "duplicate_rows": duplicate_count, "invalid_ohlc_rows": quality["invalid_ohlc_count"],
                "date_min": quality["trading_dates"][0] if quality["trading_dates"] else None,
                "date_max": quality["trading_dates"][-1] if quality["trading_dates"] else None}
    return frame, metadata


def _merge_files(paths, destination):
    frames = []
    sources = []
    for priority, path in enumerate(paths):
        frame, source = _source_rows(path)
        sources.append(source)
        if frame.empty:
            continue
        frame["_source_priority"] = priority
        frame["_source_row"] = range(len(frame))
        frames.append(frame)
    if not frames:
        destination.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(columns=DATA_COLUMNS).to_csv(destination, index=False)
        return {"sources": sources, "rows": 0, "duplicate_timestamps": 0,
                "conflicting_duplicate_timestamps": 0}
    combined = pd.concat(frames, ignore_index=True, sort=False)
    duplicated = combined.timestamp.duplicated(keep=False)
    duplicate_keys = int(combined.loc[duplicated, "timestamp"].nunique())
    conflicts = 0
    if duplicated.any():
        for _, group in combined.loc[duplicated].groupby("timestamp", sort=False):
            if len(group[DATA_COLUMNS[1:5]].drop_duplicates()) > 1:
                conflicts += 1
    combined = combined.sort_values(["_source_priority", "_source_row"], kind="stable")
    combined = combined.drop_duplicates("timestamp", keep="last")
    combined = validate_candles(combined[DATA_COLUMNS])
    destination.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(destination, index=False)
    return {"sources": sources, "rows": int(len(combined)),
            "duplicate_timestamps": duplicate_keys,
            "conflicting_duplicate_timestamps": conflicts,
            "quality": quality_report(combined)}


def assemble_sources(underlying_paths, option_dirs, output_dir):
    """Merge exact source rows without filling gaps; later paths win timestamp conflicts."""
    output = Path(output_dir)
    underlying_paths = [Path(path) for path in underlying_paths]
    option_dirs = [Path(path) for path in option_dirs]
    underlying_report = _merge_files(underlying_paths, output / "nifty_5m.csv")
    by_contract = defaultdict(list)
    option_sources = []
    for directory in option_dirs:
        for path in sorted(directory.glob("*.csv")):
            if path.stem == "nifty_5m":
                continue
            by_contract[path.stem].append(path)
            option_sources.append(str(path))
    option_reports = {}
    for symbol, paths in sorted(by_contract.items()):
        option_reports[symbol] = _merge_files(paths, output / "options" / f"{symbol}.csv")
    manifest = {"merge_policy": "exact timestamps only; no interpolation; later listed sources win conflicts",
                "underlying": underlying_report, "option_file_count": len(option_reports),
                "option_sources": option_sources, "options": option_reports}
    (output / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def _summary(group):
    outcomes = group.outcome if "outcome" in group else pd.Series(dtype=str)
    points = pd.to_numeric(group.get("points_gained_lost", pd.Series(dtype=float)), errors="coerce").dropna()
    targets = int((outcomes == "TARGET").sum()) if len(outcomes) else 0
    stop_losses = int((outcomes == "SL").sum()) if len(outcomes) else 0
    resolved_exits = targets + stop_losses
    strategy_values = set(group.strategy.astype(str)) if "strategy" in group else set()
    win_rate = targets / resolved_exits if resolved_exits else None
    win_rate_reason = None
    if strategy_values == {"EKALAYAVA"}:
        win_rate = None
        win_rate_reason = "Stop-loss is undefined for Ekalayava; win rate is not defined."
    return {"setups": int(len(group)),
            "valid_setups": int((outcomes != "SKIPPED_SL_ALREADY_BREACHED").sum()) if len(outcomes) else 0,
            "skipped": int((outcomes == "SKIPPED_SL_ALREADY_BREACHED").sum()) if len(outcomes) else 0,
            "targets": targets,
            "stop_losses": stop_losses,
            "ambiguous": int(outcomes.isin(["AMBIGUOUS", "AMBIGUOUS_SL_FIRST"]).sum()) if len(outcomes) else 0,
            "unresolved": int((outcomes == "OPEN").sum()) if len(outcomes) else 0,
            "target_rate_per_setup": targets / len(group) if len(group) else None,
            "win_rate_resolved_target_or_sl": win_rate,
            "win_rate_denominator": resolved_exits,
            "win_rate_status": win_rate_reason or "Targets divided by resolved TARGET/SL outcomes; OPEN and AMBIGUOUS excluded.",
            "total_points": float(points.sum()) if not points.empty else None,
            "average_points": float(points.mean()) if not points.empty else None,
            "median_points": float(points.median()) if not points.empty else None,
            "average_mfe": float(group.mfe.mean()) if "mfe" in group and not group.empty else None,
            "average_mae": float(group.mae.mean()) if "mae" in group and not group.empty else None,
            "average_holding_time_minutes": float(group.time_to_exit_minutes.mean())
                if "time_to_exit_minutes" in group and group.time_to_exit_minutes.notna().any() else None}


def enrich_period_report(result, selection, requested_start, requested_end, manifest=None):
    trade_rows = result.pop("events", [])
    events = pd.DataFrame(trade_rows)
    rows = []
    eligibility = {(item["date"], item["option_type"], item["itm_rank"]): item
                   for item in selection.get("contract_eligibility", [])}
    for trading_date in selection["trading_dates"]:
        for strategy in ("LEVEL_TO_LEVEL", "EKALAYAVA"):
            for option_type, rank in sorted(EXPECTED_CONTRACT_PAIRS):
                pair = eligibility.get((str(trading_date), option_type, rank))
                if events.empty:
                    group = pd.DataFrame()
                else:
                    local = pd.to_datetime(events.timestamp, utc=True).dt.tz_convert("Asia/Kolkata").dt.date
                    group = events.loc[(local == trading_date) & (events.strategy == strategy)
                                       & (events.option_type == option_type) & (events.itm_rank == rank)]
                stats = _summary(group)
                stats.update({"date": str(trading_date), "strategy": strategy,
                    "option_type": option_type, "itm_rank": rank,
                    "expiry": pair.get("expiry") if pair else None,
                    "data_status": ("MISSING_CONTRACT_DAY" if pair is None or not pair.get("contract_day_has_candles", False) else
                                    "MISSING_OPENING_CANDLE" if not pair.get("opening_candle_available", False) else
                                    "INTRADAY_GAPS" if pair.get("missing_intervals", 0) else "AVAILABLE"),
                    "option_candles": pair.get("data_coverage", {}).get("total_candles", 0) if pair else 0,
                    "missing_intervals": pair.get("missing_intervals") if pair else None})
                rows.append(stats)
    cross = {}
    if not events.empty:
        for strategy, group in events.groupby("strategy", dropna=False):
            result.setdefault("by_strategy", {}).setdefault(str(strategy), {}).update(_summary(group))
        level_group = events.loc[events.strategy == "LEVEL_TO_LEVEL"]
        if not level_group.empty:
            l2l_summary = _summary(level_group)
            result["metrics"]["level_to_level_win_rate_resolved_target_or_sl"] = l2l_summary["win_rate_resolved_target_or_sl"]
            result["metrics"]["level_to_level_win_rate_denominator"] = l2l_summary["win_rate_denominator"]
        for keys, group in events.groupby(["strategy", "option_type", "itm_rank"], dropna=False):
            strategy, option_type, rank = keys
            cross[f"{strategy}|{option_type}|ITM{rank}"] = _summary(group)
        local_times = pd.to_datetime(events.timestamp, utc=True).dt.tz_convert("Asia/Kolkata")
        events = events.assign(_local_date=local_times.dt.date.astype(str),
                               _local_time=local_times.dt.strftime("%H:%M"))
        result["by_expiry"] = {str(expiry): _summary(group)
            for expiry, group in events.groupby("expiry", dropna=False)}
        result["by_date"] = {str(trading_date): _summary(group)
            for trading_date, group in events.groupby("_local_date", dropna=False)}
        result["by_entry_time"] = {str(entry_time): _summary(group)
            for entry_time, group in events.groupby("_local_time", dropna=False)}
    result["strategy_option_type_itm_rank"] = cross
    result["daily_report"] = rows
    result["trade_events"] = trade_rows
    pair_count = len(selection["trading_dates"]) * len(EXPECTED_CONTRACT_PAIRS)
    present = sum(1 for item in eligibility.values() if item.get("contract_day_has_candles", False))
    actual_dates = [str(value) for value in selection["trading_dates"]]
    result["baseline_id"] = "BASELINE-V1"
    result["requested_period"] = {"start": str(requested_start), "end": str(requested_end)}
    result["actual_data_period"] = {"start": actual_dates[0] if actual_dates else None,
                                    "end": actual_dates[-1] if actual_dates else None}
    period_edges_present = bool(actual_dates) and actual_dates[0] <= str(requested_start) \
        and actual_dates[-1] >= str(requested_end)
    result["data_coverage_status"] = "PARTIAL_DATA" if present < pair_count or not period_edges_present \
        else "AVAILABLE_COVERAGE_REQUIRES_EXCHANGE_CALENDAR"
    uncovered_ranges = []
    if not actual_dates:
        uncovered_ranges.append({"start": str(requested_start), "end": str(requested_end),
                                 "reason": "no underlying source dates"})
    else:
        actual_start = date.fromisoformat(actual_dates[0])
        actual_end = date.fromisoformat(actual_dates[-1])
        if requested_start < actual_start:
            uncovered_ranges.append({"start": str(requested_start),
                "end": str(actual_start - timedelta(days=1)), "reason": "no underlying source files"})
        if actual_end < requested_end:
            uncovered_ranges.append({"start": str(actual_end + timedelta(days=1)),
                "end": str(requested_end), "reason": "no underlying source files"})
    by_day = selection.get("contract_coverage_by_date", {})
    complete_contract_days = 0
    partial_contract_days = 0
    missing_contract_days = 0
    for trading_date in selection["trading_dates"]:
        records = [eligibility.get((str(trading_date), kind, rank))
                   for kind, rank in EXPECTED_CONTRACT_PAIRS]
        present_records = [item for item in records if item is not None]
        has_gaps = any(item.get("missing_intervals", 0) or not item.get("opening_candle_available", False)
                       or not item.get("contract_day_has_candles", False)
                       for item in present_records)
        if len(present_records) == len(EXPECTED_CONTRACT_PAIRS) and not has_gaps:
            complete_contract_days += 1
        elif present_records or by_day.get(trading_date, {}).get("missing"):
            partial_contract_days += 1
        else:
            missing_contract_days += 1
    calendar_weekdays = (requested_end - requested_start).days + 1
    weekday_dates = [requested_start + timedelta(days=offset)
                     for offset in range(calendar_weekdays)
                     if (requested_start + timedelta(days=offset)).weekday() < 5]
    known_dates = set(selection.get("source_underlying_dates", selection["trading_dates"]))
    weekdays_without_source = [value.isoformat() for value in weekday_dates
                               if value not in known_dates]
    result["data_completeness"] = {
        "available_underlying_trading_dates": len(selection["trading_dates"]),
        "underlying_candles": result.get("data_quality", {}).get("underlying", {}).get("total_candles", 0),
        "option_candles": sum(item.get("data_coverage", {}).get("total_candles", 0)
                               for item in eligibility.values()),
        "complete_contract_days": complete_contract_days,
        "partial_contract_days": partial_contract_days,
        "missing_contract_days": missing_contract_days,
        "missing_opening_candles": sum(1 for item in eligibility.values()
                                        if not item.get("opening_candle_available", False)),
        "missing_underlying_opening_dates": selection.get("missing_underlying_opening_dates", []),
        "missing_option_intervals_between_observed_candles": sum(
            item.get("missing_intervals", 0) for item in eligibility.values()),
        "weekday_dates_without_underlying_source_data_holiday_status_unknown": weekdays_without_source,
        "uncovered_calendar_ranges": uncovered_ranges,
        "caveat": "A zero interval-gap count does not prove complete session edges; exchange calendar and session bounds are not inferred.",
    }
    result["contract_day_coverage"] = {"expected": pair_count, "available": present,
        "missing": pair_count - present,
        "availability_rate": present / pair_count if pair_count else 0.0,
        "by_option_type_itm_rank": {
            f"{kind}_ITM{rank}": sum(1 for key, item in eligibility.items()
                                     if key[1:] == (kind, rank) and item.get("contract_day_has_candles", False))
            for kind, rank in sorted(EXPECTED_CONTRACT_PAIRS)}}
    result["data_sources"] = manifest
    result["validation_status"] = "INSUFFICIENT OUT-OF-SAMPLE DATA; no strategy changes evaluated"
    groww_credentials_available = bool(CFG.api_key.strip() and
        ((CFG.api_secret.strip() and not CFG.totp.strip()) or
         (CFG.totp.strip() and not CFG.api_secret.strip())))
    result["download_status"] = {
        "attempted": False,
        "credentials_configured": groww_credentials_available,
        "reason": ("No download attempted by the report command." if groww_credentials_available else
                   "Groww read-only credentials are not configured; missing dates and contracts were not downloaded."),
    }
    result["strategy_rules"] = {
        "LEVEL_TO_LEVEL": "Opening levels from 09:15 option candle; red low below opening low; first later green candle close is the signal entry; SL is opening low minus 4 points; target is opening high; entries through 11:00 IST. A signal whose entry close is already at or below SL is reported as skipped because the stop has already been breached.",
        "EKALAYAVA": "Require a move below opening low; causal swing high is current high above prior two highs (left=2, right=0); a later completed candle must break and close above that reference before its high reaches opening high; entry is that candle close; target is opening high; SL is undefined.",
    }
    result["safety"] = {"EXECUTION_ALLOWED": False, "PAPER_ONLY": True,
                         "order_placement_or_modification_called": False}
    result["metrics"]["total_points"] = sum(
        value for value in (event.get("points_gained_lost") for event in trade_rows)
        if isinstance(value, (int, float)))
    return result


def main():
    parser = argparse.ArgumentParser(description="Run a reproducible paper-only requested-period baseline.")
    parser.add_argument("--start", type=date.fromisoformat, default=DEFAULT_START)
    parser.add_argument("--end", type=date.fromisoformat, default=DEFAULT_END)
    parser.add_argument("--underlying", action="append", required=True,
                        help="Underlying 5-minute CSV; repeat to merge sources in priority order")
    parser.add_argument("--option-dir", action="append", required=True,
                        help="Directory of option 5-minute CSV files; repeat to merge sources")
    parser.add_argument("--output-dir", default="data/derived/requested_period")
    parser.add_argument("--report", default="data/reports/baseline_v1_requested_period.json")
    args = parser.parse_args()
    if args.end < args.start:
        parser.error("--end must be on or after --start")
    manifest = assemble_sources(args.underlying, args.option_dir, args.output_dir)
    underlying_path = Path(args.output_dir) / "nifty_5m.csv"
    option_path = Path(args.output_dir) / "options"
    selection = select_requested_period(underlying_path, option_path, args.start, args.end)
    result = run_baseline_week(underlying_path, option_path, selection)
    result = enrich_period_report(result, selection, args.start, args.end, manifest)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"baseline_id": result["baseline_id"], "status": result["data_coverage_status"],
        "requested_period": result["requested_period"], "actual_data_period": result["actual_data_period"],
        "trading_days": len(result.get("week", {}).get("trading_dates", [])),
        "setups": result.get("setup_count", 0), "contract_day_coverage": result["contract_day_coverage"],
        "report": str(report_path)}, indent=2))


if __name__ == "__main__":
    main()
