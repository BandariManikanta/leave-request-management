from datetime import date

from app.dates import calendar_days, working_days


def test_calendar_days_is_inclusive():
    assert calendar_days(date(2026, 3, 2), date(2026, 3, 2)) == 1
    assert calendar_days(date(2026, 3, 2), date(2026, 3, 6)) == 5


def test_working_days_skips_weekends():
    # 2026-10-26 is a Monday, so Monday to Sunday has five working days.
    assert working_days(date(2026, 10, 26), date(2026, 11, 1)) == 5


def test_working_days_over_a_weekend_only():
    # Saturday and Sunday
    assert working_days(date(2026, 10, 31), date(2026, 11, 1)) == 0
