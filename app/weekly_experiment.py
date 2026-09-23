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
    underlying = pd.read_csv(underlying_path)
    underlying["timestamp"] = pd.to_datetime(underlying["timestamp"], utc=True)
    local = underlying["timestamp"].dt.tz_convert("Asia/Kolkata")
    opening = underlying[local.dt.date == dates[0]].sort_values("timestamp")
    if opening.empty:
        raise RuntimeError("INSUFFICIENT DATA: selected week has no opening underlying candle")
    underlying_open = float(opening.iloc[0]["open"])
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
        declared_ranks = {_file_itm_rank(path) for path in paths}
        if declared_ranks.issubset({2, 3}) and None not in declared_ranks:
            eligible.extend(paths)
            continue
        paths = [path for path in paths if (
            option_type == "CE" and _contract_metadata(path)["strike"] < underlying_open
        ) or (
            option_type == "PE" and _contract_metadata(path)["strike"] > underlying_open
        )]
        paths.sort(key=lambda path: _contract_metadata(path)["strike"], reverse=option_type == "CE")
        eligible.extend(paths[1:3])
    if len(eligible) < 4:
        raise RuntimeError("INSUFFICIENT DATA: fewer than four option files cover the latest completed week")
    eligible = sorted(eligible)
    contract_eligibility = []
    for path in eligible:
        metadata = _contract_metadata(path)
        same_type = [candidate for candidate in eligible
                     if _contract_metadata(candidate)["expiry"] == metadata["expiry"]
                     and _contract_metadata(candidate)["option_type"] == metadata["option_type"]]
        same_type.sort(key=lambda candidate: _contract_metadata(candidate)["strike"],
                       reverse=metadata["option_type"] == "CE")
        rank = _file_itm_rank(path) or same_type.index(path) + 2
        contract_eligibility.append({"date": str(dates[0]), "underlying_price": underlying_open,
                                     "expiry": metadata["expiry"], "option_type": metadata["option_type"],
                                     "strike": metadata["strike"], "itm_rank": rank,
                                     "eligible": rank in (2, 3)})
    return {"start": monday, "end": friday, "trading_dates": dates, "option_files": eligible,
            "contract_eligibility": contract_eligibility, "underlying_open": underlying_open}


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


def _file_itm_rank(path):
    try:
        frame = pd.read_csv(path, usecols=["itm_rank"])
    except (KeyError, ValueError):
        return None
    values = pd.to_numeric(frame["itm_rank"], errors="coerce").dropna().unique()
    return int(values[0]) if len(values) == 1 else None


def run_baseline_week(underlying_path, option_dir, selection):
    underlying = _load_week(underlying_path, selection["trading_dates"])
    quality = {"underlying": quality_report(underlying), "options": {}}
    rows = []
    opening_price = float(underlying.sort_values("timestamp").iloc[0]["open"])
    eligibility = []
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
        is_itm = (metadata["option_type"] == "CE" and metadata["strike"] < opening_price) or \
             (metadata["option_type"] == "PE" and metadata["strike"] > opening_price)
        eligibility.append({"date": str(selection["start"]), "underlying_price": opening_price,
                    "expiry": metadata["expiry"], "option_type": metadata["option_type"],
                    "strike": metadata["strike"], "itm_rank": metadata["itm_rank"],
                    "expected_itm_relationship": "CE strike < underlying" if metadata["option_type"] == "CE" else "PE strike > underlying",
                    "actual_relationship": is_itm, "data_coverage": quality["options"][path.name],
                    "eligible": bool(is_itm and metadata["itm_rank"] in (2, 3))})
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
    strategy_breakdown = {}
    for strategy, group in events.groupby("strategy") if not events.empty else []:
        group_points = pd.to_numeric(group["points_gained_lost"], errors="coerce")
        valid_group = group_points.dropna()
        local_dates = pd.to_datetime(group["timestamp"], utc=True).dt.tz_convert("Asia/Kolkata").dt.date
        daily_points = valid_group.groupby(local_dates.loc[valid_group.index]).sum()
        strategy_breakdown[strategy] = {
            "days": int(local_dates.nunique()), "setups": int(len(group)),
            "valid_setups": int(valid_group.count()), "target_hits": int((group.outcome == "TARGET").sum()),
            "sl_hits": int(group.outcome.isin(["SL", "AMBIGUOUS_SL_FIRST"]).sum()),
            "open_outcomes": int((group.outcome == "OPEN").sum()), "points": float(valid_group.sum()) if not valid_group.empty else 0.0,
            "average_points_per_setup": float(valid_group.mean()) if not valid_group.empty else None,
            "average_daily_points": float(daily_points.mean()) if not daily_points.empty else None,
        }
    metrics = {
        "setup_count": int(len(events)), "valid_setups": int((events.outcome != "OPEN").sum()) if not events.empty else 0,
        "target_hits": int((events.outcome == "TARGET").sum()) if not events.empty else 0,
        "sl_hits": int(events.outcome.isin(["SL", "AMBIGUOUS_SL_FIRST"]).sum()) if not events.empty else 0,
        "open_outcomes": outcomes, "average_points": float(points.dropna().mean()) if points.notna().any() else None,
        "median_points": float(points.dropna().median()) if points.notna().any() else None,
        "average_mfe": float(events.mfe.mean()) if "mfe" in events and not events.empty else None,
        "average_mae": float(events.mae.mean()) if "mae" in events and not events.empty else None,
        "average_holding_time_minutes": float(events.time_to_exit_minutes.mean()) if "time_to_exit_minutes" in events and events.time_to_exit_minutes.notna().any() else None,
        "maximum_drawdown_points": drawdown, "maximum_winning_streak": max_win_streak,
        "maximum_losing_streak": max_loss_streak, "by_strategy": strategy_breakdown,
        "by_option_type": distribution("option_type"), "by_itm_rank": distribution("itm_rank"),
        "by_entry_hour": distribution("entry_hour"),
    }
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
        "by_strategy": strategy_breakdown,
        "by_option_type": distribution("option_type"),
        "by_itm_rank": distribution("itm_rank"),
        "by_entry_hour": distribution("entry_hour"),
        "data_quality": quality,
        "lookahead_check": "PASS: deterministic engine uses completed candles and future candles only after entry",
        "development_validation": "INSUFFICIENT OUT-OF-SAMPLE DATA: one completed week is reserved for this bounded demo",
        "contract_eligibility": eligibility,
        "metrics": metrics,
    }
    return result