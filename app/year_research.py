"""Incremental month-by-month Groww retrieval for explicit year studies."""

from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, time, timedelta, timezone
import json
from pathlib import Path
import tempfile
import time as sleep_time
from typing import Any, Callable

import pandas as pd

from .contract_selection import _items, select_itm_contracts_from_ladder
from .groww_data import DATA_COLUMNS, _df, _fetch, get_contracts, get_expiries, validate_candles
from .nse_calendar import DEFAULT_NSE_CALENDAR

IST = timezone(timedelta(hours=5, minutes=30))
HISTORY_WINDOW_DAYS = 90
EXPECTED_BAR_COUNT = 75


def _month_dates(year: int, month: int) -> tuple[date, date]:
    return date(year, month, 1), date(year, month, monthrange(year, month)[1])


def _expiry_date(value: Any) -> date:
    text = str(value)
    try:
        return date.fromisoformat(text)
    except ValueError:
        return datetime.strptime(text.title(), "%d%b%y").date()


def _valid_session_stamps(day: date, now: datetime) -> list[pd.Timestamp]:
    if DEFAULT_NSE_CALENDAR.session_for(day) is None:
        return []
    start = datetime.combine(day, time(9, 15), IST)
    stamps = []
    for index in range(EXPECTED_BAR_COUNT):
        stamp = start + timedelta(minutes=5 * index)
        if stamp + timedelta(minutes=5) <= now:
            stamps.append(pd.Timestamp(stamp.astimezone(timezone.utc)))
    return stamps


def _expected_stamps(days: list[date], now: datetime) -> set[pd.Timestamp]:
    return {stamp for day in days for stamp in _valid_session_stamps(day, now)}


def _read_candles(path: Path) -> pd.DataFrame:
    if not path.is_file() or not path.stat().st_size:
        return pd.DataFrame(columns=DATA_COLUMNS)
    frame = pd.read_csv(path)
    for column in DATA_COLUMNS:
        if column not in frame:
            frame[column] = None
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
    frame = frame.loc[frame["timestamp"].notna(), DATA_COLUMNS]
    frame = frame.drop_duplicates("timestamp", keep="last")
    return validate_candles(frame)


def _local_symbol_files(root: Path, symbol: str, output_path: Path) -> list[Path]:
    matches = []
    output_path = output_path.resolve()
    for path in sorted((root / "data").rglob("*.csv")):
        if path.resolve() == output_path:
            continue
        if path.stem == symbol or (
            symbol == "NIFTY" and path.name.lower() == "nifty_5m.csv"
        ):
            matches.append(path)
    return matches


def _load_symbol_data(root: Path, symbol: str, output_path: Path) -> pd.DataFrame:
    frames = []
    if output_path.is_file():
        frames.append(_read_candles(output_path))
    for path in _local_symbol_files(root, symbol, output_path):
        frames.append(_read_candles(path))
    if not frames:
        return pd.DataFrame(columns=DATA_COLUMNS)
    combined = pd.concat(frames, ignore_index=True)
    return validate_candles(
        combined.drop_duplicates("timestamp", keep="last")[DATA_COLUMNS]
    )


def _merge_write(path: Path, frames: list[pd.DataFrame]) -> pd.DataFrame:
    nonempty = [frame for frame in frames if not frame.empty]
    if nonempty:
        combined = pd.concat(nonempty, ignore_index=True)
        combined = combined.drop_duplicates("timestamp", keep="last")
        combined = validate_candles(combined[DATA_COLUMNS])
    else:
        combined = pd.DataFrame(columns=DATA_COLUMNS)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".csv.tmp")
    combined.to_csv(temporary, index=False)
    temporary.replace(path)
    return combined


def _filter_month(frame: pd.DataFrame, year: int, month: int,
                  expected_days: set[date]) -> pd.DataFrame:
    if frame.empty:
        return frame
    local = frame["timestamp"].dt.tz_convert("Asia/Kolkata")
    mask = (
        (local.dt.year == year)
        & (local.dt.month == month)
        & local.dt.date.isin(expected_days)
        & local.dt.time.ge(time(9, 15))
        & local.dt.time.le(time(15, 25))
        & local.dt.minute.mod(5).eq(0)
        & local.dt.second.eq(0)
    )
    return frame.loc[mask, DATA_COLUMNS].copy()


