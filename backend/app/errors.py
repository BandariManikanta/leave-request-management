class AppError(Exception):
    """Base class for errors that map to an HTTP status code."""

    status_code = 500

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    """The request clashes with the current state of a record."""

    status_code = 409


class BusinessRuleError(AppError):
    """The request is well formed but breaks a leave policy rule."""

    status_code = 422
