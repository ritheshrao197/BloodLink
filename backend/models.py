from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

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
