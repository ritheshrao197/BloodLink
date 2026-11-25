from factory import login, make_request, make_user, pledge
from models import Donation, User


def _pledge(client, db):
    donor = make_user(db)
    req = make_request(db)
    pledge(client, login(db, donor), req.id, donor.id)
    return db.query(Donation).one()


def test_unverified_staff_cannot_see_or_act(client, db):
    d = _pledge(client, db)
    fake = make_user(db, name="JSS Hospital", role="hospital", is_verified=False)
    h = login(db, fake)
    res = client.get("/api/staff/pledges", headers=h)
    assert res.status_code == 403 and "verif" in res.json()["detail"].lower()
    for path, body in (("confirm", {}), ("no-show", {}), ("low-hb", {})):
        assert client.post(f"/api/staff/pledges/{d.id}/{path}", headers=h, json=body).status_code == 403, path
    db.expire_all()
    assert db.get(Donation, d.id).status == "pledged"


def test_unverified_staff_blocked_through_the_bot_too(client, db, monkeypatch):
    import auth

    monkeypatch.setattr(auth, "BOT_SECRET", "s")
    d = _pledge(client, db)
    make_user(db, name="Mysuru Blood Bank", role="blood_bank", is_verified=False, telegram_id="900")
    res = client.post(f"/api/staff/pledges/{d.id}/confirm", headers={"X-Bot-Secret": "s"}, json={"staff_telegram_id": "900"})
    assert res.status_code == 403


def test_verified_staff_and_admins_can_act(client, db):
    d = _pledge(client, db)
    admin = make_user(db, name="Admin", is_admin=True)  # admins never need a separate verification
    assert client.get("/api/staff/pledges", headers=login(db, admin)).status_code == 200
    bank = make_user(db, name="Mysuru Blood Bank", role="blood_bank")  # verified by default in tests
    assert client.post(f"/api/staff/pledges/{d.id}/confirm", headers=login(db, bank), json={}).status_code == 200


def test_new_staff_registration_is_unverified_and_admins_are_pinged(client, db, monkeypatch):
    import notifier

    sent = []
    monkeypatch.setattr(notifier, "notify", lambda chat, text: sent.append((chat, text)))
    make_user(db, name="Admin", is_admin=True, telegram_id="1")
    res = client.post("/api/register", json={"name": "City Hospital", "blood_group": "O+", "city": "Mysuru", "role": "hospital"})
    assert res.status_code == 200
    u = db.get(User, res.json()["user_id"])
    assert u.is_verified is False
    assert [c for c, _ in sent] == ["1"] and "City Hospital" in sent[0][1]


def test_new_donor_registration_does_not_ping_admins(client, db, monkeypatch):
    import notifier

    sent = []
    monkeypatch.setattr(notifier, "notify", lambda chat, text: sent.append((chat, text)))
    make_user(db, name="Admin", is_admin=True, telegram_id="1")
    client.post("/api/register", json={"name": "K", "blood_group": "O+", "city": "Mysuru", "sex": "female",
                                       "date_of_birth": "1996-01-01", "weight_kg": 55, "conditions": []})
    assert sent == []
