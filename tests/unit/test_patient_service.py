"""Tests for PatientService."""

import pytest
from datetime import UTC, datetime, timedelta

from src.models.patient import ComplianceLevel, Patient, PatientCategory
from src.models.booking import Booking, BookingStatus
from src.models.slot import Slot, SlotStatus
from src.services.patient_service import PatientService
from src.schemas.patient import PatientCreate, PatientUpdate
from src.schemas.questionnaire import ComplianceQuestionnaireCreate


@pytest.mark.asyncio
async def test_create_patient(test_session):
    """Test patient creation."""
    service = PatientService(test_session)

    patient_data = PatientCreate(
        email="new_patient@test.com",
        password="testpassword123",
        first_name="New",
        last_name="Patient",
        phone="+1234567890",
        date_of_birth="1990-01-01",
        preferred_language="en",
    )

    patient = await service.create_patient(patient_data)

    assert patient.id is not None
    assert patient.email == "new_patient@test.com"
    assert patient.first_name == "New"
    assert patient.last_name == "Patient"
    assert patient.category == PatientCategory.STABLE.value
    assert patient.compliance_level == ComplianceLevel.SILVER.value


@pytest.mark.asyncio
async def test_get_patient_by_email(test_session, test_patient):
    """Test finding patient by email."""
    service = PatientService(test_session)

    found = await service.get_patient_by_email("patient@test.com")
    assert found is not None
    assert found.id == test_patient.id

    not_found = await service.get_patient_by_email("nonexistent@test.com")
    assert not_found is None


@pytest.mark.asyncio
async def test_authenticate_patient(test_session, test_patient):
    """Test patient authentication."""
    service = PatientService(test_session)

    # Valid credentials
    authenticated = await service.authenticate_patient(
        "patient@test.com", "testpassword123"
    )
    assert authenticated is not None
    assert authenticated.id == test_patient.id

    # Invalid password
    invalid = await service.authenticate_patient("patient@test.com", "wrongpassword")
    assert invalid is None

    # Invalid email
    invalid_email = await service.authenticate_patient(
        "wrong@test.com", "testpassword123"
    )
    assert invalid_email is None


@pytest.mark.asyncio
async def test_submit_compliance_questionnaire(test_session, test_patient):
    """Test compliance questionnaire submission and score calculation."""
    service = PatientService(test_session)

    questionnaire_data = ComplianceQuestionnaireCreate(
        missed_appointments_rating=5,
        cancellation_notice_rating=5,
        schedule_importance_rating=5,
        reschedule_commitment_rating=5,
        flexibility_rating=5,
        agrees_24h_cancellation=True,
        agrees_no_show_penalty=True,
        agrees_reschedule_policy=True,
        agrees_communication_preferences=True,
    )

    questionnaire = await service.submit_compliance_questionnaire(
        test_patient.id, questionnaire_data
    )

    assert questionnaire.id is not None
    assert questionnaire.is_complete is True
    assert questionnaire.calculated_score == 100  # Perfect score

    # Check patient compliance was updated
    updated_patient = await service.get_patient_by_id(test_patient.id)
    assert updated_patient.compliance_score == 100
    assert updated_patient.compliance_level == ComplianceLevel.PLATINUM.value


@pytest.mark.asyncio
async def test_booking_window_no_active_booking(test_session, test_patient):
    """Test booking window calculation when patient has no active booking."""
    service = PatientService(test_session)

    window = await service.get_next_booking_window(test_patient.id)

    assert window["can_book"] is True
    assert window["has_active_booking"] is False
    assert window["earliest_date"] is not None
    assert window["latest_date"] is not None


@pytest.mark.asyncio
async def test_booking_window_with_active_booking(test_session, test_patient, test_doctor):
    """Test booking window calculation when patient has active booking."""
    service = PatientService(test_session)

    # Create a slot and booking
    slot = Slot(
        doctor_id=test_doctor.id,
        start_time=datetime.now(UTC) + timedelta(days=7),
        end_time=datetime.now(UTC) + timedelta(days=7, hours=1),
        status=SlotStatus.BOOKED.value,
    )
    test_session.add(slot)
    await test_session.flush()

    booking = Booking(
        patient_id=test_patient.id,
        slot_id=slot.id,
        status=BookingStatus.CONFIRMED.value,
    )
    test_session.add(booking)
    await test_session.commit()

    window = await service.get_next_booking_window(test_patient.id)

    assert window["can_book"] is False
    assert window["has_active_booking"] is True
    assert window["reason"] == "You already have an active booking"


@pytest.mark.asyncio
async def test_compliance_score_calculation(test_session, test_patient):
    """Test compliance score recalculation based on history."""
    service = PatientService(test_session)

    # Record some no-shows
    await service.record_no_show(test_patient.id)
    await service.record_no_show(test_patient.id)

    patient = await service.get_patient_by_id(test_patient.id)

    assert patient.no_shows == 2
    assert patient.total_appointments == 2
    # Score should be reduced due to no-shows (original 50 - 10*2 penalties)
    assert patient.compliance_score < 50


@pytest.mark.asyncio
async def test_update_patient(test_session, test_patient):
    """Test patient profile update."""
    service = PatientService(test_session)

    update_data = PatientUpdate(
        first_name="Updated",
        phone="+9876543210",
    )

    updated = await service.update_patient(test_patient.id, update_data)

    assert updated.first_name == "Updated"
    assert updated.phone == "+9876543210"
    assert updated.last_name == "Patient"  # Unchanged
