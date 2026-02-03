# Feature Specification: Visit Frequency Rules

## Overview
The system determines when patients can book appointments based on their medical category and visit frequency requirements.

## User Stories

### US-2.1: Category-Based Frequency
**As a** doctor
**I want to** assign patients to medical categories
**So that** the system enforces appropriate visit frequencies

**Acceptance Criteria:**
- Patients have a medical category (critical, high_risk, moderate, stable, maintenance, healthy)
- Each category maps to a visit frequency
- Frequency determines minimum days between appointments

### US-2.2: Booking Window Calculation
**As a** patient
**I want to** know when I can next book
**So that** I plan my healthcare visits appropriately

**Acceptance Criteria:**
- System calculates earliest possible booking date
- Based on last completed appointment + frequency interval
- Shows latest date based on doctor's booking window
- Prevents too-early bookings

### US-2.3: First-Time Booking
**As a** new patient
**I want to** book my first appointment immediately
**So that** I can establish care with my doctor

**Acceptance Criteria:**
- New patients (no previous appointments) can book immediately
- Booking window starts from today
- Still respects doctor's booking window limit

## Technical Specifications

### Category-Frequency Mapping
| Category    | Frequency   | Days |
|-------------|-------------|------|
| Critical    | Weekly      | 7    |
| High Risk   | Biweekly    | 14   |
| Moderate    | Monthly     | 30   |
| Stable      | Quarterly   | 90   |
| Maintenance | Biannual    | 180  |
| Healthy     | Annual      | 365  |

### API Endpoints
- `GET /api/v1/patients/me/next-booking-window` - Get booking window

### Business Rules
1. Earliest date = last_appointment_date + frequency_days
2. If earliest < today, earliest = today
3. Latest date = today + doctor.booking_window_days
4. Can book if: earliest <= slot_date <= latest
5. Cannot book if: has_active_booking = true
