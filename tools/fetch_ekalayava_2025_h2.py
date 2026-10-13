"""Fetch only the exact 2025-H2 NIFTY inputs needed by Ekalayava research.

All requests are read-only, paced, bounded to 2025-07-01 through 2025-12-31,
and issued once without automatic retries. No order endpoint is imported or
called. Raw data and the request manifest are written under ignored data/derived.
"""

from __future__ import annotations

import argparse
import csv
from datetime import date, datetime, time, timedelta
import json
from pathlib import Path
import re
import time as time_module

import pandas as pd

from app.config import CFG
from app.contract_selection import _items, _symbol_expiry, select_itm_contracts_from_ladder
from app.groww_auth import authenticate
from app.groww_data import _df, validate_candles


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "derived" / "ekalayava_2025_h2_groww"
OPTIONS = OUTPUT / "options"
START = date(2025, 7, 1)
END_EXCLUSIVE = date(2026, 1, 1)
IST = "Asia/Kolkata"
INTERVAL = timedelta(days=14)
REQUEST_PACE_SECONDS = 1.1
SELECTION_FIELDS = [
    "trading_date", "underlying_open", "expiry", "symbol", "strike",
    "option_type", "itm_rank", "selection_status",
]


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _paced() -> None:
    time_module.sleep(REQUEST_PACE_SECONDS)


def _assert_read_only_safety() -> None:
    if CFG.execution_allowed is not False or CFG.paper_only is not True or CFG.kill_switch is not False:
        raise RuntimeError("Historical retrieval requires execution disabled, paper-only, and kill switch off")
    if not CFG.api_key or not (CFG.api_secret or CFG.totp):
        raise RuntimeError("Groww read-only credentials are not configured")


def _fetch_payload(client, symbol: str, segment: str, start: datetime, end: datetime) -> pd.DataFrame:
    payload = client.get_historical_candles(
        exchange=client.EXCHANGE_NSE,
        segment=segment,
        groww_symbol=symbol if "-" in symbol else f"NSE-{symbol}",
        start_time=start.strftime("%Y-%m-%d %H:%M:%S"),
        end_time=end.strftime("%Y-%m-%d %H:%M:%S"),
        candle_interval="5minute",
        timeout=20,
    )
    return validate_candles(_df(payload))


def _session_open_by_date(underlying: pd.DataFrame) -> dict[date, float]:
    local = underlying.copy()
    local["local_timestamp"] = local["timestamp"].dt.tz_convert(IST)
    local["local_date"] = local["local_timestamp"].dt.date
    local["local_time"] = local["local_timestamp"].dt.time
    opens = local[local["local_time"] == time(9, 15)]
    return {row.local_date: float(row.open) for row in opens.itertuples()}


