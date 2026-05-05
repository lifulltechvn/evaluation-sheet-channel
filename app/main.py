from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.common.database import engine
from app.common.middleware import setup_middleware
from app.config import settings
from app.models import *  # noqa: F401, F403 — đảm bảo tất cả models được import
from app.routers import dashboard_router, employee_router, notification_router, sheet_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    lifespan=lifespan,
)

setup_middleware(app)

app.include_router(sheet_router.router)
app.include_router(employee_router.router)
app.include_router(notification_router.router)
app.include_router(dashboard_router.router)


@app.get("/")
def root():
    return {
        "message": "Evaluation Sheet API",
        "docs": "/docs",
        "health": "/v1/health",
    }


@app.get("/v1/health")
def health():
    return {"status": "ok"}
