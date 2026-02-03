"""Doctor schemas."""

from pydantic import EmailStr, Field, field_validator

from src.schemas.base import BaseSchema, ResponseSchema

# Default slot distribution percentages
DEFAULT_SLOT_DISTRIBUTION = {
    "first_visit": 20,
    "follow_up": 70,
    "emergency": 10,
}


class SlotDistribution(BaseSchema):
    """Slot distribution settings by type percentage."""

    first_visit: int = Field(20, ge=0, le=100, description="Percentage for first visit slots")
    follow_up: int = Field(70, ge=0, le=100, description="Percentage for follow-up slots")
    emergency: int = Field(10, ge=0, le=100, description="Percentage for emergency slots")

    @field_validator("emergency")
    @classmethod
    def validate_total(cls, v: int, info) -> int:
        """Ensure total percentages equal 100."""
        first_visit = info.data.get("first_visit", 20)
        follow_up = info.data.get("follow_up", 70)
        total = first_visit + follow_up + v
        if total != 100:
            raise ValueError(f"Slot distribution must total 100%, got {total}%")
        return v


class DoctorBase(BaseSchema):
    """Base doctor fields."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str | None = Field(None, max_length=20)
    specialisation: str | None = Field(None, max_length=100)
    licence_number: str | None = Field(None, max_length=50)
    bio: str | None = None


class DoctorCreate(DoctorBase):
    """Doctor registration payload."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    default_slot_duration_minutes: int = Field(30, ge=15, le=120)
    booking_window_days: int = Field(30, ge=7, le=90)
    max_daily_appointments: int = Field(20, ge=1, le=50)
    slot_distribution: SlotDistribution | None = None
    auto_generate_days: int = Field(90, ge=30, le=365)


class DoctorUpdate(BaseSchema):
    """Doctor update payload."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    phone: str | None = Field(None, max_length=20)
    specialisation: str | None = Field(None, max_length=100)
    bio: str | None = None
    default_slot_duration_minutes: int | None = Field(None, ge=15, le=120)
    booking_window_days: int | None = Field(None, ge=7, le=90)
    max_daily_appointments: int | None = Field(None, ge=1, le=50)
    slot_distribution: SlotDistribution | None = None
    auto_generate_days: int | None = Field(None, ge=30, le=365)


class DoctorResponse(ResponseSchema, DoctorBase):
    """Doctor response."""

    email: EmailStr
    default_slot_duration_minutes: int
    booking_window_days: int
    max_daily_appointments: int
    slot_distribution: dict
    auto_generate_days: int
    is_active: bool
