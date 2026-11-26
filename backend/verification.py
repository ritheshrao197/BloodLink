"""Staff-verified donations. A donor's "I can donate" is a pledge; hospital or blood bank staff confirm it.

States: pledged -> confirmed | no_show | expired | deferred_hb (all final). deferred_hb: the donor came but their
haemoglobin was too low to donate; no points and not a no-show, and alerts pause for LOW_HB_PAUSE_DAYS. Points, the next eligible date and the request's units
change only on confirmation. A pledge nobody confirms within PLEDGE_HOURS expires and counts as a no-show; every
NO_SHOW_LIMIT-th no-show pauses new pledges for BLOCK_DAYS.

Who confirms: an admin; the hospital account named on the request; any blood bank in the request's district.
Hospital and blood bank accounts must be verified by an admin first (anyone can register one under any name).
"""

import logging
import threading
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

import achievements
import auth
import eligibility
import logic
import notifier
import push
import weather
from database import SessionLocal, get_db
from models import BloodRequest, Donation, Referral, Reward, User, utcnow

log = logging.getLogger("bloodlink.verification")

PLEDGE_HOURS = 24
NO_SHOW_LIMIT = 3
BLOCK_DAYS = 30
STAFF_ROLES = ("hospital", "blood_bank")

router = APIRouter()


def iso(dt):
    return dt.isoformat() + "Z" if dt else None


def _same(a: str | None, b: str | None) -> bool:
    return (a or "").strip().lower() == (b or "").strip().lower()


def covers(staff: User, req: BloodRequest) -> bool:
    """May this account confirm pledges for this request?"""
    if staff.is_admin:
        return True
    if staff.role == "hospital":
        return _same(staff.name, req.hospital)
    if staff.role == "blood_bank":  # district names repeat across states, so match the state too when both are known
        return _same(staff.city, req.city) and (not staff.state or not req.state or _same(staff.state, req.state))
    return False


def staff_for(db: Session, req: BloodRequest) -> list[User]:
    """Hospital and blood bank accounts that cover this request (admins are not alerted)."""
    rows = db.query(User).filter(User.role.in_(STAFF_ROLES), or_(
        func.lower(User.name) == req.hospital.strip().lower(), func.lower(User.city) == (req.city or "").lower())).all()
    return [u for u in rows if covers(u, req)]


def breakdown(req: BloodRequest, donor: User, pledged_at: datetime, confirmed_at: datetime) -> list[dict]:
    """Points for a donation: the base, the quick bonus (judged by the pledge time) and the 3-month streak bonus."""
    items = [{"code": "donation", "reason": "Successful donation", "points": logic.POINTS_DONATION}]
    if req.created_at and pledged_at - req.created_at <= timedelta(minutes=logic.QUICK_RESPONSE_MINUTES):
        items.append({"code": "quick", "reason": "Quick response (< 5 min)", "points": logic.POINTS_QUICK_RESPONSE})
    if donor.last_donation_at and confirmed_at - donor.last_donation_at >= timedelta(days=logic.STREAK_DAYS):
        items.append({"code": "streak", "reason": "Streak bonus (3-month return)", "points": logic.POINTS_STREAK})
    return items


def pledge_problem(db: Session, donor: User, now: datetime) -> str | None:
    """Why this donor can't pledge right now (None = they can)."""
    if donor.pledge_blocked_until and donor.pledge_blocked_until > now:
        return (f"Pledging is paused until {donor.pledge_blocked_until:%d %b %Y} because {NO_SHOW_LIMIT} pledges "
                "were never confirmed by a hospital.")
    open_pledge = db.query(Donation).filter(Donation.donor_id == donor.id, Donation.status == "pledged").first()
    if open_pledge:
        return (f"You already have an open pledge for request #{open_pledge.request_id}. "
                "Please donate there first, or wait for it to expire.")
    return None


