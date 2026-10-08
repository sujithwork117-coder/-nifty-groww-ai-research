"""Stateful, causal paper signal/trade tracking for one option contract-day."""

from datetime import time, timedelta
import hashlib
import json
from pathlib import Path
import uuid

import pandas as pd

from .config import CFG
from .journal import append_paper_record
from .safety import ExecutionLock

IST = "Asia/Kolkata"
BAR = timedelta(minutes=5)
L2L_ID = uuid.UUID("c05e2553-5a17-47c2-9c08-1bdbd01c6287")
EKA_ID = uuid.UUID("44f38c62-55ae-42d4-88b1-1989c2381702")


def _local_timestamp(value):
    stamp = pd.Timestamp(value)
    return stamp.tz_localize(IST) if stamp.tzinfo is None else stamp.tz_convert(IST)


def _parse_time(value):
    hour, minute = str(value).split(":")[:2]
    return time(int(hour), int(minute))


class PaperContractEngine:
    """Process completed candles in order; never receives a future candle path."""

    def __init__(self, contract, config=CFG, journal_path=None, state_path=None,
                 data_quality_status="AVAILABLE"):
        ExecutionLock(config).assert_paper_only()
        self.config = config
        self.contract = dict(contract)
        self.journal_path = Path(journal_path) if journal_path else None
        self.state_path = Path(state_path) if state_path else None
        self.data_quality_status = data_quality_status
        self.state = self._empty_state()
        if self.state_path and self.state_path.exists():
            self.restore(json.loads(self.state_path.read_text(encoding="utf-8")))

    def _empty_state(self):
        return {
            "version": 1, "symbol": self.contract.get("symbol"),
            "config_signature": self._config_signature(),
            "date": None, "last_timestamp": None, "opening_high": None,
            "opening_low": None, "nifty_open": None, "nifty_last": None,
            "previous_highs": [], "data_quality_status": self.data_quality_status,
            "missing_intervals": 0, "entries_disabled": False,
            "l2l": {"phase": "WAITING_FOR_OPENING_CANDLE", "red_break_timestamp": None,
                    "signal": None, "trade": None, "daily_entry_used": False},
            "ekalayava": {"phase": "WAITING_FOR_OPENING_CANDLE", "breakdown_timestamp": None,
                           "candidate_low": None, "candidate_low_timestamp": None,
                           "swing_high": None, "swing_high_timestamp": None,
                           "signal": None, "daily_entry_used": False,
                           "setup_invalidated": False},
        }

    def _config_signature(self):
        return {"level_sl_points": float(self.config.level_sl_points),
                "level_entry_start": str(self.config.level_entry_start),
                "level_entry_end": str(self.config.level_entry_end),
                "ek_start": str(self.config.ek_start), "ek_end": str(self.config.ek_end)}

    def snapshot(self):
        return self.state.copy()

    def restore(self, state):
        if state.get("symbol") != self.contract.get("symbol"):
            raise ValueError("Paper state contract does not match the selected exact symbol")
        if state.get("config_signature") != self._config_signature():
            raise ValueError("Paper state strategy parameters do not match the active configuration")
        self.state = state
        return self

    def _persist(self):
        if not self.state_path:
            return
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.state_path.with_suffix(self.state_path.suffix + ".tmp")
        temp.write_text(json.dumps(self.state, sort_keys=True, default=str) + "\n", encoding="utf-8")
        temp.replace(self.state_path)

    def _emit(self, strategy, kind, candle, **values):
        state_key = "l2l" if strategy == "LEVEL_TO_LEVEL" else "ekalayava"
        record = {
            "event_type": kind, "strategy": strategy,
            "date": self.state["date"], "timestamp": candle["timestamp"].isoformat(),
            "close_time": candle["close_time"].isoformat(),
            "symbol": self.contract.get("symbol"), "expiry": self.contract.get("expiry"),
            "strike": self.contract.get("strike"), "option_type": self.contract.get("option_type"),
            "itm_rank": self.contract.get("itm_rank"), "nifty_price": self.state.get("nifty_last"),
            "opening_high": self.state.get("opening_high"), "opening_low": self.state.get("opening_low"),
            "data_quality_status": self.state.get("data_quality_status"),
            "missing_intervals": self.state.get("missing_intervals", 0),
            "execution": "DISABLED", "paper_only": True, **values,
        }
        event = self.state[state_key].get("signal")
        if kind == "SIGNAL":
            namespace = L2L_ID if strategy == "LEVEL_TO_LEVEL" else EKA_ID
            raw = f"{record['symbol']}|{record['date']}|{strategy}|{record['timestamp']}"
            record["event_id"] = str(uuid.uuid5(namespace, raw))
            self.state[state_key]["signal"] = record
            event = record
        elif event:
            record["event_id"] = event["event_id"]
            merged = {**event, **values}
            self.state[state_key]["signal"] = merged
        record_id = hashlib.sha256(
            f"{record.get('event_id', self.contract.get('symbol'))}|{kind}|{record['timestamp']}".encode()
        ).hexdigest()
        record["record_id"] = record_id
        if self.journal_path:
            append_paper_record(record, self.journal_path, self.config.model_version)
        return record

    def process_candle(self, candle, nifty_price=None):
        """Consume one finalized bar. Duplicates are ignored; out-of-order bars fail closed."""
        ExecutionLock(self.config).assert_paper_only()
        if candle.get("completed") is not True:
            raise ValueError("Only a proven completed 5-minute candle can enter the paper engine")
        stamp = _local_timestamp(candle["timestamp"])
        close_time = _local_timestamp(candle.get("close_time", stamp + BAR))
        if close_time != stamp + BAR:
            raise ValueError("Candle close time must equal the end of its five-minute bucket")
        if not (time(9, 15) <= stamp.time().replace(tzinfo=None) <= time(15, 25)):
            return []
        if stamp.minute % 5 or stamp.second or stamp.microsecond:
            raise ValueError("Candle timestamp must be a five-minute session bucket start")
        values = {key: float(candle[key]) for key in ("open", "high", "low", "close")}
        if (values["low"] > values["high"] or not values["low"] <= values["open"] <= values["high"]
                or not values["low"] <= values["close"] <= values["high"]):
            raise ValueError("Malformed OHLC candle")
        day = stamp.date().isoformat()
        last_value = self.state.get("last_timestamp")
        if last_value:
            last = _local_timestamp(last_value)
            if stamp == last:
                return []
            if stamp < last:
                raise ValueError("Out-of-order completed candle; replay/reconnect must resume from saved state")
            if stamp.date().isoformat() != day:
                raise ValueError("PaperContractEngine is scoped to one contract-day")
            gap = max(0, int((stamp - last) / BAR) - 1)
        else:
            gap = max(0, int((stamp - (stamp.normalize() + timedelta(hours=9, minutes=15))) / BAR))
            if stamp.time().replace(tzinfo=None) != time(9, 15):
                self.state["entries_disabled"] = True
                self.state["data_quality_status"] = "MISSING_OPENING_CANDLE"
        normalized = {**values, "timestamp": stamp, "close_time": close_time}
        if "missing_intervals_before" in candle:
            gap = max(gap, int(candle["missing_intervals_before"] or 0))
        if gap:
            self.state["missing_intervals"] = int(self.state.get("missing_intervals", 0)) + gap
            self.state["entries_disabled"] = True
            self.state["data_quality_status"] = "PARTIAL_MISSING_CANDLES"
            for key in ("l2l", "ekalayava"):
                if self.state[key].get("signal") is None:
                    self.state[key]["phase"] = "INVALIDATED_BY_DATA_GAP"
                if self.state[key].get("trade") and self.state[key]["trade"]["status"] == "OPEN":
                    self.state[key]["trade"]["status"] = "DATA_GAP_UNRESOLVED"
        self.state["date"] = day
        self.state["last_timestamp"] = stamp.isoformat()
        self.state["nifty_last"] = None if nifty_price is None else float(nifty_price)
        events = []

        if self.state["opening_high"] is None:
            if stamp.time().replace(tzinfo=None) == time(9, 15) and not gap:
                self.state["opening_high"] = values["high"]
                self.state["opening_low"] = values["low"]
                self.state["nifty_open"] = self.state["nifty_last"]
                self.state["l2l"]["phase"] = "WAITING_FOR_RED_BREAK"
                self.state["ekalayava"]["phase"] = "WAITING_FOR_OPENING_LOW_BREAK"
                self.state["previous_highs"] = [values["high"]]
            self._persist()
            return events

        prior_highs = self.state["previous_highs"][-2:]
        causal_swing = len(prior_highs) == 2 and values["high"] > max(prior_highs)

        self._update_l2l_trade(normalized, events)
        self._update_ekalayava_trade(normalized, events)
        self._detect_l2l(normalized, events)
        self._detect_ekalayava(normalized, events, causal_swing)
        self.state["previous_highs"].append(values["high"])
        self.state["previous_highs"] = self.state["previous_highs"][-3:]

        if stamp.time().replace(tzinfo=None) == time(15, 25):
            for strategy, key in (("LEVEL_TO_LEVEL", "l2l"), ("EKALAYAVA", "ekalayava")):
                current = self.state[key].get("signal")
                trade = self.state[key].get("trade")
                if current and trade and trade.get("status") in ("OPEN", "DATA_GAP_UNRESOLVED", "UNRESOLVED"):
                    final_status = "OPEN_AT_SESSION_END" if strategy == "LEVEL_TO_LEVEL" else "UNRESOLVED_AT_SESSION_END"
                    if trade.get("status") in ("OPEN", "UNRESOLVED"):
                        trade["status"] = final_status
                    events.append(self._emit(strategy, "SESSION_END_OBSERVATION", normalized,
                                             **trade))
        self._persist()
        return events

    def _detect_l2l(self, candle, events):
        setup = self.state["l2l"]
        if setup["daily_entry_used"] or self.state["entries_disabled"]:
            return
        now = candle["timestamp"].time().replace(tzinfo=None)
        if not (_parse_time(self.config.level_entry_start) <= now <= _parse_time(self.config.level_entry_end)):
            return
        opening_low = self.state["opening_low"]
        if setup["phase"] == "WAITING_FOR_RED_BREAK":
            if candle["close"] < candle["open"] and candle["low"] < opening_low:
                setup["red_break_timestamp"] = candle["timestamp"].isoformat()
                setup["phase"] = "WAITING_FOR_FIRST_GREEN"
            return
        if setup["phase"] != "WAITING_FOR_FIRST_GREEN" or candle["timestamp"].isoformat() == setup["red_break_timestamp"]:
            return
        if candle["close"] <= candle["open"]:
            return
        sl = opening_low - float(self.config.level_sl_points)
        target = self.state["opening_high"]
        status = "SKIPPED_SL_ALREADY_BREACHED" if candle["close"] <= sl else "OPEN"
        setup["daily_entry_used"] = True
        setup["phase"] = "ENTRY_SKIPPED" if status.startswith("SKIPPED") else "TRACKING_PAPER_TRADE"
        signal = self._emit("LEVEL_TO_LEVEL", "SIGNAL", candle,
                            entry=candle["close"], sl=sl, target=target,
                            entry_reason="first completed green candle after red opening-low breakdown",
                            candle_type="GREEN",
                            status=status, outcome=status, exit_timestamp=None, exit_reason=None,
                            red_break_timestamp=setup["red_break_timestamp"],
                            first_green_timestamp=candle["timestamp"].isoformat(),
                            reversal_structure=None, structural_low_candidate=None,
                            swing_high=None, breakout_timestamp=None,
                            mfe=0.0 if status.startswith("SKIPPED") else None,
                            mae=0.0 if status.startswith("SKIPPED") else None,
                            target_touch_timestamp=None,
                            structural_low_revisited=None, breakout_candle_low_revisited=None)
        events.append(signal)
        if status == "OPEN":
            setup["trade"] = {"entry": candle["close"], "entry_timestamp": candle["timestamp"].isoformat(),
                              "sl": sl, "target": target, "status": "OPEN", "mfe": None, "mae": None,
                              "exit_timestamp": None, "exit_reason": None}
            setup["phase"] = "TRACKING_PAPER_TRADE"

    def _update_l2l_trade(self, candle, events):
        setup = self.state["l2l"]
        trade = setup.get("trade")
        if not trade or candle["timestamp"].isoformat() <= trade["entry_timestamp"]:
            return
        if trade["status"] not in ("OPEN", "DATA_GAP_UNRESOLVED"):
            return
        high_delta = candle["high"] - trade["entry"]
        low_delta = candle["low"] - trade["entry"]
        trade["mfe"] = high_delta if trade["mfe"] is None else max(trade["mfe"], high_delta)
        trade["mae"] = low_delta if trade["mae"] is None else min(trade["mae"], low_delta)
        if trade["status"] == "OPEN":
            hit_sl, hit_target = candle["low"] <= trade["sl"], candle["high"] >= trade["target"]
            if hit_sl and hit_target:
                trade.update(status="AMBIGUOUS", exit_timestamp=candle["timestamp"].isoformat(),
                             exit_reason="SL_AND_TARGET_TOUCHED_SAME_CANDLE", exit_price=None)
            elif hit_sl:
                trade.update(status="SL", exit_timestamp=candle["timestamp"].isoformat(),
                             exit_reason="STOP_LOSS", exit_price=trade["sl"])
            elif hit_target:
                trade.update(status="TARGET", exit_timestamp=candle["timestamp"].isoformat(),
                             exit_reason="TARGET", exit_price=trade["target"])
        update = {**trade, "points_gained_lost": (
            trade["exit_price"] - trade["entry"] if trade.get("exit_price") is not None else None),
            "outcome": trade["status"]}
        events.append(self._emit("LEVEL_TO_LEVEL", "TRADE_UPDATE", candle, **update))

    def _detect_ekalayava(self, candle, events, causal_swing):
        setup = self.state["ekalayava"]
        if setup["daily_entry_used"] or setup["setup_invalidated"] or self.state["entries_disabled"]:
            return
        now = candle["timestamp"].time().replace(tzinfo=None)
        if now < _parse_time(self.config.ek_start):
            return
        if now > _parse_time(self.config.ek_end):
            setup["setup_invalidated"] = True
            setup["phase"] = "ENTRY_WINDOW_CLOSED"
            return
        if candle["high"] >= self.state["opening_high"]:
            setup["setup_invalidated"] = True
            setup["phase"] = "TARGET_REACHED_BEFORE_ENTRY"
            return
        if setup["breakdown_timestamp"] is None:
            if candle["low"] < self.state["opening_low"]:
                setup["breakdown_timestamp"] = candle["timestamp"].isoformat()
                setup["candidate_low"] = candle["low"]
                setup["candidate_low_timestamp"] = candle["timestamp"].isoformat()
                setup["phase"] = "RECOVERY_AND_SWING_OBSERVATION"
            return
        if candle["low"] < setup["candidate_low"]:
            setup["candidate_low"] = candle["low"]
            setup["candidate_low_timestamp"] = candle["timestamp"].isoformat()
        if setup["swing_high"] is not None and candle["high"] > setup["swing_high"] and candle["close"] > setup["swing_high"]:
            candidate_low = setup["candidate_low"]
            signal = self._emit("EKALAYAVA", "SIGNAL", candle,
                                entry=candle["close"], sl=None, candidate_sl=candidate_low,
                                entry_reason="completed causal swing-high breakout before opening-high target",
                                candle_type="GREEN" if candle["close"] > candle["open"] else "RED_OR_DOJI",
                                candidate_sl_status="OBSERVATION_ONLY_UNAPPROVED",
                                target=self.state["opening_high"], status="UNRESOLVED",
                                outcome="UNRESOLVED", exit_timestamp=None, exit_reason=None,
                                breakdown_timestamp=setup["breakdown_timestamp"],
                                reversal_structure="causal recovery following opening-low breakdown; exact structural anchor undefined",
                                structural_low_candidate=candidate_low,
                                structural_low_timestamp=setup["candidate_low_timestamp"],
                                swing_high=setup["swing_high"],
                                swing_high_timestamp=setup["swing_high_timestamp"],
                                breakout_timestamp=candle["timestamp"].isoformat(),
                                breakout_candle_low=candle["low"], mfe=None, mae=None,
                                time_to_mfe_minutes=None, time_to_mae_minutes=None,
                                target_touch_timestamp=None, time_to_target_minutes=None,
                                structural_low_revisited=False,
                                breakout_candle_low_revisited=False,
                                opening_low_revisited=False,
                                target_and_candidate_low_same_candle=False,
                                realized_pnl=None)
            events.append(signal)
            setup["daily_entry_used"] = True
            setup["phase"] = "OBSERVING_UNRESOLVED_ENTRY"
            setup["signal"] = signal
            setup["trade"] = {"entry": candle["close"], "entry_timestamp": candle["timestamp"].isoformat(),
                              "target": self.state["opening_high"], "candidate_sl": candidate_low,
                              "candidate_low": candidate_low, "breakout_candle_low": candle["low"],
                              "status": "UNRESOLVED", "mfe": None, "mae": None,
                              "time_to_mfe_minutes": None, "time_to_mae_minutes": None,
                              "target_touch_timestamp": None, "time_to_target_minutes": None,
                              "structural_low_revisited": False,
                              "breakout_candle_low_revisited": False, "opening_low_revisited": False,
                              "target_and_candidate_low_same_candle": False,
                              "realized_pnl": None}
            return
        if causal_swing:
            setup["swing_high"] = candle["high"]
            setup["swing_high_timestamp"] = candle["timestamp"].isoformat()

    def _update_ekalayava_trade(self, candle, events):
        setup = self.state["ekalayava"]
        trade = setup.get("trade")
        if not trade or candle["timestamp"].isoformat() <= trade["entry_timestamp"]:
            return
        high_delta, low_delta = candle["high"] - trade["entry"], candle["low"] - trade["entry"]
        elapsed = (candle["timestamp"] - _local_timestamp(trade["entry_timestamp"])).total_seconds() / 60
        if trade["mfe"] is None or high_delta > trade["mfe"]:
            trade["mfe"] = high_delta
            trade["time_to_mfe_minutes"] = elapsed
        if trade["mae"] is None or low_delta < trade["mae"]:
            trade["mae"] = low_delta
            trade["time_to_mae_minutes"] = elapsed
        if trade["target_touch_timestamp"] is None and candle["high"] >= trade["target"]:
            trade["target_touch_timestamp"] = candle["timestamp"].isoformat()
            trade["time_to_target_minutes"] = elapsed
        trade["structural_low_revisited"] = trade["structural_low_revisited"] or candle["low"] <= trade["candidate_low"]
        trade["breakout_candle_low_revisited"] = trade["breakout_candle_low_revisited"] or candle["low"] <= trade["breakout_candle_low"]
        trade["opening_low_revisited"] = trade["opening_low_revisited"] or candle["low"] <= self.state["opening_low"]
        trade["target_and_candidate_low_same_candle"] = (
            trade["target_and_candidate_low_same_candle"] or
            (candle["high"] >= trade["target"] and candle["low"] <= trade["candidate_low"]))
        events.append(self._emit("EKALAYAVA", "OBSERVATION_UPDATE", candle,
                                 **trade, sl=None,
                                 candidate_sl_status="OBSERVATION_ONLY_UNAPPROVED",
                                 outcome="UNRESOLVED"))
