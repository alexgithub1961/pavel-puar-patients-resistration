# Feature Specification: Initial Compliance Questionnaire

## Overview
New patients complete an initial compliance questionnaire that establishes their baseline compliance level and helps set expectations for the patient-doctor relationship.

## User Stories

### US-4.1: Complete Initial Questionnaire
**As a** new patient
**I want to** complete an initial compliance questionnaire
**So that** my doctor understands my health commitment level

**Acceptance Criteria:**
- Questionnaire presented after registration
- Covers key health commitment areas
- Results determine initial compliance level
- Cannot book until questionnaire completed
- Results visible to doctor

### US-4.2: Review Patient Compliance
**As a** doctor
**I want to** see patient compliance questionnaire results
**So that** I can tailor my approach to each patient

**Acceptance Criteria:**
- View questionnaire responses
- See calculated compliance level
- View compliance history over time
- Can add notes to patient profile
- Alerts for significant compliance changes

## Technical Specifications

### Questionnaire Fields
- medication_adherence: 1-5 scale
- appointment_attendance: 1-5 scale
- lifestyle_commitment: 1-5 scale
- communication_responsiveness: 1-5 scale
- treatment_plan_adherence: 1-5 scale
- health_monitoring_frequency: 1-5 scale
- preventive_care_engagement: 1-5 scale
- chronic_condition_management: 1-5 scale (if applicable)

### Compliance Commitments (Boolean)
- commit_to_appointments: boolean
- commit_to_medication: boolean
- commit_to_communication: boolean
- commit_to_monitoring: boolean
- acknowledge_cancellation_policy: boolean

### Compliance Level Calculation
```
rating_score = average(all 1-5 ratings) / 5 * 100
commitment_score = count(true commitments) / total_commitments * 100

final_score = (rating_score * 0.6) + (commitment_score * 0.4)

Levels:
- PLATINUM: score >= 90
- GOLD: score >= 75
- SILVER: score >= 60
- BRONZE: score >= 40
- PROBATION: score < 40
```

### Compliance Level Benefits
| Level | Booking Window | Priority Access | Late Cancel Tolerance |
|-------|---------------|-----------------|----------------------|
| PLATINUM | 90 days | Yes | 3 per year |
| GOLD | 60 days | Yes | 2 per year |
| SILVER | 45 days | No | 1 per year |
| BRONZE | 30 days | No | 0 |
| PROBATION | 14 days | No | 0 |

### API Endpoints
- `POST /api/v1/patients/{id}/compliance-questionnaire` - Submit questionnaire
- `GET /api/v1/patients/{id}/compliance-questionnaire` - Get questionnaire results
- `GET /api/v1/patients/{id}/compliance-history` - Get compliance history

### Business Rules
1. Questionnaire required within 7 days of registration
2. Can retake questionnaire every 6 months
3. Compliance level affects available booking slots
4. Doctor can manually adjust compliance level
5. Compliance score updated after each visit
