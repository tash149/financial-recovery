import re

from sqlmodel import Session, select

from app.db import engine
from app.models import Institution
from app.seed_loader import load_json

OTP = re.compile(r"\bOTP\b", re.IGNORECASE)


def _institution_count() -> int:
    with Session(engine) as s:
        return len(s.exec(select(Institution)).all())


def test_reset_wipes_and_reseeds(client):
    with Session(engine) as s:
        s.add(Institution(id="stray", canonical_name="Stray Bank", kind="bank"))
        s.commit()
    assert _institution_count() == 8

    r = client.post("/admin/reset")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["institutions"] == 7
    assert _institution_count() == 7

    with Session(engine) as s:
        sbi = s.get(Institution, "sbi")
        assert "SBIINB" in sbi.sms_sender_ids
        assert "sbi.co.in" in sbi.email_domains
        assert s.get(Institution, "stray") is None


def test_three_otp_messages_planted():
    msgs = load_json("sms_parent.json")["messages"]
    expected = load_json("expected_assets.json")["otp_message_ids"]
    assert 20 <= len(msgs) <= 30
    assert [m["id"] for m in msgs if OTP.search(m["body"])] == expected


def test_inbox_size():
    assert 18 <= len(load_json("inbox_parent.json")["emails"]) <= 22


def test_expected_assets():
    assets = load_json("expected_assets.json")["assets"]
    assert len(assets) == 7
    assert [a["key"] for a in assets if a["confidence"] == "Suggested"] == ["narmada_shares"]
    institution_ids = {i["id"] for i in load_json("institutions.json")["institutions"]}
    assert {a["institution_id"] for a in assets} <= institution_ids


def test_evidence_ids_exist():
    ids = {m["id"] for m in load_json("sms_parent.json")["messages"]}
    ids |= {e["id"] for e in load_json("inbox_parent.json")["emails"]}
    ids |= {row["row_id"] for st in load_json("ais_parent.json")["statements"] for row in st["rows"]}
    ids |= {rec["record_id"] for reg in load_json("registries_mock.json")["registries"] for rec in reg["records"]}
    ids.add("share_certificate.png")
    for a in load_json("expected_assets.json")["assets"]:
        assert set(a["evidence"]) <= ids, a["key"]


def test_impostor_contradicts_genuine_certificate():
    records = load_json("digilocker_mock.json")["death_registry"]["records"]
    genuine = next(r for r in records if r["doc_id"] == "dl-death-rks")["fields"]
    claim = load_json("impostor_claim.json")["claim"]
    policy = load_json("lic_policy_record.json")["policy"]
    assert claim["policy_no"] == policy["policy_no"]
    assert claim["deceased_as_stated"]["name"] == genuine["name_of_deceased"]
    assert claim["deceased_as_stated"]["date_of_death"] != genuine["date_of_death"]
    assert claim["claimant"]["name"] != policy["nominee"]["name"]
