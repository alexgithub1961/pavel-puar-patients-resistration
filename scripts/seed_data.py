"""Seed database with mock data including demo accounts."""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from src.core.database import AsyncSessionLocal
from src.core.security import get_password_hash
from src.models.doctor import Doctor
from src.models.patient import Patient, PatientCategory, ComplianceLevel
from src.models.slot import Slot, SlotStatus
from src.models.booking import Booking, BookingStatus

# Demo account credentials - these are PUBLIC for demo purposes
# Using example.com domain as it's a reserved domain that passes email validation
DEMO_ACCOUNTS = {
    "doctor": {
        "id": "00000000-0000-0000-0000-000000000001",
        "email": "demo.doctor@example.com",
        "password": "demo1234",
        "first_name": "Demo",
        "last_name": "Doctor",
    },
    "new_patient": {
        "id": "00000000-0000-0000-0000-000000000010",
        "email": "demo.new@example.com",
        "password": "demo1234",
        "first_name": "New",
        "last_name": "Patient",
    },
    "regular_patient": {
        "id": "00000000-0000-0000-0000-000000000020",
        "email": "demo.regular@example.com",
        "password": "demo1234",
        "first_name": "Regular",
        "last_name": "Patient",
    },
}


async def seed_data():
    """Seed database with mock data including demo accounts."""
    async with AsyncSessionLocal() as session:
        # === DEMO ACCOUNTS ===
        print("\n📌 Creating DEMO accounts...")

        # Check if demo doctor already exists
        existing_doctor = await session.execute(
            select(Doctor).where(Doctor.id == DEMO_ACCOUNTS["doctor"]["id"])
        )
        existing_doctor = existing_doctor.scalar_one_or_none()

        if existing_doctor:
            demo_doctor = existing_doctor
            print(f"  ✓ Demo Doctor already exists: {demo_doctor.email}")
        else:
            demo_doctor = Doctor(
                id=DEMO_ACCOUNTS["doctor"]["id"],
                email=DEMO_ACCOUNTS["doctor"]["email"],
                password_hash=get_password_hash(DEMO_ACCOUNTS["doctor"]["password"]),
                first_name=DEMO_ACCOUNTS["doctor"]["first_name"],
                last_name=DEMO_ACCOUNTS["doctor"]["last_name"],
                phone="+972500000001",
                specialisation="Psychiatry",
                is_active=True,
            )
            session.add(demo_doctor)
            await session.flush()
            print(f"  ✓ Demo Doctor: {demo_doctor.email} / {DEMO_ACCOUNTS['doctor']['password']}")

        # Check if demo new patient already exists
        existing_new_patient = await session.execute(
            select(Patient).where(Patient.id == DEMO_ACCOUNTS["new_patient"]["id"])
        )
        existing_new_patient = existing_new_patient.scalar_one_or_none()

        if existing_new_patient:
            demo_new_patient = existing_new_patient
            print(f"  ✓ Demo New Patient already exists: {demo_new_patient.email}")
        else:
            demo_new_patient = Patient(
                id=DEMO_ACCOUNTS["new_patient"]["id"],
                email=DEMO_ACCOUNTS["new_patient"]["email"],
                password_hash=get_password_hash(DEMO_ACCOUNTS["new_patient"]["password"]),
                first_name=DEMO_ACCOUNTS["new_patient"]["first_name"],
                last_name=DEMO_ACCOUNTS["new_patient"]["last_name"],
                phone="+972500000010",
                category=PatientCategory.STABLE.value,
                compliance_level=ComplianceLevel.SILVER.value,
                compliance_score=50,
                is_active=True,
            )
            session.add(demo_new_patient)
            print(f"  ✓ Demo New Patient: {demo_new_patient.email} / {DEMO_ACCOUNTS['new_patient']['password']}")

        # Check if demo regular patient already exists
        existing_regular_patient = await session.execute(
            select(Patient).where(Patient.id == DEMO_ACCOUNTS["regular_patient"]["id"])
        )
        existing_regular_patient = existing_regular_patient.scalar_one_or_none()

        if existing_regular_patient:
            demo_regular_patient = existing_regular_patient
            print(f"  ✓ Demo Regular Patient already exists: {demo_regular_patient.email}")
        else:
            demo_regular_patient = Patient(
                id=DEMO_ACCOUNTS["regular_patient"]["id"],
                email=DEMO_ACCOUNTS["regular_patient"]["email"],
                password_hash=get_password_hash(DEMO_ACCOUNTS["regular_patient"]["password"]),
                first_name=DEMO_ACCOUNTS["regular_patient"]["first_name"],
                last_name=DEMO_ACCOUNTS["regular_patient"]["last_name"],
                phone="+972500000020",
                category=PatientCategory.MODERATE.value,
                compliance_level=ComplianceLevel.GOLD.value,
                compliance_score=85,
                total_appointments=8,
                no_shows=0,
                late_cancellations=1,
                is_active=True,
            )
            session.add(demo_regular_patient)
            print(f"  ✓ Demo Regular Patient: {demo_regular_patient.email} / {DEMO_ACCOUNTS['regular_patient']['password']}")

        await session.flush()

        # === ADDITIONAL TEST ACCOUNTS ===
        print("\n📋 Creating additional test accounts...")

        test_patients_data = [
            ("patient1@test.local", "Alex", "Patient", PatientCategory.STABLE, ComplianceLevel.GOLD),
            ("patient2@test.local", "Boris", "Testov", PatientCategory.MODERATE, ComplianceLevel.SILVER),
            ("patient3@test.local", "Clara", "Demo", PatientCategory.HIGH_RISK, ComplianceLevel.PLATINUM),
        ]

        test_patients = []
        for email, first_name, last_name, category, compliance in test_patients_data:
            # Check if test patient already exists
            existing_test = await session.execute(
                select(Patient).where(Patient.email == email)
            )
            existing_test = existing_test.scalar_one_or_none()

            if existing_test:
                test_patients.append(existing_test)
                print(f"  ✓ Test patient already exists: {email}")
            else:
                patient = Patient(
                    id=str(uuid4()),
                    email=email,
                    password_hash=get_password_hash("patient123"),
                    first_name=first_name,
                    last_name=last_name,
                    phone="+972500000000",
                    category=category.value,
                    compliance_level=compliance.value,
                    compliance_score=70,
                    is_active=True,
                )
                session.add(patient)
                test_patients.append(patient)
                print(f"  ✓ Test patient: {email} / patient123")

        await session.flush()

        # === SLOTS AND BOOKINGS ===
        print("\n📅 Creating slots and bookings...")

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        slot_times = [9, 10, 11, 14, 15, 16]
        slots_created = 0
        bookings_created = 0

        # Create past slots with completed bookings for demo regular patient
        print("  Creating past appointment history for demo regular patient...")
        past_booking_reasons = [
            "Initial consultation",
            "Follow-up visit",
            "Medication review",
            "Progress check",
            "Monthly check-in",
            "Routine follow-up",
            "Therapy session",
            "Assessment review",
        ]

        for week_offset in range(1, 9):
            day = now - timedelta(weeks=week_offset)
            # Israel: Friday (4) and Saturday (5) are off
            while day.weekday() in (4, 5):
                day -= timedelta(days=1)

            hour = slot_times[week_offset % len(slot_times)]
            start_time = day.replace(hour=hour, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(minutes=50)

            past_slot = Slot(
                id=str(uuid4()),
                doctor_id=demo_doctor.id,
                start_time=start_time,
                end_time=end_time,
                duration_minutes=50,
                status=SlotStatus.BOOKED.value,
            )
            session.add(past_slot)
            await session.flush()

            past_booking = Booking(
                id=str(uuid4()),
                patient_id=demo_regular_patient.id,
                slot_id=past_slot.id,
                status=BookingStatus.COMPLETED.value,
                reason=past_booking_reasons[week_offset - 1],
            )
            session.add(past_booking)
            bookings_created += 1
            slots_created += 1

        # Create future slots for next 2 weeks
        print("  Creating future available slots...")

        for day_offset in range(1, 15):
            day = now + timedelta(days=day_offset)
            # Israel: Friday (4) and Saturday (5) are off
            if day.weekday() in (4, 5):
                continue

            for hour in slot_times:
                start_time = day.replace(hour=hour, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(minutes=50)

                is_booked = (slots_created % 3) == 0 and slots_created > 0

                slot = Slot(
                    id=str(uuid4()),
                    doctor_id=demo_doctor.id,
                    start_time=start_time,
                    end_time=end_time,
                    duration_minutes=50,
                    status=SlotStatus.BOOKED.value if is_booked else SlotStatus.AVAILABLE.value,
                )
                session.add(slot)
                await session.flush()
                slots_created += 1

                if is_booked and test_patients:
                    patient = test_patients[bookings_created % len(test_patients)]
                    booking = Booking(
                        id=str(uuid4()),
                        patient_id=patient.id,
                        slot_id=slot.id,
                        status=BookingStatus.CONFIRMED.value,
                        reason="Regular checkup",
                    )
                    session.add(booking)
                    bookings_created += 1

        # Create one upcoming booking for demo regular patient
        print("  Creating upcoming appointment for demo regular patient...")
        for day_offset in range(3, 10):
            day = now + timedelta(days=day_offset)
            # Israel: work days are Sun-Thu (not Fri/Sat)
            if day.weekday() not in (4, 5):
                start_time = day.replace(hour=10, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(minutes=50)

                upcoming_slot = Slot(
                    id=str(uuid4()),
                    doctor_id=demo_doctor.id,
                    start_time=start_time,
                    end_time=end_time,
                    duration_minutes=50,
                    status=SlotStatus.BOOKED.value,
                )
                session.add(upcoming_slot)
                await session.flush()

                upcoming_booking = Booking(
                    id=str(uuid4()),
                    patient_id=demo_regular_patient.id,
                    slot_id=upcoming_slot.id,
                    status=BookingStatus.CONFIRMED.value,
                    reason="Monthly follow-up",
                )
                session.add(upcoming_booking)
                slots_created += 1
                bookings_created += 1
                break

        await session.commit()

        print(f"\n✅ Seed data created successfully!")
        print(f"   - {slots_created} slots ({bookings_created} booked)")

        print("\n" + "=" * 60)
        print("🎭 DEMO CREDENTIALS (for demonstration purposes):")
        print("=" * 60)
        print(f"\n👨‍⚕️ Doctor Portal:")
        print(f"   Email:    {DEMO_ACCOUNTS['doctor']['email']}")
        print(f"   Password: {DEMO_ACCOUNTS['doctor']['password']}")
        print(f"\n👤 Patient App - New Patient (no appointments):")
        print(f"   Email:    {DEMO_ACCOUNTS['new_patient']['email']}")
        print(f"   Password: {DEMO_ACCOUNTS['new_patient']['password']}")
        print(f"\n👤 Patient App - Regular Patient (with history):")
        print(f"   Email:    {DEMO_ACCOUNTS['regular_patient']['email']}")
        print(f"   Password: {DEMO_ACCOUNTS['regular_patient']['password']}")
        print("\n" + "=" * 60)
        print("\n📋 Additional test accounts:")
        print("   patient1@test.local / patient123")
        print("   patient2@test.local / patient123")
        print("   patient3@test.local / patient123")


if __name__ == "__main__":
    asyncio.run(seed_data())
