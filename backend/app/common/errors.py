"""Application-wide error handling."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

HTTP_422_UNPROCESSABLE_ENTITY = 422


async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Report which field failed and why, never the value that was submitted.

    FastAPI's default body includes `input`, which would echo a rejected
    password back to the caller and into any log capturing response bodies.
    """
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": [
                {"type": error["type"], "loc": error["loc"], "msg": error["msg"]}
                for error in exc.errors()
            ]
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    """Attach the application's exception handlers."""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
