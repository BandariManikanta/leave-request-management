from typing import Annotated

from fastapi import Depends, Request

from .services import LeaveService


def get_service(request: Request) -> LeaveService:
    return request.app.state.service


ServiceDep = Annotated[LeaveService, Depends(get_service)]
