"""Realistic demo data: a year of simulated network activity.

Every number is derived from simulated history (registrations, referrals, SOS requests, donations, voucher
redemptions), so points, badges, leaderboards, referral stats and admin analytics are all mutually consistent.
The output is deterministic (fixed random seed) apart from timestamps, which are relative to "now".

    python seed_data.py            # seed only if the database is empty
    python seed_data.py --reset    # wipe everything and re-seed
    python seed_data.py --refresh  # replace demo data, keep real accounts (those linked to Telegram)
"""

import math
import random
import sys
from datetime import date, datetime, timedelta

from sqlalchemy import or_
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
import achievements
import eligibility
import locations
import logic
from models import BloodRequest, Donation, PointLog, Referral, Reward, User, utcnow

SEED_VERSION = "5"  # bump to make deployments with AUTO_SEED=1 refresh their demo data once
N_DONORS = 700
N_HISTORY_REQUESTS = 760
HISTORY_DAYS = 540
IST = timedelta(hours=5, minutes=30)

# (state, district, weight): where people live and where requests come from
AREAS = [
    ("Karnataka", "Bengaluru Urban", 30), ("Karnataka", "Dakshina Kannada", 15), ("Karnataka", "Mysuru", 8),
    ("Karnataka", "Udupi", 7), ("Karnataka", "Belagavi", 4), ("Karnataka", "Dharwad", 4),
    ("Karnataka", "Kalaburagi", 3), ("Karnataka", "Shivamogga", 3), ("Karnataka", "Bengaluru Rural", 2),
    ("Karnataka", "Hassan", 2), ("Karnataka", "Tumakuru", 2), ("Karnataka", "Kodagu", 1),
    ("Maharashtra", "Mumbai City", 6), ("Maharashtra", "Mumbai Suburban", 6), ("Maharashtra", "Pune", 7),
    ("Maharashtra", "Nagpur", 3), ("Maharashtra", "Thane", 3),
    ("Tamil Nadu", "Chennai", 8), ("Tamil Nadu", "Coimbatore", 4), ("Tamil Nadu", "Madurai", 3),
    ("Tamil Nadu", "Vellore", 2),
    ("Kerala", "Ernakulam", 5), ("Kerala", "Thiruvananthapuram", 4), ("Kerala", "Kozhikode", 3),
    ("Kerala", "Thrissur", 2), ("Kerala", "Kasaragod", 2),
    ("Delhi", "New Delhi", 4), ("Delhi", "South Delhi", 3), ("Delhi", "Central Delhi", 2),
    ("Delhi", "South East Delhi", 2),
    ("Goa", "North Goa", 2), ("Goa", "South Goa", 1),
]
assert all(d in locations.LOCATIONS[s] for s, d, _ in AREAS)

# Approximate Indian ABO/Rh distribution; requests skew towards rare groups (those are the ones that need SOS)
DONOR_GROUPS = {"O+": 32, "B+": 31, "A+": 22, "AB+": 8, "O-": 2.5, "B-": 2.2, "A-": 1.6, "AB-": 0.7}
REQUEST_GROUPS = {"O+": 27, "B+": 26, "A+": 19, "AB+": 7, "O-": 6, "B-": 5, "A-": 4, "AB-": 2}

FIRST_M = ["Aarav", "Abhishek", "Aditya", "Ajay", "Akash", "Amit", "Anand", "Anil", "Arjun", "Ashwin", "Deepak",
           "Ganesh", "Harish", "Karthik", "Kiran", "Manoj", "Mohan", "Naveen", "Nikhil", "Pradeep", "Prakash",
           "Pranav", "Rahul", "Rajesh", "Rakesh", "Ravi", "Rohan", "Sachin", "Sandeep", "Sanjay", "Santosh",
           "Shreyas", "Siddharth", "Sunil", "Suresh", "Tejas", "Varun", "Vijay", "Vikram", "Vinay", "Vishal",
           "Yash", "Imran", "Faisal", "Irfan", "Joel", "Melwyn", "Rohit", "Gautam", "Hemanth", "Darshan"]
