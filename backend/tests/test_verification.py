from datetime import timedelta

from sqlalchemy import text

from factory import login, make_request, make_user, pledge
from models import BloodRequest, Donation, PointLog, User, utcnow


def donation_points(db, user_id: int) -> int:
    """Points from donations alone (achievements unlocked at confirmation add their own on top)."""
    return sum(l.amount for l in db.query(PointLog).filter(PointLog.user_id == user_id, PointLog.reason.like("%request #%")))


# ---------------------------------------------------------------- model + migration
def test_new_donation_defaults_to_pledged(db):
    donor = make_user(db)
    req = make_request(db)
    d = Donation(request_id=req.id, donor_id=donor.id)
    db.add(d)
    db.commit()
    assert d.status == "pledged"
    assert d.confirmed_at is None and d.hb_g_dl is None
    assert donor.no_show_count == 0 and donor.pledge_blocked_until is None


def test_migrate_marks_old_donations_confirmed(db):
    import main
    from database import engine

    donor = make_user(db)
    req = make_request(db)
    db.add(Donation(request_id=req.id, donor_id=donor.id))
    db.commit()
    donor_id = donor.id
    db.close()
    with engine.begin() as conn:  # simulate a database from before this feature
        conn.execute(text("CREATE TABLE old AS SELECT id, request_id, donor_id, points_awarded, quick_response, "
                          "weather, created_at FROM donations"))
        conn.execute(text("DROP TABLE donations"))
        conn.execute(text("ALTER TABLE old RENAME TO donations"))
        for col in ("no_show_count", "pledge_blocked_until"):
            conn.execute(text(f"ALTER TABLE users DROP COLUMN {col}"))
    main.migrate()
    assert db.query(Donation).one().status == "confirmed"
    assert db.get(User, donor_id).no_show_count == 0


# ---------------------------------------------------------------- pledging
def test_pledge_gives_no_points_and_keeps_dates(client, db):
    donor = make_user(db)
    req = make_request(db)
    res = pledge(client, login(db, donor), req.id, donor.id)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["status"] == "pledged"
    assert body["expected_points"] == 120  # 100 + quick bonus (pledged 1 min after the request)
    db.expire_all()
    donor = db.get(User, donor.id)
    assert donor.points == 0 and donor.total_donations == 0 and donor.last_donation_at is None
    d = db.query(Donation).one()
    assert d.status == "pledged" and d.points_awarded == 0
    assert db.get(BloodRequest, req.id).units_fulfilled == 0


def test_second_open_pledge_is_refused(client, db):
    donor = make_user(db)
    h = login(db, donor)
    assert pledge(client, h, make_request(db).id, donor.id).status_code == 200
    res = pledge(client, h, make_request(db, hospital="Apollo BGS").id, donor.id)
    assert res.status_code == 409
    assert "open pledge" in res.json()["detail"]


def test_blocked_donor_cannot_pledge(client, db):
    donor = make_user(db, no_show_count=3, pledge_blocked_until=utcnow() + timedelta(days=10))
    res = pledge(client, login(db, donor), make_request(db).id, donor.id)
    assert res.status_code == 409
    assert "paused" in res.json()["detail"]


def test_pledge_inside_donation_interval_is_refused(client, db):
    donor = make_user(db, sex="male", last_donation_at=utcnow() - timedelta(days=30))
    res = pledge(client, login(db, donor), make_request(db).id, donor.id)
    assert res.status_code == 409
    assert any(r["code"] == "interval" for r in res.json()["detail"]["eligibility"]["reasons"])


def test_repledge_after_no_show_on_same_request_is_refused(client, db):
    donor = make_user(db)
    req = make_request(db)
    db.add(Donation(request_id=req.id, donor_id=donor.id, status="no_show"))
    db.commit()
    res = pledge(client, login(db, donor), req.id, donor.id)
    assert res.status_code == 400
    assert "already responded" in res.json()["detail"]


