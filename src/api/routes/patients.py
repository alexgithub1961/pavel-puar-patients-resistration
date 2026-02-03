"""Patient routes."""

from fastapi import APIRouter, HTTPException, status

from src.api.deps import DB, CurrentPatient
from src.schemas.booking import NextBookingInfo
from src.schemas.patient import PatientResponse, PatientUpdate
from src.schemas.questionnaire import (
    ComplianceQuestionnaireCreate,
    ComplianceQuestionnaireResponse,
)
from src.services.patient_service import PatientService

router = APIRouter()


@router.get("/me", response_model=PatientResponse)
async def get_current_patient(patient: CurrentPatient) -> PatientResponse:
    """Get current patient profile."""
    return PatientResponse.model_validate(patient)


@router.patch("/me", response_model=PatientResponse)
async def update_current_patient(
    data: PatientUpdate,
    patient: CurrentPatient,
    db: DB,
) -> PatientResponse:
    """Update current patient profile."""
    service = PatientService(db)
    updated = await service.update_patient(patient.id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    return PatientResponse.model_validate(updated)


@router.post("/me/compliance-questionnaire", response_model=ComplianceQuestionnaireResponse)
async def submit_compliance_questionnaire(
    data: ComplianceQuestionnaireCreate,
    patient: CurrentPatient,
    db: DB,
) -> ComplianceQuestionnaireResponse:
    """Submit initial compliance self-assessment questionnaire."""
    # Check if already submitted
    if patient.compliance_questionnaire:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Compliance questionnaire already submitted",
        )

    service = PatientService(db)
    questionnaire = await service.submit_compliance_questionnaire(patient.id, data)
    return ComplianceQuestionnaireResponse.model_validate(questionnaire)


@router.get("/me/compliance-questionnaire", response_model=ComplianceQuestionnaireResponse)
async def get_compliance_questionnaire(
    patient: CurrentPatient,
) -> ComplianceQuestionnaireResponse:
    """Get patient's compliance questionnaire."""
    if not patient.compliance_questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance questionnaire not submitted",
        )
    return ComplianceQuestionnaireResponse.model_validate(patient.compliance_questionnaire)


@router.get("/me/next-booking-window", response_model=NextBookingInfo)
async def get_next_booking_window(
    patient: CurrentPatient,
    db: DB,
) -> NextBookingInfo:
    """Get patient's next allowed booking window based on visit frequency."""
    service = PatientService(db)
    window = await service.get_next_booking_window(patient.id)
    return NextBookingInfo.model_validate(window)
