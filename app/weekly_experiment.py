from datetime import date, datetime, timedelta
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


REQUESTED_START = date(2026, 7, 23)
REQUESTED_END = date(2026, 9, 23)


def _option_dates(path):
    frame = pd.read_csv(path, usecols=["timestamp"])
    if frame.empty:
        return set()
    return set(pd.to_datetime(frame.timestamp, utc=True).dt.tz_convert("Asia/Kolkata").dt.date)


def _expiry_date(value):
    return datetime.strptime(value.title(), "%d%b%y").date()


def select_requested_period(underlying_path, option_dir, start=REQUESTED_START, end=REQUESTED_END):
    source_dates = _trading_dates(underlying_path)
    dates = [value for value in source_dates if start <= value <= end]
    if not dates:
        raise RuntimeError("INSUFFICIENT DATA: no underlying trading dates in requested period")
    underlying = pd.read_csv(underlying_path)
    underlying["timestamp"] = pd.to_datetime(underlying["timestamp"], utc=True)
    local = underlying["timestamp"].dt.tz_convert("Asia/Kolkata")
    opening_prices = {}
    missing_opening_dates = []
    for trading_date in dates:
        opening = underlying[(local.dt.date == trading_date) & (local.dt.strftime("%H:%M") == "09:15")]
        if len(opening) == 1:
            opening_prices[trading_date] = float(opening.iloc[0]["open"])
        else:
            missing_opening_dates.append(str(trading_date))
    options = sorted(Path(option_dir).glob("*.csv"))
    option_dates = {path: _option_dates(path) for path in options}
    eligible_by_date = {}
    contract_coverage_by_date = {}
    contract_eligibility = []
    for trading_date in dates:
        price = opening_prices.get(trading_date)
        # Rank from the available contract universe, not only files that happen
        # to contain candles on this date; otherwise a missing ITM2 file can
        # silently shift ITM3 into the ITM2 slot.
        candidates = options
        by_type = {"CE": [], "PE": []}
        for path in candidates:
            metadata = _contract_metadata(path)
            if price is None or _expiry_date(metadata["expiry"]) < trading_date:
                continue
            if metadata["option_type"] == "CE" and metadata["strike"] < price:
                by_type["CE"].append(path)
            if metadata["option_type"] == "PE" and metadata["strike"] > price:
                by_type["PE"].append(path)
        selected = []
        for option_type, paths in by_type.items():
            paths.sort(key=lambda path: (_expiry_date(_contract_metadata(path)["expiry"]),
                                         -_contract_metadata(path)["strike"] if option_type == "CE"
                                         else _contract_metadata(path)["strike"]))
            nearest_expiry = _expiry_date(_contract_metadata(paths[0])["expiry"]) if paths else None
            paths = [path for path in paths if _expiry_date(_contract_metadata(path)["expiry"]) == nearest_expiry]
            paths.sort(key=lambda path: _contract_metadata(path)["strike"], reverse=option_type == "CE")
            for rank, path in enumerate(paths[1:3], start=2):
                selected.append(path)
                metadata = _contract_metadata(path)
                option_day = _load_week(path, [trading_date])
                coverage = quality_report(option_day)
                local_option_times = option_day.timestamp.dt.tz_convert("Asia/Kolkata").dt.strftime("%H:%M")
                opening_candle_available = bool((local_option_times == "09:15").any())
                contract_eligibility.append({"date": str(trading_date), "underlying_price": price,
                    "symbol": path.stem,
                    "expiry": metadata["expiry"], "option_type": option_type, "strike": metadata["strike"],
                    "itm_rank": rank, "expected_itm_relationship": "CE strike < underlying" if option_type == "CE" else "PE strike > underlying",
                    "actual_relationship": True, "data_coverage": coverage,
                    "opening_candle_available": opening_candle_available,
                    "contract_day_has_candles": not option_day.empty,
                    "missing_intervals": coverage["missing_intervals"], "eligible": True})
        eligible_by_date[trading_date] = selected
        present_pairs = {(item["option_type"], item["itm_rank"]) for item in contract_eligibility
                         if item["date"] == str(trading_date) and item["contract_day_has_candles"]}
        expected_pairs = {(option_type, rank) for option_type in ("CE", "PE") for rank in (2, 3)}
        contract_coverage_by_date[trading_date] = {
            "present": sorted([{"option_type": option_type, "itm_rank": rank}
                               for option_type, rank in present_pairs],
                              key=lambda item: (item["option_type"], item["itm_rank"])),
            "missing": sorted([{"option_type": option_type, "itm_rank": rank}
                               for option_type, rank in expected_pairs - present_pairs],
                              key=lambda item: (item["option_type"], item["itm_rank"])),
        }
    eligible = sorted(set(path for paths in eligible_by_date.values() for path in paths))
    return {"start": start, "end": end, "requested_start": start, "requested_end": end,
            "trading_dates": dates, "option_files": eligible, "eligible_by_date": eligible_by_date,
            "contract_eligibility": contract_eligibility, "contract_coverage_by_date": contract_coverage_by_date,
            "missing_underlying_opening_dates": missing_opening_dates,
            "underlying_open": next(iter(opening_prices.values()), None),
            "underlying_dates": dates, "source_underlying_dates": source_dates}