def test_pledge_alerts_covering_staff(client, db, monkeypatch):
    import notifier

    sent = []
    monkeypatch.setattr(notifier, "notify_buttons", lambda chat, text, buttons: sent.append((chat, buttons)))
    make_user(db, name="Mysuru Blood Bank", role="blood_bank", telegram_id="900")
    make_user(db, name="Udupi Blood Bank", role="blood_bank", city="Udupi", telegram_id="901")
    donor = make_user(db)
    pledge(client, login(db, donor), make_request(db).id, donor.id)
    assert [c for c, _ in sent] == ["900"]
    d = db.query(Donation).one()
    assert sent[0][1][0][0]["callback_data"] == f"pok_{d.id}"


# ---------------------------------------------------------------- staff confirm / no-show
def _pledged(client, db, **req_kw):
    donor = make_user(db)
    req = make_request(db, **req_kw)
    assert pledge(client, login(db, donor), req.id, donor.id).status_code == 200
    return donor, req, db.query(Donation).filter(Donation.donor_id == donor.id).one()


def _bank(db, **kw):
    return make_user(db, name=kw.pop("name", "Mysuru Blood Bank"), role="blood_bank", **kw)


def test_blood_bank_confirms_and_points_follow(client, db):
    donor, req, d = _pledged(client, db)
    bank = _bank(db)
    h = login(db, bank)
    queue = client.get("/api/staff/pledges", headers=h).json()
    assert [p["donation_id"] for p in queue] == [d.id]
    res = client.post(f"/api/staff/pledges/{d.id}/confirm", headers=h, json={"hb_g_dl": 13.4})
    assert res.status_code == 200, res.text
    assert res.json()["points_awarded"] == 120
    db.expire_all()
    donor, d, req = db.get(User, donor.id), db.get(Donation, d.id), db.get(BloodRequest, req.id)
    assert donation_points(db, donor.id) == 120 and donor.total_donations == 1
    assert donor.last_donation_at == d.confirmed_at
    assert d.status == "confirmed" and d.confirmed_by == bank.id and d.hb_g_dl == 13.4
    assert req.units_fulfilled == 1 and req.status == "Fulfilled"
    assert client.get("/api/staff/pledges", headers=h).json() == []


def test_named_hospital_can_confirm(client, db):
    _, _, d = _pledged(client, db)
    hosp = make_user(db, name="  jss hospital ", role="hospital")
    assert client.post(f"/api/staff/pledges/{d.id}/confirm", headers=login(db, hosp), json={}).status_code == 200


def test_staff_outside_coverage_get_403(client, db):
    _, _, d = _pledged(client, db)
    outsiders = [make_user(db, name="Apollo BGS", role="hospital"),
                 _bank(db, name="Udupi Blood Bank", city="Udupi"),
                 _bank(db, name="Same district, other state", state="Kerala")]
    for u in outsiders:
        res = client.post(f"/api/staff/pledges/{d.id}/confirm", headers=login(db, u), json={})
        assert res.status_code == 403, u.name
    plain = make_user(db, name="Not Staff")
    assert client.get("/api/staff/pledges", headers=login(db, plain)).status_code == 403
    assert client.post(f"/api/staff/pledges/{d.id}/confirm", headers=login(db, plain), json={}).status_code == 403
    assert client.get("/api/staff/pledges").status_code == 401


def test_staff_cannot_confirm_own_pledge(client, db):
    bank = _bank(db)
    req = make_request(db)
    db.add(Donation(request_id=req.id, donor_id=bank.id, status="pledged"))
    db.commit()
    d = db.query(Donation).one()
    assert client.post(f"/api/staff/pledges/{d.id}/confirm", headers=login(db, bank), json={}).status_code == 403


def test_confirm_twice_is_409(client, db):
    _, _, d = _pledged(client, db)
    h = login(db, _bank(db))
    assert client.post(f"/api/staff/pledges/{d.id}/confirm", headers=h, json={}).status_code == 200
    assert client.post(f"/api/staff/pledges/{d.id}/confirm", headers=h, json={}).status_code == 409
    assert client.post(f"/api/staff/pledges/{d.id}/no-show", headers=h, json={}).status_code == 409
    assert client.post("/api/staff/pledges/9999/confirm", headers=h, json={}).status_code == 404


