"""E2E tests for Doctor PWA - login, slot management, patient view."""

import re
import pytest
from playwright.sync_api import Page, expect

from tests.e2e.conftest import DOCTOR_PWA_URL


@pytest.mark.e2e
class TestDoctorLogin:
    """Test doctor login flow."""

    def test_login_page_loads(self, doctor_page: Page):
        """Test that doctor login page loads correctly."""
        doctor_page.goto(f"{DOCTOR_PWA_URL}/login")

        expect(doctor_page.locator("h1")).to_contain_text("PUAR Doctor Portal")
        expect(doctor_page.locator("h2")).to_contain_text("Login")
        expect(doctor_page.locator('input[type="email"]')).to_be_visible()
        expect(doctor_page.locator('input[type="password"]')).to_be_visible()
        expect(doctor_page.locator('button[type="submit"]')).to_be_visible()

    def test_successful_login(self, doctor_page: Page, api_register_doctor):
        """Test successful doctor login."""
        creds = api_register_doctor
        doctor_page.goto(f"{DOCTOR_PWA_URL}/login")

        # Fill login form
        doctor_page.fill('input[type="email"]', creds["email"])
        doctor_page.fill('input[type="password"]', creds["password"])
        doctor_page.click('button[type="submit"]')

        # Should redirect to dashboard
        doctor_page.wait_for_url(re.compile(r".*/dashboard.*"), timeout=10000)

    def test_login_invalid_credentials(self, doctor_page: Page):
        """Test login with invalid credentials."""
        doctor_page.goto(f"{DOCTOR_PWA_URL}/login")

        doctor_page.fill('input[type="email"]', "invalid@example.com")
        doctor_page.fill('input[type="password"]', "wrongpassword123")
        doctor_page.click('button[type="submit"]')

        # Should show error message
        doctor_page.wait_for_selector(".bg-red-50", timeout=5000)
        expect(doctor_page.locator(".bg-red-50")).to_be_visible()


@pytest.mark.e2e
class TestDoctorDashboard:
    """Test doctor dashboard functionality."""

    def test_dashboard_loads_after_login(self, logged_in_doctor_page: Page):
        """Test that dashboard loads correctly after login."""
        expect(logged_in_doctor_page).to_have_url(re.compile(r".*/dashboard.*"))


@pytest.mark.e2e
class TestDoctorSlotManagement:
    """Test doctor slot management functionality."""

    def test_can_access_slots_page(self, logged_in_doctor_page: Page):
        """Test that slots page is accessible."""
        page = logged_in_doctor_page

        # Navigate to slots page
        page.goto(f"{DOCTOR_PWA_URL}/slots")

        # Should show slots page
        page.wait_for_load_state("networkidle")
        expect(page.locator("h1").filter(has_text="Manage Slots")).to_be_visible()

    def test_create_slots_button_visible(self, logged_in_doctor_page: Page):
        """Test that create slots button is visible."""
        page = logged_in_doctor_page

        page.goto(f"{DOCTOR_PWA_URL}/slots")
        page.wait_for_load_state("networkidle")

        # Should have a create slots button
        create_button = page.locator('button:has-text("Create")')
        expect(create_button).to_be_visible()

    def test_open_create_slots_modal(self, logged_in_doctor_page: Page):
        """Test opening the create slots modal."""
        page = logged_in_doctor_page

        page.goto(f"{DOCTOR_PWA_URL}/slots")
        page.wait_for_load_state("networkidle")

        # Click create slots button
        page.click('button:has-text("Create")')

        # Modal should appear
        modal = page.locator(".fixed.inset-0, [role='dialog']")
        expect(modal.first).to_be_visible()

    def test_slots_table_structure(self, logged_in_doctor_page: Page):
        """Test that slots table has correct structure."""
        page = logged_in_doctor_page

        page.goto(f"{DOCTOR_PWA_URL}/slots")
        page.wait_for_load_state("networkidle")

        # Table should have headers
        table = page.locator("table")
        expect(table).to_be_visible()

        # Check for expected headers
        headers = page.locator("th")
        expect(headers.first).to_be_visible()


@pytest.mark.e2e
class TestDoctorBookings:
    """Test doctor bookings view."""

    def test_can_access_bookings_page(self, logged_in_doctor_page: Page):
        """Test that bookings page is accessible."""
        page = logged_in_doctor_page

        page.goto(f"{DOCTOR_PWA_URL}/bookings")
        page.wait_for_load_state("networkidle")

        # Should show bookings page
        expect(page.locator("h1").filter(has_text="Appointments")).to_be_visible()


@pytest.mark.e2e
class TestDoctorPatientsView:
    """Test doctor patients view functionality."""

    def test_can_access_patients_page(self, logged_in_doctor_page: Page):
        """Test that patients page is accessible."""
        page = logged_in_doctor_page

        page.goto(f"{DOCTOR_PWA_URL}/patients")
        page.wait_for_load_state("networkidle")

        # Should show patients page
        expect(page.locator("h1").filter(has_text="Patients")).to_be_visible()