def prepare_inputs(client) -> dict:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest = _read_json(OUTPUT / "manifest.json")
    if manifest:
        raise RuntimeError("2025-H2 preparation already exists; refusing duplicate catalog/data requests")

    manifest.update({
        "phase": "prepare_in_progress",
        "source": "Groww read-only historical candle and contract-catalog APIs",
        "period_inclusive": ["2025-07-01", "2025-12-31"],
        "bar_interval": "5minute",
        "strategy_contract_selection": "exact first non-expired weekly expiry; exact ITM2/ITM3 CE/PE from the daily catalog strike ladder",
        "request_pacing_seconds": REQUEST_PACE_SECONDS,
        "automatic_retries": False,
        "execution_allowed": False,
        "paper_only": True,
        "orders_submitted": False,
        "underlying_chunks": [],
        "catalog_expiries": [],
        "catalog_errors": [],
    })
    _write_json(OUTPUT / "manifest.json", manifest)

    underlying_chunks = []
    cursor = datetime.combine(START, time.min)
    end = datetime.combine(END_EXCLUSIVE, time.min)
    while cursor < end:
        next_cursor = min(cursor + INTERVAL, end)
        try:
            frame = _fetch_payload(client, "NSE-NIFTY", CFG.segment_cash, cursor, next_cursor)
        except Exception as error:
            manifest["underlying_error"] = {
                "start": cursor.isoformat(), "end": next_cursor.isoformat(),
                "exception_type": type(error).__name__,
            }
            _write_json(OUTPUT / "manifest.json", manifest)
            raise RuntimeError("Stopped after one failed underlying chunk; no retry was made") from error
        underlying_chunks.append(frame)
        manifest["underlying_chunks"].append({
            "start": cursor.isoformat(), "end": next_cursor.isoformat(),
            "rows": len(frame),
        })
        cursor = next_cursor
        _paced()

    underlying = validate_candles(pd.concat(underlying_chunks, ignore_index=True).drop_duplicates("timestamp"))
    local_dates = underlying["timestamp"].dt.tz_convert(IST).dt.date
    in_scope = (local_dates >= START) & (local_dates < END_EXCLUSIVE)
    underlying = underlying.loc[in_scope].reset_index(drop=True)
    if underlying.empty:
        raise RuntimeError("Groww returned no NIFTY underlying bars for the requested period")
    underlying.to_csv(OUTPUT / "nifty_5m.csv", index=False, lineterminator="\n")

    expiry_payload = client.get_expiries(
        exchange=client.EXCHANGE_NSE,
        underlying_symbol="NIFTY",
        year=2025,
        timeout=20,
    )
    expiries = sorted({
        str(value) for value in _items(expiry_payload, "expiries")
        if START <= date.fromisoformat(str(value)) < END_EXCLUSIVE
    })
    _paced()
    if not expiries:
        raise RuntimeError("Groww returned no 2025 expiries in the requested window")

    chains = {}
    for expiry in expiries:
        try:
            payload = client.get_contracts(
                exchange=client.EXCHANGE_NSE,
                underlying_symbol="NIFTY",
                expiry_date=expiry,
                timeout=20,
            )
            contracts = _items(payload, "contracts")
        except Exception as error:
            manifest["catalog_errors"].append({
                "expiry": expiry, "exception_type": type(error).__name__,
            })
            _write_json(OUTPUT / "manifest.json", manifest)
            raise RuntimeError(f"Stopped after one failed contract-catalog request for {expiry}") from error
        chains[expiry] = contracts
        manifest["catalog_expiries"].append({
            "expiry": expiry, "contract_count": len(contracts),
        })
        _paced()

    opens = _session_open_by_date(underlying)
    selected_expiries = sorted(expiries)
    selections: list[dict] = []
    missing_sessions = []
    for trading_date, opening in sorted(opens.items()):
        if not START <= trading_date < END_EXCLUSIVE:
            continue
        expiry = next((value for value in selected_expiries
                       if date.fromisoformat(value) >= trading_date), None)
        if expiry is None:
            missing_sessions.append({
                "trading_date": trading_date.isoformat(),
                "reason": "no_non_expired_catalog_expiry",
            })
            continue
        selected, strike_step, expected = select_itm_contracts_from_ladder(
            chains[expiry], opening, itm_ranks=(2, 3),
            option_types=("CE", "PE"), expiry=expiry,
        )
        selected_keys = {(row["option_type"], row["itm_rank"]) for row in selected}
        for row in selected:
            symbol = row["symbol"]
            symbol_expiry = _symbol_expiry(symbol)
            if symbol_expiry is not None and symbol_expiry.isoformat() != expiry:
                raise ValueError(f"Catalog symbol expiry mismatch for {symbol}")
            selections.append({
                "trading_date": trading_date.isoformat(),
                "underlying_open": opening,
                "expiry": expiry,
                "symbol": symbol,
                "strike": row["strike"],
                "option_type": row["option_type"],
                "itm_rank": row["itm_rank"],
                "selection_status": "SELECTED",
            })
        missing = sorted(
            f"{side}_ITM{rank}" for side in ("CE", "PE") for rank in (2, 3)
            if (side, rank) not in selected_keys
        )
        if missing:
            missing_sessions.append({
                "trading_date": trading_date.isoformat(),
                "reason": "catalog_missing_exact_ladder_contracts",
                "missing": missing,
                "strike_step": strike_step,
                "expected_strikes": expected,
            })

    with (OUTPUT / "selected_contract_sessions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SELECTION_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(selections)

    manifest.update({
        "phase": "prepared",
        "underlying_path": str((OUTPUT / "nifty_5m.csv").relative_to(ROOT)),
        "underlying_rows": len(underlying),
        "underlying_sessions_with_0915_open": len(opens),
        "underlying_first_timestamp_ist": underlying["timestamp"].min().tz_convert(IST).isoformat(),
        "underlying_last_timestamp_ist": underlying["timestamp"].max().tz_convert(IST).isoformat(),
        "expiry_count": len(expiries),
        "expiry_dates": expiries,
        "selected_session_contract_rows": len(selections),
        "unique_selected_contracts": len({row["symbol"] for row in selections}),
        "sessions_missing_exact_contracts": missing_sessions,
        "option_requests": [],
    })
    _write_json(OUTPUT / "manifest.json", manifest)
    return manifest


def fetch_options(client) -> dict:
    manifest_path = OUTPUT / "manifest.json"
    manifest = _read_json(manifest_path)
    if manifest.get("phase") != "prepared":
        raise RuntimeError("Run the prepare stage first; refusing unbounded contract discovery")
    selections = pd.read_csv(OUTPUT / "selected_contract_sessions.csv").to_dict("records")
    grouped: dict[str, list[dict]] = {}
    for row in selections:
        grouped.setdefault(str(row["symbol"]), []).append(row)
    OPTIONS.mkdir(parents=True, exist_ok=True)
    completed_symbols = {
        row["symbol"] for row in manifest.get("option_requests", [])
        if row.get("status") == "saved"
    }
    failed_symbols = {
        row["symbol"] for row in manifest.get("option_requests", [])
        if row.get("status") != "saved"
    }
    results = manifest.setdefault("option_requests", [])
    total = len(grouped)
    for request_number, (symbol, rows) in enumerate(sorted(grouped.items()), start=1):
        if symbol in completed_symbols or symbol in failed_symbols:
            continue
        dates = sorted({date.fromisoformat(str(row["trading_date"])) for row in rows})
        start = datetime.combine(dates[0], time(9, 15))
        end = datetime.combine(dates[-1], time(15, 30))
        try:
            frame = _fetch_payload(client, symbol, CFG.segment_fno, start, end)
            if frame.empty:
                results.append({
                    "symbol": symbol, "status": "empty", "selected_dates": [d.isoformat() for d in dates],
                    "rows": 0,
                })
            else:
                meta = rows[0]
                for key in ("expiry", "strike", "option_type", "itm_rank"):
                    frame[key] = meta[key]
                filename = re.sub(r"[^A-Za-z0-9_.-]+", "_", symbol) + ".csv"
                frame.to_csv(OPTIONS / filename, index=False, lineterminator="\n")
                local_dates = frame["timestamp"].dt.tz_convert(IST).dt.date
                present_dates = sorted({
                    value.isoformat() for value in local_dates
                    if value in set(dates)
                })
                results.append({
                    "symbol": symbol, "status": "saved",
                    "selected_dates": [d.isoformat() for d in dates],
                    "dates_with_candles": present_dates,
                    "rows": len(frame), "path": str((OPTIONS / filename).relative_to(ROOT)),
                })
        except Exception as error:
            results.append({
                "symbol": symbol, "status": "error",
                "selected_dates": [d.isoformat() for d in dates],
                "exception_type": type(error).__name__,
            })
            _write_json(manifest_path, manifest)
            if "rate limit" in str(error).lower() or "too many requests" in str(error).lower():
                manifest["option_retrieval_stopped"] = "Groww rate limit; no retry or further requests"
                _write_json(manifest_path, manifest)
                break
        _write_json(manifest_path, manifest)
        if request_number % 10 == 0 or request_number == total:
            print(f"option contracts processed: {request_number}/{total}", flush=True)
        if request_number < total:
            _paced()

    saved = sum(row.get("status") == "saved" for row in results)
    errors = sum(row.get("status") == "error" for row in results)
    empties = sum(row.get("status") == "empty" for row in results)
    manifest["phase"] = "options_complete" if saved == total and not errors and not empties else "options_partial"
    manifest["option_contracts_saved"] = saved
    manifest["option_contracts_empty"] = empties
    manifest["option_contracts_failed"] = errors
    _write_json(manifest_path, manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("prepare", "options"))
    args = parser.parse_args()
    _assert_read_only_safety()
    client = authenticate(CFG)
    result = prepare_inputs(client) if args.stage == "prepare" else fetch_options(client)
    print(json.dumps({
        key: result.get(key) for key in (
            "phase", "underlying_rows", "underlying_sessions_with_0915_open",
            "expiry_count", "selected_session_contract_rows", "unique_selected_contracts",
            "option_contracts_saved", "option_contracts_empty", "option_contracts_failed",
            "option_retrieval_stopped",
        ) if key in result
    }, indent=2))


if __name__ == "__main__":
    main()
