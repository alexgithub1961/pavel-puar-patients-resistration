"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.core.database import get_db
from src.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from src.models.doctor import Doctor
from src.models.patient import Patient
from src.schemas.auth import DemoLoginRequest, LoginRequest, RefreshTokenRequest, TokenResponse
from src.schemas.doctor import DoctorCreate, DoctorResponse
from src.schemas.patient import PatientCreate, PatientResponse


# Demo account credentials - PUBLIC for demo purposes
DEMO_ACCOUNTS = {
    "new_patient": {
        "email": "demo.new@example.com",
        "password": "demo1234",
        "first_name": "Demo",
        "last_name": "NewPatient",
        "phone": "+1234567890",
    },
    "regular_patient": {
        "email": "demo.regular@example.com",
        "password": "demo1234",
        "first_name": "Demo",
        "last_name": "RegularPatient",
        "phone": "+1234567891",
    },
    "doctor": {
        "email": "demo.doctor@example.com",
        "password": "demo1234",
        "first_name": "Demo",
        "last_name": "Doctor",
        "phone": "+1234567892",
        "specialisation": "General Practice",
        "licence_number": "DEMO-001",
    },
}

router = APIRouter()


@router.post("/patients/register", response_model=PatientResponse)
async def register_patient(
    data: PatientCreate,
    db: AsyncSession = Depends(get_db),
) -> Patient:
    """Register a new patient."""
    # Check if email exists
    result = await db.execute(select(Patient).where(Patient.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    patient = Patient(
        email=data.email,
        password_hash=get_password_hash(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        date_of_birth=data.date_of_birth,
        preferred_language=data.preferred_language,
    )

    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


@router.post("/patients/login", response_model=TokenResponse)
async def login_patient(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate patient and return tokens."""
    result = await db.execute(select(Patient).where(Patient.email == data.email))
    patient = result.scalar_one_or_none()

    if not patient or not verify_password(data.password, patient.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not patient.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    access_token = create_access_token({"sub": f"patient:{patient.id}"})
    refresh_token = create_refresh_token({"sub": f"patient:{patient.id}"})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/doctors/register", response_model=DoctorResponse)
async def register_doctor(
    data: DoctorCreate,
    db: AsyncSession = Depends(get_db),
) -> Doctor:
    """Register a new doctor."""
    # Check if email exists
    result = await db.execute(select(Doctor).where(Doctor.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    doctor = Doctor(
        email=data.email,
        password_hash=get_password_hash(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        specialisation=data.specialisation,
        licence_number=data.licence_number,
        bio=data.bio,
        default_slot_duration_minutes=data.default_slot_duration_minutes,
        booking_window_days=data.booking_window_days,
        max_daily_appointments=data.max_daily_appointments,
    )

    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)
    return doctor


@router.post("/doctors/login", response_model=TokenResponse)
async def login_doctor(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate doctor and return tokens."""
    result = await db.execute(select(Doctor).where(Doctor.email == data.email))
    doctor = result.scalar_one_or_none()

    if not doctor or not verify_password(data.password, doctor.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not doctor.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    access_token = create_access_token({"sub": f"doctor:{doctor.id}"})
    refresh_token = create_refresh_token({"sub": f"doctor:{doctor.id}"})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(data: RefreshTokenRequest) -> TokenResponse:
    """Refresh access token using refresh token."""
    from src.core.security import decode_token

    token_data = decode_token(data.refresh_token)
    if not token_data or token_data.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    access_token = create_access_token({"sub": token_data.sub})
    refresh_token = create_refresh_token({"sub": token_data.sub})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/demo", response_model=TokenResponse)
async def demo_login(
    data: DemoLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Demo login - creates demo account if needed and returns tokens.
    
    This endpoint is for demonstration and E2E testing purposes.
    Available roles: new_patient, regular_patient, doctor
    """
    settings = get_settings()
    
    if not settings.demo_mode_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo mode is disabled",
        )
    
    if data.role not in DEMO_ACCOUNTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(DEMO_ACCOUNTS.keys())}",
        )
    
    account = DEMO_ACCOUNTS[data.role]
    
    if data.role == "doctor":
        # Handle doctor demo account
        result = await db.execute(select(Doctor).where(Doctor.email == account["email"]))
        doctor = result.scalar_one_or_none()
        
        if not doctor:
            # Create demo doctor
            doctor = Doctor(
                email=account["email"],
                password_hash=get_password_hash(account["password"]),
                first_name=account["first_name"],
                last_name=account["last_name"],
                phone=account["phone"],
                specialisation=account["specialisation"],
                licence_number=account["licence_number"],
            )
            db.add(doctor)
            await db.commit()
            await db.refresh(doctor)
        
        access_token = create_access_token({"sub": f"doctor:{doctor.id}"})
        refresh_token = create_refresh_token({"sub": f"doctor:{doctor.id}"})
    else:
        # Handle patient demo accounts
        result = await db.execute(select(Patient).where(Patient.email == account["email"]))
        patient = result.scalar_one_or_none()
        
        if not patient:
            # Create demo patient
            patient = Patient(
                email=account["email"],
                password_hash=get_password_hash(account["password"]),
                first_name=account["first_name"],
                last_name=account["last_name"],
                phone=account["phone"],
            )
            db.add(patient)
            await db.commit()
            await db.refresh(patient)
        
        access_token = create_access_token({"sub": f"patient:{patient.id}"})
        refresh_token = create_refresh_token({"sub": f"patient:{patient.id}"})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


# Demo login endpoint - public credentials for testing
DEMO_CREDENTIALS = {
    "new_patient": {
        "email": "demo.new@example.com",
        "password": "demo1234",
    },
    "regular_patient": {
        "email": "demo.regular@example.com",
        "password": "demo1234",
    },
}




@router.post("/demo", response_model=TokenResponse)
async def demo_login(
    data: DemoLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Login with demo account.
    
    This endpoint allows quick login with predefined demo accounts
    for testing and demonstration purposes.
    """
    creds = DEMO_CREDENTIALS.get(data.role)
    if not creds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid demo role",
        )
    
    # Find the patient
    result = await db.execute(select(Patient).where(Patient.email == creds["email"]))
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo account not found. Please seed the database.",
        )
    
    if not patient.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo account is inactive",
        )
    
    access_token = create_access_token({"sub": f"patient:{patient.id}"})
    refresh_token = create_refresh_token({"sub": f"patient:{patient.id}"})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
