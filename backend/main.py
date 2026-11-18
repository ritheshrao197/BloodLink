import logging
import os
from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import func, inspect, text
from sqlalchemy.orm import Session

import database  # noqa: F401  (loads .env before notifier reads the token)
import achievements
import auth
import community
import demo_pulse
import eligibility
import geo
import reminders
from database import Base, SessionLocal, engine, get_db
import locations
import logic
import notifier
import secrets
import threading
import weather
from models import AuthSession, BloodRequest, Donation, LoginRequest, SosAlert, PointLog, Referral, Reward, User, UserAchievement, utcnow
from schemas import (AvailabilityBody, DonateBody, EligibilityBody, HealthBody, LanguageBody, LocationBody, RedeemBody, SOSCreate,
                     UserCreate)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("bloodlink")


def migrate() -> None:
    """Add columns introduced after v2.0 to existing SQLite files and map old city names to districts."""
    new_columns = {"users": {"state": "VARCHAR", "language": "VARCHAR DEFAULT 'en'", "available_since": "TIMESTAMP",
                             "sex": "VARCHAR", "date_of_birth": "DATE", "weight_kg": "INTEGER", "deferred_until": "TIMESTAMP",
                             "is_admin": "BOOLEAN DEFAULT FALSE", "is_demo": "BOOLEAN DEFAULT FALSE",
                             "lat": "FLOAT", "lng": "FLOAT", "location_at": "TIMESTAMP"},
                   "requests": {"state": "VARCHAR", "requester_language": "VARCHAR", "lat": "FLOAT", "lng": "FLOAT",
                                "alert_ring": "INTEGER DEFAULT 0", "next_ring_at": "TIMESTAMP", "is_demo": "BOOLEAN DEFAULT FALSE"},
                   "donations": {"weather": "VARCHAR"}}
    insp = inspect(engine)
    with engine.begin() as conn:
        for table, cols in new_columns.items():
            existing = {c["name"] for c in insp.get_columns(table)}
            for name, ddl in cols.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))
                    if name == "available_since":  # assume people available now have been since joining
                        conn.execute(text("UPDATE users SET available_since = created_at WHERE is_available"))
    db = SessionLocal()
    try:
        for row in [*db.query(User).filter(User.state.is_(None)), *db.query(BloodRequest).filter(BloodRequest.state.is_(None))]:
            state, district = locations.normalize(row.city)
            if state:
                row.state, row.city = state, district
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    migrate()
    if os.getenv("AUTO_SEED", "1") == "1":
        db = SessionLocal()
        try:
            from seed_data import auto_seed

            if done := auto_seed(db):
                log.info("Demo data: %s (set AUTO_SEED=0 to disable)", done)
        except Exception:  # noqa: BLE001  (never block startup: the previous data stays in place)
            log.exception("Demo data refresh failed; keeping existing data")
        finally:
            db.close()
    db = SessionLocal()
    try:
        if n := auth.promote_admins(db):
            log.info("Admins from ADMIN_TELEGRAM_IDS: %d", n)
    finally:
        db.close()
    db = SessionLocal()
    try:  # award anything already earned (existing users after an upgrade, time-based ones like The Constant)
        unlocked = achievements.evaluate(db, db.query(User).filter(User.role == "donor").all())
        db.commit()
        if unlocked:
            log.info("Achievements: %d unlocked for %d users at startup", sum(map(len, unlocked.values())), len(unlocked))
    finally:
        db.close()
    log.info("Telegram notifications %s", "ENABLED" if notifier.enabled() else "DISABLED (no TELEGRAM_BOT_TOKEN)")
    reminders.start()
    threading.Thread(target=_escalation_loop, name="sos-escalation", daemon=True).start()
    demo_pulse.start()
    yield


app = FastAPI(title="BLOODLINK API", version="2.0", lifespan=lifespan)
app.include_router(community.router)  # teams + donation camps
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

WEB_URL = os.getenv("BLOODLINK_WEB_URL", "http://localhost:5173").rstrip("/")


# ---------------------------------------------------------------- serializers
def iso(dt):
    return dt.isoformat() + "Z" if dt else None


def user_public(u: User) -> dict:
    return {
        "id": u.id, "name": u.name, "blood_group": u.blood_group, "city": u.city, "state": u.state, "role": u.role,
        "points": u.points, "badge": u.badge, "total_donations": u.total_donations,
        "is_available": u.is_available, "is_verified": u.is_verified,
        "telegram_linked": bool(u.telegram_id), "last_donation_at": iso(u.last_donation_at),
        "created_at": iso(u.created_at),
    }


def referral_stats(db: Session, u: User) -> dict:
    refs = db.query(Referral).filter(Referral.referrer_id == u.id).all()
    return {
        "total": len(refs),
        "registered": len(refs),
        "donated": sum(1 for r in refs if r.status == "Donated"),
        "points_earned": sum(r.points_awarded or 0 for r in refs),
    }


def user_private(db: Session, u: User) -> dict:
    bot = notifier.bot_username()
    stats = referral_stats(db, u)
    extra_badges = ["Influencer"] if stats["total"] >= logic.INFLUENCER_REFERRALS else []
    return {
        **user_public(u),
        "phone": u.phone,
        "language": u.language or "en",
        "telegram_username": u.telegram_username,
        "referral_code": u.referral_code,
        "referred_by": u.referred_by,
        "badge_info": logic.badge_info(u.badge),
        "extra_badges": extra_badges,
        "referral_link": f"https://t.me/{bot}?start={u.referral_code}",
        "web_referral_link": f"{WEB_URL}/register?ref={u.referral_code}",
        "is_admin": bool(u.is_admin),
        "is_demo": bool(u.is_demo),
        "location": {"lat": u.lat, "lng": u.lng, "updated_at": iso(u.location_at)} if geo.valid(u.lat, u.lng) else None,
        "referrals": stats,
        "achievements": achievements.showcase(db, [u.id])[u.id],
        "eligibility": eligibility.status(u) if u.role == "donor" else None,
    }


