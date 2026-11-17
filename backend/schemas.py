from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from logic import BLOOD_GROUPS


def _check_group(v: str) -> str:
    v = v.strip().upper()
    if v not in BLOOD_GROUPS:
        raise ValueError(f"blood_group must be one of {', '.join(BLOOD_GROUPS)}")
    return v


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    blood_group: str
    city: str = Field(min_length=1, max_length=80)
    state: Optional[str] = None
    language: Literal["en", "kn", "hi"] = "en"
    phone: Optional[str] = None
    role: Literal["donor", "hospital"] = "donor"
    referred_by: Optional[str] = None
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None

    _bg = field_validator("blood_group")(_check_group)

    @field_validator("name", "city")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be empty")
        return v


class SOSCreate(BaseModel):
    requester_name: str = Field(min_length=1, max_length=80)
    blood_group: str
    hospital: str = Field(min_length=1, max_length=120)
    city: str = Field(min_length=1, max_length=80)
    state: Optional[str] = None
    units_needed: int = Field(default=1, ge=1, le=10)
    urgency: Literal["Critical", "High", "Normal"] = "High"
    contact_phone: Optional[str] = None
    requester_telegram_id: Optional[str] = None
    requester_language: Optional[Literal["en", "kn", "hi"]] = None

    _bg = field_validator("blood_group")(_check_group)


class DonateBody(BaseModel):
    donor_telegram_id: Optional[str] = None
    user_id: Optional[int] = None
    confirmed: bool = True


class RedeemBody(BaseModel):
    user_id: Optional[int] = None
    telegram_id: Optional[str] = None


class LinkTelegramBody(BaseModel):
    referral_code: str
    telegram_id: str
    telegram_username: Optional[str] = None


class AvailabilityBody(BaseModel):
    is_available: bool


class LanguageBody(BaseModel):
    language: Literal["en", "kn", "hi"]
