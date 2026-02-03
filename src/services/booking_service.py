"""Booking service for managing appointments."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.booking import Booking, BookingStatus
from src.models.doctor import Doctor
from src.models.patient import Patient
from src.models.questionnaire import TriageQuestionnaire, UrgencyLevel
from src.models.slot import Slot, SlotStatus
from src.schemas.booking import BookingCreate
from src.schemas.questionnaire import TriageQuestionnaireCreate
from src.services.patient_service import PatientService
from src.services.slot_service import SlotService


class BookingService:
    """Service for booking operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.patient_service = PatientService(db)
        self.slot_service = SlotService(db)

    async def create_booking(
        self, patient_id: str, data: BookingCreate, doctor_id: str
    ) -> Booking | dict:
        """Create a new booking for a patient."""
        from src.models.slot import SlotType

        # Check slot availability
        slot = await self.slot_service.get_slot_by_id(data.slot_id)
        if not slot:
            return {"error": "Slot not found"}

        if slot.status != SlotStatus.AVAILABLE.value:
            return {"error": "Slot is not available"}

        if slot.doctor_id != doctor_id:
            return {"error": "Slot does not belong to this doctor"}

        # Check patient eligibility
        patient = await self.patient_service.get_patient_by_id(patient_id)
        if not patient:
            return {"error": "Patient not found"}

        # Emergency bookings bypass normal window restrictions
        is_emergency = data.is_emergency or False

        if is_emergency:
            # Validate emergency booking requirements
            if slot.slot_type != SlotType.EMERGENCY.value:
                return {"error": "Emergency bookings can only use emergency slots"}
            if not data.urgency_reason or len(data.urgency_reason) < 10:
                return {"error": "Emergency bookings require an urgency reason (min 10 characters)"}
        else:
            # Normal booking - verify booking window
            booking_window = await self.patient_service.get_next_booking_window(
                patient_id, doctor_booking_window_days=30
            )

            if not booking_window["can_book"]:
                return {"error": booking_window["reason"]}

            # Check slot is within allowed window
            if booking_window["earliest_date"] and slot.start_time < booking_window["earliest_date"]:
                return {"error": "This slot is too early for your visit frequency"}

            if booking_window["latest_date"] and slot.start_time > booking_window["latest_date"]:
                return {"error": "This slot is outside the booking window"}

            # Non-emergency bookings cannot book emergency slots
            if slot.slot_type == SlotType.EMERGENCY.value:
                return {"error": "This slot is reserved for emergency bookings"}

        # Create booking
        booking = Booking(
            patient_id=patient_id,
            slot_id=data.slot_id,
            reason=data.reason,
            notes=data.notes,
            is_emergency=is_emergency,
            urgency_reason=data.urgency_reason if is_emergency else None,
            status=BookingStatus.CONFIRMED.value,
            confirmed_at=datetime.now(UTC),
        )

        # Mark slot as booked
        await self.slot_service.mark_slot_booked(data.slot_id)

        self.db.add(booking)
        await self.db.flush()
        return booking

    async def get_booking_by_id(self, booking_id: str) -> Booking | None:
        """Get booking by ID with related data."""
        result = await self.db.execute(
            select(Booking)
            .options(selectinload(Booking.slot), selectinload(Booking.patient))
            .where(Booking.id == booking_id)
        )
        return result.scalar_one_or_none()

    async def get_patient_bookings(
        self,
        patient_id: str,
        include_past: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Booking], int]:
        """Get patient's bookings."""
        query = (
            select(Booking)
            .options(selectinload(Booking.slot).selectinload(Slot.doctor))
            .where(Booking.patient_id == patient_id)
        )

        if not include_past:
            query = query.where(
                Booking.status.in_([
                    BookingStatus.PENDING.value,
                    BookingStatus.CONFIRMED.value,
                ])
            )

        # Count
        count_query = select(Booking.id).where(Booking.patient_id == patient_id)
        if not include_past:
            count_query = count_query.where(
                Booking.status.in_([
                    BookingStatus.PENDING.value,
                    BookingStatus.CONFIRMED.value,
                ])
            )
        count_result = await self.db.execute(count_query)
        total = len(count_result.all())

        # Paginate
        query = (
            query.order_by(Booking.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def get_doctor_bookings(
        self,
        doctor_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        status: BookingStatus | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Booking], int]:
        """Get doctor's bookings (via slots)."""
        query = (
            select(Booking)
            .join(Slot)
            .options(selectinload(Booking.slot), selectinload(Booking.patient))
            .where(Slot.doctor_id == doctor_id)
        )

        if start_date:
            query = query.where(Slot.start_time >= start_date)
        if end_date:
            query = query.where(Slot.start_time <= end_date)
        if status:
            query = query.where(Booking.status == status.value)

        # Count
        count_query = select(Booking.id).join(Slot).where(Slot.doctor_id == doctor_id)
        count_result = await self.db.execute(count_query)
        total = len(count_result.all())

        # Paginate
        query = (
            query.order_by(Slot.start_time)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def submit_triage_questionnaire(
        self, booking_id: str, data: TriageQuestionnaireCreate
    ) -> TriageQuestionnaire | dict:
        """Submit triage questionnaire for cancel/reschedule."""
        booking = await self.get_booking_by_id(booking_id)
        if not booking:
            return {"error": "Booking not found"}

        if not booking.is_cancellable:
            return {"error": "This booking cannot be modified"}

        # Check if free slots exist for reschedule
        if data.request_type == "reschedule":
            has_slots = await self._check_available_slots_exist(
                booking.slot.doctor_id, booking.patient_id
            )
            if not has_slots:
                return {"error": "No available slots for rescheduling"}

        triage = TriageQuestionnaire(
            booking_id=booking_id,
            request_type=data.request_type,
            reason_category=data.reason_category,
            reason_details=data.reason_details,
            condition_changed=data.condition_changed,
            symptoms_worsened=data.symptoms_worsened,
            new_symptoms=data.new_symptoms,
            available_within_week=data.available_within_week,
            preferred_times=data.preferred_times,
            acknowledges_impact=data.acknowledges_impact,
            commits_to_new_appointment=data.commits_to_new_appointment,
        )

        # Calculate urgency
        urgency = triage.calculate_urgency()

        # Auto-approve routine cancellations/reschedules
        if urgency == UrgencyLevel.ROUTINE and not triage.requires_doctor_review:
            triage.is_approved = True
            triage.approved_by = "system"
            triage.approved_at = datetime.now(UTC)

        self.db.add(triage)
        await self.db.flush()
        return triage

    async def cancel_booking(
        self, booking_id: str, triage_id: str, patient_id: str
    ) -> Booking | dict:
        """Cancel a booking after triage approval."""
        booking = await self.get_booking_by_id(booking_id)
        if not booking:
            return {"error": "Booking not found"}

        if booking.patient_id != patient_id:
            return {"error": "Not authorized to cancel this booking"}

        # Verify triage approval
        triage = await self._get_triage(triage_id)
        if not triage or triage.booking_id != booking_id:
            return {"error": "Invalid triage questionnaire"}

        if triage.is_approved is None:
            return {"error": "Triage questionnaire pending approval"}

        if not triage.is_approved:
            return {"error": f"Cancellation denied: {triage.rejection_reason}"}

        # Check for late cancellation (less than 24h)
        if booking.slot and booking.slot.start_time:
            hours_until = (booking.slot.start_time - datetime.now(UTC)).total_seconds() / 3600
            if hours_until < 24:
                await self.patient_service.record_late_cancellation(patient_id)

        # Cancel booking
        booking.status = BookingStatus.CANCELLED_BY_PATIENT.value
        booking.cancelled_at = datetime.now(UTC)
        booking.cancellation_reason = triage.reason_details or triage.reason_category

        # Release slot
        await self.slot_service.release_slot(booking.slot_id)

        await self.db.flush()
        return booking

    async def reschedule_booking(
        self,
        booking_id: str,
        new_slot_id: str,
        triage_id: str,
        patient_id: str,
    ) -> Booking | dict:
        """Reschedule a booking to a new slot."""
        booking = await self.get_booking_by_id(booking_id)
        if not booking:
            return {"error": "Booking not found"}

        if booking.patient_id != patient_id:
            return {"error": "Not authorized to reschedule this booking"}

        # Verify triage approval
        triage = await self._get_triage(triage_id)
        if not triage or triage.booking_id != booking_id:
            return {"error": "Invalid triage questionnaire"}

        if triage.is_approved is None:
            return {"error": "Triage questionnaire pending approval"}

        if not triage.is_approved:
            return {"error": f"Reschedule denied: {triage.rejection_reason}"}

        # Check new slot availability
        new_slot = await self.slot_service.get_slot_by_id(new_slot_id)
        if not new_slot or new_slot.status != SlotStatus.AVAILABLE.value:
            return {"error": "New slot is not available"}

        # Check for late reschedule
        if booking.slot and booking.slot.start_time:
            hours_until = (booking.slot.start_time - datetime.now(UTC)).total_seconds() / 3600
            if hours_until < 24:
                await self.patient_service.record_late_cancellation(patient_id)

        # Mark old booking as rescheduled
        booking.status = BookingStatus.RESCHEDULED.value
        booking.cancelled_at = datetime.now(UTC)

        # Release old slot
        await self.slot_service.release_slot(booking.slot_id)

        # Create new booking
        new_booking = Booking(
            patient_id=patient_id,
            slot_id=new_slot_id,
            reason=booking.reason,
            notes=booking.notes,
            status=BookingStatus.CONFIRMED.value,
            confirmed_at=datetime.now(UTC),
            rescheduled_from_id=booking_id,
        )

        # Update old booking with reference to new
        booking.rescheduled_to_id = new_booking.id

        # Mark new slot as booked
        await self.slot_service.mark_slot_booked(new_slot_id)

        self.db.add(new_booking)
        await self.db.flush()
        return new_booking

    async def mark_no_show(self, booking_id: str) -> Booking | dict:
        """Mark a booking as no-show (doctor action)."""
        booking = await self.get_booking_by_id(booking_id)
        if not booking:
            return {"error": "Booking not found"}

        booking.status = BookingStatus.NO_SHOW.value
        await self.patient_service.record_no_show(booking.patient_id)

        await self.db.flush()
        return booking

    async def mark_completed(self, booking_id: str) -> Booking | dict:
        """Mark a booking as completed (doctor action)."""
        booking = await self.get_booking_by_id(booking_id)
        if not booking:
            return {"error": "Booking not found"}

        booking.status = BookingStatus.COMPLETED.value
        await self.patient_service.record_completed_appointment(booking.patient_id)

        await self.db.flush()
        return booking

    async def _get_triage(self, triage_id: str) -> TriageQuestionnaire | None:
        """Get triage questionnaire by ID."""
        result = await self.db.execute(
            select(TriageQuestionnaire).where(TriageQuestionnaire.id == triage_id)
        )
        return result.scalar_one_or_none()

    async def _check_available_slots_exist(
        self, doctor_id: str, patient_id: str
    ) -> bool:
        """Check if any available slots exist for the patient."""
        patient = await self.patient_service.get_patient_by_id(patient_id)
        if not patient:
            return False

        now = datetime.now(UTC)
        result = await self.db.execute(
            select(Slot)
            .where(
                and_(
                    Slot.doctor_id == doctor_id,
                    Slot.status == SlotStatus.AVAILABLE.value,
                    Slot.start_time > now,
                )
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None
