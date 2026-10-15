import os
from collections.abc import Iterator
from pathlib import Path

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, create_engine

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

if DATABASE_URL.startswith("sqlite:///"):
    Path(DATABASE_URL.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)

# An in-memory SQLite DB exists per connection, so share one connection across threads (tests).
_pool = {"poolclass": StaticPool} if DATABASE_URL == "sqlite:///:memory:" else {}
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, **_pool)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
