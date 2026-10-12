"""Fail-closed NSE equity/F&O session calendar for supported 2026 sessions.

The source calendar is maintained explicitly because holiday and special-session
dates can change. Unknown years and sessions with unpublished timings are closed
by default until this table is reviewed and updated.

Sources:
- https://www.nseindia.com/resources/exchange-communication-holidays
- https://nsearchives.nseindia.com/content/circulars/FAOP72352.pdf
"""

from dataclasses import dataclass
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


@dataclass(frozen=True)
class MarketSession:
    trading_date: date
    opens_at: time
    closes_at: time
    source_note: str = "NSE normal market session"


# NSE's 2026 equity holiday page includes the Jan 15 Maharashtra civic-election
# closure. Keep it in addition to the Dec 2025 annual holiday circular.
NSE_2026_HOLIDAYS = frozenset(date.fromisoformat(value) for value in (
    "2026-01-15", "2026-01-26", "2026-03-03", "2026-03-26", "2026-03-31",
    "2026-04-03", "2026-04-14", "2026-05-01", "2026-05-28", "2026-06-26",
    "2026-09-14", "2026-10-02", "2026-10-20", "2026-11-10", "2026-11-24",
    "2026-12-25",
))

# The Feb 1 Budget session is a published normal-timing session despite falling
# on Sunday. Muhurat trading on Nov 8 has no published timings in this snapshot,
# so it is deliberately not treated as a normal session.
NSE_2026_SPECIAL_SESSIONS = {
    date(2026, 2, 1): MarketSession(
        date(2026, 2, 1), time(9, 15), time(15, 30),
        "NSE F&O circular FAOP72352: Union Budget live session, standard timings",
    ),
}
NSE_2026_UNSCHEDULED_SPECIAL_DATES = frozenset({date(2026, 11, 8)})


class NSECalendar:
    """Resolve supported market sessions; unknown dates fail closed."""

    def session_for(self, trading_date: date) -> MarketSession | None:
        if trading_date in NSE_2026_SPECIAL_SESSIONS:
            return NSE_2026_SPECIAL_SESSIONS[trading_date]
        if trading_date.year != 2026:
            return None
        if trading_date in NSE_2026_UNSCHEDULED_SPECIAL_DATES:
            return None
        if trading_date.weekday() >= 5 or trading_date in NSE_2026_HOLIDAYS:
            return None
        return MarketSession(trading_date, time(9, 15), time(15, 30))

    def market_open(self, now: datetime | None = None) -> bool:
        current = now or datetime.now(IST)
        current = current.replace(tzinfo=IST) if current.tzinfo is None else current.astimezone(IST)
        session = self.session_for(current.date())
        if session is None:
            return False
        local_time = current.time().replace(tzinfo=None)
        return session.opens_at <= local_time < session.closes_at


DEFAULT_NSE_CALENDAR = NSECalendar()
