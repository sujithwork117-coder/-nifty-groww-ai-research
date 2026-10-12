"""Bounded, offline experimental exits for saved causal Ekalayava entries.

None of these research policies changes the canonical strategy definition or
paper engine. Inputs are completed 5-minute OHLC bars and fixed entry-time
levels. Missing intervals fail closed; no order APIs are involved.
"""

from datetime import datetime, timedelta


BAR = timedelta(minutes=5)


def _stamp(value):
    return value if isinstance(value, datetime) else datetime.fromisoformat(
        str(value).replace("Z", "+00:00"))


def simulate_ekalayava_exit(candles, *, entry_timestamp, entry, initial_stop,
                            target, expected_last_timestamp, trailing=False,
                            trail_buffer=2.0):
    """Simulate one stop/target/EOD policy after a completed entry candle.

    Stops/targets activate after entry close. If both are inside one OHLC bar,
    the result is ambiguous unless the bar open itself gaps through a level,
    establishing that level was reached first. A gap through a stop fills at
    the bar open; otherwise a stop fills at its level. Targets fill at target.
    Trailing mode only tightens after a completed bar whose low is below the
    previous two completed lows; the new stop becomes active on the next bar.
    """
    entry_timestamp = _stamp(entry_timestamp)
    expected_last_timestamp = _stamp(expected_last_timestamp)
    entry, stop, target = float(entry), float(initial_stop), float(target)
    ordered = sorted(candles, key=lambda bar: _stamp(bar["timestamp"]))
    entry_indexes = [i for i, bar in enumerate(ordered)
                     if _stamp(bar["timestamp"]) == entry_timestamp]
    if not entry_indexes:
        return {"outcome": "UNRESOLVED_ENTRY_BAR_MISSING", "reason": "entry_bar_missing"}
    if stop >= entry:
        return {"outcome": "EXCLUDED_INVALID_STOP", "reason": "stop_not_below_entry"}
    if target <= entry:
        return {"outcome": "EXCLUDED_INVALID_TARGET", "reason": "target_not_above_entry"}

    entry_i = entry_indexes[0]
    future = ordered[entry_i + 1:]
    previous = entry_timestamp
    active_stop = stop
    terminal_bar = None
    outcome = None
    exit_price = None
    reason = None
    stop_updates = []

    for index, bar in enumerate(future):
        stamp = _stamp(bar["timestamp"])
        if stamp - previous != BAR:
            outcome, reason = "UNRESOLVED_DATA_GAP", "missing_completed_5m_interval"
            break
        previous = stamp
        open_price, high, low = (float(bar[k]) for k in ("open", "high", "low"))

        if open_price <= active_stop:
            outcome, exit_price, reason = "STOP_LOSS", open_price, "gap_through_stop_filled_at_open"
        elif open_price >= target:
            outcome, exit_price, reason = "TARGET", target, "target_gap_filled_at_target"
        else:
            hit_stop, hit_target = low <= active_stop, high >= target
            if hit_stop and hit_target:
                outcome, reason = "AMBIGUOUS", "stop_and_target_same_bar_order_unknown"
            elif hit_stop:
                outcome, exit_price, reason = "STOP_LOSS", active_stop, "stop_touched"
            elif hit_target:
                outcome, exit_price, reason = "TARGET", target, "target_touched"

        if outcome is not None:
            terminal_bar = bar
            break

        if trailing and index >= 2:
            prior_two = future[index - 2:index]
            if low < min(float(x["low"]) for x in prior_two):
                proposed = low - float(trail_buffer)
                tightened = max(active_stop, proposed)
                if tightened > active_stop:
                    active_stop = tightened
                    stop_updates.append({"timestamp": stamp.isoformat(), "new_stop": active_stop,
                                         "anchor_low": low,
                                         "rule": "completed_low_below_previous_two_lows_minus_buffer"})

    if outcome is None:
        if not future or _stamp(future[-1]["timestamp"]) != expected_last_timestamp:
            return {"outcome": "UNRESOLVED_SESSION_TAIL_MISSING",
                    "reason": "final_expected_15_25_candle_unavailable",
                    "stop_updates": stop_updates}
        terminal_bar = future[-1]
        outcome, exit_price, reason = "END_OF_SESSION", float(terminal_bar["close"]), "last_valid_session_candle_close"

    terminal_stamp = _stamp(terminal_bar["timestamp"]) if terminal_bar else None
    observed = [bar for bar in future if terminal_stamp is None
                or _stamp(bar["timestamp"]) <= terminal_stamp]
    mfe = max([0.0] + [float(bar["high"]) - entry for bar in observed])
    mae = min([0.0] + [float(bar["low"]) - entry for bar in observed])
    points = None if exit_price is None else exit_price - entry
    return {
        "outcome": outcome, "reason": reason,
        "exit_timestamp": None if terminal_stamp is None else terminal_stamp.isoformat(),
        "exit_price": exit_price, "points": points,
        "holding_minutes": None if terminal_stamp is None else
            (terminal_stamp - entry_timestamp).total_seconds() / 60,
        "active_stop_at_exit": active_stop,
        "stop_updates": stop_updates,
        "mfe_through_terminal_bar": mfe,
        "mae_through_terminal_bar": mae,
        "terminal_bar_excursion_order_unknown": outcome in ("STOP_LOSS", "TARGET", "AMBIGUOUS"),
    }
