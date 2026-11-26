from datetime import timedelta

import eligibility
from database import SessionLocal
from factory import make_user
from models import User, utcnow


def test_demo_accounts_inside_gap_can_donate_again():
    db = SessionLocal()
    now = utcnow()
    man = make_user(db, name="Demo M", sex="male", is_demo=True, last_donation_at=now - timedelta(days=10), total_donations=3)
    woman = make_user(db, name="Demo F", sex="female", is_demo=True, last_donation_at=now - timedelta(days=100))
    old = make_user(db, name="Demo old", sex="male", is_demo=True, last_donation_at=now - timedelta(days=200))
    real = make_user(db, name="Real", sex="male", last_donation_at=now - timedelta(days=10))

    assert eligibility.clear_demo_intervals(db, now) == 2

    for u in (man, woman, old):
        db.refresh(u)
        assert all(r["code"] != "interval" for r in eligibility.status(u, now)["reasons"])
        assert eligibility.can_be_alerted(u, now)
    assert db.get(User, old.id).last_donation_at == now - timedelta(days=200)  # outside the gap: untouched
    assert db.get(User, man.id).total_donations == 3  # history kept
    db.refresh(real)
    assert real.last_donation_at == now - timedelta(days=10)  # real accounts never touched
    assert not eligibility.can_be_alerted(real, now)
    db.close()
