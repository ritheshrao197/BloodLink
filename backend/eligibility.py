"""Pre-donation self-screening, based on India's NBTC/DGHS whole-blood donor guidelines (simplified).

This is a *preliminary* check so donors don't make a wasted (or unsafe) trip. The hospital's own screening
(haemoglobin, blood pressure, history) is always final.

Rules
  * no permanent condition from PERMANENT (asked once, at registration or before the first pledge)
  * age 18-65, weight >= 45 kg
  * at least 90 days since the last whole-blood donation for men, 120 for women (and when sex is not recorded)
  * temporary deferrals from the questionnaire below, each with its own waiting period
"""

from datetime import date, datetime, timedelta

from models import User, utcnow

MIN_AGE, MAX_AGE = 18, 65
MIN_WEIGHT_KG = 45
MIN_HB_G_DL = 12.5  # measured by the hospital before every donation
BORDERLINE_HB_G_DL = 13.0  # at or below this the donor gets stronger iron advice
LOW_HB_PAUSE_DAYS = 30  # deferred for low haemoglobin: alerts pause, then they can try again
INTERVAL_DAYS = {"male": 90, "female": 120}
DEFAULT_INTERVAL_DAYS = 120  # sex not recorded: use the longer (safer) interval

# code -> (English question, waiting period in days, only asked for this sex or None)
QUESTIONS = {
    "fever": ("Fever, cold, cough or any infection in the last 2 weeks?", 14, None),
    "antibiotics": ("Taken antibiotics in the last 7 days?", 7, None),
    "alcohol": ("Had alcohol in the last 24 hours?", 1, None),
    "tattoo": ("Tattoo, piercing or acupuncture in the last 12 months?", 365, None),
    "surgery": ("Surgery or a hospital procedure in the last 6 months?", 180, None),
    "pregnancy": ("Pregnant, delivered a baby or breastfeeding in the last 12 months?", 365, "female"),
}


# Permanent deferrals: code -> (English label, short explanation). Only the outcome is stored, never the code.
PERMANENT = {
    "thalassaemia": ("Thalassaemia major or intermedia", "Carrying the thalassaemia trait (minor) is fine."),
    "sickle_cell": ("Sickle cell disease", "Carrying the sickle cell trait is fine."),
    "bleeding": ("Haemophilia or another bleeding disorder", "Donating can cause dangerous bleeding."),
    "hiv": ("HIV / AIDS", "Infections that blood can carry protect the patient by excluding the donor."),
    "hepatitis": ("Hepatitis B or C (ever)", "Even after treatment these can pass through blood."),
    "heart": ("Heart disease: heart attack, angina or heart surgery", "Donating strains the heart."),
    "cancer": ("Cancer (now or in the past)", "Blood cancers and most other cancers rule out donation."),
    "epilepsy": ("Epilepsy or fits on treatment", "Donating can trigger a seizure."),
    "kidney_liver": ("Chronic kidney or liver disease", "These organs need the blood more than the patient does."),
    "insulin_diabetes": ("Diabetes treated with insulin", "Diabetes controlled by tablets or diet is fine."),
}


def hb_band(hb: float | None) -> str | None:
    """good (> 13), borderline (12.5-13) or low (< 12.5); None without a reading."""
    if hb is None:
        return None
    if hb < MIN_HB_G_DL:
        return "low"
    return "borderline" if hb <= BORDERLINE_HB_G_DL else "good"


def needs_screening(user: User) -> bool:
    return (user.role or "donor") == "donor" and user.screened_at is None


def apply_screening(user: User, conditions: list[str], now: datetime | None = None) -> None:
    """Record the permanent-conditions answer (caller validates codes and commits). The codes are not kept."""
    user.screened_at = now or utcnow()
    user.permanently_ineligible = bool(conditions)
    if user.permanently_ineligible:
        user.is_available = False


def interval_days(user: User) -> int:
    return INTERVAL_DAYS.get(user.sex or "", DEFAULT_INTERVAL_DAYS)


def next_eligible_at(user: User) -> datetime | None:
    """When the donation interval ends (None = no previous donation)."""
    if not user.last_donation_at:
        return None
    return user.last_donation_at + timedelta(days=interval_days(user))


