from datetime import timedelta

from factory import login, make_request, make_user, pledge
from models import Donation, User, utcnow


def _pledged(client, db, **donor_kw):
    donor = make_user(db, **donor_kw)
    req = make_request(db)
    assert pledge(client, login(db, donor), req.id, donor.id).status_code == 200
    d = db.query(Donation).filter(Donation.donor_id == donor.id).one()
    bank = make_user(db, name="Mysuru Blood Bank", role="blood_bank")
    return donor, d, login(db, bank)


def _capture(monkeypatch):
    import notifier

    sent = []
    monkeypatch.setattr(notifier, "notify", lambda chat, text: sent.append((chat, text)))
    monkeypatch.setattr(notifier, "notify_buttons", lambda chat, text, buttons: sent.append((chat, text, buttons)))
    return sent


def test_hb_bands():
    import eligibility

    assert eligibility.hb_band(None) is None
    assert eligibility.hb_band(11.9) == "low"
    assert eligibility.hb_band(12.5) == "borderline"
    assert eligibility.hb_band(13.0) == "borderline"
    assert eligibility.hb_band(13.1) == "good"


def test_low_hb_defers_without_points_or_no_show(client, db):
    donor, d, staff_h = _pledged(client, db)
    res = client.post(f"/api/staff/pledges/{d.id}/low-hb", headers=staff_h, json={"hb_g_dl": 11.2})
    assert res.status_code == 200, res.text
    db.expire_all()
    donor, d = db.get(User, donor.id), db.get(Donation, d.id)
    assert d.status == "deferred_hb" and d.hb_g_dl == 11.2 and d.points_awarded == 0
    assert donor.points == 0 and donor.no_show_count == 0 and donor.total_donations == 0
    assert donor.last_donation_at is None
    assert donor.deferred_until > utcnow() + timedelta(days=29)
    import eligibility

    assert eligibility.can_be_alerted(donor, utcnow()) is False
    # the pledge is closed, so a second outcome is refused
    assert client.post(f"/api/staff/pledges/{d.id}/confirm", headers=staff_h, json={}).status_code == 409


def test_low_hb_without_a_reading_works_for_the_bot_button(client, db):
    _, d, staff_h = _pledged(client, db)
    assert client.post(f"/api/staff/pledges/{d.id}/low-hb", headers=staff_h, json={}).status_code == 200


def test_low_hb_reading_must_actually_be_low(client, db):
    _, d, staff_h = _pledged(client, db)
    assert client.post(f"/api/staff/pledges/{d.id}/low-hb", headers=staff_h, json={"hb_g_dl": 13.5}).status_code == 422


def test_confirming_with_a_low_reading_is_refused(client, db):
    _, d, staff_h = _pledged(client, db)
    res = client.post(f"/api/staff/pledges/{d.id}/confirm", headers=staff_h, json={"hb_g_dl": 11.0})
    assert res.status_code == 422
    assert "Low" in res.json()["detail"]


def test_low_hb_message_gives_advice_and_retry_date(client, db, monkeypatch):
    sent = _capture(monkeypatch)
    _, d, staff_h = _pledged(client, db, telegram_id="77")
    sent.clear()
    client.post(f"/api/staff/pledges/{d.id}/low-hb", headers=staff_h, json={"hb_g_dl": 11.2})
    texts = [m[1] for m in sent if m[0] == "77"]
    assert len(texts) == 1
    assert "11.2" in texts[0] and "jaggery" in texts[0] and "doctor" in texts[0]


def test_confirmation_message_includes_hb_and_recovery_tips(client, db, monkeypatch):
    sent = _capture(monkeypatch)
    _, d, staff_h = _pledged(client, db, telegram_id="78")
    sent.clear()
    client.post(f"/api/staff/pledges/{d.id}/confirm", headers=staff_h, json={"hb_g_dl": 13.4})
    text = next(m[1] for m in sent if m[0] == "78" and "confirmed" in m[1].lower())
    assert "13.4" in text and "fluids" in text


def test_staff_pledge_alert_has_a_low_hb_button(client, db, monkeypatch):
    sent = _capture(monkeypatch)
    make_user(db, name="Mysuru Blood Bank", role="blood_bank", telegram_id="900")
    donor = make_user(db)
    pledge(client, login(db, donor), make_request(db).id, donor.id)
    d = db.query(Donation).one()
    buttons = next(m[2] for m in sent if m[0] == "900")
    assert [b["callback_data"] for b in buttons[0]] == [f"pok_{d.id}", f"pns_{d.id}", f"phb_{d.id}"]


def test_activity_lists_hb_history_newest_first(client, db):
    donor = make_user(db)
    old = make_request(db, hospital="Old")
    new = make_request(db, hospital="New")
    db.add_all([Donation(request_id=old.id, donor_id=donor.id, status="confirmed", hb_g_dl=13.6,
                         confirmed_at=utcnow() - timedelta(days=200), created_at=utcnow() - timedelta(days=200)),
                Donation(request_id=new.id, donor_id=donor.id, status="deferred_hb", hb_g_dl=12.1,
                         confirmed_at=utcnow() - timedelta(days=3), created_at=utcnow() - timedelta(days=3))])
    db.commit()
    hb = client.get(f"/api/users/{donor.id}/activity", headers=login(db, donor)).json()["haemoglobin"]
    assert [(h["hb_g_dl"], h["band"], h["status"]) for h in hb] == [(12.1, "low", "deferred_hb"), (13.6, "good", "confirmed")]


def test_reminder_adds_iron_tip_stronger_when_borderline(db, monkeypatch):
    import reminders

    sent = _capture(monkeypatch)
    now = utcnow()
    for tg, hb in (("81", 13.8), ("82", 12.7)):
        donor = make_user(db, name=f"D{tg}", telegram_id=tg, sex="male", last_donation_at=now - timedelta(days=87))
        db.add(Donation(request_id=make_request(db, hospital=f"H{tg}").id, donor_id=donor.id, status="confirmed",
                        hb_g_dl=hb, confirmed_at=donor.last_donation_at, created_at=donor.last_donation_at))
    db.commit()
    reminders._send(db, db.query(User).filter_by(telegram_id="81").one(), "soon", now)
    reminders._send(db, db.query(User).filter_by(telegram_id="82").one(), "soon", now)
    good, borderline = (next(m[1] for m in sent if m[0] == tg) for tg in ("81", "82"))
    assert "iron" in good and "12.7" not in good
    assert "12.7" in borderline and "iron" in borderline
