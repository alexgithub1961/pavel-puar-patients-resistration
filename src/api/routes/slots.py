"""Slot routes."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import DB, CurrentDoctor, CurrentPatient
from src.models.slot import SlotStatus, SlotType
from src.schemas.slot import (
    AvailableDatesResponse,
    SlotAutoGenerateRequest,
    SlotAutoGenerateResponse,
    SlotAvailableResponse,
    SlotBulkCreate,
    SlotCreate,
    SlotListResponse,
    SlotResponse,
    SlotUpdate,
)
from src.services.patient_service import PatientService
from src.services.slot_service import SlotService

router = APIRouter()


# Doctor endpoints
@router.post("/", response_model=SlotResponse)
async def create_slot(
    data: SlotCreate,
    doctor: CurrentDoctor,
    db: DB,
) -> SlotResponse:
    """Create a single appointment slot."""
    service = SlotService(db)
    slot = await service.create_slot(doctor.id, data)
    return SlotResponse.model_validate(slot)


@router.post("/bulk", response_model=list[SlotResponse])
async def create_bulk_slots(
    data: SlotBulkCreate,
    doctor: CurrentDoctor,
    db: DB,
) -> list[SlotResponse]:
    """Create multiple recurring slots."""
    service = SlotService(db)
    slots = await service.create_bulk_slots(doctor.id, data)
    return [SlotResponse.model_validate(s) for s in slots]


@router.get("/doctor", response_model=SlotListResponse)
async def get_doctor_slots(
    doctor: CurrentDoctor,
    db: DB,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    status: SlotStatus | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> SlotListResponse:
    """Get doctor's slots with filters."""
    service = SlotService(db)
    slots, total = await service.get_doctor_slots(
        doctor.id, start_date, end_date, status, page, page_size
    )

    return SlotListResponse(
        items=[SlotResponse.model_validate(s) for s in slots],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch("/{slot_id}", response_model=SlotResponse)
async def update_slot(
    slot_id: str,
    data: SlotUpdate,
    doctor: CurrentDoctor,
    db: DB,
) -> SlotResponse:
    """Update a slot."""
    service = SlotService(db)
    slot = await service.get_slot_by_id(slot_id)

    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found",
        )

    if slot.doctor_id != doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this slot",
        )

    updated = await service.update_slot(slot_id, data)
    return SlotResponse.model_validate(updated)


@router.post("/{slot_id}/block")
async def block_slot(
    slot_id: str,
    doctor: CurrentDoctor,
    db: DB,
) -> dict:
    """Block a slot (mark as unavailable)."""
    service = SlotService(db)
    slot = await service.get_slot_by_id(slot_id)

    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found",
        )

    if slot.doctor_id != doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this slot",
        )

    await service.block_slot(slot_id)
    return {"status": "blocked", "slot_id": slot_id}


@router.delete("/recurring/{recurrence_group_id}")
async def delete_recurring_slots(
    recurrence_group_id: str,
    doctor: CurrentDoctor,
    db: DB,
) -> dict:
    """Delete all future slots in a recurrence group."""
    service = SlotService(db)
    count = await service.delete_recurring_slots(recurrence_group_id)
    return {"deleted_count": count, "recurrence_group_id": recurrence_group_id}


@router.post("/auto-generate", response_model=SlotAutoGenerateResponse)
async def auto_generate_slots(
    data: SlotAutoGenerateRequest,
    doctor: CurrentDoctor,
    db: DB,
) -> SlotAutoGenerateResponse:
    """Auto-generate slots for next N days with distribution from doctor settings."""
    service = SlotService(db)

    # Use doctor's slot distribution settings
    distribution = doctor.slot_distribution or {
        "first_visit": 20,
        "follow_up": 70,
        "emergency": 10,
    }

    slots = await service.auto_generate_slots(
        doctor_id=doctor.id,
        days=data.days,
        weekdays=data.weekdays,
        start_times=data.start_times,
        duration_minutes=data.duration_minutes,
        slot_distribution=distribution,
    )

    recurrence_group_id = slots[0].recurrence_group_id if slots else ""

    return SlotAutoGenerateResponse(
        slots_created=len(slots),
        recurrence_group_id=recurrence_group_id or "",
        distribution=distribution,
    )


