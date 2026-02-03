# Feature Specification: Cancellation/Reschedule Logic

## Overview
Patients can cancel or reschedule appointments after completing a triage questionnaire that assesses the reason and urgency.

## User Stories

### US-3.1: Request Cancellation
**As a** patient
**I want to** cancel my appointment when necessary
**So that** the slot can be made available to others

**Acceptance Criteria:**
- Patient must complete triage questionnaire first
- Questionnaire assesses reason and urgency
- Auto-approved for routine cancellations
- Doctor notified for urgent/high-risk cases
- Late cancellations (< 24h) affect compliance score

### US-3.2: Request Reschedule
**As a** patient
**I want to** reschedule my appointment to a new time
**So that** I can maintain my healthcare continuity

**Acceptance Criteria:**
- Only allowed if free slots exist
- Must complete triage questionnaire
- Can select new slot after approval
- Old booking marked as rescheduled
- New booking linked to original

### US-3.3: Triage Assessment
**As a** doctor
**I want** the system to assess cancellation requests
**So that** I can focus on patients with health changes

**Acceptance Criteria:**
- Questionnaire captures: reason, symptoms, availability
- Calculates urgency level (emergency, urgent, moderate, routine)
- Auto-approves routine requests
- Flags urgent cases for doctor review
- Records patient acknowledgments

## Technical Specifications

### Triage Questionnaire Fields
- request_type: cancel | reschedule
- reason_category: work | health | family | transport | other
- condition_changed: boolean
- symptoms_worsened: boolean
- new_symptoms: boolean
- available_within_week: boolean
- acknowledges_impact: boolean
- commits_to_new_appointment: boolean

### Urgency Calculation
- symptoms_worsened OR new_symptoms → URGENT (requires review)
- condition_changed → MODERATE (requires review)
- else → ROUTINE (auto-approve)

### API Endpoints
- `POST /api/v1/bookings/{id}/triage` - Submit triage questionnaire
- `POST /api/v1/bookings/{id}/cancel` - Cancel booking (after approval)
- `POST /api/v1/bookings/{id}/reschedule` - Reschedule booking

### Business Rules
1. Cannot cancel/reschedule completed appointments
2. Late cancellations recorded in patient history
3. Multiple cancellations affect compliance score
4. Reschedule requires available alternative slot
5. Doctor can override auto-approval decisions
