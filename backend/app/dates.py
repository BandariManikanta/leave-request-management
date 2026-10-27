from datetime import date, timedelta


def calendar_days(start: date, end: date) -> int:
    """Inclusive number of calendar days between two dates."""
    return (end - start).days + 1


def working_days(start: date, end: date) -> int:
    """Inclusive number of Monday-to-Friday days. Public holidays are not considered."""
    total = 0
    current = start
    while current <= end:
        if current.weekday() < 5:
            total += 1
        current += timedelta(days=1)
    return total
