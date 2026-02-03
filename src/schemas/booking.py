"""Booking schemas."""

from datetime import datetime

from pydantic import Field

from src.models.booking import BookingStatus
from src.schemas.base import BaseSchema, ResponseSchema


class BookingBase(BaseSchema):
    """Base booking fields."""

    reason: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=1000)


class BookingCreate(BookingBase):
    """Booking creation payload."""

    slot_id: str
    is_emergency: bool = False
    urgency_reason: str | None = Field(None, min_length=10, max_length=500)


class BookingUpdate(BaseSchema):
    """Booking update payload."""

    reason: str | None = Field(None, max_length=500)
    notes: str | None = Field(None, max_length=1000)


class RescheduleRequest(BaseSchema):
    """Request to reschedule a booking."""

    new_slot_id: str
    triage_questionnaire_id: str  # Must complete triage first


class CancelRequest(BaseSchema):
    """Request to cancel a booking."""

    triage_questionnaire_id: str  # Must complete triage first


class BookingResponse(ResponseSchema, BookingBase):
    """Full booking response."""

    patient_id: str
    slot_id: str
    status: BookingStatus
    cancelled_at: datetime | None
    cancellation_reason: str | None
    rescheduled_from_id: str | None
    rescheduled_to_id: str | None
    confirmed_at: datetime | None
    reminder_sent: bool


class BookingWithSlotResponse(BookingResponse):
    """Booking with slot details."""

    slot_start_time: datetime
    slot_end_time: datetime
    doctor_name: str


class BookingListResponse(BaseSchema):
    """Paginated booking list."""

    items: list[BookingWithSlotResponse]
    total: int
    page: int
    page_size: int


class NextBookingInfo(BaseSchema):
    """Information about patient's next allowed booking window."""

    can_book: bool
    earliest_date: datetime | None  # Earliest allowed date
    latest_date: datetime | None  # Latest allowed date (booking window)
    reason: str | None  # Why they can't book if can_book=False
    has_active_booking: bool
    visit_frequency_days: int
