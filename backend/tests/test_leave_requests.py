import json
from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import SEED_DIR, create_app
from app.schemas import Employee, LeaveRequest
from helpers import FAR_FUTURE, leave_payload


# Employees

def test_lists_employees_with_balances(client):
    response = client.get("/api/employees")

    assert response.status_code == 200
    employees = {e["id"]: e for e in response.json()}
    assert len(employees) >= 5
    assert employees["EMP001"]["leave_balance"] == 13
    assert employees["EMP001"]["available_balance"] == 13


def test_unknown_employee_returns_404(client):
    response = client.get("/api/employees/EMP999")

    assert response.status_code == 404


# Listing and filtering

def test_filters_by_status(client):
    response = client.get("/api/leave-requests", params={"status": "Pending"})

    assert response.status_code == 200
    body = response.json()
    assert body and all(r["status"] == "Pending" for r in body)


def test_filters_by_employee(client):
    response = client.get("/api/leave-requests", params={"employee_id": "EMP002"})

    assert response.status_code == 200
    assert all(r["employee_id"] == "EMP002" for r in response.json())


def test_filters_by_employee_name(client):
    response = client.get("/api/leave-requests", params={"employee_name": "asha"})

    assert response.status_code == 200
    assert response.json() and all(r["employee_name"] == "Asha Menon" for r in response.json())


def test_date_range_matches_overlapping_requests(client):
    # LR-001 runs 2026-03-02 to 2026-03-06, so a range covering only its last day still matches.
    response = client.get(
        "/api/leave-requests",
        params={"from_date": "2026-03-06", "to_date": "2026-03-06"},
    )

    assert [r["id"] for r in response.json()] == ["LR-001"]


def test_inverted_date_range_is_rejected(client):
    response = client.get(
        "/api/leave-requests",
        params={"from_date": "2026-06-01", "to_date": "2026-05-01"},
    )

    assert response.status_code == 422


def test_summary_counts_by_status(client):
    body = client.get("/api/leave-requests/summary").json()

    assert body["total"] == 9
    assert body["by_status"] == {"Pending": 3, "Approved": 4, "Rejected": 2}


# Creating

def test_create_calculates_days_and_starts_pending(client):
    response = client.post("/api/leave-requests", json=leave_payload(
        start=FAR_FUTURE, end=FAR_FUTURE + timedelta(days=2)
    ))

    assert response.status_code == 201
    body = response.json()
    assert body["number_of_days"] == 3
    assert body["status"] == "Pending"
    assert body["employee_name"] == "Mei Lin"


def test_create_rejects_past_start_date(client):
    response = client.post("/api/leave-requests", json=leave_payload(
        start=date.today() - timedelta(days=1)
    ))

    assert response.status_code == 422
    assert "past" in response.json()["detail"]


def test_create_rejects_end_before_start(client):
    response = client.post("/api/leave-requests", json=leave_payload(
        start=FAR_FUTURE, end=FAR_FUTURE - timedelta(days=1)
    ))

    assert response.status_code == 422


def test_create_rejects_unknown_employee(client):
    response = client.post("/api/leave-requests", json=leave_payload(employee_id="EMP999"))

    assert response.status_code == 404


def test_create_rejects_overlapping_active_request(client):
    first = client.post("/api/leave-requests", json=leave_payload(
        start=FAR_FUTURE, end=FAR_FUTURE + timedelta(days=4)
    ))
    overlapping = client.post("/api/leave-requests", json=leave_payload(
        start=FAR_FUTURE + timedelta(days=4), end=FAR_FUTURE + timedelta(days=6)
    ))

    assert first.status_code == 201
    assert overlapping.status_code == 409


def test_create_rejects_request_over_available_balance(client):
    # EMP006 has a balance of 1 day, so a 2-day request must fail.
    response = client.post("/api/leave-requests", json=leave_payload(
        employee_id="EMP006", start=FAR_FUTURE, end=FAR_FUTURE + timedelta(days=1)
    ))

    assert response.status_code == 422
    assert "available" in response.json()["detail"]


