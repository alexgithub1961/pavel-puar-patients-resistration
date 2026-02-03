"""Booking model for patient appointments."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel

if TYPE_CHECKING:
    from src.models.patient import Patient
    from src.models.questionnaire import TriageQuestionnaire
    from src.models.slot import Slot


class BookingStatus(str, Enum):
    """Booking lifecycle status."""

    PENDING = "pending"  # Awaiting confirmation
    CONFIRMED = "confirmed"  # Confirmed by system/doctor
    COMPLETED = "completed"  # Appointment completed
    CANCELLED_BY_PATIENT = "cancelled_by_patient"
    CANCELLED_BY_DOCTOR = "cancelled_by_doctor"
    NO_SHOW = "no_show"  # Patient didn't attend
    RESCHEDULED = "rescheduled"  # Moved to another slot


class Booking(BaseModel):
    """Patient appointment booking."""

    __tablename__ = "bookings"

    # Foreign keys
    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    slot_id: Mapped[str] = mapped_column(
        ForeignKey("slots.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One booking per slot
    )

    # Status tracking
    status: Mapped[BookingStatus] = mapped_column(
        String(30), default=BookingStatus.PENDING.value, index=True
    )

    # Booking details
    reason: Mapped[str | None] = mapped_column(Text)  # Visit reason
    notes: Mapped[str | None] = mapped_column(Text)  # Additional notes

    # Emergency booking fields
    is_emergency: Mapped[bool] = mapped_column(Boolean, default=False)
    urgency_reason: Mapped[str | None] = mapped_column(Text)  # Required if is_emergency=True

    # Cancellation/reschedule tracking
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancellation_reason: Mapped[str | None] = mapped_column(Text)
    rescheduled_from_id: Mapped[str | None] = mapped_column(
        ForeignKey("bookings.id"), nullable=True
    )
    rescheduled_to_id: Mapped[str | None] = mapped_column(String(36))

    # Confirmation
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reminder_sent: Mapped[bool] = mapped_column(default=False)

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="bookings")
    slot: Mapped["Slot"] = relationship("Slot", back_populates="booking")
    triage_questionnaire: Mapped["TriageQuestionnaire | None"] = relationship(
        "TriageQuestionnaire", back_populates="booking", uselist=False
    )

    @property
    def is_cancellable(self) -> bool:
        """Check if booking can be cancelled."""
        return self.status in [BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]

    @property
    def is_active(self) -> bool:
        """Check if booking is active (not cancelled/completed)."""
        return self.status in [BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]