def request_out(r: BloodRequest) -> dict:
    return {
        "id": r.id, "requester_name": r.requester_name, "blood_group": r.blood_group,
        "hospital": r.hospital, "city": r.city, "state": r.state, "units_needed": r.units_needed,
        "units_fulfilled": r.units_fulfilled, "urgency": r.urgency, "status": r.status,
        "fulfilled_by": r.fulfilled_by, "is_verified": r.is_verified,
        "notified_count": r.notified_count, "contact_phone": r.contact_phone,
        "compatible_donor_groups": logic.compatible_donor_groups(r.blood_group),
        "lat": r.lat, "lng": r.lng,
        "created_at": iso(r.created_at), "fulfilled_at": iso(r.fulfilled_at),
    }


def find_user(db: Session, user_id: int | None = None, telegram_id: str | None = None) -> User:
    user = None
    if user_id is not None:
        user = db.get(User, user_id)
    elif telegram_id:
        user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
    if not user:
        raise HTTPException(404, "User not found. Register first (web app or /register on Telegram).")
    return user


# ---------------------------------------------------------------- meta
@app.get("/api/health")
def health():
    return {"status": "ok", "telegram": notifier.enabled()}


@app.get("/api/config")
def config(db: Session = Depends(get_db)):
    heroes = []
    if auth.DEMO_LOGIN:  # showcase accounts, each with (almost) every achievement
        import seed_data
        codes = [h["code"] for h in seed_data.HEROES]
        counts = dict(db.query(User.referral_code, func.count(UserAchievement.id))
                      .join(UserAchievement, UserAchievement.user_id == User.id)
                      .filter(User.referral_code.in_(codes), User.is_demo.is_(True)).group_by(User.referral_code).all())
        names = dict(db.query(User.referral_code, User.name).filter(User.referral_code.in_(codes), User.is_demo.is_(True)).all())
        heroes = [{"code": c, "name": names[c], "achievements": counts.get(c, 0), "total": len(achievements.CATALOG)}
                  for c in codes if c in names]
    return {
        "blood_groups": logic.BLOOD_GROUPS,
        "compatibility": logic.COMPATIBILITY,
        "badges": [{"name": n, "min_points": m, "icon": i, "title": t} for n, m, i, t in logic.BADGES],
        "points": {
            "register": logic.POINTS_REGISTER, "welcome_bonus": logic.POINTS_WELCOME_BONUS,
            "referral_register": logic.POINTS_REFERRAL_REGISTER, "donation": logic.POINTS_DONATION,
            "referral_donation": logic.POINTS_REFERRAL_DONATION, "quick_response": logic.POINTS_QUICK_RESPONSE,
            "streak": logic.POINTS_STREAK,
        },
        "bot_username": notifier.bot_username(),
        "telegram_enabled": notifier.enabled(),
        "telegram_login": notifier.enabled(),
        "demo_login": auth.DEMO_LOGIN,
        "demo_hero_code": heroes[0]["code"] if heroes else None,  # kept for older clients
        "demo_heroes": heroes,
        "admin_password_login": bool(auth.ADMIN_PASSWORD),
    }


@app.get("/api/locations")
def get_locations():
    """State -> district -> hospital tree for tap-to-select pickers."""
    return {"states": locations.as_tree()}


@app.get("/api/compatible/{blood_group}")
def get_compatible(blood_group: str):
    bg = blood_group.upper()
    if bg not in logic.COMPATIBILITY:
        raise HTTPException(400, "Unknown blood group")
    return {"blood_group": bg, "compatible_donors": logic.compatible_donor_groups(bg),
            "can_donate_to": logic.recipients_for(bg)}


