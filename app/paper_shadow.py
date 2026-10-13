"""Isolated deterministic Ekalayava exit-candidate shadow tracking.

Candidate state is separate from canonical strategy state and never produces
broker instructions. All prices are hypothetical premium points.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta
import hashlib
import json
import math
from pathlib import Path

from .config import CFG
from .journal import append_paper_record
from .safety import ExecutionLock


BAR = timedelta(minutes=5)
SESSION_LAST = time(15, 25)
CANDIDATES = (
    {"candidate_id": "A_B4_OPENING_HIGH_V1", "buffer": 4.0, "target": "OPENING_HIGH"},
    {"candidate_id": "A_B4_TP25_V1", "buffer": 4.0, "target": "FIXED_25"},
    {"candidate_id": "A_STRUCTURAL_TROUGH_B4_TP25", "buffer": 4.0, "target": "FRACTIONAL_25"},
    {"candidate_id": "B_B2_LOWER_LOW_TRAIL_OPENING_HIGH_V1", "buffer": 2.0,
     "target": "OPENING_HIGH", "trailing": True},
    {"candidate_id": "C_B2_1R_V1", "buffer": 2.0, "target": "R_MULTIPLE", "multiple": 1.0},
    {"candidate_id": "C_B2_1_5R_V1", "buffer": 2.0, "target": "R_MULTIPLE", "multiple": 1.5},
    {"candidate_id": "C_B2_2R_V1", "buffer": 2.0, "target": "R_MULTIPLE", "multiple": 2.0},
)


def _stamp(value) -> datetime:
    result = value if isinstance(value, datetime) else datetime.fromisoformat(
        str(value).replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Shadow timestamps must include a timezone")
    return result


def _target(spec, entry, stop, opening_high):
    target_kind = spec["target"]
    if target_kind == "OPENING_HIGH":
        return opening_high
    if target_kind == "FIXED_25":
        return entry + 25.0
    if target_kind == "FRACTIONAL_25":
        return entry + 0.25 * (opening_high - entry)
    if target_kind == "R_MULTIPLE":
        return entry + (entry - stop) * spec["multiple"]
    raise ValueError(f"Unknown candidate target kind: {target_kind}")


class EkalayavaShadowBook:
    """Persist and advance independent candidate states for canonical signals."""

    def __init__(self, state_path, journal_path=None, config=CFG):
        ExecutionLock(config).assert_paper_only()
        self.config = config
        self.state_path = Path(state_path)
        self.journal_path = Path(journal_path) if journal_path else None
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state = {"version": 1, "candidates": {}}
        if self.state_path.exists():
            self.state = json.loads(self.state_path.read_text(encoding="utf-8"))
            if self.state.get("version") != 1 or not isinstance(self.state.get("candidates"), dict):
                raise ValueError("Invalid shadow state schema")

    def _persist(self):
        temporary = self.state_path.with_suffix(self.state_path.suffix + ".tmp")
        temporary.write_text(json.dumps(self.state, sort_keys=True, separators=(",", ":")) + "\n",
                             encoding="utf-8")
        temporary.replace(self.state_path)

    def _record(self, candidate, kind, timestamp, *, source_candle_timestamp=None):
        stamp = _stamp(timestamp)
        setup_id = candidate["setup_id"]
        candidate_id = candidate["candidate_id"]
        event_id = hashlib.sha256(f"{setup_id}|{candidate_id}|{kind}|{stamp.isoformat()}".encode()).hexdigest()
        row = {
            "record_id": hashlib.sha256(f"{event_id}|{kind}".encode()).hexdigest(),
            "event_id": event_id,
            "setup_id": setup_id,
            "event_type": kind,
            "strategy": "EKALAYAVA_SHADOW",
            "strategy_version": candidate["strategy_version"],
            "simulation_mode": "ISOLATED_SHADOW_CANDIDATE",
            "exit_model_version": candidate_id,
            "candidate_id": candidate_id,
            "date": candidate["date"],
            "timestamp": stamp.isoformat(),
            "source_candle_timestamp": source_candle_timestamp,
            "symbol": candidate["symbol"],
            "expiry": candidate.get("expiry"),
            "strike": candidate.get("strike"),
            "option_type": candidate.get("option_type"),
            "itm_rank": candidate.get("itm_rank"),
            "entry": candidate["entry"],
            "entry_timestamp": candidate["entry_timestamp"],
            "sl": candidate["initial_stop"],
            "target": candidate["target"],
            "hypothetical_stop": candidate["active_stop"],
            "hypothetical_target": candidate["target"],
            "hypothetical_exit_price": candidate.get("exit_price"),
            "hypothetical_points": candidate.get("points"),
            "stop_updates_json": json.dumps(candidate["stop_updates"], sort_keys=True, separators=(",", ":")),
            "candidate_state_json": json.dumps(candidate, sort_keys=True, separators=(",", ":")),
            "status": candidate["status"],
            "outcome": candidate.get("outcome"),
            "quote_timestamp": None,
            "bid": None,
            "ask": None,
            "spread_points": None,
            "fill_assumption": None,
            "cost_points": None,
            "cost_provenance": None,
            "execution": "DISABLED",
            "paper_only": True,
        }
        if self.journal_path:
            append_paper_record(row, self.journal_path, self.config.model_version)

    def observe_signal(self, event):
        """Create candidates only from a canonical Ekalayava signal event."""
        if event.get("strategy") != "EKALAYAVA" or event.get("event_type") != "SIGNAL":
            return False
        setup_id = event.get("setup_id") or event.get("event_id")
        if not setup_id:
            raise ValueError("Canonical Ekalayava signal requires a stable setup ID")
        setup_id = str(setup_id)
        created = False
        entry_time = _stamp(event["timestamp"])
        entry_timestamp = entry_time.isoformat()
        entry = float(event["entry"])
        signal_date = str(event.get("date", entry_time.date().isoformat()))
        strategy_version = event.get("strategy_version", "unknown")
        anchor = event.get("structural_low_candidate", event.get("structural_low_price"))
        if anchor is None or not math.isfinite(float(anchor)):
            raise ValueError("Canonical Ekalayava signal lacks its structural trough")
        anchor = float(anchor)
        opening_high = float(event["opening_high"])
        if not all(math.isfinite(value) for value in (entry, anchor, opening_high)):
            raise ValueError("Canonical signal levels must be finite")
        for spec in CANDIDATES:
            key = f"{setup_id}|{spec['candidate_id']}"
            if key in self.state["candidates"]:
                existing = self.state["candidates"][key]
                if (existing.get("event_id") != event.get("event_id")
                        or existing.get("entry_timestamp") != entry_timestamp
                        or existing.get("entry") != entry
                        or existing.get("structural_anchor") != anchor
                        or existing.get("opening_high") != opening_high
                        or existing.get("symbol") != event.get("symbol")
                        or existing.get("expiry") != event.get("expiry")
                        or existing.get("strike") != event.get("strike")
                        or existing.get("option_type") != event.get("option_type")
                        or existing.get("itm_rank") != event.get("itm_rank")
                        or existing.get("strategy_version") != strategy_version
                        or existing.get("date") != signal_date):
                    raise ValueError("Canonical signal identity conflicts with persisted shadow state")
                continue
            stop = anchor - spec["buffer"]
            target = float(_target(spec, entry, stop, opening_high))
            if stop >= entry:
                status, outcome = "EXCLUDED", "EXCLUDED_INVALID_STOP"
            elif target <= entry:
                status, outcome = "EXCLUDED", "EXCLUDED_INVALID_TARGET"
            else:
                status, outcome = "OPEN", None
            candidate = {
                "setup_id": setup_id,
                "event_id": event.get("event_id"),
                "candidate_id": spec["candidate_id"],
                "strategy_version": strategy_version,
                "date": signal_date,
                "symbol": event.get("symbol"),
                "expiry": event.get("expiry"),
                "strike": event.get("strike"),
                "option_type": event.get("option_type"),
                "itm_rank": event.get("itm_rank"),
                "entry": entry,
                "entry_timestamp": entry_timestamp,
                "opening_high": opening_high,
                "structural_anchor": anchor,
                "initial_stop": stop,
                "active_stop": stop,
                "target": target,
                "trailing": bool(spec.get("trailing", False)),
                "stop_updates": [],
                "post_entry_lows": [],
                "last_timestamp": entry_time.isoformat(),
                "status": status,
                "outcome": outcome,
                "exit_timestamp": None,
                "exit_price": None,
                "points": None,
                "source_candle_timestamp": None,
                "quote_timestamp": None,
                "bid": None,
                "ask": None,
                "spread_points": None,
                "fill_assumption": None,
                "cost_points": None,
                "cost_provenance": None,
                "execution": "DISABLED",
                "paper_only": True,
            }
            self.state["candidates"][key] = candidate
            self._record(candidate, "SHADOW_CANDIDATE_OPEN", entry_time,
                         source_candle_timestamp=entry_time.isoformat())
            created = True
        self._persist()
        return created

    def advance(self, candle):
        """Advance all open candidates by one completed candle, once."""
        if candle.get("completed") is not True:
            raise ValueError("Shadow evaluation requires a completed candle")
        stamp = _stamp(candle["timestamp"])
        close_time = _stamp(candle.get("close_time", stamp + BAR))
        if close_time != stamp + BAR or stamp.minute % 5:
            raise ValueError("Invalid five-minute completed candle boundary")
        values = {name: float(candle[name]) for name in ("open", "high", "low", "close")}
        if (not all(math.isfinite(value) for value in values.values())
                or values["low"] > values["high"]
                or not values["low"] <= values["open"] <= values["high"]
                or not values["low"] <= values["close"] <= values["high"]):
            raise ValueError("Invalid OHLC candle")
        changed = False
        for candidate in self.state["candidates"].values():
            if candidate["status"] != "OPEN" or candle.get("symbol") not in (None, candidate.get("symbol")):
                continue
            previous = _stamp(candidate["last_timestamp"])
            if stamp <= previous:
                if stamp == previous:
                    continue
                raise ValueError("Out-of-order shadow candle")
            if stamp.date() != previous.date() or stamp - previous != BAR:
                candidate["status"] = "UNRESOLVED"
                candidate["outcome"] = "UNRESOLVED_DATA_GAP"
                candidate["last_timestamp"] = stamp.isoformat()
                self._record(candidate, "SHADOW_CANDIDATE_UNRESOLVED", stamp,
                             source_candle_timestamp=stamp.isoformat())
                changed = True
                continue
            stop, target = candidate["active_stop"], candidate["target"]
            outcome = exit_price = None
            if values["open"] <= stop:
                outcome, exit_price = "STOP_LOSS", values["open"]
            elif values["open"] >= target:
                outcome, exit_price = "TARGET", target
            else:
                hit_stop, hit_target = values["low"] <= stop, values["high"] >= target
                if hit_stop and hit_target:
                    outcome = "AMBIGUOUS"
                elif hit_stop:
                    outcome, exit_price = "STOP_LOSS", stop
                elif hit_target:
                    outcome, exit_price = "TARGET", target
            candidate["last_timestamp"] = stamp.isoformat()
            if outcome:
                candidate["status"] = "CLOSED" if outcome != "AMBIGUOUS" else "AMBIGUOUS"
                candidate["outcome"] = outcome
                candidate["exit_timestamp"] = stamp.isoformat()
                candidate["exit_price"] = exit_price
                candidate["points"] = None if exit_price is None else exit_price - candidate["entry"]
                candidate["source_candle_timestamp"] = stamp.isoformat()
                self._record(candidate, "SHADOW_CANDIDATE_EXIT", stamp,
                             source_candle_timestamp=stamp.isoformat())
                changed = True
                continue
            if candidate["trailing"] and len(candidate["post_entry_lows"]) >= 2:
                if values["low"] < min(candidate["post_entry_lows"][-2:]):
                    proposed = values["low"] - 2.0
                    if proposed > candidate["active_stop"]:
                        candidate["active_stop"] = proposed
                        update = {
                            "source_timestamp": stamp.isoformat(),
                            "effective_from_timestamp": (stamp + BAR).isoformat(),
                            "source_low": values["low"],
                            "new_stop": proposed,
                        }
                        candidate["stop_updates"].append(update)
                        self._record(candidate, "SHADOW_CANDIDATE_STOP_UPDATE", stamp,
                                     source_candle_timestamp=stamp.isoformat())
                        changed = True
            candidate["post_entry_lows"].append(values["low"])
            candidate["post_entry_lows"] = candidate["post_entry_lows"][-2:]
            if stamp.time().replace(tzinfo=None) == SESSION_LAST:
                candidate["status"] = "CLOSED"
                candidate["outcome"] = "END_OF_SESSION"
                candidate["exit_timestamp"] = stamp.isoformat()
                candidate["exit_price"] = values["close"]
                candidate["points"] = values["close"] - candidate["entry"]
                candidate["source_candle_timestamp"] = stamp.isoformat()
                self._record(candidate, "SHADOW_CANDIDATE_EXIT", stamp,
                             source_candle_timestamp=stamp.isoformat())
            changed = True
        if changed:
            self._persist()

    def snapshot(self):
        return json.loads(json.dumps(self.state, sort_keys=True))
