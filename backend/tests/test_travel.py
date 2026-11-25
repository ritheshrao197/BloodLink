from factory import login, make_request, make_user, pledge
from models import Donation


def _capture(monkeypatch):
    import notifier

    sent = []
    monkeypatch.setattr(notifier, "notify", lambda chat, text: sent.append((chat, text)))
    monkeypatch.setattr(notifier, "notify_buttons", lambda chat, text, buttons: sent.append((chat, text)))
    return sent


def _pledged(client, db, **donor_kw):
    donor = make_user(db, phone="+91 98450 12345", **donor_kw)
    req = make_request(db, requester_telegram_id="500", requester_language="en")
    h = login(db, donor)
    assert pledge(client, h, req.id, donor.id).status_code == 200
    return donor, req, db.query(Donation).filter(Donation.donor_id == donor.id).one(), h


def test_ride_help_alerts_requester_and_staff_once(client, db, monkeypatch):
    make_user(db, name="Mysuru Blood Bank", role="blood_bank", telegram_id="900")
    sent = _capture(monkeypatch)
    donor, req, d, h = _pledged(client, db)
    sent.clear()
    res = client.post(f"/api/pledges/{d.id}/ride-help", headers=h, json={})
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "requested" and res.json()["notified"] == 2
    chats = sorted(c for c, _ in sent)
    assert chats == ["500", "900"]
    text = dict(sent)["900"]
    assert donor.name in text and "+91 98450 12345" in text and f"#{req.id}" in text
    db.expire_all()
    assert db.get(Donation, d.id).ride_help_at is not None
    # a second tap does not alert anyone again
    sent.clear()
    again = client.post(f"/api/pledges/{d.id}/ride-help", headers=h, json={})
    assert again.status_code == 200 and again.json()["status"] == "already_requested" and sent == []


def test_staff_queue_flags_donors_who_need_a_ride(client, db):
    bank = make_user(db, name="Mysuru Blood Bank", role="blood_bank")
    _, _, d, h = _pledged(client, db)
    client.post(f"/api/pledges/{d.id}/ride-help", headers=h, json={})
    queue = client.get("/api/staff/pledges", headers=login(db, bank)).json()
    assert queue[0]["ride_help"] is True


def test_only_the_donor_can_ask_and_only_while_open(client, db):
    _, _, d, h = _pledged(client, db)
    other = make_user(db, name="Someone else")
    assert client.post(f"/api/pledges/{d.id}/ride-help", headers=login(db, other), json={}).status_code == 403
    assert client.post(f"/api/pledges/{d.id}/ride-help", json={}).status_code == 401
    d = db.get(Donation, d.id)
    d.status = "confirmed"
    db.commit()
    assert client.post(f"/api/pledges/{d.id}/ride-help", headers=h, json={}).status_code == 409
    assert client.post("/api/pledges/9999/ride-help", headers=h, json={}).status_code == 404


def test_bot_asks_for_the_donor_by_telegram_id(client, db, monkeypatch):
    import auth

    monkeypatch.setattr(auth, "BOT_SECRET", "s")
    _, _, d, _ = _pledged(client, db, telegram_id="321")
    bot = {"X-Bot-Secret": "s"}
    assert client.post(f"/api/pledges/{d.id}/ride-help", headers=bot, json={"donor_telegram_id": "999"}).status_code == 403
    assert client.post(f"/api/pledges/{d.id}/ride-help", headers=bot, json={"donor_telegram_id": "321"}).status_code == 200
