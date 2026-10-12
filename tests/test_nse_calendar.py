from datetime import date, datetime

from app.nse_calendar import DEFAULT_NSE_CALENDAR


def test_nse_2026_holidays_and_published_special_session():
    assert DEFAULT_NSE_CALENDAR.session_for(date(2026, 10, 2)) is None
    session = DEFAULT_NSE_CALENDAR.session_for(date(2026, 2, 1))
    assert session is not None
    assert session.opens_at.isoformat() == "09:15:00"
    assert session.closes_at.isoformat() == "15:30:00"


def test_calendar_fails_closed_for_unknown_year_and_unscheduled_muhurat():
    assert DEFAULT_NSE_CALENDAR.session_for(date(2027, 1, 4)) is None
    assert DEFAULT_NSE_CALENDAR.session_for(date(2026, 11, 8)) is None
    assert not DEFAULT_NSE_CALENDAR.market_open(datetime.fromisoformat("2026-11-08T10:00:00+05:30"))
