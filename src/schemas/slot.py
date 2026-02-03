"""Slot schemas."""

from datetime import datetime

from pydantic import Field, field_validator

from src.models.patient import ComplianceLevel
from src.models.slot import SlotStatus, SlotType
from src.schemas.base import BaseSchema, ResponseSchema


class SlotBase(BaseSchema):
    """Base slot fields."""

    start_time: datetime
    end_time: datetime
    duration_minutes: int = Field(30, ge=15, le=120)

    @field_validator("end_time")
    @classmethod
    def validate_end_after_start(cls, v: datetime, info) -> datetime:
        """Ensure end_time is after start_time."""
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class SlotCreate(SlotBase):
    """Single slot creation."""

    slot_type: SlotType = SlotType.FOLLOW_UP
    is_priority_only: bool = False
    is_urgent_only: bool = False
    min_compliance_level: ComplianceLevel | None = None


class SlotBulkCreate(BaseSchema):
    """Bulk slot creation for recurring schedules."""

    start_date: datetime  # Start date for generation
    end_date: datetime  # End date for generation
    weekdays: list[int] = Field(..., min_length=1)  # 0=Monday, 6=Sunday
    start_times: list[str] = Field(..., min_length=1)  # ["09:00", "14:00"]
    duration_minutes: int = Field(30, ge=15, le=120)
    slot_type: SlotType = SlotType.FOLLOW_UP
    is_priority_only: bool = False
    is_urgent_only: bool = False
    min_compliance_level: ComplianceLevel | None = None

    @field_validator("weekdays")
    @classmethod
    def validate_weekdays(cls, v: list[int]) -> list[int]:
        """Ensure valid weekday values."""
        for day in v:
            if day < 0 or day > 6:
                raise ValueError("Weekdays must be 0-6 (Monday-Sunday)")
        return v

    @field_validator("start_times")
    @classmethod
    def validate_times(cls, v: list[str]) -> list[str]:
        """Validate time format HH:MM."""
        import re

        for time_str in v:
            if not re.match(r"^\d{2}:\d{2}$", time_str):
                raise ValueError("Times must be in HH:MM format")
        return v


class SlotUpdate(BaseSchema):
    """Slot update payload."""

    status: SlotStatus | None = None
    slot_type: SlotType | None = None
    is_priority_only: bool | None = None
    is_urgent_only: bool | None = None
    min_compliance_level: ComplianceLevel | None = None


class SlotResponse(ResponseSchema, SlotBase):
    """Slot response."""

    doctor_id: str
    status: SlotStatus
    slot_type: SlotType
    is_priority_only: bool
    is_urgent_only: bool
    min_compliance_level: ComplianceLevel | None
    is_recurring: bool
    recurrence_group_id: str | None


class SlotAvailableResponse(BaseSchema):
    """Available slot for patient booking view."""

    id: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    doctor_name: str
    slot_type: SlotType


class SlotListResponse(BaseSchema):
    """Paginated slot list."""

    items: list[SlotResponse]
    total: int
    page: int
    page_size: int


class SlotAutoGenerateRequest(BaseSchema):
    """Request to auto-generate slots with distribution."""

    days: int = Field(90, ge=30, le=365, description="Number of days to generate")
    weekdays: list[int] = Field([0, 1, 2, 3, 4], min_length=1)  # Mon-Fri default
    start_times: list[str] = Field(
        ["09:00", "09:30", "10:00", "10:30", "11:00", "14:00", "14:30", "15:00", "15:30", "16:00"],
        min_length=1,
    )
    duration_minutes: int = Field(30, ge=15, le=120)

    @field_validator("weekdays")
    @classmethod
    def validate_weekdays(cls, v: list[int]) -> list[int]:
        """Ensure valid weekday values."""
        for day in v:
            if day < 0 or day > 6:
                raise ValueError("Weekdays must be 0-6 (Monday-Sunday)")
        return v

    @field_validator("start_times")
    @classmethod
    def validate_times(cls, v: list[str]) -> list[str]:
        """Validate time format HH:MM."""
        import re

        for time_str in v:
            if not re.match(r"^\d{2}:\d{2}$", time_str):
                raise ValueError("Times must be in HH:MM format")
        return v


class SlotAutoGenerateResponse(BaseSchema):
    """Response from slot auto-generation."""

    slots_created: int
    recurrence_group_id: str
    distribution: dict


class AvailableDatesResponse(BaseSchema):
    """Response with list of dates that have available slots."""

    dates: list[datetime]
    total_slots: int


class EmergencyBookingRequest(BaseSchema):
    """Request to book an emergency slot."""

    slot_id: str
    urgency_reason: str = Field(..., min_length=10, max_length=500)
    symptoms: str | None = Field(None, max_length=1000)
