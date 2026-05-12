import logging

logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, dashboard, sheets, employees, notifications, periods

app = FastAPI(title="Evaluation Sheet API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# --- Health Check ---

@app.get("/v1/health")
def health():
    return {"status": "ok"}


# --- Register BFF Routers ---

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(sheets.router)
app.include_router(employees.router)
app.include_router(notifications.router)
app.include_router(periods.router)
