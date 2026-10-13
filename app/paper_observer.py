"""Read-only Groww 5-minute observer feeding durable paper strategy engines.

This module never places orders. It polls historical-candle endpoints for the
current session, discards candles that have not closed, and resumes each
contract-day engine from its durable state file. The observer is not started by
importing this module.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
import hashlib
import json
import logging
from pathlib import Path
import threading
import time as sleep_time
from typing import Callable
from zoneinfo import ZoneInfo

import pandas as pd

from .config import CFG
from .contract_selection import select_daily_itm_contracts
from .groww_data import get_session_candles
from .journal import append_paper_record
from .nse_calendar import DEFAULT_NSE_CALENDAR, NSECalendar
from .paper_engine import PaperContractEngine
from .paper_shadow import EkalayavaShadowBook
from .safety import ExecutionLock

IST = ZoneInfo("Asia/Kolkata")
BAR = timedelta(minutes=5)
LOG = logging.getLogger(__name__)


def _local(value):
    stamp = pd.Timestamp(value)
    return stamp.tz_localize(IST) if stamp.tzinfo is None else stamp.tz_convert(IST)


def _symbol_key(symbol):
    return hashlib.sha256(str(symbol).encode("utf-8")).hexdigest()[:20]


def _latest_expected_bar_start(now, session_open, session_close):
    current = min(now, session_close)
    elapsed = int((current - session_open).total_seconds() // BAR.total_seconds())
    return None if elapsed < 1 else session_open + BAR * (elapsed - 1)


def _completed_session_bars(frame, trading_date, now):
    """Return validated session bars whose five-minute close boundary passed."""
    if frame.empty:
        return []
    local = frame.copy()
    local["timestamp"] = pd.to_datetime(local["timestamp"], utc=True).dt.tz_convert(IST)
    local_now = _local(now)
    session_end = datetime.combine(trading_date, time(15, 30), IST)
    end = min(local_now, session_end)
    latest_closed_start = pd.Timestamp(end) - timedelta(minutes=5)
    local = local.loc[
        (local["timestamp"].dt.date == trading_date)
        & (local["timestamp"].dt.time >= time(9, 15))
        & (local["timestamp"].dt.time <= time(15, 25))
        & (local["timestamp"] <= latest_closed_start)
    ].sort_values("timestamp", kind="stable")
    bars = []
    for row in local.to_dict("records"):
        stamp = _local(row["timestamp"])
        bars.append({
            "timestamp": stamp,
            "close_time": stamp + BAR,
            "open": float(row["open"]), "high": float(row["high"]),
            "low": float(row["low"]), "close": float(row["close"]),
            "completed": True,
        })
    return bars


def _missing_intervals(bars):
    """Count absent five-minute buckets between the observed session bars."""
    return sum(
        max(0, int((right["timestamp"] - left["timestamp"]) / BAR) - 1)
        for left, right in zip(bars, bars[1:])
    )


class GrowwPaperObserver:
    """One NIFTY session coordinator with exact daily contracts and recovery."""

    def __init__(self, groww, config=CFG, state_dir="data/paper_observer",
                 calendar: NSECalendar = DEFAULT_NSE_CALENDAR,
                 groww_factory: Callable | None = None):
        ExecutionLock(config).assert_paper_only()
        self._validate_configuration(config)
        self.groww = groww
        self.groww_factory = groww_factory
        self.config = config
        self.calendar = calendar
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.status = {
            "health": "INITIALIZED", "trading_date": None,
            "authentication_status": "NOT_VERIFIED",
            "selected_expiry": None, "selected_contracts": [],
            "missing_contracts": [], "last_underlying_candle": None,
            "contract_selection_timestamp": None, "contract_coverage": "0/4",
            "underlying_reference_price": None,
            "underlying_reference_candle_timestamp": None,
            "underlying_candle_age_seconds": None,
            "missing_underlying_intervals": 0,
            "option_candle_age_seconds": {},
            "duplicate_candles_suppressed": 0,
            "invalid_data_events": 0,
            "journal_status": "NOT_VERIFIED",
            "reconnect_attempts": 0,
            "shadow_candidates": {},
            "shadow_candidate_errors": {},
            "last_option_candles": {}, "signals": [], "paper_positions": {},
            "skipped": [], "errors": [], "execution_allowed": False,
            "paper_only": True, "kill_switch": bool(config.kill_switch),
        }
        self._session_selection = None
        self._selection_date = None
        self._lock = threading.RLock()
        self._reconnect_attempt = 0

    @staticmethod
    def _validate_configuration(config):
        if config.underlying != "NIFTY":
            raise ValueError("The paper observer supports NIFTY only")
        if tuple(config.itm_ranks) != (2, 3) or tuple(config.option_types) != ("CE", "PE"):
            raise ValueError("Observer contract universe must be CE/PE ITM2/ITM3")
        if float(config.level_sl_points) != 4.0:
            raise ValueError("Observer L2L stop is fixed at the canonical four premium points")
        buffer_points = getattr(config, "ekalayava_sl_buffer_points", None)
        experimental = bool(getattr(config, "ekalayava_experimental_exit_simulation", False))
        if buffer_points is None and experimental:
            raise ValueError("Experimental Ekalayava simulation requires an explicit stop buffer")
        if buffer_points is not None and not experimental:
            raise ValueError("A buffer requires EKALAYAVA_EXPERIMENTAL_EXIT_SIMULATION=true")

    def _state_path(self, trading_date, symbol):
        directory = self.state_dir / trading_date.isoformat()
        directory.mkdir(parents=True, exist_ok=True)
        return directory / f"{_symbol_key(symbol)}.json"

    def _journal_path(self, trading_date):
        directory = self.state_dir / trading_date.isoformat()
        directory.mkdir(parents=True, exist_ok=True)
        return directory / "paper_journal.jsonl"

    def _fetch(self, symbol, start, end, segment):
        return get_session_candles(self.groww, symbol, start, end, segment)

    def _make_engines(self, trading_date, selection):
        engines = {}
        for contract in selection["contracts"]:
            symbol = contract["symbol"]
            path = self._state_path(trading_date, symbol)
            engine = PaperContractEngine(
                contract, self.config, journal_path=self._journal_path(trading_date),
                state_path=path,
            )
            engines[symbol] = engine
        return engines

    def _record_observer_event(self, event_type, current, *, stream, symbol=None,
                               reason=None, error_type=None, last_completed_candle=None,
                               retry_after_seconds=None, suppressed_candle_count=None,
                               missing_intervals=None, selection_timestamp=None,
                               underlying_reference_price=None,
                               underlying_reference_candle_timestamp=None,
                               contract_catalog_retrieved_at=None,
                               selection_rationale=None, selected_contracts_json=None,
                               expected_strikes_json=None, observed_strike_step=None):
        identity = "|".join(str(value or "") for value in (
            event_type, current.date().isoformat(), stream, symbol,
            last_completed_candle, reason, suppressed_candle_count,
            self._reconnect_attempt if event_type.startswith("RECONNECT") else "",
        ))
        event_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        record_id = hashlib.sha256(f"{event_id}|{event_type}".encode("utf-8")).hexdigest()
        return append_paper_record({
            "record_id": record_id, "event_id": event_id, "setup_id": None,
            "event_type": event_type, "strategy": "OBSERVER",
            "strategy_version": getattr(self.config, "strategy_version", self.config.model_version),
            "simulation_mode": "READ_ONLY_OBSERVATION", "date": current.date().isoformat(),
            "timestamp": current.isoformat(), "symbol": symbol, "stream": stream,
            "reason": reason, "error_type": error_type,
            "last_completed_candle": last_completed_candle,
            "retry_after_seconds": retry_after_seconds,
            "suppressed_candle_count": suppressed_candle_count,
            "missing_intervals": missing_intervals,
            "selection_timestamp": selection_timestamp,
            "underlying_reference_price": underlying_reference_price,
            "underlying_reference_candle_timestamp": underlying_reference_candle_timestamp,
            "contract_catalog_retrieved_at": contract_catalog_retrieved_at,
            "selection_rationale": selection_rationale,
            "selected_contracts_json": selected_contracts_json,
            "expected_strikes_json": expected_strikes_json,
            "observed_strike_step": observed_strike_step,
            "execution": "DISABLED", "paper_only": True,
        }, self._journal_path(current.date()), self.config.model_version)

    def _record_observed_candle(self, candle, current, *, stream, contract=None):
        symbol = contract.get("symbol") if contract else (
            self.config.underlying if stream == "NIFTY" else None
        )
        candle_timestamp = _local(candle["timestamp"]).isoformat()
        identity = "|".join((
            "CANDLE_OBSERVED", current.date().isoformat(), stream,
            str(symbol or ""), candle_timestamp,
        ))
        event_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        inserted = append_paper_record({
            "record_id": hashlib.sha256(f"{event_id}|CANDLE_OBSERVED".encode()).hexdigest(),
            "event_id": event_id, "setup_id": None, "event_type": "CANDLE_OBSERVED",
            "strategy": "OBSERVER", "strategy_version": self.config.strategy_version,
            "simulation_mode": "READ_ONLY_OBSERVATION",
            "date": current.date().isoformat(), "timestamp": candle_timestamp,
            "close_time": _local(candle["close_time"]).isoformat(),
            "stream": stream,
            "symbol": symbol, "expiry": contract.get("expiry") if contract else None,
            "strike": contract.get("strike") if contract else None,
            "option_type": contract.get("option_type") if contract else None,
            "itm_rank": contract.get("itm_rank") if contract else None,
            "open": float(candle["open"]), "high": float(candle["high"]),
            "low": float(candle["low"]), "close": float(candle["close"]),
            "data_provenance": "GROWW_READ_ONLY_HISTORICAL_CANDLES",
            "source_retrieved_at": current.isoformat(),
            "data_quality_status": "COMPLETED_CANDLE",
            "execution": "DISABLED", "paper_only": True,
        }, self._journal_path(current.date()), self.config.model_version)
        if not inserted:
            self.status["duplicate_candles_suppressed"] += 1
        else:
            self.status["journal_status"] = "WRITE_VERIFIED"
        return inserted

    def run_once(self, now=None):
        """Fetch and process one safe snapshot; provider errors are sanitized."""
        current = now or datetime.now(IST)
        current = current.replace(tzinfo=IST) if current.tzinfo is None else current.astimezone(IST)
        with self._lock:
            ExecutionLock(self.config).assert_paper_only()
            self.status["kill_switch"] = bool(self.config.kill_switch)
            self.status["errors"] = []
            self.status["skipped"] = []
            self.status["missing_underlying_intervals"] = 0
            self.status["option_candle_age_seconds"] = {}
            trading_date = current.date()
            self.status["trading_date"] = trading_date.isoformat()
            session = self.calendar.session_for(trading_date)
            if session is None:
                self.status["health"] = "CLOSED_OR_CALENDAR_UNSUPPORTED"
                return self._finish_status(current)
            session_open = datetime.combine(trading_date, session.opens_at, IST)
            session_close = datetime.combine(trading_date, session.closes_at, IST)
            # One five-minute grace window after the official close is allowed to
            # retrieve the final 15:25-15:30 completed candle. No later polling.
            if current < session_open or current > session_close + BAR:
                self.status["health"] = "CLOSED_OR_CALENDAR_UNSUPPORTED"
                return self._finish_status(current)
            if self._selection_date != trading_date:
                self.status["last_option_candles"] = {}
                self.status["paper_positions"] = {}
                self.status["signals"] = []
                self.status["last_underlying_candle"] = None
                self.status["selected_expiry"] = None
                self.status["selected_contracts"] = []
                self.status["missing_contracts"] = []
                self.status["contract_selection_timestamp"] = None
                self.status["contract_coverage"] = "0/4"
                self.status["underlying_reference_price"] = None
                self.status["underlying_reference_candle_timestamp"] = None
            session_start = session_open
            request_end = min(current, session_close)
            if request_end < session_start + BAR:
                self.status["health"] = "WAITING_FOR_COMPLETED_OPENING_CANDLE"
                return self._finish_status(current)

            try:
                underlying_frame = self._fetch(
                    self.config.underlying, session_start, request_end, self.config.segment_cash)
            except Exception as exc:
                self.status["health"] = "DEGRADED_UNDERLYING_DATA"
                self.status["errors"].append({"stream": "NIFTY", "error_type": type(exc).__name__})
                self._record_observer_event(
                    "UNDERLYING_STREAM_UNAVAILABLE", current, stream="NIFTY",
                    error_type=type(exc).__name__)
                LOG.warning("NIFTY candle request failed (%s)", type(exc).__name__)
                return self._finish_status(current)

            underlying_bars = _completed_session_bars(underlying_frame, trading_date, current)
            for bar in underlying_bars:
                self._record_observed_candle(bar, current, stream="NIFTY")
            expected_start = _latest_expected_bar_start(current, session_open, session_close)
            opening = next((bar for bar in underlying_bars
                            if bar["timestamp"].time().replace(tzinfo=None) == time(9, 15)), None)
            if opening is None:
                self.status["health"] = "MISSING_OR_UNFINISHED_NIFTY_OPEN"
                self.status["skipped"] = [{"stream": "NIFTY", "reason": "completed 09:15 opening candle unavailable"}]
                self._record_observer_event(
                    "MISSING_OPENING_CANDLE", current, stream="NIFTY",
                    reason="completed 09:15 opening candle unavailable")
                return self._finish_status(current)
            self.status["last_underlying_candle"] = underlying_bars[-1]["timestamp"].isoformat()
            self.status["underlying_candle_age_seconds"] = max(
                0.0,
                (
                    current - (underlying_bars[-1]["timestamp"].to_pydatetime() + BAR)
                ).total_seconds(),
            )
            if expected_start is not None and underlying_bars[-1]["timestamp"] < expected_start:
                self.status["health"] = "DEGRADED_UNDERLYING_DATA"
                self.status["skipped"] = [{"stream": "NIFTY", "reason": "latest completed candle is stale"}]
                self._record_observer_event(
                    "STALE_CANDLE_FEED", current, stream="NIFTY",
                    reason="latest completed candle is stale",
                    last_completed_candle=self.status["last_underlying_candle"])
                return self._finish_status(current)
            underlying_gaps = _missing_intervals(underlying_bars)
            self.status["missing_underlying_intervals"] = underlying_gaps
            underlying_failures = []
            if underlying_gaps:
                underlying_failures.append({
                    "stream": "NIFTY",
                    "reason": "MISSING_CANDLE_INTERVALS",
                    "missing_intervals": underlying_gaps,
                })
                self._record_observer_event(
                    "CANDLE_GAP_DETECTED", current, stream="NIFTY",
                    reason="missing intervals between completed underlying candles",
                    last_completed_candle=self.status["last_underlying_candle"],
                    missing_intervals=underlying_gaps)
                LOG.warning(
                    "Underlying candle stream has missing intervals (%s)",
                    underlying_gaps,
                )

            if self._selection_date != trading_date:
                try:
                    selection = select_daily_itm_contracts(
                        self.groww, opening["open"], trading_date,
                        underlying=self.config.underlying,
                        itm_ranks=self.config.itm_ranks,
                        option_types=self.config.option_types,
                    )
                except Exception as exc:
                    self.status["health"] = "DEGRADED_CONTRACT_SELECTION"
                    self.status["invalid_data_events"] += 1
                    self.status["errors"].append({"stream": "CONTRACT_CATALOG", "error_type": type(exc).__name__})
                    self._record_observer_event(
                        "CONTRACT_SELECTION_FAILED", current, stream="CONTRACT_CATALOG",
                        error_type=type(exc).__name__)
                    LOG.warning("Exact daily contract selection failed (%s)", type(exc).__name__)
                    return self._finish_status(current)
                self._session_selection = selection
                self._selection_date = trading_date
                self.status["selected_expiry"] = selection.get("expiry")
                self.status["selected_contracts"] = [dict(item) for item in selection["contracts"]]
                self.status["missing_contracts"] = [
                    {"option_type": kind, "itm_rank": rank} for kind, rank in selection["missing"]
                ]
                self.status["contract_selection_timestamp"] = current.isoformat()
                self.status["underlying_reference_price"] = float(opening["open"])
                self.status["underlying_reference_candle_timestamp"] = _local(
                    opening["close_time"]).isoformat()
                self.status["contract_coverage"] = (
                    f"{len(selection['contracts'])}/"
                    f"{len(self.config.itm_ranks) * len(self.config.option_types)}"
                )
                self._record_observer_event(
                    "DAILY_CONTRACTS_SELECTED", current, stream="CONTRACT_CATALOG",
                    selection_timestamp=current.isoformat(),
                    underlying_reference_price=float(opening["open"]),
                    underlying_reference_candle_timestamp=_local(
                        opening["close_time"]).isoformat(),
                    contract_catalog_retrieved_at=current.isoformat(),
                    selection_rationale=(
                        "Earliest non-expired Groww expiry; exact catalog ITM2/ITM3 "
                        "strike ladder; missing ranks are not substituted"
                    ),
                    selected_contracts_json=json.dumps(
                        selection["contracts"], sort_keys=True, separators=(",", ":")),
                    expected_strikes_json=json.dumps(
                        selection.get("expected_strikes", {}), sort_keys=True,
                        separators=(",", ":")),
                    observed_strike_step=selection.get("observed_strike_step"),
                )
                for kind, rank in selection["missing"]:
                    self._record_observer_event(
                        "EXACT_CONTRACT_UNAVAILABLE", current, stream="CONTRACT_CATALOG",
                        reason=f"no exact {kind} ITM{rank} catalog symbol")

            selection = self._session_selection
            if not selection or not selection["contracts"]:
                self.status["health"] = "NO_EXACT_DAILY_CONTRACTS"
                return self._finish_status(current)

            engines = self._make_engines(trading_date, selection)
            nifty_by_time = {bar["timestamp"].isoformat(): bar["close"] for bar in underlying_bars}
            option_failures = []
            self.status["last_option_candles"] = {}
            self.status["paper_positions"] = {}
            self.status["shadow_candidates"] = {}
            self.status["shadow_candidate_errors"] = {}
            for contract in selection["contracts"]:
                symbol = contract["symbol"]
                engine = engines[symbol]
                try:
                    shadow = EkalayavaShadowBook(
                        self._state_path(trading_date, symbol).with_suffix(".shadow.json"),
                        self._journal_path(trading_date), self.config,
                    )
                except Exception as exc:
                    error_type = type(exc).__name__
                    self.status["shadow_candidate_errors"][symbol] = error_type
                    option_failures.append({"symbol": symbol, "reason": "SHADOW_STATE_INVALID"})
                    self.status["paper_positions"][symbol] = {
                        "l2l": self._position_summary(engine.state.get("l2l", {}).get("trade")),
                        "ekalayava": self._position_summary(engine.state.get("ekalayava", {}).get("trade")),
                        "last_completed_candle": engine.state.get("last_timestamp"),
                        "stale": True,
                        "data_quality_status": engine.state.get("data_quality_status"),
                        "missing_intervals": engine.state.get("missing_intervals", 0),
                    }
                    self._record_observer_event(
                        "SHADOW_CANDIDATE_ERROR", current, stream="OPTIONS",
                        symbol=symbol, error_type=error_type,
                        reason="isolated candidate state could not be restored")
                    continue
                try:
                    option_frame = self._fetch(symbol, session_start, request_end, self.config.segment_fno)
                    option_bars = _completed_session_bars(option_frame, trading_date, current)
                except Exception as exc:
                    reason = type(exc).__name__
                    self.status["invalid_data_events"] += 1
                    engine.mark_data_quality_issue("OPTION_STREAM_UNAVAILABLE")
                    option_failures.append({"symbol": symbol, "reason": reason})
                    self._record_observer_event(
                        "OPTION_STREAM_UNAVAILABLE", current, stream="OPTIONS", symbol=symbol,
                        error_type=reason, last_completed_candle=engine.state.get("last_timestamp"))
                    self.status["paper_positions"][symbol] = {
                        "l2l": self._position_summary(engine.state.get("l2l", {}).get("trade")),
                        "ekalayava": self._position_summary(engine.state.get("ekalayava", {}).get("trade")),
                        "last_completed_candle": engine.state.get("last_timestamp"),
                        "stale": True,
                        "data_quality_status": engine.state.get("data_quality_status"),
                        "missing_intervals": engine.state.get("missing_intervals", 0),
                    }
                    LOG.warning("Exact option contract skipped (%s, %s)", symbol, reason)
                    continue
                if not option_bars:
                    self.status["invalid_data_events"] += 1
                    engine.mark_data_quality_issue("NO_COMPLETED_OPTION_CANDLES")
                    option_failures.append({"symbol": symbol, "reason": "NO_COMPLETED_CANDLES"})
                    self._record_observer_event(
                        "OPTION_STREAM_EMPTY", current, stream="OPTIONS", symbol=symbol,
                        reason="no completed option candles returned",
                        last_completed_candle=engine.state.get("last_timestamp"))
                    self.status["paper_positions"][symbol] = {
                        "l2l": self._position_summary(engine.state.get("l2l", {}).get("trade")),
                        "ekalayava": self._position_summary(engine.state.get("ekalayava", {}).get("trade")),
                        "last_completed_candle": engine.state.get("last_timestamp"),
                        "stale": True,
                        "data_quality_status": engine.state.get("data_quality_status"),
                        "missing_intervals": engine.state.get("missing_intervals", 0),
                    }
                    continue
                for bar in option_bars:
                    self._record_observed_candle(
                        bar, current, stream="OPTIONS", contract=contract,
                    )
                response_last = option_bars[-1]["timestamp"]
                self.status["option_candle_age_seconds"][symbol] = max(
                    0.0,
                    (
                        current - (response_last.to_pydatetime() + BAR)
                    ).total_seconds(),
                )
                if expected_start is not None and response_last < pd.Timestamp(expected_start):
                    self.status["invalid_data_events"] += 1
                    engine.mark_data_quality_issue("STALE_OPTION_CANDLES")
                    option_failures.append({"symbol": symbol, "reason": "STALE_COMPLETED_CANDLES"})
                    self._record_observer_event(
                        "STALE_CANDLE_FEED", current, stream="OPTIONS", symbol=symbol,
                        reason="latest completed option candle is stale",
                        last_completed_candle=response_last.isoformat())
                    self.status["paper_positions"][symbol] = {
                        "l2l": self._position_summary(engine.state.get("l2l", {}).get("trade")),
                        "ekalayava": self._position_summary(engine.state.get("ekalayava", {}).get("trade")),
                        "last_completed_candle": engine.state.get("last_timestamp"),
                        "stale": True,
                        "data_quality_status": engine.state.get("data_quality_status"),
                        "missing_intervals": engine.state.get("missing_intervals", 0),
                    }
                    continue
                last_seen = engine.state.get("last_timestamp")
                total_response_bars = len(option_bars)
                if last_seen:
                    last_seen = _local(last_seen)
                    option_bars = [bar for bar in option_bars if bar["timestamp"] > last_seen]
                    suppressed = total_response_bars - len(option_bars)
                    if suppressed:
                        self._record_observer_event(
                            "DUPLICATE_CANDLES_SUPPRESSED", current, stream="OPTIONS",
                            symbol=symbol, last_completed_candle=last_seen.isoformat(),
                            suppressed_candle_count=suppressed)
                try:
                    for bar in option_bars:
                        nifty_price = nifty_by_time.get(bar["timestamp"].isoformat())
                        previous_missing = int(engine.state.get("missing_intervals", 0))
                        previous_candle = engine.state.get("last_timestamp")
                        try:
                            shadow.advance(bar)
                        except Exception as exc:
                            error_type = type(exc).__name__
                            self.status["shadow_candidate_errors"][symbol] = error_type
                            self._record_observer_event(
                                "SHADOW_CANDIDATE_ERROR", current, stream="OPTIONS",
                                symbol=symbol, error_type=error_type,
                                reason="isolated candidate state failed closed")
                            raise
                        events = engine.process_candle(bar, nifty_price=nifty_price)
                        for event in events:
                            try:
                                shadow.observe_signal(event)
                            except Exception as exc:
                                error_type = type(exc).__name__
                                self.status["shadow_candidate_errors"][symbol] = error_type
                                self._record_observer_event(
                                    "SHADOW_CANDIDATE_ERROR", current, stream="OPTIONS",
                                    symbol=symbol, error_type=error_type,
                                    reason="canonical signal could not initialize isolated candidates")
                                raise
                        missing_now = int(engine.state.get("missing_intervals", 0))
                        if missing_now > previous_missing:
                            missing_count = missing_now - previous_missing
                            self._record_observer_event(
                                "CANDLE_GAP_DETECTED", current, stream="OPTIONS", symbol=symbol,
                                reason="missing intervals between completed candles",
                                last_completed_candle=previous_candle,
                                missing_intervals=missing_count)
                            option_failures.append({
                                "symbol": symbol,
                                "reason": "MISSING_CANDLE_INTERVALS",
                                "missing_intervals": missing_count,
                            })
                        self.status["signals"].extend(
                            event for event in events if event.get("event_type") == "SIGNAL")
                        self.status["signals"] = self.status["signals"][-50:]
                except Exception as exc:
                    self.status["invalid_data_events"] += 1
                    reason = f"INVALID_CANDLE_SEQUENCE_{type(exc).__name__}"
                    option_failures.append({"symbol": symbol, "reason": reason})
                    self.status["paper_positions"][symbol] = {
                        "l2l": self._position_summary(engine.state.get("l2l", {}).get("trade")),
                        "ekalayava": self._position_summary(engine.state.get("ekalayava", {}).get("trade")),
                        "last_completed_candle": engine.state.get("last_timestamp"),
                        "stale": True,
                        "data_quality_status": engine.state.get("data_quality_status"),
                        "missing_intervals": engine.state.get("missing_intervals", 0),
                    }
                    self.status["shadow_candidates"][symbol] = [
                        dict(candidate)
                        for candidate in shadow.snapshot()["candidates"].values()
                    ]
                    LOG.warning("Exact option stream rejected (%s, %s)", symbol, type(exc).__name__)
                    continue
                last_bar = (option_bars[-1]["timestamp"].isoformat() if option_bars else
                            engine.state.get("last_timestamp"))
                self.status["last_option_candles"][symbol] = last_bar
                trade = engine.state.get("l2l", {}).get("trade") or engine.state.get("ekalayava", {}).get("trade")
                self.status["paper_positions"][symbol] = {
                    "l2l": self._position_summary(engine.state.get("l2l", {}).get("trade")),
                    "ekalayava": self._position_summary(engine.state.get("ekalayava", {}).get("trade")),
                    "last_completed_candle": last_bar,
                    "stale": False,
                    "data_quality_status": engine.state.get("data_quality_status"),
                    "missing_intervals": engine.state.get("missing_intervals", 0),
                }
            self.status["skipped"] = underlying_failures + option_failures + [
                {"option_type": kind, "itm_rank": rank, "reason": "NO_EXACT_CATALOG_CONTRACT"}
                for kind, rank in selection["missing"]
            ]
            if option_failures or selection["missing"]:
                self.status["health"] = "DEGRADED_OPTION_DATA"
            elif underlying_failures:
                self.status["health"] = "DEGRADED_UNDERLYING_DATA"
            else:
                self.status["health"] = "HEALTHY"
            if current >= session_close and self.status["health"] == "HEALTHY":
                self.status["health"] = "SESSION_COMPLETE"
            return self._finish_status(current)

    @staticmethod
    def _position_summary(trade):
        if not trade:
            return None
        return {key: trade.get(key) for key in (
            "status", "outcome", "entry", "entry_timestamp", "sl", "target",
            "sl_buffer_points", "exit_timestamp", "exit_price", "exit_reason",
            "mfe", "mae", "holding_time_minutes", "realized_pnl",
        )}

    def _persist_health(self):
        destination = self.state_dir / "observer_health.json"
        temporary = destination.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(self.status, sort_keys=True, default=str) + "\n", encoding="utf-8")
        temporary.replace(destination)

    def _finish_status(self, current):
        self.status["updated_at"] = current.isoformat()
        self._persist_health()
        return self.health_status()

    def health_status(self):
        """Return an operator-safe snapshot with no credential or token fields."""
        return json.loads(json.dumps(self.status, default=str))

    def run_forever(self, stop_requested=None, poll_seconds=60, max_backoff_seconds=300,
                    max_reconnect_attempts=5, now_fn=None, sleeper=None):
        """Run until stopped/session close; stop after bounded reconnect failures."""
        if max_reconnect_attempts < 1:
            raise ValueError("max_reconnect_attempts must be positive")
        now_fn = now_fn or (lambda: datetime.now(IST))
        sleeper = sleeper or sleep_time.sleep
        backoff = max(1, int(poll_seconds))
        reconnect_attempts = 0
        while not (stop_requested and stop_requested()):
            current = now_fn()
            current = current.replace(tzinfo=IST) if current.tzinfo is None else current.astimezone(IST)
            if self.config.kill_switch:
                self.status["health"] = "STOPPED_KILL_SWITCH"
                self.status["updated_at"] = current.isoformat()
                self._persist_health()
                return self.health_status()
            session = self.calendar.session_for(current.date())
            if session is None:
                self.status["health"] = "CLOSED_OR_CALENDAR_UNSUPPORTED"
                self.status["updated_at"] = current.isoformat()
                self._persist_health()
                return self.health_status()
            session_close = datetime.combine(current.date(), session.closes_at, IST)
            if current > session_close + BAR:
                self.status["health"] = "SESSION_CLOSED"
                self.status["updated_at"] = current.isoformat()
                self._persist_health()
                return self.health_status()
            if current < datetime.combine(current.date(), session.opens_at, IST):
                sleeper(max(1, int(poll_seconds)))
                continue
            snapshot = self.run_once(current)
            if snapshot["health"].startswith("DEGRADED"):
                if reconnect_attempts >= max_reconnect_attempts:
                    self.status["health"] = "STOPPED_RECONNECT_LIMIT"
                    self.status["updated_at"] = current.isoformat()
                    self._persist_health()
                    return self.health_status()
                reconnect_attempts += 1
                self.status["reconnect_attempts"] = reconnect_attempts
                wait = min(backoff, max_backoff_seconds)
                LOG.warning("Observer degraded; retrying with bounded backoff (%ss)", wait)
                self._reconnect_attempt += 1
                self._record_observer_event(
                    "RECONNECT_ATTEMPT", current, stream="GROWW_CLIENT",
                    reason="observer health degraded", retry_after_seconds=wait)
                if self.groww_factory is not None:
                    try:
                        self.groww = self.groww_factory()
                        self._record_observer_event(
                            "READ_ONLY_CLIENT_RECREATED", current, stream="GROWW_CLIENT",
                            reason="client factory returned a replacement client")
                    except Exception as exc:
                        self._record_observer_event(
                            "RECONNECT_FAILED", current, stream="GROWW_CLIENT",
                            error_type=type(exc).__name__)
                        LOG.warning("Read-only client reconnect failed (%s)", type(exc).__name__)
                backoff = min(max_backoff_seconds, max(backoff * 2, 1))
                sleeper(wait)
            else:
                reconnect_attempts = 0
                self.status["reconnect_attempts"] = 0
                backoff = max(1, int(poll_seconds))
                if current >= session_close:
                    self._persist_health()
                    return self.health_status()
                sleeper(max(1, int(poll_seconds)))
        self.status["health"] = "STOPPED_BY_OPERATOR"
        self.status["updated_at"] = datetime.now(IST).isoformat()
        self._persist_health()
        return self.health_status()


def authenticated_groww_factory(config=CFG):
    """Return a read-only Groww client factory without exposing credentials."""
    from .groww_auth import authenticate

    def create_authenticated_client():
        client = authenticate(config)
        profile = client.get_user_profile()
        if not isinstance(profile, dict):
            raise RuntimeError("Groww read-only profile verification returned an invalid response")
        return client

    return create_authenticated_client


def main():
    """Start an explicitly requested, supervised read-only observer session."""
    factory = authenticated_groww_factory(CFG)
    try:
        observer = GrowwPaperObserver(factory(), CFG, groww_factory=factory)
        observer.status["authentication_status"] = "READ_ONLY_PROFILE_VERIFIED"
    except Exception as exc:
        print(f"Paper observer startup failed ({type(exc).__name__}); credentials and provider details were not logged.")
        return 1
    try:
        result = observer.run_forever()
    except KeyboardInterrupt:
        observer.status["health"] = "STOPPED_BY_OPERATOR"
        observer.status["updated_at"] = datetime.now(IST).isoformat()
        observer._persist_health()
        print("Paper observer stopped by operator; no orders were sent.")
        return 0
    print(json.dumps({key: result.get(key) for key in (
        "health", "authentication_status", "trading_date", "selected_expiry",
        "selected_contracts", "missing_contracts", "contract_coverage",
        "contract_selection_timestamp", "underlying_reference_price",
        "underlying_reference_candle_timestamp", "last_underlying_candle",
        "underlying_candle_age_seconds", "option_candle_age_seconds",
        "missing_underlying_intervals", "last_option_candles", "signals",
        "duplicate_candles_suppressed", "invalid_data_events", "journal_status",
        "reconnect_attempts", "paper_positions",
        "shadow_candidates", "shadow_candidate_errors",
        "skipped", "errors", "kill_switch", "execution_allowed", "paper_only",
    )}, sort_keys=True, default=str))
    return 0


__all__ = ["GrowwPaperObserver", "authenticated_groww_factory"]


if __name__ == "__main__":
    raise SystemExit(main())
