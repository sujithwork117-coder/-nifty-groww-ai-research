"""Safe terminal entry point for NIFTY historical research and paper observation."""

from __future__ import annotations

import argparse
import csv
from datetime import date, datetime, time, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "data" / "reports"
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
HISTORY_CHUNK_DAYS = 14
MAX_FETCH_DAYS = 31
GROWW_HISTORY_WINDOW_DAYS = 90
EXPECTED_BARS_PER_SESSION = 75

sys.path.insert(0, str(ROOT))

from app.config import CFG  # noqa: E402
from app.safety import ExecutionLock  # noqa: E402


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _timestamp_name() -> str:
    return _now().strftime("%Y%m%dT%H%M%S%fZ")


def _write_report(payload: dict[str, Any], title: str) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _timestamp_name()
    json_path = REPORT_DIR / f"run_research_{stamp}.json"
    markdown_path = REPORT_DIR / f"run_research_{stamp}.md"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    lines = [f"# {title}", "", f"Generated: `{payload['generated_at']}`", ""]
    if payload.get("summary"):
        lines.extend([payload["summary"], ""])
    lines.extend(["## Result", "", "```json",
                  json.dumps(payload, indent=2, sort_keys=True, default=str),
                  "```", ""])
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, markdown_path


def _safe_diagnostics() -> dict[str, Any]:
    lock_passed = False
    lock_error = None
    try:
        if CFG.execution_allowed is not False or CFG.paper_only is not True:
            raise RuntimeError("required safety flags are not set")
        ExecutionLock(CFG).assert_paper_only()
        lock_passed = True
    except RuntimeError as exc:
        lock_error = str(exc)
    credentials_available = bool(
        CFG.api_key.strip()
        and ((CFG.api_secret.strip() and not CFG.totp.strip())
             or (CFG.totp.strip() and not CFG.api_secret.strip()))
    )
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "execution_allowed": CFG.execution_allowed,
        "paper_only": CFG.paper_only,
        "kill_switch": CFG.kill_switch,
        "execution_lock_passed": lock_passed,
        "execution_lock_error": lock_error,
        "groww_credentials_configured": credentials_available,
        "network_used": False,
        "observer_started": False,
    }


def _inventory_data(root: Path = ROOT) -> dict[str, Any]:
    """Count local timestamped CSV rows without treating duplicate copies as unique data."""
    data_root = root / "data"
    by_year: dict[str, dict[str, int]] = {}
    by_area: dict[str, dict[str, int]] = {}
    files_seen = 0
    unreadable_files = []
    earliest = None
    latest = None
    for area in ("raw", "derived", "runs"):
        folder = data_root / area
        if not folder.exists():
            continue
        for path in sorted(folder.rglob("*.csv")):
            files_seen += 1
            try:
                with path.open("r", encoding="utf-8-sig", newline="") as stream:
                    reader = csv.DictReader(stream)
                    if not reader.fieldnames or "timestamp" not in reader.fieldnames:
                        continue
                    years_in_file = set()
                    for row in reader:
                        value = (row.get("timestamp") or "").strip()
                        if not value:
                            continue
                        try:
                            stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
                        except ValueError:
                            continue
                        year = str(stamp.year)
                        years_in_file.add(year)
                        by_year.setdefault(year, {"rows_across_files": 0, "files_with_rows": 0})
                        by_year[year]["rows_across_files"] += 1
                        by_area.setdefault(area, {}).setdefault(year, 0)
                        by_area[area][year] += 1
                        comparable_stamp = (
                            stamp.replace(tzinfo=IST).astimezone(timezone.utc)
                            if stamp.tzinfo is None else stamp.astimezone(timezone.utc)
                        )
                        if earliest is None or comparable_stamp < earliest:
                            earliest = comparable_stamp
                        if latest is None or comparable_stamp > latest:
                            latest = comparable_stamp
                    for year in years_in_file:
                        by_year[year]["files_with_rows"] += 1
            except (OSError, UnicodeError, csv.Error):
                unreadable_files.append(str(path.relative_to(root)))
    return {
        "files_inspected": files_seen,
        "rows_across_file_copies_by_year": by_year,
        "rows_by_storage_area_and_year": by_area,
        "duplicate_copies_note": "Rows are counted across files; duplicated run/cache copies are not deduplicated.",
        "earliest_timestamp": earliest.isoformat() if earliest else None,
        "latest_timestamp": latest.isoformat() if latest else None,
        "unreadable_csv_count": len(unreadable_files),
        "unreadable_csv_paths": unreadable_files[:20],
    }


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    return value if isinstance(value, dict) else None