def pledge(db: Session, req: BloodRequest, donor: User, now: datetime) -> Donation:
    """Record the pledge and alert the staff who can confirm it. Caller commits."""
    quick = bool(req.created_at and now - req.created_at <= timedelta(minutes=logic.QUICK_RESPONSE_MINUTES))
    d = Donation(request_id=req.id, donor_id=donor.id, status="pledged", points_awarded=0, quick_response=quick,
                 created_at=now)
    db.add(d)
    db.flush()
    for s in staff_for(db, req):
        lang = s.language or "en"
        phone = f"\n📞 {notifier.esc(donor.phone)}" if donor.phone else ""
        text = notifier.t(lang, "staff_pledge", id=req.id, name=notifier.esc(donor.name), group=donor.blood_group,
                          phone=phone, hospital=notifier.esc(req.hospital), city=notifier.esc(req.city), hours=PLEDGE_HOURS)
        notifier.tell_text(s, text, "/staff", [[
            {"text": notifier.t(lang, "staff_done_btn"), "callback_data": f"pok_{d.id}"},
            {"text": notifier.t(lang, "staff_noshow_btn"), "callback_data": f"pns_{d.id}"},
            {"text": notifier.t(lang, "staff_lowhb_btn"), "callback_data": f"phb_{d.id}"}]])
    return d


def _referral_payout(db: Session, donor: User) -> User | None:
    """The referrer earns +200 BLP and a voucher on their friend's first confirmed donation."""
    if not donor.referred_by:
        return None
    referrer = db.query(User).filter(User.referral_code == donor.referred_by).first()
    if not referrer:
        return None
    logic.award(db, referrer, logic.POINTS_REFERRAL_DONATION, f"Referral: {donor.name} donated")
    code = logic.voucher_code(logic.REFERRAL_VOUCHER["prefix"])
    db.add(Reward(user_id=referrer.id, reward_name=logic.REFERRAL_VOUCHER["name"], points_cost=0, voucher_code=code))
    ref = db.query(Referral).filter(Referral.referrer_id == referrer.id, Referral.referred_id == donor.id).first()
    if ref:
        ref.status = "Donated"
        ref.points_awarded = (ref.points_awarded or 0) + logic.POINTS_REFERRAL_DONATION
    notifier.tell(referrer, "ref_donated", "/profile",
                      name=notifier.esc(donor.name), points=logic.POINTS_REFERRAL_DONATION, code=code)
    return referrer


def confirm(db: Session, d: Donation, staff: User | None, hb_g_dl: float | None, now: datetime) -> dict:
    """Staff saw the donation happen: award points, start the donor's interval, count the unit. Caller commits."""
    req = db.get(BloodRequest, d.request_id)
    donor = db.get(User, d.donor_id)
    items = breakdown(req, donor, d.created_at, now)
    first_donation = (donor.total_donations or 0) == 0
    for item in items:
        logic.award(db, donor, item["points"], f"{item['reason']} — request #{req.id}")
    total = sum(i["points"] for i in items)
    d.status, d.confirmed_at, d.points_awarded, d.hb_g_dl = "confirmed", now, total, hb_g_dl
    d.confirmed_by = staff.id if staff else None
    donor.total_donations = (donor.total_donations or 0) + 1
    donor.last_donation_at = now
    req.units_fulfilled = (req.units_fulfilled or 0) + 1
    req.fulfilled_by = f"{req.fulfilled_by}, {donor.name}" if req.fulfilled_by else donor.name
    if req.status == "Active" and req.units_fulfilled >= req.units_needed:
        req.status, req.fulfilled_at = "Fulfilled", now
    referrer = _referral_payout(db, donor) if first_donation else None
    db.flush()
    unlocked = achievements.evaluate(db, [donor, referrer] if referrer else [donor])
    nxt = eligibility.next_eligible_at(donor)
    lang = donor.language
    text = notifier.t(lang, "pledge_confirmed", hospital=notifier.esc(req.hospital), points=total,
                      balance=donor.points, next=f"{nxt:%d %b %Y}" if nxt else "—")
    if hb_g_dl is not None:
        mark = "✅" if eligibility.hb_band(hb_g_dl) == "good" else "⚠️"
        text += "\n\n" + notifier.t(lang, "hb_after", hb=f"{hb_g_dl:g}", mark=mark)
    notifier.tell_text(donor, text, "/profile")
    return {"points": total, "breakdown": items, "achievements": unlocked.get(donor.id, [])}


