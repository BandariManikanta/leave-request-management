from fastapi import APIRouter

from ..dependencies import ServiceDep
from ..schemas import EmployeeOut

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeOut])
def list_employees(service: ServiceDep):
    return service.list_employees()


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: str, service: ServiceDep):
    return service.get_employee(employee_id)
