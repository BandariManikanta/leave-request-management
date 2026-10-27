from datetime import date
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, StringConstraints

Reason = Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=250)]
Comment = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class LeaveType(str, Enum):
    CASUAL = "Casual"
    SICK = "Sick"
    ANNUAL = "Annual"


class LeaveStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


# Stored records

class Employee(BaseModel):
    id: str
    name: str
    email: EmailStr
    leave_balance: int = Field(ge=0)


class LeaveRequest(BaseModel):
    id: str
    employee_id: str
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: str
    number_of_days: int
    status: LeaveStatus = LeaveStatus.PENDING
    reviewer_comment: str | None = None


# Responses

class EmployeeOut(Employee):
    pending_days: int
    available_balance: int


class LeaveRequestOut(LeaveRequest):
    employee_name: str
    working_days: int


class LeaveSummary(BaseModel):
    total: int
    by_status: dict[str, int]


# Request bodies

class LeaveRequestCreate(BaseModel):
    employee_id: str = Field(min_length=1)
    leave_type: LeaveType
    start_date: date
    end_date: date
    reason: Reason


class ApprovalDecision(BaseModel):
    comment: Comment | None = None


class RejectionDecision(BaseModel):
    comment: Comment
