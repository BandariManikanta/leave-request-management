import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .errors import AppError
from .routers import employees, leave_requests
from .schemas import Employee, LeaveRequest
from .services import LeaveService
from .storage import JsonFileStore, ensure_data_files

BACKEND_DIR = Path(__file__).resolve().parent.parent
SEED_DIR = BACKEND_DIR / "seed"


def create_app(data_dir: Path | None = None) -> FastAPI:
    data_dir = data_dir or Path(os.environ.get("LEAVE_DATA_DIR", BACKEND_DIR / "data"))
    ensure_data_files(data_dir, SEED_DIR)

    app = FastAPI(title="Leave Request Management API", version="1.0.0")
    app.state.service = LeaveService(
        employees=JsonFileStore(data_dir / "employees.json", Employee),
        requests=JsonFileStore(data_dir / "leave_requests.json", LeaveRequest),
    )

    app.include_router(employees.router)
    app.include_router(leave_requests.router)

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
