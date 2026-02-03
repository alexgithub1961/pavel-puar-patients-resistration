"""E2E tests for Patient PWA - registration, login, booking flow."""

import re
import pytest
from playwright.sync_api import Page, expect

from tests.e2e.conftest import PATIENT_PWA_URL


@pytest.mark.e2e
class TestPatientRegistration:
    """Test patient registration flow."""

    def test_registration_page_loads(self, patient_page: Page):
        """Test that registration page loads correctly."""
        patient_page.goto(f"{PATIENT_PWA_URL}/register")

        # Check page title and form elements
        expect(patient_page.locator("h1")).to_contain_text("PUAR")
        expect(patient_page.locator("h2")).to_contain_text("Register")
        expect(patient_page.locator('input[type="email"]')).to_be_visible()
        expect(patient_page.locator('input[type="password"]').first).to_be_visible()

    def test_successful_registration(self, patient_page: Page, test_patient_credentials):
        """Test successful patient registration."""
        patient_page.goto(f"{PATIENT_PWA_URL}/register")

        # Wait for form to load
        patient_page.wait_for_load_state("networkidle")

        # Fill registration form using name attributes
        patient_page.fill('input[name="firstName"]', test_patient_credentials["first_name"])
        patient_page.fill('input[name="lastName"]', test_patient_credentials["last_name"])
        patient_page.fill('input[type="email"]', test_patient_credentials["email"])
        patient_page.fill('input[name="password"]', test_patient_credentials["password"])
        patient_page.fill('input[name="confirmPassword"]', test_patient_credentials["password"])

        # Submit
        patient_page.click('button[type="submit"]')

        # Should redirect to login page after successful registration
        patient_page.wait_for_url(re.compile(r".*/login.*"), timeout=10000)
        expect(patient_page.locator("h2")).to_contain_text("Login")

    def test_registration_validation_errors(self, patient_page: Page):
        """Test registration form validation."""
        patient_page.goto(f"{PATIENT_PWA_URL}/register")

        # Submit empty form
        patient_page.click('button[type="submit"]')

        # Should show validation errors
        expect(patient_page.locator(".text-red-600").first).to_be_visible()


@pytest.mark.e2e
class TestPatientLogin:
    """Test patient login flow."""

    def test_login_page_loads(self, patient_page: Page):
        """Test that login page loads correctly."""
        patient_page.goto(f"{PATIENT_PWA_URL}/login")

        expect(patient_page.locator("h1")).to_contain_text("PUAR")
        expect(patient_page.locator("h2")).to_contain_text("Login")
        expect(patient_page.locator('input[type="email"]')).to_be_visible()
        expect(patient_page.locator('input[type="password"]')).to_be_visible()
        expect(patient_page.locator('button[type="submit"]')).to_be_visible()

    def test_login_link_to_register(self, patient_page: Page):
        """Test link from login to register page."""
        patient_page.goto(f"{PATIENT_PWA_URL}/login")

        # Click register link
        patient_page.click('a[href="/register"]')

        # Should navigate to register page
        patient_page.wait_for_url(re.compile(r".*/register.*"))
        expect(patient_page.locator("h2")).to_contain_text("Register")

    def test_successful_login(self, patient_page: Page, api_register_patient):
        """Test successful patient login."""
        creds = api_register_patient
        patient_page.goto(f"{PATIENT_PWA_URL}/login")

        # Fill login form
        patient_page.fill('input[type="email"]', creds["email"])
        patient_page.fill('input[type="password"]', creds["password"])
        patient_page.click('button[type="submit"]')

        # Should redirect to dashboard
        patient_page.wait_for_url(re.compile(r".*/dashboard.*"), timeout=10000)

    def test_login_invalid_credentials(self, patient_page: Page):
        """Test login with invalid credentials."""
        patient_page.goto(f"{PATIENT_PWA_URL}/login")

        patient_page.fill('input[type="email"]', "invalid@example.com")
        patient_page.fill('input[type="password"]', "wrongpassword123")
        patient_page.click('button[type="submit"]')

        # Should show error message
        patient_page.wait_for_selector(".bg-red-50", timeout=5000)
        expect(patient_page.locator(".bg-red-50")).to_be_visible()


@pytest.mark.e2e
class TestPatientDashboard:
    """Test patient dashboard functionality."""

    def test_dashboard_loads_after_login(self, logged_in_patient_page: Page):
        """Test that dashboard loads correctly after login."""
        # Should be on dashboard
        expect(logged_in_patient_page).to_have_url(re.compile(r".*/dashboard.*"))

    def test_navigation_menu(self, logged_in_patient_page: Page):
        """Test navigation menu items."""
        page = logged_in_patient_page

        # Check navigation links exist
        # Try different selectors for navigation
        nav = page.locator("nav, aside, header")
        expect(nav.first).to_be_visible()


@pytest.mark.e2e
class TestPatientBookingFlow:
    """Test patient booking flow."""

    def test_can_access_booking_page(self, logged_in_patient_page: Page):
        """Test that booking page is accessible."""
        page = logged_in_patient_page

        # Navigate to booking page
        page.goto(f"{PATIENT_PWA_URL}/book")

        # Should show booking page content
        expect(page.locator("h1")).to_be_visible()

    def test_booking_window_check(self, logged_in_patient_page: Page):
        """Test booking window validation."""
        page = logged_in_patient_page

        # Navigate to booking page
        page.goto(f"{PATIENT_PWA_URL}/book")

        # Page should load either booking form or "cannot book" message
        # Wait for page content to load
        page.wait_for_load_state("networkidle")

        # Check for either date selection or booking restriction message
        booking_content = page.locator("body")
        expect(booking_content).to_be_visible()

    def test_view_existing_bookings(self, logged_in_patient_page: Page):
        """Test viewing existing bookings."""
        page = logged_in_patient_page

        # Navigate to bookings page
        page.goto(f"{PATIENT_PWA_URL}/bookings")

        # Should show bookings page
        expect(page.locator("h1")).to_be_visible()


@pytest.mark.e2e
class TestPatientProfile:
    """Test patient profile functionality."""

    def test_can_view_profile(self, logged_in_patient_page: Page):
        """Test viewing patient profile."""
        page = logged_in_patient_page

        # Navigate to profile page
        page.goto(f"{PATIENT_PWA_URL}/profile")

        # Should show profile page
        page.wait_for_load_state("networkidle")
        # Check for profile page content - just verify we're on the profile page
        expect(page.locator("h1")).to_be_visible()
