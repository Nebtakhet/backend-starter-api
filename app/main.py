# FastAPI application setup, middleware, and global error handling.

from collections.abc import Sequence
from contextlib import asynccontextmanager
import logging
from time import perf_counter
from uuid import uuid4

from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import configure_logging, reset_request_id, set_request_id
from app.core.metrics import IN_PROGRESS, metrics_payload, record_request
from app.core.rate_limit import limiter
from app.db.base import Base
from app.db.session import engine

configure_logging()
logger = logging.getLogger("app.request")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist on startup for local/dev usage.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Backend Starter API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
app.add_middleware(SlowAPIMiddleware)

# CORS middleware - configure allowed origins in settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid4().hex
    token = set_request_id(request_id)
    start = perf_counter()
    IN_PROGRESS.inc()
    route_path = request.url.path
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception:
        duration_ms = (perf_counter() - start) * 1000
        record_request(
            method=request.method,
            path=route_path,
            status_code=status_code,
            duration_seconds=duration_ms / 1000,
        )
        logger.exception(
            "request.failed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "duration_ms": round(duration_ms, 2),
            },
        )
        reset_request_id(token)
        IN_PROGRESS.dec()
        raise

    duration_ms = (perf_counter() - start) * 1000
    route = request.scope.get("route")
    if route is not None and hasattr(route, "path"):
        route_path = route.path
    record_request(
        method=request.method,
        path=route_path,
        status_code=status_code,
        duration_seconds=duration_ms / 1000,
    )
    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request.completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        },
    )
    reset_request_id(token)
    IN_PROGRESS.dec()
    return response


def error_payload(detail: str, code: str, errors: Sequence[object] | None = None) -> dict:
    payload: dict[str, object] = {"detail": detail, "code": code}
    if errors is not None:
        payload["errors"] = errors
    return payload


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = jsonable_encoder(exc.errors())
    return JSONResponse(
        status_code=422,
        content=error_payload(
            detail="Validation error",
            code="validation_error",
            errors=errors,
        ),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code = "auth_error" if exc.status_code in (401, 403) else "http_error"
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(detail=str(exc.detail), code=code),
    )


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content=error_payload(detail="Database integrity error", code="db_integrity_error"),
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content=error_payload(detail="Database error", code="db_error"),
    )


app.include_router(api_router, prefix="/api/v1")


@app.get("/metrics")
async def metrics() -> Response:
    payload, content_type = metrics_payload()
    return Response(content=payload, media_type=content_type)


@app.get("/health")
async def health_check() -> dict:
    # Health check endpoint with database connectivity verification.
    from app.db.session import SessionLocal

    health_status = {"status": "ok", "database": "unknown"}

    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1"))
            health_status["database"] = "connected"
    except Exception:
        health_status["status"] = "degraded"
        health_status["database"] = "disconnected"

    return health_status
