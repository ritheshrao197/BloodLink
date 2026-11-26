"""Keeps the demo network alive: new SOS requests appear, demo donors pledge, the blood bank confirms them, stale
requests close.

Runs only in demo mode (DEMO_LOGIN=1, or DEMO_PULSE=1). Safety: demo requests are flagged is_demo, never alert anyone
on Telegram and never escalate; only seeded demo donors (no Telegram) respond to them. Real users can still pledge.
"""

import logging
import os
import random
import threading
import time
from datetime import timedelta

from sqlalchemy import func

import eligibility
import geo
import logic
import verification
from database import SessionLocal
from models import BloodRequest, BloodStock, Donation, User, utcnow

log = logging.getLogger("bloodlink.demo")
ENABLED = os.getenv("DEMO_PULSE", os.getenv("DEMO_LOGIN", "1")) == "1"
TICK_SECONDS = 60
MAX_ACTIVE = 16
STALE_HOURS = 30
GROUPS = {"O+": 27, "B+": 26, "A+": 19, "AB+": 7, "O-": 6, "B-": 5, "A-": 4, "AB-": 2}
URGENCY = {"Critical": 28, "High": 47, "Normal": 25}
FIRST_RESPONSE_MIN = {"Critical": 9, "High": 24, "Normal": 70}  # median minutes until someone pledges
CONFIRM_AFTER_MIN = (35, 120)
RECOUNT_HOURS = (6, 16)  # demo blood banks update their stock this often, so it never goes stale (hidden after 48 h)
RIDE_CHANCE = 0.12  # share of demo pledges that ask for help getting to the hospital  # a demo donor reaches the hospital and is confirmed this long after pledging
_rng = random.Random()
_next_sos_at = None


def _pick(weights: dict):
    return _rng.choices(list(weights), weights=list(weights.values()))[0]


def _new_request(db) -> BloodRequest | None:
    """Clone the shape of a recent demo request (real hospital, district, requester style) with fresh details."""
    template = (db.query(BloodRequest).filter(BloodRequest.is_demo.is_(True)).order_by(BloodRequest.id.desc())
                .offset(_rng.randint(0, 300)).first())
    donors = db.query(User).filter(User.is_demo.is_(True), User.role == "donor").order_by(User.id).all()
    if not template or not donors:
        return None
    namer = _rng.choice(donors)
    urgency = _pick(URGENCY)
    req = BloodRequest(requester_name=f"{namer.name.split()[0]} {_rng.choice(donors).name.split()[-1]}",
                       blood_group=_pick(GROUPS), hospital=template.hospital, city=template.city, state=template.state,
                       units_needed=_rng.choices([1, 2, 3, 4], [55, 28, 11, 6])[0], units_fulfilled=0, urgency=urgency,
                       status="Active", is_verified=urgency == "Critical" or _rng.random() < 0.5, is_demo=True,
                       contact_phone=f"+91 {_rng.choice('6789')}{_rng.randint(1000, 9999)} {_rng.randint(10000, 99999)}",
                       requester_language=template.requester_language, lat=template.lat, lng=template.lng,
                       created_at=utcnow(), next_ring_at=None)
    db.add(req)
    db.flush()
    import main  # late import: main imports this module

    req.notified_count = len(main.alert_plan(db, req))  # simulated reach (nobody is actually messaged)
    db.commit()
    return req


def _respond(db, req: BloodRequest) -> bool:
    """A compatible, eligible demo donor near the hospital pledges, through the real donation endpoint."""
    import auth
    import main
    from schemas import DonateBody

    now = utcnow()
    ok = set(logic.compatible_donor_groups(req.blood_group))
    pool = [u for u, _, _ in main.alert_plan(db, req) if u.is_demo and u.blood_group in ok and eligibility.can_be_alerted(u, now)]
    if not pool:
        return False
    donor = _rng.choice(pool[:15])  # the nearest few answer first
    try:
        main.donate(req.id, DonateBody(user_id=donor.id, screening={"answers": {}, "basics_confirmed": True}), db,
                    auth.Actor(is_bot=True))
        if _rng.random() < RIDE_CHANCE:  # set directly: no staff message for simulated traffic
            d = db.query(Donation).filter(Donation.donor_id == donor.id, Donation.request_id == req.id,
                                          Donation.status == "pledged").first()
            if d:
                d.ride_help_at = utcnow()
                db.commit()
        return True
    except Exception as exc:  # noqa: BLE001  (e.g. the donor turned out ineligible: try someone else next tick)
        db.rollback()
        log.debug("demo pledge skipped: %s", exc)
        return False


