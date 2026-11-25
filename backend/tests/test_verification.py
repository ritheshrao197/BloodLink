from datetime import timedelta

from sqlalchemy import text

from factory import login, make_request, make_user, pledge
from models import BloodRequest, Donation, User, utcnow


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
