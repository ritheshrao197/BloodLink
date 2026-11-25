from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from logic import BLOOD_GROUPS


def _check_group(v: str) -> str:
    v = v.strip().upper()
    if v not in BLOOD_GROUPS:
        raise ValueError(f"blood_group must be one of {', '.join(BLOOD_GROUPS)}")
    return v


Sex = Literal["male", "female", "other"]


class HealthBody(BaseModel):
    sex: Optional[Sex] = None
    date_of_birth: Optional[date] = None
    weight_kg: Optional[int] = Field(default=None, ge=20, le=250)


def _check_conditions(v: Optional[list[str]]) -> Optional[list[str]]:
    from eligibility import PERMANENT

    if v is None:
        return v
    unknown = [c for c in v if c not in PERMANENT]
    if unknown:
        raise ValueError(f"unknown condition(s): {', '.join(unknown)}")
    return sorted(set(v))


class ScreeningBody(BaseModel):
    """Answer to the permanent-conditions check: the codes that apply (empty list = none)."""
    conditions: list[str]

    _c = field_validator("conditions")(_check_conditions)


class Screening(BaseModel):
    """Answers to the pre-donation questionnaire (see eligibility.QUESTIONS)."""
    answers: dict[str, bool] = {}
    conditions: Optional[list[str]] = None  # permanent-conditions answer, for donors who have not answered it yet
    basics_confirmed: bool = False  # "I am 18-65 years old and weigh at least 45 kg" (when the profile lacks them)
    health: Optional[HealthBody] = None  # optionally save health basics at the same time

    _c = field_validator("conditions")(_check_conditions)


class EligibilityBody(BaseModel):
    user_id: Optional[int] = None
    telegram_id: Optional[str] = None
    screening: Screening = Screening()


class LocationBody(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    blood_group: str
    city: str = Field(min_length=1, max_length=80)
    state: Optional[str] = None
    language: Literal["en", "kn", "hi", "ml", "ta", "te", "bn", "as", "kok", "tcy"] = "en"
    phone: Optional[str] = None
    role: Literal["donor", "hospital", "blood_bank"] = "donor"
    referred_by: Optional[str] = None
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None
    sex: Optional[Sex] = None
    date_of_birth: Optional[date] = None
    weight_kg: Optional[int] = Field(default=None, ge=20, le=250)
    conditions: Optional[list[str]] = None  # permanent-conditions check (required for donors); never stored

    _bg = field_validator("blood_group")(_check_group)
    _c = field_validator("conditions")(_check_conditions)

    @model_validator(mode="after")
    def _donor_screening(self):
        if self.role == "donor":
            missing = [f for f in ("sex", "date_of_birth", "weight_kg", "conditions") if getattr(self, f) is None]
            if missing:
                raise ValueError(f"donors must answer: {', '.join(missing)}")
        return self

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
    requester_language: Optional[Literal["en", "kn", "hi", "ml", "ta", "te", "bn", "as", "kok", "tcy"]] = None

    _bg = field_validator("blood_group")(_check_group)
    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    lng: Optional[float] = Field(default=None, ge=-180, le=180)


class DonateBody(BaseModel):
    donor_telegram_id: Optional[str] = None
    user_id: Optional[int] = None
    confirmed: bool = True
    screening: Optional[Screening] = None


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
    language: Literal["en", "kn", "hi", "ml", "ta", "te", "bn", "as", "kok", "tcy"]