def _request_month(
    client: Any,
    symbol: str,
    segment: str,
    expected: set[pd.Timestamp],
    expected_days: set[date],
    year: int,
    month: int,
    raw_dir: Path,
    root: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if not expected:
        return pd.DataFrame(columns=DATA_COLUMNS), {"status": "NO_COMPLETED_EXPECTED_BARS", "rows": 0}
    local_stamps = sorted(expected)
    start = local_stamps[0].tz_convert("Asia/Kolkata").to_pydatetime()
    last = local_stamps[-1].tz_convert("Asia/Kolkata").to_pydatetime()
    end = last + timedelta(minutes=5)
    try:
        payload = _fetch(client, symbol, start, end, segment)
        frame = _df(payload)
        if not frame.empty:
            frame = validate_candles(frame, reject_out_of_order=True)
            frame = _filter_month(frame, year, month, expected_days)
            frame = frame.loc[frame["timestamp"].isin(expected)].copy()
        raw_dir.mkdir(parents=True, exist_ok=True)
        raw_path = raw_dir / f"{year}-{month:02d}_{symbol.replace('/', '_')}.json"
        raw_path.write_text(
            json.dumps(payload, default=str, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return frame, {
            "status": "DATA_RETURNED" if not frame.empty else "EMPTY_RESPONSE",
            "rows": len(frame),
            "request_start": start.isoformat(),
            "request_end": end.isoformat(),
            "raw_payload": str(raw_path.relative_to(root)),
        }
    except Exception as exc:
        return pd.DataFrame(columns=DATA_COLUMNS), {
            "status": "FAILED",
            "error_type": type(exc).__name__,
            "request_start": start.isoformat(),
            "request_end": end.isoformat(),
        }


def _missing_sessions(expected: set[pd.Timestamp], frame: pd.DataFrame) -> set[pd.Timestamp]:
    if frame.empty:
        return expected
    return expected - set(pd.to_datetime(frame["timestamp"], utc=True))


def _collect_contract_catalog(
    client: Any, year: int, month: int, month_start: date, month_end: date,
    catalog: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    expiry_values: set[str] = set()
    queries = []
    for query_year, query_month in (
        (year, month),
        ((year + 1, 1) if month == 12 else (year, month + 1)),
    ):
        try:
            response = get_expiries(
                client, underlying="NIFTY", year=query_year, month=query_month,
            )
            values = _items(response, "expiries")
            expiry_values.update(str(value) for value in values if value)
            queries.append({"month": f"{query_year}-{query_month:02d}", "status": "OK"})
        except Exception as exc:
            queries.append({
                "month": f"{query_year}-{query_month:02d}",
                "status": "FAILED",
                "error_type": type(exc).__name__,
            })

    relevant = []
    for expiry in expiry_values:
        try:
            expiry_day = _expiry_date(expiry)
        except (ValueError, TypeError):
            continue
        if month_start <= expiry_day <= month_end + timedelta(days=7):
            relevant.append((expiry_day, expiry))

    chain_results = []
    for _, expiry in sorted(relevant):
        if expiry in catalog:
            continue
        try:
            response = get_contracts(client, expiry_date=expiry, underlying="NIFTY")
            contracts = _items(response, "contracts")
            if contracts:
                catalog[expiry] = contracts
                status = "DATA_RETURNED"
            else:
                status = "EMPTY_RESPONSE"
            chain_results.append({
                "expiry": expiry,
                "status": status,
                "contracts": len(contracts),
            })
        except Exception as exc:
            chain_results.append({
                "expiry": expiry,
                "status": "FAILED",
                "error_type": type(exc).__name__,
            })
    return {"expiry_queries": queries, "chains": chain_results}


def _fetch_option_month(
    client: Any, year: int, month: int, month_days: list[date],
    underlying: pd.DataFrame, catalog: dict[str, list[dict[str, Any]]],
    derived_options: Path, raw_dir: Path, root: Path, now: datetime,
) -> dict[str, Any]:
    local_underlying = underlying["timestamp"].dt.tz_convert("Asia/Kolkata")
    opening = underlying.loc[
        (local_underlying.dt.year == year)
        & (local_underlying.dt.month == month)
        & (local_underlying.dt.strftime("%H:%M") == "09:15")
    ]
    expiry_order = sorted(catalog, key=_expiry_date)
    wanted: dict[str, dict[str, Any]] = {}
    wanted_stamps: dict[str, set[pd.Timestamp]] = {}
    unavailable_days = []

    for row in opening.itertuples():
        trading_day = row.timestamp.tz_convert("Asia/Kolkata").date()
        if trading_day not in month_days:
            continue
        selected_expiry = next(
            (expiry for expiry in expiry_order if _expiry_date(expiry) >= trading_day),
            None,
        )
        if selected_expiry is None:
            unavailable_days.append({
                "date": trading_day.isoformat(),
                "reason": "NO_NON_EXPIRED_EXPIRY_IN_GROWW_CATALOG",
            })
            continue
        selected, _, _ = select_itm_contracts_from_ladder(
            catalog[selected_expiry], float(row.open),
            itm_ranks=(2, 3), option_types=("CE", "PE"), expiry=selected_expiry,
        )
        if not selected:
            unavailable_days.append({
                "date": trading_day.isoformat(),
                "reason": "NO_EXACT_ITM2_ITM3_CONTRACTS_IN_GROWW_CATALOG",
            })
        for contract in selected:
            symbol = str(contract["symbol"])
            wanted[symbol] = contract
            wanted_stamps.setdefault(symbol, set()).update(
                _valid_session_stamps(trading_day, now)
            )

    results = []
    for symbol, contract in sorted(wanted.items()):
        path = derived_options / f"{symbol}.csv"
        existing = _load_symbol_data(root, symbol, path)
        expected = wanted_stamps[symbol]
        missing = _missing_sessions(expected, existing)
        request_result = {"status": "ALREADY_COVERED", "rows": 0}
        if missing:
            expected_days = {
                stamp.tz_convert("Asia/Kolkata").date() for stamp in missing
            }
            fetched, request_result = _request_month(
                client, symbol, "FNO", missing, expected_days, year, month,
                raw_dir, root,
            )
        else:
            fetched = pd.DataFrame(columns=DATA_COLUMNS)
        if not path.is_file() or not fetched.empty:
            existing = _merge_write(path, [existing, fetched])
            for field in ("expiry", "strike", "option_type", "itm_rank"):
                existing[field] = contract.get(field)
            existing.to_csv(path, index=False)
        available = expected - _missing_sessions(expected, existing)
        results.append({
            "symbol": symbol,
            "option_type": contract.get("option_type"),
            "itm_rank": contract.get("itm_rank"),
            "expiry": contract.get("expiry"),
            "expected_bars": len(expected),
            "available_bars": len(available),
            "missing_bars": len(expected - available),
            **request_result,
        })
        sleep_time.sleep(0.1)
    return {
        "requested_contracts": len(wanted),
        "contracts": results,
        "unavailable_days": unavailable_days,
    }


def collect_year(
    client: Any,
    year: int,
    root: Path,
    *,
    now: datetime | None = None,
    progress: Callable[[str], None] = print,
) -> dict[str, Any]:
    """Fetch supported missing months and exact selected option candles sequentially."""
    from .config import CFG
    from .safety import ExecutionLock

    ExecutionLock(CFG).assert_paper_only()
    now = now or datetime.now(IST)
    if now.tzinfo is None:
        raise ValueError("Study timestamp must be timezone-aware")
    now = now.astimezone(IST)
    earliest_supported = now.date() - timedelta(days=HISTORY_WINDOW_DAYS)
    base = root / "data" / "derived" / "groww_history"
    raw_base = root / "data" / "raw" / "groww_history"
    underlying_path = base / "NIFTY.csv"
    options_path = base / "options"
    catalog: dict[str, list[dict[str, Any]]] = {}
    catalog_path = base / f"contract_catalog_{year}.json"
    if catalog_path.is_file():
        try:
            cached_catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            if isinstance(cached_catalog, dict):
                catalog = {
                    str(expiry): contracts
                    for expiry, contracts in cached_catalog.items()
                    if isinstance(contracts, list)
                }
        except (OSError, ValueError):
            catalog = {}
    monthly: list[dict[str, Any]] = []
    existing_underlying = _load_symbol_data(root, "NIFTY", underlying_path)
    if not underlying_path.is_file() and not existing_underlying.empty:
        existing_underlying = _merge_write(underlying_path, [existing_underlying])

    for month in range(1, 13):
        first, last = _month_dates(year, month)
        if first > now.date():
            monthly.append({
                "month": f"{year}-{month:02d}",
                "status": "FUTURE_MONTH",
                "rows": 0,
            })
            progress(f"[{year}-{month:02d}] skipped: future month")
            continue
        bounded_start = max(first, earliest_supported)
        bounded_end = min(last, now.date())
        if bounded_start > bounded_end:
            monthly.append({
                "month": f"{year}-{month:02d}",
                "status": "OUTSIDE_GROWW_FIVE_MINUTE_HISTORY_WINDOW",
                "available_from": earliest_supported.isoformat(),
                "rows": 0,
            })
            progress(
                f"[{year}-{month:02d}] skipped: outside Groww's "
                f"{HISTORY_WINDOW_DAYS}-day five-minute history window"
            )
            continue

        month_days = [
            date(year, month, day)
            for day in range(bounded_start.day, bounded_end.day + 1)
            if DEFAULT_NSE_CALENDAR.session_for(date(year, month, day)) is not None
        ]
        if not month_days:
            monthly.append({
                "month": f"{year}-{month:02d}",
                "status": "NO_SUPPORTED_NSE_SESSIONS",
                "rows": 0,
            })
            progress(f"[{year}-{month:02d}] skipped: no supported NSE sessions")
            continue

        expected = _expected_stamps(month_days, now)
        current_month = _filter_month(existing_underlying, year, month, set(month_days))
        missing = _missing_sessions(expected, current_month)
        request_result = {"status": "ALREADY_COVERED", "rows": 0}
        if missing:
            progress(
                f"[{year}-{month:02d}] fetching NIFTY candles "
                f"({len(missing)} missing five-minute bars)"
            )
            fetched, request_result = _request_month(
                client, "NIFTY", "CASH", missing, set(month_days),
                year, month, raw_base / "NIFTY", root,
            )
            if not fetched.empty:
                existing_underlying = _merge_write(
                    underlying_path, [existing_underlying, fetched],
                )
        else:
            progress(f"[{year}-{month:02d}] NIFTY candles already cover supported bars")

        month_underlying = _filter_month(
            existing_underlying, year, month, set(month_days),
        )
        has_opening = (
            not month_underlying.empty
            and month_underlying["timestamp"].dt.tz_convert("Asia/Kolkata")
            .dt.strftime("%H:%M").eq("09:15").any()
        )
        if has_opening:
            try:
                catalog_result = _collect_contract_catalog(
                    client, year, month, bounded_start, bounded_end, catalog,
                )
            except Exception as exc:
                catalog_result = {
                    "status": "FAILED",
                    "error_type": type(exc).__name__,
                }
        else:
            catalog_result = {
                "status": "SKIPPED_NO_UNDERLYING_OPENING_CANDLES",
                "expiry_queries": [],
                "chains": [],
            }
        try:
            option_result = _fetch_option_month(
                client, year, month, month_days, month_underlying,
                catalog, options_path, raw_base / "options", root, now,
            )
        except Exception as exc:
            option_result = {
                "status": "FAILED",
                "error_type": type(exc).__name__,
                "requested_contracts": 0,
                "contracts": [],
                "unavailable_days": [],
            }
        month_available = expected - _missing_sessions(expected, month_underlying)
        options_complete = bool(option_result["requested_contracts"]) and all(
            item["missing_bars"] == 0 for item in option_result["contracts"]
        ) and not option_result["unavailable_days"]
        month_result = {
            "month": f"{year}-{month:02d}",
            "status": (
                "COMPLETE"
                if not (expected - month_available) and options_complete
                else "PARTIAL"
            ),
            "requested_start": bounded_start.isoformat(),
            "requested_end": bounded_end.isoformat(),
            "underlying_expected_bars": len(expected),
            "underlying_available_bars": len(month_available),
            "underlying_missing_bars": len(expected - month_available),
            "underlying_request": request_result,
            "contract_catalog": catalog_result,
            "options": option_result,
        }
        monthly.append(month_result)
        progress(
            f"[{year}-{month:02d}] finished: "
            f"{len(month_available)}/{len(expected)} NIFTY bars; "
            f"{option_result['requested_contracts']} exact option contracts; "
            f"request={request_result['status']}"
        )

    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_path.write_text(
        json.dumps(catalog, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "source": "Groww read-only historical candles and contract catalog",
        "year": year,
        "generated_at": now.isoformat(),
        "history_window_days": HISTORY_WINDOW_DAYS,
        "available_from": earliest_supported.isoformat(),
        "underlying_csv": str(underlying_path.relative_to(root)),
        "option_directory": str(options_path.relative_to(root)),
        "contract_catalog": str(catalog_path.relative_to(root)),
        "months": monthly,
        "monthly_status_counts": {
            status: sum(1 for item in monthly if item["status"] == status)
            for status in sorted({item["status"] for item in monthly})
        },
        "network_calls_are_sequential": True,
        "safety": {"EXECUTION_ALLOWED": False, "PAPER_ONLY": True},
    }
    manifest_path = base / f"year_study_{year}.manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    return manifest


def year_has_fetchable_sessions(
    year: int, *, now: datetime | None = None,
) -> bool:
    now = now or datetime.now(IST)
    now = now.astimezone(IST)
    earliest = now.date() - timedelta(days=HISTORY_WINDOW_DAYS)
    first, last = date(year, 1, 1), min(date(year, 12, 31), now.date())
    if max(first, earliest) > last:
        return False
    cursor = max(first, earliest)
    while cursor <= last:
        if DEFAULT_NSE_CALENDAR.session_for(cursor) is not None:
            return True
        cursor += timedelta(days=1)
    return False


def local_year_study_complete(
    year: int, root: Path, *, now: datetime | None = None,
) -> bool:
    """Reuse a complete recent-year manifest without another Groww login."""
    now = (now or datetime.now(IST)).astimezone(IST)
    base = root / "data" / "derived" / "groww_history"
    manifest_path = base / f"year_study_{year}.manifest.json"
    catalog_path = base / f"contract_catalog_{year}.json"
    if not manifest_path.is_file() or not catalog_path.is_file():
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        previous = {item["month"]: item for item in manifest.get("months", [])}
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, KeyError, TypeError):
        return False
    if not catalog:
        return False

    earliest = now.date() - timedelta(days=HISTORY_WINDOW_DAYS)
    checked_supported_month = False
    for month in range(1, 13):
        first, last = _month_dates(year, month)
        if first > now.date():
            continue
        start = max(first, earliest)
        end = min(last, now.date())
        if start > end:
            continue
        days = [
            date(year, month, day)
            for day in range(start.day, end.day + 1)
            if DEFAULT_NSE_CALENDAR.session_for(date(year, month, day)) is not None
        ]
        expected_count = len(_expected_stamps(days, now))
        if not expected_count:
            continue
        checked_supported_month = True
        item = previous.get(f"{year}-{month:02d}", {})
        if (
            item.get("status") != "COMPLETE"
            or item.get("requested_start") != start.isoformat()
            or item.get("requested_end") != end.isoformat()
            or item.get("underlying_expected_bars") != expected_count
        ):
            return False
    return checked_supported_month


def analyze_year(year: int, root: Path) -> dict[str, Any]:
    """Run the canonical period engine and seven isolated exit shadows locally."""
    from .paper_shadow import CANDIDATES, EkalayavaShadowBook
    from .period_research import enrich_period_report, select_requested_period
    from .weekly_experiment import run_baseline_week

    base = root / "data" / "derived" / "groww_history"
    underlying_path = base / "NIFTY.csv"
    option_path = base / "options"
    catalog_path = base / f"contract_catalog_{year}.json"
    if not underlying_path.is_file() or not catalog_path.is_file():
        return {"status": "INSUFFICIENT_DATA", "reason": "Underlying data or contract catalog is missing."}
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    if not catalog:
        return {"status": "INSUFFICIENT_DATA", "reason": "Groww returned no option contract catalog."}
    try:
        selection = select_requested_period(
            underlying_path, option_path, date(year, 1, 1), date(year, 12, 31),
            contract_catalog=catalog,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        return {
            "status": "INSUFFICIENT_DATA",
            "reason": f"Canonical period selection unavailable ({type(exc).__name__}).",
        }
    result = run_baseline_week(underlying_path, option_path, selection)
    candidate_events = [
        event for event in result.get("events", [])
        if event.get("strategy") == "EKALAYAVA"
    ]
    candidate_states: list[dict[str, Any]] = []
    candles_by_symbol: dict[str, pd.DataFrame] = {}
    with tempfile.TemporaryDirectory(prefix="nifty-year-shadow-") as temp:
        for index, event in enumerate(candidate_events):
            anchor = event.get("observed_reversal_structure_low")
            if anchor is None or pd.isna(anchor):
                continue
            stamp = pd.to_datetime(event["timestamp"], utc=True)
            local_date = stamp.tz_convert("Asia/Kolkata").date()
            symbol = str(event["symbol"])
            signal = {
                "strategy": "EKALAYAVA",
                "event_type": "SIGNAL",
                "event_id": f"{local_date}|{symbol}|{stamp.isoformat()}",
                "setup_id": f"{local_date}|{symbol}|{stamp.isoformat()}",
                "date": local_date.isoformat(),
                "timestamp": stamp.isoformat(),
                "strategy_version": "canonical-baseline-v1",
                "symbol": symbol,
                "expiry": event.get("expiry"),
                "strike": event.get("strike"),
                "option_type": event.get("option_type"),
                "itm_rank": event.get("itm_rank"),
                "entry": float(event["entry"]),
                "opening_high": float(event["opening_high"]),
                "structural_low_candidate": float(anchor),
            }
            book = EkalayavaShadowBook(Path(temp) / f"{index}.json")
            book.observe_signal(signal)
            if symbol not in candles_by_symbol:
                path = option_path / f"{symbol}.csv"
                candles_by_symbol[symbol] = (
                    validate_candles(pd.read_csv(path)[DATA_COLUMNS])
                    if path.is_file() else pd.DataFrame(columns=DATA_COLUMNS)
                )
            frame = candles_by_symbol[symbol]
            local = frame["timestamp"].dt.tz_convert("Asia/Kolkata")
            future = frame.loc[
                (local.dt.date == local_date)
                & (frame["timestamp"] > stamp)
                & (local.dt.strftime("%H:%M").between("09:20", "15:25"))
            ]
            for row in future.itertuples():
                candle_stamp = row.timestamp.to_pydatetime()
                book.advance({
                    "timestamp": candle_stamp,
                    "close_time": candle_stamp + timedelta(minutes=5),
                    "open": float(row.open),
                    "high": float(row.high),
                    "low": float(row.low),
                    "close": float(row.close),
                    "completed": True,
                    "symbol": symbol,
                })
            candidate_states.extend(book.snapshot()["candidates"].values())

    candidate_summary = {}
    for spec in CANDIDATES:
        selected = [
            item for item in candidate_states
            if item.get("candidate_id") == spec["candidate_id"]
        ]
        outcomes = [item.get("outcome") for item in selected]
        points = [
            float(item["points"]) for item in selected
            if isinstance(item.get("points"), (int, float))
        ]
        candidate_summary[spec["candidate_id"]] = {
            "eligible_entries": len(selected),
            "target_exits": outcomes.count("TARGET"),
            "stop_exits": outcomes.count("STOP_LOSS"),
            "ambiguous": outcomes.count("AMBIGUOUS"),
            "end_of_session_exits": outcomes.count("END_OF_SESSION"),
            "unresolved": sum(
                1 for item in selected
                if item.get("status") in {"OPEN", "UNRESOLVED"}
            ),
            "excluded": sum(1 for item in selected if item.get("status") == "EXCLUDED"),
            "gross_option_premium_points": sum(points),
        }
    result = enrich_period_report(
        result, selection, date(year, 1, 1), date(year, 12, 31),
    )
    return {
        "status": "ANALYZED",
        "source": "fetched/local exact-contract 5-minute candles",
        "requested_period": result["requested_period"],
        "actual_data_period": result["actual_data_period"],
        "data_coverage_status": result["data_coverage_status"],
        "data_completeness": result["data_completeness"],
        "contract_day_coverage": result["contract_day_coverage"],
        "missing_data": result["missing_data"],
        "baseline_v1": {
            "setup_count": result["setup_count"],
            "outcomes": result["outcomes"],
            "by_strategy": result["by_strategy"],
            "trade_events": result["trade_events"],
        },
        "ekalayava_seven_candidate_shadow": {
            "unique_canonical_signals": len(candidate_events),
            "signals_without_structural_anchor": len(candidate_events) - sum(
                1 for item in candidate_events
                if item.get("observed_reversal_structure_low") is not None
                and not pd.isna(item.get("observed_reversal_structure_low"))
            ),
            "candidate_evaluations_are_not_new_signals": True,
            "results": candidate_summary,
        },
        "limitations": [
            "Groww five-minute API history is bounded to the most recent 90 days.",
            "The repository's exchange calendar is currently supported only for 2026.",
            "OHLC outcomes are simulations and do not verify quotes, fills, fees, or slippage.",
            "No Ekalayava stop/target candidate is approved by this report.",
        ],
    }
