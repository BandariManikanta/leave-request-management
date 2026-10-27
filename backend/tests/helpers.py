from datetime import date, timedelta

# Far enough ahead that no seed request overlaps the windows the tests create.
FAR_FUTURE = date.today() + timedelta(days=1000)


def leave_payload(employee_id="EMP004", start=FAR_FUTURE, end=None, **overrides):
    end = end or start
    payload = {
        "employee_id": employee_id,
        "leave_type": "Annual",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "reason": "Family visit planned well in advance.",
    }
    payload.update(overrides)
    return payload
