import threading
from datetime import date

from .dates import calendar_days, working_days
from .errors import BusinessRuleError, ConflictError, NotFoundError
from .schemas import (
    ApprovalDecision,
    Employee,
    EmployeeOut,
    LeaveRequest,
    LeaveRequestCreate,
    LeaveRequestOut,
    LeaveStatus,
    LeaveSummary,
    RejectionDecision,
)
from .storage import JsonFileStore

ACTIVE_STATUSES = {LeaveStatus.PENDING, LeaveStatus.APPROVED}


class LeaveService:
    def __init__(
        self,
        employees: JsonFileStore[Employee],
        requests: JsonFileStore[LeaveRequest],
    ):
        self.employees = employees
        self.requests = requests
        # Mutations read and write both files, so they run one at a time.
        self._lock = threading.RLock()

    # Employees

    def list_employees(self) -> list[EmployeeOut]:
        requests = self.requests.read_all()
        return [self._employee_out(e, requests) for e in self.employees.read_all()]

    def get_employee(self, employee_id: str) -> EmployeeOut:
        employee = self._find_employee(self.employees.read_all(), employee_id)
        return self._employee_out(employee, self.requests.read_all())

    # Leave requests

    def list_requests(
        self,
        status: LeaveStatus | None = None,
        employee_id: str | None = None,
        employee_name: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[LeaveRequestOut]:
        if from_date and to_date and from_date > to_date:
            raise BusinessRuleError("from_date cannot be later than to_date.")

        employees = self.employees.read_all()
        names = {e.id: e.name for e in employees}
        search = employee_name.lower() if employee_name else None

        matches = []
        for leave in self.requests.read_all():
            if status and leave.status != status:
                continue
            if employee_id and leave.employee_id != employee_id:
                continue
            if search and search not in names.get(leave.employee_id, "").lower():
                continue
            # A request matches a date range when it overlaps the range at all.
            if from_date and leave.end_date < from_date:
                continue
            if to_date and leave.start_date > to_date:
                continue
            matches.append(leave)

        matches.sort(key=lambda leave: (leave.start_date, leave.id))
        return [self._request_out(leave, employees) for leave in matches]

    def get_request(self, request_id: str) -> LeaveRequestOut:
        leave = self._find_request(self.requests.read_all(), request_id)
        return self._request_out(leave, self.employees.read_all())

    def create_request(self, data: LeaveRequestCreate, today: date | None = None) -> LeaveRequestOut:
        today = today or date.today()
        if data.start_date < today:
            raise BusinessRuleError("Start date cannot be in the past.")
        if data.end_date < data.start_date:
            raise BusinessRuleError("End date cannot be earlier than start date.")

        with self._lock:
            employees = self.employees.read_all()
            employee = self._find_employee(employees, data.employee_id)
            requests = self.requests.read_all()

            self._ensure_no_overlap(requests, employee.id, data.start_date, data.end_date)

            days = calendar_days(data.start_date, data.end_date)
            available = employee.leave_balance - self._pending_days(requests, employee.id)
            if days > available:
                raise BusinessRuleError(
                    f"Request needs {days} day(s) but only {available} day(s) are available."
                )

            leave = LeaveRequest(
                id=self._next_request_id(requests),
                employee_id=employee.id,
                leave_type=data.leave_type,
                start_date=data.start_date,
                end_date=data.end_date,
                reason=data.reason,
                number_of_days=days,
            )
            requests.append(leave)
            self.requests.write_all(requests)

        return self._request_out(leave, employees)

    def approve(self, request_id: str, decision: ApprovalDecision | None) -> LeaveRequestOut:
        comment = decision.comment if decision else None

        with self._lock:
            employees = self.employees.read_all()
            requests = self.requests.read_all()
            leave = self._find_request(requests, request_id)
            self._ensure_pending(leave, "approved")

            employee = self._find_employee(employees, leave.employee_id)
            if leave.number_of_days > employee.leave_balance:
                raise BusinessRuleError(
                    f"Employee has {employee.leave_balance} day(s) of balance; "
                    f"this request needs {leave.number_of_days}."
                )

            employee.leave_balance -= leave.number_of_days
            leave.status = LeaveStatus.APPROVED
            leave.reviewer_comment = comment
            self.employees.write_all(employees)
            self.requests.write_all(requests)

        return self._request_out(leave, employees)

    def reject(self, request_id: str, decision: RejectionDecision) -> LeaveRequestOut:
        with self._lock:
            employees = self.employees.read_all()
            requests = self.requests.read_all()
            leave = self._find_request(requests, request_id)
            self._ensure_pending(leave, "rejected")

            leave.status = LeaveStatus.REJECTED
            leave.reviewer_comment = decision.comment
            self.requests.write_all(requests)

        return self._request_out(leave, employees)

    def cancel(self, request_id: str) -> None:
        with self._lock:
            requests = self.requests.read_all()
            leave = self._find_request(requests, request_id)
            self._ensure_pending(leave, "cancelled")

            # Cancelled requests are removed, because the spec defines no Cancelled status.
            self.requests.write_all([r for r in requests if r.id != leave.id])

    def summary(self) -> LeaveSummary:
        requests = self.requests.read_all()
        by_status = {status.value: 0 for status in LeaveStatus}
        for leave in requests:
            by_status[leave.status.value] += 1
        return LeaveSummary(total=len(requests), by_status=by_status)

    # Helpers

    @staticmethod
    def _find_employee(employees: list[Employee], employee_id: str) -> Employee:
        for employee in employees:
            if employee.id == employee_id:
                return employee
        raise NotFoundError(f"Employee {employee_id} was not found.")

    @staticmethod
    def _find_request(requests: list[LeaveRequest], request_id: str) -> LeaveRequest:
        for leave in requests:
            if leave.id == request_id:
                return leave
        raise NotFoundError(f"Leave request {request_id} was not found.")

    @staticmethod
    def _ensure_pending(leave: LeaveRequest, action: str) -> None:
        if leave.status != LeaveStatus.PENDING:
            raise ConflictError(
                f"Request {leave.id} cannot be {action} because it is {leave.status.value}. "
                "Only pending requests can be approved, rejected or cancelled."
            )

    @staticmethod
    def _ensure_no_overlap(
        requests: list[LeaveRequest], employee_id: str, start: date, end: date
    ) -> None:
        for leave in requests:
            overlaps = leave.start_date <= end and leave.end_date >= start
            if leave.employee_id == employee_id and leave.status in ACTIVE_STATUSES and overlaps:
                raise ConflictError(
                    f"Dates overlap with {leave.status.value.lower()} request {leave.id}."
                )

    @staticmethod
    def _pending_days(requests: list[LeaveRequest], employee_id: str) -> int:
        return sum(
            leave.number_of_days
            for leave in requests
            if leave.employee_id == employee_id and leave.status == LeaveStatus.PENDING
        )

    @staticmethod
    def _next_request_id(requests: list[LeaveRequest]) -> str:
        highest = max((int(leave.id.split("-")[1]) for leave in requests), default=0)
        return f"LR-{highest + 1:03d}"

    def _employee_out(self, employee: Employee, requests: list[LeaveRequest]) -> EmployeeOut:
        pending = self._pending_days(requests, employee.id)
        return EmployeeOut(
            **employee.model_dump(),
            pending_days=pending,
            available_balance=employee.leave_balance - pending,
        )

    @staticmethod
    def _request_out(leave: LeaveRequest, employees: list[Employee]) -> LeaveRequestOut:
        employee_name = next((e.name for e in employees if e.id == leave.employee_id), "")
        return LeaveRequestOut(
            **leave.model_dump(),
            employee_name=employee_name,
            working_days=working_days(leave.start_date, leave.end_date),
        )
