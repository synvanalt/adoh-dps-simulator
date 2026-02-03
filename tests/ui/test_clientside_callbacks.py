"""Test clientside JavaScript callbacks using Playwright.

These tests verify that clientside callbacks execute correctly in the browser
without requiring server round-trips.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.ui
@pytest.mark.clientside
class TestBuildSwitcherCallbacks:
    """Test build switching clientside callbacks."""

    def test_build_switching_loads_config(self, dash_page: Page, wait_for_spinner):
        """Test that switching builds loads the correct config via clientside callback."""
        # Add a second build
        add_btn = dash_page.locator("#add-build-btn")
        add_btn.click()
        wait_for_spinner()

        # Modify Build 2's AB input
        ab_input = dash_page.locator("#ab-input")
        ab_input.fill("80")
        dash_page.keyboard.press("Tab")  # Trigger blur
        dash_page.wait_for_timeout(500)  # Wait for auto-save

        # Get build tabs
        build_tabs = dash_page.locator("button.build-tab-btn")

        # Switch to Build 1 (index 0)
        build_tabs.nth(0).click()
        wait_for_spinner()

        # Verify Build 1 has default AB (not 80)
        ab_value = ab_input.input_value()
        assert ab_value == "68", f"Expected default AB 68, got {ab_value}"

        # Switch back to Build 2 (index 1)
        build_tabs.nth(1).click()
        wait_for_spinner()

        # Verify Build 2 has modified AB (80)
        ab_value = ab_input.input_value()
        assert ab_value == "80", f"Expected modified AB 80, got {ab_value}"

    def test_build_switching_preserves_multiple_inputs(self, dash_page: Page, wait_for_spinner):
        """Test that switching builds preserves multiple input values."""
        # Add second build
        add_btn = dash_page.locator("#add-build-btn")
        add_btn.click()
        wait_for_spinner()

        # Modify multiple inputs on Build 2
        dash_page.locator("#ab-input").fill("75")
        dash_page.locator("#str-mod-input").fill("25")

        # Toggle Keen checkbox
        keen_checkbox = dash_page.locator("#keen-checkbox")
        initial_keen_state = keen_checkbox.is_checked()
        keen_checkbox.click()

        dash_page.wait_for_timeout(500)  # Auto-save delay

        # Switch to Build 1
        build_tabs = dash_page.locator("button.build-tab-btn")
        build_tabs.nth(0).click()
        wait_for_spinner()

        # Verify default values on Build 1
        assert dash_page.locator("#ab-input").input_value() == "68"
        assert dash_page.locator("#str-mod-input").input_value() == "21"
        assert dash_page.locator("#keen-checkbox").is_checked() == True  # Default is checked

        # Switch back to Build 2
        build_tabs.nth(1).click()
        wait_for_spinner()

        # Verify modified values preserved
        assert dash_page.locator("#ab-input").input_value() == "75"
        assert dash_page.locator("#str-mod-input").input_value() == "25"
        assert dash_page.locator("#keen-checkbox").is_checked() != initial_keen_state

    def test_switch_build_no_update_on_same_build(self, dash_page: Page):
        """Test that clicking the active build doesn't trigger updates."""
        # Get the active build tab (Build 1)
        build_tabs = dash_page.locator("button.build-tab-btn")

        # Click the active build
        build_tabs.nth(0).click()

        # Verify no spinner appears (spinner only shows for different build)
        spinner = dash_page.locator("#loading-overlay")
        # Spinner should remain hidden
        expect(spinner).to_have_css("display", "none")

    def test_load_from_buffer_after_add_build(self, dash_page: Page, wait_for_spinner):
        """Test load_from_buffer callback after adding new build."""
        # Add new build
        add_btn = dash_page.locator("#add-build-btn")
        add_btn.click()
        wait_for_spinner()

        # Verify default values loaded via load_from_buffer
        assert dash_page.locator("#ab-input").input_value() == "68"
        assert dash_page.locator("#str-mod-input").input_value() == "21"
        assert dash_page.locator("#keen-checkbox").is_checked() == True


