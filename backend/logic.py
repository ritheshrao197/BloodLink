"""Business rules: ABO/Rh matching, points, badges, vouchers. Strictly rule-based (no AI/ML)."""

import random
import string

from sqlalchemy.orm import Session

from models import PointLog, User

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

# Recipient -> donor groups it can receive from
COMPATIBILITY = {
    "A+": ["A+", "A-", "O+", "O-"],
    "A-": ["A-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    "AB-": ["AB-", "A-", "B-", "O-"],
    "O+": ["O+", "O-"],
    "O-": ["O-"],
}

# Points (BLP)
POINTS_REGISTER = 50
POINTS_WELCOME_BONUS = 50  # new user who joined via a referral
POINTS_REFERRAL_REGISTER = 50
POINTS_DONATION = 100
POINTS_REFERRAL_DONATION = 200
POINTS_QUICK_RESPONSE = 20
POINTS_STREAK = 50
QUICK_RESPONSE_MINUTES = 5
STREAK_DAYS = 90
INFLUENCER_REFERRALS = 5

BADGES = [
    # name, min points, icon, title
    ("Bronze", 0, "🥉", "First Responder"),
    ("Silver", 101, "🥈", "Life Saver"),
    ("Gold", 501, "🥇", "Guardian Angel"),
    ("Platinum", 1000, "💎", "Legendary Hero"),
]

REWARDS = [
    {"id": 1, "name": "Coffee Voucher", "cost": 100, "prefix": "CAFE", "icon": "coffee",
     "description": "Free coffee at a partner café"},
    {"id": 2, "name": "Movie Ticket", "cost": 250, "prefix": "MOVIE", "icon": "film",
     "description": "One movie voucher at a partner cinema"},
    {"id": 3, "name": "Shopping Voucher", "cost": 500, "prefix": "SHOP", "icon": "shopping-bag",
     "description": "$10 online shopping gift card"},
    {"id": 4, "name": "College Merch", "cost": 1000, "prefix": "MERCH", "icon": "shirt",
     "description": "Custom BLOODLINK T-shirt"},
]
REFERRAL_VOUCHER = {"name": "$5 Referral Voucher", "prefix": "REF5"}


def compatible_donor_groups(recipient_group: str) -> list[str]:
    return COMPATIBILITY.get(recipient_group, [])


def can_donate(donor_group: str, recipient_group: str) -> bool:
    return donor_group in compatible_donor_groups(recipient_group)


def recipients_for(donor_group: str) -> list[str]:
    return [r for r, donors in COMPATIBILITY.items() if donor_group in donors]


def badge_for(points: int) -> str:
    badge = BADGES[0][0]
    for name, minimum, _, _ in BADGES:
        if points >= minimum:
            badge = name
    return badge


def badge_info(name: str) -> dict:
    for i, (badge, minimum, icon, title) in enumerate(BADGES):
        if badge == name:
            nxt = BADGES[i + 1] if i + 1 < len(BADGES) else None
            return {
                "name": badge, "icon": icon, "title": title, "min_points": minimum,
                "next": {"name": nxt[0], "min_points": nxt[1], "icon": nxt[2]} if nxt else None,
            }
    return badge_info("Bronze")


def update_badge(user: User) -> None:
    user.badge = badge_for(user.points or 0)


def award(db: Session, user: User, amount: int, reason: str) -> None:
    user.points = (user.points or 0) + amount
    update_badge(user)
    db.add(PointLog(user_id=user.id, amount=amount, reason=reason))


def new_referral_code(db: Session) -> str:
    while True:
        code = f"USER_{random.randint(10000, 99999)}"
        if not db.query(User).filter(User.referral_code == code).first():
            return code


def voucher_code(prefix: str) -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{suffix}"


def get_reward(reward_id: int) -> dict | None:
    return next((r for r in REWARDS if r["id"] == reward_id), None)
