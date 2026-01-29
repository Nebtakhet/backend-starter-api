from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import engine

configure_logging()

app = FastAPI(title="Backend Starter API")
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
