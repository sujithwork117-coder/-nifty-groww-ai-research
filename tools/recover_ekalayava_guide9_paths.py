"""Make one bounded, read-only attempt to recover missing exact 2026 paths."""

from __future__ import annotations

from datetime import date, datetime, time
import json
from pathlib import Path
import re

import pandas as pd

from app.groww_auth import authenticate
from tools.fetch_ekalayava_2025_h2 import (
    IST,
    _assert_read_only_safety,
    _fetch_payload,
    _paced,
    _write_json,
)


ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "reports" / "ekalayava_guide7_2026_entry_path_coverage.csv"
OUTPUT = ROOT / "data" / "derived" / "ekalayava_guide9_2026_groww"
OPTIONS = OUTPUT / "options"
SYMBOL_PATTERN = re.compile(r"^NSE-NIFTY-\d{2}[A-Z][a-z]{2}\d{2}-\d+-[CP]E$")
MAX_REQUESTS = 253
REQUEST_START = time(9, 15)
REQUEST_END = time(15, 30)


def _request_plan(coverage: pd.DataFrame) -> list[tuple[str, date]]:
    missing = coverage.loc[
        coverage["path_status"].eq("NO_USABLE_POST_ENTRY_PATH"),
        ["symbol", "date"],
    ].drop_duplicates()
    requests: list[tuple[str, date]] = []
    for row in missing.itertuples(index=False):
        symbol = str(row.symbol)
        if not SYMBOL_PATTERN.fullmatch(symbol):
            raise ValueError(f"Unexpected exact-contract symbol in ledger: {symbol}")
        trading_date = date.fromisoformat(str(row.date))
        if trading_date.year != 2026:
            raise ValueError(f"Recovery is limited to 2026, found {trading_date}")
        requests.append((symbol, trading_date))
    requests.sort(key=lambda item: (item[1], item[0]))
    if len(requests) > MAX_REQUESTS:
        raise ValueError(
            f"Request plan exceeds the bounded {MAX_REQUESTS}-session limit"
        )
    return requests


def main() -> None:
    _assert_read_only_safety()
    if not COVERAGE.is_file():
        raise FileNotFoundError(f"Missing exact-path coverage ledger: {COVERAGE}")
    if (OUTPUT / "manifest.json").exists():
        raise FileExistsError(
            "Guide 9 recovery already has a manifest; refusing to repeat requests"
        )

    coverage = pd.read_csv(COVERAGE)
    requests = _request_plan(coverage)
    client = authenticate()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    OPTIONS.mkdir(parents=True, exist_ok=True)
    manifest = {
        "source": "Groww read-only historical option-candle API",
        "scope": "only missing exact symbol/date rows in the saved 2026 Ekalayava ledger",
        "request_count_planned": len(requests),
        "request_window_ist": [
            REQUEST_START.isoformat(), REQUEST_END.isoformat(),
        ],
        "bar_interval": "5minute",
        "automatic_retries": False,
        "execution_allowed": False,
        "paper_only": True,
        "orders_submitted": False,
        "requests": [],
    }
    _write_json(OUTPUT / "manifest.json", manifest)

    for index, (symbol, trading_date) in enumerate(requests, start=1):
        start = datetime.combine(trading_date, REQUEST_START)
        end = datetime.combine(trading_date, REQUEST_END)
        try:
            frame = _fetch_payload(client, symbol, client.SEGMENT_FNO, start, end)
        except Exception as error:
            manifest["stopped_after_error"] = {
                "symbol": symbol,
                "date": trading_date.isoformat(),
                "exception_type": type(error).__name__,
                "requests_completed": index - 1,
            }
            _write_json(OUTPUT / "manifest.json", manifest)
            raise RuntimeError(
                "Stopped after one Groww request failure; no retry was made"
            ) from error

        request = {
            "symbol": symbol,
            "date": trading_date.isoformat(),
            "rows_returned": len(frame),
            "status": "DATA" if not frame.empty else "EMPTY",
            "path": "",
        }
        if not frame.empty:
            local_stamps = frame["timestamp"].dt.tz_convert(IST)
            in_session = (
                (local_stamps.dt.date == trading_date)
                & (local_stamps.dt.time >= REQUEST_START)
                & (local_stamps.dt.time <= REQUEST_END)
            )
            frame = frame.loc[in_session].reset_index(drop=True)
            request["rows_in_session"] = len(frame)
            request["status"] = "DATA" if not frame.empty else "EMPTY"
        if not frame.empty:
            destination = OPTIONS / f"{symbol}.csv"
            if destination.exists():
                existing = pd.read_csv(destination)
                combined = pd.concat([existing, frame], ignore_index=True)
                combined["timestamp"] = pd.to_datetime(
                    combined["timestamp"], utc=True, errors="raise",
                )
                combined = combined.drop_duplicates("timestamp", keep="last")
                combined.sort_values("timestamp").to_csv(
                    destination, index=False, lineterminator="\n",
                )
            else:
                frame.to_csv(destination, index=False, lineterminator="\n")
            request["path"] = str(destination.relative_to(ROOT))
        manifest["requests"].append(request)
        _write_json(OUTPUT / "manifest.json", manifest)
        if index < len(requests):
            _paced()

    manifest["requests_completed"] = len(requests)
    manifest["data_responses"] = sum(
        row["status"] == "DATA" for row in manifest["requests"]
    )
    manifest["empty_responses"] = sum(
        row["status"] == "EMPTY" for row in manifest["requests"]
    )
    manifest["completed"] = True
    _write_json(OUTPUT / "manifest.json", manifest)
    print(json.dumps({
        "requests_completed": manifest["requests_completed"],
        "data_responses": manifest["data_responses"],
        "empty_responses": manifest["empty_responses"],
        "execution_allowed": False,
        "paper_only": True,
        "orders_submitted": False,
    }, indent=2))


if __name__ == "__main__":
    main()
