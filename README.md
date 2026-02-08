# PUAR-Patients v1.0

Patient Appointment Management System with intelligent scheduling, compliance tracking, and prioritisation.

## Features

- **Self-Booking System**: Patients book appointments within doctor-defined slots
- **Visit Frequency Rules**: Patient category determines required visit frequency
- **Cancellation/Reschedule Logic**: Triage questionnaire for change requests
- **Compliance Tracking**: Initial questionnaire and ongoing compliance scoring
- **Prioritisation Under Scarcity**: Fair slot allocation based on medical urgency

## Tech Stack

### Backend
- FastAPI with async support
- SQLAlchemy 2.0 with asyncpg
- PostgreSQL database
- JWT authentication
- Pydantic v2 validation

### Frontend
- React 18 with TypeScript
- Vite build tool
- Tailwind CSS
- Zustand state management
- React Query for API calls

### Infrastructure
- Docker & Docker Compose
- AWS App Runner (API)
- AWS S3 + CloudFront (Frontend PWAs)
- AWS RDS PostgreSQL
- AWS Secrets Manager
- Redis for caching

## Production URLs

| Service | URL |
|---------|-----|
| **Patient PWA** | https://d2wowd7dw25och.cloudfront.net |
| **Doctor PWA** | https://d24gl9ln0vt8cq.cloudfront.net |
| **API** | https://nmpjiqngaz.us-east-1.awsapprunner.com |
| **API Docs** | https://nmpjiqngaz.us-east-1.awsapprunner.com/docs |

## AWS Deployment

### Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  Patient PWA    │     │   Doctor PWA    │
│  (CloudFront)   │     │  (CloudFront)   │
└────────┬────────┘     └────────┬────────┘
         │                       │
         │    ┌──────────────┐   │
         └────►  S3 Buckets  ◄───┘
              └──────────────┘
                     
┌─────────────────────────────────────────┐
│            AWS App Runner               │
│         (FastAPI Backend)               │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┴────────────┐
    ▼                         ▼
┌────────────┐        ┌───────────────┐
│ RDS Postgres│        │Secrets Manager│
│  (db.t3.micro)      │ (DB + JWT)    │
└────────────┘        └───────────────┘
```

### Deployment Scripts

| Script | Purpose |
|--------|---------|
| `scripts/aws/deploy.sh` | Full stack deploy (RDS, ECR, App Runner, S3, CloudFront) |
| `scripts/deploy_frontends.sh` | Frontend-only redeploy with cache invalidation |

### Full Deployment

```bash
# Set AWS profile
export AWS_PROFILE=aptus

# Deploy entire stack
./scripts/aws/deploy.sh
```

This creates:
- RDS PostgreSQL instance
- ECR repository + Docker image
- App Runner service
- S3 buckets for both PWAs
- CloudFront distributions (HTTPS)
- Secrets in AWS Secrets Manager

### Frontend-Only Deployment

```bash
# Redeploy frontends after changes
./scripts/deploy_frontends.sh
```

### AWS Resources

- **Region:** us-east-1
- **Account:** 860599907983
- **RDS Host:** puar-patients-db.c4pohmvgvnit.us-east-1.rds.amazonaws.com
- **ECR Repo:** 860599907983.dkr.ecr.us-east-1.amazonaws.com/puar-patients

## Quick Start

```bash
# Clone repository
git clone <repository-url>
cd puar-patients

# Start with Docker Compose
docker-compose up -d

# Access applications
# Patient PWA: http://localhost:3000
# Doctor PWA: http://localhost:3001
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Development

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Start development server
uvicorn src.main:app --reload
```

## Project Structure

```
puar-patients/
├── src/
│   ├── api/           # FastAPI routes
│   ├── core/          # Configuration, security, database
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── i18n/          # Translations (EN/HE/RU)
├── frontend/
│   ├── patient/       # Patient PWA
│   └── doctor/        # Doctor PWA
├── tests/             # pytest tests
├── specs/             # Feature specifications
└── scripts/           # Deployment scripts
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Internationalisation

Supports English, Hebrew, and Russian for both backend messages and frontend UI.

## Licence

Private - All rights reserved
