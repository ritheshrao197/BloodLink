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
