# Leave Request Management

A full-stack app where employees submit leave requests and a reviewer approves, rejects, or cancels them.

- **Backend:** Python, FastAPI, JSON files for storage (no database, no authentication)
- **Frontend:** React with Vite

## Project layout

```
use case/
├── backend/
│   ├── app/
│   │   ├── main.py            # App factory, error handling, routes wiring
│   │   ├── routers/           # employees.py, leave_requests.py
│   │   ├── services.py        # Business rules (overlap, balance, status transitions)
│   │   ├── schemas.py         # Pydantic models for storage, requests and responses
│   │   ├── storage.py         # Reads and writes JSON files
│   │   ├── dates.py           # Calendar and working-day calculations
│   │   ├── dependencies.py
│   │   └── errors.py
│   ├── seed/                  # Seed data (copied to data/ on first run)
│   │   ├── employees.json
│   │   └── leave_requests.json
│   ├── tests/                 # pytest suite
│   ├── pytest.ini
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── api.js             # fetch wrapper for the API
    │   ├── components/        # Form, filters, table, balances, summary, review dialog
    │   └── styles.css
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## Prerequisites

- Python 3.11 or newer
- Node.js 20.19 or newer (or 22.12 or newer) and npm

## Setup and run

Run the backend and frontend in two terminals.

### 1. Backend (http://127.0.0.1:8000)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Interactive API docs are at http://127.0.0.1:8000/docs.

### 2. Frontend (http://localhost:5173)

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` requests to the backend, so both servers must be running.

### Running the tests

```bash
cd backend
python -m pytest
```

## Data storage

- On first start, the app copies `backend/seed/*.json` into `backend/data/`.
- All reads and writes go to `backend/data/employees.json` and `backend/data/leave_requests.json`.
- Writes go to a temp file that then replaces the original, so a crash cannot leave a half-written file.
- To reset to the seed data, stop the backend and delete `backend/data/`.
- To use a different data directory, set the `LEAVE_DATA_DIR` environment variable. The tests use a temp directory this way.

## API

| Method | Path | Purpose | Success |
|---|---|---|---|
| GET | `/api/employees` | List employees with balance, pending days, and available balance | 200 |
| GET | `/api/employees/{id}` | One employee | 200 / 404 |
| GET | `/api/leave-requests` | List requests. Query: `status`, `employee_id`, `employee_name`, `from_date`, `to_date` | 200 |
| GET | `/api/leave-requests/summary` | Total and counts by status | 200 |
| GET | `/api/leave-requests/{id}` | One request | 200 / 404 |
| POST | `/api/leave-requests` | Submit a request (body: `employee_id`, `leave_type`, `start_date`, `end_date`, `reason`) | 201 |
| POST | `/api/leave-requests/{id}/approve` | Approve a pending request. Optional body: `{ "comment": "..." }` | 200 |
| POST | `/api/leave-requests/{id}/reject` | Reject a pending request. Body: `{ "comment": "..." }` (required) | 200 |
| DELETE | `/api/leave-requests/{id}` | Cancel a pending request | 204 |

Error responses use the shape `{ "detail": "message" }`. Request validation errors use FastAPI's standard 422 list.

| Status | Meaning |
|---|---|
| 404 | Employee or request not found |
| 409 | Overlaps a Pending or Approved request, or the request is not in the right state for the action |
| 422 | Breaks a business rule (past start date, end before start, insufficient balance) or fails validation (reason length, missing reviewer comment) |

## Business rules

- **Days:** `number_of_days` is calculated by the backend as the inclusive count of calendar days. `working_days` (Monday to Friday, public holidays not considered) is returned alongside it for display.
- **Dates:** the start date cannot be in the past, and the end date cannot be earlier than the start date.
- **Balance:** a new request must fit within the employee's *available* balance, which is `leave_balance` minus the days of their Pending requests. A pending request therefore reserves its days until it is approved, rejected, or cancelled.
- **Approval:** approving deducts the request's days from `leave_balance`. The balance is checked again at this point.
- **Overlap:** an employee cannot have a Pending or Approved request whose dates overlap another Pending or Approved request.
- **Status transitions:** only Pending requests can be approved, rejected, or cancelled.
- **Reviewer comment:** required when rejecting, optional when approving.
- **Reason:** 10 to 250 characters after trimming whitespace.
- **Employee must exist** when a request is created.

## Design choices

- **Cancelled requests are deleted.** The spec defines only three statuses (Pending, Approved, Rejected), so cancelling removes the record instead of adding a fourth status.
- **Leave type shares one balance pool.** Casual, Sick, and Annual requests all draw from `leave_balance`. The spec describes a single balance per employee.
- **Calendar days are deducted.** If the policy should deduct working days instead, change `calendar_days` to `working_days` in `services.py` where `number_of_days` is set.
- **Summary and filters are optional extras.** Date-range filtering, name search, and working-day display are implemented as the optional enhancements.

## Seed data

- 6 employees. `EMP006` has a balance of 1 day, so the balance rule is easy to see.
- 9 leave requests: 4 Approved, 3 Pending, 2 Rejected.
- Seeded balances already reflect the approved requests.

## Limitations

- JSON files are not safe for multiple server processes. A single uvicorn process is fine for this use case.
- Approving updates the employee file and then the request file. These are two separate writes, so a crash between them could leave the two out of step. A database would remove this risk.
- Public holidays are not excluded from working-day counts.
- There is no authentication, so anyone who can reach the API can act as the reviewer.
