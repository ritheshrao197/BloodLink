"""Teams (colleges, companies, friend groups) and donation camps.

Team score = donations its members make *after* joining (SOS donations and camp attendance), so recruiting someone
with a long history does not inflate a team. Camps: organisers post a drive, donors RSVP (only if they will be
eligible by then), organisers mark attendance, which records the donation and keeps the safe-interval clock running.
"""

import random
import string
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import achievements
import eligibility
import locations
import logic
import notifier
from database import get_db
from models import Camp, CampRSVP, Donation, Team, TeamMember, User, utcnow

router = APIRouter(prefix="/api")

TEAM_KINDS = ("college", "company", "community", "group")
CAMP_POINTS = 100


def iso(dt):
    return dt.isoformat() + "Z" if dt else None


def _user(db: Session, user_id: int | None) -> User:
    user = db.get(User, user_id) if user_id else None
    if not user:
        raise HTTPException(404, "User not found. Sign in first.")
    return user


def invite_code(db: Session) -> str:
    while True:
        code = "TEAM-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if not db.query(Team).filter(Team.invite_code == code).first():
            return code


# ---------------------------------------------------------------- team scoring
def team_scores(db: Session, team_ids: list[int] | None = None) -> dict[int, dict]:
    """{team_id: {members, donations, points}} counting only contributions made after each member joined."""
    q = db.query(TeamMember)
    if team_ids is not None:
        q = q.filter(TeamMember.team_id.in_(team_ids))
    members = q.all()
    scores = defaultdict(lambda: {"members": 0, "donations": 0, "points": 0})
    by_user = defaultdict(list)
    for m in members:
        scores[m.team_id]["members"] += 1
        by_user[m.user_id].append(m)
    if not by_user:
        return scores
    uids = list(by_user)
    for donor_id, at, pts in db.query(Donation.donor_id, Donation.created_at, Donation.points_awarded).filter(Donation.donor_id.in_(uids)):
        for m in by_user[donor_id]:
            if at >= m.joined_at:
                scores[m.team_id]["donations"] += 1
                scores[m.team_id]["points"] += pts or 0
    for uid, at in (db.query(CampRSVP.user_id, CampRSVP.attended_at)
                    .filter(CampRSVP.user_id.in_(uids), CampRSVP.status == "Attended")):
        for m in by_user[uid]:
            if at and at >= m.joined_at:
                scores[m.team_id]["donations"] += 1
                scores[m.team_id]["points"] += CAMP_POINTS
    return scores


def team_out(t: Team, score: dict, rank: int | None = None, mine: set | None = None) -> dict:
    return {"id": t.id, "name": t.name, "kind": t.kind, "city": t.city, "state": t.state, "rank": rank,
            "members": score["members"], "donations": score["donations"], "points": score["points"],
            "is_mine": bool(mine and t.id in mine), "created_at": iso(t.created_at)}


def ranked(db: Session, kind: str | None = None) -> list[tuple[Team, dict]]:
    q = db.query(Team)
    if kind:
        q = q.filter(Team.kind == kind)
    teams = q.all()
    scores = team_scores(db, [t.id for t in teams])
    return sorted(((t, scores[t.id]) for t in teams), key=lambda x: (-x[1]["points"], -x[1]["donations"], x[0].id))


# ---------------------------------------------------------------- team endpoints
class TeamCreate(BaseModel):
    user_id: int
    name: str = Field(min_length=2, max_length=60)
    kind: str = "group"
    city: str | None = None
    state: str | None = None


class TeamJoin(BaseModel):
    user_id: int
    invite_code: str


class UserOnly(BaseModel):
    user_id: int


@router.get("/teams")
def list_teams(kind: str | None = None, user_id: int | None = None, limit: int = 50, db: Session = Depends(get_db)):
    mine = {m.team_id for m in db.query(TeamMember).filter(TeamMember.user_id == user_id)} if user_id else set()
    rows = ranked(db, kind if kind in TEAM_KINDS else None)
    return [team_out(t, s, i + 1, mine) for i, (t, s) in enumerate(rows[: min(limit, 200)])]


