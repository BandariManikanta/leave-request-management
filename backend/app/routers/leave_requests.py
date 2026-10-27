from datetime import date

from fastapi import APIRouter, Response

from ..dependencies import ServiceDep
from ..schemas import (
    ApprovalDecision,
    LeaveRequestCreate,
    LeaveRequestOut,
    LeaveStatus,
    LeaveSummary,
    RejectionDecision,
)

router = APIRouter(prefix="/api/leave-requests", tags=["leave requests"])


@router.get("", response_model=list[LeaveRequestOut])
def list_leave_requests(
    service: ServiceDep,
    status: LeaveStatus | None = None,
    employee_id: str | None = None,
    employee_name: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
):
    return service.list_requests(
        status=status,
        employee_id=employee_id,
        employee_name=employee_name,
        from_date=from_date,
        to_date=to_date,
    )


# Declared before /{request_id} so "summary" is not treated as an ID.
@router.get("/summary", response_model=LeaveSummary)
def get_summary(service: ServiceDep):
    return service.summary()


@router.get("/{request_id}", response_model=LeaveRequestOut)
def get_leave_request(request_id: str, service: ServiceDep):
    return service.get_request(request_id)


@router.post("", response_model=LeaveRequestOut, status_code=201)
def create_leave_request(payload: LeaveRequestCreate, service: ServiceDep):
    return service.create_request(payload)


@router.post("/{request_id}/approve", response_model=LeaveRequestOut)
def approve_leave_request(
    request_id: str,
    service: ServiceDep,
    decision: ApprovalDecision | None = None,
):
    return service.approve(request_id, decision)


@router.post("/{request_id}/reject", response_model=LeaveRequestOut)
def reject_leave_request(request_id: str, decision: RejectionDecision, service: ServiceDep):
    return service.reject(request_id, decision)


@router.delete("/{request_id}", status_code=204)
def cancel_leave_request(request_id: str, service: ServiceDep):
    service.cancel(request_id)
    return Response(status_code=204)
