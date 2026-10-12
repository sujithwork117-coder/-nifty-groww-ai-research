"""Offline, fixed-grid L2L target-policy simulation for research reports.

This module does not change the canonical strategy or production paper engine.
It evaluates a target threshold against completed OHLC bars after a saved entry.
"""

from datetime import datetime, timedelta


BAR = timedelta(minutes=5)


def target_for_fraction(entry, opening_high, fraction):
    """Return a strictly-above-entry target at the fixed fraction of baseline distance."""
    entry = float(entry)
    opening_high = float(opening_high)
    fraction = float(fraction)
    if not 0 < fraction <= 1:
        raise ValueError("Target fraction must be in (0, 1]")
    if opening_high <= entry:
        return None
    target = entry + fraction * (opening_high - entry)
    if target <= entry:
        raise ValueError("Candidate target must be strictly above entry")
    return target


def _timestamp(value):
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def simulate_exit_policy(candles, *, entry_timestamp, entry, stop, opening_high,
                         target_fraction, session_last_timestamp=None):
    """Simulate one policy using only bars strictly after the completed entry bar.

    `candles` must contain the entry candle and same-session bars in chronological
    order. A missing interval before a touch makes the path unresolved. A candle
    touching both stop and target is ambiguous. No forced end-of-day fill is made.
    """
    entry_timestamp = _timestamp(entry_timestamp)
    entry = float(entry)
    stop = float(stop)
    target = target_for_fraction(entry, opening_high, target_fraction)
    if entry <= stop:
        return {"status": "SKIPPED_STOP_ALREADY_BREACHED", "target": target,
                "exit_timestamp": None, "exit_price": None, "points": None,
                "holding_minutes": None, "reason": "entry_at_or_below_stop"}
    if target is None:
        return {"status": "SKIPPED_TARGET_ALREADY_REACHED", "target": None,
                "exit_timestamp": None, "exit_price": None, "points": None,
                "holding_minutes": None, "reason": "entry_at_or_above_opening_high"}

    ordered = sorted(candles, key=lambda candle: _timestamp(candle["timestamp"]))
    entry_index = next((i for i, candle in enumerate(ordered)
                        if _timestamp(candle["timestamp"]) == entry_timestamp), None)
    if entry_index is None:
        return {"status": "UNRESOLVED_ENTRY_BAR_MISSING", "target": target,
                "exit_timestamp": None, "exit_price": None, "points": None,
                "holding_minutes": None, "reason": "entry_bar_not_in_source"}

    previous = entry_timestamp
    for candle in ordered[entry_index + 1:]:
        stamp = _timestamp(candle["timestamp"])
        if stamp - previous != BAR:
            return {"status": "UNRESOLVED_DATA_GAP", "target": target,
                    "exit_timestamp": None, "exit_price": None, "points": None,
                    "holding_minutes": None, "reason": "missing_completed_candle_interval"}
        previous = stamp
        low, high = float(candle["low"]), float(candle["high"])
        hit_stop, hit_target = low <= stop, high >= target
        if hit_stop and hit_target:
            status, exit_price = "AMBIGUOUS", None
        elif hit_stop:
            status, exit_price = "SL", stop
        elif hit_target:
            status, exit_price = "TARGET", target
        else:
            continue
        return {"status": status, "target": target,
                "exit_timestamp": stamp.isoformat(), "exit_price": exit_price,
                "points": None if exit_price is None else exit_price - entry,
                "holding_minutes": (stamp - entry_timestamp).total_seconds() / 60,
                "reason": "same_bar_stop_and_target" if status == "AMBIGUOUS" else status.lower()}

    if session_last_timestamp is not None and previous < _timestamp(session_last_timestamp):
        status, reason = "UNRESOLVED_DATA_GAP", "session_tail_missing"
    else:
        status, reason = "UNRESOLVED_END_OF_DATA", "no_terminal_touch_before_last_available_bar"
    return {"status": status, "target": target, "exit_timestamp": None,
            "exit_price": None, "points": None, "holding_minutes": None,
            "reason": reason}