def defer_low_hb(db: Session, d: Donation, staff: User | None, hb_g_dl: float | None, now: datetime) -> None:
    """The donor came but their haemoglobin was below the minimum: pause them and send advice. Caller commits."""
    req = db.get(BloodRequest, d.request_id)
    donor = db.get(User, d.donor_id)
    d.status, d.hb_g_dl, d.confirmed_at = "deferred_hb", hb_g_dl, now
    d.confirmed_by = staff.id if staff else None
    until = now + timedelta(days=eligibility.LOW_HB_PAUSE_DAYS)
    donor.deferred_until = max(donor.deferred_until or until, until)
    lang = donor.language
    reading = (notifier.t(lang, "hb_low_value", hb=f"{hb_g_dl:g}") if hb_g_dl is not None
               else notifier.t(lang, "hb_low_novalue"))
    notifier.tell(donor, "hb_low", "/profile", reading=reading, until=f"{until:%d %b %Y}")
    log.info("Pledge %s at %s: deferred for low haemoglobin", d.id, req.hospital)


def miss(db: Session, d: Donation, status: str, now: datetime) -> None:
    """The donor never showed (status "no_show") or nobody confirmed in time ("expired"). Caller commits."""
    req = db.get(BloodRequest, d.request_id)
    donor = db.get(User, d.donor_id)
    d.status = status
    donor.no_show_count = (donor.no_show_count or 0) + 1
    blocked = ""
    if donor.no_show_count % NO_SHOW_LIMIT == 0:
        donor.pledge_blocked_until = now + timedelta(days=BLOCK_DAYS)
        blocked = notifier.t(donor.language, "pledge_blocked", n=NO_SHOW_LIMIT,
                             until=f"{donor.pledge_blocked_until:%d %b %Y}")
    notifier.tell(donor, "pledge_missed", "/profile", hospital=notifier.esc(req.hospital),
                      blocked=blocked)


def expire_once(now: datetime | None = None) -> int:
    """Expire pledges that no staff member confirmed within PLEDGE_HOURS. Returns how many expired."""
    now = now or utcnow()
    db = SessionLocal()
    try:
        stale = db.query(Donation).filter(Donation.status == "pledged",
                                          Donation.created_at <= now - timedelta(hours=PLEDGE_HOURS)).all()
        for d in stale:
            miss(db, d, "expired", now)
        db.commit()
        if stale:
            log.info("Expired %d unconfirmed pledge(s)", len(stale))
        return len(stale)
    finally:
        db.close()


def record_weather(donation_id: int, district: str) -> None:
    """Background: note whether it was raining (Rainmaker achievement). Never delays the response."""
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


# ---------------------------------------------------------------- staff API
class StaffBody(BaseModel):
    staff_telegram_id: str | None = None  # set by the bot when staff tap a button on Telegram


class ConfirmBody(StaffBody):
    hb_g_dl: float | None = Field(default=None, ge=4, le=25)


class LowHbBody(StaffBody):
    hb_g_dl: float | None = Field(default=None, ge=4, lt=eligibility.MIN_HB_G_DL)  # optional: the bot button sends none


NOT_VERIFIED = "Your hospital or blood bank account is waiting to be verified by BloodLink before it can confirm donations."


def _staff(db: Session, a: auth.Actor, telegram_id: str | None) -> User:
    if a.is_bot:
        user = db.query(User).filter(User.telegram_id == str(telegram_id)).first() if telegram_id else None
        if not user or not (user.is_admin or user.role in STAFF_ROLES):
            raise HTTPException(403, "This Telegram account is not a hospital or blood bank account.")
    else:
        if not a.user:
            raise HTTPException(401, "Please sign in.")
        user = a.user
        if not (user.is_admin or user.role in STAFF_ROLES):
            raise HTTPException(403, "Only hospital and blood bank staff can confirm donations.")
    if not user.is_admin and not user.is_verified:
        raise HTTPException(403, NOT_VERIFIED)
    return user


def _open_pledge(db: Session, donation_id: int, staff: User) -> Donation:
    d = db.get(Donation, donation_id)
    if not d:
        raise HTTPException(404, "Pledge not found")
    if d.donor_id == staff.id:
        raise HTTPException(403, "You can't confirm your own donation.")
    if not covers(staff, db.get(BloodRequest, d.request_id)):
        raise HTTPException(403, "This pledge is for another hospital or district.")
    if d.status != "pledged":
        raise HTTPException(409, f"This pledge is already {d.status.replace('_', ' ')}.")
    return d


