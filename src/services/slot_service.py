"""Slot service for managing doctor availability."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.patient import ComplianceLevel, Patient
from src.models.slot import Slot, SlotStatus, SlotType
from src.schemas.slot import SlotBulkCreate, SlotCreate, SlotUpdate


# Compliance level priority order
COMPLIANCE_PRIORITY = {
    ComplianceLevel.PLATINUM.value: 5,
    ComplianceLevel.GOLD.value: 4,
    ComplianceLevel.SILVER.value: 3,
    ComplianceLevel.BRONZE.value: 2,
    ComplianceLevel.PROBATION.value: 1,
}


class SlotService:
    """Service for slot management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_slot(self, doctor_id: str, data: SlotCreate) -> Slot:
        """Create a single slot."""
        slot = Slot(
            doctor_id=doctor_id,
            start_time=data.start_time,
            end_time=data.end_time,
            duration_minutes=data.duration_minutes,
            slot_type=data.slot_type.value,
            is_priority_only=data.is_priority_only,
            is_urgent_only=data.is_urgent_only,
            min_compliance_level=data.min_compliance_level.value if data.min_compliance_level else None,
        )
        self.db.add(slot)
        await self.db.flush()
        return slot

    async def create_bulk_slots(self, doctor_id: str, data: SlotBulkCreate) -> list[Slot]:
        """Create multiple slots based on a recurring schedule."""
        slots = []
        recurrence_group_id = str(uuid4())

        current_date = data.start_date.replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=UTC
        )
        end_date = data.end_date.replace(tzinfo=UTC)

        while current_date <= end_date:
            weekday = current_date.weekday()

            if weekday in data.weekdays:
                for time_str in data.start_times:
                    hour, minute = map(int, time_str.split(":"))
                    start_time = current_date.replace(hour=hour, minute=minute)
                    end_time = start_time + timedelta(minutes=data.duration_minutes)

                    # Don't create slots in the past
                    if start_time > datetime.now(UTC):
                        slot = Slot(
                            doctor_id=doctor_id,
                            start_time=start_time,
                            end_time=end_time,
                            duration_minutes=data.duration_minutes,
                            slot_type=data.slot_type.value,
                            is_priority_only=data.is_priority_only,
                            is_urgent_only=data.is_urgent_only,
                            min_compliance_level=data.min_compliance_level.value if data.min_compliance_level else None,
                            is_recurring=True,
                            recurrence_group_id=recurrence_group_id,
                        )
                        slots.append(slot)
                        self.db.add(slot)

            current_date += timedelta(days=1)

        await self.db.flush()
        return slots

    async def get_slot_by_id(self, slot_id: str) -> Slot | None:
        """Get slot by ID."""
        result = await self.db.execute(select(Slot).where(Slot.id == slot_id))
        return result.scalar_one_or_none()

    async def get_doctor_slots(
        self,
        doctor_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        status: SlotStatus | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Slot], int]:
        """Get doctor's slots with optional filters."""
        query = select(Slot).where(Slot.doctor_id == doctor_id)

        if start_date:
            query = query.where(Slot.start_time >= start_date)
        if end_date:
            query = query.where(Slot.start_time <= end_date)
        if status:
            query = query.where(Slot.status == status.value)

        # Count total
        count_result = await self.db.execute(
            select(Slot.id).where(Slot.doctor_id == doctor_id)
        )
        total = len(count_result.all())

        # Apply pagination and ordering
        query = (
            query.order_by(Slot.start_time)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def get_available_slots_for_patient(
        self,
        doctor_id: str,
        patient: Patient,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Slot]:
        """Get slots available to a specific patient based on their compliance level."""
        patient_compliance_priority = COMPLIANCE_PRIORITY.get(
            patient.compliance_level, 1
        )

        # Base query for available slots
        query = select(Slot).where(
            and_(
                Slot.doctor_id == doctor_id,
                Slot.status == SlotStatus.AVAILABLE.value,
                Slot.start_time >= start_date,
                Slot.start_time <= end_date,
                Slot.start_time > datetime.now(UTC),  # Not in the past
            )
        )

        result = await self.db.execute(query.order_by(Slot.start_time))
        all_slots = list(result.scalars().all())

        # Filter based on patient compliance
        available_slots = []
        for slot in all_slots:
            # Check if patient meets compliance requirements
            if slot.min_compliance_level:
                min_priority = COMPLIANCE_PRIORITY.get(slot.min_compliance_level, 1)
                if patient_compliance_priority < min_priority:
                    continue

            # Check priority-only slots
            if slot.is_priority_only:
                # Only high-compliance patients can see these
                if patient_compliance_priority < 4:  # Below GOLD
                    continue

            # Check urgent-only slots
            if slot.is_urgent_only:
                # These are reserved for urgent cases - skip for normal booking
                continue

            available_slots.append(slot)

        return available_slots

    async def update_slot(self, slot_id: str, data: SlotUpdate) -> Slot | None:
        """Update a slot."""
        slot = await self.get_slot_by_id(slot_id)
        if not slot:
            return None

        for field, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                if hasattr(value, "value"):  # Enum
                    setattr(slot, field, value.value)
                else:
                    setattr(slot, field, value)

        await self.db.flush()
        return slot

    async def mark_slot_booked(self, slot_id: str) -> Slot | None:
        """Mark a slot as booked."""
        slot = await self.get_slot_by_id(slot_id)
        if slot and slot.status == SlotStatus.AVAILABLE.value:
            slot.status = SlotStatus.BOOKED.value
            await self.db.flush()
            return slot
        return None

    async def release_slot(self, slot_id: str) -> Slot | None:
        """Release a booked slot back to available."""
        slot = await self.get_slot_by_id(slot_id)
        if slot and slot.status == SlotStatus.BOOKED.value:
            slot.status = SlotStatus.AVAILABLE.value
            await self.db.flush()
            return slot
        return None

    async def block_slot(self, slot_id: str) -> Slot | None:
        """Block a slot (doctor unavailable)."""
        slot = await self.get_slot_by_id(slot_id)
        if slot:
            slot.status = SlotStatus.BLOCKED.value
            await self.db.flush()
            return slot
        return None

    async def delete_recurring_slots(self, recurrence_group_id: str) -> int:
        """Delete all future slots in a recurrence group."""
        result = await self.db.execute(
            select(Slot).where(
                and_(
                    Slot.recurrence_group_id == recurrence_group_id,
                    Slot.start_time > datetime.now(UTC),
                    Slot.status == SlotStatus.AVAILABLE.value,
                )
            )
        )
        slots = list(result.scalars().all())

        count = 0
        for slot in slots:
            await self.db.delete(slot)
            count += 1

        await self.db.flush()
        return count

    async def auto_generate_slots(
        self,
        doctor_id: str,
        days: int,
        weekdays: list[int],
        start_times: list[str],
        duration_minutes: int,
        slot_distribution: dict,
    ) -> list[Slot]:
        """Auto-generate slots for specified days with type distribution.

        Args:
            doctor_id: The doctor's ID
            days: Number of days to generate slots for
            weekdays: List of weekday indices (0=Monday, 6=Sunday)
            start_times: List of time strings ["09:00", "14:00", ...]
            duration_minutes: Duration of each slot
            slot_distribution: Dict with percentages {"first_visit": 20, "follow_up": 70, "emergency": 10}

        Returns:
            List of created Slot objects
        """
        slots: list[Slot] = []
        recurrence_group_id = str(uuid4())

        # Calculate slots per type based on total slots per day
        slots_per_day = len(start_times)
        first_visit_pct = slot_distribution.get("first_visit", 20) / 100
        follow_up_pct = slot_distribution.get("follow_up", 70) / 100
        emergency_pct = slot_distribution.get("emergency", 10) / 100

        # Distribute slot types across time slots
        # Use a rotating pattern to mix slot types throughout the day
        slot_types_per_day: list[SlotType] = []

        first_visit_count = max(1, round(slots_per_day * first_visit_pct))
        emergency_count = max(1, round(slots_per_day * emergency_pct))
        follow_up_count = slots_per_day - first_visit_count - emergency_count

        # Build pattern: first visits in morning, emergency throughout, follow-ups fill rest
        for i in range(slots_per_day):
            if i < first_visit_count:
                slot_types_per_day.append(SlotType.FIRST_VISIT)
            elif i >= slots_per_day - emergency_count:
                slot_types_per_day.append(SlotType.EMERGENCY)
            else:
                slot_types_per_day.append(SlotType.FOLLOW_UP)

        current_date = datetime.now(UTC).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_date = current_date + timedelta(days=days)

        while current_date <= end_date:
            weekday = current_date.weekday()

            if weekday in weekdays:
                for idx, time_str in enumerate(sorted(start_times)):
                    hour, minute = map(int, time_str.split(":"))
                    start_time = current_date.replace(hour=hour, minute=minute)
                    end_time = start_time + timedelta(minutes=duration_minutes)

                    # Skip slots in the past
                    if start_time <= datetime.now(UTC):
                        continue

                    # Check if slot already exists
                    existing = await self.db.execute(
                        select(Slot).where(
                            and_(
                                Slot.doctor_id == doctor_id,
                                Slot.start_time == start_time,
                            )
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue

                    slot_type = slot_types_per_day[idx % len(slot_types_per_day)]

                    slot = Slot(
                        doctor_id=doctor_id,
                        start_time=start_time,
                        end_time=end_time,
                        duration_minutes=duration_minutes,
                        slot_type=slot_type.value,
                        is_priority_only=False,
                        is_urgent_only=(slot_type == SlotType.EMERGENCY),
                        is_recurring=True,
                        recurrence_group_id=recurrence_group_id,
                    )
                    slots.append(slot)
                    self.db.add(slot)

            current_date += timedelta(days=1)

        await self.db.flush()
        return slots

    async def get_available_slots_for_emergency(
        self,
        doctor_id: str,
        patient: Patient,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Slot]:
        """Get emergency slots available to a patient (bypasses normal restrictions)."""
        query = select(Slot).where(
            and_(
                Slot.doctor_id == doctor_id,
                Slot.slot_type == SlotType.EMERGENCY.value,
                Slot.status == SlotStatus.AVAILABLE.value,
                Slot.start_time >= start_date,
                Slot.start_time <= end_date,
                Slot.start_time > datetime.now(UTC),
            )
        )

        result = await self.db.execute(query.order_by(Slot.start_time))
        return list(result.scalars().all())

    async def get_dates_with_available_slots(
        self,
        doctor_id: str,
        start_date: datetime,
        end_date: datetime,
        slot_type: SlotType | None = None,
    ) -> list[datetime]:
        """Get list of dates that have available slots.

        Used to grey out unavailable dates in patient calendar.
        """
        query = select(Slot.start_time).where(
            and_(
                Slot.doctor_id == doctor_id,
                Slot.status == SlotStatus.AVAILABLE.value,
                Slot.start_time >= start_date,
                Slot.start_time <= end_date,
                Slot.start_time > datetime.now(UTC),
            )
        )

        if slot_type:
            query = query.where(Slot.slot_type == slot_type.value)

        result = await self.db.execute(query)
        slot_times = result.scalars().all()

        # Extract unique dates
        unique_dates = list({
            st.replace(hour=0, minute=0, second=0, microsecond=0)
            for st in slot_times
        })

        return sorted(unique_dates)