# ---------------------------------------------------------------- users
@app.post("/api/register")
def register_user(body: UserCreate, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    if body.telegram_id and not a.is_bot:
        raise HTTPException(403, "Telegram accounts are linked through the bot.")
    if body.telegram_id and db.query(User).filter(User.telegram_id == body.telegram_id).first():
        raise HTTPException(409, "This Telegram account is already registered.")

    referrer = None
    ref_code = (body.referred_by or "").strip().upper() or None
    if ref_code:
        referrer = db.query(User).filter(func.upper(User.referral_code) == ref_code).first()
        if not referrer:
            raise HTTPException(400, f"Referral code '{body.referred_by}' not found.")

    state, district = locations.normalize(body.city, body.state)
    user = User(
        name=body.name, blood_group=body.blood_group, city=district, state=state, phone=body.phone,
        language=body.language,
        role=body.role, telegram_id=body.telegram_id, telegram_username=body.telegram_username,
        referral_code=logic.new_referral_code(db),
        referred_by=referrer.referral_code if referrer else None, points=0,
        sex=body.sex, date_of_birth=body.date_of_birth, weight_kg=body.weight_kg,
    )
    db.add(user)
    db.flush()
    logic.award(db, user, logic.POINTS_REGISTER, "Registration bonus")

    if referrer:
        logic.award(db, user, logic.POINTS_WELCOME_BONUS, f"Welcome bonus (invited by {referrer.name})")
        logic.award(db, referrer, logic.POINTS_REFERRAL_REGISTER, f"Referral: {user.name} registered")
        db.add(Referral(referrer_id=referrer.id, referred_id=user.id, status="Registered",
                        points_awarded=logic.POINTS_REFERRAL_REGISTER))
        notifier.notify_t(referrer.telegram_id, referrer.language, "ref_joined",
                          name=notifier.esc(user.name), points=logic.POINTS_REFERRAL_REGISTER)
        db.flush()
        achievements.evaluate(db, [referrer])
    token = None if a.is_bot else auth.new_session(db, user)  # the web registrant is signed in straight away
    db.commit()
    db.refresh(user)
    return {"status": "success", "user_id": user.id, "referral_code": user.referral_code,
            "points": user.points, "user": user_private(db, user), "token": token}


@app.get("/api/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    user = find_user(db, user_id=user_id)
    if a.is_bot or a.is_admin or (a.user and a.user.id == user.id):
        return user_private(db, user)
    return user_public(user)


@app.get("/api/users/by-code/{code}")
def get_user_by_code(code: str, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    auth.require_admin(a)
    user = db.query(User).filter(func.upper(User.referral_code) == code.strip().upper()).first()
    if not user:
        raise HTTPException(404, "No user with that code")
    return user_private(db, user)


@app.get("/api/users/by-telegram/{telegram_id}")
def get_user_by_telegram(telegram_id: str, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    auth.require_bot(a)
    return user_private(db, find_user(db, telegram_id=telegram_id))


@app.get("/api/users/{user_id}/activity")
def user_activity(user_id: int, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    user = find_user(db, user_id=user_id)
    auth.require_self(a, user)
    logs = db.query(PointLog).filter(PointLog.user_id == user.id).order_by(PointLog.id.desc()).limit(30).all()
    donations = (
        db.query(Donation, BloodRequest).join(BloodRequest, Donation.request_id == BloodRequest.id)
        .filter(Donation.donor_id == user.id).order_by(Donation.id.desc()).all()
    )
    vouchers = db.query(Reward).filter(Reward.user_id == user.id).order_by(Reward.id.desc()).all()
    referrals = (
        db.query(Referral, User).join(User, Referral.referred_id == User.id)
        .filter(Referral.referrer_id == user.id).order_by(Referral.id.desc()).all()
    )
    return {
        "points_log": [{"amount": l.amount, "reason": l.reason, "created_at": iso(l.created_at)} for l in logs],
        "donations": [{"request_id": r.id, "hospital": r.hospital, "city": r.city, "blood_group": r.blood_group,
                       "points_awarded": d.points_awarded, "quick_response": d.quick_response,
                       "created_at": iso(d.created_at)} for d, r in donations],
        "vouchers": [{"reward_name": v.reward_name, "points_cost": v.points_cost, "voucher_code": v.voucher_code,
                      "status": v.status, "created_at": iso(v.created_at)} for v in vouchers],
        "referrals": [{"name": u.name, "blood_group": u.blood_group, "status": ref.status,
                       "points_awarded": ref.points_awarded, "created_at": iso(ref.created_at)}
                      for ref, u in referrals],
    }


def set_available(user: User, value: bool) -> None:
    if value and not user.is_available:
        user.available_since = utcnow()
    elif not value:
        user.available_since = None
    user.is_available = value


def _set_location(user: User, body: LocationBody | None) -> None:
    if body is None:
        user.lat = user.lng = user.location_at = None
    else:
        user.lat, user.lng, user.location_at = geo.round_coord(body.lat), geo.round_coord(body.lng), utcnow()


@app.patch("/api/users/{user_id}/location")
def set_location(user_id: int, body: LocationBody, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    """Opt-in approximate location (rounded to ~1 km) so the nearest donors are alerted first."""
    user = find_user(db, user_id=user_id)
    auth.require_self(a, user)
    _set_location(user, body)
    db.commit()
    return user_private(db, user)


@app.delete("/api/users/{user_id}/location")
def clear_location(user_id: int, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    user = find_user(db, user_id=user_id)
    auth.require_self(a, user)
    _set_location(user, None)
    db.commit()
    return user_private(db, user)


@app.patch("/api/users/by-telegram/{telegram_id}/location")
def set_location_tg(telegram_id: str, body: LocationBody, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    auth.require_bot(a)
    user = find_user(db, telegram_id=telegram_id)
    _set_location(user, body)
    db.commit()
    return user_private(db, user)


@app.patch("/api/users/{user_id}/availability")
def set_availability(user_id: int, body: AvailabilityBody, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    user = find_user(db, user_id=user_id)
    auth.require_self(a, user)
    set_available(user, body.is_available)
    db.commit()
    return user_private(db, user)


@app.patch("/api/users/by-telegram/{telegram_id}/availability")
def set_availability_tg(telegram_id: str, body: AvailabilityBody, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    auth.require_bot(a)
    user = find_user(db, telegram_id=telegram_id)
    set_available(user, body.is_available)
    db.commit()
    return user_private(db, user)


@app.patch("/api/users/{user_id}/language")
def set_language(user_id: int, body: LanguageBody, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    """Web language choice; Telegram messages follow it too."""
    user = find_user(db, user_id=user_id)
    auth.require_self(a, user)
    user.language = body.language
    db.commit()
    return user_private(db, user)


@app.patch("/api/users/by-telegram/{telegram_id}/language")
def set_language_tg(telegram_id: str, body: LanguageBody, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    auth.require_bot(a)
    user = find_user(db, telegram_id=telegram_id)
    user.language = body.language
    db.commit()
    return user_private(db, user)


# ---------------------------------------------------------------- eligibility
def _save_health(user: User, health: HealthBody | None) -> None:
    if not health:
        return
    for field in ("sex", "date_of_birth", "weight_kg"):
        value = getattr(health, field)
        if value is not None:
            setattr(user, field, value)


@app.get("/api/eligibility/questions")
def eligibility_questions(sex: str | None = None):
    return {"questions": eligibility.questions_for(sex), "min_age": eligibility.MIN_AGE, "max_age": eligibility.MAX_AGE,
            "min_weight_kg": eligibility.MIN_WEIGHT_KG, "interval_days": eligibility.INTERVAL_DAYS}


@app.post("/api/eligibility/check")
def eligibility_check(body: EligibilityBody, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    """Run the pre-donation check without donating (records any deferral)."""
    user = find_user(db, user_id=body.user_id, telegram_id=body.telegram_id)
    auth.require_self(a, user)
    _save_health(user, body.screening.health)
    result = eligibility.check(user, body.screening.model_dump())
    db.commit()
    return result


@app.patch("/api/users/{user_id}/health")
def set_health(user_id: int, body: HealthBody, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    user = find_user(db, user_id=user_id)
    auth.require_self(a, user)
    _save_health(user, body)
    db.commit()
    return user_private(db, user)


@app.delete("/api/users/{user_id}/deferral")
def clear_deferral(user_id: int, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    """The donor answered a screening question by mistake: lift the self-reported deferral."""
    user = find_user(db, user_id=user_id)
    auth.require_self(a, user)
    user.deferred_until = None
    db.commit()
    return user_private(db, user)


@app.get("/api/donors")
def search_donors(
    blood_group: str | None = None,
    city: str | None = None,
    available: bool | None = None,
    compatible_for: str | None = Query(None, description="Recipient group: return every compatible donor"),
    db: Session = Depends(get_db),
):
    q = db.query(User).filter(User.role == "donor")
    if compatible_for:
        q = q.filter(User.blood_group.in_(logic.compatible_donor_groups(compatible_for.upper())))
    elif blood_group:
        q = q.filter(User.blood_group == blood_group.upper())
    if city:
        q = q.filter(func.lower(User.city).contains(city.strip().lower()))
    if available is not None:
        q = q.filter(User.is_available == available)
    return [user_public(u) for u in q.order_by(User.is_available.desc(), User.points.desc()).limit(200)]


@app.get("/api/leaderboard")
def leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(User).filter(User.role != "admin").order_by(User.points.desc(), User.id).limit(min(limit, 100)).all()
    counts = dict(
        db.query(Referral.referrer_id, func.count(Referral.id)).group_by(Referral.referrer_id).all()
    )
    shows = achievements.showcase(db, [u.id for u in users])
    return [
        {"id": u.id, "name": u.name, "points": u.points, "badge": u.badge, "blood_group": u.blood_group,
         "city": u.city, "total_donations": u.total_donations, "referrals": counts.get(u.id, 0),
         "influencer": counts.get(u.id, 0) >= logic.INFLUENCER_REFERRALS, "achievements": shows[u.id]}
        for u in users
    ]


# ---------------------------------------------------------------- requests / SOS
def alert_plan(db: Session, req: BloodRequest) -> list[tuple[User, int, float | None]]:
    """Every donor who could answer this request, with their alert circle (0 = nearest) and distance, nearest first."""
    groups = logic.compatible_donor_groups(req.blood_group)
    q = db.query(User).filter(User.role == "donor", User.is_available.is_(True), User.blood_group.in_(groups))
    if req.requester_telegram_id:
        q = q.filter((User.telegram_id.is_(None)) | (User.telegram_id != req.requester_telegram_id))
    if req.state:
        q = q.filter((User.state == req.state) | (func.lower(User.city) == req.city.lower()))
    else:
        q = q.filter(func.lower(User.city) == req.city.lower())
    now = utcnow()
    has_point = geo.valid(req.lat, req.lng)
    plan = []
    for u in q.all():
        if not eligibility.can_be_alerted(u, now):
            continue
        dist = geo.km(req.lat, req.lng, u.lat, u.lng) if has_point and geo.valid(u.lat, u.lng) else None
        same_district = (u.city or "").lower() == (req.city or "").lower()
        ring = geo.ring_for(dist, same_district, bool(req.state) and u.state == req.state)
        if not has_point and same_district:
            ring = 0  # no location on the request: the whole district is the first circle
        if ring is not None:
            plan.append((u, ring, dist))
    plan.sort(key=lambda x: (x[1], x[2] if x[2] is not None else 9999))
    return plan


def matching_donors(db: Session, req: BloodRequest) -> list[User]:
    return [u for u, _, _ in alert_plan(db, req)]


def first_wave(plan) -> int:
    """Widest circle in the first wave: grow until enough donors are reached."""
    rings = sorted({r for _, r, _ in plan})
    reached = 0
    for r in rings:
        reached += sum(1 for _, ring, _ in plan if ring == r)
        if reached >= geo.MIN_FIRST_WAVE:
            return r
    return rings[-1] if rings else 0


def send_rings(db: Session, req: BloodRequest, upto: int) -> int:
    """Alert everyone in circles <= upto who has not been alerted yet. Returns Telegram messages delivered."""
    done = {uid for (uid,) in db.query(SosAlert.user_id).filter(SosAlert.request_id == req.id)}
    batch = [(u, r, d) for u, r, d in alert_plan(db, req) if r <= upto and u.id not in done]
    for u, r, d in batch:
        db.add(SosAlert(request_id=req.id, user_id=u.id, ring=r, distance_km=round(d, 2) if d is not None else None))
    db.commit()
    targets = [] if req.is_demo else [  # simulated demo requests never message real people
        {"telegram_id": u.telegram_id, "language": u.language, "km": geo.shown_km(d)} for u, _, d in batch if u.telegram_id]
    sent = notifier.broadcast_sos(request_out(req), targets) if targets else 0
    req.notified_count = (req.notified_count or 0) + sent
    db.commit()
    return sent


def _schedule_next(req: BloodRequest, plan, now) -> None:
    wider = [r for _, r, _ in plan if r > (req.alert_ring or 0)]
    req.next_ring_at = now + timedelta(minutes=geo.ESCALATE_MINUTES.get(req.urgency, 10)) if wider else None


def _broadcast(request_id: int):
    db = SessionLocal()
    try:
        req = db.get(BloodRequest, request_id)
        plan = alert_plan(db, req)
        req.alert_ring = first_wave(plan)
        sent = send_rings(db, req, req.alert_ring)
        _schedule_next(req, plan, utcnow())
        db.commit()
        log.info("SOS #%s: first wave (circles <= %s) reached %s Telegram donors", request_id, req.alert_ring, sent)
    finally:
        db.close()


def escalate_once() -> int:
    """Widen the alert circle for open requests whose wait is over. Returns how many requests escalated."""
    db = SessionLocal()
    n = 0
    try:
        now = utcnow()
        for req in db.query(BloodRequest).filter(BloodRequest.status == "Active", BloodRequest.next_ring_at.isnot(None),
                                                 BloodRequest.next_ring_at <= now).all():
            if (req.units_fulfilled or 0) >= (req.units_needed or 1):
                req.next_ring_at = None
                continue
            plan = alert_plan(db, req)
            rings = sorted({r for _, r, _ in plan if r > (req.alert_ring or 0)})
            if not rings:
                req.next_ring_at = None
                continue
            req.alert_ring = rings[0]
            sent = send_rings(db, req, req.alert_ring)
            _schedule_next(req, plan, now)
            n += 1
            log.info("SOS #%s still open: widened to circle %s, %s more donors alerted", req.id, req.alert_ring, sent)
        db.commit()
    finally:
        db.close()
    return n


def _escalation_loop() -> None:
    import time

    while True:
        time.sleep(60)
        try:
            escalate_once()
        except Exception:  # noqa: BLE001  (keep the loop alive)
            log.exception("escalation run failed")


@app.post("/api/sos")
def create_sos(body: SOSCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    req = BloodRequest(**body.model_dump(exclude={"lat", "lng"}))
    req.state, req.city = locations.normalize(body.city, body.state)
    point = (body.lat, body.lng) if geo.valid(body.lat, body.lng) else geo.DISTRICT_CENTRES.get(req.city)
    if point:
        req.lat, req.lng = geo.round_coord(point[0]), geo.round_coord(point[1])
    db.add(req)
    db.commit()
    db.refresh(req)
    plan = alert_plan(db, req)
    wave = first_wave(plan)
    first = [(u, r, d) for u, r, d in plan if r <= wave]
    background_tasks.add_task(_broadcast, req.id)
    return {
        "status": "broadcasted",
        "request_id": req.id,
        "matched_donors": len(plan),
        "first_wave": len(first),
        "first_wave_km": geo.RINGS_KM[wave] if wave < len(geo.RINGS_KM) and geo.valid(req.lat, req.lng) else None,
        "escalate_minutes": geo.ESCALATE_MINUTES.get(req.urgency, 10),
        "telegram_reachable": sum(1 for u, _, _ in first if u.telegram_id),
        "donors": [{**user_public(u), "distance_km": geo.shown_km(d), "ring": r} for u, r, d in plan[:20]],
        "request": request_out(req),
    }


@app.get("/api/requests")
def get_requests(status: str = "Active", db: Session = Depends(get_db)):
    q = db.query(BloodRequest)
    if status.lower() != "all":
        q = q.filter(BloodRequest.status == status.title())
    return [request_out(r) for r in q.order_by(BloodRequest.id.desc()).limit(200)]


@app.get("/api/requests/{request_id}")
def get_request(request_id: int, db: Session = Depends(get_db)):
    req = db.get(BloodRequest, request_id)
    if not req:
        raise HTTPException(404, "Request not found")
    donors = (
        db.query(Donation, User).join(User, Donation.donor_id == User.id)
        .filter(Donation.request_id == req.id).all()
    )
    return {**request_out(req), "donors": [{"name": u.name, "blood_group": u.blood_group,
                                            "created_at": iso(d.created_at)} for d, u in donors]}


@app.post("/api/donate/{request_id}")
def donate(request_id: int, body: DonateBody, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    if not body.confirmed:
        raise HTTPException(400, "Please confirm this donation is real.")
    req = db.get(BloodRequest, request_id)
    if not req:
        raise HTTPException(404, "Request not found")
    if req.status != "Active":
        raise HTTPException(400, f"This request is already {req.status.lower()}. Thank you anyway! 🙏")
    donor = find_user(db, user_id=body.user_id, telegram_id=body.donor_telegram_id)
    auth.require_self(a, donor)
    if not logic.can_donate(donor.blood_group, req.blood_group):
        raise HTTPException(400, f"{donor.blood_group} cannot donate to a {req.blood_group} patient. "
                                 f"Compatible groups: {', '.join(logic.compatible_donor_groups(req.blood_group))}.")
    if db.query(Donation).filter(Donation.request_id == req.id, Donation.donor_id == donor.id).first():
        raise HTTPException(400, "You have already responded to this request.")
    if body.screening is None:
        raise HTTPException(400, "Please answer the quick health check before donating.")
    _save_health(donor, body.screening.health)
    check = eligibility.check(donor, body.screening.model_dump())
    if not check["eligible"]:
        db.commit()  # keep any recorded deferral
        raise HTTPException(409, {"message": "Not eligible to donate right now.", "eligibility": check})

    now = utcnow()
    breakdown = [{"code": "donation", "reason": "Successful donation", "points": logic.POINTS_DONATION}]
    quick = req.created_at and (now - req.created_at) <= timedelta(minutes=logic.QUICK_RESPONSE_MINUTES)
    if quick:
        breakdown.append({"code": "quick", "reason": "Quick response (< 5 min)", "points": logic.POINTS_QUICK_RESPONSE})
    if donor.last_donation_at and (now - donor.last_donation_at) >= timedelta(days=logic.STREAK_DAYS):
        breakdown.append({"code": "streak", "reason": "Streak bonus (3-month return)", "points": logic.POINTS_STREAK})

    first_donation = (donor.total_donations or 0) == 0
    for item in breakdown:
        logic.award(db, donor, item["points"], f"{item['reason']} — request #{req.id}")
    total = sum(i["points"] for i in breakdown)
    donor.total_donations = (donor.total_donations or 0) + 1
    donor.last_donation_at = now
    db.add(Donation(request_id=req.id, donor_id=donor.id, points_awarded=total, quick_response=bool(quick)))

    req.units_fulfilled = (req.units_fulfilled or 0) + 1
    req.fulfilled_by = f"{req.fulfilled_by}, {donor.name}" if req.fulfilled_by else donor.name
    if req.units_fulfilled >= req.units_needed:
        req.status = "Fulfilled"
        req.fulfilled_at = now

    # Referral payout: referrer earns +200 BLP and a voucher on the friend's first donation
    if first_donation and donor.referred_by:
        referrer = db.query(User).filter(User.referral_code == donor.referred_by).first()
        if referrer:
            logic.award(db, referrer, logic.POINTS_REFERRAL_DONATION, f"Referral: {donor.name} donated")
            code = logic.voucher_code(logic.REFERRAL_VOUCHER["prefix"])
            db.add(Reward(user_id=referrer.id, reward_name=logic.REFERRAL_VOUCHER["name"], points_cost=0,
                          voucher_code=code))
            ref = db.query(Referral).filter(Referral.referrer_id == referrer.id,
                                            Referral.referred_id == donor.id).first()
            if ref:
                ref.status = "Donated"
                ref.points_awarded = (ref.points_awarded or 0) + logic.POINTS_REFERRAL_DONATION
            notifier.notify_t(referrer.telegram_id, referrer.language, "ref_donated",
                              name=notifier.esc(donor.name), points=logic.POINTS_REFERRAL_DONATION, code=code)
    db.flush()
    unlocked = achievements.evaluate(db, [donor, referrer] if first_donation and donor.referred_by else [donor])
    db.commit()
    donation_id = db.query(Donation.id).filter(Donation.request_id == req.id, Donation.donor_id == donor.id).scalar()
    threading.Thread(target=record_weather, args=(donation_id, req.city), daemon=True).start()

    if req.requester_telegram_id:
        requester = db.query(User).filter(User.telegram_id == req.requester_telegram_id).first()
        lang = req.requester_language or (requester.language if requester else None) or "en"
        contact = notifier.t(lang, "contact", phone=notifier.esc(donor.phone)) if donor.phone else ""
        notifier.notify_t(req.requester_telegram_id, lang, "donor_coming", name=notifier.esc(donor.name),
                          group=donor.blood_group, hospital=notifier.esc(req.hospital), contact=contact,
                          done=req.units_fulfilled, units=req.units_needed,
                          status=notifier.t(lang, f"st_{req.status}"))
    return {
        "status": "success",
        "message": f"Request {'fulfilled' if req.status == 'Fulfilled' else 'updated'}! "
                   f"Donor awarded {total} BLP.",
        "points_awarded": total,
        "breakdown": breakdown,
        "achievements": [achievements.public(a) for a in unlocked.get(donor.id, [])],
        "donor": user_private(db, donor),
        "request": request_out(req),
    }


def record_weather(donation_id: int, district: str) -> None:
    """Background: note whether it was raining (Rainmaker achievement). Never delays the donation response."""
    w = weather.current(district)
    if not w:
        return
    db = SessionLocal()
    try:
        d = db.get(Donation, donation_id)
        if d:
            d.weather = w
            db.flush()
            achievements.evaluate(db, [db.get(User, d.donor_id)])
            db.commit()
    except Exception:  # noqa: BLE001  (best effort)
        log.exception("recording weather failed")
    finally:
        db.close()


# ---------------------------------------------------------------- achievements
@app.get("/api/achievements")
def achievement_catalog(db: Session = Depends(get_db)):
    """Every achievement, with how many donors hold it (live rarity)."""
    counts, donors = achievements.unlock_counts(db)
    return {"donors": donors, "categories": achievements.CATEGORIES, "rarities": achievements.RARITIES,
            "achievements": [{**achievements.public(a), "unlocked_by": counts.get(a["key"], 0),
                              "percent_of_donors": round(100 * counts.get(a["key"], 0) / donors, 1) if donors else 0}
                             for a in achievements.CATALOG]}


def _collection(db: Session, user: User) -> dict:
    achievements.evaluate(db, [user])  # catches time-based unlocks such as The Constant
    db.commit()
    return achievements.collection(db, user)


@app.get("/api/users/{user_id}/achievements")
def user_achievements(user_id: int, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    user = find_user(db, user_id=user_id)
    auth.require_self(a, user)
    return _collection(db, user)


@app.get("/api/users/by-telegram/{telegram_id}/achievements")
def user_achievements_tg(telegram_id: str, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    auth.require_bot(a)
    return _collection(db, find_user(db, telegram_id=telegram_id))


@app.post("/api/users/{user_id}/achievements/seen")
def achievements_seen(user_id: int, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    user = find_user(db, user_id=user_id)
    auth.require_self(a, user)
    db.query(UserAchievement).filter(UserAchievement.user_id == user.id).update({"is_new": False})
    db.commit()
    return {"status": "success"}


# ---------------------------------------------------------------- rewards
@app.get("/api/rewards")
def rewards():
    return [{k: v for k, v in r.items() if k != "prefix"} for r in logic.REWARDS]


@app.post("/api/redeem/{reward_id}")
def redeem(reward_id: int, body: RedeemBody, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    reward = logic.get_reward(reward_id)
    if not reward:
        raise HTTPException(404, "Reward not found")
    user = find_user(db, user_id=body.user_id, telegram_id=body.telegram_id)
    auth.require_self(a, user)
    if user.points < reward["cost"]:
        raise HTTPException(400, f"Not enough BLP: {reward['name']} costs {reward['cost']}, you have {user.points}.")
    logic.award(db, user, -reward["cost"], f"Redeemed {reward['name']}")
    code = logic.voucher_code(reward["prefix"])
    db.add(Reward(user_id=user.id, reward_id=reward["id"], reward_name=reward["name"],
                  points_cost=reward["cost"], voucher_code=code))
    db.commit()
    notifier.notify_t(user.telegram_id, user.language, "redeemed", reward=notifier.esc(reward["name"]), code=code)
    return {"status": "success", "voucher_code": code, "reward": reward["name"],
            "points_remaining": user.points, "badge": user.badge}


@app.get("/api/activity/recent")
def recent_activity(limit: int = 8, db: Session = Depends(get_db)):
    """Latest pledges for the home page ticker (first name + initial only)."""
    rows = (db.query(Donation, BloodRequest, User).join(BloodRequest, Donation.request_id == BloodRequest.id)
            .join(User, Donation.donor_id == User.id).order_by(Donation.created_at.desc()).limit(min(limit, 20)).all())

    def short(name: str) -> str:
        parts = name.split()
        return f"{parts[0]} {parts[-1][0]}." if len(parts) > 1 else parts[0]

    return [{"name": short(u.name), "blood_group": u.blood_group, "hospital": r.hospital, "city": r.city,
             "badge": u.badge, "created_at": iso(d.created_at)} for d, r, u in rows]


# ---------------------------------------------------------------- public stats (home page)
@app.get("/api/stats")
def public_stats(db: Session = Depends(get_db)):
    s = _stats(db)
    return {"totals": {k: v for k, v in s["totals"].items() if k != "points_in_circulation"},
            "avg_response_minutes": s["avg_response_minutes"]}


# ---------------------------------------------------------------- admin (admin sign-in required)
@app.get("/api/admin/stats")
def admin_stats(db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    auth.require_admin(a)
    return _stats(db)


def _stats(db: Session) -> dict:
    def by_group(rows):
        d = dict(rows)
        return [{"blood_group": g, "count": d.get(g, 0)} for g in logic.BLOOD_GROUPS]

    demand = by_group(db.query(BloodRequest.blood_group, func.count(BloodRequest.id))
                      .group_by(BloodRequest.blood_group).all())
    supply = by_group(db.query(User.blood_group, func.count(User.id))
                      .filter(User.role == "donor", User.is_available.is_(True)).group_by(User.blood_group).all())
    cities = (db.query(BloodRequest.city, func.count(BloodRequest.id)).group_by(BloodRequest.city)
              .order_by(func.count(BloodRequest.id).desc()).limit(8).all())

    first_resp = dict(db.query(Donation.request_id, func.min(Donation.created_at)).group_by(Donation.request_id).all())
    reqs = db.query(BloodRequest).filter(BloodRequest.id.in_(first_resp.keys())).all() if first_resp else []
    minutes = [(first_resp[r.id] - r.created_at).total_seconds() / 60 for r in reqs if r.created_at]
    avg_resp = round(sum(minutes) / len(minutes), 1) if minutes else None

    recent = (db.query(PointLog, User).join(User, PointLog.user_id == User.id)
              .order_by(PointLog.id.desc()).limit(12).all())
    return {
        "totals": {
            "users": db.query(User).count(),
            "donors": db.query(User).filter(User.role == "donor").count(),
            "teams": db.query(community.Team).count(),
            "upcoming_camps": db.query(community.Camp).filter(community.Camp.status == "Upcoming").count(),
            "available_donors": db.query(User).filter(User.role == "donor", User.is_available.is_(True)).count(),
            "hospitals": db.query(User).filter(User.role == "hospital").count(),
            "telegram_linked": db.query(User).filter(User.telegram_id.isnot(None)).count(),
            "active_requests": db.query(BloodRequest).filter(BloodRequest.status == "Active").count(),
            "fulfilled_requests": db.query(BloodRequest).filter(BloodRequest.status == "Fulfilled").count(),
            "donations": db.query(Donation).count(),
            "referrals": db.query(Referral).count(),
            "vouchers_issued": db.query(Reward).count(),
            "points_in_circulation": db.query(func.coalesce(func.sum(User.points), 0)).scalar(),
        },
        "avg_response_minutes": avg_resp,
        "demand_by_blood_group": demand,
        "supply_by_blood_group": supply,
        "demand_by_city": [{"city": c, "count": n} for c, n in cities],
        "recent_activity": [{"name": u.name, "amount": l.amount, "reason": l.reason,
                             "created_at": iso(l.created_at)} for l, u in recent],
    }


@app.get("/api/admin/users")
def admin_users(db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    auth.require_admin(a)
    return [{**user_public(u), "phone": u.phone, "referral_code": u.referral_code}
            for u in db.query(User).order_by(User.id.desc()).all()]


@app.post("/api/admin/users/{user_id}/verify")
def admin_verify_user(user_id: int, verified: bool = True, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    auth.require_admin(a)
    user = find_user(db, user_id=user_id)
    user.is_verified = verified
    db.flush()
    achievements.evaluate(db, [user])
    db.commit()
    return user_public(user)


@app.post("/api/admin/reminders/run")
def admin_run_reminders(a: auth.Actor = Depends(auth.actor)):
    """Send any donation reminders that are due right now (they also run hourly in the background)."""
    auth.require_admin(a)
    return {"sent": reminders.run_once(), "telegram": notifier.enabled()}


@app.post("/api/admin/users/{user_id}/favorite")
def admin_favorite(user_id: int, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    """Award the hand-picked "Admin's Favorite" achievement."""
    auth.require_admin(a)
    user = find_user(db, user_id=user_id)
    if user.role != "donor":
        raise HTTPException(400, "Only donors can receive achievements")
    granted = achievements.grant(db, user, "admins_favorite")
    db.commit()
    return {"status": "success" if granted else "already_awarded", "user": user_public(user)}


@app.post("/api/admin/requests/{request_id}/verify")
def admin_verify_request(request_id: int, verified: bool = True, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    req = db.get(BloodRequest, request_id)
    if not req:
        raise HTTPException(404, "Request not found")
    _require_admin_or_hospital(a, req)
    req.is_verified = verified
    db.flush()
    donor_ids = [d for (d,) in db.query(Donation.donor_id).filter(Donation.request_id == req.id)]
    achievements.evaluate(db, db.query(User).filter(User.id.in_(donor_ids)).all() if donor_ids else [])
    db.commit()
    return request_out(req)


@app.post("/api/admin/requests/{request_id}/status")
def admin_set_status(request_id: int, status: str, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    req = db.get(BloodRequest, request_id)
    if not req:
        raise HTTPException(404, "Request not found")
    _require_admin_or_hospital(a, req)
    status = status.title()
    if status not in ("Active", "Fulfilled", "Cancelled"):
        raise HTTPException(400, "status must be Active, Fulfilled or Cancelled")
    req.status = status
    req.fulfilled_at = utcnow() if status == "Fulfilled" else None
    db.commit()
    return request_out(req)


@app.get("/api/admin/vouchers")
def admin_vouchers(db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    auth.require_admin(a)
    rows = db.query(Reward, User).join(User, Reward.user_id == User.id).order_by(Reward.id.desc()).all()
    return [{"id": r.id, "user": u.name, "reward_name": r.reward_name, "points_cost": r.points_cost,
             "voucher_code": r.voucher_code, "status": r.status, "created_at": iso(r.created_at)} for r, u in rows]


def _require_admin_or_hospital(a: auth.Actor, req: BloodRequest) -> None:
    """Admins manage every request; a hospital account manages requests at its own hospital."""
    if a.is_admin or (a.user and a.user.role == "hospital" and a.user.name.strip().lower() == req.hospital.strip().lower()):
        return
    auth.require_admin(a)


# ---------------------------------------------------------------- sign-in
class _Nonce(BaseModel):
    nonce: str


class _TelegramStart(BaseModel):
    purpose: str = "login"  # login | link


class _TelegramConfirm(BaseModel):
    nonce: str
    telegram_id: str
    telegram_username: str | None = None


class _Code(BaseModel):
    code: str


class _Password(BaseModel):
    password: str


@app.post("/api/auth/telegram/start")
def telegram_start(body: _TelegramStart, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    """Begin a Telegram login (or, when signed in, linking Telegram to this account)."""
    if not notifier.enabled():
        raise HTTPException(503, "Telegram login is not configured on this server.")
    purpose = "link" if body.purpose == "link" else "login"
    if purpose == "link" and not a.user:
        raise HTTPException(401, "Sign in first to link Telegram.")
    nonce = secrets.token_urlsafe(18)
    db.add(LoginRequest(nonce=nonce, purpose=purpose, user_id=a.user.id if purpose == "link" else None,
                        expires_at=utcnow() + timedelta(minutes=auth.LOGIN_MINUTES)))
    db.commit()
    return {"nonce": nonce, "url": f"https://t.me/{notifier.bot_username()}?start={purpose}_{nonce}",
            "expires_in": auth.LOGIN_MINUTES * 60}


@app.post("/api/auth/telegram/confirm")
def telegram_confirm(body: _TelegramConfirm, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    """Called by the bot when someone taps Start on a login/link link. Telegram vouches for telegram_id."""
    auth.require_bot(a)
    req = db.query(LoginRequest).filter(LoginRequest.nonce == body.nonce).first()
    if not req or req.expires_at < utcnow() or req.status != "pending":
        return {"status": "expired"}
    tid = str(body.telegram_id)
    if req.purpose == "link":
        owner = db.get(User, req.user_id)
        other = db.query(User).filter(User.telegram_id == tid, User.id != owner.id).first()
        if other:
            req.status = "taken"
            db.commit()
            return {"status": "taken", "name": other.name}
        owner.telegram_id, owner.telegram_username = tid, body.telegram_username
        req.status = "ok"
        db.commit()
        return {"status": "linked", "name": owner.name, "language": owner.language}
    user = db.query(User).filter(User.telegram_id == tid).first()
    if not user:
        req.status = "not_registered"
        db.commit()
        return {"status": "not_registered"}
    req.user_id, req.token, req.status = user.id, auth.new_session(db, user), "ok"
    db.commit()
    return {"status": "ok", "name": user.name, "language": user.language}


@app.get("/api/auth/telegram/poll/{nonce}")
def telegram_poll(nonce: str, db: Session = Depends(get_db)):
    """The browser waits here; the session token is handed over exactly once."""
    req = db.query(LoginRequest).filter(LoginRequest.nonce == nonce).first()
    if not req or req.expires_at < utcnow():
        return {"status": "expired"}
    if req.status == "ok" and req.purpose == "login" and req.token:
        token, user = req.token, db.get(User, req.user_id)
        db.delete(req)
        db.commit()
        return {"status": "ok", "token": token, "user": user_private(db, user)}
    if req.status == "ok" and req.purpose == "link":
        user = db.get(User, req.user_id)
        db.delete(req)
        db.commit()
        return {"status": "linked", "user": user_private(db, user)}
    return {"status": req.status}


@app.post("/api/auth/demo")
def demo_login(body: _Code, db: Session = Depends(get_db)):
    """Demo accounts (no Telegram) can be opened by code while DEMO_LOGIN=1. Real accounts must use Telegram."""
    if not auth.DEMO_LOGIN:
        raise HTTPException(403, "Demo sign-in is disabled. Use Telegram.")
    user = db.query(User).filter(func.upper(User.referral_code) == body.code.strip().upper()).first()
    if not user or not user.is_demo:  # real accounts (even web-only ones) can never be opened by their public code
        raise HTTPException(404, "No demo account with that code.")
    if user.telegram_id:
        raise HTTPException(403, "This account is linked to Telegram: please sign in with Telegram.")
    token = auth.new_session(db, user)
    db.commit()
    return {"token": token, "user": user_private(db, user)}


@app.post("/api/auth/admin")
def admin_login(body: _Password, db: Session = Depends(get_db)):
    if not auth.check_admin_password(body.password):
        raise HTTPException(401, "Wrong admin password." if auth.ADMIN_PASSWORD else "Admin password sign-in is not configured.")
    user = auth.admin_user(db)
    token = auth.new_session(db, user)
    db.commit()
    return {"token": token, "user": user_private(db, user)}


@app.get("/api/auth/me")
def me(db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    if not a.user:
        raise HTTPException(401, "Not signed in.")
    return user_private(db, a.user)


@app.post("/api/auth/logout")
def logout(db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    if a.token_hash:
        db.query(AuthSession).filter(AuthSession.token_hash == a.token_hash).delete()
        db.commit()
    return {"status": "success"}


# --- Production: serve the built React app (frontend/dist) from the same origin as the API ---
DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        if path.startswith("api/"):
            raise HTTPException(404, "Not found")
        file = (DIST / path).resolve()
        if path and file.is_file() and DIST in file.parents:
            return FileResponse(file)
        return FileResponse(DIST / "index.html")  # client-side routes like /sos, /profile
