"""Donation reminders on Telegram, timed to each donor's safe interval (90 days for men, 120 for women).

    soon      5 days before the donor is eligible again      "In 5 days you can donate again"
    eligible  on the day (sent up to 2 days late)           "You're eligible again!" [I'm available] [Later]
    nudge     7 days after becoming eligible, if they haven't donated since and are not marked available

Each reminder is sent at most once per donation cycle (ReminderLog is keyed by the donation date). A background thread
runs the check every hour; POST /api/admin/reminders/run triggers it on demand. Disable with REMINDERS=0.
"""

import logging
import math
import os
import threading
import time
from datetime import timedelta

import eligibility
import notifier
from database import SessionLocal
from sqlalchemy import or_

from models import BloodRequest, Camp, CampRSVP, Donation, PushSubscription, ReminderLog, User, utcnow

log = logging.getLogger("bloodlink.reminders")
ENABLED = os.getenv("REMINDERS", "1") == "1"
INTERVAL_SECONDS = 3600


def _last_hospital(db, user: User) -> str | None:
    row = (db.query(BloodRequest.hospital).join(Donation, Donation.request_id == BloodRequest.id)
           .filter(Donation.donor_id == user.id, Donation.status == "confirmed")
           .order_by(Donation.confirmed_at.desc()).first())
    return row[0] if row else None


def _last_hb(db, user: User) -> float | None:
    row = (db.query(Donation.hb_g_dl).filter(Donation.donor_id == user.id, Donation.hb_g_dl.isnot(None))
           .order_by(Donation.confirmed_at.desc()).first())
    return row[0] if row else None


def due(user: User, now) -> str | None:
    """Which reminder (if any) this donor should get now."""
    nxt = eligibility.next_eligible_at(user)
    if not nxt:
        return None
    if timedelta(0) < nxt - now <= timedelta(days=5):
        return "soon"
    if timedelta(0) <= now - nxt <= timedelta(days=2):
        return "eligible"
    if timedelta(days=7) <= now - nxt <= timedelta(days=9) and not user.is_available:
        return "nudge"
    return None


def run_once(send: bool = True) -> dict:
    """Send every reminder that is due. Returns counts per kind."""
    db = SessionLocal()
    sent = {"soon": 0, "eligible": 0, "nudge": 0}
    try:
        now = utcnow()
        window_start = now - timedelta(days=eligibility.DEFAULT_INTERVAL_DAYS + 10)
        pushed = db.query(PushSubscription.user_id).filter(PushSubscription.user_id.isnot(None))
        donors = (db.query(User).filter(User.role == "donor", or_(User.telegram_id.isnot(None), User.id.in_(pushed)),
                                        User.last_donation_at.isnot(None), User.last_donation_at >= window_start - timedelta(days=10))
                  .all())
        for u in donors:
            kind = due(u, now)
            if not kind:
                continue
            cycle = u.last_donation_at.date().isoformat()
            if db.query(ReminderLog).filter_by(user_id=u.id, kind=kind, cycle=cycle).first():
                continue
            db.add(ReminderLog(user_id=u.id, kind=kind, cycle=cycle, sent_at=now))
            db.commit()  # record first, so a crash never double-sends
            if send:
                _send(db, u, kind, now)
            sent[kind] += 1
    finally:
        db.close()
    sent.update(run_camps(send))
    if any(sent.values()):
        log.info("Reminders sent: %s", sent)
    return sent


def camp_due(camp: Camp, now) -> str | None:
    left = camp.starts_at - now
    if timedelta(days=2) < left <= timedelta(days=3):
        return "camp3"
    if timedelta(hours=6) < left <= timedelta(days=1):
        return "camp1"
    if timedelta(0) < left <= timedelta(hours=6):
        return "camp0"
    return None


def run_camps(send: bool = True) -> dict:
    """Remind registered donors 3 days before, the day before and on the day of a camp."""
    db = SessionLocal()
    sent = {"camp3": 0, "camp1": 0, "camp0": 0}
    try:
        now = utcnow()
        rows = (db.query(CampRSVP, Camp, User).join(Camp, CampRSVP.camp_id == Camp.id).join(User, CampRSVP.user_id == User.id)
                .filter(CampRSVP.status == "Registered", Camp.status == "Upcoming", Camp.starts_at > now,
                        Camp.starts_at <= now + timedelta(days=3), User.telegram_id.isnot(None)).all())
        for _r, camp, u in rows:
            kind = camp_due(camp, now)
            if not kind or db.query(ReminderLog).filter_by(user_id=u.id, kind=kind, cycle=str(camp.id)).first():
                continue
            db.add(ReminderLog(user_id=u.id, kind=kind, cycle=str(camp.id), sent_at=now))
            db.commit()
            if send:
                when = (camp.starts_at + timedelta(hours=5, minutes=30)).strftime("%d %b, %I:%M %p")
                notifier.notify(u.telegram_id, notifier.t(u.language, f"rem_{kind}", title=notifier.esc(camp.title),
                                                          venue=notifier.esc(camp.venue), when=when))
            sent[kind] += 1
    finally:
        db.close()
    return sent


def _send(db, u: User, kind: str, now) -> None:
    lang = u.language
    if kind == "soon":
        days = max(1, math.ceil((eligibility.next_eligible_at(u) - now).total_seconds() / 86400))
        hb = _last_hb(db, u)  # get ready for the haemoglobin check: stronger advice when the last reading was close
        tip = (notifier.t(lang, "rem_iron_borderline", hb=f"{hb:g}") if eligibility.hb_band(hb) in ("borderline", "low")
               else notifier.t(lang, "rem_iron"))
        notifier.tell_text(u, notifier.t(lang, "rem_soon", days=days) + tip, "/profile")
    elif kind == "eligible":
        hospital = _last_hospital(db, u)
        where = notifier.t(lang, "rem_where", hospital=notifier.esc(hospital)) if hospital else ""
        buttons = [[{"text": notifier.t(lang, "rem_available_btn"), "callback_data": "m_available"},
                    {"text": notifier.t(lang, "rem_later_btn"), "callback_data": "rem_later"}]]
        notifier.tell_text(u, notifier.t(lang, "rem_eligible", where=where), "/profile", buttons)
    else:
        buttons = [[{"text": notifier.t(lang, "rem_available_btn"), "callback_data": "m_available"}]]
        notifier.tell_text(u, notifier.t(lang, "rem_nudge"), "/profile", buttons)


def _loop() -> None:
    time.sleep(60)  # let the app finish starting
    while True:
        try:
            run_once()
        except Exception:  # noqa: BLE001  (keep the scheduler alive)
            log.exception("reminder run failed")
        time.sleep(INTERVAL_SECONDS)


def start() -> None:
    if ENABLED and notifier.enabled():
        threading.Thread(target=_loop, name="reminders", daemon=True).start()
        log.info("Donation reminders scheduled (hourly)")
