import logging
import os
from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, inspect, text
from sqlalchemy.orm import Session

import database  # noqa: F401  (loads .env before notifier reads the token)
from database import Base, SessionLocal, engine, get_db
import locations
import logic
import notifier
from models import BloodRequest, Donation, PointLog, Referral, Reward, User, utcnow
from schemas import (AvailabilityBody, DonateBody, LanguageBody, LinkTelegramBody, RedeemBody, SOSCreate,
                     UserCreate)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("bloodlink")


def migrate() -> None:
    """Add columns introduced after v2.0 to existing SQLite files and map old city names to districts."""
    new_columns = {"users": {"state": "VARCHAR", "language": "VARCHAR DEFAULT 'en'"},
                   "requests": {"state": "VARCHAR", "requester_language": "VARCHAR"}}
    insp = inspect(engine)
    with engine.begin() as conn:
        for table, cols in new_columns.items():
            existing = {c["name"] for c in insp.get_columns(table)}
            for name, ddl in cols.items():
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))
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
            if db.query(User).count() == 0:
                from seed_data import seed

                seed(db)
                log.info("Empty database: inserted demo seed data (set AUTO_SEED=0 to disable)")
        finally:
            db.close()
    log.info("Telegram notifications %s", "ENABLED" if notifier.enabled() else "DISABLED (no TELEGRAM_BOT_TOKEN)")
    yield


app = FastAPI(title="BLOODLINK API", version="2.0", lifespan=lifespan)
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
        "telegram_link_url": f"https://t.me/{bot}?start=link_{u.referral_code}",
        "referrals": stats,
    }


