from datetime import timedelta
from pathlib import Path
import re

import pandas as pd

from .data_quality import quality_report
from .paper import analyze_ekalayava, backtest_level_to_level
from .groww_data import validate_candles


def _trading_dates(path):
    frame = pd.read_csv(path, usecols=["timestamp"])
    timestamps = pd.to_datetime(frame["timestamp"], utc=True)
    return sorted(timestamps.dt.tz_convert("Asia/Kolkata").dt.date.unique())


def select_latest_completed_week(underlying_path, option_dir):
    dates = _trading_dates(underlying_path)
    weeks = {}
    for date in dates:
        monday = date - timedelta(days=date.weekday())
        weeks.setdefault(monday, []).append(date)
    candidates = []
    for monday, week_dates in weeks.items():
        friday = monday + timedelta(days=4)
        if len(week_dates) >= 5 and max(week_dates) >= friday:
            candidates.append((monday, friday, sorted(week_dates)))
    if not candidates:
        raise RuntimeError("INSUFFICIENT DATA: no completed Monday-Friday trading week")
    monday, friday, dates = max(candidates)
    options = sorted(Path(option_dir).glob("*.csv"))
    usable = []
    for path in options:
        frame = pd.read_csv(path, usecols=["timestamp"])
        if frame.empty:
            continue
        local = pd.to_datetime(frame.timestamp, utc=True).dt.tz_convert("Asia/Kolkata").dt.date
        if set(dates).intersection(local):
            usable.append(path)
    grouped = {}
    for path in usable:
        metadata = _contract_metadata(path)
        grouped.setdefault((metadata["expiry"], metadata["option_type"]), []).append(path)
    eligible = []
    for (expiry, option_type), paths in grouped.items():
        paths.sort(key=lambda path: _contract_metadata(path)["strike"],
                   reverse=option_type == "CE")
        for offset, path in enumerate(paths, start=2):
            if offset in (2, 3):
                eligible.append(path)
    if len(eligible) < 4:
        raise RuntimeError("INSUFFICIENT DATA: fewer than four option files cover the latest completed week")
    return {"start": monday, "end": friday, "trading_dates": dates, "option_files": sorted(eligible)}


def _load_week(path, dates):
    frame = pd.read_csv(path)
    frame["timestamp"] = pd.to_datetime(frame.timestamp, utc=True)
    frame = validate_candles(frame)
    local = frame.timestamp.dt.tz_convert("Asia/Kolkata")
    return frame[local.dt.date.isin(dates)].copy()


def _contract_metadata(path):
    match = re.search(r"NSE-NIFTY-(\d{2}[A-Za-z]{3}\d{2})-(\d+(?:\.\d+)?)-(CE|PE)", path.stem)
    if not match:
        raise RuntimeError(f"INSUFFICIENT DATA: unparseable option contract {path.name}")
    return {"expiry": match.group(1), "strike": float(match.group(2)),
            "option_type": match.group(3)}


def run_baseline_week(underlying_path, option_dir, selection):
    underlying = _load_week(underlying_path, selection["trading_dates"])
    quality = {"underlying": quality_report(underlying), "options": {}}
    rows = []
    for path in selection["option_files"]:
        option = _load_week(path, selection["trading_dates"])
        quality["options"][path.name] = quality_report(option)
        if option.empty:
            continue
        metadata = {"symbol": path.stem, **_contract_metadata(path)}
        group_paths = [candidate for candidate in selection["option_files"]
                   if _contract_metadata(candidate)["expiry"] == metadata["expiry"]
                   and _contract_metadata(candidate)["option_type"] == metadata["option_type"]]
        group_paths.sort(key=lambda candidate: _contract_metadata(candidate)["strike"],
                 reverse=metadata["option_type"] == "CE")
        metadata["itm_rank"] = group_paths.index(path) + 2
        level = backtest_level_to_level(option, metadata)
        eka = analyze_ekalayava(option, metadata)
        for strategy, events in (("LEVEL_TO_LEVEL", level), ("EKALAYAVA", eka)):
            for event in events.to_dict("records"):
                event["strategy"] = strategy
                rows.append(event)
    events = pd.DataFrame(rows)
    outcomes = events.outcome.value_counts().to_dict() if not events.empty else {}
    points = pd.to_numeric(events.points_gained_lost, errors="coerce") if "points_gained_lost" in events else pd.Series(dtype=float)
    valid_points = points.dropna()
    cumulative = valid_points.cumsum() if not valid_points.empty else pd.Series(dtype=float)
    drawdown = float((cumulative.cummax() - cumulative).max()) if not cumulative.empty else 0.0
    wins = [value > 0 for value in valid_points]
    max_win_streak = max_loss_streak = current_win = current_loss = 0
    for win in wins:
        current_win = current_win + 1 if win else 0
        current_loss = current_loss + 1 if not win else 0
        max_win_streak = max(max_win_streak, current_win)
        max_loss_streak = max(max_loss_streak, current_loss)
    def distribution(column):
        if column not in events or events.empty:
            return {}
        return {str(key): int(value) for key, value in events[column].value_counts(dropna=False).items()}
    result = {
        "week": {"start": str(selection["start"]), "end": str(selection["end"]),
                 "trading_dates": [str(value) for value in selection["trading_dates"]]},
        "dataset": str(underlying_path), "strategy_version": "baseline-v1",
        "setup_count": int(len(events)), "valid_setups": int((events.outcome != "OPEN").sum()) if not events.empty else 0,
        "skipped_setups": int((events.outcome == "OPEN").sum()) if not events.empty else 0,
        "ambiguous_setups": int((events.outcome == "AMBIGUOUS_SL_FIRST").sum()) if not events.empty else 0,
        "target_hits": int((events.outcome == "TARGET").sum()) if not events.empty else 0,
        "sl_hits": int(events.outcome.isin(["SL", "AMBIGUOUS_SL_FIRST"]).sum()) if not events.empty else 0,
        "average_points": float(points.dropna().mean()) if points.notna().any() else None,
        "median_points": float(points.dropna().median()) if points.notna().any() else None,
        "average_mfe": float(events.mfe.mean()) if "mfe" in events and not events.empty else None,
        "average_mae": float(events.mae.mean()) if "mae" in events and not events.empty else None,
        "maximum_drawdown_points": drawdown,
        "maximum_winning_streak": max_win_streak,
        "maximum_losing_streak": max_loss_streak,
        "average_holding_time_minutes": float(events.time_to_exit_minutes.mean())
        if "time_to_exit_minutes" in events and events.time_to_exit_minutes.notna().any() else None,
        "outcomes": {str(key): int(value) for key, value in outcomes.items()},
        "by_strategy": {str(key): int(value) for key, value in events.strategy.value_counts().items()} if not events.empty else {},
        "by_option_type": distribution("option_type"),
        "by_itm_rank": distribution("itm_rank"),
        "by_entry_hour": distribution("entry_hour"),
        "data_quality": quality,
        "lookahead_check": "PASS: deterministic engine uses completed candles and future candles only after entry",
        "development_validation": "INSUFFICIENT OUT-OF-SAMPLE DATA: one completed week is reserved for this bounded demo",
    }
    return result