def test_pending_requests_reserve_balance(client):
    # EMP006 has 1 day. A 1-day pending request leaves nothing for a second one.
    first = client.post("/api/leave-requests", json=leave_payload(employee_id="EMP006"))
    second = client.post("/api/leave-requests", json=leave_payload(
        employee_id="EMP006", start=FAR_FUTURE + timedelta(days=10)
    ))

    assert first.status_code == 201
    assert second.status_code == 422


def test_reason_must_be_between_10_and_250_characters(client):
    too_short = client.post("/api/leave-requests", json=leave_payload(reason="too short"))
    too_long = client.post("/api/leave-requests", json=leave_payload(reason="x" * 251))

    assert too_short.status_code == 422
    assert too_long.status_code == 422


# Reviewing

def test_approve_reduces_employee_balance(client):
    created = client.post("/api/leave-requests", json=leave_payload(
        start=FAR_FUTURE, end=FAR_FUTURE + timedelta(days=2)
    )).json()

    response = client.post(f"/api/leave-requests/{created['id']}/approve", json={"comment": "OK"})

    assert response.status_code == 200
    assert response.json()["status"] == "Approved"
    assert response.json()["reviewer_comment"] == "OK"
    assert client.get("/api/employees/EMP004").json()["leave_balance"] == 17


def test_reject_requires_a_comment(client):
    created = client.post("/api/leave-requests", json=leave_payload()).json()

    response = client.post(f"/api/leave-requests/{created['id']}/reject", json={"comment": "   "})

    assert response.status_code == 422


def test_reject_sets_status_and_keeps_balance(client):
    created = client.post("/api/leave-requests", json=leave_payload()).json()

    response = client.post(
        f"/api/leave-requests/{created['id']}/reject",
        json={"comment": "Team coverage is short that week."},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Rejected"
    assert client.get("/api/employees/EMP004").json()["leave_balance"] == 20


def test_only_pending_requests_can_be_approved(client):
    response = client.post("/api/leave-requests/LR-001/approve", json={})

    assert response.status_code == 409


def test_only_pending_requests_can_be_rejected(client):
    response = client.post(
        "/api/leave-requests/LR-001/reject", json={"comment": "Too late to change."}
    )

    assert response.status_code == 409


def test_review_of_unknown_request_returns_404(client):
    response = client.post("/api/leave-requests/LR-999/approve", json={})

    assert response.status_code == 404


# Cancelling

def test_cancel_removes_pending_request(client):
    created = client.post("/api/leave-requests", json=leave_payload()).json()

    response = client.delete(f"/api/leave-requests/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/api/leave-requests/{created['id']}").status_code == 404


def test_cancel_rejects_non_pending_request(client):
    response = client.delete("/api/leave-requests/LR-001")

    assert response.status_code == 409


# Persistence and seed data

def test_changes_are_written_to_json_files(tmp_path):
    with TestClient(create_app(tmp_path)) as client:
        client.post("/api/leave-requests", json=leave_payload())

    saved = json.loads((tmp_path / "leave_requests.json").read_text(encoding="utf-8"))
    assert saved[-1]["id"] == "LR-010"
    assert saved[-1]["status"] == "Pending"


def test_seed_data_is_valid_and_covers_every_status():
    employees = [Employee.model_validate(e) for e in json.loads(
        (SEED_DIR / "employees.json").read_text(encoding="utf-8"))]
    requests = [LeaveRequest.model_validate(r) for r in json.loads(
        (SEED_DIR / "leave_requests.json").read_text(encoding="utf-8"))]

    assert len(employees) >= 5
    assert len(requests) >= 8
    assert {r.status.value for r in requests} == {"Pending", "Approved", "Rejected"}
    employee_ids = {e.id for e in employees}
    assert all(r.employee_id in employee_ids for r in requests)
    assert all(
        r.number_of_days == (r.end_date - r.start_date).days + 1 for r in requests
    )
