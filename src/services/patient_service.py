"""Patient service for managing patient operations."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash, verify_password
from src.models.booking import Booking, BookingStatus
from src.models.patient import (
    FREQUENCY_DAYS_MAP,
    ComplianceLevel,
    Patient,
    PatientCategory,
)
from src.models.questionnaire import ComplianceQuestionnaire
from src.schemas.patient import PatientCreate, PatientUpdate
from src.schemas.questionnaire import ComplianceQuestionnaireCreate


class PatientService:
    """Service for patient-related operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_patient(self, data: PatientCreate) -> Patient:
        """Register a new patient."""
        patient = Patient(
            email=data.email,
            password_hash=get_password_hash(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            date_of_birth=data.date_of_birth,
            preferred_language=data.preferred_language,
        )
        self.db.add(patient)
        await self.db.flush()
        return patient

    async def get_patient_by_id(self, patient_id: str) -> Patient | None:
        """Get patient by ID."""
        result = await self.db.execute(select(Patient).where(Patient.id == patient_id))
        return result.scalar_one_or_none()

    async def get_patient_by_email(self, email: str) -> Patient | None:
        """Get patient by email."""
        result = await self.db.execute(select(Patient).where(Patient.email == email))
        return result.scalar_one_or_none()

    async def authenticate_patient(self, email: str, password: str) -> Patient | None:
        """Authenticate patient by email and password."""
        patient = await self.get_patient_by_email(email)
        if patient and verify_password(password, patient.password_hash):
            return patient
        return None

    async def update_patient(self, patient_id: str, data: PatientUpdate) -> Patient | None:
        """Update patient information."""
        patient = await self.get_patient_by_id(patient_id)
        if not patient:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(patient, field, value)

        await self.db.flush()
        return patient

    async def submit_compliance_questionnaire(
        self, patient_id: str, data: ComplianceQuestionnaireCreate
    ) -> ComplianceQuestionnaire:
        """Submit initial compliance questionnaire."""
        questionnaire = ComplianceQuestionnaire(
            patient_id=patient_id,
            missed_appointments_rating=data.missed_appointments_rating,
            cancellation_notice_rating=data.cancellation_notice_rating,
            schedule_importance_rating=data.schedule_importance_rating,
            reschedule_commitment_rating=data.reschedule_commitment_rating,
            flexibility_rating=data.flexibility_rating,
            agrees_24h_cancellation=data.agrees_24h_cancellation,
            agrees_no_show_penalty=data.agrees_no_show_penalty,
            agrees_reschedule_policy=data.agrees_reschedule_policy,
            agrees_communication_preferences=data.agrees_communication_preferences,
            additional_notes=data.additional_notes,
            completed_at=datetime.now(UTC),
            is_complete=True,
        )

        # Calculate score
        score = questionnaire.calculate_score()

        # Update patient compliance based on score
        patient = await self.get_patient_by_id(patient_id)
        if patient:
            patient.compliance_score = score
            patient.compliance_level = self._score_to_compliance_level(score)

        self.db.add(questionnaire)
        await self.db.flush()
        return questionnaire

    def _score_to_compliance_level(self, score: int) -> str:
        """Convert compliance score to level."""
        if score >= 90:
            return ComplianceLevel.PLATINUM.value
        elif score >= 75:
            return ComplianceLevel.GOLD.value
        elif score >= 50:
            return ComplianceLevel.SILVER.value
        elif score >= 25:
            return ComplianceLevel.BRONZE.value
        else:
            return ComplianceLevel.PROBATION.value

    async def get_next_booking_window(
        self, patient_id: str, doctor_booking_window_days: int = 30
    ) -> dict:
        """Calculate when patient can next book an appointment."""
        patient = await self.get_patient_by_id(patient_id)
        if not patient:
            return {
                "can_book": False,
                "earliest_date": None,
                "latest_date": None,
                "reason": "Patient not found",
                "has_active_booking": False,
                "visit_frequency_days": 0,
            }

        # Check for active bookings
        active_booking = await self._get_active_booking(patient_id)
        if active_booking:
            return {
                "can_book": False,
                "earliest_date": None,
                "latest_date": None,
                "reason": "You already have an active booking",
                "has_active_booking": True,
                "visit_frequency_days": patient.visit_interval_days,
            }

        # Get last completed appointment
        last_appointment = await self._get_last_completed_booking(patient_id)

        now = datetime.now(UTC)
        frequency_days = patient.visit_interval_days

        if last_appointment and last_appointment.slot:
            # Calculate earliest based on frequency
            last_visit_date = last_appointment.slot.start_time
            earliest = last_visit_date + timedelta(days=frequency_days)

            # Don't allow booking in the past
            if earliest < now:
                earliest = now
        else:
            # First appointment - can book immediately
            earliest = now

        # Latest is based on doctor's booking window
        latest = now + timedelta(days=doctor_booking_window_days)

        # Check if earliest is beyond the booking window
        if earliest > latest:
            return {
                "can_book": False,
                "earliest_date": earliest,
                "latest_date": latest,
                "reason": f"Your next appointment is due after {earliest.date()}, which is outside the current booking window",
                "has_active_booking": False,
                "visit_frequency_days": frequency_days,
            }

        return {
            "can_book": True,
            "earliest_date": earliest,
            "latest_date": latest,
            "reason": None,
            "has_active_booking": False,
            "visit_frequency_days": frequency_days,
        }

    async def _get_active_booking(self, patient_id: str) -> Booking | None:
        """Get patient's current active booking."""
        result = await self.db.execute(
            select(Booking)
            .where(
                Booking.patient_id == patient_id,
                Booking.status.in_([
                    BookingStatus.PENDING.value,
                    BookingStatus.CONFIRMED.value,
                ]),
            )
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _get_last_completed_booking(self, patient_id: str) -> Booking | None:
        """Get patient's last completed booking."""
        result = await self.db.execute(
            select(Booking)
            .where(
                Booking.patient_id == patient_id,
                Booking.status == BookingStatus.COMPLETED.value,
            )
            .order_by(Booking.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def record_no_show(self, patient_id: str) -> None:
        """Record a no-show and update compliance."""
        patient = await self.get_patient_by_id(patient_id)
        if patient:
            patient.no_shows += 1
            patient.total_appointments += 1
            await self._recalculate_compliance(patient)

    async def record_late_cancellation(self, patient_id: str) -> None:
        """Record a late cancellation and update compliance."""
        patient = await self.get_patient_by_id(patient_id)
        if patient:
            patient.late_cancellations += 1
            await self._recalculate_compliance(patient)

    async def record_completed_appointment(self, patient_id: str) -> None:
        """Record a completed appointment."""
        patient = await self.get_patient_by_id(patient_id)
        if patient:
            patient.total_appointments += 1
            await self._recalculate_compliance(patient)

    async def _recalculate_compliance(self, patient: Patient) -> None:
        """Recalculate patient compliance based on history."""
        if patient.total_appointments == 0:
            return

        # Base score from questionnaire (if exists)
        base_score = patient.compliance_score

        # Penalty for no-shows (10 points each)
        no_show_penalty = patient.no_shows * 10

        # Penalty for late cancellations (5 points each)
        cancel_penalty = patient.late_cancellations * 5

        # Bonus for good attendance (1 point per completed without issues)
        good_appointments = patient.total_appointments - patient.no_shows
        attendance_bonus = min(good_appointments * 2, 20)  # Max 20 bonus

        # Calculate new score
        new_score = max(0, min(100, base_score - no_show_penalty - cancel_penalty + attendance_bonus))
        patient.compliance_score = new_score
        patient.compliance_level = self._score_to_compliance_level(new_score)
