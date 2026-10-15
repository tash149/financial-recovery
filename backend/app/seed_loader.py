"""Load the synthetic demo data in backend/seed/ and (re)build the database from it.

Only reference data goes into the DB at reset time (institutions). The other seed files are mock
external sources (SMS export, mailbox, AIS, DigiLocker, registries) that later steps read from disk
when the heir "connects" them; reset just checks they are all present and parse.
"""

import json
from pathlib import Path
from typing import Any

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel

from app import models  # noqa: F401  (registers tables on SQLModel.metadata)
from app.models import Institution

SEED_DIR = Path(__file__).resolve().parent.parent / "seed"

SEED_JSON_FILES = [
    "institutions.json",
    "digilocker_mock.json",
    "sms_parent.json",
    "inbox_parent.json",
    "ais_parent.json",
    "registries_mock.json",
    "impostor_claim.json",
    "lic_policy_record.json",
    "expected_assets.json",
]
SEED_IMAGE_FILES = ["death_certificate.png", "impostor_death_certificate.png", "share_certificate.png"]


def load_json(name: str) -> Any:
    return json.loads((SEED_DIR / name).read_text(encoding="utf-8"))


def seed_path(name: str) -> Path:
    return SEED_DIR / name


def check_seed_files() -> None:
    for name in SEED_JSON_FILES:
        load_json(name)
    missing = [n for n in SEED_IMAGE_FILES if not (SEED_DIR / n).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing seed images {missing}; run `python -m seed.generate_images` in backend/")


def reset_database(engine: Engine) -> dict:
    """Drop every table, recreate the schema and load reference data. Returns a short summary."""
    check_seed_files()
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    institutions = load_json("institutions.json")["institutions"]
    model_fields = set(Institution.model_fields)
    with Session(engine) as session:
        for row in institutions:
            session.add(Institution(**{k: v for k, v in row.items() if k in model_fields}))
        session.commit()

    return {"institutions": len(institutions), "seed_files": SEED_JSON_FILES + SEED_IMAGE_FILES}
