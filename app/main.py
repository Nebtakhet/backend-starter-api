"""FastAPI application setup, middleware, and global error handling."""

from collections.abc import Sequence
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.rate_limit import limiter
from app.db.base import Base
from app.db.session import engine

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist on startup for local/dev usage.
    Base.metadata.create_all(bind=engine)
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


def error_payload(detail: str, code: str, errors: Sequence[object] | None = None) -> dict:
    payload: dict[str, object] = {"detail": detail, "code": code}
    if errors is not None:
        payload["errors"] = errors
    return payload


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=error_payload(
            detail="Validation error",
            code="validation_error",
            errors=exc.errors(),
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


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint with database connectivity verification."""
    from app.db.session import SessionLocal
    
    health_status = {
        "status": "ok",
        "database": "unknown"
    }
    
    # Test database connectivity
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            health_status["database"] = "connected"
        finally:
            db.close()
    except Exception:
        health_status["status"] = "degraded"
        health_status["database"] = "disconnected"
    
    return health_status
