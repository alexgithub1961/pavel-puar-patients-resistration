# PUAR-Patients

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
- AWS ECS/Fargate deployment
- Redis for caching

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
