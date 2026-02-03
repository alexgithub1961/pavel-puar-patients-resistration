"""Doctor model."""

from typing import TYPE_CHECKING

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel

if TYPE_CHECKING:
    from src.models.slot import Slot

# Default slot distribution percentages
DEFAULT_SLOT_DISTRIBUTION = {
    "first_visit": 20,  # 20% for new patients
    "follow_up": 70,    # 70% for regular follow-ups
    "emergency": 10,    # 10% reserved for emergencies
}


class Doctor(BaseModel):
    """Doctor entity - manages appointments and slots."""

    __tablename__ = "doctors"

    # Basic info
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))

    # Professional info
    specialisation: Mapped[str | None] = mapped_column(String(100))
    licence_number: Mapped[str | None] = mapped_column(String(50))
    bio: Mapped[str | None] = mapped_column(Text)

    # Settings
    default_slot_duration_minutes: Mapped[int] = mapped_column(default=30)
    booking_window_days: Mapped[int] = mapped_column(default=30)  # How far ahead patients can book
    max_daily_appointments: Mapped[int] = mapped_column(default=20)

    # Slot distribution settings (percentage per slot type)
    slot_distribution: Mapped[dict] = mapped_column(
        JSON, default=DEFAULT_SLOT_DISTRIBUTION.copy
    )

    # Auto-generation settings
    auto_generate_days: Mapped[int] = mapped_column(default=90)  # Generate slots for next N days

    # Status
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    slots: Mapped[list["Slot"]] = relationship(
        "Slot", back_populates="doctor", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        """Return doctor's full name."""
        return f"{self.first_name} {self.last_name}"
