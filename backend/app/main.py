from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlmodel import Session

from app.db import get_session, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="{{reclaim}} API", lifespan=lifespan)


@app.get("/health")
def health(session: Session = Depends(get_session)) -> dict:
    session.exec(text("SELECT 1"))
    return {"status": "ok", "db": "ok"}