FIRST_F = ["Aishwarya", "Ananya", "Anjali", "Bhavana", "Deepa", "Divya", "Gayathri", "Harini", "Isha", "Kavya",
           "Keerthi", "Lakshmi", "Meera", "Megha", "Nandini", "Neha", "Nisha", "Pooja", "Priya", "Rashmi",
           "Riya", "Sahana", "Shreya", "Shruti", "Sneha", "Swathi", "Tanvi", "Varsha", "Vidya", "Fatima",
           "Ayesha", "Sana", "Zoya", "Sharon", "Reshma", "Pallavi", "Aparna", "Chaitra", "Spoorthi", "Akshatha"]
SURNAMES = {
    "Karnataka": ["Shetty", "Rao", "Hegde", "Gowda", "Kamath", "Pai", "Bhat", "Nayak", "Kulkarni", "Patil",
                  "Murthy", "Reddy", "Prabhu", "Acharya", "Shenoy", "Poojary", "D'Souza", "Pinto", "Fernandes",
                  "Kotian", "Salian", "Bangera", "Hussain", "Ahmed", "Naik", "Desai"],
    "Kerala": ["Nair", "Menon", "Pillai", "Varghese", "Thomas", "Kurian", "Panicker", "Joseph", "Mathew",
               "Krishnan", "Nambiar", "Abdulla", "Rahman"],
    "Tamil Nadu": ["Iyer", "Krishnan", "Subramanian", "Raman", "Pandian", "Selvam", "Murugan", "Natarajan",
                   "Rajan", "Sundaram", "Venkatesh", "Ibrahim"],
    "Maharashtra": ["Deshpande", "Joshi", "Patil", "Kulkarni", "Pawar", "Jadhav", "Shinde", "Gokhale", "Bhosale",
                    "More", "Sawant", "Shaikh", "Mehta"],
    "Delhi": ["Sharma", "Verma", "Gupta", "Singh", "Malhotra", "Kapoor", "Chopra", "Arora", "Khan", "Bansal",
              "Saxena", "Mishra", "Ahuja"],
    "Goa": ["Naik", "Fernandes", "D'Souza", "Kamat", "Gaonkar", "Rodrigues", "Pereira", "Desai"],
}
# Spoken language for Telegram messages, by state
LANG_BY_STATE = {"Karnataka": {"kn": 45, "en": 50, "hi": 5}, "Delhi": {"hi": 55, "en": 45},
                 "Maharashtra": {"hi": 30, "en": 70}}
URGENCY = {"Critical": 28, "High": 47, "Normal": 25}
# Median minutes until the first donor responds, by urgency
RESPONSE_MEDIAN = {"Critical": 9, "High": 24, "Normal": 70}
UNITS = {1: 55, 2: 28, 3: 11, 4: 6}

# Live feed: what's open right now (minutes ago, urgency, units, units already pledged)
ACTIVE = [(2, "Critical", 2, 0), (4, "Critical", 1, 0), (9, "High", 1, 0), (14, "Critical", 3, 1),
          (22, "High", 2, 0), (31, "High", 1, 0), (47, "Normal", 2, 1), (63, "Critical", 2, 1),
          (85, "High", 1, 0), (130, "Normal", 1, 0), (190, "High", 3, 2), (260, "Normal", 2, 0),
          (60 * 9, "Normal", 1, 0), (60 * 20, "Normal", 2, 1)]


def rain_chance(state: str | None, when: datetime) -> float:
    """Rough monsoon climatology: SW monsoon Jun-Sep (strongest on the west coast), NE monsoon Oct-Dec in Tamil Nadu."""
    m = (when + IST).month
    if 6 <= m <= 9:
        return 0.6 if state in ("Kerala", "Goa") else 0.45 if state in ("Karnataka", "Maharashtra") else 0.3
    if 10 <= m <= 12 and state in ("Tamil Nadu", "Kerala"):
        return 0.35
    return 0.05


def pick(rng: random.Random, weights: dict):
    return rng.choices(list(weights), weights=list(weights.values()))[0]


