"""E2E test configuration and fixtures."""

import os
import re
import pytest
from playwright.sync_api import Page, BrowserContext

# Base URLs for the PWAs
PATIENT_PWA_URL = os.getenv("PATIENT_PWA_URL", "http://localhost:3000")
DOCTOR_PWA_URL = os.getenv("DOCTOR_PWA_URL", "http://localhost:3001")
API_URL = os.getenv("API_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for all tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture
def patient_page(page: Page) -> Page:
    """Fixture providing a page navigated to Patient PWA."""
    page.goto(PATIENT_PWA_URL)
    return page


@pytest.fixture
def doctor_page(context: BrowserContext) -> Page:
    """Fixture providing a new page navigated to Doctor PWA."""
    page = context.new_page()
    page.goto(DOCTOR_PWA_URL)
    return page


@pytest.fixture
def test_patient_credentials():
    """Test patient credentials."""
    import uuid
    unique_id = uuid.uuid4().hex[:8]
    return {
        "email": f"test.patient.{unique_id}@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "Patient",
    }


@pytest.fixture
def test_doctor_credentials():
    """Test doctor credentials."""
    import uuid
    unique_id = uuid.uuid4().hex[:8]
    return {
        "email": f"test.doctor.{unique_id}@example.com",
        "password": "TestPassword123!",
        "first_name": "Dr. Test",
        "last_name": "Doctor",
        "specialisation": "General Practice",
        "licence_number": f"LIC-{unique_id}",
    }


@pytest.fixture
def api_register_patient(test_patient_credentials):
    """Register a patient via API and return credentials."""
    import httpx

    response = httpx.post(
        f"{API_URL}/api/v1/auth/patients/register",
        json={
            "email": test_patient_credentials["email"],
            "password": test_patient_credentials["password"],
            "first_name": test_patient_credentials["first_name"],
            "last_name": test_patient_credentials["last_name"],
        },
    )

    if response.status_code == 200:
        return test_patient_credentials
    elif response.status_code == 400 and "already registered" in response.text:
        return test_patient_credentials
    else:
        raise Exception(f"Failed to register patient: {response.text}")


@pytest.fixture
def api_register_doctor(test_doctor_credentials):
    """Register a doctor via API and return credentials."""
    import httpx

    response = httpx.post(
        f"{API_URL}/api/v1/auth/doctors/register",
        json={
            "email": test_doctor_credentials["email"],
            "password": test_doctor_credentials["password"],
            "first_name": test_doctor_credentials["first_name"],
            "last_name": test_doctor_credentials["last_name"],
            "specialisation": test_doctor_credentials["specialisation"],
            "licence_number": test_doctor_credentials["licence_number"],
        },
    )

    if response.status_code == 200:
        return test_doctor_credentials
    elif response.status_code == 400 and "already registered" in response.text:
        return test_doctor_credentials
    else:
        raise Exception(f"Failed to register doctor: {response.text}")


@pytest.fixture
def logged_in_patient_page(patient_page: Page, api_register_patient) -> Page:
    """Fixture providing a logged-in patient page."""
    creds = api_register_patient

    # Navigate to login page if not already there
    if "/login" not in patient_page.url:
        patient_page.goto(f"{PATIENT_PWA_URL}/login")

    # Fill login form
    patient_page.fill('input[type="email"]', creds["email"])
    patient_page.fill('input[type="password"]', creds["password"])
    patient_page.click('button[type="submit"]')

    # Wait for navigation to dashboard
    patient_page.wait_for_url(re.compile(r".*/dashboard.*"), timeout=10000)

    return patient_page


@pytest.fixture
def logged_in_doctor_page(doctor_page: Page, api_register_doctor) -> Page:
    """Fixture providing a logged-in doctor page."""
    creds = api_register_doctor

    # Navigate to login page if not already there
    if "/login" not in doctor_page.url:
        doctor_page.goto(f"{DOCTOR_PWA_URL}/login")

    # Fill login form
    doctor_page.fill('input[type="email"]', creds["email"])
    doctor_page.fill('input[type="password"]', creds["password"])
    doctor_page.click('button[type="submit"]')

    # Wait for navigation to dashboard
    doctor_page.wait_for_url(re.compile(r".*/dashboard.*"), timeout=10000)

    return doctor_page
