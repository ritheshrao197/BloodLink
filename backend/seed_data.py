"""Demo data so the leaderboard, feed and analytics look alive.

    python seed_data.py          # seed only if the database is empty
    python seed_data.py --reset  # wipe everything and re-seed
"""

import sys
from datetime import timedelta

from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
import locations
import logic
from models import BloodRequest, Donation, PointLog, Referral, Reward, User, utcnow

USERS = [
    # name, group, city, points, donations, phone, role
    ("Karthik", "O-", "Bengaluru Urban", 650, 5, "+91 98450 11111", "donor"),
    ("Dr. Kavita Joshi", "AB-", "Bengaluru Urban", 480, 4, "+91 98450 22222", "donor"),
    ("Mohammad Farooq", "B+", "New Delhi", 320, 3, "+91 98110 33333", "donor"),
    ("Priya Sharma", "A+", "Mumbai City", 150, 1, "+91 98200 44444", "donor"),
    ("Rahul Verma", "O+", "Chennai", 120, 1, "+91 98400 55555", "donor"),
    ("Ananya Rao", "A-", "Bengaluru Urban", 270, 2, "+91 98450 66666", "donor"),
    ("Vikram Shetty", "B-", "Dakshina Kannada", 210, 2, "+91 98440 77777", "donor"),
    ("Sneha Kulkarni", "O+", "Bengaluru Urban", 95, 0, "+91 98450 88888", "donor"),
    ("Arjun Nair", "AB+", "Dakshina Kannada", 60, 0, "+91 98440 99999", "donor"),
    ("Fatima Sheikh", "O-", "Mumbai City", 540, 4, "+91 98200 12121", "donor"),
    ("Apollo Hospital, Bannerghatta Road", "O+", "Bengaluru Urban", 0, 0, "+91 80 2630 4050", "hospital"),
]

REQUESTS = [
    # requester, group, hospital, city, units, urgency, minutes ago, status
    ("Priya", "O-", "Apollo Hospital, Bannerghatta Road", "Bengaluru Urban", 2, "Critical", 3, "Active"),
    ("Suresh Kumar", "B+", "AIIMS New Delhi", "New Delhi", 1, "High", 25, "Active"),
    ("Meena Iyer", "A+", "Manipal Hospital, Old Airport Road", "Bengaluru Urban", 1, "Normal", 70, "Active"),
    ("Rohit Das", "AB-", "KMC Hospital, Attavar", "Dakshina Kannada", 3, "Critical", 12, "Active"),
    ("Lakshmi", "O+", "Fortis Hospital, Bannerghatta Road", "Bengaluru Urban", 1, "High", 60 * 26, "Fulfilled"),
    ("Imran", "B-", "Wenlock District Hospital", "Dakshina Kannada", 1, "High", 60 * 50, "Fulfilled"),
    ("Neha", "A-", "Narayana Health City", "Bengaluru Urban", 1, "Normal", 60 * 75, "Fulfilled"),
]


def seed(db: Session) -> None:
    now = utcnow()
    users = []
    for i, (name, bg, city, pts, dons, phone, role) in enumerate(USERS):
        u = User(name=name, blood_group=bg, city=city, state=locations.normalize(city)[0], points=pts, total_donations=dons, phone=phone, role=role,
                 referral_code=logic.new_referral_code(db), is_verified=i < 6 or role == "hospital",
                 is_available=name != "Rahul Verma",
                 last_donation_at=now - timedelta(days=30 + i * 15) if dons else None,
                 created_at=now - timedelta(days=60 - i))
        logic.update_badge(u)
        db.add(u)
        db.flush()
        db.add(PointLog(user_id=u.id, amount=pts, reason="Seeded demo balance", created_at=u.created_at))
        users.append(u)

    # Karthik referred a few people
    karthik = users[0]
    for friend, status in ((users[3], "Donated"), (users[7], "Registered"), (users[8], "Registered")):
        friend.referred_by = karthik.referral_code
        pts = logic.POINTS_REFERRAL_REGISTER + (logic.POINTS_REFERRAL_DONATION if status == "Donated" else 0)
        db.add(Referral(referrer_id=karthik.id, referred_id=friend.id, status=status, points_awarded=pts))
    db.add(Reward(user_id=karthik.id, reward_name=logic.REFERRAL_VOUCHER["name"], points_cost=0,
                  voucher_code=logic.voucher_code(logic.REFERRAL_VOUCHER["prefix"])))

    donors_for = {"O+": users[4], "B-": users[6], "A-": users[5]}
    for requester, bg, hospital, city, units, urgency, ago, status in REQUESTS:
        created = now - timedelta(minutes=ago)
        r = BloodRequest(requester_name=requester, blood_group=bg, hospital=hospital, city=city,
                         state=locations.normalize(city)[0],
                         units_needed=units, urgency=urgency, status=status, created_at=created,
                         is_verified=status == "Fulfilled" or urgency == "Critical")
        db.add(r)
        db.flush()
        if status == "Fulfilled":
            donor = donors_for[bg]
            r.units_fulfilled = units
            r.fulfilled_by = donor.name
            r.fulfilled_at = created + timedelta(minutes=18 + ago % 20)
            db.add(Donation(request_id=r.id, donor_id=donor.id, points_awarded=logic.POINTS_DONATION,
                            created_at=r.fulfilled_at))
    db.commit()


def reset_and_seed() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
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
            if db.query(User).count():
                print("Database already has data. Use --reset to wipe and re-seed.")
            else:
                seed(db)
                print("✅ Seed data inserted!")
        finally:
            db.close()