def phone(rng: random.Random) -> str:
    return f"+91 {rng.choice('6789')}{rng.randint(1000, 9999)} {rng.randint(10000, 99999)}"


def daytime(rng: random.Random, day: datetime) -> datetime:
    """A random moment on `day`, concentrated in waking hours IST, returned as naive UTC."""
    hour_ist = min(23.9, max(6.0, rng.gauss(14.5, 4.0)))
    start = datetime(day.year, day.month, day.day) - IST
    return start + timedelta(hours=hour_ist, seconds=rng.randint(0, 59))


def seed(db: Session) -> None:
    rng = random.Random(20261117)
    now = utcnow()
    area_w = [w for *_, w in AREAS]
    logs: list[tuple] = []      # (user, amount, reason, when): turned into PointLog rows once ids exist
    vouchers: list[dict] = []
    codes: set[str] = {c for (c,) in db.query(User.referral_code)}

    def code() -> str:
        while True:
            c = f"USER_{rng.randint(10000, 99999)}"
            if c not in codes:
                codes.add(c)
                return c

    def earn(u: User, amount: int, reason: str, when: datetime) -> None:
        u.points += amount
        logs.append((u, amount, reason, when))

    # ---------- people ----------
    people = []
    for _ in range(N_DONORS):
        state, district, _w = rng.choices(AREAS, weights=area_w)[0]
        female = rng.random() < 0.42
        first = rng.choice(FIRST_F if female else FIRST_M)
        people.append({"state": state, "district": district, "female": female,
                       "name": f"{first} {rng.choice(SURNAMES[state])}",
                       # how likely this person is to answer an SOS: a few heroes, a long tail
                       "zeal": rng.paretovariate(1.6),
                       # a founding cohort (launch drive), then steady growth that accelerates
                       "joined": now - timedelta(days=HISTORY_DAYS - rng.uniform(0, 30) if rng.random() < 0.14
                                                 else HISTORY_DAYS * (1 - rng.random() ** 0.8),
                                                 minutes=rng.randint(0, 1440))})
    people.sort(key=lambda p: p["joined"])

    ambassadors: list[User] = []  # campus/community volunteers who refer lots of people
    donors: list[User] = []
    for i, p in enumerate(people):
        u = User(name=p["name"], blood_group=pick(rng, DONOR_GROUPS), city=p["district"], state=p["state"],
                 language=pick(rng, LANG_BY_STATE.get(p["state"], {"en": 1})), phone=phone(rng), role="donor",
                 referral_code=code(), points=0, total_donations=0, is_available=True,
                 created_at=p["joined"], sex="female" if p["female"] else "male",
                 # most donors are 18-45; weights are realistic for eligible adults
                 date_of_birth=date(now.year - int(min(62, max(18, rng.gauss(29, 8)))), rng.randint(1, 12), rng.randint(1, 28)),
                 weight_kg=int(max(46, rng.gauss(58 if p["female"] else 70, 9))))
        u.zeal = p["zeal"]
        earn(u, logic.POINTS_REGISTER, "Registration bonus", u.created_at)
        earlier = [d for d in donors if d.created_at < u.created_at - timedelta(days=1)]
        if earlier and rng.random() < 0.3:
            pool = [a for a in ambassadors if a.state == u.state] if rng.random() < 0.3 else []
            referrer = rng.choice(pool or [d for d in earlier if d.state == u.state] or earlier)
            u.referred_by = referrer.referral_code
            earn(u, logic.POINTS_WELCOME_BONUS, f"Welcome bonus (invited by {referrer.name})", u.created_at)
            earn(referrer, logic.POINTS_REFERRAL_REGISTER, f"Referral: {u.name} registered", u.created_at)
            u.referral = {"referrer": referrer, "status": "Registered",
                          "points_awarded": logic.POINTS_REFERRAL_REGISTER, "created_at": u.created_at}
        else:
            u.referral = None
        if i % 29 == 5:
            u.zeal += 2  # volunteers who recruit also tend to show up
            ambassadors.append(u)
        donors.append(u)
    db.add_all(donors)

    hospitals = []
    for state, district, w in AREAS:
        names = locations.hospitals_for(state, district)
        for name in names[: 2 if w >= 6 else 1]:
            if not name.startswith("Govt. District Hospital"):
                hospitals.append(User(name=name, blood_group="O+", city=district, state=state, role="hospital",
                                      phone=f"+91 {rng.randint(20, 99)} {rng.randint(2000, 9999)} {rng.randint(1000, 9999)}",
                                      referral_code=code(), points=0, is_verified=True, is_available=True,
                                      created_at=now - timedelta(days=rng.randint(200, HISTORY_DAYS + 20))))
    db.add_all(hospitals)

    by_district: dict[str, list[User]] = {}
    by_state: dict[str, list[User]] = {}
    for d in donors:
        by_district.setdefault(d.city, []).append(d)
        by_state.setdefault(d.state, []).append(d)

    def respond(req: BloodRequest, donor: User, when: datetime) -> None:
        quick = when - req.created_at <= timedelta(minutes=logic.QUICK_RESPONSE_MINUTES)
        total = logic.POINTS_DONATION
        earn(donor, logic.POINTS_DONATION, f"Successful donation — request #{req.id}", when)
        if quick:
            total += logic.POINTS_QUICK_RESPONSE
            earn(donor, logic.POINTS_QUICK_RESPONSE, f"Quick response (< 5 min) — request #{req.id}", when)
        if donor.last_donation_at and when - donor.last_donation_at >= timedelta(days=logic.STREAK_DAYS):
            total += logic.POINTS_STREAK
            earn(donor, logic.POINTS_STREAK, f"Streak bonus (3-month return) — request #{req.id}", when)
        if donor.total_donations == 0 and donor.referral:
            referrer = donor.referral["referrer"]
            earn(referrer, logic.POINTS_REFERRAL_DONATION, f"Referral: {donor.name} donated", when)
            donor.referral["status"] = "Donated"
            donor.referral["points_awarded"] += logic.POINTS_REFERRAL_DONATION
            vouchers.append({"user": referrer, "reward_name": logic.REFERRAL_VOUCHER["name"], "points_cost": 0,
                             "voucher_code": logic.voucher_code(logic.REFERRAL_VOUCHER["prefix"]), "created_at": when})
        donor.total_donations += 1
        donor.last_donation_at = when
        db.add(Donation(request_id=req.id, donor_id=donor.id, points_awarded=total, quick_response=quick,
                        weather="rain" if rng.random() < rain_chance(req.state, when) else "dry", created_at=when))
        req.units_fulfilled += 1
        req.fulfilled_by = f"{req.fulfilled_by}, {donor.name}" if req.fulfilled_by else donor.name

    def candidates(req: BloodRequest, at: datetime) -> list[User]:
        ok = set(logic.compatible_donor_groups(req.blood_group))
        def eligible(pool):
            return [d for d in pool if d.blood_group in ok and d.created_at < at and d.is_available
                    and (not d.last_donation_at or at - d.last_donation_at >= timedelta(days=eligibility.interval_days(d)))]

        local = eligible(by_district.get(req.city, []))
        if len(local) >= max(3, req.units_needed * 2):
            return local
        # Few matches nearby: the alert widens to the rest of the state
        return local + [d for d in eligible(by_state.get(req.state, [])) if d.city != req.city]

    def new_request(created: datetime, urgency: str, units: int) -> BloodRequest:
        state, district, _w = rng.choices(AREAS, weights=area_w)[0]
        hosp = rng.choice(locations.hospitals_for(state, district))
        local_h = [h for h in hospitals if h.name == hosp]
        by_hospital = local_h and rng.random() < 0.45
        female = rng.random() < 0.5
        requester = (local_h[0].name if by_hospital else
                     f"{rng.choice(FIRST_F if female else FIRST_M)} {rng.choice(SURNAMES[state])}")
        req = BloodRequest(requester_name=requester, blood_group=pick(rng, REQUEST_GROUPS), hospital=hosp,
                           city=district, state=state, units_needed=units, units_fulfilled=0, urgency=urgency,
                           status="Active", is_verified=by_hospital or rng.random() < 0.55,
                           contact_phone=local_h[0].phone if by_hospital else phone(rng),
                           requester_language=pick(rng, LANG_BY_STATE.get(state, {"en": 1})), created_at=created)
        db.add(req)
        db.flush()
        return req

    def take(pool: list[User], k: int) -> list[User]:
        chosen = []
        pool = list(pool)
        while pool and len(chosen) < k:
            d = rng.choices(pool, weights=[p.zeal for p in pool])[0]
            pool.remove(d)
            chosen.append(d)
        return chosen

    db.flush()  # ids for users, needed by Donation rows

    # ---------- a year of SOS history, oldest first (ids follow time, like real traffic) ----------
    # request volume grows with the network: most traffic is recent
    starts = sorted(now - timedelta(days=(HISTORY_DAYS - 20) * (rng.random() ** 1.5)) for _ in range(N_HISTORY_REQUESTS))
    for day in starts:
        created = daytime(rng, day)
        if created > now - timedelta(days=1):
            continue
        urgency = pick(rng, URGENCY)
        req = new_request(created, urgency, pick(rng, UNITS))
        pool = candidates(req, created)
        req.notified_count = len(pool)
        if not pool or rng.random() < 0.04:
            req.status = "Cancelled"  # resolved by the hospital's own blood bank / patient transferred
            continue
        responders = take(pool, req.units_needed)
        t = created + timedelta(minutes=max(1.5, rng.lognormvariate(math.log(RESPONSE_MEDIAN[urgency]), 0.8)))
        for donor in responders:
            respond(req, donor, t)
            t += timedelta(minutes=rng.uniform(4, 45))
        if req.units_fulfilled >= req.units_needed:
            req.status, req.fulfilled_at = "Fulfilled", t - timedelta(minutes=1)
        else:
            req.status = "Cancelled"

    # Some donors are temporarily unavailable (recently donated, travelling, unwell)
    for d in donors:
        recent = d.last_donation_at and now - d.last_donation_at < timedelta(days=45)
        if rng.random() < (0.55 if recent else 0.1):
            d.is_available = False

    # ---------- the live feed ----------
    for minutes, urgency, units, pledged in ACTIVE:
        created = now - timedelta(minutes=minutes, seconds=rng.randint(0, 50))
        req = new_request(created, urgency, units)
        if urgency == "Critical":
            req.is_verified = True
        pool = candidates(req, created)
        for _ in range(8):  # the live feed should show alerts actually going out
            if pool:
                break
            req.blood_group = pick(rng, REQUEST_GROUPS)
            pool = candidates(req, created)
        req.notified_count = len(pool)
        for k, donor in enumerate(take(pool, pledged)):
            respond(req, donor, created + timedelta(minutes=min(minutes * 0.8, 3 + 9 * k + rng.uniform(0, 6))))

    # ---------- voucher redemptions ----------
    catalog = sorted(logic.REWARDS, key=lambda r: r["cost"])
    for d in donors:
        if d.points >= 150 and rng.random() < 0.4:
            affordable = [r for r in catalog if r["cost"] <= d.points - 50]
            if not affordable:
                continue
            reward = rng.choices(affordable, weights=[4, 3, 2, 1][: len(affordable)])[0]
            last = max(when for u, _a, _r, when in logs if u is d)
            when = last + (now - last) * rng.uniform(0.1, 0.9)
            earn(d, -reward["cost"], f"Redeemed {reward['name']}", when)
            vouchers.append({"user": d, "reward_id": reward["id"], "reward_name": reward["name"],
                             "points_cost": reward["cost"], "voucher_code": logic.voucher_code(reward["prefix"]),
                             "status": rng.choice(["Issued", "Issued", "Used"]), "created_at": when})

    for d in donors:
        d.is_verified = d.total_donations > 0 and rng.random() < 0.9 or rng.random() < 0.2
        if d.is_available:  # availability streaks of varying length, for "The Constant"
            start = max(d.created_at, d.last_donation_at or d.created_at)
            d.available_since = start + (now - start) * rng.uniform(0, 0.5)
        else:
            d.available_since = None
    db.add_all(Referral(referrer_id=d.referral["referrer"].id, referred_id=d.id, status=d.referral["status"],
                        points_awarded=d.referral["points_awarded"], created_at=d.referral["created_at"])
               for d in donors if d.referral)
    db.flush()

    seed_community(db, rng, now, donors, hospitals, earn)

    # ---------- achievements, dated to the moment each was earned ----------
    def verified_at(u: User) -> datetime:
        return min(now, u.created_at + timedelta(days=rng.uniform(1, 20)))

    achievements.evaluate(db, donors, now=now, award=earn, timeless_at=verified_at,
                          new_since=now - timedelta(days=7), notify=False)
    standouts = sorted(donors, key=lambda u: -(u.total_donations * 3 + u.zeal))[:4]
    fav = achievements.BY_KEY["admins_favorite"]
    for u in standouts:
        when = now - timedelta(days=rng.uniform(3, 60))
        db.add(achievements.UserAchievement(user_id=u.id, key=fav["key"], unlocked_at=when, is_new=False))
        earn(u, fav["points"], f"Achievement unlocked: {fav['icon']} {fav['name']}", when)
    for d in donors:
        logic.update_badge(d)

    # Insert ledgers in time order so "latest activity" lists read naturally
    db.add_all(PointLog(user_id=u.id, amount=a, reason=r, created_at=w)
               for u, a, r, w in sorted(logs, key=lambda x: x[3]))
    db.add_all(Reward(user_id=v.pop("user").id, **v) for v in sorted(vouchers, key=lambda v: v["created_at"]))
    for d in donors:
        del d.zeal, d.referral
    db.commit()


