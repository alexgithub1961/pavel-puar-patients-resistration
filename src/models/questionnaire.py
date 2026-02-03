"""Questionnaire models for compliance and triage assessment."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel

if TYPE_CHECKING:
    from src.models.booking import Booking
    from src.models.patient import Patient


class UrgencyLevel(str, Enum):
    """Urgency level from triage assessment."""

    EMERGENCY = "emergency"  # Immediate attention needed
    URGENT = "urgent"  # Same day/next day
    MODERATE = "moderate"  # Within a week
    ROUTINE = "routine"  # Standard scheduling


class QuestionnaireResponse(BaseModel):
    """Generic questionnaire response storage."""

    __tablename__ = "questionnaire_responses"

    # Questionnaire type
    questionnaire_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Owner (patient or booking)
    patient_id: Mapped[str | None] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), nullable=True, index=True
    )
    booking_id: Mapped[str | None] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"), nullable=True
    )

    # Response data (flexible JSON storage)
    responses: Mapped[dict] = mapped_column(JSON, default=dict)

    # Calculated scores
    total_score: Mapped[int | None] = mapped_column(Integer)
    risk_level: Mapped[str | None] = mapped_column(String(20))

    # Metadata
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)


class ComplianceQuestionnaire(BaseModel):
    """Initial patient compliance self-assessment."""

    __tablename__ = "compliance_questionnaires"

    patient_id: Mapped[str] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Self-assessment questions (1-5 scale)
    # Q1: How often do you miss scheduled appointments?
    missed_appointments_rating: Mapped[int] = mapped_column(Integer, default=3)  # 1=often, 5=never

    # Q2: How much advance notice do you typically give for cancellations?
    cancellation_notice_rating: Mapped[int] = mapped_column(Integer, default=3)  # 1=none, 5=24h+

    # Q3: How important is maintaining your appointment schedule?
    schedule_importance_rating: Mapped[int] = mapped_column(Integer, default=3)  # 1=low, 5=critical

    # Q4: How likely are you to reschedule if you must cancel?
    reschedule_commitment_rating: Mapped[int] = mapped_column(Integer, default=3)  # 1=unlikely, 5=always

    # Q5: How flexible is your schedule for appointments?
    flexibility_rating: Mapped[int] = mapped_column(Integer, default=3)  # 1=rigid, 5=very flexible

    # Commitments (checkboxes the patient agrees to)
    agrees_24h_cancellation: Mapped[bool] = mapped_column(Boolean, default=False)
    agrees_no_show_penalty: Mapped[bool] = mapped_column(Boolean, default=False)
    agrees_reschedule_policy: Mapped[bool] = mapped_column(Boolean, default=False)
    agrees_communication_preferences: Mapped[bool] = mapped_column(Boolean, default=False)

    # Calculated compliance score (0-100)
    calculated_score: Mapped[int] = mapped_column(Integer, default=50)

    # Completion tracking
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)

    # Notes
    additional_notes: Mapped[str | None] = mapped_column(Text)

    # Relationship
    patient: Mapped["Patient"] = relationship(
        "Patient", back_populates="compliance_questionnaire"
    )

    def calculate_score(self) -> int:
        """Calculate compliance score from responses."""
        # Rating scores (each 1-5, total max 25)
        ratings_sum = (
            self.missed_appointments_rating
            + self.cancellation_notice_rating
            + self.schedule_importance_rating
            + self.reschedule_commitment_rating
            + self.flexibility_rating
        )
        ratings_score = (ratings_sum / 25) * 60  # 60% from ratings

        # Commitment scores (each worth 10 points, max 40)
        commitments_score = sum([
            10 if self.agrees_24h_cancellation else 0,
            10 if self.agrees_no_show_penalty else 0,
            10 if self.agrees_reschedule_policy else 0,
            10 if self.agrees_communication_preferences else 0,
        ])

        self.calculated_score = int(ratings_score + commitments_score)
        return self.calculated_score


class TriageQuestionnaire(BaseModel):
    """Triage questionnaire for cancellation/reschedule requests."""

    __tablename__ = "triage_questionnaires"

    booking_id: Mapped[str] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Request type
    request_type: Mapped[str] = mapped_column(String(20))  # "cancel" or "reschedule"

    # Q1: Reason for change
    reason_category: Mapped[str] = mapped_column(String(50))  # work, health, family, transport, other
    reason_details: Mapped[str | None] = mapped_column(Text)

    # Q2: Urgency assessment
    condition_changed: Mapped[bool] = mapped_column(Boolean, default=False)
    symptoms_worsened: Mapped[bool] = mapped_column(Boolean, default=False)
    new_symptoms: Mapped[bool] = mapped_column(Boolean, default=False)

    # Q3: Availability for reschedule
    available_within_week: Mapped[bool] = mapped_column(Boolean, default=True)
    preferred_times: Mapped[str | None] = mapped_column(Text)  # JSON list of preferred times

    # Q4: Commitment acknowledgment
    acknowledges_impact: Mapped[bool] = mapped_column(Boolean, default=False)
    commits_to_new_appointment: Mapped[bool] = mapped_column(Boolean, default=False)

    # Calculated urgency level
    urgency_level: Mapped[UrgencyLevel] = mapped_column(
        String(20), default=UrgencyLevel.ROUTINE.value
    )

    # Doctor notification required
    requires_doctor_review: Mapped[bool] = mapped_column(Boolean, default=False)

    # Approval status
    is_approved: Mapped[bool | None] = mapped_column(Boolean)  # None = pending
    approved_by: Mapped[str | None] = mapped_column(String(36))  # Doctor ID or "system"
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[str | None] = mapped_column(Text)

    # Relationship
    booking: Mapped["Booking"] = relationship(
        "Booking", back_populates="triage_questionnaire"
    )

    def calculate_urgency(self) -> UrgencyLevel:
        """Calculate urgency level based on responses."""
        if self.symptoms_worsened or self.new_symptoms:
            self.urgency_level = UrgencyLevel.URGENT
            self.requires_doctor_review = True
        elif self.condition_changed:
            self.urgency_level = UrgencyLevel.MODERATE
            self.requires_doctor_review = True
        else:
            self.urgency_level = UrgencyLevel.ROUTINE
            self.requires_doctor_review = False

        return UrgencyLevel(self.urgency_level)