# Patient endpoints
@router.get("/available", response_model=list[SlotAvailableResponse])
async def get_available_slots(
    patient: CurrentPatient,
    db: DB,
    doctor_id: str = Query(..., description="Doctor ID to find slots for"),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[SlotAvailableResponse]:
    """Get available slots for patient's booking window."""
    # Get patient's booking window
    patient_service = PatientService(db)
    window = await patient_service.get_next_booking_window(patient.id)

    if not window["can_book"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=window["reason"],
        )

    # Use provided dates or default to booking window
    search_start = start_date or window["earliest_date"]
    search_end = end_date or window["latest_date"]

    # Ensure within booking window
    if search_start < window["earliest_date"]:
        search_start = window["earliest_date"]
    if search_end > window["latest_date"]:
        search_end = window["latest_date"]

    slot_service = SlotService(db)
    slots = await slot_service.get_available_slots_for_patient(
        doctor_id, patient, search_start, search_end
    )

    # Get doctor name
    from sqlalchemy import select
    from src.models.doctor import Doctor

    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    doctor = result.scalar_one_or_none()
    doctor_name = doctor.full_name if doctor else "Unknown"

    return [
        SlotAvailableResponse(
            id=slot.id,
            start_time=slot.start_time,
            end_time=slot.end_time,
            duration_minutes=slot.duration_minutes,
            doctor_name=doctor_name,
            slot_type=SlotType(slot.slot_type),
        )
        for slot in slots
    ]


@router.get("/available-dates", response_model=AvailableDatesResponse)
async def get_available_dates(
    patient: CurrentPatient,
    db: DB,
    doctor_id: str = Query(..., description="Doctor ID to find slots for"),
    slot_type: SlotType | None = Query(None, description="Filter by slot type"),
) -> AvailableDatesResponse:
    """Get dates that have available slots for calendar UI.

    Used to grey out unavailable dates in the patient booking calendar.
    """
    patient_service = PatientService(db)
    window = await patient_service.get_next_booking_window(patient.id)

    if not window["can_book"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=window["reason"],
        )

    slot_service = SlotService(db)
    dates = await slot_service.get_dates_with_available_slots(
        doctor_id=doctor_id,
        start_date=window["earliest_date"],
        end_date=window["latest_date"],
        slot_type=slot_type,
    )

    # Count total available slots
    from sqlalchemy import select, func
    from src.models.slot import Slot

    count_query = select(func.count(Slot.id)).where(
        Slot.doctor_id == doctor_id,
        Slot.status == SlotStatus.AVAILABLE.value,
        Slot.start_time >= window["earliest_date"],
        Slot.start_time <= window["latest_date"],
        Slot.start_time > datetime.now(UTC),
    )
    if slot_type:
        count_query = count_query.where(Slot.slot_type == slot_type.value)

    result = await db.execute(count_query)
    total_slots = result.scalar() or 0

    return AvailableDatesResponse(
        dates=dates,
        total_slots=total_slots,
    )


@router.get("/available/emergency", response_model=list[SlotAvailableResponse])
async def get_emergency_slots(
    patient: CurrentPatient,
    db: DB,
    doctor_id: str = Query(..., description="Doctor ID to find slots for"),
) -> list[SlotAvailableResponse]:
    """Get available emergency slots for urgent booking.

    Emergency slots bypass normal booking window restrictions.
    """
    slot_service = SlotService(db)

    # For emergency, allow booking from now to 30 days ahead
    start_date = datetime.now(UTC)
    end_date = start_date + timedelta(days=30)

    slots = await slot_service.get_available_slots_for_emergency(
        doctor_id=doctor_id,
        patient=patient,
        start_date=start_date,
        end_date=end_date,
    )

    # Get doctor name
    from sqlalchemy import select
    from src.models.doctor import Doctor

    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    doctor = result.scalar_one_or_none()
    doctor_name = doctor.full_name if doctor else "Unknown"

    return [
        SlotAvailableResponse(
            id=slot.id,
            start_time=slot.start_time,
            end_time=slot.end_time,
            duration_minutes=slot.duration_minutes,
            doctor_name=doctor_name,
            slot_type=SlotType(slot.slot_type),
        )
        for slot in slots
    ]
