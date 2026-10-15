from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlmodel import Session

from app.db import engine, get_session
from app.seed_loader import reset_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # v0: every start begins from the same synthetic demo state.
    reset_database(engine)
    yield


app = FastAPI(title="{{reclaim}} API", lifespan=lifespan)


@app.get("/health")
def health(session: Session = Depends(get_session)) -> dict:
    session.exec(text("SELECT 1"))
    return {"status": "ok", "db": "ok"}


@app.post("/admin/reset")
def admin_reset() -> dict:
    """Wipe every table and reload the synthetic demo data."""
    return {"status": "ok", **reset_database(engine)}
