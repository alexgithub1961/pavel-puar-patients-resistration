"""Slot model for doctor availability."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel

if TYPE_CHECKING:
    from src.models.booking import Booking
    from src.models.doctor import Doctor


class SlotStatus(str, Enum):
    """Slot availability status."""

    AVAILABLE = "available"  # Open for booking
    BOOKED = "booked"  # Has a confirmed booking
    BLOCKED = "blocked"  # Blocked by doctor (break, meeting, etc.)
    RESERVED = "reserved"  # Reserved for urgent/priority cases
    CANCELLED = "cancelled"  # Previously booked but cancelled


class SlotType(str, Enum):
    """Type of appointment slot."""

    FIRST_VISIT = "first_visit"  # For new patients or first consultations
    FOLLOW_UP = "follow_up"  # For returning patients with previous visits
    EMERGENCY = "emergency"  # For urgent cases, bypasses normal booking rules


class Slot(BaseModel):
    """Time slot for appointments."""

    __tablename__ = "slots"

    # Foreign keys
    doctor_id: Mapped[str] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Time details
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)

    # Status
    status: Mapped[SlotStatus] = mapped_column(
        String(20), default=SlotStatus.AVAILABLE.value, index=True
    )

    # Slot type
    slot_type: Mapped[SlotType] = mapped_column(
        String(20), default=SlotType.FOLLOW_UP.value, index=True
    )

    # Restrictions
    is_priority_only: Mapped[bool] = mapped_column(Boolean, default=False)
    is_urgent_only: Mapped[bool] = mapped_column(Boolean, default=False)
    min_compliance_level: Mapped[str | None] = mapped_column(String(20))  # Minimum required

    # Recurrence (for generating recurring slots)
    recurrence_group_id: Mapped[str | None] = mapped_column(String(36))
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="slots")
    booking: Mapped["Booking | None"] = relationship(
        "Booking", back_populates="slot", uselist=False
    )

    @property
    def is_available(self) -> bool:
        """Check if slot is available for booking."""
        return self.status == SlotStatus.AVAILABLE.value

    @property
    def is_past(self) -> bool:
        """Check if slot is in the past."""
        from datetime import UTC

        return self.start_time < datetime.now(UTC)
