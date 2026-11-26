"""Blood bank stock: verified blood banks keep units per blood group; anyone can see fresh stock near them.

Stock is shown next to an SOS but never replaces donor alerts. Numbers older than FRESH_HOURS are hidden, and the bank
is reminded once a day while they are REMIND_AFTER_HOURS..STOP_REMINDING_DAYS old (reminders.run_stock).
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlalchemy import func
from sqlalchemy.orm import Session

import auth
import geo
import locations
import logic
from database import get_db
from models import BloodStock, User, utcnow

FRESH_HOURS = 48
REMIND_AFTER_HOURS = 24
STOP_REMINDING_DAYS = 7
RADIUS_KM = 50
MAX_UNITS = 9999

router = APIRouter()


def iso(dt):
    return dt.isoformat() + "Z" if dt else None


def _sheet(db: Session, bank_id: int) -> tuple[dict[str, int], object]:
    rows = db.query(BloodStock).filter(BloodStock.bank_id == bank_id).all()
    units = {g: 0 for g in logic.BLOOD_GROUPS}
    units.update({r.blood_group: r.units for r in rows})
    return units, max((r.updated_at for r in rows), default=None)


def nearby(db: Session, blood_group: str, lat: float | None = None, lng: float | None = None,
           district: str | None = None, state: str | None = None, limit: int = 20) -> list[dict]:
    """Verified banks with fresh stock a patient of this group can receive: within RADIUS_KM or in the same district."""
    groups = logic.compatible_donor_groups(blood_group)
    since = utcnow() - timedelta(hours=FRESH_HOURS)
    banks = (db.query(User).join(BloodStock, BloodStock.bank_id == User.id)
             .filter(User.role == "blood_bank", User.is_verified.is_(True), BloodStock.updated_at >= since,
                     BloodStock.blood_group.in_(groups), BloodStock.units > 0).distinct().all())
    if not geo.valid(lat, lng) and district:
        centre = geo.district_centre(district)
        lat, lng = centre if centre else (None, None)
    out = []
    for bank in banks:
        same_district = bool(district) and (bank.city or "").lower() == district.lower() and (
            not state or not bank.state or bank.state.lower() == state.lower())
        point = geo.home_point(bank)
        dist = geo.km(lat, lng, point["lat"], point["lng"]) if point and geo.valid(lat, lng) else None
        if not same_district and (dist is None or dist > RADIUS_KM):
            continue
        units, updated = _sheet(db, bank.id)
        out.append({
            "bank": {"id": bank.id, "name": bank.name, "city": bank.city, "state": bank.state, "phone": bank.phone},
            "distance_km": geo.shown_km(dist),
            "units": units[blood_group],
            "compatible": {g: units[g] for g in logic.BLOOD_GROUPS if g in groups and g != blood_group and units[g] > 0},
            "updated_at": iso(updated),
            "_sort": (dist if dist is not None else 0, -units[blood_group]),
        })
    out.sort(key=lambda r: r.pop("_sort"))
    return out[:limit]


# ---------------------------------------------------------------- API
class StockBody(BaseModel):
    units: dict[str, int]

    @field_validator("units")
    @classmethod
    def _check(cls, v: dict[str, int]) -> dict[str, int]:
        for group, n in v.items():
            if group not in logic.BLOOD_GROUPS:
                raise ValueError(f"Unknown blood group {group}")
            if not 0 <= n <= MAX_UNITS:
                raise ValueError(f"Units must be between 0 and {MAX_UNITS}")
        return v


def _bank(a: auth.Actor) -> User:
    if not a.user:
        raise HTTPException(401, "Please sign in.")
    if a.user.role != "blood_bank" and not a.user.is_admin:
        raise HTTPException(403, "Only blood bank accounts can update stock.")
    if not a.user.is_verified and not a.user.is_admin:
        raise HTTPException(403, "An admin needs to verify this blood bank before its stock is shown.")
    return a.user


@router.get("/api/stock/mine")
def my_stock(db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    bank = _bank(a)
    units, updated = _sheet(db, bank.id)
    return {"units": units, "updated_at": iso(updated), "fresh_hours": FRESH_HOURS}


@router.put("/api/stock/mine")
def save_stock(body: StockBody, db: Session = Depends(get_db), a: auth.Actor = Depends(auth.actor)):
    bank = _bank(a)
    now = utcnow()
    rows = {r.blood_group: r for r in db.query(BloodStock).filter(BloodStock.bank_id == bank.id)}
    for group in logic.BLOOD_GROUPS:  # the whole sheet is replaced: a group left out is 0
        row = rows.get(group) or BloodStock(bank_id=bank.id, blood_group=group)
        row.units, row.updated_at = body.units.get(group, 0), now
        db.add(row)
    db.commit()
    return my_stock(db, a)


@router.get("/api/stock")
def search_stock(blood_group: str = Query(...), lat: float | None = None, lng: float | None = None,
                 district: str | None = None, state: str | None = None, db: Session = Depends(get_db)):
    if blood_group not in logic.BLOOD_GROUPS:
        raise HTTPException(422, "Unknown blood group")
    if district:
        state, district = locations.normalize(district, state)
    if not district and not geo.valid(lat, lng):
        raise HTTPException(422, "Pick a district or share your location.")
    return nearby(db, blood_group, lat, lng, district, state)


def stale_banks(db: Session) -> list[User]:
    """Banks whose stock is old enough to remind about, but not so old that they have clearly stopped."""
    now = utcnow()
    newest = (db.query(BloodStock.bank_id, func.max(BloodStock.updated_at).label("at"))
              .group_by(BloodStock.bank_id).subquery())
    return (db.query(User).join(newest, newest.c.bank_id == User.id)
            .filter(User.role == "blood_bank", newest.c.at <= now - timedelta(hours=REMIND_AFTER_HOURS),
                    newest.c.at > now - timedelta(days=STOP_REMINDING_DAYS)).all())
