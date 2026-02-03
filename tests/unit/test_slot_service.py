"""Tests for SlotService."""

import pytest
from datetime import UTC, datetime, timedelta

from src.models.patient import ComplianceLevel, Patient
from src.models.slot import Slot, SlotStatus
from src.services.slot_service import SlotService
from src.schemas.slot import SlotCreate, SlotBulkCreate


@pytest.mark.asyncio
async def test_create_single_slot(test_session, test_doctor):
    """Test creating a single slot."""
    service = SlotService(test_session)

    slot_data = SlotCreate(
        start_time=datetime.now(UTC) + timedelta(days=1),
        end_time=datetime.now(UTC) + timedelta(days=1, minutes=30),
        duration_minutes=30,
    )

    slot = await service.create_slot(test_doctor.id, slot_data)

    assert slot.id is not None
    assert slot.doctor_id == test_doctor.id
    assert slot.status == SlotStatus.AVAILABLE.value
    assert slot.duration_minutes == 30


@pytest.mark.asyncio
async def test_create_bulk_slots(test_session, test_doctor):
    """Test creating bulk recurring slots."""
    service = SlotService(test_session)

    bulk_data = SlotBulkCreate(
        start_date=datetime.now(UTC) + timedelta(days=1),
        end_date=datetime.now(UTC) + timedelta(days=7),
        weekdays=[0, 1, 2, 3, 4],  # Monday-Friday
        start_times=["09:00", "10:00"],
        duration_minutes=30,
    )

    slots = await service.create_bulk_slots(test_doctor.id, bulk_data)

    assert len(slots) > 0
    # All slots should have same recurrence group
    recurrence_id = slots[0].recurrence_group_id
    assert all(s.recurrence_group_id == recurrence_id for s in slots)
    assert all(s.is_recurring for s in slots)


@pytest.mark.asyncio
async def test_get_slot_by_id(test_session, test_doctor):
    """Test getting slot by ID."""
    service = SlotService(test_session)

    # Create a slot
    slot = Slot(
        doctor_id=test_doctor.id,
        start_time=datetime.now(UTC) + timedelta(days=1),
        end_time=datetime.now(UTC) + timedelta(days=1, minutes=30),
        status=SlotStatus.AVAILABLE.value,
    )
    test_session.add(slot)
    await test_session.commit()

    # Find it
    found = await service.get_slot_by_id(slot.id)
    assert found is not None
    assert found.id == slot.id

    # Not found
    not_found = await service.get_slot_by_id("nonexistent-id")
    assert not_found is None


@pytest.mark.asyncio
async def test_mark_slot_booked(test_session, test_doctor):
    """Test marking slot as booked."""
    service = SlotService(test_session)

    slot = Slot(
        doctor_id=test_doctor.id,
        start_time=datetime.now(UTC) + timedelta(days=1),
        end_time=datetime.now(UTC) + timedelta(days=1, minutes=30),
        status=SlotStatus.AVAILABLE.value,
    )
    test_session.add(slot)
    await test_session.commit()

    booked = await service.mark_slot_booked(slot.id)
    assert booked.status == SlotStatus.BOOKED.value


@pytest.mark.asyncio
async def test_release_slot(test_session, test_doctor):
    """Test releasing a booked slot."""
    service = SlotService(test_session)

    slot = Slot(
        doctor_id=test_doctor.id,
        start_time=datetime.now(UTC) + timedelta(days=1),
        end_time=datetime.now(UTC) + timedelta(days=1, minutes=30),
        status=SlotStatus.BOOKED.value,
    )
    test_session.add(slot)
    await test_session.commit()

    released = await service.release_slot(slot.id)
    assert released.status == SlotStatus.AVAILABLE.value


@pytest.mark.asyncio
async def test_get_available_slots_for_patient(test_session, test_doctor, test_patient):
    """Test filtering available slots based on patient compliance."""
    service = SlotService(test_session)

    # Create regular slot
    regular_slot = Slot(
        doctor_id=test_doctor.id,
        start_time=datetime.now(UTC) + timedelta(days=1),
        end_time=datetime.now(UTC) + timedelta(days=1, minutes=30),
        status=SlotStatus.AVAILABLE.value,
    )

    # Create priority-only slot (requires GOLD or higher)
    priority_slot = Slot(
        doctor_id=test_doctor.id,
        start_time=datetime.now(UTC) + timedelta(days=2),
        end_time=datetime.now(UTC) + timedelta(days=2, minutes=30),
        status=SlotStatus.AVAILABLE.value,
        is_priority_only=True,
    )

    test_session.add_all([regular_slot, priority_slot])
    await test_session.commit()

    # Patient with SILVER compliance
    available = await service.get_available_slots_for_patient(
        test_doctor.id,
        test_patient,
        datetime.now(UTC),
        datetime.now(UTC) + timedelta(days=7),
    )

    # Silver patient should only see regular slots
    slot_ids = [s.id for s in available]
    assert regular_slot.id in slot_ids
    assert priority_slot.id not in slot_ids


@pytest.mark.asyncio
async def test_get_available_slots_gold_patient(test_session, test_doctor):
    """Test that GOLD patients can access priority slots."""
    service = SlotService(test_session)

    # Create patient with GOLD compliance
    gold_patient = Patient(
        email="gold@test.com",
        password_hash="hash",
        first_name="Gold",
        last_name="Patient",
        compliance_level=ComplianceLevel.GOLD.value,
    )
    test_session.add(gold_patient)

    # Create priority-only slot
    priority_slot = Slot(
        doctor_id=test_doctor.id,
        start_time=datetime.now(UTC) + timedelta(days=1),
        end_time=datetime.now(UTC) + timedelta(days=1, minutes=30),
        status=SlotStatus.AVAILABLE.value,
        is_priority_only=True,
    )
    test_session.add(priority_slot)
    await test_session.commit()

    available = await service.get_available_slots_for_patient(
        test_doctor.id,
        gold_patient,
        datetime.now(UTC),
        datetime.now(UTC) + timedelta(days=7),
    )

    assert len(available) == 1
    assert available[0].id == priority_slot.id


@pytest.mark.asyncio
async def test_block_slot(test_session, test_doctor):
    """Test blocking a slot."""
    service = SlotService(test_session)

    slot = Slot(
        doctor_id=test_doctor.id,
        start_time=datetime.now(UTC) + timedelta(days=1),
        end_time=datetime.now(UTC) + timedelta(days=1, minutes=30),
        status=SlotStatus.AVAILABLE.value,
    )
    test_session.add(slot)
    await test_session.commit()

    blocked = await service.block_slot(slot.id)
    assert blocked.status == SlotStatus.BLOCKED.value
