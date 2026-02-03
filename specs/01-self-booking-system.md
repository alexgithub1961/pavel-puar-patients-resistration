# Feature Specification: Self-Booking System

## Overview
Patients can view available appointment slots and book appointments themselves based on system-defined rules and their eligibility.

## User Stories

### US-1.1: View Available Slots
**As a** patient
**I want to** see available appointment slots
**So that** I can choose a convenient time for my appointment

**Acceptance Criteria:**
- Patient sees only slots within their allowed booking window
- Slots are filtered based on patient's compliance level
- Past slots are not shown
- Booked/blocked slots are not shown
- Slots show date, time, duration, and doctor name

### US-1.2: Book an Appointment
**As a** patient
**I want to** book an available slot
**So that** I have a confirmed appointment with my doctor

**Acceptance Criteria:**
- Patient can select an available slot
- Patient can provide a reason for visit (optional)
- Booking is confirmed immediately
- Patient receives confirmation message
- Slot is marked as booked (no double-booking)

### US-1.3: View My Bookings
**As a** patient
**I want to** see my upcoming and past appointments
**So that** I can manage my healthcare schedule

**Acceptance Criteria:**
- Shows list of all bookings
- Separates upcoming and past appointments
- Shows date, time, status, and doctor for each
- Allows navigation to booking details

## Technical Specifications

### API Endpoints
- `GET /api/v1/slots/available` - Get available slots for patient
- `POST /api/v1/bookings` - Create a new booking
- `GET /api/v1/bookings` - List patient's bookings
- `GET /api/v1/bookings/{id}` - Get booking details

### Data Models
- **Slot**: id, doctor_id, start_time, end_time, status, restrictions
- **Booking**: id, patient_id, slot_id, status, reason, timestamps

### Business Rules
1. Patient must be authenticated
2. Patient must have completed compliance questionnaire
3. Slot must be within patient's booking window
4. Slot must match patient's compliance restrictions
5. Patient cannot have more than one active booking