def _study_evidence(years: list[int], root: Path = ROOT) -> dict[str, Any]:
    reports = root / "reports"
    guide_counts_path = reports / "ekalayava_guide8_candidate_counts.csv"
    l2l_path = reports / "multi_year_baseline_metrics.csv"
    candidate_rows = []
    if guide_counts_path.is_file():
        with guide_counts_path.open(encoding="utf-8-sig", newline="") as stream:
            candidate_rows = list(csv.DictReader(stream))
    baseline_rows = []
    if l2l_path.is_file():
        with l2l_path.open(encoding="utf-8-sig", newline="") as stream:
            baseline_rows = list(csv.DictReader(stream))
    by_year: dict[str, Any] = {}
    for year in years:
        if year == 2024:
            by_year[str(year)] = {
                "status": "UNAVAILABLE",
                "reason": "No local five-minute 2024 dataset or supported evidence artifact was found.",
                "l2l": None,
                "ekalayava": None,
            }
            continue
        if year == 2025:
            period = "GROWW_2025_H2"
            entry_total = 194
            date_range = ["2025-07-01", "2025-12-31"]
            path_evidence = _read_json(
                root / "data" / "derived" / "ekalayava_2025_h2_groww" / "manifest.json"
            )
            limitations = [
                "The local 2025 entry study covers H2 only.",
                "There are 192 complete and 2 partial canonical entry paths.",
                "Results are five-minute OHLC simulations; historical fills and costs are not measured.",
            ]
        elif year == 2026:
            period = "EXISTING_2026_ENTRY_LEDGER"
            entry_total = 253
            date_range = ["2026-01-01", "2026-09-30"]
            path_evidence = _read_json(reports / "multi_year_data_coverage.json")
            limitations = [
                "The saved ledger has 253 entry observations; not every entry was independently redetected.",
                "2026 option coverage is incomplete; missing exact contracts can suppress setups.",
                "Previously inspected periods are retrospective, not untouched holdouts.",
            ]
        else:
            by_year[str(year)] = {
                "status": "NOT_SUPPORTED",
                "reason": "Supported study years are 2024, 2025 and 2026.",
                "l2l": None,
                "ekalayava": None,
            }
            continue

        candidate_period_rows = [row for row in candidate_rows if row.get("period") == period]
        candidates = []
        for row in candidate_period_rows:
            candidates.append({
                "candidate_id": row.get("policy_id"),
                "eligible_entries": int(row.get("eligible_entries") or 0),
                "evaluated_entries": int(row.get("simulated_entries_with_exact_path") or 0),
                "target_exits": int(row.get("target_exits") or 0),
                "stop_exits": int(row.get("stop_loss_exits") or 0),
                "ambiguous": int(row.get("ambiguous_exits") or 0),
                "experimental_end_of_session_exits": int(row.get("end_of_session_exits") or 0),
                "unresolved": int(row.get("unresolved_entries") or 0),
                "partial_paths": 2 if year == 2025 else 0,
                "gross_option_premium_points": float(row.get("gross_points") or 0),
                "evidence_source": str(guide_counts_path.relative_to(root)),
            })
        if year == 2025:
            l2l = {
                "status": "UNKNOWN",
                "reason": "No local 2025 L2L baseline artifact was found in the supported evidence set.",
            }
        else:
            row = next((item for item in baseline_rows
                        if item.get("dimension") == "ALL" and item.get("group") == "ALL"), None)
            l2l = ({
                "status": "REPRODUCED_FROM_EXISTING_METRICS_ARTIFACT",
                "setups": int(row["setups"]),
                "eligible_entries": int(row["entered"]),
                "target_exits": int(row["target"]),
                "stop_exits": int(row["stop_loss"]),
                "ambiguous": int(row["ambiguous"]),
                "unresolved": int(row["unresolved"]),
                "gross_option_premium_points": float(row["gross_points"]),
                "max_drawdown_equal_unit_points": float(
                    row["max_drawdown_equal_unit_resolved_sequence"]
                ),
                "evidence_source": str(l2l_path.relative_to(root)),
            } if row else {"status": "UNKNOWN", "reason": "L2L baseline artifact unavailable."})
        by_year[str(year)] = {
            "status": "AVAILABLE_FROM_LOCAL_EVIDENCE" if candidate_period_rows else "NO_MATCHING_ARTIFACT",
            "requested_date_range": date_range,
            "canonical_ekalayava_entry_observations": entry_total if candidate_period_rows else None,
            "candidate_results": candidates,
            "l2l": l2l,
            "path_manifest_available": path_evidence is not None,
            "limitations": limitations,
        }
    return {
        "requested_years": years,
        "point_convention": "Gross option-premium points; no currency multiplier or actual costs assumed.",
        "candidate_results_are_seven_policy_evaluations_not_seven_times_as_many_signals": True,
        "no_exit_policy_approved": True,
        "results_by_year": by_year,
        "source_artifacts": [
            "reports/ekalayava_guide8_candidate_counts.csv",
            "reports/multi_year_baseline_metrics.csv",
            "reports/multi_year_data_coverage.json",
            "data/derived/ekalayava_2025_h2_groww/manifest.json",
        ],
    }