# ---------- teams and camps ----------
# Fictional organisations (not real institutions), spread over the demo districts
TEAMS = [
    ("Karavali Institute of Technology · CSE", "college", "Karnataka", "Dakshina Kannada"),
    ("Karavali Institute of Technology · ECE", "college", "Karnataka", "Dakshina Kannada"),
    ("Netravati Arts & Science College", "college", "Karnataka", "Dakshina Kannada"),
    ("Udupi Coastal Engineering College", "college", "Karnataka", "Udupi"),
    ("Mysuru Heritage University", "college", "Karnataka", "Mysuru"),
    ("Garden City Tech Park Volunteers", "company", "Karnataka", "Bengaluru Urban"),
    ("Silk Board Software Labs", "company", "Karnataka", "Bengaluru Urban"),
    ("Marina Fintech Pvt Ltd", "company", "Tamil Nadu", "Chennai"),
    ("Deccan Riders Club", "community", "Maharashtra", "Pune"),
    ("Backwaters Running Club", "community", "Kerala", "Ernakulam"),
    ("Lifeline Blood Warriors", "community", "Delhi", "New Delhi"),
    ("The Bloodline Squad", "group", "Karnataka", "Bengaluru Urban"),
]
CAMPS = [
    # title, organiser team index (or None = a hospital), state, district, days from now, expected
    ("KIT Mega Blood Drive", 0, "Karnataka", "Dakshina Kannada", 4, 120),
    ("Tech Park Donate-a-Thon", 5, "Karnataka", "Bengaluru Urban", 9, 150),
    ("Riders for Life Camp", 8, "Maharashtra", "Pune", 2, 60),
    ("Monsoon Blood Drive", None, "Kerala", "Ernakulam", 12, 80),
    ("Heritage Campus Donation Day", 4, "Karnataka", "Mysuru", 20, 100),
    ("Marina Corporate Camp", 7, "Tamil Nadu", "Chennai", 6, 70),
    ("Independence Day Blood Drive", 0, "Karnataka", "Dakshina Kannada", -95, 100),
    ("Founders' Day Camp", 3, "Karnataka", "Udupi", -60, 80),
    ("World Blood Donor Day Camp", None, "Karnataka", "Bengaluru Urban", -156, 200),
    ("Run & Give Camp", 9, "Kerala", "Ernakulam", -40, 60),
]


