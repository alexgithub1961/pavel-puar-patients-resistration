"""Questionnaire schemas."""

from datetime import datetime

from pydantic import Field

from src.models.questionnaire import UrgencyLevel
from src.schemas.base import BaseSchema, ResponseSchema


class ComplianceQuestionnaireCreate(BaseSchema):
    """Initial compliance questionnaire submission."""

    # Self-assessment (1-5 scale)
    missed_appointments_rating: int = Field(..., ge=1, le=5)
    cancellation_notice_rating: int = Field(..., ge=1, le=5)
    schedule_importance_rating: int = Field(..., ge=1, le=5)
    reschedule_commitment_rating: int = Field(..., ge=1, le=5)
    flexibility_rating: int = Field(..., ge=1, le=5)

    # Commitments
    agrees_24h_cancellation: bool
    agrees_no_show_penalty: bool
    agrees_reschedule_policy: bool
    agrees_communication_preferences: bool

    # Optional notes
    additional_notes: str | None = None


class ComplianceQuestionnaireResponse(ResponseSchema):
    """Compliance questionnaire response."""

    patient_id: str
    missed_appointments_rating: int
    cancellation_notice_rating: int
    schedule_importance_rating: int
    reschedule_commitment_rating: int
    flexibility_rating: int
    agrees_24h_cancellation: bool
    agrees_no_show_penalty: bool
    agrees_reschedule_policy: bool
    agrees_communication_preferences: bool
    calculated_score: int
    completed_at: datetime | None
    is_complete: bool


class TriageQuestionnaireCreate(BaseSchema):
    """Triage questionnaire for cancel/reschedule."""

    booking_id: str
    request_type: str = Field(..., pattern=r"^(cancel|reschedule)$")

    # Reason
    reason_category: str = Field(
        ..., pattern=r"^(work|health|family|transport|other)$"
    )
    reason_details: str | None = None

    # Urgency assessment
    condition_changed: bool = False
    symptoms_worsened: bool = False
    new_symptoms: bool = False

    # Availability
    available_within_week: bool = True
    preferred_times: str | None = None

    # Acknowledgments
    acknowledges_impact: bool
    commits_to_new_appointment: bool


class TriageQuestionnaireResponse(ResponseSchema):
    """Triage questionnaire response."""

    booking_id: str
    request_type: str
    reason_category: str
    reason_details: str | None
    condition_changed: bool
    symptoms_worsened: bool
    new_symptoms: bool
    urgency_level: UrgencyLevel
    requires_doctor_review: bool
    is_approved: bool | None
    approved_by: str | None
    approved_at: datetime | None
    rejection_reason: str | None


class TriageDecision(BaseSchema):
    """Doctor's decision on triage questionnaire."""

    is_approved: bool
    rejection_reason: str | None = None
