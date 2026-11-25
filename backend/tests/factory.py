from datetime import timedelta
from uuid import uuid4

import auth
from models import BloodRequest, User, utcnow

SCREENING = {"answers": {}, "basics_confirmed": True}


def make_user(db, name="Asha Rao", blood_group="O+", city="Mysuru", state="Karnataka", role="donor", **kw) -> User:
    if role == "donor":
        kw.setdefault("screened_at", utcnow())  # answered the permanent-conditions check at registration
    else:
        kw.setdefault("is_verified", True)  # staff accounts confirm only once an admin has verified them
    u = User(name=name, blood_group=blood_group, city=city, state=state, role=role,
             referral_code=f"T_{uuid4().hex[:8].upper()}", points=0, **kw)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def make_request(db, blood_group="O+", hospital="JSS Hospital", city="Mysuru", state="Karnataka", units=1,
                 age_minutes=1, **kw) -> BloodRequest:
    r = BloodRequest(requester_name="Ravi", blood_group=blood_group, hospital=hospital, city=city, state=state,
                     units_needed=units, units_fulfilled=0, urgency="High", status="Active",
                     created_at=utcnow() - timedelta(minutes=age_minutes), **kw)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def login(db, user: User) -> dict:
    token = auth.new_session(db, user)
    db.commit()
    return {"Authorization": f"Bearer {token}"}


def pledge(client, headers, request_id: int, user_id: int):
    return client.post(f"/api/donate/{request_id}", headers=headers,
                       json={"user_id": user_id, "confirmed": True, "screening": SCREENING})
