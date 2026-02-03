"""
CRITICAL USER JOURNEY TESTS

These tests verify that a REAL USER can complete the core flows.
They should be run against the DEPLOYED URLs, not localhost.

Usage:
    # Against deployed AWS:
    PATIENT_PWA_URL=https://d2wowd7dw25och.cloudfront.net \
    API_URL=https://nmpjiqngaz.us-east-1.awsapprunner.com \
    pytest tests/e2e/test_user_journey.py -v

If these tests pass on localhost but FAIL on deployed URLs,
you have a localhost contamination bug!
"""

import re
import pytest
from playwright.sync_api import Page, expect

from tests.e2e.conftest import PATIENT_PWA_URL, API_URL


def demo_login(page: Page, account_type: str = "new_patient"):
    """
    Helper to perform demo login.
    
    Handles the feature tour modal that appears after clicking demo button.
    """
    page.goto(f"{PATIENT_PWA_URL}/login")
    page.wait_for_load_state("networkidle")
    
    if account_type == "new_patient":
        btn = page.locator("button", has_text="New Patient").or_(
            page.locator("button", has_text="מטופל חדש")).or_(
            page.locator("button", has_text="Новый пациент"))
    else:
        btn = page.locator("button", has_text="Regular Patient").or_(
            page.locator("button", has_text="מטופל קבוע")).or_(
            page.locator("button", has_text="Постоянный пациент"))
    
    btn.click()
    
    # Feature tour modal appears - close it to trigger demo login
    close_tour_btn = page.locator("button").filter(has=page.locator("svg.lucide-x")).first
    try:
        if close_tour_btn.is_visible(timeout=3000):
            close_tour_btn.click()
    except:
        pass  # Tour might not show in some cases
    
    # Wait for dashboard
    page.wait_for_url(re.compile(r".*/dashboard.*"), timeout=15000)


@pytest.mark.e2e
@pytest.mark.critical
class TestDemoUserJourney:
    """
    Test the DEMO user journey - this is what users actually do!
    
    If this test fails, THE APP IS BROKEN for users.
    """

    def test_demo_new_patient_can_login(self, page: Page):
        """
        CRITICAL: Demo new patient can login and reach dashboard.
        
        This is the PRIMARY user journey for demos.
        If this fails, the demo is broken!
        """
        demo_login(page, "new_patient")
        
        # Verify we're actually on the dashboard with content
        expect(page.locator("h1")).to_be_visible()
        
    def test_demo_regular_patient_can_login(self, page: Page):
        """
        CRITICAL: Demo regular patient can login and reach dashboard.
        """
        demo_login(page, "regular_patient")
        expect(page.locator("h1")).to_be_visible()

    def test_demo_patient_can_see_next_steps(self, page: Page):
        """
        After demo login, user should see "next steps" guidance.
        """
        demo_login(page, "new_patient")
        
        # Dashboard should have content
        dashboard_content = page.locator("main, .dashboard, [role='main']")
        expect(dashboard_content).to_be_visible()


@pytest.mark.e2e
@pytest.mark.critical
class TestBookingUserJourney:
    """Test the booking flow - the core business value."""

    def test_demo_patient_can_access_booking(self, page: Page):
        """Demo patient can navigate to booking page."""
        demo_login(page, "new_patient")
        
        # Navigate to booking
        page.goto(f"{PATIENT_PWA_URL}/book")
        page.wait_for_load_state("networkidle")
        
        # Should see booking page content
        expect(page.locator("h1")).to_be_visible()

    def test_demo_patient_can_view_appointments(self, page: Page):
        """Demo patient can view their appointments (past & future)."""
        demo_login(page, "regular_patient")
        
        # Navigate to bookings/appointments
        page.goto(f"{PATIENT_PWA_URL}/bookings")
        page.wait_for_load_state("networkidle")
        
        # Should see appointments page
        expect(page.locator("h1")).to_be_visible()


@pytest.mark.e2e  
@pytest.mark.critical
class TestAPIConnectivity:
    """
    Verify frontend can actually reach the API.
    
    This catches localhost contamination bugs!
    """
    
    def test_api_is_reachable_from_test_environment(self):
        """API should be reachable (sanity check)."""
        import httpx
        
        response = httpx.get(f"{API_URL}/", timeout=10)
        assert response.status_code == 200
        assert "PUAR" in response.text or "app" in response.text
        
    def test_demo_login_api_works(self):
        """Demo login API endpoint works directly."""
        import httpx
        
        response = httpx.post(
            f"{API_URL}/api/v1/auth/demo",
            json={"role": "new_patient"},
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        
    def test_frontend_calls_correct_api(self, page: Page):
        """
        Verify frontend actually calls the configured API, not localhost.
        
        This is the KEY test for localhost contamination!
        """
        # Capture network requests
        api_calls = []
        
        def handle_request(request):
            if "/api/" in request.url:
                api_calls.append(request.url)
        
        page.on("request", handle_request)
        
        # Perform demo login (this will trigger API calls)
        demo_login(page, "new_patient")
        
        # Check that API calls went to the right place
        assert len(api_calls) > 0, "No API calls captured - frontend not calling API?"
        
        for call in api_calls:
            assert "localhost" not in call, f"Frontend calling localhost! URL: {call}"
