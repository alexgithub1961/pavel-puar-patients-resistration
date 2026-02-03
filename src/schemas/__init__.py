"""Pydantic schemas for API validation."""

from src.schemas.auth import LoginRequest, TokenResponse
from src.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingUpdate,
    RescheduleRequest,
)
from src.schemas.doctor import DoctorCreate, DoctorResponse, DoctorUpdate
from src.schemas.patient import PatientCreate, PatientPublicResponse, PatientResponse, PatientUpdate
from src.schemas.questionnaire import (
    ComplianceQuestionnaireCreate,
    ComplianceQuestionnaireResponse,
    TriageQuestionnaireCreate,
    TriageQuestionnaireResponse,
)
from src.schemas.slot import (
    SlotBulkCreate,
    SlotCreate,
    SlotResponse,
    SlotUpdate,
)

__all__ = [
    "BookingCreate",
    "BookingResponse",
    "BookingUpdate",
    "ComplianceQuestionnaireCreate",
    "ComplianceQuestionnaireResponse",
    "DoctorCreate",
    "DoctorResponse",
    "DoctorUpdate",
    "LoginRequest",
    "PatientCreate",
    "PatientPublicResponse",
    "PatientResponse",
    "PatientUpdate",
    "RescheduleRequest",
    "SlotBulkCreate",
    "SlotCreate",
    "SlotResponse",
    "SlotUpdate",
    "TokenResponse",
    "TriageQuestionnaireCreate",
    "TriageQuestionnaireResponse",
]
