"""Booking routes."""

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import DB, CurrentPatient
from src.models.booking import BookingStatus
from src.schemas.booking import (
    BookingCreate,
    BookingListResponse,
    BookingResponse,
    BookingWithSlotResponse,
    CancelRequest,
    RescheduleRequest,
)
from src.schemas.questionnaire import (
    TriageQuestionnaireCreate,
    TriageQuestionnaireResponse,
)
from src.services.booking_service import BookingService

router = APIRouter()


@router.post("/", response_model=BookingResponse)
async def create_booking(
    data: BookingCreate,
    patient: CurrentPatient,
    db: DB,
    doctor_id: str = Query(..., description="Doctor ID for the booking"),
) -> BookingResponse:
    """Create a new appointment booking."""
    service = BookingService(db)
    result = await service.create_booking(patient.id, data, doctor_id)

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"],
        )

    return BookingResponse.model_validate(result)


@router.get("/", response_model=BookingListResponse)
async def get_patient_bookings(
    patient: CurrentPatient,
    db: DB,
    include_past: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> BookingListResponse:
    """Get patient's bookings."""
    service = BookingService(db)
    bookings, total = await service.get_patient_bookings(
        patient.id, include_past, page, page_size
    )

    # Get doctor info for each booking
    items = []
    for booking in bookings:
        doctor_name = "Unknown"
        if booking.slot and booking.slot.doctor:
            doctor_name = booking.slot.doctor.full_name

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
            slot_start_time=booking.slot.start_time if booking.slot else None,
            slot_end_time=booking.slot.end_time if booking.slot else None,
            doctor_name=doctor_name,
        )
        items.append(item)

    return BookingListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    patient: CurrentPatient,
    db: DB,
) -> BookingResponse:
    """Get a specific booking."""
    service = BookingService(db)
    booking = await service.get_booking_by_id(booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.patient_id != patient.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this booking",
        )

    return BookingResponse.model_validate(booking)


@router.post("/{booking_id}/triage", response_model=TriageQuestionnaireResponse)
async def submit_triage_questionnaire(
    booking_id: str,
    data: TriageQuestionnaireCreate,
    patient: CurrentPatient,
    db: DB,
) -> TriageQuestionnaireResponse:
    """Submit triage questionnaire for cancellation/reschedule."""
    service = BookingService(db)

    # Verify ownership
    booking = await service.get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.patient_id != patient.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this booking",
        )

    # Ensure booking_id matches
    data_dict = data.model_dump()
    data_dict["booking_id"] = booking_id

    result = await service.submit_triage_questionnaire(
        booking_id,
        TriageQuestionnaireCreate.model_validate(data_dict),
    )

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"],
        )

    return TriageQuestionnaireResponse.model_validate(result)


@router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: str,
    data: CancelRequest,
    patient: CurrentPatient,
    db: DB,
) -> dict:
    """Cancel a booking (requires approved triage)."""
    service = BookingService(db)
    result = await service.cancel_booking(
        booking_id, data.triage_questionnaire_id, patient.id
    )

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"],
        )

    return {"status": "cancelled", "booking_id": booking_id}


@router.post("/{booking_id}/reschedule", response_model=BookingResponse)
async def reschedule_booking(
    booking_id: str,
    data: RescheduleRequest,
    patient: CurrentPatient,
    db: DB,
) -> BookingResponse:
    """Reschedule a booking to a new slot (requires approved triage)."""
    service = BookingService(db)
    result = await service.reschedule_booking(
        booking_id, data.new_slot_id, data.triage_questionnaire_id, patient.id
    )

    if isinstance(result, dict) and "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"],
        )

    return BookingResponse.model_validate(result)