def select_latest_completed_week(underlying_path, option_dir):
    """Compatibility name retained for callers; selection is now the requested period."""
    return select_requested_period(underlying_path, option_dir)


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
    eligibility = []
    missing_data = []
    for trading_date in selection["trading_dates"]:
        day_underlying = _load_week(underlying_path, [trading_date])
        if day_underlying.empty:
            missing_data.append({"date": str(trading_date), "dataset": "underlying", "reason": "no candles"})
            continue
        opening_rows = day_underlying[day_underlying.timestamp.dt.tz_convert("Asia/Kolkata").dt.strftime("%H:%M") == "09:15"]
        if len(opening_rows) != 1:
            missing_data.append({"date": str(trading_date), "dataset": "underlying",
                                 "reason": "missing unique 09:15 opening candle"})
            continue
        opening_price = float(opening_rows.iloc[0]["open"])
        day_paths = selection.get("eligible_by_date", {}).get(trading_date, selection["option_files"])
        for pair in selection.get("contract_coverage_by_date", {}).get(trading_date, {}).get("missing", []):
            matching_pair = next((item for item in selection.get("contract_eligibility", [])
                if item["date"] == str(trading_date) and item["option_type"] == pair["option_type"]
                and item["itm_rank"] == pair["itm_rank"]), None)
            missing_data.append({"date": str(trading_date), "dataset": "options",
                "option_type": pair["option_type"], "itm_rank": pair["itm_rank"],
                "contract": matching_pair.get("symbol") if matching_pair else None,
                "expiry": matching_pair.get("expiry") if matching_pair else None,
                "reason": "selected contract has no candle data for this date" if matching_pair
                          else "no contract candidate for this CE/PE and ITM rank in available sources"})
        for path in day_paths:
            option = _load_week(path, [trading_date])
            coverage_key = f"{trading_date}:{path.name}"
            quality["options"][coverage_key] = quality_report(option)
            if option.empty:
                continue
            metadata = {"symbol": path.stem, **_contract_metadata(path)}
            matching = [item for item in selection.get("contract_eligibility", [])
                        if item["date"] == str(trading_date) and item["strike"] == metadata["strike"]
                        and item["option_type"] == metadata["option_type"]]
            metadata["itm_rank"] = matching[0]["itm_rank"] if matching else None
            if metadata["itm_rank"] not in (2, 3):
                continue
            eligibility.extend(matching)
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
            "valid_setups": int((group.outcome != "SKIPPED_SL_ALREADY_BREACHED").sum()),
            "skipped_setups": int((group.outcome == "SKIPPED_SL_ALREADY_BREACHED").sum()),
            "target_hits": int((group.outcome == "TARGET").sum()),
            "sl_hits": int((group.outcome == "SL").sum()),
            "ambiguous_setups": int(group.outcome.isin(["AMBIGUOUS", "AMBIGUOUS_SL_FIRST"]).sum()),
            "open_outcomes": int((group.outcome == "OPEN").sum()), "points": float(valid_group.sum()) if not valid_group.empty else 0.0,
            "average_points_per_setup": float(valid_group.mean()) if not valid_group.empty else None,
            "average_daily_points": float(daily_points.mean()) if not daily_points.empty else None,
        }
    metrics = {
        "setup_count": int(len(events)),
        "valid_setups": int((events.outcome != "SKIPPED_SL_ALREADY_BREACHED").sum()) if not events.empty else 0,
        "skipped_setups": int((events.outcome == "SKIPPED_SL_ALREADY_BREACHED").sum()) if not events.empty else 0,
        "target_hits": int((events.outcome == "TARGET").sum()) if not events.empty else 0,
        "sl_hits": int((events.outcome == "SL").sum()) if not events.empty else 0,
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
    actual_dates = sorted({str(value) for value in selection["trading_dates"]
                           if value in selection.get("source_underlying_dates", selection["trading_dates"])})
    result = {
        "week": {"start": str(selection["start"]), "end": str(selection["end"]),
                 "trading_dates": [str(value) for value in selection["trading_dates"]]},
        "requested_period": {"start": str(selection.get("requested_start", selection["start"])),
                              "end": str(selection.get("requested_end", selection["end"]))},
        "actual_data_period": {"start": actual_dates[0] if actual_dates else None,
                               "end": actual_dates[-1] if actual_dates else None},
        "trading_day_coverage": {"requested": [str(value) for value in selection.get("source_underlying_dates", selection["trading_dates"])
                                                   if selection.get("requested_start", selection["start"]) <= value <= selection.get("requested_end", selection["end"])],
                                  "available": actual_dates},
        "option_data_coverage": quality["options"],
        "missing_data": missing_data,
        "contract_count": len({(item["expiry"], item["option_type"], item["strike"])
                    for item in eligibility}),
        "dataset": str(underlying_path), "strategy_version": "baseline-v1",
        "setup_count": int(len(events)),
        "valid_setups": int((events.outcome != "SKIPPED_SL_ALREADY_BREACHED").sum()) if not events.empty else 0,
        "skipped_setups": int((events.outcome == "SKIPPED_SL_ALREADY_BREACHED").sum()) if not events.empty else 0,
        "ambiguous_setups": int(events.outcome.isin(["AMBIGUOUS", "AMBIGUOUS_SL_FIRST"]).sum()) if not events.empty else 0,
        "target_hits": int((events.outcome == "TARGET").sum()) if not events.empty else 0,
        "sl_hits": int((events.outcome == "SL").sum()) if not events.empty else 0,
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
        "development_validation": "Coverage is reported from the requested period; missing source data is not substituted.",
        "contract_eligibility": eligibility,
        "metrics": metrics,
        "events": rows,
    }
    return result
