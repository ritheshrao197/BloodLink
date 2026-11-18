"""Authentication: Telegram one-tap login, session tokens, the bot as a trusted service, and admin access.

How people sign in
  * Telegram (everyone with Telegram): the site asks for a one-time nonce, opens t.me/<bot>?start=login_<nonce>, the bot
    confirms who tapped Start (Telegram vouches for the id), and the site's poll receives a session token.
  * Linking Telegram to a web account works the same way with link_<nonce>, issued only to the signed-in owner.
  * Demo accounts (seeded, no Telegram) may sign in with their code while DEMO_LOGIN=1. Real accounts never can.
  * Admin: users flagged is_admin (ADMIN_TELEGRAM_IDS), or ADMIN_PASSWORD for the built-in admin account.

Sessions are random 256-bit tokens; only their SHA-256 is stored. The bot authenticates with X-Bot-Secret, derived from
the bot token both processes already share.
"""

import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass
from datetime import timedelta

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models import AuthSession, User, utcnow

SESSION_DAYS = 30
LOGIN_MINUTES = 10
DEMO_LOGIN = os.getenv("DEMO_LOGIN", "1") == "1"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()
ADMIN_TELEGRAM_IDS = {x.strip() for x in os.getenv("ADMIN_TELEGRAM_IDS", "").split(",") if x.strip()}
_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
BOT_SECRET = hashlib.sha256(f"bloodlink-bot:{_TOKEN}".encode()).hexdigest() if _TOKEN else None


def digest(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def new_session(db: Session, user: User) -> str:
    raw = secrets.token_urlsafe(32)
    db.add(AuthSession(token_hash=digest(raw), user_id=user.id, expires_at=utcnow() + timedelta(days=SESSION_DAYS)))
    return raw


@dataclass
class Actor:
    user: User | None = None
    is_bot: bool = False
    token_hash: str | None = None

    @property
    def is_admin(self) -> bool:
        return bool(self.user and self.user.is_admin)


def actor(request: Request, db: Session = Depends(get_db)) -> Actor:
    bot = request.headers.get("x-bot-secret")
    if bot and BOT_SECRET and hmac.compare_digest(bot, BOT_SECRET):
        return Actor(is_bot=True)
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        h = digest(header[7:].strip())
        s = db.query(AuthSession).filter(AuthSession.token_hash == h).first()
        if s and s.expires_at > utcnow():
            user = db.get(User, s.user_id)
            if user:
                return Actor(user=user, token_hash=h)
    return Actor()


def require_self(a: Actor, user: User) -> None:
    """The caller must be this user (or the bot, or an admin)."""
    if a.is_bot or a.is_admin or (a.user and a.user.id == user.id):
        return
    raise HTTPException(401 if not a.user else 403, "Please sign in as this user." if not a.user else "Not allowed.")


def require_bot(a: Actor) -> None:
    if not a.is_bot:
        raise HTTPException(403, "Only the BloodLink bot can call this.")


def require_admin(a: Actor) -> None:
    if not a.is_admin:
        raise HTTPException(401 if not a.user else 403, "Admin sign-in required.")


def admin_user(db: Session) -> User:
    """The built-in admin account used with ADMIN_PASSWORD."""
    user = db.query(User).filter(User.referral_code == "ADMIN").first()
    if not user:
        user = User(name="BloodLink Admin", blood_group="O+", city="—", role="admin", referral_code="ADMIN", points=0,
                    is_admin=True, is_available=False, is_verified=True)
        db.add(user)
        db.flush()
    return user


def check_admin_password(password: str) -> bool:
    return bool(ADMIN_PASSWORD) and hmac.compare_digest(password.encode(), ADMIN_PASSWORD.encode())


def promote_admins(db: Session) -> int:
    """Flag the Telegram accounts listed in ADMIN_TELEGRAM_IDS as admins (run at startup)."""
    if not ADMIN_TELEGRAM_IDS:
        return 0
    users = db.query(User).filter(User.telegram_id.in_(ADMIN_TELEGRAM_IDS)).all()
    for u in users:
        u.is_admin = True
    db.commit()
    return len(users)
