"""Reconcile 2025-H2 and locally replayable 2026 Ekalayava exit paths.

This offline runner uses a fixed six-policy candidate set. It does not fetch
data, run a parameter grid, change the entry engine, or call order APIs.
2025 test-period exits are evaluated only if one policy passes the frozen
training/validation screen.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date, datetime, time
import json
import math
from pathlib import Path
import re
import statistics

import pandas as pd

from app.config import CFG
from app.paper import analyze_ekalayava
from app.research_ekalayava_exits import simulate_ekalayava_exit
from app.groww_data import DATA_COLUMNS, validate_candles


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
SOURCE_2025 = ROOT / "data" / "derived" / "ekalayava_2025_h2_groww"
OPTION_ROOT_2025 = SOURCE_2025 / "options"
PERIODS_2025 = {
    "TRAIN_2025_JUL_AUG": ("2025-07-01", "2025-08-31"),
    "VALIDATION_2025_SEP_OCT": ("2025-09-01", "2025-10-31"),
    "TEST_2025_NOV_DEC": ("2025-11-01", "2025-12-31"),
}
SESSION_START = time(9, 15)
SESSION_END = time(15, 25)
IST = "Asia/Kolkata"

POLICIES = (
    {
        "policy_id": "A_B4_TP25_V1", "family": "A_FIXED",
        "buffer": 4.0, "target_kind": "FIXED_25", "target_parameter": 25.0,
        "trailing": False,
    },
    {
        "policy_id": "A_B4_OPENING_HIGH_V1", "family": "A_OPENING_HIGH",
        "buffer": 4.0, "target_kind": "OPENING_HIGH", "target_parameter": None,
        "trailing": False,
    },
    {
        "policy_id": "B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1", "family": "B_TRAILING_PROXY",
        "buffer": 2.0, "target_kind": "OPENING_HIGH", "target_parameter": None,
        "trailing": True,
    },
    {
        "policy_id": "C_B2_1R_V1", "family": "C_REWARD_RISK",
        "buffer": 2.0, "target_kind": "RR", "target_parameter": 1.0,
        "trailing": False,
    },
    {
        "policy_id": "C_B2_1_5R_V1", "family": "C_REWARD_RISK",
        "buffer": 2.0, "target_kind": "RR", "target_parameter": 1.5,
        "trailing": False,
    },
    {
        "policy_id": "C_B2_2R_V1", "family": "C_REWARD_RISK",
        "buffer": 2.0, "target_kind": "RR", "target_parameter": 2.0,
        "trailing": False,
    },
)

OLD_POLICY_MAP = {
    "A_B4_OPENING_HIGH_V1": "A_STRUCTURAL_TROUGH_B4_TP100_OPENING_HIGH",
    "B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1": "TRAIL_CAUSAL_LOWER_LOW_B2_TP100",
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def _session_bars(frame: pd.DataFrame, trading_date: str) -> list[dict]:
    local = frame["timestamp"].dt.tz_convert(IST)
    same_day = frame.loc[
        (local.dt.strftime("%Y-%m-%d") == trading_date)
        & (local.dt.time >= SESSION_START)
        & (local.dt.time <= SESSION_END)
    ].sort_values("timestamp")
    return [
        {
            "timestamp": row.timestamp.to_pydatetime(),
            "open": float(row.open), "high": float(row.high),
            "low": float(row.low), "close": float(row.close),
        }
        for row in same_day.itertuples()
    ]


def _path_status(bars: list[dict], trading_date: str) -> str:
    if not bars:
        return "NO_USABLE_POST_ENTRY_PATH"
    stamps = [pd.Timestamp(row["timestamp"]).tz_convert(IST) for row in bars]
    if len(stamps) != len(set(stamps)):
        return "INVALID_OR_MISMATCHED"
    expected = pd.date_range(
        f"{trading_date} 09:15", f"{trading_date} 15:25",
        freq="5min", tz=IST,
    )
    actual = set(stamps)
    if all(stamp in actual for stamp in expected):
        return "COMPLETE_POST_ENTRY_PATH"
    if any(stamp in actual for stamp in expected):
        return "PARTIAL_POST_ENTRY_PATH"
    return "NO_USABLE_POST_ENTRY_PATH"


def _contract_metadata_matches(symbol: str, frame: pd.DataFrame) -> bool:
    parts = symbol.split("-")
    if len(parts) != 5:
        return False
    try:
        expected_expiry = datetime.strptime(parts[2], "%d%b%y").date()
        expected_strike = float(parts[3])
        expected_type = parts[4]
    except (ValueError, TypeError):
        return False
    if expected_type not in {"CE", "PE"}:
        return False
    for column, expected in (
        ("expiry", expected_expiry), ("strike", expected_strike),
        ("option_type", expected_type),
    ):
        if column not in frame:
            continue
        values = frame[column].dropna().unique()
        if not len(values):
            continue
        try:
            if column == "expiry":
                if any(pd.Timestamp(value).date() != expected for value in values):
                    return False
            elif column == "strike":
                if any(not math.isclose(float(value), expected) for value in values):
                    return False
            elif any(str(value) != expected for value in values):
                return False
        except (ValueError, TypeError):
            return False
    return True


def _load_option_files(search_roots: list[Path]) -> tuple[dict[str, list[tuple[Path, pd.DataFrame]]], list[str]]:
    indexed: dict[str, list[tuple[Path, pd.DataFrame]]] = defaultdict(list)
    invalid = []
    for root in search_roots:
        if not root.is_dir():
            continue
        for path in root.rglob("NSE-NIFTY-*.csv"):
            try:
                raw = pd.read_csv(path)
                frame = validate_candles(raw)
                indexed[path.stem].append((path, frame))
            except (OSError, ValueError, pd.errors.EmptyDataError):
                invalid.append(str(path.relative_to(ROOT)))
    return indexed, invalid


def _choose_exact_session(
    symbol: str, trading_date: str, entry_timestamp: pd.Timestamp | None,
    entry_price: float | None, indexed: dict[str, list[tuple[Path, pd.DataFrame]]],
) -> tuple[str, str | None, list[dict], pd.DataFrame | None]:
    candidates = indexed.get(symbol, [])
    best = None
    ranking = {
        "COMPLETE_POST_ENTRY_PATH": 4,
        "PARTIAL_POST_ENTRY_PATH": 3,
        "NO_USABLE_POST_ENTRY_PATH": 2,
        "INVALID_OR_MISMATCHED": 1,
    }
    for path, frame in candidates:
        day_mask = frame["timestamp"].dt.tz_convert(IST).dt.strftime("%Y-%m-%d") == trading_date
        day = frame.loc[day_mask].copy()
        if day.empty:
            continue
        if not _contract_metadata_matches(symbol, day):
            status = "INVALID_OR_MISMATCHED"
            bars = []
        else:
            bars = _session_bars(frame, trading_date)
            status = _path_status(bars, trading_date)
            if entry_timestamp is not None:
                entry_rows = day[day["timestamp"] == entry_timestamp.tz_convert("UTC")]
                if entry_rows.empty or (
                    entry_price is not None
                    and abs(float(entry_rows.iloc[0]["close"]) - entry_price) >= 0.011
                ):
                    status = "NO_USABLE_POST_ENTRY_PATH"
            elif not bars:
                status = "NO_USABLE_POST_ENTRY_PATH"
        score = ranking[status]
        if best is None or score > best[0]:
            best = (score, status, path, bars, day)
    if best is None:
        if candidates:
            return "NO_USABLE_POST_ENTRY_PATH", str(candidates[0][0].relative_to(ROOT)), [], None
        return "NO_USABLE_POST_ENTRY_PATH", None, [], None
    return best[1], str(best[2].relative_to(ROOT)), best[3], best[4]


def _target_for(policy: dict, entry: float, stop: float, opening_high: float) -> float:
    kind = policy["target_kind"]
    if kind == "FIXED_25":
        return entry + float(policy["target_parameter"])
    if kind == "OPENING_HIGH":
        return opening_high
    if kind == "RR":
        risk = entry - stop
        if risk <= 0:
            return entry
        return entry + risk * float(policy["target_parameter"])
    raise ValueError(f"Unknown target kind: {kind}")


def _simulate_event(event: dict, bars: list[dict], policy: dict) -> dict:
    entry = float(event["entry"])
    anchor = event.get("observed_reversal_structure_low")
    if anchor is None or pd.isna(anchor):
        return {"outcome": "EXCLUDED_ANCHOR_UNAVAILABLE", "reason": "structural_trough_missing"}
    stop = float(anchor) - float(policy["buffer"])
    target = _target_for(policy, entry, stop, float(event["opening_high"]))
    date_text = str(event["date"])
    result = simulate_ekalayava_exit(
        bars,
        entry_timestamp=pd.Timestamp(event["timestamp"]).to_pydatetime(),
        entry=entry,
        initial_stop=stop,
        target=target,
        expected_last_timestamp=pd.Timestamp(
            f"{date_text} 15:25", tz=IST,
        ).to_pydatetime(),
        trailing=bool(policy["trailing"]),
        trail_buffer=2.0,
    )
    risk = entry - stop
    return {
        **result,
        "initial_stop": stop,
        "target": target,
        "initial_risk": risk,
        "target_rr": (target - entry) / risk if risk > 0 else None,
    }


def _build_2025_events(indexed: dict[str, list[tuple[Path, pd.DataFrame]]]) -> tuple[list[dict], list[dict]]:
    selections = _read_csv(SOURCE_2025 / "selected_contract_sessions.csv")
    selected_by_symbol: dict[str, dict[str, dict]] = defaultdict(dict)
    for row in selections:
        selected_by_symbol[row["symbol"]][row["trading_date"]] = row

    contract_sessions = []
    events = []
    for symbol, dates in sorted(selected_by_symbol.items()):
        source_rows = indexed.get(symbol, [])
        valid_source = None
        invalid_symbol = False
        for path, frame in source_rows:
            if not _contract_metadata_matches(symbol, frame):
                invalid_symbol = True
                continue
            valid_source = (path, frame)
            break
        if valid_source is None:
            for trading_date, selection in sorted(dates.items()):
                contract_sessions.append({
                    **selection,
                    "path_status": "INVALID_OR_MISMATCHED" if invalid_symbol else "NO_USABLE_POST_ENTRY_PATH",
                    "source_path": None,
                    "session_bar_count": 0,
                })
            continue
        path, frame = valid_source
        for trading_date, selection in sorted(dates.items()):
            bars = _session_bars(frame, trading_date)
            status = _path_status(bars, trading_date)
            contract_sessions.append({
                **selection,
                "path_status": status,
                "source_path": str(path.relative_to(ROOT)),
                "session_bar_count": len(bars),
            })
        prepared = frame.copy()
        local = prepared["timestamp"].dt.tz_convert(IST)
        prepared = prepared.loc[
            (local.dt.time >= SESSION_START) & (local.dt.time <= time(15, 30))
        ].reset_index(drop=True)
        analyzed = analyze_ekalayava(prepared, contract={})
        if analyzed.empty:
            continue
        for observation in analyzed.to_dict("records"):
            trading_date = str(observation["date"])
            selection = dates.get(trading_date)
            if selection is None:
                continue
            stamp = pd.Timestamp(observation["timestamp"])
            bars = _session_bars(frame, trading_date)
            if not bars or stamp.tz_convert(IST).date().isoformat() != trading_date:
                continue
            observation.update({
                "symbol": symbol,
                "expiry": selection["expiry"],
                "strike": float(selection["strike"]),
                "option_type": selection["option_type"],
                "itm_rank": int(selection["itm_rank"]),
                "setup_id": f"{symbol}|{trading_date}|{stamp.isoformat()}",
                "period": _period_2025(trading_date),
                "path_status": _path_status(bars, trading_date),
                "source_path": str(path.relative_to(ROOT)),
            })
            events.append(observation)
    events.sort(key=lambda row: (str(row["date"]), str(row["timestamp"]), row["symbol"]))
    return events, contract_sessions


def _period_2025(trading_date: str) -> str:
    for period, (start, end) in PERIODS_2025.items():
        if start <= trading_date <= end:
            return period
    return "OUT_OF_SCOPE"


def _metrics(rows: list[dict]) -> dict:
    counts = Counter(row["outcome"] for row in rows)
    resolved = [row for row in rows if row["outcome"] in {"TARGET", "STOP_LOSS", "END_OF_SESSION"}]
    def chronological_key(row: dict) -> tuple[str, int]:
        stamp = (
            row.get("exit_timestamp")
            or row.get("entry_timestamp_utc")
            or row.get("timestamp_utc")
            or row.get("timestamp")
        )
        if stamp is None:
            raise ValueError("Resolved research row is missing its timestamp")
        return row["date"], pd.Timestamp(stamp).value

    resolved.sort(key=chronological_key)
    points = [float(row["points"]) for row in resolved if row.get("points") is not None]
    wins = [point for point in points if point > 0]
    losses = [point for point in points if point < 0]
    equity = peak = drawdown = 0.0
    streak = max_streak = 0
    for point in points:
        equity += point
        peak = max(peak, equity)
        drawdown = max(drawdown, peak - equity)
        streak = streak + 1 if point < 0 else 0
        max_streak = max(max_streak, streak)
    risks = [float(row["initial_risk"]) for row in rows
             if row.get("initial_risk") is not None and float(row["initial_risk"]) > 0]
    realized_rr = [
        float(row["points"]) / float(row["initial_risk"])
        for row in resolved if row.get("points") is not None
        and row.get("initial_risk") is not None and float(row["initial_risk"]) > 0
    ]
    mfe = [
        float(row.get("mfe_through_terminal_bar", row.get("mfe")))
        for row in resolved
        if row.get("mfe_through_terminal_bar", row.get("mfe")) is not None
    ]
    mae = [
        float(row.get("mae_through_terminal_bar", row.get("mae")))
        for row in resolved
        if row.get("mae_through_terminal_bar", row.get("mae")) is not None
    ]
    holds = [float(row["holding_minutes"]) for row in resolved
             if row.get("holding_minutes") is not None]
    return {
        "eligible_entries": len(rows),
        "executed_simulated_entries": sum(
            not row["outcome"].startswith("EXCLUDED") for row in rows
        ),
        "target_exits": counts["TARGET"],
        "stop_exits": counts["STOP_LOSS"],
        "end_of_session_exits": counts["END_OF_SESSION"],
        "ambiguous_exits": counts["AMBIGUOUS"],
        "unresolved": sum(value for key, value in counts.items() if key.startswith("UNRESOLVED")),
        "excluded": sum(value for key, value in counts.items() if key.startswith("EXCLUDED")),
        "gross_points": sum(points),
        "mean_points_resolved": statistics.mean(points) if points else None,
        "median_points_resolved": statistics.median(points) if points else None,
        "win_rate_resolved": len(wins) / len(points) if points else None,
        "profit_factor": sum(wins) / abs(sum(losses)) if losses and sum(losses) else None,
        "max_drawdown": drawdown,
        "longest_losing_streak": max_streak,
        "mean_initial_risk": statistics.mean(risks) if risks else None,
        "mean_realized_rr": statistics.mean(realized_rr) if realized_rr else None,
        "mean_mfe": statistics.mean(mfe) if mfe else None,
        "mean_mae": statistics.mean(mae) if mae else None,
        "mean_holding_minutes": statistics.mean(holds) if holds else None,
        "resolved_count": len(points),
    }


def _candidate_result_rows(events: list[dict], include_periods: set[str]) -> list[dict]:
    output = []
    for event in events:
        if event["period"] not in include_periods:
            continue
        bars = _session_bars_for_event(event)
        for policy in POLICIES:
            result = _simulate_event(event, bars, policy)
            output.append({
                "dataset": "GROWW_2025_H2",
                "period": event["period"],
                "date": event["date"],
                "setup_id": event["setup_id"],
                "symbol": event["symbol"],
                "expiry": event["expiry"],
                "option_type": event["option_type"],
                "itm_rank": event["itm_rank"],
                "entry_timestamp_utc": pd.Timestamp(event["timestamp"]).isoformat(),
                "entry": float(event["entry"]),
                "opening_high": float(event["opening_high"]),
                "structural_trough": event.get("observed_reversal_structure_low"),
                "path_status": event["path_status"],
                "source_path": event["source_path"],
                "policy_id": policy["policy_id"],
                "family": policy["family"],
                "stop_buffer": policy["buffer"],
                "initial_stop": result.get("initial_stop"),
                "target_kind": policy["target_kind"],
                "target": result.get("target"),
                "initial_risk": result.get("initial_risk"),
                "target_rr": result.get("target_rr"),
                "outcome": result["outcome"],
                "reason": result.get("reason"),
                "exit_timestamp": result.get("exit_timestamp"),
                "exit_price": result.get("exit_price"),
                "points": result.get("points"),
                "holding_minutes": result.get("holding_minutes"),
                "active_stop_at_exit": result.get("active_stop_at_exit"),
                "mfe": result.get("mfe_through_terminal_bar"),
                "mae": result.get("mae_through_terminal_bar"),
                "stop_updates": json.dumps(result.get("stop_updates", []), separators=(",", ":")),
            })
    return output


def _session_bars_for_event(event: dict) -> list[dict]:
    cached = event.get("_bars")
    if cached is not None:
        return cached
    raise RuntimeError("Internal research event is missing its candle path")


def _add_event_bars(events: list[dict], indexed: dict[str, list[tuple[Path, pd.DataFrame]]]) -> None:
    for event in events:
        for _, frame in indexed.get(event["symbol"], []):
            if _contract_metadata_matches(event["symbol"], frame):
                bars = _session_bars(frame, str(event["date"]))
                if bars:
                    event["_bars"] = bars
                    break
        if "_bars" not in event:
            event["_bars"] = []


def _summary_rows(trace_rows: list[dict], periods: set[str]) -> list[dict]:
    result = []
    for policy in POLICIES:
        for period in sorted(periods):
            selected = [
                row for row in trace_rows
                if row["policy_id"] == policy["policy_id"] and row["period"] == period
            ]
            metrics = _metrics(selected)
            complete = sum(row["path_status"] == "COMPLETE_POST_ENTRY_PATH" for row in selected)
            result.append({
                "policy_id": policy["policy_id"], "family": policy["family"],
                "period": period, **metrics,
                "complete_entry_paths": complete,
            })
    return result


def _monthly_summary_rows(trace_rows: list[dict]) -> list[dict]:
    output = []
    for policy in POLICIES:
        selected_policy_rows = [
            row for row in trace_rows if row["policy_id"] == policy["policy_id"]
        ]
        months = sorted({str(row["date"])[:7] for row in selected_policy_rows})
        for month in months:
            selected = [row for row in selected_policy_rows if str(row["date"])[:7] == month]
            output.append({
                "policy_id": policy["policy_id"],
                "family": policy["family"],
                "month": month,
                **_metrics(selected),
            })
    return output


def _load_2026_observations(
    indexed: dict[str, list[tuple[Path, pd.DataFrame]]],
) -> tuple[list[dict], list[dict], list[dict]]:
    observations = _read_csv(REPORTS / "multi_year_ekalayava_observations.csv")
    legacy_trades = _read_csv(REPORTS / "ekalayava_exit_policy_trades.csv")
    trace_rows = []
    coverage_rows = []
    archive_rows = []
    for event in observations:
        stamp = pd.Timestamp(event["timestamp_utc"]).tz_convert("UTC")
        status, source_path, bars, day = _choose_exact_session(
            event["symbol"], event["date"], stamp, float(event["entry"]), indexed,
        )
        coverage_rows.append({
            "dataset": "EXISTING_2026_ENTRY_LEDGER",
            "period": event["period"],
            "date": event["date"],
            "setup_id": event["setup_id"],
            "symbol": event["symbol"],
            "entry_timestamp_utc": event["timestamp_utc"],
            "path_status": status,
            "source_path": source_path,
            "session_bars": len(bars),
        })
        if status != "COMPLETE_POST_ENTRY_PATH":
            continue
        path = [{"timestamp": pd.Timestamp(row["timestamp"]).to_pydatetime(),
                 "open": row["open"], "high": row["high"], "low": row["low"], "close": row["close"]}
                for row in bars]
        entry = {
            **event,
            "timestamp": stamp,
            "observed_reversal_structure_low": (
                float(event["structural_low_candidate"])
                if event.get("structural_low_candidate") else None
            ),
            "opening_high": float(event["opening_high"]),
            "entry": float(event["entry"]),
            "date": event["date"],
            "setup_id": event["setup_id"],
            "_bars": path,
        }
        for policy in POLICIES:
            result = _simulate_event(entry, path, policy)
            trace_rows.append({
                "dataset": "EXISTING_2026_EXACT_PATH_SUBSET",
                "period": event["period"], "date": event["date"],
                "setup_id": event["setup_id"], "symbol": event["symbol"],
                "policy_id": policy["policy_id"], "outcome": result["outcome"],
                "reason": result.get("reason"), "points": result.get("points"),
                "path_status": status, "source_path": source_path,
                "exit_timestamp": result.get("exit_timestamp"),
            })
            old_policy = OLD_POLICY_MAP.get(policy["policy_id"])
            if old_policy is None:
                continue
            matches = [
                row for row in legacy_trades
                if row["policy"] == old_policy
                and row["symbol"] == event["symbol"]
                and row["date"] == event["date"]
                and row["timestamp_utc"] == event["timestamp_utc"]
            ]
            if len(matches) != 1:
                trace_rows[-1]["saved_ledger_reproduction"] = "NO_UNIQUE_SAVED_ROW"
                continue
            saved = matches[0]
            replay = simulate_ekalayava_exit(
                path,
                entry_timestamp=stamp.to_pydatetime(),
                entry=float(event["entry"]),
                initial_stop=float(saved["stop"]),
                target=float(saved["target"]),
                expected_last_timestamp=pd.Timestamp(
                    f"{event['date']} 15:25", tz=IST,
                ).to_pydatetime(),
                trailing=old_policy.startswith("TRAIL_"),
                trail_buffer=2.0,
            )
            trace_rows[-1]["saved_ledger_outcome"] = saved["outcome"]
            trace_rows[-1]["saved_ledger_points"] = saved["points"]
            same_points = (
                saved["points"] == "" and replay.get("points") is None
                or saved["points"] != "" and replay.get("points") is not None
                and math.isclose(float(saved["points"]), float(replay["points"]), abs_tol=1e-8)
            )
            same_exit_time = (
                saved["exit_timestamp"] == ""
                and replay.get("exit_timestamp") is None
                or saved["exit_timestamp"] != ""
                and replay.get("exit_timestamp") is not None
                and pd.Timestamp(saved["exit_timestamp"]).tz_convert("UTC")
                == pd.Timestamp(replay["exit_timestamp"]).tz_convert("UTC")
            )
            trace_rows[-1]["saved_ledger_reproduction"] = (
                "MATCH" if saved["outcome"] == replay["outcome"]
                and same_points and same_exit_time
                else "MISMATCH"
            )
            archive_rows.append({
                "setup_id": event["setup_id"], "date": event["date"],
                "symbol": event["symbol"], "policy": old_policy,
                "path_status": status,
                "saved_outcome": saved["outcome"],
                "replay_outcome": replay["outcome"],
                "saved_points": saved["points"],
                "replay_points": replay.get("points"),
                "saved_exit_timestamp": saved["exit_timestamp"],
                "replay_exit_timestamp": replay.get("exit_timestamp"),
                "reproduction": trace_rows[-1]["saved_ledger_reproduction"],
                "target_fraction": saved.get("target_fraction"),
                "target": saved["target"],
            })
            touch = event.get("target_touch_time_utc")
            if (
                touch and replay["outcome"] == "STOP_LOSS"
                and policy["target_kind"] == "OPENING_HIGH"
                and pd.Timestamp(touch).tz_convert("UTC")
                > pd.Timestamp(replay["exit_timestamp"]).tz_convert("UTC")
            ):
                trace_rows[-1]["opening_high_touched_after_exit"] = True
        archived_tp25 = [
            row for row in legacy_trades
            if row["policy"] == "A_STRUCTURAL_TROUGH_B4_TP25"
            and row["symbol"] == event["symbol"]
            and row["date"] == event["date"]
            and row["timestamp_utc"] == event["timestamp_utc"]
        ]
        for saved in archived_tp25:
            replay = simulate_ekalayava_exit(
                path,
                entry_timestamp=stamp.to_pydatetime(),
                entry=float(event["entry"]),
                initial_stop=float(saved["stop"]),
                target=float(saved["target"]),
                expected_last_timestamp=pd.Timestamp(
                    f"{event['date']} 15:25", tz=IST,
                ).to_pydatetime(),
            )
            same_points = (
                saved["points"] == "" and replay.get("points") is None
                or saved["points"] != "" and replay.get("points") is not None
                and math.isclose(float(saved["points"]), float(replay["points"]), abs_tol=1e-8)
            )
            same_exit_time = (
                saved["exit_timestamp"] == ""
                and replay.get("exit_timestamp") is None
                or saved["exit_timestamp"] != ""
                and replay.get("exit_timestamp") is not None
                and pd.Timestamp(saved["exit_timestamp"]).tz_convert("UTC")
                == pd.Timestamp(replay["exit_timestamp"]).tz_convert("UTC")
            )
            archive_rows.append({
                "setup_id": event["setup_id"], "date": event["date"],
                "symbol": event["symbol"],
                "policy": "A_STRUCTURAL_TROUGH_B4_TP25",
                "path_status": status,
                "saved_outcome": saved["outcome"],
                "replay_outcome": replay["outcome"],
                "saved_points": saved["points"],
                "replay_points": replay.get("points"),
                "saved_exit_timestamp": saved["exit_timestamp"],
                "replay_exit_timestamp": replay.get("exit_timestamp"),
                "reproduction": (
                    "MATCH" if saved["outcome"] == replay["outcome"]
                    and same_points and same_exit_time else "MISMATCH"
                ),
                "target_fraction": saved.get("target_fraction"),
                "target": saved["target"],
            })
    return coverage_rows, trace_rows, archive_rows


def _write_summary(summary: list[dict]) -> None:
    fields = list(summary[0]) if summary else []
    _write_csv(REPORTS / "ekalayava_guide7_candidate_metrics.csv", fields, summary)


def main() -> None:
    if CFG.execution_allowed or not CFG.paper_only or CFG.kill_switch:
        raise RuntimeError("Guide 7 research requires disabled execution, paper-only mode, and no kill switch")
    manifest_path = SOURCE_2025 / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("Run tools.fetch_ekalayava_2025_h2 prepare and options stages first")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("phase") not in {"options_complete", "options_partial"}:
        raise RuntimeError("2025 option retrieval has not completed")
    REPORTS.mkdir(parents=True, exist_ok=True)
    index_2025, invalid_2025 = _load_option_files([OPTION_ROOT_2025])
    entries_2025, contract_sessions = _build_2025_events(index_2025)
    _add_event_bars(entries_2025, index_2025)
    coverage_2025 = Counter(row["path_status"] for row in contract_sessions)

    index_2026, invalid_2026 = _load_option_files([
        ROOT / "data" / "raw" / "options",
        ROOT / "data" / "runs",
        ROOT / "data" / "derived" / "final_jan_sep_2026" / "assembled" / "options",
    ])
    coverage_2026, traces_2026, archive_reproductions = _load_2026_observations(index_2026)

    _write_csv(
        REPORTS / "ekalayava_guide7_2025_contract_session_coverage.csv",
        ["trading_date", "underlying_open", "expiry", "symbol", "strike",
         "option_type", "itm_rank", "selection_status", "path_status",
         "source_path", "session_bar_count"],
        contract_sessions,
    )
    _write_csv(
        REPORTS / "ekalayava_guide7_2026_entry_path_coverage.csv",
        ["dataset", "period", "date", "setup_id", "symbol",
         "entry_timestamp_utc", "path_status", "source_path", "session_bars"],
        coverage_2026,
    )
    event_fields = [
        "setup_id", "date", "period", "symbol", "expiry", "strike", "option_type",
        "itm_rank", "timestamp", "entry", "opening_high", "opening_low",
        "swing_high", "swing_high_timestamp", "breakdown_timestamp",
        "observed_reversal_structure_low", "breakout_candle_low", "target_touched",
        "target_touch_time", "mfe", "mae", "path_status", "source_path",
    ]
    _write_csv(
        REPORTS / "ekalayava_guide7_2025_entry_paths.csv", event_fields,
        [{key: value for key, value in event.items() if key in event_fields}
         for event in entries_2025],
    )

    pretest_periods = {"TRAIN_2025_JUL_AUG", "VALIDATION_2025_SEP_OCT"}
    pretest_rows = _candidate_result_rows(entries_2025, pretest_periods)
    pretest_summary = _summary_rows(pretest_rows, pretest_periods)
    validation = [
        row for row in pretest_summary
        if row["period"] == "VALIDATION_2025_SEP_OCT"
    ]
    qualifying = [
        row for row in validation
        if row["complete_entry_paths"] >= 25
        and row["gross_points"] > 0
        and row["profit_factor"] is not None
        and row["profit_factor"] > 1
    ]
    selected_policy = None
    selection_reason = "No candidate passed the frozen minimum validation screen."
    if qualifying:
        # Prefer the policy with the lowest validation drawdown, then lower
        # losing streak, then higher gross expectancy; do not rank on target rate.
        chosen = min(
            qualifying,
            key=lambda row: (
                row["max_drawdown"],
                row["longest_losing_streak"],
                -row["gross_points"] / row["eligible_entries"],
            ),
        )
        selected_policy = chosen["policy_id"]
        selection_reason = (
            "Passed >=25 complete validation paths, positive gross points and "
            "profit factor >1; tie-break selected by lower drawdown, losing "
            "streak, then gross expectancy."
        )

    test_rows = []
    if selected_policy is not None:
        frozen = next(policy for policy in POLICIES if policy["policy_id"] == selected_policy)
        for event in entries_2025:
            if event["period"] != "TEST_2025_NOV_DEC":
                continue
            result = _simulate_event(event, _session_bars_for_event(event), frozen)
            test_rows.append({
                "dataset": "GROWW_2025_H2_UNTOUCHED_TEST",
                "period": event["period"], "date": event["date"],
                "setup_id": event["setup_id"], "symbol": event["symbol"],
                "entry_timestamp_utc": pd.Timestamp(event["timestamp"]).isoformat(),
                "policy_id": selected_policy, "path_status": event["path_status"],
                "outcome": result["outcome"], "reason": result.get("reason"),
                "points": result.get("points"), "exit_timestamp": result.get("exit_timestamp"),
                "initial_risk": result.get("initial_risk"),
                "target_rr": result.get("target_rr"),
                "mfe": result.get("mfe_through_terminal_bar"),
                "mae": result.get("mae_through_terminal_bar"),
                "holding_minutes": result.get("holding_minutes"),
            })
    else:
        # The test period's entry/path coverage is reported, but no outcomes
        # are computed or inspected when validation selects no policy.
        for event in entries_2025:
            if event["period"] == "TEST_2025_NOV_DEC":
                test_rows.append({
                    "dataset": "GROWW_2025_H2_UNTOUCHED_TEST",
                    "period": event["period"], "date": event["date"],
                    "setup_id": event["setup_id"], "symbol": event["symbol"],
                    "entry_timestamp_utc": pd.Timestamp(event["timestamp"]).isoformat(),
                    "policy_id": "", "path_status": event["path_status"],
                    "outcome": "NOT_EVALUATED_NO_VALIDATION_SELECTION",
                    "points": None, "initial_risk": None, "target_rr": None,
                    "mfe": None, "mae": None, "holding_minutes": None,
                })

    candidate_fields = list(pretest_rows[0]) if pretest_rows else []
    _write_csv(REPORTS / "ekalayava_guide7_pretest_candidate_traces.csv",
               candidate_fields, pretest_rows)
    _write_summary(pretest_summary)
    monthly_metrics = _monthly_summary_rows(pretest_rows + [
        {
            "policy_id": row["policy_id"],
            "family": next(policy["family"] for policy in POLICIES
                           if policy["policy_id"] == row["policy_id"]),
            "date": row["date"],
            "entry_timestamp_utc": row.get("entry_timestamp_utc"),
            "outcome": row["outcome"],
            "points": row.get("points"),
            "initial_risk": row.get("initial_risk"),
            "mfe": row.get("mfe"),
            "mae": row.get("mae"),
            "holding_minutes": row.get("holding_minutes"),
        }
        for row in test_rows
        if row.get("policy_id") in {policy["policy_id"] for policy in POLICIES}
    ])
    _write_csv(
        REPORTS / "ekalayava_guide7_monthly_candidate_metrics.csv",
        list(monthly_metrics[0]) if monthly_metrics else [],
        monthly_metrics,
    )
    _write_csv(
        REPORTS / "ekalayava_guide7_test_results.csv",
        [
            "dataset", "period", "date", "setup_id", "symbol", "entry_timestamp_utc", "policy_id",
            "path_status", "outcome", "reason", "points", "exit_timestamp",
            "initial_risk", "target_rr",
            "mfe", "mae", "holding_minutes",
        ],
        test_rows,
    )
    _write_csv(
        REPORTS / "ekalayava_guide7_2026_candidate_traces.csv",
        list(traces_2026[0]) if traces_2026 else [],
        traces_2026,
    )
    _write_csv(
        REPORTS / "ekalayava_guide7_2026_archive_reproduction.csv",
        list(archive_reproductions[0]) if archive_reproductions else [
            "setup_id", "date", "symbol", "policy", "path_status",
            "saved_outcome", "replay_outcome", "saved_points", "replay_points",
            "saved_exit_timestamp", "replay_exit_timestamp", "reproduction",
            "target_fraction", "target",
        ],
        archive_reproductions,
    )

    summary = {
        "source_manifest": str(manifest_path.relative_to(ROOT)),
        "source_phase": manifest.get("phase"),
        "period_scope": ["2025-07-01 through 2025-12-31", "existing 2026 Jan-Sep ledger"],
        "2025_trading_dates_with_underlying_open": manifest.get("underlying_sessions_with_0915_open"),
        "2025_selected_contract_session_rows": len(contract_sessions),
        "2025_contract_session_path_counts": dict(coverage_2025),
        "2025_detected_entries_with_local_option_paths": len(entries_2025),
        "2025_entries_by_period": dict(Counter(event["period"] for event in entries_2025)),
        "2025_entry_path_counts": dict(Counter(event["path_status"] for event in entries_2025)),
        "2026_saved_entries": len(coverage_2026),
        "2026_entry_path_counts": dict(Counter(row["path_status"] for row in coverage_2026)),
        "2026_candidate_metrics_exact_path_subset": _summary_rows(
            traces_2026, {str(row["period"]) for row in traces_2026}
        ),
        "2026_archive_reproduction_counts": dict(Counter(
            row["reproduction"] for row in archive_reproductions
        )),
        "2026_archive_reproductions_by_policy": {
            policy: dict(Counter(
                row["reproduction"] for row in archive_reproductions
                if row["policy"] == policy
            ))
            for policy in sorted({row["policy"] for row in archive_reproductions})
        },
        "2026_invalid_option_files": invalid_2026,
        "2025_invalid_option_files": invalid_2025,
        "fixed_policy_ids": [policy["policy_id"] for policy in POLICIES],
        "2025_training_validation_metrics": pretest_summary,
        "2025_monthly_candidate_metrics": monthly_metrics,
        "validation_screen": {
            "minimum_complete_validation_entries": 25,
            "minimum_gross_points": "positive",
            "minimum_profit_factor": ">1",
            "selected_policy": selected_policy,
            "reason": selection_reason,
        },
        "2025_test_results_evaluated": selected_policy is not None,
        "2025_test_entry_rows": len(test_rows),
        "2025_test_metrics": (
            _metrics([
                {
                    "outcome": row["outcome"], "points": row.get("points"),
                    "initial_risk": row.get("initial_risk"),
                    "mfe": row.get("mfe"), "mae": row.get("mae"),
                    "holding_minutes": row.get("holding_minutes"),
                    "date": row["date"], "exit_timestamp": row.get("exit_timestamp"),
                }
                for row in test_rows if row.get("policy_id") == selected_policy
            ])
            if selected_policy is not None else None
        ),
        "2026_candidate_vs_archive_reproduction_counts": dict(Counter(
            row.get("saved_ledger_reproduction", "NOT_COMPARABLE")
            for row in traces_2026
            if row.get("saved_ledger_reproduction")
        )),
        "2026_opening_high_touches_after_simulated_exit": sum(
            bool(row.get("opening_high_touched_after_exit"))
            for row in traces_2026
        ),
        "costs": "Not available; net profitability not computed. Flat cost sensitivity must not be inferred.",
        "execution_allowed": CFG.execution_allowed,
        "paper_only": CFG.paper_only,
        "kill_switch": CFG.kill_switch,
        "orders_submitted": False,
    }
    (REPORTS / "ekalayava_guide7_research_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        key: summary[key] for key in (
            "2025_contract_session_path_counts", "2025_detected_entries_with_local_option_paths",
            "2025_entries_by_period", "2025_entry_path_counts", "2026_entry_path_counts",
            "validation_screen", "2025_test_results_evaluated",
            "2026_candidate_vs_archive_reproduction_counts",
            "2026_archive_reproduction_counts",
            "2026_opening_high_touches_after_simulated_exit",
        )
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
