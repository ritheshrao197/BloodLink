"""GitHub-style achievements: permanent, collectible badges, separate from spendable BLP.

Everything is computed from real history (donations, the requests they answered, referrals, availability), so an
achievement records *when* its condition was first met. `evaluate()` is idempotent and safe to call any time: after a
donation, a referral, a verification, or lazily when someone opens their collection.

Medical note: whole-blood donors in India must wait 90 days between donations (120 for women), so streaks are counted
in consecutive 3-month windows, never calendar months. Rewarding monthly donation would reward unsafe behaviour.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Callable

from sqlalchemy import func
from sqlalchemy.orm import Session

import logic
from models import BloodRequest, CampRSVP, Donation, Referral, User, UserAchievement, utcnow

IST = timedelta(hours=5, minutes=30)
RARITIES = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]
TIERS = ["Bronze", "Silver", "Gold", "Platinum"]
TIER_RARITY = {"Bronze": "Common", "Silver": "Uncommon", "Gold": "Rare", "Platinum": "Epic"}
TIER_POINTS = {"Bronze": 25, "Silver": 75, "Gold": 150, "Platinum": 300}
CATEGORIES = ["Donation", "Speed", "Referral", "Streak", "Location", "Community", "Fun", "Verification"]

# Lakshmi Puja (Diwali, celebrated over ~5 days) and Vijayadashami (Dussehra) dates.
DIWALI = [date(2024, 11, 1), date(2025, 10, 20), date(2026, 11, 8), date(2027, 10, 29), date(2028, 10, 17)]
DUSSEHRA = [date(2024, 10, 12), date(2025, 10, 2), date(2026, 10, 20), date(2027, 10, 9), date(2028, 9, 27)]
FESTIVAL_DAYS = {d + timedelta(days=k) for d in DIWALI for k in range(-2, 3)} | set(DUSSEHRA)


# ---------------------------------------------------------------- facts about a user
@dataclass
class D:  # one donation
    at: datetime
    response_min: float
    district: str
    state: str | None
    hospital: str
    verified: bool
    first: bool  # first responder on that request
    rainy: bool

    @property
    def ist(self) -> datetime:
        return self.at + IST


@dataclass
class Facts:
    user: User
    donations: list[D] = field(default_factory=list)
    referrals: list[datetime] = field(default_factory=list)
    camps: list[datetime] = field(default_factory=list)  # camp attendances
    unlocked: dict[str, datetime] = field(default_factory=dict)


# ---------------------------------------------------------------- metric helpers: each returns (progress, achieved_at)
def nth(times: list[datetime], n: int):
    times = sorted(times)
    return len(times), (times[n - 1] if len(times) >= n else None)


def distinct(f: Facts, attr: str, n: int):
    seen = set()
    for d in f.donations:
        v = getattr(d, attr)
        if v and v not in seen:
            seen.add(v)
            if len(seen) == n:
                return n, d.at
    return len(seen), None


def quarter_streak(f: Facts, n: int):
    """Longest run of consecutive 3-month windows (calendar quarters, IST) with at least one donation."""
    best, run, prev = 0, 0, None
    for d in f.donations:
        q = d.ist.year * 4 + (d.ist.month - 1) // 3
        if q == prev:
            continue
        run = run + 1 if prev is not None and q == prev + 1 else 1
        prev = q
        best = max(best, run)
        if run >= n:
            return n, d.at
    return best, None


def within(f: Facts, k: int, days: int):
    """k donations inside any window of `days` days."""
    ts = [d.at for d in f.donations]
    best = min(1, len(ts))
    for i in range(len(ts)):
        j = i
        while j + 1 < len(ts) and ts[j + 1] - ts[i] <= timedelta(days=days):
            j += 1
        best = max(best, j - i + 1)
        if j - i + 1 >= k:
            return k, ts[i + k - 1]
    return best, None


def first_where(f: Facts, pred: Callable[[D], bool]):
    hit = next((d for d in f.donations if pred(d)), None)
    return (1, hit.at) if hit else (0, None)


def constant(f: Facts, n_days: int, now: datetime):
    u = f.user
    if not (u.is_available and u.available_since):
        return 0, None
    days = (now - u.available_since).days
    return min(days, n_days), (u.available_since + timedelta(days=n_days) if days >= n_days else None)


# ---------------------------------------------------------------- catalog
def A(key, name, icon, category, rarity, description, requirement, points, target, metric):
    return {"key": key, "name": name, "icon": icon, "category": category, "rarity": rarity,
            "description": description, "requirement": requirement, "points": points, "target": target,
            "metric": metric, "family": None, "tier": None}


def donations(n):
    return lambda f, now: nth([d.at for d in f.donations], n)


def fast(minutes, n):
    return lambda f, now: nth([d.at for d in f.donations if d.response_min <= minutes], n)


def referrals(n):
    return lambda f, now: nth(f.referrals, n)


def streak(n):
    return lambda f, now: quarter_streak(f, n)


def night(start_h, end_h):
    return lambda f, now: first_where(f, lambda d: start_h <= d.ist.hour < end_h)


SINGLES = [
    # --- Donation ---
    A("first_drop", "First Drop", "🩸", "Donation", "Common", "You've officially saved a life. Welcome to the club.",
      "Complete your 1st donation", 50, 1, donations(1)),
    A("life_saver", "Life Saver", "💉", "Donation", "Uncommon", "Three lives. Three families. One hero.",
      "Complete 3 donations", 100, 3, donations(3)),
    A("guardian_angel", "Guardian Angel", "👼", "Donation", "Rare",
      "You're now a Guardian Angel. Your blood flows through five survivors.", "Complete 5 donations", 200, 5, donations(5)),
    A("legendary_hero", "Legendary Hero", "🦸", "Donation", "Epic",
      "Ten donations. You are the backbone of this community.", "Complete 10 donations", 500, 10, donations(10)),
    A("century_club", "Century Club", "💯", "Donation", "Legendary", "25 donations. You are a living legend.",
      "Complete 25 donations", 1000, 25, donations(25)),
    A("bloodline_royalty", "Bloodline Royalty", "👑", "Donation", "Mythic",
      "50 donations. You've saved more lives than most hospitals.", "Complete 50 donations", 2000, 50, donations(50)),
    # --- Speed ---
    A("first_responder", "First Responder", "🚑", "Speed", "Uncommon",
      'When the alert went out, you were the first to say "I can help."', "Be the first to accept an SOS", 50, 1,
      lambda f, now: nth([d.at for d in f.donations if d.first], 1)),
    A("night_owl", "Night Owl", "🦉", "Speed", "Rare", "While the world slept, you answered the call.",
      "Donate between 12 AM and 4 AM", 75, 1, night(0, 4)),
    A("rapid_fire", "Rapid Fire", "🔥", "Speed", "Rare", "Three emergencies, each answered in under ten minutes.",
      "Answer 3 SOS alerts within 10 minutes each", 150, 3, fast(10, 3)),
    A("speed_demon", "Speed Demon", "💨", "Speed", "Epic", "Five emergencies. Five lightning-fast responses.",
      "Answer 5 SOS alerts within 10 minutes each", 250, 5, fast(10, 5)),
    # --- Referral ---
    A("influencer", "Influencer", "📢", "Referral", "Uncommon", "Five people joined because of you.",
      "Refer 5 friends who register", 200, 5, referrals(5)),
    A("community_champion", "Community Champion", "🏅", "Referral", "Rare",
      "Ten people. Ten potential heroes. You're a leader.", "Refer 10 friends who register", 500, 10, referrals(10)),
    A("viral_sensation", "Viral Sensation", "🌊", "Referral", "Epic", "Twenty-five referrals. You've built a movement.",
      "Refer 25 friends who register", 1000, 25, referrals(25)),
    A("bloodline_ambassador", "Bloodline Ambassador", "🎖️", "Referral", "Legendary",
      "Fifty people. You are the face of BloodLink.", "Refer 50 friends who register", 2500, 50, referrals(50)),
    # --- Streak (3-month windows: the safe donation interval) ---
    A("on_a_roll", "On a Roll", "🎯", "Streak", "Common", "Consistency is key. You're on a roll.",
      "Donate in 2 consecutive 3-month windows", 75, 2, streak(2)),
    A("streak_master", "Streak Master", "🔥", "Streak", "Uncommon", "Three windows straight. Dedication.",
      "Donate in 3 consecutive 3-month windows", 150, 3, streak(3)),
    A("unstoppable", "Unstoppable", "🚀", "Streak", "Rare", "A full year, every window. Nothing stops you.",
      "Donate in 4 consecutive 3-month windows (1 year)", 300, 4, streak(4)),
    A("iron_will", "Iron Will", "🛡️", "Streak", "Epic", "Two years without missing a window. Iron Will.",
      "Donate in 8 consecutive 3-month windows (2 years)", 750, 8, streak(8)),
    A("the_constant", "The Constant", "🧭", "Streak", "Rare", "Always ready. Always available. Always a hero.",
      "Stay available for 90 days straight", 150, 90, lambda f, now: constant(f, 90, now)),
    # --- Location ---
    A("city_hero", "City Hero", "🏙️", "Location", "Uncommon", "Your impact spans three cities.",
      "Donate in 3 different districts", 150, 3, lambda f, now: distinct(f, "district", 3)),
    A("state_champion", "State Champion", "🗺️", "Location", "Rare", "Five districts. Five communities.",
      "Donate in 5 different districts", 300, 5, lambda f, now: distinct(f, "district", 5)),
    A("globetrotter", "Globetrotter", "🌐", "Location", "Epic", "Your blood has traveled across state lines.",
      "Donate in 3 different states", 500, 3, lambda f, now: distinct(f, "state", 3)),
    A("bharat_sevak", "Bharat Sevak", "🇮🇳", "Location", "Legendary", "Five states. One nation. One hero.",
      "Donate in 5 different states", 1000, 5, lambda f, now: distinct(f, "state", 5)),
    # --- Community ---
    A("first_camp", "First Camp", "🎪", "Community", "Common", "You showed up for a blood drive. Communities run on people like you.",
      "Donate at a donation camp", 50, 1, lambda f, now: nth(f.camps, 1)),
    A("camp_champion", "Camp Champion", "🏕️", "Community", "Rare", "Three camps. You make blood drives work.",
      "Donate at 3 donation camps", 150, 3, lambda f, now: nth(f.camps, 3)),
    # --- Fun ---
    A("yolo", "YOLO", "🎲", "Fun", "Common", "No hesitation. Straight into action.",
      "Donate on the day you register", 25, 1,
      lambda f, now: first_where(f, lambda d: d.ist.date() == (f.user.created_at + IST).date())),
    A("rainmaker", "Rainmaker", "🌧️", "Fun", "Common", "Neither rain nor storm stops you.",
      "Donate while it's raining", 25, 1, lambda f, now: first_where(f, lambda d: d.rainy)),
    A("festival_of_life", "Festival of Life", "🪔", "Fun", "Uncommon", "While others celebrated, you saved a life.",
      "Donate during Diwali or Dussehra", 75, 1, lambda f, now: first_where(f, lambda d: d.ist.date() in FESTIVAL_DAYS)),
    A("new_year_hero", "New Year Hero", "🎆", "Fun", "Rare", "You started the year by saving a life.",
      "Donate on January 1st", 150, 1, lambda f, now: first_where(f, lambda d: (d.ist.month, d.ist.day) == (1, 1))),
    A("midnight_caller", "Midnight Caller", "🌙", "Fun", "Rare", "The world was asleep. You were awake.",
      "Accept an SOS between 12 AM and 3 AM", 100, 1, night(0, 3)),
    A("the_unicorn", "The Unicorn", "🦄", "Fun", "Legendary", "AB- is the rarest. You are the unicorn.",
      "Donate as an AB- donor", 500, 1,
      lambda f, now: first_where(f, lambda d: f.user.blood_group == "AB-")),
    A("hat_trick", "Hat-Trick", "🎩", "Fun", "Rare", "Three donations in a year: the safe maximum pace, kept up.",
      "Complete 3 donations within 12 months", 200, 3, lambda f, now: within(f, 3, 365)),
    A("perfect_ten", "Perfect Ten", "🔟", "Fun", "Epic", "Ten emergencies. Ten times you showed up fast.",
      "Answer 10 SOS alerts within 10 minutes each", 500, 10, fast(10, 10)),
    # --- Verification ---
    A("verified_donor", "Verified Donor", "✅", "Verification", "Common", "Your identity is verified. Trust earned.",
      "Get verified by a hospital or admin", 50, 1, lambda f, now: (1, TIMELESS) if f.user.is_verified else (0, None)),
    A("trusted_donor", "Trusted Donor", "🔒", "Verification", "Uncommon",
      "Five verified donations. The community trusts you.", "Complete 5 verified donations", 150, 5,
      lambda f, now: nth([d.at for d in f.donations if d.verified], 5)),
    A("gold_standard", "Gold Standard", "🥇", "Verification", "Rare", "Ten verified. You're the gold standard.",
      "Complete 10 verified donations", 300, 10, lambda f, now: nth([d.at for d in f.donations if d.verified], 10)),
    A("medical_hero", "Medical Hero", "⚕️", "Verification", "Rare", "Three hospitals. Three medical partners.",
      "Donate at 3 different hospitals", 200, 3, lambda f, now: distinct(f, "hospital", 3)),
    A("admins_favorite", "Admin's Favorite", "⭐", "Verification", "Epic", "Hand-picked by the team. You're a star.",
      "Be recognised by the BloodLink team", 300, 1,
      lambda f, now: (1, f.unlocked["admins_favorite"]) if "admins_favorite" in f.unlocked else (0, None)),
]
TIMELESS = object()  # "true now": achieved_at is supplied by the caller (now, or a seed's chosen time)

# GitHub-style tiered badges: one badge that levels up Bronze -> Silver -> Gold -> Platinum
FAMILIES = [
    {"key": "blood_shark", "name": "Blood Shark", "icon": "🦈", "category": "Donation",
     "description": "Keep donating to level up.", "unit": "donations", "thresholds": [1, 5, 10, 25], "metric": donations},
    {"key": "quickdraw", "name": "Quickdraw", "icon": "⚡", "category": "Speed",
     "description": "Answer SOS alerts within 5 minutes.", "unit": "fast responses", "thresholds": [1, 5, 10, 25],
     "metric": lambda n: fast(logic.QUICK_RESPONSE_MINUTES, n)},
    {"key": "recruiter", "name": "Recruiter", "icon": "🤝", "category": "Referral",
     "description": "Bring friends into the movement.", "unit": "referrals", "thresholds": [1, 5, 10, 25],
     "metric": referrals},
    {"key": "hot_streak", "name": "Hot Streak", "icon": "🔥", "category": "Streak",
     "description": "Donate in consecutive 3-month windows.", "unit": "windows in a row", "thresholds": [2, 3, 4, 8],
     "metric": streak},
]
TIERED = [
    {"key": f"{fam['key']}_{tier.lower()}", "name": fam["name"], "icon": fam["icon"], "category": fam["category"],
     "rarity": TIER_RARITY[tier], "description": fam["description"], "requirement": f"{n} {fam['unit']}",
     "points": TIER_POINTS[tier], "target": n, "metric": fam["metric"](n), "family": fam["key"], "tier": tier}
    for fam in FAMILIES for tier, n in zip(TIERS, fam["thresholds"])
]
CATALOG = SINGLES + TIERED
BY_KEY = {a["key"]: a for a in CATALOG}
MANUAL = {"admins_favorite"}


def public(a: dict) -> dict:
    return {k: v for k, v in a.items() if k != "metric"}


# ---------------------------------------------------------------- loading facts in bulk
def load_facts(db: Session, users: list[User]) -> dict[int, Facts]:
    ids = [u.id for u in users]
    facts = {u.id: Facts(u) for u in users}
    rows = (db.query(Donation, BloodRequest).join(BloodRequest, Donation.request_id == BloodRequest.id)
            .filter(Donation.donor_id.in_(ids)).order_by(Donation.created_at, Donation.id).all())
    req_ids = {r.id for _, r in rows}
    first = dict(db.query(Donation.request_id, func.min(Donation.id)).filter(Donation.request_id.in_(req_ids))
                 .group_by(Donation.request_id).all()) if req_ids else {}
    for d, r in rows:
        facts[d.donor_id].donations.append(D(
            at=d.created_at, response_min=(d.created_at - r.created_at).total_seconds() / 60,
            district=r.city, state=r.state, hospital=r.hospital, verified=bool(r.is_verified),
            first=first.get(r.id) == d.id, rainy=d.weather == "rain"))
    for referrer_id, at in db.query(Referral.referrer_id, Referral.created_at).filter(Referral.referrer_id.in_(ids)):
        facts[referrer_id].referrals.append(at)
    for uid, at in (db.query(CampRSVP.user_id, CampRSVP.attended_at)
                    .filter(CampRSVP.user_id.in_(ids), CampRSVP.status == "Attended")):
        if at:
            facts[uid].camps.append(at)
    for uid, key, at in (db.query(UserAchievement.user_id, UserAchievement.key, UserAchievement.unlocked_at)
                         .filter(UserAchievement.user_id.in_(ids))):
        facts[uid].unlocked[key] = at
    return facts


# ---------------------------------------------------------------- evaluation
AwardFn = Callable[[User, int, str, datetime], None]


def _award_now(db: Session) -> AwardFn:
    return lambda user, amount, reason, when: logic.award(db, user, amount, reason)


def evaluate(db: Session, users: list[User], now: datetime | None = None, award: AwardFn | None = None,
             timeless_at: Callable[[User], datetime] | None = None, new_since: datetime | None = None,
             notify: bool = True) -> dict[int, list[dict]]:
    """Unlock everything each user has newly earned. Returns {user_id: [achievement, ...]} (caller commits)."""
    now = now or utcnow()
    award = award or _award_now(db)
    users = [u for u in users if u and u.role == "donor"]
    if not users:
        return {}
    facts = load_facts(db, users)
    result: dict[int, list[dict]] = {}
    for u in users:
        f = facts[u.id]
        for a in CATALOG:
            if a["key"] in f.unlocked or a["key"] in MANUAL:
                continue
            _, when = a["metric"](f, now)
            if when is None:
                continue
            if when is TIMELESS:
                when = timeless_at(u) if timeless_at else now
            when = min(when, now)
            db.add(UserAchievement(user_id=u.id, key=a["key"], unlocked_at=when,
                                   is_new=new_since is None or when >= new_since))
            f.unlocked[a["key"]] = when
            label = f"{a['name']} ({a['tier']})" if a["tier"] else a["name"]
            award(u, a["points"], f"Achievement unlocked: {a['icon']} {label}", when)
            result.setdefault(u.id, []).append(a)
    if notify:
        import notifier

        for u in users:
            if result.get(u.id) and u.telegram_id:
                lines = "\n".join(_line(a) for a in result[u.id])
                total = sum(a["points"] for a in result[u.id])
                notifier.notify_t(u.telegram_id, u.language, "achievements", lines=lines, points=total)
    return result


def grant(db: Session, user: User, key: str) -> dict | None:
    """Manually award an achievement (e.g. Admin's Favorite). Returns it, or None if already held."""
    a = BY_KEY[key]
    if db.query(UserAchievement).filter(UserAchievement.user_id == user.id, UserAchievement.key == key).first():
        return None
    db.add(UserAchievement(user_id=user.id, key=key, unlocked_at=utcnow(), is_new=True))
    logic.award(db, user, a["points"], f"Achievement unlocked: {a['icon']} {a['name']}")
    import notifier

    notifier.notify_t(user.telegram_id, user.language, "achievements", lines=_line(a), points=a["points"])
    return a


RARITY_DOT = {"Common": "⚪", "Uncommon": "🟢", "Rare": "🔵", "Epic": "🟣", "Legendary": "🟡", "Mythic": "🔴"}


def _line(a: dict) -> str:
    name = f"{a['name']} ({a['tier']})" if a["tier"] else a["name"]
    return f"{a['icon']} <b>{name}</b> · {RARITY_DOT[a['rarity']]} {a['rarity']} · +{a['points']} BLP"


# ---------------------------------------------------------------- presentation
def unlock_counts(db: Session) -> tuple[dict[str, int], int]:
    counts = dict(db.query(UserAchievement.key, func.count(UserAchievement.id)).group_by(UserAchievement.key).all())
    donors = db.query(User).filter(User.role == "donor").count()
    return counts, donors


def collection(db: Session, user: User) -> dict:
    """A user's full collection: unlocked and locked achievements with progress, tiered badges with levels."""
    now = utcnow()
    f = load_facts(db, [user])[user.id]
    counts, donors = unlock_counts(db)

    def pct(key):
        return round(100 * counts.get(key, 0) / donors, 1) if donors else 0

    def progress(a):
        value, _ = a["metric"](f, now)
        return min(value, a["target"])

    singles = []
    for a in SINGLES:
        at = f.unlocked.get(a["key"])
        singles.append({**public(a), "unlocked": at is not None, "unlocked_at": iso(at), "progress": progress(a),
                        "percent_of_donors": pct(a["key"])})
    families = []
    for fam in FAMILIES:
        tiers = [a for a in TIERED if a["family"] == fam["key"]]
        got = [a for a in tiers if a["key"] in f.unlocked]
        nxt = next((a for a in tiers if a["key"] not in f.unlocked), None)
        families.append({
            "key": fam["key"], "name": fam["name"], "icon": fam["icon"], "category": fam["category"],
            "description": fam["description"], "unit": fam["unit"],
            "tier": got[-1]["tier"] if got else None,
            "unlocked_at": iso(f.unlocked[got[-1]["key"]]) if got else None,
            "value": fam["metric"](10 ** 6)(f, now)[0],
            "next": {"tier": nxt["tier"], "target": nxt["target"], "points": nxt["points"]} if nxt else None,
            "tiers": [{"tier": a["tier"], "target": a["target"], "points": a["points"],
                       "unlocked_at": iso(f.unlocked.get(a["key"])), "percent_of_donors": pct(a["key"])}
                      for a in tiers],
        })
    new = (db.query(UserAchievement.key).filter(UserAchievement.user_id == user.id, UserAchievement.is_new.is_(True))
           .all())
    unlocked_keys = set(f.unlocked)
    return {
        "summary": {"unlocked": len(unlocked_keys), "total": len(CATALOG),
                    "points_earned": sum(BY_KEY[k]["points"] for k in unlocked_keys if k in BY_KEY)},
        "new": [k for (k,) in new],
        "singles": singles,
        "families": families,
        "categories": CATEGORIES,
        "rarities": RARITIES,
    }


def showcase(db: Session, user_ids: list[int], limit: int = 4) -> dict[int, dict]:
    """Per user: achievement count and their rarest few icons, for leaderboards."""
    rows = db.query(UserAchievement.user_id, UserAchievement.key).filter(UserAchievement.user_id.in_(user_ids)).all()
    by_user = defaultdict(list)
    for uid, key in rows:
        if key in BY_KEY:
            by_user[uid].append(BY_KEY[key])
    out = {}
    for uid in user_ids:
        items = by_user.get(uid, [])
        best: dict[str, dict] = {}
        for a in items:  # one icon per tiered family: its highest tier
            k = a["family"] or a["key"]
            if k not in best or TIERS.index(a["tier"]) > TIERS.index(best[k]["tier"]):
                best[k] = a
        top = sorted(best.values(), key=lambda a: -RARITIES.index(a["rarity"]))[:limit]
        out[uid] = {"count": len(items),
                    "top": [{"icon": a["icon"], "name": a["name"], "tier": a["tier"], "rarity": a["rarity"]} for a in top]}
    return out


def iso(dt):
    return dt.isoformat() + "Z" if dt else None
