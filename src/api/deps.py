"""API dependencies for authentication and database."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import decode_token
from src.models.doctor import Doctor
from src.models.patient import Patient
from src.services.patient_service import PatientService

security = HTTPBearer()


async def get_current_user_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict:
    """Validate JWT token and return token data."""
    token_data = decode_token(credentials.credentials)
    if not token_data or token_data.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return {"sub": token_data.sub, "type": token_data.type}


async def get_current_patient(
    token: Annotated[dict, Depends(get_current_user_token)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Patient:
    """Get current authenticated patient."""
    if not token["sub"].startswith("patient:"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient access required",
        )

    patient_id = token["sub"].replace("patient:", "")
    service = PatientService(db)
    patient = await service.get_patient_by_id(patient_id)

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    if not patient.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    return patient


async def get_current_doctor(
    token: Annotated[dict, Depends(get_current_user_token)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Doctor:
    """Get current authenticated doctor."""
    if not token["sub"].startswith("doctor:"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor access required",
        )

    doctor_id = token["sub"].replace("doctor:", "")

    from sqlalchemy import select
    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    doctor = result.scalar_one_or_none()

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )

    if not doctor.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    return doctor


# Type aliases for cleaner route signatures
CurrentPatient = Annotated[Patient, Depends(get_current_patient)]
CurrentDoctor = Annotated[Doctor, Depends(get_current_doctor)]
DB = Annotated[AsyncSession, Depends(get_db)]
