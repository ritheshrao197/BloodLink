"""Web push: subscriptions, delivery next to Telegram, dead-subscription cleanup, requester updates."""
import json

import pytest

from factory import login, make_request, make_user, pledge
from models import BloodRequest, Donation, PushSubscription

SUB = {"endpoint": "https://push.example/abc", "keys": {"p256dh": "BPub", "auth": "Auth"}}


@pytest.fixture
def pushed(monkeypatch):
    """Push is 'configured', sends run inline, and every delivery is recorded instead of leaving the machine."""
    import push

    sent = []

    def fake_webpush(subscription_info, data, **kw):
        sent.append((subscription_info["endpoint"], json.loads(data)))

    monkeypatch.setattr(push, "PUBLIC_KEY", "pub")
    monkeypatch.setattr(push, "PRIVATE_KEY", "priv")
    monkeypatch.setattr(push, "_vapid", lambda: object())
    monkeypatch.setattr(push, "webpush", fake_webpush)
    monkeypatch.setattr(push, "_spawn", lambda fn, *args: fn(*args))
    return sent


def _subscribe(client, headers=None, endpoint="https://push.example/abc", **extra):
    return client.post("/api/push/subscribe", headers=headers or {},
                       json={"subscription": {**SUB, "endpoint": endpoint}, **extra})


def test_key_endpoint_reports_whether_push_is_on(client, pushed):
    assert client.get("/api/push/key").json() == {"enabled": True, "public_key": "pub"}


def test_signed_in_subscribe_and_unsubscribe(client, db, pushed):
    u = make_user(db)
    h = login(db, u)
    assert _subscribe(client, h).status_code == 200
    assert _subscribe(client, h).status_code == 200  # same browser again: no duplicate
    assert db.query(PushSubscription).filter_by(user_id=u.id).count() == 1
    assert client.request("DELETE", "/api/push/subscribe", json={"endpoint": SUB["endpoint"]}).status_code == 200
    assert db.query(PushSubscription).count() == 0


def test_subscribe_needs_an_account_or_the_request_token(client, db, pushed):
    assert _subscribe(client).status_code == 401
    req = make_request(db)
    assert _subscribe(client, request_id=req.id, request_token="wrong").status_code == 403


def test_donor_gets_confirmation_by_push_and_telegram(client, db, pushed, monkeypatch):
    import notifier

    tg = []
    monkeypatch.setattr(notifier, "notify", lambda chat, text: tg.append(chat))
    donor = make_user(db, telegram_id="77")
    _subscribe(client, login(db, donor))
    req = make_request(db)
    pledge(client, login(db, donor), req.id, donor.id)
    d = db.query(Donation).one()
    bank = make_user(db, name="Mysuru Blood Bank", role="blood_bank")
    pushed.clear()
    client.post(f"/api/staff/pledges/{d.id}/confirm", headers=login(db, bank), json={"hb_g_dl": 13.4})
    assert "77" in tg
    payload = next(p for e, p in pushed if e == SUB["endpoint"])
    assert "confirmed" in payload["title"].lower() + payload["body"].lower()
    assert "<b>" not in payload["body"] and payload["url"] == "/profile"


def test_push_only_staff_get_pledge_alerts(client, db, pushed):
    bank = make_user(db, name="Mysuru Blood Bank", role="blood_bank")  # no Telegram
    _subscribe(client, login(db, bank), endpoint="https://push.example/bank")
    donor = make_user(db)
    pledge(client, login(db, donor), make_request(db).id, donor.id)
    assert [p["url"] for e, p in pushed if e == "https://push.example/bank"] == ["/staff"]


def test_sos_reaches_push_only_donors_and_counts_them(client, db, pushed):
    donor = make_user(db)  # compatible, nearby, no Telegram
    _subscribe(client, login(db, donor), endpoint="https://push.example/donor")
    res = client.post("/api/sos", json={"requester_name": "R", "blood_group": "O+", "hospital": "JSS Hospital",
                                        "city": "Mysuru", "state": "Karnataka", "units_needed": 1, "urgency": "Critical"})
    assert res.status_code == 200
    assert res.json()["reachable"] == 1 and res.json()["telegram_reachable"] == 0
    assert any(e == "https://push.example/donor" for e, _ in pushed)
    db.expire_all()
    assert db.get(BloodRequest, res.json()["request_id"]).notified_count == 1


def test_web_requester_gets_updates_for_their_request(client, db, pushed):
    res = client.post("/api/sos", json={"requester_name": "R", "blood_group": "O+", "hospital": "JSS Hospital",
                                        "city": "Mysuru", "state": "Karnataka", "units_needed": 1, "urgency": "High"})
    body = res.json()
    assert body["request_token"]
    assert _subscribe(client, endpoint="https://push.example/family", request_id=body["request_id"],
                      request_token=body["request_token"]).status_code == 200
    donor = make_user(db, phone="+91 90000 00000")
    h = login(db, donor)
    pledge(client, h, body["request_id"], donor.id)
    d = db.query(Donation).one()
    client.post(f"/api/pledges/{d.id}/ride-help", headers=h, json={})
    family = [p for e, p in pushed if e == "https://push.example/family"]
    assert len(family) == 2  # "a donor is on the way", then "needs help getting there"
    assert donor.name in family[1]["title"] and donor.phone in family[1]["body"]


def test_gone_subscriptions_are_removed(client, db, pushed, monkeypatch):
    import push

    class Gone(Exception):
        response = type("R", (), {"status_code": 410})()

    def gone(**kw):
        raise push.WebPushException("gone", response=Gone.response)

    u = make_user(db)
    _subscribe(client, login(db, u))
    monkeypatch.setattr(push, "webpush", gone)
    push.to_user(u.id, "<b>Hi</b>\nthere", "/")
    db.expire_all()
    assert db.query(PushSubscription).count() == 0
