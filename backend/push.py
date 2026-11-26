"""Web push notifications in the browser, sent next to Telegram (see notifier.tell).

Off unless VAPID_PUBLIC_KEY and VAPID_PRIVATE_KEY are set (generate them with `python make_vapid_keys.py`). A
subscription belongs to a signed-in user, or to one SOS request for a requester without an account (they prove it
with the request's token). Subscriptions the push service reports as gone (404/410) are deleted.
"""

import hashlib
import html
import json
import logging
import os
import re
import secrets
import threading

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from pywebpush import WebPushException, webpush
from sqlalchemy.orm import Session

import auth
from database import SessionLocal, get_db
from models import BloodRequest, PushSubscription, utcnow

log = logging.getLogger("bloodlink.push")

PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "").strip()
PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "").strip()
_web = os.getenv("BLOODLINK_WEB_URL", "")
SUBJECT = os.getenv("VAPID_SUBJECT") or (_web if _web.startswith("https://") else "mailto:alerts@bloodlink.invalid")
TTL_SECONDS = 12 * 3600

router = APIRouter()


def enabled() -> bool:
    return bool(PUBLIC_KEY and PRIVATE_KEY)


_vapid_obj = None


def _vapid():
    global _vapid_obj
    if _vapid_obj is None:
        from py_vapid import Vapid01

        _vapid_obj = Vapid01.from_raw(PRIVATE_KEY.encode())
    return _vapid_obj


def _spawn(fn, *args) -> None:
    """Deliver in the background so API responses never wait on push services (tests run it inline)."""
    threading.Thread(target=fn, args=args, daemon=True).start()


def payload(text: str, url: str) -> dict:
    """Telegram-style HTML -> a notification: first line is the title, the rest the body."""
    plain = html.unescape(re.sub(r"<[^>]+>", "", text)).strip()
    title, _, body = plain.partition("\n")
    return {"title": title.strip() or "BloodLink", "body": body.strip(), "url": url}


def _deliver(rows: list[tuple[int, str, str, str]], data: dict) -> None:
    gone = []
    for sub_id, endpoint, p256dh, auth_key in rows:
        try:
            webpush(subscription_info={"endpoint": endpoint, "keys": {"p256dh": p256dh, "auth": auth_key}},
                    data=json.dumps(data), vapid_private_key=_vapid(), vapid_claims={"sub": SUBJECT}, ttl=TTL_SECONDS)
        except WebPushException as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            if status in (404, 410):
                gone.append(endpoint)
            else:
                log.warning("push to subscription %s failed: %s", sub_id, exc)
        except Exception:  # noqa: BLE001  (one bad subscription never stops the others)
            log.exception("push to subscription %s failed", sub_id)
    if gone:
        db = SessionLocal()
        try:
            db.query(PushSubscription).filter(PushSubscription.endpoint.in_(gone)).delete(synchronize_session=False)
            db.commit()
        finally:
            db.close()


def _send(filter_kw: dict, text: str, url: str) -> None:
    db = SessionLocal()
    try:
        rows = [(s.id, s.endpoint, s.p256dh, s.auth) for s in db.query(PushSubscription).filter_by(**filter_kw)]
    finally:
        db.close()
    if rows:
        _deliver(rows, payload(text, url))


def to_user(user_id: int, text: str, url: str = "/") -> None:
    if enabled():
        _spawn(_send, {"user_id": user_id}, text, url)


def to_request(request_id: int, text: str, url: str = "/") -> None:
    """Whoever raised this SOS in a browser without an account."""
    if enabled():
        _spawn(_send, {"request_id": request_id}, text, url)


def users_with_push(db: Session, user_ids: list[int]) -> set[int]:
    if not enabled() or not user_ids:
        return set()
    return {u for (u,) in db.query(PushSubscription.user_id).filter(PushSubscription.user_id.in_(user_ids)).distinct()}


# ---------------------------------------------------------------- request owner token (anonymous requesters)
def new_request_token(req: BloodRequest) -> str:
    """Given to the browser that raised the SOS; only its hash is stored."""
    raw = secrets.token_urlsafe(18)
    req.owner_token_hash = hashlib.sha256(raw.encode()).hexdigest()
    return raw


def _owns(req: BloodRequest, token: str | None) -> bool:
    return bool(token and req.owner_token_hash
                and secrets.compare_digest(req.owner_token_hash, hashlib.sha256(token.encode()).hexdigest()))


# ---------------------------------------------------------------- API
class _Keys(BaseModel):
    p256dh: str = Field(min_length=1, max_length=200)
    auth: str = Field(min_length=1, max_length=100)


class _Subscription(BaseModel):
    endpoint: str = Field(pattern=r"^https://", max_length=1000)
    keys: _Keys


class SubscribeBody(BaseModel):
    subscription: _Subscription
    request_id: int | None = None  # anonymous requester: updates for this SOS only
    request_token: str | None = None


class UnsubscribeBody(BaseModel):
    endpoint: str


@router.get("/api/push/key")
def push_key():
    return {"enabled": enabled(), "public_key": PUBLIC_KEY or None}


@router.post("/api/push/subscribe")
def subscribe(body: SubscribeBody, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    if body.request_id is not None:
        req = db.get(BloodRequest, body.request_id)
        if not req:
            raise HTTPException(404, "Request not found")
        if not _owns(req, body.request_token):
            raise HTTPException(403, "Only the browser that raised this request can follow it.")
        owner = {"request_id": req.id, "user_id": None}
    elif a.user:
        owner = {"user_id": a.user.id, "request_id": None}
    else:
        raise HTTPException(401, "Please sign in.")
    sub = db.query(PushSubscription).filter_by(endpoint=body.subscription.endpoint, **owner).first()
    if not sub:
        sub = PushSubscription(endpoint=body.subscription.endpoint, created_at=utcnow(), **owner)
        db.add(sub)
    sub.p256dh, sub.auth = body.subscription.keys.p256dh, body.subscription.keys.auth
    db.commit()
    return {"status": "subscribed"}


@router.delete("/api/push/subscribe")
def unsubscribe(body: UnsubscribeBody, db: Session = Depends(get_db)):
    """Knowing the endpoint (a long secret URL held by this browser) is enough to remove it."""
    n = db.query(PushSubscription).filter(PushSubscription.endpoint == body.endpoint).delete(synchronize_session=False)
    db.commit()
    return {"status": "unsubscribed", "removed": n}