def test_confirm_after_request_closed_still_counts(client, db):
    donor, req, d = _pledged(client, db)
    req = db.get(BloodRequest, req.id)
    req.status = "Cancelled"
    db.commit()
    assert client.post(f"/api/staff/pledges/{d.id}/confirm", headers=login(db, _bank(db)), json={}).status_code == 200
    db.expire_all()
    assert donation_points(db, donor.id) == 120
    assert db.get(BloodRequest, req.id).status == "Cancelled"


def test_hb_out_of_range_is_rejected(client, db):
    _, _, d = _pledged(client, db)
    res = client.post(f"/api/staff/pledges/{d.id}/confirm", headers=login(db, _bank(db)), json={"hb_g_dl": 90})
    assert res.status_code == 422


def test_no_show_counts_and_third_blocks(client, db):
    donor = make_user(db)
    bank_h = login(db, _bank(db))
    donor_h = login(db, donor)
    for n in range(1, 4):
        req = make_request(db, hospital=f"Hospital {n}")
        assert pledge(client, donor_h, req.id, donor.id).status_code == 200
        d = db.query(Donation).filter(Donation.request_id == req.id).one()
        res = client.post(f"/api/staff/pledges/{d.id}/no-show", headers=bank_h, json={})
        assert res.json()["no_show_count"] == n
    db.expire_all()
    donor = db.get(User, donor.id)
    assert donor.points == 0
    assert donor.pledge_blocked_until > utcnow() + timedelta(days=29)
    assert pledge(client, donor_h, make_request(db, hospital="Hospital 4").id, donor.id).status_code == 409


def test_bot_confirms_for_linked_staff_only(client, db, monkeypatch):
    import auth

    monkeypatch.setattr(auth, "BOT_SECRET", "test-secret")
    bot = {"X-Bot-Secret": "test-secret"}
    _, _, d = _pledged(client, db)
    _bank(db, telegram_id="900")
    make_user(db, name="Random", telegram_id="901")
    url = f"/api/staff/pledges/{d.id}/confirm"
    assert client.post(url, headers=bot, json={"staff_telegram_id": "901"}).status_code == 403
    assert client.post(url, headers=bot, json={"staff_telegram_id": "555"}).status_code == 403
    assert client.post(url, headers=bot, json={}).status_code == 403
    assert client.post(url, headers=bot, json={"staff_telegram_id": "900"}).status_code == 200


def test_first_confirmed_donation_pays_referrer(client, db):
    import logic
    from models import Referral

    referrer = make_user(db, name="Meera")
    donor = make_user(db, referred_by=referrer.referral_code)
    db.add(Referral(referrer_id=referrer.id, referred_id=donor.id, status="Registered", points_awarded=50))
    db.commit()
    pledge(client, login(db, donor), make_request(db).id, donor.id)
    db.expire_all()
    assert db.get(User, referrer.id).points == 0  # nothing at pledge time
    d = db.query(Donation).one()
    client.post(f"/api/staff/pledges/{d.id}/confirm", json={}, headers=login(db, _bank(db)))
    db.expire_all()
    paid = db.query(PointLog).filter(PointLog.user_id == referrer.id, PointLog.reason.like("Referral:%donated")).one()
    assert paid.amount == logic.POINTS_REFERRAL_DONATION


def test_old_pledges_expire_as_no_shows(db):
    import verification

    donor = make_user(db)
    other = make_user(db, name="Other")
    db.add_all([Donation(request_id=make_request(db, hospital="Old").id, donor_id=donor.id, status="pledged",
                         created_at=utcnow() - timedelta(hours=25)),
                Donation(request_id=make_request(db, hospital="New").id, donor_id=other.id, status="pledged",
                         created_at=utcnow() - timedelta(hours=2))])
    db.commit()
    assert verification.expire_once() == 1
    db.expire_all()
    assert sorted(d.status for d in db.query(Donation)) == ["expired", "pledged"]
    assert db.get(User, donor.id).no_show_count == 1
