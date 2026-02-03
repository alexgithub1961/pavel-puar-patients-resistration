"""Integration tests for API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test health check endpoint."""
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_ready_endpoint(client):
    """Test readiness endpoint."""
    response = await client.get("/api/v1/ready")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


@pytest.mark.asyncio
async def test_patient_registration(client):
    """Test patient registration flow."""
    response = await client.post(
        "/api/v1/auth/patients/register",
        json={
            "email": "newpatient@test.com",
            "password": "testpassword123",
            "first_name": "New",
            "last_name": "Patient",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newpatient@test.com"
    assert data["first_name"] == "New"
    assert "id" in data


@pytest.mark.asyncio
async def test_patient_registration_duplicate_email(client):
    """Test patient registration with duplicate email."""
    # First registration
    await client.post(
        "/api/v1/auth/patients/register",
        json={
            "email": "duplicate@test.com",
            "password": "testpassword123",
            "first_name": "First",
            "last_name": "Patient",
        },
    )

    # Duplicate registration
    response = await client.post(
        "/api/v1/auth/patients/register",
        json={
            "email": "duplicate@test.com",
            "password": "testpassword123",
            "first_name": "Second",
            "last_name": "Patient",
        },
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_patient_login(client, test_patient):
    """Test patient login."""
    response = await client.post(
        "/api/v1/auth/patients/login",
        json={
            "email": "patient@test.com",
            "password": "testpassword123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_patient_login_wrong_password(client, test_patient):
    """Test patient login with wrong password."""
    response = await client.post(
        "/api/v1/auth/patients/login",
        json={
            "email": "patient@test.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_patient(client, patient_auth_headers):
    """Test getting current patient profile."""
    response = await client.get(
        "/api/v1/patients/me",
        headers=patient_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "patient@test.com"
    assert "compliance_score" in data
    assert "category" in data


@pytest.mark.asyncio
async def test_get_patient_booking_window(client, patient_auth_headers):
    """Test getting patient booking window."""
    response = await client.get(
        "/api/v1/patients/me/next-booking-window",
        headers=patient_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "can_book" in data
    assert "earliest_date" in data
    assert "visit_frequency_days" in data


@pytest.mark.asyncio
async def test_doctor_registration(client):
    """Test doctor registration."""
    response = await client.post(
        "/api/v1/auth/doctors/register",
        json={
            "email": "newdoctor@test.com",
            "password": "testpassword123",
            "first_name": "New",
            "last_name": "Doctor",
            "specialisation": "Cardiology",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newdoctor@test.com"
    assert data["specialisation"] == "Cardiology"


@pytest.mark.asyncio
async def test_doctor_login(client, test_doctor):
    """Test doctor login."""
    response = await client.post(
        "/api/v1/auth/doctors/login",
        json={
            "email": "doctor@test.com",
            "password": "testpassword123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_get_current_doctor(client, doctor_auth_headers):
    """Test getting current doctor profile."""
    response = await client.get(
        "/api/v1/doctors/me",
        headers=doctor_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "doctor@test.com"
    assert "default_slot_duration_minutes" in data


@pytest.mark.asyncio
async def test_protected_endpoint_without_auth(client):
    """Test that protected endpoints require authentication."""
    response = await client.get("/api/v1/patients/me")
    assert response.status_code == 401  # 401 Unauthorized for missing auth


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test root endpoint."""
    response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data
