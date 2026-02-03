"""Doctor routes."""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import DB, CurrentDoctor
from src.models.booking import BookingStatus
from src.schemas.booking import BookingListResponse, BookingWithSlotResponse
from src.schemas.doctor import DoctorResponse, DoctorUpdate
from src.schemas.patient import PatientListResponse, PatientPublicResponse
from src.services.booking_service import BookingService
from src.services.prioritisation_service import PrioritisationService

router = APIRouter()


@router.get("/me", response_model=DoctorResponse)
async def get_current_doctor(doctor: CurrentDoctor) -> DoctorResponse:
    """Get current doctor profile."""
    return DoctorResponse.model_validate(doctor)


@router.patch("/me", response_model=DoctorResponse)
async def update_current_doctor(
    data: DoctorUpdate,
    doctor: CurrentDoctor,
    db: DB,
) -> DoctorResponse:
    """Update current doctor profile."""
    from sqlalchemy import select
    from src.models.doctor import Doctor

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(doctor, field, value)

    await db.flush()
    await db.refresh(doctor)
    return DoctorResponse.model_validate(doctor)


@router.get("/me/bookings", response_model=BookingListResponse)
async def get_doctor_bookings(
    doctor: CurrentDoctor,
    db: DB,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    status: BookingStatus | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> BookingListResponse:
    """Get doctor's appointments."""
    service = BookingService(db)
    bookings, total = await service.get_doctor_bookings(
        doctor.id, start_date, end_date, status, page, page_size
    )

    items = []
    for booking in bookings:
        item = BookingWithSlotResponse(
            id=booking.id,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
            patient_id=booking.patient_id,
            slot_id=booking.slot_id,
            status=BookingStatus(booking.status),
            reason=booking.reason,
            notes=booking.notes,
            cancelled_at=booking.cancelled_at,
            cancellation_reason=booking.cancellation_reason,
            rescheduled_from_id=booking.rescheduled_from_id,
            rescheduled_to_id=booking.rescheduled_to_id,
            confirmed_at=booking.confirmed_at,
            reminder_sent=booking.reminder_sent,
            slot_start_time=booking.slot.start_time,
            slot_end_time=booking.slot.end_time,
            doctor_name=doctor.full_name,
        )
        items.append(item)

    return BookingListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/me/bookings/{booking_id}/complete")
async def mark_booking_complete(
    booking_id: str,
    doctor: CurrentDoctor,
    db: DB,
) -> dict:
    """Mark a booking as completed."""
    service = BookingService(db)
    result = await service.mark_completed(booking_id)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"],
        )

    return {"status": "completed", "booking_id": booking_id}


@router.post("/me/bookings/{booking_id}/no-show")
async def mark_booking_no_show(
    booking_id: str,
    doctor: CurrentDoctor,
    db: DB,
) -> dict:
    """Mark a booking as no-show."""
    service = BookingService(db)
    result = await service.mark_no_show(booking_id)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"],
        )

    return {"status": "no_show", "booking_id": booking_id}


@router.get("/me/scarcity")
async def get_slot_scarcity(
    doctor: CurrentDoctor,
    db: DB,
    days_ahead: int = Query(7, ge=1, le=30),
) -> dict:
    """Get slot scarcity analysis."""
    service = PrioritisationService(db)
    return await service.get_scarcity_level(doctor.id, days_ahead)


@router.post("/me/reserve-urgent-slots")
async def reserve_urgent_slots(
    doctor: CurrentDoctor,
    db: DB,
    percentage: float = Query(0.1, ge=0.05, le=0.3),
) -> dict:
    """Reserve a percentage of slots for urgent cases."""
    service = PrioritisationService(db)
    count = await service.reserve_slots_for_urgent(doctor.id, percentage)
    return {"reserved_count": count, "percentage": percentage}


@router.post("/me/release-reserved-slots")
async def release_reserved_slots(
    doctor: CurrentDoctor,
    db: DB,
    hours_before: int = Query(48, ge=12, le=168),
) -> dict:
    """Release unused reserved slots close to appointment time."""
    service = PrioritisationService(db)
    count = await service.release_unused_reserved_slots(doctor.id, hours_before)
    return {"released_count": count, "hours_before": hours_before}


@router.get("/me/patients", response_model=PatientListResponse)
async def get_doctor_patients(
    doctor: CurrentDoctor,
    db: DB,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PatientListResponse:
    """Get patients who have booked with this doctor."""
    from sqlalchemy import select, distinct
    from src.models.booking import Booking
    from src.models.patient import Patient
    from src.models.slot import Slot

    # Get distinct patient IDs from bookings
    query = (
        select(Patient)
        .join(Booking, Booking.patient_id == Patient.id)
        .join(Slot, Booking.slot_id == Slot.id)
        .where(Slot.doctor_id == doctor.id)
        .distinct()
    )

    result = await db.execute(query)
    patients = list(result.scalars().all())
    total = len(patients)

    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    paginated = patients[start:end]

    items = [PatientPublicResponse.model_validate(p) for p in paginated]

    return PatientListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
