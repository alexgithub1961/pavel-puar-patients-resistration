"""Patient model with category and compliance tracking."""

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel

if TYPE_CHECKING:
    from src.models.booking import Booking
    from src.models.questionnaire import ComplianceQuestionnaire


class VisitFrequency(str, Enum):
    """Patient visit frequency based on their category."""

    WEEKLY = "weekly"  # Every week
    BIWEEKLY = "biweekly"  # Every 2 weeks
    MONTHLY = "monthly"  # Once a month
    BIMONTHLY = "bimonthly"  # Every 2 months
    QUARTERLY = "quarterly"  # Every 3 months
    BIANNUAL = "biannual"  # Every 6 months
    ANNUAL = "annual"  # Once a year


class PatientCategory(str, Enum):
    """Patient medical category affecting visit frequency."""

    CRITICAL = "critical"  # Weekly visits required
    HIGH_RISK = "high_risk"  # Biweekly visits
    MODERATE = "moderate"  # Monthly visits
    STABLE = "stable"  # Quarterly visits
    MAINTENANCE = "maintenance"  # Biannual visits
    HEALTHY = "healthy"  # Annual checkups


class ComplianceLevel(str, Enum):
    """Patient compliance/trust level based on questionnaire and history."""

    PLATINUM = "platinum"  # Excellent compliance, priority access
    GOLD = "gold"  # Good compliance
    SILVER = "silver"  # Average compliance
    BRONZE = "bronze"  # Below average, more restrictions
    PROBATION = "probation"  # Poor history, strict limits


# Mapping from category to required visit frequency
CATEGORY_FREQUENCY_MAP: dict[PatientCategory, VisitFrequency] = {
    PatientCategory.CRITICAL: VisitFrequency.WEEKLY,
    PatientCategory.HIGH_RISK: VisitFrequency.BIWEEKLY,
    PatientCategory.MODERATE: VisitFrequency.MONTHLY,
    PatientCategory.STABLE: VisitFrequency.QUARTERLY,
    PatientCategory.MAINTENANCE: VisitFrequency.BIANNUAL,
    PatientCategory.HEALTHY: VisitFrequency.ANNUAL,
}

# Frequency to days mapping
FREQUENCY_DAYS_MAP: dict[VisitFrequency, int] = {
    VisitFrequency.WEEKLY: 7,
    VisitFrequency.BIWEEKLY: 14,
    VisitFrequency.MONTHLY: 30,
    VisitFrequency.BIMONTHLY: 60,
    VisitFrequency.QUARTERLY: 90,
    VisitFrequency.BIANNUAL: 180,
    VisitFrequency.ANNUAL: 365,
}


class Patient(BaseModel):
    """Patient entity with medical category and compliance tracking."""

    __tablename__ = "patients"

    # Basic info
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    date_of_birth: Mapped[str | None] = mapped_column(String(10))  # YYYY-MM-DD

    # Medical info
    category: Mapped[PatientCategory] = mapped_column(
        String(20), default=PatientCategory.STABLE.value
    )
    notes: Mapped[str | None] = mapped_column(Text)

    # Compliance tracking
    compliance_level: Mapped[ComplianceLevel] = mapped_column(
        String(20), default=ComplianceLevel.SILVER.value
    )
    compliance_score: Mapped[int] = mapped_column(Integer, default=50)  # 0-100 score
    total_appointments: Mapped[int] = mapped_column(Integer, default=0)
    no_shows: Mapped[int] = mapped_column(Integer, default=0)
    late_cancellations: Mapped[int] = mapped_column(Integer, default=0)

    # Preferred language for i18n
    preferred_language: Mapped[str] = mapped_column(String(5), default="en")

    # Status
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="patient", cascade="all, delete-orphan"
    )
    compliance_questionnaire: Mapped["ComplianceQuestionnaire | None"] = relationship(
        "ComplianceQuestionnaire", back_populates="patient", uselist=False
    )

    # Foreign key for primary doctor
    primary_doctor_id: Mapped[str | None] = mapped_column(
        ForeignKey("doctors.id"), nullable=True
    )

    @property
    def full_name(self) -> str:
        """Return patient's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def visit_frequency(self) -> VisitFrequency:
        """Get required visit frequency based on category."""
        return CATEGORY_FREQUENCY_MAP.get(
            PatientCategory(self.category), VisitFrequency.QUARTERLY
        )

    @property
    def visit_interval_days(self) -> int:
        """Get visit interval in days."""
        return FREQUENCY_DAYS_MAP.get(self.visit_frequency, 90)

    @property
    def cancellation_rate(self) -> float:
        """Calculate cancellation/no-show rate."""
        if self.total_appointments == 0:
            return 0.0
        return (self.no_shows + self.late_cancellations) / self.total_appointments