def _recount_stock(db, now) -> int:
    """Demo banks recount every few hours: units drift a little (issued, collected), the sheet gets a fresh time."""
    import seed_data

    n = 0
    for bank in db.query(User).filter(User.is_demo.is_(True), User.role == "blood_bank").all():
        rows = db.query(BloodStock).filter(BloodStock.bank_id == bank.id).all()
        newest = max((r.updated_at for r in rows), default=None)
        if newest and now - newest < timedelta(hours=_rng.uniform(*RECOUNT_HOURS)):
            continue
        if not rows:
            seed_data.seed_stock(db, bank, _rng, now)
        for r in rows:
            r.units = max(0, r.units + _rng.randint(-3, 3)) if r.units or _rng.random() < 0.3 else 0
            r.updated_at = now
        n += 1
    db.commit()
    return n


def tick() -> dict:
    global _next_sos_at
    db = SessionLocal()
    out = {"created": 0, "pledged": 0, "confirmed": 0, "closed": 0, "stock": 0}
    try:
        now = utcnow()
        out["stock"] = _recount_stock(db, now)
        # close stale demo requests (as hospitals do when they source blood elsewhere)
        for req in db.query(BloodRequest).filter(BloodRequest.is_demo.is_(True), BloodRequest.status == "Active",
                                                 BloodRequest.created_at < now - timedelta(hours=STALE_HOURS)):
            req.status = "Cancelled"
            out["closed"] += 1
        db.commit()
        active = db.query(BloodRequest).filter(BloodRequest.is_demo.is_(True), BloodRequest.status == "Active").all()
        if _next_sos_at is None:
            _next_sos_at = now + timedelta(minutes=_rng.uniform(2, 10))
        if now >= _next_sos_at and len(active) < MAX_ACTIVE:
            if _new_request(db):
                out["created"] += 1
            _next_sos_at = now + timedelta(minutes=_rng.uniform(15, 35))
        # the blood bank confirms demo donors once they have had time to get there (real pledges wait for real staff)
        for d in (db.query(Donation).join(BloodRequest, Donation.request_id == BloodRequest.id)
                  .join(User, Donation.donor_id == User.id)
                  .filter(Donation.status == "pledged", BloodRequest.is_demo.is_(True), User.is_demo.is_(True),
                          Donation.created_at < now - timedelta(minutes=CONFIRM_AFTER_MIN[0])).all()):
            age_min = (now - d.created_at).total_seconds() / 60
            if age_min >= CONFIRM_AFTER_MIN[1] or _rng.random() < 0.15:
                verification.confirm(db, d, None, None, now)
                out["confirmed"] += 1
        db.commit()
        pledged = dict(db.query(Donation.request_id, func.count(Donation.id))
                       .filter(Donation.status == "pledged").group_by(Donation.request_id).all())
        for req in active:
            age_min = (now - req.created_at).total_seconds() / 60
            if age_min < 1.5 or (req.units_fulfilled or 0) + pledged.get(req.id, 0) >= (req.units_needed or 1):
                continue
            # roughly exponential waiting time around the urgency's median
            p = min(0.9, (TICK_SECONDS / 60) * 0.69 / FIRST_RESPONSE_MIN.get(req.urgency, 30))
            if _rng.random() < p and _respond(db, req):
                out["pledged"] += 1
    finally:
        db.close()
    if any(out.values()):
        log.info("demo activity: %s", out)
    return out


def _loop() -> None:
    time.sleep(30)
    while True:
        try:
            tick()
        except Exception:  # noqa: BLE001
            log.exception("demo pulse failed")
        time.sleep(TICK_SECONDS)


def start() -> None:
    if ENABLED:
        threading.Thread(target=_loop, name="demo-pulse", daemon=True).start()
        log.info("Demo activity enabled: new SOS every 15-35 min, demo donors respond (DEMO_PULSE=0 to disable)")