@router.get("/api/staff/pledges")
def staff_pledges(db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    staff = _staff(db, a, None)
    rows = (db.query(Donation, BloodRequest, User).join(BloodRequest, Donation.request_id == BloodRequest.id)
            .join(User, Donation.donor_id == User.id).filter(Donation.status == "pledged")
            .order_by(Donation.created_at).all())
    return [{
        "donation_id": d.id, "pledged_at": iso(d.created_at),
        "expires_at": iso(d.created_at + timedelta(hours=PLEDGE_HOURS)),
        "donor": {"id": u.id, "name": u.name, "blood_group": u.blood_group, "phone": u.phone},
        "ride_help": d.ride_help_at is not None,
        "request": {"id": r.id, "hospital": r.hospital, "city": r.city, "blood_group": r.blood_group,
                    "urgency": r.urgency, "status": r.status, "units_needed": r.units_needed,
                    "units_fulfilled": r.units_fulfilled},
    } for d, r, u in rows if covers(staff, r) and u.id != staff.id]


@router.post("/api/staff/pledges/{donation_id}/confirm")
def staff_confirm(donation_id: int, body: ConfirmBody, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    staff = _staff(db, a, body.staff_telegram_id)
    d = _open_pledge(db, donation_id, staff)
    if body.hb_g_dl is not None and body.hb_g_dl < eligibility.MIN_HB_G_DL:
        raise HTTPException(422, f"Haemoglobin below {eligibility.MIN_HB_G_DL:g} g/dL: use 'Low Hb' instead of confirming.")
    result = confirm(db, d, staff, body.hb_g_dl, utcnow())
    db.commit()
    req = db.get(BloodRequest, d.request_id)
    threading.Thread(target=record_weather, args=(d.id, req.city), daemon=True).start()
    donor = db.get(User, d.donor_id)
    return {"status": "confirmed", "points_awarded": result["points"], "donor_name": donor.name,
            "next_eligible_at": iso(eligibility.next_eligible_at(donor))}


@router.post("/api/staff/pledges/{donation_id}/low-hb")
def staff_low_hb(donation_id: int, body: LowHbBody, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    staff = _staff(db, a, body.staff_telegram_id)
    d = _open_pledge(db, donation_id, staff)
    defer_low_hb(db, d, staff, body.hb_g_dl, utcnow())
    db.commit()
    donor = db.get(User, d.donor_id)
    return {"status": "deferred_hb", "donor_name": donor.name, "deferred_until": iso(donor.deferred_until)}


class RideHelpBody(BaseModel):
    donor_telegram_id: str | None = None  # set by the bot


@router.post("/api/pledges/{donation_id}/ride-help")
def ride_help(donation_id: int, body: RideHelpBody, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    """The donor pledged but needs help getting to the hospital: alert the requester and the covering staff once."""
    d = db.get(Donation, donation_id)
    if not d:
        raise HTTPException(404, "Pledge not found")
    donor = db.get(User, d.donor_id)
    if a.is_bot:
        if not body.donor_telegram_id or body.donor_telegram_id != donor.telegram_id:
            raise HTTPException(403, "Not your pledge.")
    else:
        auth.require_self(a, donor)
    if d.status != "pledged":
        raise HTTPException(409, "This pledge is no longer open.")
    if d.ride_help_at:
        return {"status": "already_requested", "notified": 0, "phone": donor.phone}
    d.ride_help_at = utcnow()
    req = db.get(BloodRequest, d.request_id)
    phone = f"\n📞 {notifier.esc(donor.phone)}" if donor.phone else ""
    words = dict(name=notifier.esc(donor.name), group=donor.blood_group, id=req.id, hospital=notifier.esc(req.hospital),
                 area=notifier.esc(donor.city), phone=phone)
    notified = 0
    if req.requester_telegram_id and req.requester_telegram_id != donor.telegram_id:
        notifier.notify_t(req.requester_telegram_id, req.requester_language or "en", "ride_help", **words)
        notified += 1
    push.to_request(req.id, notifier.t(req.requester_language or "en", "ride_help", **words), "/")
    for s in staff_for(db, req):
        if s.id != donor.id:
            notifier.tell(s, "ride_help", "/staff", **words)
            notified += 1
    db.commit()
    return {"status": "requested", "notified": notified, "phone": donor.phone}


@router.post("/api/staff/pledges/{donation_id}/no-show")
def staff_no_show(donation_id: int, body: StaffBody, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    staff = _staff(db, a, body.staff_telegram_id)
    d = _open_pledge(db, donation_id, staff)
    miss(db, d, "no_show", utcnow())
    db.commit()
    donor = db.get(User, d.donor_id)
    return {"status": "no_show", "no_show_count": donor.no_show_count,
            "pledge_blocked_until": iso(donor.pledge_blocked_until)}
