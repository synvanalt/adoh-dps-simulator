"""Smoke tests to verify E2E testing infrastructure works.

Run these first to ensure Playwright and Dash integration is working.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
def test_dash_app_loads(dash_page: Page):
    """Smoke test: Verify Dash app loads successfully."""
    # Verify tabs loaded
    tabs = dash_page.locator("#tabs")
    expect(tabs).to_be_visible(timeout=10000)


@pytest.mark.e2e
def test_app_content_visible(dash_page: Page):
    """Smoke test: Verify main app content is visible."""
    # Verify main tabs exist
    tabs = dash_page.locator("#tabs")
    expect(tabs).to_be_visible(timeout=10000)


@pytest.mark.e2e
def test_basic_input_exists(dash_page: Page):
    """Smoke test: Verify basic input controls exist."""
    # Verify AB input exists
    ab_input = dash_page.locator("#ab-input")
    expect(ab_input).to_be_visible(timeout=5000)


@pytest.mark.e2e
def test_run_button_exists(dash_page: Page):
    """Smoke test: Verify run simulation button exists."""
    run_btn = dash_page.locator("#sticky-simulate-button")
    expect(run_btn).to_be_visible(timeout=5000)


@pytest.mark.e2e
def test_no_javascript_errors_on_load(dash_page: Page):
    """Smoke test: Verify no JavaScript errors on initial load."""
    errors = []

    def on_console(msg):
        if msg.type == "error":
            errors.append(msg.text)

    dash_page.on("console", on_console)

    # Wait a bit for any errors to appear
    dash_page.wait_for_timeout(2000)

    # Should have no console errors
    assert len(errors) == 0, f"JavaScript console errors found: {errors}"
