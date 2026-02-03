"""Pytest fixtures and configuration."""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.database import Base, get_db
from src.core.security import get_password_hash
from src.main import app
from src.models.doctor import Doctor
from src.models.patient import Patient

# Test database URL (SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with overridden database dependency."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sync_client(test_session: AsyncSession) -> TestClient:
    """Create a sync test client for simple tests."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_doctor(test_session: AsyncSession) -> Doctor:
    """Create a test doctor."""
    doctor = Doctor(
        email="doctor@test.com",
        password_hash=get_password_hash("testpassword123"),
        first_name="Test",
        last_name="Doctor",
        specialisation="General Practice",
        default_slot_duration_minutes=30,
        booking_window_days=30,
        max_daily_appointments=20,
    )
    test_session.add(doctor)
    await test_session.commit()
    await test_session.refresh(doctor)
    return doctor


@pytest_asyncio.fixture
async def test_patient(test_session: AsyncSession) -> Patient:
    """Create a test patient."""
    patient = Patient(
        email="patient@test.com",
        password_hash=get_password_hash("testpassword123"),
        first_name="Test",
        last_name="Patient",
        category="stable",
        compliance_level="silver",
        compliance_score=50,
    )
    test_session.add(patient)
    await test_session.commit()
    await test_session.refresh(patient)
    return patient


@pytest_asyncio.fixture
async def doctor_auth_headers(client: AsyncClient, test_doctor: Doctor) -> dict[str, str]:
    """Get authentication headers for test doctor."""
    response = await client.post(
        "/api/v1/auth/doctors/login",
        json={"email": "doctor@test.com", "password": "testpassword123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def patient_auth_headers(client: AsyncClient, test_patient: Patient) -> dict[str, str]:
    """Get authentication headers for test patient."""
    response = await client.post(
        "/api/v1/auth/patients/login",
        json={"email": "patient@test.com", "password": "testpassword123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