def seed_community(db: Session, rng: random.Random, now: datetime, donors: list[User], hospitals: list[User], earn) -> None:
    from models import Camp, CampRSVP, Team, TeamMember

    donation_times: dict[int, list[datetime]] = {}
    for donor_id, at in db.query(Donation.donor_id, Donation.created_at):
        donation_times.setdefault(donor_id, []).append(at)

    teams = []
    for i, (name, kind, state, district) in enumerate(TEAMS):
        local = [d for d in donors if d.city == district] or [d for d in donors if d.state == state]
        created = now - timedelta(days=rng.uniform(150, 420))
        team = Team(name=name, kind=kind, city=district, state=state, invite_code=f"TEAM-{1001 + i}", created_at=created)
        db.add(team)
        db.flush()
        members = rng.sample(local, min(len(local), rng.randint(8, 30)))
        team.created_by = members[0].id
        for k, u in enumerate(members):
            joined = max(u.created_at, created) + timedelta(days=rng.uniform(0, 60))
            db.add(TeamMember(team_id=team.id, user_id=u.id, role="owner" if k == 0 else "member", joined_at=min(joined, now)))
        teams.append((team, members))

    for title, team_idx, state, district, days, expected in CAMPS:
        start_ist = (now + timedelta(days=days)).replace(hour=9, minute=30, second=0, microsecond=0)
        starts = start_ist - IST
        team, members = teams[team_idx] if team_idx is not None else (None, [])
        hosp = next((h for h in hospitals if h.city == district), None)
        organizer = team.name if team else (hosp.name if hosp else f"District Blood Bank, {district}")
        venue = (f"Main auditorium, {team.name.split(' · ')[0]}" if team and team.kind == "college"
                 else "Community hall" if team else hosp.name if hosp else f"District Hospital, {district}")
        camp = Camp(title=title, organizer=organizer, team_id=team.id if team else None, venue=venue, city=district, state=state,
                    starts_at=starts, ends_at=starts + timedelta(hours=7), expected_donors=expected,
                    created_by=(members[0].id if members else (hosp.id if hosp else None)),
                    status="Upcoming" if days > 0 else "Completed", created_at=starts - timedelta(days=rng.uniform(10, 30)),
                    description="Free health check-up and refreshments for every donor. Please bring a photo ID.")
        db.add(camp)
        db.flush()
        pool = list({u.id: u for u in members + [d for d in donors if d.city == district]}.values())
        for u in rng.sample(pool, min(len(pool), int(expected * rng.uniform(0.35, 0.7)))):
            interval = timedelta(days=eligibility.interval_days(u))
            times = donation_times.get(u.id, [])
            # only donors who would be eligible on the day, and whose later donations keep a safe gap
            if any(abs(t - starts) < interval for t in times) or u.created_at > camp.created_at:
                continue
            rsvp = CampRSVP(camp_id=camp.id, user_id=u.id, created_at=camp.created_at + timedelta(days=rng.uniform(0, 9)))
            if days < 0 and rng.random() < 0.8:
                rsvp.status, rsvp.attended_at = "Attended", starts + timedelta(hours=rng.uniform(0.5, 6.5))
                earn(u, 100, f"Camp donation — {title}", rsvp.attended_at)
                times.append(rsvp.attended_at)
                donation_times[u.id] = times
                u.last_donation_at = max(u.last_donation_at or rsvp.attended_at, rsvp.attended_at)
            db.add(rsvp)
    db.flush()