def clear_demo_intervals(db, now: datetime | None = None) -> int:
    """Demo (test) accounts inside their 90/120-day gap get their last donation moved back to just past it, so every
    demo account can donate right away. Only the clock is reset: donation history, points and achievements stay.
    Runs at startup; a test donation made afterwards starts the normal gap again. Real accounts are never touched."""
    now = now or utcnow()
    cleared = 0
    for u in db.query(User).filter(User.is_demo.is_(True), User.last_donation_at.isnot(None)).all():
        gap = timedelta(days=interval_days(u))
        if now - u.last_donation_at < gap:
            u.last_donation_at = now - gap - timedelta(days=1)
            cleared += 1
    db.commit()
    return cleared


def age_on(dob: date, today: date) -> int:
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def iso(dt):
    return dt.isoformat() + "Z" if isinstance(dt, datetime) else (dt.isoformat() if dt else None)


def status(user: User, now: datetime | None = None) -> dict:
    """Eligibility from what we already know about the donor (no questionnaire)."""
    now = now or utcnow()
    reasons = []
    if user.permanently_ineligible:
        reasons.append({"code": "permanent", "until": None})
    elif needs_screening(user):
        reasons.append({"code": "screening", "until": None})
    nxt = next_eligible_at(user)
    if nxt and nxt > now:
        reasons.append({"code": "interval", "until": iso(nxt), "days": interval_days(user)})
    if user.deferred_until and user.deferred_until > now:
        reasons.append({"code": "deferred", "until": iso(user.deferred_until)})
    if user.date_of_birth:
        age = age_on(user.date_of_birth, now.date())
        if age < MIN_AGE:
            until = user.date_of_birth.replace(year=user.date_of_birth.year + MIN_AGE)
            reasons.append({"code": "too_young", "until": iso(until)})
        elif age > MAX_AGE:
            reasons.append({"code": "too_old", "until": None})
    if user.weight_kg is not None and user.weight_kg < MIN_WEIGHT_KG:
        reasons.append({"code": "underweight", "until": None})
    return {
        "eligible": not reasons,
        "reasons": reasons,
        "next_eligible_at": iso(nxt),
        "interval_days": interval_days(user),
        "deferred_until": iso(user.deferred_until),
        "profile_complete": bool(user.sex and user.date_of_birth and user.weight_kg),
        "screened": not needs_screening(user),
        "permanently_ineligible": bool(user.permanently_ineligible),
        "profile": {"sex": user.sex, "date_of_birth": iso(user.date_of_birth), "weight_kg": user.weight_kg},
    }


def check(user: User, screening: dict | None, now: datetime | None = None) -> dict:
    """Full check: known facts + today's answers. Records any new deferral on the user (caller commits)."""
    now = now or utcnow()
    result = status(user, now)
    screening = screening or {}
    answers = screening.get("answers") or {}
    if not result["profile_complete"] and not screening.get("basics_confirmed"):
        result["reasons"].append({"code": "basics", "until": None})
    deferral_end = None
    for code, (_text, days, only_sex) in QUESTIONS.items():
        if only_sex and user.sex and user.sex != only_sex:
            continue
        if answers.get(code):
            until = now + timedelta(days=days)
            result["reasons"].append({"code": code, "until": iso(until)})
            deferral_end = max(deferral_end or until, until)
    if deferral_end and deferral_end - now > timedelta(days=1):
        # remember longer deferrals so SOS alerts skip this donor until then (they can undo it on their profile)
        user.deferred_until = max(user.deferred_until or deferral_end, deferral_end)
        result["deferred_until"] = iso(user.deferred_until)
    result["eligible"] = not result["reasons"]
    return result


def can_be_alerted(user: User, now: datetime) -> bool:
    """Used by SOS matching: skip donors still inside their interval or a self-reported deferral."""
    if user.permanently_ineligible:
        return False
    nxt = next_eligible_at(user)
    if nxt and nxt > now:
        return False
    if user.deferred_until and user.deferred_until > now:
        return False
    if user.weight_kg is not None and user.weight_kg < MIN_WEIGHT_KG:
        return False
    if user.date_of_birth and not MIN_AGE <= age_on(user.date_of_birth, now.date()) <= MAX_AGE:
        return False
    return True


def permanent_list() -> list[dict]:
    return [{"code": c, "text": label, "detail": detail} for c, (label, detail) in PERMANENT.items()]


def questions_for(sex: str | None) -> list[dict]:
    return [{"code": c, "text": q, "days": d} for c, (q, d, only) in QUESTIONS.items() if not only or not sex or sex == only]


def parse_dob(value) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])