@router.post("/teams")
def create_team(body: TeamCreate, db: Session = Depends(get_db)):
    user = _user(db, body.user_id)
    if body.kind not in TEAM_KINDS:
        raise HTTPException(400, f"kind must be one of {', '.join(TEAM_KINDS)}")
    name = body.name.strip()
    if db.query(Team).filter(Team.name.ilike(name)).first():
        raise HTTPException(409, "A team with this name already exists. Ask its members for the invite code.")
    state, district = locations.normalize(body.city or user.city, body.state or user.state)
    team = Team(name=name, kind=body.kind, city=district, state=state, invite_code=invite_code(db), created_by=user.id)
    db.add(team)
    db.flush()
    db.add(TeamMember(team_id=team.id, user_id=user.id, role="owner"))
    db.commit()
    return team_detail(team.id, user.id, db)


@router.post("/teams/join")
def join_team(body: TeamJoin, db: Session = Depends(get_db)):
    user = _user(db, body.user_id)
    team = db.query(Team).filter(Team.invite_code == body.invite_code.strip().upper()).first()
    if not team:
        raise HTTPException(404, "No team with that invite code.")
    if not db.query(TeamMember).filter_by(team_id=team.id, user_id=user.id).first():
        db.add(TeamMember(team_id=team.id, user_id=user.id))
        db.commit()
    return team_detail(team.id, user.id, db)


@router.post("/teams/{team_id}/leave")
def leave_team(team_id: int, body: UserOnly, db: Session = Depends(get_db)):
    db.query(TeamMember).filter_by(team_id=team_id, user_id=body.user_id).delete()
    db.commit()
    return {"status": "success"}


@router.get("/teams/{team_id}")
def team_detail(team_id: int, user_id: int | None = None, db: Session = Depends(get_db)):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(404, "Team not found")
    rows = ranked(db, None)
    rank = next((i + 1 for i, (t, _) in enumerate(rows) if t.id == team.id), None)
    score = next(s for t, s in rows if t.id == team.id)
    # per-member contribution since joining
    members = db.query(TeamMember, User).join(User, TeamMember.user_id == User.id).filter(TeamMember.team_id == team.id).all()
    contrib = defaultdict(lambda: [0, 0])
    uids = [u.id for _, u in members]
    joined = {m.user_id: m.joined_at for m, _ in members}
    if uids:
        for donor_id, at, pts in db.query(Donation.donor_id, Donation.created_at, Donation.points_awarded).filter(Donation.donor_id.in_(uids)):
            if at >= joined[donor_id]:
                contrib[donor_id][0] += 1
                contrib[donor_id][1] += pts or 0
        for uid, at in db.query(CampRSVP.user_id, CampRSVP.attended_at).filter(CampRSVP.user_id.in_(uids), CampRSVP.status == "Attended"):
            if at and at >= joined[uid]:
                contrib[uid][0] += 1
                contrib[uid][1] += CAMP_POINTS
    is_member = user_id in joined
    out = team_out(team, score, rank, {team.id} if is_member else set())
    out["teams_total"] = len(rows)
    out["invite_code"] = team.invite_code if is_member else None
    out["members_list"] = sorted(
        ({"id": u.id, "name": u.name, "blood_group": u.blood_group, "badge": u.badge, "role": m.role,
          "donations": contrib[u.id][0], "points": contrib[u.id][1], "joined_at": iso(m.joined_at)} for m, u in members),
        key=lambda x: (-x["points"], x["name"]))
    ahead = rows[rank - 2] if rank and rank > 1 else None
    out["gap_to_next"] = {"name": ahead[0].name, "points": ahead[1]["points"] - score["points"]} if ahead else None
    return out


@router.get("/users/{user_id}/teams")
def my_teams(user_id: int, db: Session = Depends(get_db)):
    ids = [m.team_id for m in db.query(TeamMember).filter(TeamMember.user_id == user_id)]
    rows = ranked(db, None)
    return [team_out(t, s, i + 1, set(ids)) for i, (t, s) in enumerate(rows) if t.id in ids]


# ---------------------------------------------------------------- camps
class CampCreate(BaseModel):
    user_id: int
    title: str = Field(min_length=3, max_length=80)
    organizer: str = Field(min_length=2, max_length=80)
    venue: str = Field(min_length=2, max_length=120)
    city: str
    state: str | None = None
    starts_at: datetime
    hours: int = Field(default=6, ge=1, le=14)
    expected_donors: int = Field(default=50, ge=5, le=2000)
    description: str | None = Field(default=None, max_length=400)
    team_id: int | None = None


