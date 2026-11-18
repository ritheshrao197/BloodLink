from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint

from database import Base


def utcnow() -> datetime:
    """Naive UTC timestamp (SQLite does not store tz info)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    blood_group = Column(String, nullable=False, index=True)
    city = Column(String, nullable=False, index=True)  # district (see locations.py)
    state = Column(String, nullable=True)
    language = Column(String, default="en")  # en | kn | hi (Telegram messages)
    phone = Column(String, nullable=True)
    role = Column(String, default="donor")  # donor | hospital
    telegram_id = Column(String, unique=True, nullable=True)
    telegram_username = Column(String, nullable=True)
    points = Column(Integer, default=0)
    badge = Column(String, default="Bronze")
    referral_code = Column(String, unique=True, nullable=False)
    referred_by = Column(String, nullable=True)
    total_donations = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    available_since = Column(DateTime, default=utcnow, nullable=True)  # for "The Constant" achievement
    # health basics for the eligibility check (all optional, self-reported)
    sex = Column(String, nullable=True)  # male | female | other
    date_of_birth = Column(Date, nullable=True)
    weight_kg = Column(Integer, nullable=True)
    deferred_until = Column(DateTime, nullable=True)  # self-reported temporary deferral (fever, tattoo, ...)
    is_admin = Column(Boolean, default=False)
    is_demo = Column(Boolean, default=False)  # seeded demo account (may be opened by code while DEMO_LOGIN=1)
    is_verified = Column(Boolean, default=False)
    last_donation_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class BloodRequest(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    requester_name = Column(String, nullable=False)
    requester_telegram_id = Column(String, nullable=True)
    requester_language = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    blood_group = Column(String, nullable=False)
    hospital = Column(String, nullable=False)
    city = Column(String, nullable=False)  # district
    state = Column(String, nullable=True)
    units_needed = Column(Integer, default=1)
    units_fulfilled = Column(Integer, default=0)
    urgency = Column(String, default="High")  # Critical | High | Normal
    status = Column(String, default="Active")  # Active | Fulfilled | Cancelled
    fulfilled_by = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    notified_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)
    fulfilled_at = Column(DateTime, nullable=True)


class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    donor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    points_awarded = Column(Integer, default=0)
    quick_response = Column(Boolean, default=False)
    weather = Column(String, nullable=True)  # "rain" | "dry" | None (unknown), for the Rainmaker achievement
    created_at = Column(DateTime, default=utcnow)


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"))
    referred_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="Registered")  # Registered | Donated
    points_awarded = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)


class Reward(Base):
    """A redeemed (or awarded) voucher. Catalog lives in logic.REWARDS."""

    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    reward_id = Column(Integer, nullable=True)
    reward_name = Column(String)
    points_cost = Column(Integer)
    voucher_code = Column(String)
    status = Column(String, default="Issued")
    created_at = Column(DateTime, default=utcnow)


class PointLog(Base):
    """Ledger of every BLP change, used for activity feeds."""

    __tablename__ = "point_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)
    reason = Column(String)
    created_at = Column(DateTime, default=utcnow)


class ReminderLog(Base):
    """One row per reminder sent, so each kind goes out once per donation cycle."""

    __tablename__ = "reminder_logs"
    __table_args__ = (UniqueConstraint("user_id", "kind", "cycle"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    kind = Column(String, nullable=False)  # soon | eligible | nudge
    cycle = Column(String, nullable=False)  # date of the donation that started this cycle
    sent_at = Column(DateTime, default=utcnow)


class AuthSession(Base):
    """A signed-in browser. Only the SHA-256 of the token is stored."""

    __tablename__ = "auth_sessions"

    id = Column(Integer, primary_key=True, index=True)
    token_hash = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    expires_at = Column(DateTime, nullable=False)


class LoginRequest(Base):
    """A pending Telegram login/link: the site polls it until the bot confirms who tapped Start."""

    __tablename__ = "login_requests"

    id = Column(Integer, primary_key=True, index=True)
    nonce = Column(String, unique=True, index=True, nullable=False)
    purpose = Column(String, default="login")  # login | link
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # link: the signed-in owner; login: set on confirm
    token = Column(String, nullable=True)  # raw session token, handed over once to the polling browser, then deleted
    status = Column(String, default="pending")  # pending | ok | not_registered | taken
    created_at = Column(DateTime, default=utcnow)
    expires_at = Column(DateTime, nullable=False)


class Team(Base):
    """A college, class, company or friend group competing on donations."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    kind = Column(String, default="group")  # college | company | community | group
    city = Column(String, nullable=True)  # district
    state = Column(String, nullable=True)
    invite_code = Column(String, unique=True, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utcnow)


class TeamMember(Base):
    __tablename__ = "team_members"
    __table_args__ = (UniqueConstraint("team_id", "user_id"),)

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    role = Column(String, default="member")  # owner | member
    joined_at = Column(DateTime, default=utcnow)  # only donations after this count for the team


class Camp(Base):
    """A blood donation drive that donors RSVP to."""

    __tablename__ = "camps"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    organizer = Column(String, nullable=False)  # shown name: hospital, college, NGO...
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    venue = Column(String, nullable=False)
    city = Column(String, nullable=False)  # district
    state = Column(String, nullable=True)
    starts_at = Column(DateTime, nullable=False)  # UTC
    ends_at = Column(DateTime, nullable=False)
    expected_donors = Column(Integer, default=50)
    description = Column(String, nullable=True)
    status = Column(String, default="Upcoming")  # Upcoming | Completed | Cancelled
    created_at = Column(DateTime, default=utcnow)


class CampRSVP(Base):
    __tablename__ = "camp_rsvps"
    __table_args__ = (UniqueConstraint("camp_id", "user_id"),)

    id = Column(Integer, primary_key=True, index=True)
    camp_id = Column(Integer, ForeignKey("camps.id"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    status = Column(String, default="Registered")  # Registered | Attended | Cancelled
    created_at = Column(DateTime, default=utcnow)
    attended_at = Column(DateTime, nullable=True)


class UserAchievement(Base):
    """An unlocked achievement. The catalog itself lives in code (achievements.py), keyed by `key`."""

    __tablename__ = "user_achievements"
    __table_args__ = (UniqueConstraint("user_id", "key"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    key = Column(String, nullable=False)
    unlocked_at = Column(DateTime, default=utcnow)
    is_new = Column(Boolean, default=True)  # shows a NEW tag until the user has seen it
