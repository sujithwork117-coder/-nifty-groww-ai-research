"""Causal 5-minute candle assembly for read-only market observations."""

from collections import defaultdict
from datetime import datetime, timedelta
import math
from zoneinfo import ZoneInfo

import pandas as pd

IST = ZoneInfo("Asia/Kolkata")
BAR = timedelta(minutes=5)


def _timestamp(value):
    stamp = pd.Timestamp(value)
    if stamp.tzinfo is None:
        stamp = stamp.tz_localize(IST)
    else:
        stamp = stamp.tz_convert(IST)
    return stamp


class FiveMinuteCandleBuilder:
    """Aggregate price ticks and emit each fully closed session bar once.

    Missing buckets are reported as gaps. No empty/forward-filled candles are
    generated. A tick for a bucket already finalized is rejected.
    """

    def __init__(self):
        self._ticks = defaultdict(dict)
        self._finalized = set()
        self._last_emitted = {}
        self._last_tick_by_day = {}
        self.duplicate_ticks = 0
        self.late_ticks = 0
        self.out_of_order_ticks = 0

    def add_tick(self, timestamp, price):
        stamp = _timestamp(timestamp)
        local_time = stamp.strftime("%H:%M")
        # Do not infer exchange holidays/weekends here: special sessions exist.
        # The feed/session calendar is responsible for deciding when to poll.
        if not ("09:15" <= local_time <= "15:29"):
            return False
        value = float(price)
        if not math.isfinite(value) or value <= 0:
            raise ValueError("Tick price must be a finite positive number")
        start = stamp.floor("5min")
        if start in self._finalized:
            self.late_ticks += 1
            return False
        tick_key = stamp.value
        bucket = self._ticks[start]
        if tick_key in bucket:
            self.duplicate_ticks += 1
            return False
        previous = self._last_tick_by_day.get(stamp.date())
        if previous is not None and stamp < previous:
            self.out_of_order_ticks += 1
        self._last_tick_by_day[stamp.date()] = max(stamp, previous) if previous is not None else stamp
        bucket[tick_key] = (stamp, value)
        return True

    def add_ticks(self, ticks):
        added = 0
        for tick in ticks:
            timestamp = tick.get("timestamp", tick.get("ts"))
            price = tick.get("price", tick.get("ltp"))
            if timestamp is None or price is None:
                continue
            added += int(self.add_tick(timestamp, price))
        return added

    def finalize(self, as_of=None):
        now = _timestamp(as_of or datetime.now(IST))
        ready = sorted(start for start in self._ticks if start + BAR <= now)
        emitted = []
        for start in ready:
            day = start.date()
            items = sorted(self._ticks.pop(start).values(), key=lambda item: item[0])
            if not items:
                continue
            prices = [price for _, price in items]
            last = self._last_emitted.get(day)
            previous_start = pd.Timestamp(last) if last is not None else None
            if previous_start is None:
                first_expected = start.normalize() + timedelta(hours=9, minutes=15)
                missing = max(0, int((start - first_expected) / BAR))
            else:
                missing = max(0, int((start - previous_start) / BAR) - 1)
            row = {
                "timestamp": start,
                "close_time": start + BAR,
                "open": prices[0], "high": max(prices), "low": min(prices), "close": prices[-1],
                "tick_count": len(prices), "missing_intervals_before": missing,
                "completed": True,
            }
            emitted.append(row)
            self._finalized.add(start)
            self._last_emitted[day] = start
        return emitted

    def snapshot(self):
        return {
            "ticks": {start.isoformat(): [[stamp.isoformat(), price] for stamp, price in bucket.values()]
                      for start, bucket in self._ticks.items()},
            "finalized": sorted(stamp.isoformat() for stamp in self._finalized),
            "last_emitted": {day.isoformat(): stamp.isoformat() for day, stamp in self._last_emitted.items()},
            "duplicate_ticks": self.duplicate_ticks,
            "late_ticks": self.late_ticks,
            "out_of_order_ticks": self.out_of_order_ticks,
        }

    def restore(self, state):
        self._ticks.clear()
        self._finalized = {_timestamp(value) for value in state.get("finalized", [])}
        for start, values in state.get("ticks", {}).items():
            self._ticks[_timestamp(start)] = {_timestamp(ts).value: (_timestamp(ts), float(price))
                                               for ts, price in values}
        self._last_emitted = {datetime.fromisoformat(day).date(): _timestamp(stamp)
                              for day, stamp in state.get("last_emitted", {}).items()}
        self.duplicate_ticks = int(state.get("duplicate_ticks", 0))
        self.late_ticks = int(state.get("late_ticks", 0))
        self.out_of_order_ticks = int(state.get("out_of_order_ticks", 0))
        self._last_tick_by_day = {}
        for bucket in self._ticks.values():
            for stamp, _ in bucket.values():
                self._last_tick_by_day[stamp.date()] = max(
                    stamp, self._last_tick_by_day.get(stamp.date(), stamp))
        return self


def completed_5m_candle(ticks, as_of=None):
    """Compatibility helper returning the newest bar proven complete at as_of."""
    builder = FiveMinuteCandleBuilder()
    builder.add_ticks(ticks)
    completed = builder.finalize(as_of)
    return completed[-1] if completed else None
