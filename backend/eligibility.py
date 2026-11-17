"""Pre-donation self-screening, based on India's NBTC/DGHS whole-blood donor guidelines (simplified).

This is a *preliminary* check so donors don't make a wasted (or unsafe) trip. The hospital's own screening
(haemoglobin, blood pressure, history) is always final.

Rules
  * age 18-65, weight >= 45 kg
  * at least 90 days since the last whole-blood donation for men, 120 for women (and when sex is not recorded)
  * temporary deferrals from the questionnaire below, each with its own waiting period
"""

from datetime import date, datetime, timedelta

from models import User, utcnow

MIN_AGE, MAX_AGE = 18, 65
MIN_WEIGHT_KG = 45
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


def interval_days(user: User) -> int:
    return INTERVAL_DAYS.get(user.sex or "", DEFAULT_INTERVAL_DAYS)


def next_eligible_at(user: User) -> datetime | None:
    """When the donation interval ends (None = no previous donation)."""
    if not user.last_donation_at:
        return None
    return user.last_donation_at + timedelta(days=interval_days(user))


def age_on(dob: date, today: date) -> int:
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def iso(dt):
    return dt.isoformat() + "Z" if isinstance(dt, datetime) else (dt.isoformat() if dt else None)


def status(user: User, now: datetime | None = None) -> dict:
    """Eligibility from what we already know about the donor (no questionnaire)."""
    now = now or utcnow()
    reasons = []
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


def questions_for(sex: str | None) -> list[dict]:
    return [{"code": c, "text": q, "days": d} for c, (q, d, only) in QUESTIONS.items() if not only or not sex or sex == only]


def parse_dob(value) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])