class Attend(BaseModel):
    user_id: int  # organiser (or admin) marking attendance
    attendee_id: int


def camp_out(c: Camp, counts: dict, my: CampRSVP | None = None, team: Team | None = None) -> dict:
    return {"id": c.id, "title": c.title, "organizer": c.organizer, "venue": c.venue, "city": c.city, "state": c.state,
            "starts_at": iso(c.starts_at), "ends_at": iso(c.ends_at), "expected_donors": c.expected_donors,
            "description": c.description, "status": c.status, "team": {"id": team.id, "name": team.name} if team else None,
            "registered": counts.get("Registered", 0) + counts.get("Attended", 0), "attended": counts.get("Attended", 0),
            "my_status": my.status if my else None, "created_by": c.created_by}


def _camp_counts(db: Session, camp_ids: list[int]) -> dict[int, dict]:
    out = defaultdict(dict)
    for cid, status in db.query(CampRSVP.camp_id, CampRSVP.status).filter(CampRSVP.camp_id.in_(camp_ids)):
        out[cid][status] = out[cid].get(status, 0) + 1
    return out


def _refresh_status(db: Session) -> None:
    """Upcoming camps whose end has passed become Completed."""
    now = utcnow()
    for c in db.query(Camp).filter(Camp.status == "Upcoming", Camp.ends_at < now):
        c.status = "Completed"
    db.commit()


@router.get("/camps")
def list_camps(when: str = "upcoming", state: str | None = None, user_id: int | None = None, db: Session = Depends(get_db)):
    _refresh_status(db)
    q = db.query(Camp)
    q = q.filter(Camp.status == "Upcoming").order_by(Camp.starts_at) if when == "upcoming" else \
        q.filter(Camp.status == "Completed").order_by(Camp.starts_at.desc())
    if state:
        q = q.filter(Camp.state == state)
    camps = q.limit(60).all()
    counts = _camp_counts(db, [c.id for c in camps])
    mine = {r.camp_id: r for r in db.query(CampRSVP).filter(CampRSVP.user_id == user_id)} if user_id else {}
    teams = {t.id: t for t in db.query(Team).filter(Team.id.in_([c.team_id for c in camps if c.team_id]))}
    return [camp_out(c, counts[c.id], mine.get(c.id), teams.get(c.team_id)) for c in camps]


@router.post("/camps")
def create_camp(body: CampCreate, db: Session = Depends(get_db)):
    user = _user(db, body.user_id)
    starts = body.starts_at.replace(tzinfo=None) if body.starts_at.tzinfo is None else \
        (body.starts_at - body.starts_at.utcoffset()).replace(tzinfo=None)
    if starts < utcnow():
        raise HTTPException(400, "The camp must start in the future.")
    state, district = locations.normalize(body.city, body.state)
    camp = Camp(title=body.title.strip(), organizer=body.organizer.strip(), venue=body.venue.strip(), city=district, state=state,
                starts_at=starts, ends_at=starts + timedelta(hours=body.hours), expected_donors=body.expected_donors,
                description=(body.description or "").strip() or None, team_id=body.team_id, created_by=user.id)
    db.add(camp)
    db.commit()
    return camp_out(camp, {})


def _rsvp_block(user: User, camp: Camp) -> list[dict]:
    """Reasons the donor won't be able to donate on the camp day."""
    reasons = []
    nxt = eligibility.next_eligible_at(user)
    if nxt and nxt > camp.starts_at:
        reasons.append({"code": "interval", "until": iso(nxt), "days": eligibility.interval_days(user)})
    if user.deferred_until and user.deferred_until > camp.starts_at:
        reasons.append({"code": "deferred", "until": iso(user.deferred_until)})
    if user.weight_kg is not None and user.weight_kg < eligibility.MIN_WEIGHT_KG:
        reasons.append({"code": "underweight", "until": None})
    if user.date_of_birth and not eligibility.MIN_AGE <= eligibility.age_on(user.date_of_birth, camp.starts_at.date()) <= eligibility.MAX_AGE:
        reasons.append({"code": "too_young" if eligibility.age_on(user.date_of_birth, camp.starts_at.date()) < 18 else "too_old", "until": None})
    return reasons