def request_out(r: BloodRequest) -> dict:
    return {
        "id": r.id, "requester_name": r.requester_name, "blood_group": r.blood_group,
        "hospital": r.hospital, "city": r.city, "state": r.state, "units_needed": r.units_needed,
        "units_fulfilled": r.units_fulfilled, "urgency": r.urgency, "status": r.status,
        "fulfilled_by": r.fulfilled_by, "is_verified": r.is_verified,
        "notified_count": r.notified_count, "contact_phone": r.contact_phone,
        "compatible_donor_groups": logic.compatible_donor_groups(r.blood_group),
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
def config():
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
def register_user(body: UserCreate, db: Session = Depends(get_db)):
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
    db.commit()
    db.refresh(user)
    return {"status": "success", "user_id": user.id, "referral_code": user.referral_code,
            "points": user.points, "user": user_private(db, user)}


@app.get("/api/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return user_private(db, find_user(db, user_id=user_id))


@app.get("/api/users/by-code/{code}")
def get_user_by_code(code: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.upper(User.referral_code) == code.strip().upper()).first()
    if not user:
        raise HTTPException(404, "No user with that code")
    return user_private(db, user)


@app.get("/api/users/by-telegram/{telegram_id}")
def get_user_by_telegram(telegram_id: str, db: Session = Depends(get_db)):
    return user_private(db, find_user(db, telegram_id=telegram_id))


@app.get("/api/users/{user_id}/activity")
def user_activity(user_id: int, db: Session = Depends(get_db)):
    user = find_user(db, user_id=user_id)
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


@app.post("/api/users/link-telegram")
def link_telegram(body: LinkTelegramBody, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.upper(User.referral_code) == body.referral_code.strip().upper()).first()
    if not user:
        raise HTTPException(404, "No account with that code")
    other = db.query(User).filter(User.telegram_id == body.telegram_id, User.id != user.id).first()
    if other:
        raise HTTPException(409, f"This Telegram account is already linked to {other.name}.")
    user.telegram_id = body.telegram_id
    user.telegram_username = body.telegram_username
    db.commit()
    return {"status": "success", "user": user_private(db, user)}


@app.patch("/api/users/{user_id}/availability")
def set_availability(user_id: int, body: AvailabilityBody, db: Session = Depends(get_db)):
    user = find_user(db, user_id=user_id)
    user.is_available = body.is_available
    db.commit()
    return user_private(db, user)


@app.patch("/api/users/by-telegram/{telegram_id}/availability")
def set_availability_tg(telegram_id: str, body: AvailabilityBody, db: Session = Depends(get_db)):
    user = find_user(db, telegram_id=telegram_id)
    user.is_available = body.is_available
    db.commit()
    return user_private(db, user)


@app.patch("/api/users/by-telegram/{telegram_id}/language")
def set_language_tg(telegram_id: str, body: LanguageBody, db: Session = Depends(get_db)):
    user = find_user(db, telegram_id=telegram_id)
    user.language = body.language
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
    users = db.query(User).order_by(User.points.desc(), User.id).limit(min(limit, 100)).all()
    counts = dict(
        db.query(Referral.referrer_id, func.count(Referral.id)).group_by(Referral.referrer_id).all()
    )
    return [
        {"id": u.id, "name": u.name, "points": u.points, "badge": u.badge, "blood_group": u.blood_group,
         "city": u.city, "total_donations": u.total_donations, "referrals": counts.get(u.id, 0),
         "influencer": counts.get(u.id, 0) >= logic.INFLUENCER_REFERRALS}
        for u in users
    ]


# ---------------------------------------------------------------- requests / SOS
def matching_donors(db: Session, req: BloodRequest) -> list[User]:
    groups = logic.compatible_donor_groups(req.blood_group)
    base = db.query(User).filter(User.role == "donor", User.is_available.is_(True), User.blood_group.in_(groups))
    if req.requester_telegram_id:
        base = base.filter((User.telegram_id.is_(None)) | (User.telegram_id != req.requester_telegram_id))
    local = base.filter(func.lower(User.city) == req.city.lower()).all()
    return local or base.all()  # fall back to all cities when nobody local matches


def _broadcast(request_id: int):
    db = SessionLocal()
    try:
        req = db.get(BloodRequest, request_id)
        donors = [{"telegram_id": d.telegram_id, "language": d.language}
                  for d in matching_donors(db, req) if d.telegram_id]
        req.notified_count = notifier.broadcast_sos(request_out(req), donors)
        db.commit()
        log.info("SOS #%s broadcast to %s/%s Telegram donors", request_id, req.notified_count, len(donors))
    finally:
        db.close()


@app.post("/api/sos")
def create_sos(body: SOSCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    req = BloodRequest(**body.model_dump())
    req.state, req.city = locations.normalize(body.city, body.state)
    db.add(req)
    db.commit()
    db.refresh(req)
    donors = matching_donors(db, req)
    background_tasks.add_task(_broadcast, req.id)
    return {
        "status": "broadcasted",
        "request_id": req.id,
        "matched_donors": len(donors),
        "telegram_reachable": sum(1 for d in donors if d.telegram_id),
        "donors": [user_public(d) for d in donors[:20]],
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
def donate(request_id: int, body: DonateBody, db: Session = Depends(get_db)):
    if not body.confirmed:
        raise HTTPException(400, "Please confirm this donation is real.")
    req = db.get(BloodRequest, request_id)
    if not req:
        raise HTTPException(404, "Request not found")
    if req.status != "Active":
        raise HTTPException(400, f"This request is already {req.status.lower()}. Thank you anyway! 🙏")
    donor = find_user(db, user_id=body.user_id, telegram_id=body.donor_telegram_id)
    if not logic.can_donate(donor.blood_group, req.blood_group):
        raise HTTPException(400, f"{donor.blood_group} cannot donate to a {req.blood_group} patient. "
                                 f"Compatible groups: {', '.join(logic.compatible_donor_groups(req.blood_group))}.")
    if db.query(Donation).filter(Donation.request_id == req.id, Donation.donor_id == donor.id).first():
        raise HTTPException(400, "You have already responded to this request.")

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
    db.commit()

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
        "donor": user_private(db, donor),
        "request": request_out(req),
    }


# ---------------------------------------------------------------- rewards
@app.get("/api/rewards")
def rewards():
    return [{k: v for k, v in r.items() if k != "prefix"} for r in logic.REWARDS]


@app.post("/api/redeem/{reward_id}")
def redeem(reward_id: int, body: RedeemBody, db: Session = Depends(get_db)):
    reward = logic.get_reward(reward_id)
    if not reward:
        raise HTTPException(404, "Reward not found")
    user = find_user(db, user_id=body.user_id, telegram_id=body.telegram_id)
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


# ---------------------------------------------------------------- admin (no auth in hackathon build)
@app.get("/api/admin/stats")
def admin_stats(db: Session = Depends(get_db)):
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
def admin_users(db: Session = Depends(get_db)):
    return [{**user_public(u), "phone": u.phone, "referral_code": u.referral_code}
            for u in db.query(User).order_by(User.id.desc()).all()]


@app.post("/api/admin/users/{user_id}/verify")
def admin_verify_user(user_id: int, verified: bool = True, db: Session = Depends(get_db)):
    user = find_user(db, user_id=user_id)
    user.is_verified = verified
    db.commit()
    return user_public(user)


@app.post("/api/admin/requests/{request_id}/verify")
def admin_verify_request(request_id: int, verified: bool = True, db: Session = Depends(get_db)):
    req = db.get(BloodRequest, request_id)
    if not req:
        raise HTTPException(404, "Request not found")
    req.is_verified = verified
    db.commit()
    return request_out(req)


@app.post("/api/admin/requests/{request_id}/status")
def admin_set_status(request_id: int, status: str, db: Session = Depends(get_db)):
    req = db.get(BloodRequest, request_id)
    if not req:
        raise HTTPException(404, "Request not found")
    status = status.title()
    if status not in ("Active", "Fulfilled", "Cancelled"):
        raise HTTPException(400, "status must be Active, Fulfilled or Cancelled")
    req.status = status
    req.fulfilled_at = utcnow() if status == "Fulfilled" else None
    db.commit()
    return request_out(req)


@app.get("/api/admin/vouchers")
def admin_vouchers(db: Session = Depends(get_db)):
    rows = db.query(Reward, User).join(User, Reward.user_id == User.id).order_by(Reward.id.desc()).all()
    return [{"id": r.id, "user": u.name, "reward_name": r.reward_name, "points_cost": r.points_cost,
             "voucher_code": r.voucher_code, "status": r.status, "created_at": iso(r.created_at)} for r, u in rows]
