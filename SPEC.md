# PUAR-Patients: Patient Appointment Management System

## Overview
A patient appointment scheduling system with intelligent slot management, patient categorization, and compliance tracking.

## Core Features

### 1. Self-Booking System
- Doctor defines available time slots (calendar/slots)
- Patients see only slots permitted by system rules
- Self-booking into available slots

### 2. Patient Category → Visit Frequency
- Patient status/category determines visit frequency:
  - Monthly
  - Every 2 weeks
  - Every 6 months
  - etc.
- System calculates "when next visit should be available"
- Opens booking only within appropriate time range
- Prevents too-early/too-frequent bookings

### 3. Cancellation/Reschedule Logic
- Only allowed if free slots exist
- Requires triage questionnaire:
  - Reason assessment
  - Urgency evaluation
  - Commitment acknowledgment
  - Penalty logic
- Questionnaire results affect:
  - Permission to reschedule
  - Available date options
  - Doctor notification (if high risk)

### 4. Initial Compliance Questionnaire
- Patient self-assesses discipline (compliance)
- Confirms commitments (no-shows, cancellation notice, etc.)
- Results determine:
  - Prioritization for slot access
  - Trust level (higher = easier reschedules, fewer checks)

### 5. Prioritization Under Scarcity
- Rank patients by: status, compliance, urgency, cancellation history, wait time, triage
- Reserve slots for: urgent cases, returns after cancellations

## Tech Stack
- Frontend: React/Next.js
- Backend: Python FastAPI
- Database: PostgreSQL
- Deployment: AWS (Lambda/ECS + RDS)

## Assumptions (to be validated)
1. Single doctor practice initially (multi-doctor later)
2. Hebrew + Russian language support
3. Email/SMS notifications
4. No payment integration in MVP
5. GDPR-compliant data handling

## Success Criteria
- [ ] Doctor can define available slots
- [ ] Patient can register with compliance questionnaire
- [ ] Patient can book within their allowed frequency
- [ ] Reschedule requires triage flow
- [ ] Prioritization works under slot scarcity
- [ ] All tests green
- [ ] Deployed to AWS


## Future: Productization (TODO)

### Backup/Restore
- Automated database backups (daily)
- Point-in-time recovery
- Export/import patient data
- GDPR-compliant data export

### Stress Testing
- Load testing with k6 or Locust
- Concurrent booking simulation
- API rate limiting validation
- Database connection pool testing
- Target: 100+ concurrent users

## Success Criteria (CONSTITUTION)

**Tasks are NOT done until:**
1. ✅ Deployed to AWS (public URL)
2. ✅ URL sent to Alex
3. ✅ Tests run against PUBLIC URL (not just internal)
4. ✅ Accessible for outside beta-testers

**Deployment Requirements:**
- Public HTTPS URL
- E2E tests run against deployed URL
- No "localhost" testing counts as complete
- Beta testers can access without VPN/internal network

**Definition of Done:**
- [ ] AWS deployment live
- [ ] Public URL provided
- [ ] E2E tests pass on public URL
- [ ] Alex confirms access works