# ---------- maintenance ----------

def _ensure_meta(db: Session) -> None:
    from sqlalchemy import text

    db.execute(text("CREATE TABLE IF NOT EXISTS app_meta (key VARCHAR PRIMARY KEY, value VARCHAR)"))


def seed_version(db: Session) -> str | None:
    from sqlalchemy import text

    _ensure_meta(db)
    return db.execute(text("SELECT value FROM app_meta WHERE key = 'seed_version'")).scalar()


def mark_seeded(db: Session) -> None:
    from sqlalchemy import text

    _ensure_meta(db)
    db.execute(text("DELETE FROM app_meta WHERE key = 'seed_version'"))
    db.execute(text("INSERT INTO app_meta (key, value) VALUES ('seed_version', :v)"), {"v": SEED_VERSION})
    db.commit()


def clear_demo(db: Session) -> int:
    """Delete demo data. Accounts linked to Telegram, and SOS requests made from Telegram, are real and kept."""
    demo_users = [i for (i,) in db.query(User.id).filter(User.telegram_id.is_(None))]
    demo_reqs = [i for (i,) in db.query(BloodRequest.id).filter(BloodRequest.requester_telegram_id.is_(None))]
    db.query(Donation).filter(or_(Donation.donor_id.in_(demo_users), Donation.request_id.in_(demo_reqs))) \
        .delete(synchronize_session=False)
    db.query(achievements.UserAchievement).filter(achievements.UserAchievement.user_id.in_(demo_users)).delete(synchronize_session=False)
    from models import Camp, CampRSVP, ReminderLog, Team, TeamMember

    demo_teams = [i for (i,) in db.query(Team.id).filter(or_(Team.created_by.in_(demo_users), Team.created_by.is_(None)))]
    demo_camps = [i for (i,) in db.query(Camp.id).filter(or_(Camp.created_by.in_(demo_users), Camp.created_by.is_(None),
                                                              Camp.team_id.in_(demo_teams)))]
    db.query(CampRSVP).filter(or_(CampRSVP.user_id.in_(demo_users), CampRSVP.camp_id.in_(demo_camps))).delete(synchronize_session=False)
    db.query(Camp).filter(Camp.id.in_(demo_camps)).delete(synchronize_session=False)
    db.query(TeamMember).filter(or_(TeamMember.user_id.in_(demo_users), TeamMember.team_id.in_(demo_teams))).delete(synchronize_session=False)
    db.query(Team).filter(Team.id.in_(demo_teams)).delete(synchronize_session=False)
    db.query(ReminderLog).filter(ReminderLog.user_id.in_(demo_users)).delete(synchronize_session=False)
    db.query(Referral).filter(or_(Referral.referrer_id.in_(demo_users), Referral.referred_id.in_(demo_users))) \
        .delete(synchronize_session=False)
    db.query(Reward).filter(Reward.user_id.in_(demo_users)).delete(synchronize_session=False)
    db.query(PointLog).filter(PointLog.user_id.in_(demo_users)).delete(synchronize_session=False)
    db.query(BloodRequest).filter(BloodRequest.id.in_(demo_reqs)).delete(synchronize_session=False)
    db.query(User).filter(User.id.in_(demo_users)).delete(synchronize_session=False)
    for u in db.query(User):  # kept accounts may have pledged to demo requests that are now gone
        u.total_donations = db.query(Donation).filter(Donation.donor_id == u.id).count()
    db.commit()
    return len(demo_users)


def auto_seed(db: Session) -> str | None:
    """Startup hook: seed an empty database, or refresh demo data once when SEED_VERSION changes."""
    if db.query(User).count() == 0:
        seed(db)
        mark_seeded(db)
        return "seeded empty database"
    if seed_version(db) != SEED_VERSION:
        removed = clear_demo(db)
        seed(db)
        mark_seeded(db)
        return f"refreshed demo data to v{SEED_VERSION} (replaced {removed} demo accounts, kept Telegram-linked ones)"
    return None


def reset_and_seed() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
        mark_seeded(db)
    finally:
        db.close()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    if "--reset" in sys.argv:
        reset_and_seed()
        print("✅ Database reset and seed data inserted!")
    else:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            if "--refresh" in sys.argv:
                n = clear_demo(db)
                seed(db)
                mark_seeded(db)
                print(f"✅ Replaced {n} demo accounts with fresh demo data (Telegram-linked accounts kept).")
            elif db.query(User).count():
                print("Database already has data. Use --refresh or --reset.")
            else:
                seed(db)
                mark_seeded(db)
                print("✅ Seed data inserted!")
        finally:
            db.close()