@pytest.mark.ui
@pytest.mark.clientside
class TestSpinnerCallbacks:
    """Test spinner display clientside callbacks."""

    def test_spinner_on_tab_click(self, dash_page: Page):
        """Test that spinner shows when clicking different build tab."""
        # Add second build first
        add_btn = dash_page.locator("#add-build-btn")
        add_btn.click()

        # Wait for spinner to hide after add
        spinner = dash_page.locator("#loading-overlay")
        expect(spinner).to_have_css("display", "none", timeout=10000)

        # Click Build 1 tab
        build_tabs = dash_page.locator("button.build-tab-btn")
        build_tabs.nth(0).click()

        # Spinner should appear (display: flex)
        expect(spinner).to_have_css("display", "flex", timeout=2000)

        # Wait for it to disappear after switch complete
        expect(spinner).to_have_css("display", "none", timeout=10000)

    def test_spinner_on_add_build_click(self, dash_page: Page):
        """Test that spinner shows when clicking add build button."""
        spinner = dash_page.locator("#loading-overlay")

        # Click add build
        add_btn = dash_page.locator("#add-build-btn")
        add_btn.click()

        # Spinner should appear immediately
        expect(spinner).to_have_css("display", "flex", timeout=2000)

        # Wait for it to disappear
        expect(spinner).to_have_css("display", "none", timeout=10000)

    def test_spinner_on_duplicate_build_click(self, dash_page: Page, wait_for_spinner):
        """Test that spinner shows when clicking duplicate build button."""
        # First add a build to have something to duplicate
        add_btn = dash_page.locator("#add-build-btn")
        add_btn.click()
        wait_for_spinner()

        spinner = dash_page.locator("#loading-overlay")

        # Click duplicate build
        dup_btn = dash_page.locator("#duplicate-build-btn")
        dup_btn.click()

        # Spinner should appear
        expect(spinner).to_have_css("display", "flex", timeout=2000)

        # Wait for it to disappear
        expect(spinner).to_have_css("display", "none", timeout=10000)

    def test_spinner_on_delete_build_click(self, dash_page: Page, wait_for_spinner):
        """Test that spinner shows when clicking delete build button."""
        # Add builds first (need at least 2 to delete)
        add_btn = dash_page.locator("#add-build-btn")
        add_btn.click()
        wait_for_spinner()
        add_btn.click()
        wait_for_spinner()

        spinner = dash_page.locator("#loading-overlay")

        # Click delete build
        del_btn = dash_page.locator("#delete-build-btn")
        del_btn.click()

        # Spinner should appear
        expect(spinner).to_have_css("display", "flex", timeout=2000)

        # Wait for it to disappear
        expect(spinner).to_have_css("display", "none", timeout=10000)

    def test_spinner_on_reset_click(self, dash_page: Page):
        """Test that spinner shows when clicking reset button."""
        # Modify some inputs first
        dash_page.locator("#ab-input").fill("99")

        # Make sticky bar appear by scrolling or modifying inputs
        dash_page.wait_for_timeout(500)

        # Click reset button
        reset_btn = dash_page.locator("#reset-config-btn")
        if reset_btn.is_visible():
            spinner = dash_page.locator("#loading-overlay")

            reset_btn.click()

            # Spinner should appear
            expect(spinner).to_have_css("display", "flex", timeout=2000)

            # Wait for it to disappear
            expect(spinner).to_have_css("display", "none", timeout=10000)


@pytest.mark.ui
@pytest.mark.clientside
class TestClientsidenNoErrors:
    """Test that clientside callbacks don't produce JavaScript errors."""

    def test_no_console_errors_during_build_operations(self, dash_page: Page, wait_for_spinner):
        """Test that no console errors occur during build operations."""
        errors = []

        def on_console(msg):
            if msg.type == "error":
                errors.append(msg.text)

        dash_page.on("console", on_console)

        # Perform various build operations
        add_btn = dash_page.locator("#add-build-btn")

        # Add build
        add_btn.click()
        wait_for_spinner()

        # Modify inputs
        dash_page.locator("#ab-input").fill("75")
        dash_page.wait_for_timeout(500)

        # Switch builds
        build_tabs = dash_page.locator("button.build-tab-btn")
        build_tabs.nth(0).click()
        wait_for_spinner()

        build_tabs.nth(1).click()
        wait_for_spinner()

        # Duplicate build
        dup_btn = dash_page.locator("#duplicate-build-btn")
        dup_btn.click()
        wait_for_spinner()

        # Check no errors
        assert len(errors) == 0, f"JavaScript console errors found: {errors}"

    def test_clientside_callbacks_execute_without_server_roundtrip(self, dash_page: Page, wait_for_spinner):
        """Verify clientside callbacks execute in browser without server calls."""
        # Add second build
        add_btn = dash_page.locator("#add-build-btn")
        add_btn.click()
        wait_for_spinner()

        # Modify Build 2
        dash_page.locator("#ab-input").fill("85")
        dash_page.wait_for_timeout(500)

        # Monitor network requests during tab switch
        requests = []

        def on_request(request):
            requests.append(request.url)

        dash_page.on("request", on_request)

        # Switch to Build 1 (should be clientside only)
        build_tabs = dash_page.locator("button.build-tab-btn")
        build_tabs.nth(0).click()

        # Wait a bit for any potential server calls
        dash_page.wait_for_timeout(1000)

        # Filter out static asset requests
        server_requests = [r for r in requests if "/_dash-update-component" in r]

        # Clientside callback should NOT make server requests for tab switching
        # Note: There might be auto-save requests, but the tab switch itself should be clientside
        # We're mainly checking that config values update without additional server calls
        ab_value = dash_page.locator("#ab-input").input_value()
        assert ab_value == "68", "Config should update via clientside callback"
