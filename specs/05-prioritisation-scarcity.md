# Feature Specification: Prioritisation Under Slot Scarcity

## Overview
When appointment slots become scarce, the system prioritises patients based on medical urgency, compliance history, and time since last visit to ensure the most critical patients receive care first.

## User Stories

### US-5.1: Fair Slot Allocation
**As a** clinic administrator
**I want** the system to fairly allocate scarce slots
**So that** critical patients are not left without care

**Acceptance Criteria:**
- Automatic prioritisation when slots < 30% capacity
- Medical category weighted highest
- Compliance history considered
- Time since last visit factored in
- Transparent priority scoring

### US-5.2: Priority Notification
**As a** high-priority patient
**I want to** be notified when priority slots become available
**So that** I can book critical appointments

**Acceptance Criteria:**
- Push notification for priority slots
- 24-hour booking window for priority patients
- Clear indication of priority status
- Option to decline and release slot

### US-5.3: Scarcity Dashboard
**As a** doctor
**I want to** see slot utilisation and scarcity metrics
**So that** I can adjust my availability accordingly

**Acceptance Criteria:**
- Real-time slot availability display
- Scarcity alerts and trends
- Patient waiting list visibility
- Ability to add emergency slots

## Technical Specifications

### Priority Score Calculation
```
priority_score = (
    medical_category_weight * 0.40 +
    compliance_score * 0.25 +
    urgency_factor * 0.20 +
    wait_time_factor * 0.15
)

Medical Category Weights:
- CRITICAL: 100
- HIGH_RISK: 80
- MODERATE: 60
- STABLE: 40
- MAINTENANCE: 20
- HEALTHY: 10

Urgency Factor:
- days_overdue / expected_frequency * 100 (capped at 100)

Wait Time Factor:
- days_since_last_visit / 365 * 100 (capped at 100)
```

### Scarcity Thresholds
| Level | Available Slots | Action |
|-------|----------------|--------|
| Normal | > 50% | Standard booking |
| Moderate | 30-50% | Priority patients first |
| High | 10-30% | Critical/High-Risk only |
| Critical | < 10% | Emergency only |

### Slot Reservation Rules
1. Reserve 20% of slots for CRITICAL patients
2. Reserve 15% for HIGH_RISK patients
3. Remaining 65% available to all
4. Priority slots release 48h before if unclaimed

### API Endpoints
- `GET /api/v1/slots/availability-status` - Get scarcity level
- `GET /api/v1/patients/priority-ranking` - Get patient priority list
- `POST /api/v1/slots/{id}/reserve-priority` - Reserve priority slot
- `GET /api/v1/doctors/{id}/scarcity-metrics` - Get scarcity dashboard data

### Business Rules
1. Priority scoring recalculated daily
2. Patients notified of priority changes
3. Doctor can override priority decisions
4. Audit log for all priority allocations
5. Monthly review of scarcity patterns
6. Emergency slots bypass all rules
