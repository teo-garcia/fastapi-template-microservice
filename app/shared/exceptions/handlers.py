from datetime import UTC, datetime
from typing import Any

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

logger = structlog.get_logger("exceptions")


def _request_path(request: Request) -> str:
    query = request.url.query
    return f"{request.url.path}?{query}" if query else request.url.path


def _api_error_body(
    request: Request,
    status: int,
    message: str,
    error: str,
    errors: Any = None,
) -> dict[str, Any]:
    request_id = getattr(request.state, "request_id", None)
    body = {
        "success": False,
        "statusCode": status,
        "timestamp": datetime.now(UTC).isoformat(),
        "path": _request_path(request),
        "method": request.method,
        "message": message,
        "error": error,
    }
    if request_id:
        body["meta"] = {"requestId": request_id}
    if errors is not None:
        body["errors"] = errors
    return body


async def _http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_api_error_body(request, exc.status_code, str(exc.detail), type(exc).__name__),
    )


async def _validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=_api_error_body(request, 422, "Validation failed", "ValidationError", exc.errors()),
    )


async def _integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    await logger.awarning("integrity_error", detail=str(exc.orig))
    return JSONResponse(
        status_code=409,
        content=_api_error_body(
            request,
            409,
            "A record with the given data already exists.",
            "ConflictError",
        ),
    )


async def _unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    await logger.aerror("unhandled_error", exc_info=exc, request_id=request_id)
    return JSONResponse(
        status_code=500,
        content=_api_error_body(
            request,
            500,
            "An unexpected error occurred.",
            "InternalServerError",
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, _http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(IntegrityError, _integrity_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _unhandled_error_handler)