@router.post("/camps/{camp_id}/rsvp")
def rsvp(camp_id: int, body: UserOnly, db: Session = Depends(get_db)):
    """Toggle the user's RSVP."""
    user = _user(db, body.user_id)
    camp = db.get(Camp, camp_id)
    if not camp or camp.status != "Upcoming":
        raise HTTPException(404, "This camp is not open for registration.")
    row = db.query(CampRSVP).filter_by(camp_id=camp.id, user_id=user.id).first()
    if row and row.status == "Registered":
        row.status = "Cancelled"
        db.commit()
        return {"status": "cancelled", "camp": camp_out(camp, _camp_counts(db, [camp.id])[camp.id], row)}
    reasons = _rsvp_block(user, camp)
    if reasons:
        raise HTTPException(409, {"message": "You won't be able to donate on the camp day.", "eligibility": {"reasons": reasons}})
    if row:
        row.status = "Registered"
    else:
        row = CampRSVP(camp_id=camp.id, user_id=user.id)
        db.add(row)
    db.commit()
    when = (camp.starts_at + timedelta(hours=5, minutes=30)).strftime("%d %b, %I:%M %p")
    notifier.notify_t(user.telegram_id, user.language, "camp_rsvp", title=notifier.esc(camp.title),
                      venue=notifier.esc(camp.venue), when=when)
    return {"status": "registered", "camp": camp_out(camp, _camp_counts(db, [camp.id])[camp.id], row)}


@router.get("/camps/{camp_id}/attendees")
def attendees(camp_id: int, user_id: int, db: Session = Depends(get_db)):
    camp = db.get(Camp, camp_id)
    if not camp:
        raise HTTPException(404, "Camp not found")
    if camp.created_by != user_id:
        raise HTTPException(403, "Only the organiser can see the attendee list.")
    rows = db.query(CampRSVP, User).join(User, CampRSVP.user_id == User.id).filter(CampRSVP.camp_id == camp.id,
                                                                                   CampRSVP.status != "Cancelled").all()
    return [{"id": u.id, "name": u.name, "blood_group": u.blood_group, "phone": u.phone, "status": r.status} for r, u in rows]


@router.post("/camps/{camp_id}/attend")
def mark_attended(camp_id: int, body: Attend, db: Session = Depends(get_db)):
    """Organiser confirms a donor donated at the camp: records the donation and awards points."""
    camp = db.get(Camp, camp_id)
    if not camp:
        raise HTTPException(404, "Camp not found")
    if camp.created_by != body.user_id:
        raise HTTPException(403, "Only the organiser can confirm attendance.")
    row = db.query(CampRSVP).filter_by(camp_id=camp.id, user_id=body.attendee_id).first()
    if not row or row.status == "Cancelled":
        raise HTTPException(404, "This donor has not registered for the camp.")
    if row.status == "Attended":
        return {"status": "already_attended"}
    donor = db.get(User, body.attendee_id)
    now = utcnow()
    row.status, row.attended_at = "Attended", now
    donor.last_donation_at = now  # the safe interval starts again
    logic.award(db, donor, CAMP_POINTS, f"Camp donation — {camp.title}")
    db.flush()
    achievements.evaluate(db, [donor])
    db.commit()
    notifier.notify_t(donor.telegram_id, donor.language, "camp_thanks", title=notifier.esc(camp.title), points=CAMP_POINTS)
    return {"status": "attended"}


@router.get("/users/{user_id}/camps")
def my_camps(user_id: int, db: Session = Depends(get_db)):
    rows = (db.query(CampRSVP, Camp).join(Camp, CampRSVP.camp_id == Camp.id)
            .filter(CampRSVP.user_id == user_id, CampRSVP.status != "Cancelled").order_by(Camp.starts_at.desc()).all())
    counts = _camp_counts(db, [c.id for _, c in rows])
    return [camp_out(c, counts[c.id], r) for r, c in rows]


@router.get("/camps/leaderboard")
def camp_leaderboard(db: Session = Depends(get_db)):
    camps = db.query(Camp).filter(Camp.status == "Completed").all()
    counts = _camp_counts(db, [c.id for c in camps])
    out = [camp_out(c, counts[c.id]) for c in camps]
    return sorted(out, key=lambda c: -c["attended"])[:10]

