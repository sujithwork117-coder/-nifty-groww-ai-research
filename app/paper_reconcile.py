"""Read-only integrity and outcome reconciliation for one observer session."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json
import math
from pathlib import Path

from .paper_shadow import CANDIDATES

BAR = timedelta(minutes=5)
REQUIRED_FIELDS = {"record_id", "event_type", "timestamp"}
TERMINAL_OUTCOMES = {"TARGET", "STOP_LOSS", "AMBIGUOUS", "END_OF_SESSION"}


def _timestamp(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return parsed


def _read_json(path, label, errors):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{label}: {type(exc).__name__}")
        return None


def reconcile_session(session_dir):
    """Read and reconcile a session directory without modifying its contents."""
    root = Path(session_dir)
    errors = []
    warnings = []
    health_path = root / "observer_health.json"
    journal_path = root / "paper_journal.jsonl"
    health_location = "session_directory"
    if not health_path.is_file() and (root.parent / "observer_health.json").is_file():
        health_path = root.parent / "observer_health.json"
        health_location = "observer_parent"
    health = _read_json(health_path, "observer_health.json", errors)
    if not isinstance(health, dict):
        errors.append("observer_health.json must contain a JSON object")
    elif (len(root.name) == 10 and root.name[4:5] == "-" and root.name[7:8] == "-"
          and health.get("trading_date") not in (None, root.name)):
        errors.append("session directory date does not match observer health trading_date")

    records = []
    if not journal_path.is_file():
        errors.append("paper_journal.jsonl is missing")
    else:
        with journal_path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                try:
                    record = json.loads(line)
                    if not isinstance(record, dict):
                        raise ValueError("record must be an object")
                    missing = sorted(REQUIRED_FIELDS - record.keys())
                    if missing:
                        raise ValueError(f"missing required fields: {','.join(missing)}")
                    if not isinstance(record["record_id"], str) or not record["record_id"]:
                        raise ValueError("record_id must be a non-empty string")
                    if not isinstance(record["event_type"], str) or not record["event_type"]:
                        raise ValueError("event_type must be a non-empty string")
                    _timestamp(record["timestamp"])
                    for timestamp_field in (
                        "recorded_at", "close_time", "entry_timestamp", "exit_timestamp",
                        "source_candle_timestamp", "quote_timestamp", "target_touch_timestamp",
                        "red_break_timestamp", "first_green_timestamp", "breakdown_timestamp",
                        "structural_low_timestamp", "swing_high_timestamp", "breakout_timestamp",
                    ):
                        timestamp_value = record.get(timestamp_field)
                        if timestamp_value is not None:
                            _timestamp(timestamp_value)
                    if record.get("event_type") == "CANDLE_OBSERVED":
                        candle_fields = {
                            "close_time", "stream", "symbol", "open", "high", "low", "close",
                            "data_provenance", "source_retrieved_at",
                        }
                        missing_schema = sorted(candle_fields - record.keys())
                        if missing_schema:
                            raise ValueError(f"incomplete candle schema: {','.join(missing_schema)}")
                        if not isinstance(record["stream"], str) or not isinstance(record["symbol"], str):
                            raise ValueError("candle stream and symbol must be strings")
                        if record.get("close_time") is None:
                            raise ValueError("candle is missing its completed close_time")
                        start, close = _timestamp(record["timestamp"]), _timestamp(record["close_time"])
                        if close != start + BAR:
                            raise ValueError("candle close_time does not match five-minute boundary")
                        if start.minute % 5 or start.second or start.microsecond:
                            raise ValueError("candle timestamp is off the five-minute grid")
                        ohlc = [float(record[key]) for key in ("open", "high", "low", "close")]
                        if not all(math.isfinite(value) for value in ohlc):
                            raise ValueError("candle OHLC values must be finite")
                        opening, high, low, closing = ohlc
                        if low > high or not low <= opening <= high or not low <= closing <= high:
                            raise ValueError("candle OHLC values are inconsistent")
                    if (record.get("event_type") == "SIGNAL"
                            and not (record.get("setup_id") or record.get("event_id"))):
                        raise ValueError("canonical signal is missing its stable setup identity")
                    if record.get("simulation_mode") == "ISOLATED_SHADOW_CANDIDATE":
                        required_shadow_fields = {
                            "setup_id", "candidate_id", "candidate_state_json",
                            "hypothetical_points", "quote_timestamp", "bid", "ask",
                            "fill_assumption", "cost_points", "source_candle_timestamp",
                        }
                        missing_shadow_fields = sorted(required_shadow_fields - record.keys())
                        if missing_shadow_fields:
                            raise ValueError(
                                f"incomplete shadow event schema: {','.join(missing_shadow_fields)}"
                            )
                        if record.get("candidate_id") not in {
                            candidate["candidate_id"] for candidate in CANDIDATES
                        }:
                            raise ValueError("unknown shadow candidate identity")
                        try:
                            candidate_snapshot = json.loads(record["candidate_state_json"])
                        except (TypeError, json.JSONDecodeError) as exc:
                            raise ValueError("invalid candidate_state_json") from exc
                        if not isinstance(candidate_snapshot, dict):
                            raise ValueError("candidate_state_json must contain an object")
                        if (candidate_snapshot.get("setup_id") != record["setup_id"]
                                or candidate_snapshot.get("candidate_id") != record["candidate_id"]
                                or candidate_snapshot.get("outcome") != record.get("outcome")
                                or candidate_snapshot.get("points") != record.get("hypothetical_points")
                                or candidate_snapshot.get("status") != record.get("status")):
                            raise ValueError("shadow event fields disagree with candidate_state_json")
                    records.append(record)
                except (json.JSONDecodeError, TypeError, ValueError) as exc:
                    errors.append(f"journal line {line_number}: {exc}")

    ids = Counter(record.get("record_id") for record in records)
    duplicates = sorted(record_id for record_id, count in ids.items() if count > 1)
    if duplicates:
        errors.append(f"duplicate record_id values: {len(duplicates)}")

    candles = defaultdict(list)
    for record in records:
        if record.get("event_type") == "CANDLE_OBSERVED":
            stream = record.get("stream") or (
                "NIFTY" if record.get("symbol") == "NIFTY" else "OPTIONS"
            )
            candles[(stream, record.get("symbol"))].append(record)
    candle_findings = []
    for (stream, symbol), group in sorted(candles.items(), key=lambda item: str(item[0])):
        input_stamps = [_timestamp(row["timestamp"]) for row in group]
        ordered = sorted(group, key=lambda row: _timestamp(row["timestamp"]))
        stamps = [_timestamp(row["timestamp"]) for row in ordered]
        repeated = sorted({stamp.isoformat() for stamp, count in Counter(stamps).items() if count > 1})
        out_of_order = any(right < left for left, right in zip(input_stamps, input_stamps[1:]))
        gaps = [
            {"after": left.isoformat(), "before": right.isoformat(),
             "missing_intervals": int((right - left) / BAR) - 1}
            for left, right in zip(stamps, stamps[1:])
            if right - left > BAR
        ]
        last = stamps[-1] if stamps else None
        candle_findings.append({
            "stream": stream,
            "symbol": symbol,
            "candle_count": len(group),
            "first_timestamp": stamps[0].isoformat() if stamps else None,
            "last_timestamp": last.isoformat() if last else None,
            "has_session_final_bar": bool(last and last.time().replace(tzinfo=None).isoformat() == "15:25:00"),
            "duplicate_timestamps": repeated,
            "out_of_order": out_of_order,
            "gaps": gaps,
            "incomplete_path": not bool(last and last.time().replace(tzinfo=None).isoformat() == "15:25:00"),
        })
        if repeated:
            errors.append(f"duplicate candle timestamps for {symbol}")
        if out_of_order:
            errors.append(f"out-of-order candle records for {symbol}")
        if gaps or not (last and last.time().replace(tzinfo=None).isoformat() == "15:25:00"):
            warnings.append(f"candle path incomplete for {symbol}")

    strategy_signals = [
        row for row in records
        if row.get("event_type") == "SIGNAL"
        and row.get("strategy") in {"EKALAYAVA", "LEVEL_TO_LEVEL"}
    ]
    signal_keys = [
        (str(row["strategy"]), str(row.get("setup_id") or row.get("event_id")))
        for row in strategy_signals
    ]
    signal_counts = Counter(signal_keys)
    duplicate_signal_ids = [
        {"strategy": strategy, "setup_id": setup_id}
        for strategy, setup_id in sorted(signal_counts)
        if signal_counts[(strategy, setup_id)] > 1
    ]
    if duplicate_signal_ids:
        errors.append(f"duplicate canonical signal identities: {len(duplicate_signal_ids)}")
    signal_ids = {
        setup_id for strategy, setup_id in signal_keys if strategy == "EKALAYAVA"
    }
    state_signals = {}
    candidate_states = []
    for path in sorted(root.glob("*.json")):
        if path.name == "observer_health.json":
            continue
        state = _read_json(path, path.name, errors)
        if not isinstance(state, dict):
            continue
        for strategy, state_key in (("EKALAYAVA", "ekalayava"), ("LEVEL_TO_LEVEL", "l2l")):
            strategy_state = state.get(state_key)
            signal = strategy_state.get("signal") if isinstance(strategy_state, dict) else None
            if isinstance(signal, dict):
                setup_id = str(signal.get("setup_id") or signal.get("event_id") or "")
                if setup_id:
                    state_signals[(strategy, setup_id)] = signal
        candidates = state.get("candidates")
        if isinstance(candidates, dict):
            candidate_states.extend(candidates.values())
    signal_key_set = set(signal_keys)
    unmatched_signals = sorted(signal_key_set - state_signals.keys())
    orphan_states = sorted(state_signals.keys() - signal_key_set)
    if unmatched_signals:
        errors.append("canonical signals missing matching strategy state")
    if orphan_states:
        errors.append("strategy states missing matching canonical observation")
    journal_signals = {
        (str(row["strategy"]), str(row.get("setup_id") or row.get("event_id"))): row
        for row in strategy_signals
    }
    state_observation_mismatches = []
    for key in sorted(signal_key_set & state_signals.keys()):
        journal_signal = journal_signals[key]
        persisted_signal = state_signals[key]
        for field in ("timestamp", "symbol", "entry", "opening_high"):
            if (field in journal_signal and field in persisted_signal
                    and journal_signal[field] != persisted_signal[field]):
                state_observation_mismatches.append(
                    {"strategy": key[0], "setup_id": key[1], "field": field}
                )
    if state_observation_mismatches:
        errors.append("persisted strategy states disagree with canonical observations")
    shadow_setup_ids = {str(candidate.get("setup_id")) for candidate in candidate_states
                        if isinstance(candidate, dict)}
    candidate_keys = [
        (str(candidate.get("setup_id")), str(candidate.get("candidate_id")))
        for candidate in candidate_states
        if isinstance(candidate, dict) and candidate.get("setup_id") and candidate.get("candidate_id")
    ]
    duplicate_candidate_states = sorted(
        f"{setup_id}|{candidate_id}"
        for (setup_id, candidate_id), count in Counter(candidate_keys).items()
        if count > 1
    )
    if duplicate_candidate_states:
        errors.append(f"duplicate persisted candidate states: {len(duplicate_candidate_states)}")
    expected_candidate_ids = {candidate["candidate_id"] for candidate in CANDIDATES}
    present_candidates = defaultdict(set)
    for setup_id, candidate_id in candidate_keys:
        present_candidates[setup_id].add(candidate_id)
    missing_shadow = {
        setup_id: sorted(expected_candidate_ids - present_candidates.get(setup_id, set()))
        for setup_id in sorted(signal_ids)
        if expected_candidate_ids - present_candidates.get(setup_id, set())
    }
    shadow_without_signal = sorted(shadow_setup_ids - signal_ids)
    if missing_shadow:
        errors.append("canonical signals missing one or more candidate shadow states")
    if shadow_without_signal:
        errors.append("candidate shadow states missing canonical signal")

    terminal_rows = [
        row for row in records
        if row.get("event_type") == "SHADOW_CANDIDATE_EXIT"
        or (row.get("event_type") == "SHADOW_CANDIDATE_UNRESOLVED")
    ]
    terminal_by_key = defaultdict(list)
    candidate_metrics = defaultdict(Counter)
    candidate_points = defaultdict(float)
    candidate_null_points = Counter()
    candidate_zero_points = Counter()
    for row in terminal_rows:
        key = (str(row.get("setup_id")), str(row.get("candidate_id")))
        terminal_by_key[key].append(row)
        candidate = str(row.get("candidate_id") or "UNKNOWN")
        outcome = row.get("outcome")
        if outcome in TERMINAL_OUTCOMES or (isinstance(outcome, str) and outcome.startswith("UNRESOLVED")):
            candidate_metrics[candidate][str(outcome)] += 1
        points = row.get("hypothetical_points")
        if points is None:
            candidate_null_points[candidate] += 1
        else:
            try:
                value = float(points)
            except (TypeError, ValueError):
                errors.append(f"invalid hypothetical points for {candidate}")
                continue
            if not math.isfinite(value):
                errors.append(f"non-finite hypothetical points for {candidate}")
                continue
            candidate_points[candidate] += value
            if value == 0:
                candidate_zero_points[candidate] += 1
    conflicts = []
    for key, group in terminal_by_key.items():
        if len(group) > 1:
            conflicts.append({"setup_id": key[0], "candidate_id": key[1],
                              "outcomes": sorted({str(row.get("outcome")) for row in group}),
                              "event_count": len(group)})
    if conflicts:
        errors.append(f"conflicting terminal candidate events: {len(conflicts)}")
    persisted_candidate_map = {
        (str(candidate.get("setup_id")), str(candidate.get("candidate_id"))): candidate
        for candidate in candidate_states
        if isinstance(candidate, dict) and candidate.get("setup_id") and candidate.get("candidate_id")
    }
    terminal_state_mismatches = []
    for key, group in terminal_by_key.items():
        persisted = persisted_candidate_map.get(key)
        if persisted is None:
            terminal_state_mismatches.append({"setup_id": key[0], "candidate_id": key[1],
                                              "reason": "missing persisted state"})
            continue
        for row in group:
            timestamp_mismatch = (
                row.get("event_type") == "SHADOW_CANDIDATE_EXIT"
                and row.get("timestamp") != persisted.get("exit_timestamp")
            )
            if (row.get("outcome") != persisted.get("outcome")
                    or row.get("hypothetical_points") != persisted.get("points")
                    or timestamp_mismatch):
                terminal_state_mismatches.append(
                    {"setup_id": key[0], "candidate_id": key[1],
                     "reason": "journal terminal differs from persisted state"}
                )
                break
    if terminal_state_mismatches:
        errors.append("terminal candidate journal events disagree with persisted states")

    candidate_ids = sorted(
        expected_candidate_ids
        | set(candidate_metrics)
        | set(candidate_points)
        | set(candidate_null_points)
        | {str(row.get("candidate_id")) for row in records if row.get("candidate_id")}
        | {
            str(candidate_state.get("candidate_id"))
            for candidate_state in candidate_states
            if isinstance(candidate_state, dict) and candidate_state.get("candidate_id")
        }
    )
    candidate_summary = {}
    for candidate in candidate_ids:
        counts = candidate_metrics[candidate]
        state_unresolved = sum(
            1 for candidate_state in candidate_states
            if isinstance(candidate_state, dict)
            and candidate_state.get("candidate_id") == candidate
            and candidate_state.get("status") == "UNRESOLVED"
        )
        candidate_summary[candidate] = {
            "target_exits": counts["TARGET"],
            "stop_exits": counts["STOP_LOSS"],
            "ambiguous": counts["AMBIGUOUS"],
            "session_end_exits": counts["END_OF_SESSION"],
            "unresolved": max(state_unresolved, sum(
                count for outcome, count in counts.items() if outcome.startswith("UNRESOLVED")
            )),
            "gross_hypothetical_points": candidate_points[candidate],
            "null_point_outcomes": candidate_null_points[candidate],
            "zero_point_outcomes": candidate_zero_points[candidate],
            "distinct_candidate_states": sum(
                1 for candidate_state in candidate_states
                if isinstance(candidate_state, dict)
                and candidate_state.get("candidate_id") == candidate
            ),
            "open_states": sum(
                1 for candidate_state in candidate_states
                if isinstance(candidate_state, dict)
                and candidate_state.get("candidate_id") == candidate
                and candidate_state.get("status") == "OPEN"
            ),
            "excluded_states": sum(
                1 for candidate_state in candidate_states
                if isinstance(candidate_state, dict)
                and candidate_state.get("candidate_id") == candidate
                and candidate_state.get("status") == "EXCLUDED"
            ),
        }

    absent_quotes = sum(
        1 for record in records
        if record.get("event_type", "").startswith("SHADOW_CANDIDATE")
        and (record.get("bid") is None or record.get("ask") is None)
    )
    absent_fill_costs = sum(
        1 for record in records
        if record.get("event_type", "").startswith("SHADOW_CANDIDATE")
        and (record.get("fill_assumption") is None or record.get("cost_points") is None)
    )
    actual_fill_records = sum(
        1 for record in records
        if record.get("event_type", "").startswith("SHADOW_CANDIDATE")
        and (record.get("actual_fill_price") is not None
             or record.get("actual_fill") is not None)
    )
    transaction_cost_records = sum(
        1 for record in records
        if record.get("event_type", "").startswith("SHADOW_CANDIDATE")
        and record.get("cost_points") is not None
        and record.get("cost_provenance") is not None
    )
    health_missing_known = isinstance(health, dict) and "missing_contracts" in health
    health_missing = health.get("missing_contracts") if health_missing_known else None
    if health_missing_known and not isinstance(health_missing, list):
        errors.append("observer health missing_contracts must be a list")
        health_missing = None
    result = {
        "session": root.name,
        "health_snapshot_location": health_location,
        "record_count": len(records),
        "canonical_ekalayava_signal_count": len(signal_ids),
        "canonical_signal_counts": {
            strategy: sum(1 for key in signal_key_set if key[0] == strategy)
            for strategy in ("LEVEL_TO_LEVEL", "EKALAYAVA")
        },
        "canonical_signals_missing_state": unmatched_signals,
        "states_missing_canonical_signal": orphan_states,
        "canonical_signal_state_mismatches": state_observation_mismatches,
        "canonical_signals_missing_shadow_state": missing_shadow,
        "duplicate_canonical_signal_ids": duplicate_signal_ids,
        "shadow_states_missing_canonical_signal": shadow_without_signal,
        "candle_streams": candle_findings,
        "missing_contracts": health_missing,
        "missing_contracts_known": health_missing_known,
        "candidate_outcomes": {
            candidate: candidate_summary[candidate] for candidate in candidate_ids
        },
        "candidate_terminal_conflicts": conflicts,
        "missing_quote_records": absent_quotes,
        "missing_fill_or_cost_records": absent_fill_costs,
        "actual_fill_records": actual_fill_records,
        "actual_fill_status": "RECORDED" if actual_fill_records else "NOT_RECORDED",
        "transaction_cost_records": transaction_cost_records,
        "transaction_cost_status": (
            "RECORDED" if transaction_cost_records else "NOT_RECORDED"
        ),
        "integrity_errors": errors,
        "data_quality_warnings": warnings,
        "integrity_ok": not errors,
    }
    return result


def human_summary(result):
    lines = [
        f"Session: {result['session']}",
        f"Records: {result['record_count']}; Ekalayava signals: {result['canonical_ekalayava_signal_count']}",
        f"Candle streams: {len(result['candle_streams'])}; missing contracts: {len(result['missing_contracts'])}",
        f"Candidates reconciled: {len(result['candidate_outcomes'])}",
        f"Missing quote records: {result['missing_quote_records']}; missing fill/cost records: {result['missing_fill_or_cost_records']}",
        f"Actual fills: {result['actual_fill_status']}; transaction costs: {result['transaction_cost_status']}",
        f"Integrity: {'PASS' if result['integrity_ok'] else 'FAIL'}",
    ]
    lines.extend(f"ERROR: {error}" for error in result["integrity_errors"])
    lines.extend(f"WARNING: {warning}" for warning in result["data_quality_warnings"])
    return "\n".join(lines)
