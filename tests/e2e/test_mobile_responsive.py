"""E2E tests for mobile responsiveness."""
import pytest
from playwright.sync_api import Page, expect


class TestMobileResponsive:
    """Test mobile responsiveness of Patient PWA."""

    def test_booking_page_calendar_visible_on_mobile(self, logged_in_patient_page: Page):
        """Calendar should be fully visible on mobile booking page."""
        page = logged_in_patient_page
        # Set mobile viewport
        page.set_viewport_size({"width": 390, "height": 844})
        
        page.goto("http://localhost:3000/book")
        page.wait_for_load_state("networkidle")
        
        # Calendar should be visible (not just "Select a Date" text)
        # Use data-testid for reliable selection (avoids matching SVG icons with calendar class)
        calendar = page.get_by_test_id("calendar")
        expect(calendar).to_be_visible(timeout=5000)
        
        # Calendar should have day tiles
        day_tiles = page.locator(".react-calendar__tile, [class*='CalendarDay'], button[name*='day']")
        expect(day_tiles.first).to_be_visible()

    def test_booking_page_title_not_translation_key(self, logged_in_patient_page: Page):
        """Booking page should have proper title, not 'booking.new' translation key."""
        page = logged_in_patient_page
        page.set_viewport_size({"width": 390, "height": 844})
        
        page.goto("http://localhost:3000/book")
        page.wait_for_load_state("networkidle")
        
        # Get all headings
        headings = page.locator("h1, h2")
        
        for i in range(headings.count()):
            heading = headings.nth(i)
            if heading.is_visible():
                text = heading.text_content() or ""
                # Translation keys have format like "booking.new" or "page.title"
                assert not (text.count(".") >= 1 and text.replace(".", "").isalpha()), \
                    f"Heading appears to be untranslated key: '{text}'"

    def test_booking_stepper_fits_mobile_viewport(self, logged_in_patient_page: Page):
        """Step indicator (1-2-3) should fit within mobile width without overflow."""
        page = logged_in_patient_page
        viewport_width = 390
        page.set_viewport_size({"width": viewport_width, "height": 844})
        
        page.goto("http://localhost:3000/book")
        page.wait_for_load_state("networkidle")
        
        # Find stepper or step indicators
        stepper = page.locator("[class*='stepper'], [class*='step'], [class*='wizard']").first
        if stepper.is_visible():
            box = stepper.bounding_box()
            assert box is not None, "Stepper should have bounding box"
            # Allow some padding but shouldn't overflow much
            assert box["width"] <= viewport_width + 20, \
                f"Stepper width {box['width']}px exceeds mobile viewport {viewport_width}px"

    def test_bottom_navigation_visible_on_mobile(self, logged_in_patient_page: Page):
        """Bottom navigation should be visible and all items accessible on mobile."""
        page = logged_in_patient_page
        page.set_viewport_size({"width": 390, "height": 844})
        
        page.goto("http://localhost:3000")
        page.wait_for_load_state("networkidle")
        
        # Bottom nav should be visible
        nav = page.locator("nav, [class*='BottomNav'], [class*='bottomNav'], [role='navigation']")
        expect(nav.first).to_be_visible()
        
        # Should have navigation items
        nav_items = page.locator("nav a, nav button, [class*='navItem'], [class*='NavItem']")
        count = nav_items.count()
        assert count >= 3, f"Expected at least 3 nav items, got {count}"

    def test_dashboard_content_fits_mobile(self, logged_in_patient_page: Page):
        """Dashboard content should not overflow horizontally on mobile."""
        page = logged_in_patient_page
        viewport_width = 390
        page.set_viewport_size({"width": viewport_width, "height": 844})
        
        page.goto("http://localhost:3000")
        page.wait_for_load_state("networkidle")
        
        # Check for horizontal scroll (indicates overflow)
        scroll_width = page.evaluate("document.documentElement.scrollWidth")
        client_width = page.evaluate("document.documentElement.clientWidth")
        
        assert scroll_width <= client_width + 10, \
            f"Page has horizontal overflow: scrollWidth={scroll_width}, clientWidth={client_width}"