def _build_report(title: str, payload: dict[str, Any], summary: str) -> tuple[Path, Path]:
    payload.update({"generated_at": _now().isoformat(), "summary": summary})
    json_path, markdown_path = _write_report(payload, title)
    print(summary)
    print(f"JSON report: {json_path.relative_to(ROOT)}")
    print(f"Markdown report: {markdown_path.relative_to(ROOT)}")
    return json_path, markdown_path


def doctor() -> int:
    diagnostics = _safe_diagnostics()
    packages = {
        name: importlib.util.find_spec(name) is not None
        for name in ("pandas", "numpy", "pytest", "growwapi")
    }
    result = {
        "command": "doctor",
        "diagnostics": diagnostics,
        "dependencies_importable": packages,
        "offline_default": True,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if diagnostics["execution_lock_passed"] else 2


def _offline_smoke_test() -> dict[str, Any]:
    from app.journal import append_paper_record
    from app.paper_reconcile import reconcile_session
    from app.paper_shadow import EkalayavaShadowBook

    ExecutionLock(CFG).assert_paper_only()
    with tempfile.TemporaryDirectory(prefix="nifty-research-smoke-") as temp:
        session = Path(temp) / "2026-10-13"
        session.mkdir()
        stamp = datetime.fromisoformat("2026-10-13T09:15:00+05:30")
        setup_id = "offline-smoke-setup"
        symbol = "NSE-NIFTY-15Oct26-25000-CE"
        signal = {
            "event_type": "SIGNAL", "strategy": "EKALAYAVA",
            "event_id": setup_id, "setup_id": setup_id, "date": "2026-10-13",
            "timestamp": stamp.isoformat(), "strategy_version": "smoke-v1",
            "symbol": symbol, "expiry": "2026-10-15", "strike": 25000,
            "option_type": "CE", "itm_rank": 2, "entry": 100.0,
            "opening_high": 120.0, "structural_low_candidate": 90.0,
        }
        book = EkalayavaShadowBook(session / "contract.shadow.json",
                                   session / "paper_journal.jsonl")
        book.observe_signal(signal)
        completed = stamp + timedelta(minutes=5)
        book.advance({
            "timestamp": completed, "close_time": completed + timedelta(minutes=5),
            "open": 100.0, "high": 130.0, "low": 99.0, "close": 105.0,
            "completed": True, "symbol": symbol,
        })
        append_paper_record({
            "record_id": "offline-smoke-canonical-signal",
            "event_id": setup_id, "setup_id": setup_id,
            "event_type": "SIGNAL", "strategy": "EKALAYAVA",
            "timestamp": stamp.isoformat(), "symbol": symbol,
            "entry": 100.0, "opening_high": 120.0,
        }, session / "paper_journal.jsonl", CFG.model_version)
        (session / "contract.state.json").write_text(
            json.dumps({"ekalayava": {"signal": signal}}), encoding="utf-8"
        )
        (session / "observer_health.json").write_text(
            json.dumps({"trading_date": "2026-10-13", "missing_contracts": []}),
            encoding="utf-8",
        )
        result = reconcile_session(session)
        candidate_states = book.snapshot()["candidates"]
        if not result["integrity_ok"] or len(candidate_states) != 7:
            raise RuntimeError("offline smoke test failed shadow/reconciliation acceptance")
        if sum(row["target_exits"] for row in result["candidate_outcomes"].values()) != 7:
            raise RuntimeError("offline smoke test did not reconcile all seven candidates")
        return {
            "status": "PASS",
            "network_used": False,
            "observer_started": False,
            "canonical_signals": 1,
            "candidate_states": len(candidate_states),
            "candidate_target_exits": 7,
            "integrity_ok": result["integrity_ok"],
            "execution_allowed": False,
            "paper_only": True,
        }


def smoke_test() -> int:
    result = _offline_smoke_test()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def study(years: list[int]) -> int:
    invalid = sorted(set(years) - {2024, 2025, 2026})
    if invalid:
        print(f"Unsupported year(s): {', '.join(map(str, invalid))}; use 2024, 2025, 2026.")
        return 2
    inventory = _inventory_data()
    evidence = _study_evidence(years)
    summary = (
        f"Offline study complete for {', '.join(map(str, years))}; "
        "existing research artifacts reused; no network, new download, or expensive replay."
    )
    payload = {
        "command": "study",
        "safety": _safe_diagnostics(),
        "local_data_inventory": inventory,
        "historical_evidence": evidence,
        "network_used": False,
        "new_downloads": 0,
        "full_simulation_rerun": False,
        "summary": summary,
    }
    _build_report("NIFTY offline historical study", payload, summary)
    return 0


def default_workflow() -> int:
    diagnostics = _safe_diagnostics()
    if not diagnostics["execution_lock_passed"]:
        print("Safety diagnostics failed; offline workflow stopped.")
        return 2
    smoke = _offline_smoke_test()
    inventory = _inventory_data()
    evidence = _study_evidence([2024, 2025, 2026])
    summary = (
        "Offline workflow PASS: safety lock, seven-candidate smoke test, "
        "local data inventory and available historical evidence completed. "
        "No Groww connection or observer was started."
    )
    payload = {
        "command": "default_offline_workflow",
        "diagnostics": diagnostics,
        "smoke_test": smoke,
        "local_data_inventory": inventory,
        "historical_evidence": evidence,
        "network_used": False,
        "observer_started": False,
        "new_downloads": 0,
        "summary": summary,
    }
    _build_report("NIFTY default offline research workflow", payload, summary)
    return 0


def auth_check() -> int:
    from app.groww_auth import authenticate

    try:
        ExecutionLock(CFG).assert_paper_only()
        client = authenticate(CFG)
        profile = client.get_user_profile()
        if not isinstance(profile, dict):
            print("Groww auth-check FAIL: profile response was invalid; response details suppressed.")
            return 2
    except Exception as exc:
        print(f"Groww auth-check FAIL ({type(exc).__name__}); sensitive provider details suppressed.")
        return 2
    print("Groww authentication: SUCCESS")
    print("Groww read-only profile: SUCCESS")
    print("Order execution: DISABLED")
    return 0


def _safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._") or "instrument"


def _historical_source_paths(symbol: str, root: Path = ROOT) -> list[Path]:
    slug = _safe_slug(symbol)
    candidates = []
    for path in sorted((root / "data").rglob("*.csv")):
        if path.stem == symbol or path.stem == slug:
            candidates.append(path)
        elif symbol.upper() == "NIFTY" and path.name.lower() == "nifty_5m.csv":
            candidates.append(path)
    return candidates


def _load_existing_history(paths: list[Path], start: date, end: date):
    import pandas as pd
    from app.groww_data import DATA_COLUMNS, validate_candles

    frames = []
    for path in paths:
        try:
            frame = pd.read_csv(path)
        except (OSError, pd.errors.EmptyDataError) as exc:
            raise RuntimeError(f"Could not inspect local source {path}: {type(exc).__name__}") from None
        for column in DATA_COLUMNS:
            if column not in frame:
                frame[column] = None
        frame = validate_candles(frame[DATA_COLUMNS])
        local_dates = frame["timestamp"].dt.tz_convert(IST).dt.date
        frames.append(frame.loc[(local_dates >= start) & (local_dates <= end)].copy())
    if not frames:
        return pd.DataFrame(columns=DATA_COLUMNS), set()
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.drop_duplicates("timestamp", keep="last")
    combined = validate_candles(combined[DATA_COLUMNS])
    return combined, set(combined["timestamp"])


def _session_gaps(day: date, available: set):
    from app.nse_calendar import DEFAULT_NSE_CALENDAR

    session = DEFAULT_NSE_CALENDAR.session_for(day)
    if session is None:
        return None
    expected = []
    stamp = datetime.combine(day, time(9, 15), IST)
    final = datetime.combine(day, time(15, 25), IST)
    while stamp <= final:
        expected.append(stamp.astimezone(timezone.utc))
        stamp += timedelta(minutes=5)
    return [stamp for stamp in expected if stamp not in available]


def _missing_date_groups(missing_dates: list[date]) -> list[list[date]]:
    groups: list[list[date]] = []
    for day in missing_dates:
        if not groups or (day - groups[-1][-1]).days > 1 or (
            day - groups[-1][0]
        ).days >= HISTORY_CHUNK_DAYS:
            groups.append([day])
        else:
            groups[-1].append(day)
    return groups


def fetch_history(start: date, end: date, symbol: str = "NIFTY",
                  segment: str = "CASH") -> int:
    import pandas as pd
    from app.groww_data import DATA_COLUMNS, _df, _fetch, validate_candles
    from app.groww_auth import authenticate

    if end < start:
        print("Invalid date range: --end must be on or after --start.")
        return 2
    if (end - start).days + 1 > MAX_FETCH_DAYS:
        print(f"Fetch range exceeds the bounded {MAX_FETCH_DAYS}-calendar-day limit.")
        return 2
    today = datetime.now(IST).date()
    if end > today:
        print("Fetch range cannot extend beyond today's date.")
        return 2

    destination = ROOT / "data" / "derived" / "groww_history" / f"{_safe_slug(symbol)}.csv"
    local_paths = _historical_source_paths(symbol)
    if destination not in local_paths and destination.is_file():
        local_paths.append(destination)
    existing, available_timestamps = _load_existing_history(local_paths, start, end)

    days = []
    current = start
    while current <= end:
        gap_timestamps = _session_gaps(current, available_timestamps)
        if gap_timestamps:
            days.append(current)
        elif gap_timestamps is None and current.weekday() < 5:
            # Do not claim old dates are complete when the repository has no
            # authoritative holiday calendar for that year.
            if not any(ts.astimezone(IST).date() == current for ts in available_timestamps):
                days.append(current)
        current += timedelta(days=1)

    if days:
        earliest_supported = today - timedelta(days=GROWW_HISTORY_WINDOW_DAYS)
        if min(days) < earliest_supported:
            print(
                "Requested missing dates are outside the documented recent Groww "
                f"five-minute history window ({GROWW_HISTORY_WINDOW_DAYS} days); "
                "no authentication or request was made."
            )
            return 2

    if not days:
        print("No missing sessions were identified from the supported local calendar and data.")
        print("No network request or authentication performed.")
        return 0

    try:
        ExecutionLock(CFG).assert_paper_only()
        client = authenticate(CFG)
        profile = client.get_user_profile()
        if not isinstance(profile, dict):
            print("Historical fetch stopped: read-only profile validation failed.")
            return 2
    except Exception as exc:
        print(f"Historical fetch stopped during read-only auth/profile ({type(exc).__name__}).")
        return 2

    raw_dir = ROOT / "data" / "raw" / "groww_history" / _safe_slug(symbol)
    raw_dir.mkdir(parents=True, exist_ok=True)
    fetched_frames = []
    request_log = []
    groups = _missing_date_groups(days)
    for group_number, group in enumerate(groups, 1):
        request_start = datetime.combine(group[0], time(9, 15), IST)
        request_end = datetime.combine(group[-1], time(15, 30), IST)
        now = datetime.now(IST)
        if group[-1] == now.date():
            latest_closed_start = now.replace(
                minute=(now.minute // 5) * 5, second=0, microsecond=0,
            ) - timedelta(minutes=5)
            request_end = min(request_end, latest_closed_start + timedelta(minutes=5))
            if group[0] == now.date() and request_end <= request_start:
                request_log.append({
                    "start": request_start.isoformat(),
                    "end": request_end.isoformat(),
                    "rows": 0,
                    "status": "NO_COMPLETED_CANDLES_YET",
                })
                continue
        try:
            raw = _fetch(client, symbol, request_start, request_end, segment)
            frame = _df(raw)
            if not frame.empty:
                frame = validate_candles(frame, reject_out_of_order=True)
                local = frame["timestamp"].dt.tz_convert(IST)
                if (local.dt.minute.mod(5).ne(0) | local.dt.second.ne(0)).any():
                    raise ValueError("provider returned timestamps outside five-minute grid")
                local_dates = local.dt.date
                in_requested_dates = (
                    local_dates.ge(group[0]) & local_dates.le(group[-1])
                    & local.dt.time.ge(time(9, 15)) & local.dt.time.le(time(15, 25))
                )
                if group[-1] == now.date():
                    in_requested_dates &= (
                        local <= pd.Timestamp(latest_closed_start)
                    )
                frame = frame.loc[in_requested_dates].copy()
                fetched_frames.append(frame)
            raw_path = raw_dir / (
                f"{group[0].isoformat()}_{group[-1].isoformat()}_{group_number:03d}.json"
            )
            raw_path.write_text(json.dumps(raw, default=str, sort_keys=True) + "\n",
                                encoding="utf-8")
            request_log.append({
                "start": request_start.isoformat(),
                "end": request_end.isoformat(),
                "rows": len(frame),
                "raw_payload": str(raw_path.relative_to(ROOT)),
                "status": "DATA_RETURNED" if not frame.empty else "EMPTY_RESPONSE",
            })
        except Exception as exc:
            request_log.append({
                "start": request_start.isoformat(),
                "end": request_end.isoformat(),
                "status": "FAILED",
                "error_type": type(exc).__name__,
            })
            print(f"Historical request failed ({type(exc).__name__}); details suppressed.")
            break

    pieces = [existing]
    pieces.extend(fetched_frames)
    nonempty = [frame for frame in pieces if not frame.empty]
    if nonempty:
        combined = pd.concat(nonempty, ignore_index=True)
        duplicate_count = int(combined["timestamp"].duplicated(keep=False).sum())
        conflicting = 0
        duplicated = combined.loc[combined["timestamp"].duplicated(keep=False)]
        for _, group in duplicated.groupby("timestamp", sort=False):
            if len(group[["open", "high", "low", "close"]].drop_duplicates()) > 1:
                conflicting += 1
        combined = combined.drop_duplicates("timestamp", keep="last")
        combined = validate_candles(combined[DATA_COLUMNS])
    else:
        combined = pd.DataFrame(columns=DATA_COLUMNS)
        duplicate_count = conflicting = 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".csv.tmp")
    combined.to_csv(temporary, index=False)
    temporary.replace(destination)

    retrieved_at = _now().isoformat()
    manifest = {
        "source": "Groww read-only historical candles endpoint",
        "symbol": symbol,
        "segment": segment,
        "bar_interval": "5minute",
        "requested_start": start.isoformat(),
        "requested_end": end.isoformat(),
        "retrieved_at": retrieved_at,
        "row_count_in_requested_range": int(len(combined)),
        "requested_missing_sessions": [day.isoformat() for day in days],
        "requests": request_log,
        "request_responses_complete": bool(request_log) and all(
            row["status"] == "DATA_RETURNED" for row in request_log
        ),
        "duplicate_rows_before_deduplication": duplicate_count,
        "conflicting_timestamp_groups": conflicting,
        "missing_intervals_preserved": True,
        "normalized_derived_csv": str(destination.relative_to(ROOT)),
        "raw_payload_directory": str(raw_dir.relative_to(ROOT)),
        "safety": {"execution_allowed": False, "paper_only": True},
    }
    available_after_fetch = set(combined["timestamp"]) if not combined.empty else set()
    missing_after_fetch = {}
    for day in days:
        remaining = _session_gaps(day, available_after_fetch)
        if remaining is not None:
            missing_after_fetch[day.isoformat()] = len(remaining)
    responses_complete = bool(request_log) and all(
        row["status"] == "DATA_RETURNED" for row in request_log
    )
    coverage_complete = bool(missing_after_fetch) and all(
        count == 0 for count in missing_after_fetch.values()
    )
    manifest["remaining_missing_intervals_by_session"] = missing_after_fetch
    manifest["coverage_complete_for_supported_sessions"] = coverage_complete
    manifest_path = destination.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
    status = "COMPLETE" if responses_complete and coverage_complete else "PARTIAL"
    print(json.dumps({
        "status": status,
        "symbol": symbol,
        "requested_range": [start.isoformat(), end.isoformat()],
        "requested_missing_sessions": len(days),
        "rows": int(len(combined)),
        "missing_intervals_preserved": True,
        "coverage_complete_for_supported_sessions": coverage_complete,
        "remaining_missing_intervals_by_session": missing_after_fetch,
        "conflicting_timestamp_groups": conflicting,
        "manifest": str(manifest_path.relative_to(ROOT)),
    }, indent=2))
    return 0 if status == "COMPLETE" else 2


def live() -> int:
    from app.nse_calendar import DEFAULT_NSE_CALENDAR
    from app.paper_observer import GrowwPaperObserver, IST
    from app.paper_observer import authenticated_groww_factory

    current = datetime.now(IST)
    session = DEFAULT_NSE_CALENDAR.session_for(current.date())
    if session is None or not (
        session.opens_at <= current.time().replace(tzinfo=None) < session.closes_at
    ):
        print("LIVE refused: current time is outside a supported open NSE session.")
        return 2
    if not (CFG.execution_allowed is False and CFG.paper_only is True):
        print("LIVE refused: mandatory paper-only safety flags are not satisfied.")
        return 2
    try:
        ExecutionLock(CFG).assert_paper_only()
        factory = authenticated_groww_factory(CFG)
        client = factory()
        observer = GrowwPaperObserver(client, CFG, groww_factory=factory)
        observer.status["authentication_status"] = "READ_ONLY_PROFILE_VERIFIED"
        preflight = observer.run_once(current)
    except Exception as exc:
        print(f"LIVE preflight failed ({type(exc).__name__}); sensitive details suppressed.")
        return 2

    selected_pairs = {
        (item.get("option_type"), int(item.get("itm_rank", 0)))
        for item in preflight.get("selected_contracts", [])
    }
    if (preflight.get("health") != "HEALTHY"
            or preflight.get("contract_coverage") != "4/4"
            or preflight.get("missing_contracts")
            or selected_pairs != {("CE", 2), ("CE", 3), ("PE", 2), ("PE", 3)}
            or preflight.get("underlying_reference_candle_timestamp") is None
            or preflight.get("shadow_candidate_errors")):
        print(json.dumps({
            "status": "LIVE_PREFLIGHT_ABORTED",
            "health": preflight.get("health"),
            "contract_coverage": preflight.get("contract_coverage"),
            "missing_contracts": preflight.get("missing_contracts"),
            "selected_expiry": preflight.get("selected_expiry"),
            "skipped": preflight.get("skipped"),
            "shadow_candidate_errors": preflight.get("shadow_candidate_errors"),
            "execution_allowed": False,
            "paper_only": True,
        }, indent=2))
        return 2
    print(json.dumps({
        "status": "LIVE_PREFLIGHT_PASS",
        "trading_date": preflight.get("trading_date"),
        "selected_expiry": preflight.get("selected_expiry"),
        "contract_coverage": preflight.get("contract_coverage"),
        "last_underlying_candle": preflight.get("last_underlying_candle"),
        "execution_allowed": False,
        "paper_only": True,
        "operator_note": "Supervised observer active; stop with Ctrl-C.",
    }, indent=2), flush=True)
    try:
        result = observer.run_forever()
    except KeyboardInterrupt:
        observer.status["health"] = "STOPPED_BY_OPERATOR"
        observer.status["updated_at"] = datetime.now(IST).isoformat()
        observer._persist_health()
        print("Observer stopped by operator; no orders were sent.")
        return 0
    print(json.dumps({
        "health": result.get("health"),
        "trading_date": result.get("trading_date"),
        "selected_expiry": result.get("selected_expiry"),
        "contract_coverage": result.get("contract_coverage"),
        "reconnect_attempts": result.get("reconnect_attempts"),
        "execution_allowed": False,
        "paper_only": True,
    }, indent=2))
    return 0 if result.get("health") in {"SESSION_COMPLETE", "STOPPED_BY_OPERATOR"} else 2


def reconcile(day: date) -> int:
    from app.paper_reconcile import human_summary, reconcile_session

    session_dir = ROOT / "data" / "paper_observer" / day.isoformat()
    result = reconcile_session(session_dir)
    result["report_directory"] = str(session_dir.relative_to(ROOT))
    print(json.dumps(result, indent=2, sort_keys=True))
    print(human_summary(result), file=sys.stderr)
    print(f"Session data: {session_dir.relative_to(ROOT)}", file=sys.stderr)
    return 0 if result["integrity_ok"] else 2


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Offline-first NIFTY research and supervised read-only Groww paper observer."
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("doctor", help="check environment and execution safety without network access")
    subparsers.add_parser("test", help="run the full pytest suite")
    subparsers.add_parser("smoke-test", help="run an offline shadow/reconciliation acceptance test")
    subparsers.add_parser("auth-check", help="authenticate and validate Groww read-only profile")
    study_parser = subparsers.add_parser("study", help="summarize supported local historical evidence")
    study_parser.add_argument("--years", nargs="+", type=int, choices=(2024, 2025, 2026),
                              default=[2024, 2025, 2026])
    fetch_parser = subparsers.add_parser("fetch-history", help="explicit bounded read-only history retrieval")
    fetch_parser.add_argument("--start", required=True, type=date.fromisoformat)
    fetch_parser.add_argument("--end", required=True, type=date.fromisoformat)
    fetch_parser.add_argument("--symbol", default="NIFTY",
                              help="exact Groww instrument symbol (default: NIFTY)")
    fetch_parser.add_argument("--segment", choices=("CASH", "FNO"), default="CASH")
    subparsers.add_parser("live", help="start supervised read-only observation after live preflight")
    reconcile_parser = subparsers.add_parser("reconcile", help="reconcile a saved observer session")
    reconcile_parser.add_argument("--date", required=True, type=date.fromisoformat)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.command is None:
        return default_workflow()
    if args.command == "doctor":
        return doctor()
    if args.command == "smoke-test":
        return smoke_test()
    if args.command == "test":
        return subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, check=False).returncode
    if args.command == "auth-check":
        return auth_check()
    if args.command == "study":
        return study(args.years)
    if args.command == "fetch-history":
        return fetch_history(args.start, args.end, args.symbol, args.segment)
    if args.command == "live":
        return live()
    if args.command == "reconcile":
        return reconcile(args.date)
    parser.error("unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
