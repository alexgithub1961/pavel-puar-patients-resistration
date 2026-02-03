"""Patient schemas."""

from pydantic import EmailStr, Field

from src.models.patient import ComplianceLevel, PatientCategory
from src.schemas.base import BaseSchema, ResponseSchema


class PatientBase(BaseSchema):
    """Base patient fields."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: str | None = Field(None, max_length=20)
    date_of_birth: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    preferred_language: str = Field("en", pattern=r"^(en|he|ru)$")


class PatientCreate(PatientBase):
    """Patient registration payload."""

    email: EmailStr
    password: str = Field(..., min_length=8)


class PatientUpdate(BaseSchema):
    """Patient update payload."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    phone: str | None = Field(None, max_length=20)
    date_of_birth: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    preferred_language: str | None = Field(None, pattern=r"^(en|he|ru)$")
    notes: str | None = None


class PatientAdminUpdate(PatientUpdate):
    """Admin-only patient update fields."""

    category: PatientCategory | None = None
    compliance_level: ComplianceLevel | None = None
    compliance_score: int | None = Field(None, ge=0, le=100)
    is_active: bool | None = None


class PatientResponse(ResponseSchema, PatientBase):
    """Full patient response (for patient/admin)."""

    email: EmailStr
    category: PatientCategory
    compliance_level: ComplianceLevel
    compliance_score: int
    total_appointments: int
    no_shows: int
    late_cancellations: int
    is_active: bool
    notes: str | None
    primary_doctor_id: str | None


class PatientPublicResponse(ResponseSchema):
    """Limited patient info (for doctor view)."""

    first_name: str
    last_name: str
    category: PatientCategory
    compliance_level: ComplianceLevel
    compliance_score: int
    total_appointments: int
    no_shows: int
    late_cancellations: int


class PatientListResponse(BaseSchema):
    """Paginated patient list."""

    items: list[PatientPublicResponse]
    total: int
    page: int
    page_size: int
