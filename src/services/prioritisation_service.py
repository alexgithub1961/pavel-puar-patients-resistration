"""Prioritisation service for slot scarcity management."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.booking import Booking, BookingStatus
from src.models.patient import ComplianceLevel, Patient, PatientCategory
from src.models.slot import Slot, SlotStatus


class PriorityFactor(str, Enum):
    """Factors affecting patient priority."""

    CATEGORY = "category"  # Medical category
    COMPLIANCE = "compliance"  # Compliance level
    URGENCY = "urgency"  # Triage urgency
    WAIT_TIME = "wait_time"  # Days since last visit
    CANCELLATION_HISTORY = "cancellation_history"  # Recent cancellations
    RETURN_AFTER_CANCEL = "return_after_cancel"  # Returning after cancellation


# Category priority weights (higher = more urgent)
CATEGORY_WEIGHTS = {
    PatientCategory.CRITICAL.value: 100,
    PatientCategory.HIGH_RISK.value: 80,
    PatientCategory.MODERATE.value: 60,
    PatientCategory.STABLE.value: 40,
    PatientCategory.MAINTENANCE.value: 20,
    PatientCategory.HEALTHY.value: 10,
}

# Compliance weights
COMPLIANCE_WEIGHTS = {
    ComplianceLevel.PLATINUM.value: 50,
    ComplianceLevel.GOLD.value: 40,
    ComplianceLevel.SILVER.value: 30,
    ComplianceLevel.BRONZE.value: 20,
    ComplianceLevel.PROBATION.value: 10,
}


@dataclass
class PatientPriority:
    """Calculated patient priority for slot allocation."""

    patient_id: str
    total_score: float
    category_score: float
    compliance_score: float
    urgency_score: float
    wait_time_score: float
    cancellation_penalty: float
    return_bonus: float
    can_access_slot: bool
    reason: str | None = None


class PrioritisationService:
    """Service for patient prioritisation during slot scarcity."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_patient_priority(
        self,
        patient: Patient,
        slot: Slot,
        urgency_level: str | None = None,
        is_return_after_cancel: bool = False,
    ) -> PatientPriority:
        """Calculate priority score for a patient for a specific slot."""
        # Base category score
        category_score = CATEGORY_WEIGHTS.get(patient.category, 30)

        # Compliance score
        compliance_score = COMPLIANCE_WEIGHTS.get(patient.compliance_level, 20)

        # Urgency score (from triage)
        urgency_score = 0.0
        if urgency_level:
            urgency_scores = {
                "emergency": 100,
                "urgent": 70,
                "moderate": 40,
                "routine": 10,
            }
            urgency_score = urgency_scores.get(urgency_level, 10)

        # Wait time score (days since last completed appointment)
        wait_time_score = await self._calculate_wait_time_score(patient)

        # Cancellation penalty
        cancellation_penalty = self._calculate_cancellation_penalty(patient)

        # Return after cancel bonus
        return_bonus = 20.0 if is_return_after_cancel else 0.0

        # Total score
        total_score = (
            category_score
            + compliance_score
            + urgency_score
            + wait_time_score
            - cancellation_penalty
            + return_bonus
        )

        # Check if patient can access this slot
        can_access, reason = self._can_access_slot(patient, slot)

        return PatientPriority(
            patient_id=patient.id,
            total_score=total_score,
            category_score=category_score,
            compliance_score=compliance_score,
            urgency_score=urgency_score,
            wait_time_score=wait_time_score,
            cancellation_penalty=cancellation_penalty,
            return_bonus=return_bonus,
            can_access_slot=can_access,
            reason=reason,
        )

    async def rank_patients_for_slot(
        self, slot: Slot, patient_ids: list[str]
    ) -> list[PatientPriority]:
        """Rank multiple patients for a single slot."""
        priorities = []

        for patient_id in patient_ids:
            result = await self.db.execute(
                select(Patient).where(Patient.id == patient_id)
            )
            patient = result.scalar_one_or_none()

            if patient:
                priority = await self.calculate_patient_priority(patient, slot)
                if priority.can_access_slot:
                    priorities.append(priority)

        # Sort by total score descending
        priorities.sort(key=lambda p: p.total_score, reverse=True)
        return priorities

    async def get_reserved_slots(self, doctor_id: str) -> list[Slot]:
        """Get slots reserved for urgent/priority cases."""
        result = await self.db.execute(
            select(Slot).where(
                and_(
                    Slot.doctor_id == doctor_id,
                    Slot.status == SlotStatus.RESERVED.value,
                    Slot.start_time > datetime.now(UTC),
                )
            )
        )
        return list(result.scalars().all())

    async def reserve_slots_for_urgent(
        self, doctor_id: str, percentage: float = 0.1
    ) -> int:
        """Reserve a percentage of available slots for urgent cases."""
        # Get available slots
        result = await self.db.execute(
            select(Slot).where(
                and_(
                    Slot.doctor_id == doctor_id,
                    Slot.status == SlotStatus.AVAILABLE.value,
                    Slot.start_time > datetime.now(UTC),
                )
            )
        )
        available_slots = list(result.scalars().all())

        # Calculate how many to reserve
        total = len(available_slots)
        to_reserve = int(total * percentage)

        # Reserve early slots (more likely to be urgent)
        reserved_count = 0
        for slot in available_slots[:to_reserve]:
            slot.status = SlotStatus.RESERVED.value
            slot.is_urgent_only = True
            reserved_count += 1

        await self.db.flush()
        return reserved_count

    async def release_unused_reserved_slots(self, doctor_id: str, hours_before: int = 48) -> int:
        """Release reserved slots that haven't been used close to appointment time."""
        threshold = datetime.now(UTC) + timedelta(hours=hours_before)

        result = await self.db.execute(
            select(Slot).where(
                and_(
                    Slot.doctor_id == doctor_id,
                    Slot.status == SlotStatus.RESERVED.value,
                    Slot.start_time <= threshold,
                    Slot.start_time > datetime.now(UTC),
                )
            )
        )
        reserved_slots = list(result.scalars().all())

        released_count = 0
        for slot in reserved_slots:
            slot.status = SlotStatus.AVAILABLE.value
            slot.is_urgent_only = False
            released_count += 1

        await self.db.flush()
        return released_count

    async def get_scarcity_level(self, doctor_id: str, days_ahead: int = 7) -> dict:
        """Calculate slot scarcity level for the coming period."""
        now = datetime.now(UTC)
        end_date = now + timedelta(days=days_ahead)

        # Count available slots
        available_result = await self.db.execute(
            select(func.count(Slot.id)).where(
                and_(
                    Slot.doctor_id == doctor_id,
                    Slot.status == SlotStatus.AVAILABLE.value,
                    Slot.start_time >= now,
                    Slot.start_time <= end_date,
                )
            )
        )
        available_count = available_result.scalar() or 0

        # Count total slots
        total_result = await self.db.execute(
            select(func.count(Slot.id)).where(
                and_(
                    Slot.doctor_id == doctor_id,
                    Slot.start_time >= now,
                    Slot.start_time <= end_date,
                )
            )
        )
        total_count = total_result.scalar() or 0

        # Calculate availability percentage
        if total_count == 0:
            availability_pct = 0
        else:
            availability_pct = (available_count / total_count) * 100

        # Determine scarcity level
        if availability_pct >= 50:
            level = "low"
        elif availability_pct >= 25:
            level = "moderate"
        elif availability_pct >= 10:
            level = "high"
        else:
            level = "critical"

        return {
            "level": level,
            "available_slots": available_count,
            "total_slots": total_count,
            "availability_percentage": round(availability_pct, 1),
            "days_ahead": days_ahead,
        }

    async def _calculate_wait_time_score(self, patient: Patient) -> float:
        """Calculate score based on time since last appointment."""
        result = await self.db.execute(
            select(Booking)
            .join(Slot)
            .where(
                and_(
                    Booking.patient_id == patient.id,
                    Booking.status == BookingStatus.COMPLETED.value,
                )
            )
            .order_by(Slot.start_time.desc())
            .limit(1)
        )
        last_booking = result.scalar_one_or_none()

        if not last_booking or not last_booking.slot:
            # First appointment - moderate priority
            return 30.0

        days_since = (datetime.now(UTC) - last_booking.slot.start_time).days

        # More days waiting = higher priority (capped at 50)
        return min(days_since * 0.5, 50.0)

    def _calculate_cancellation_penalty(self, patient: Patient) -> float:
        """Calculate penalty based on cancellation history."""
        # 5 points per no-show, 2 points per late cancellation
        return (patient.no_shows * 5) + (patient.late_cancellations * 2)

    def _can_access_slot(self, patient: Patient, slot: Slot) -> tuple[bool, str | None]:
        """Check if patient can access a specific slot."""
        compliance_priority = COMPLIANCE_WEIGHTS.get(patient.compliance_level, 20)

        # Check minimum compliance level
        if slot.min_compliance_level:
            min_required = COMPLIANCE_WEIGHTS.get(slot.min_compliance_level, 0)
            if compliance_priority < min_required:
                return False, f"Requires {slot.min_compliance_level} compliance level"

        # Check priority-only slots
        if slot.is_priority_only:
            if compliance_priority < COMPLIANCE_WEIGHTS[ComplianceLevel.GOLD.value]:
                return False, "Slot reserved for high-compliance patients"

        # Check urgent-only slots
        if slot.is_urgent_only:
            # Only allow for critical/high-risk patients
            if patient.category not in [
                PatientCategory.CRITICAL.value,
                PatientCategory.HIGH_RISK.value,
            ]:
                return False, "Slot reserved for urgent medical cases"

        return True, None
