"""UI component test fixtures using Playwright."""
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def mock_simulation_results():
    """Mock simulation results for UI tests."""
    return {
        "avg_dps": 245.6,
        "std_dps": 12.3,
        "cv": 0.05,
        "total_damage": 147360,
        "total_rounds": 600,
        "hit_rate": 0.85,
        "crit_rate": 0.15,
        "damage_breakdown": {
            "physical": 0.65,
            "fire": 0.25,
            "divine": 0.10
        }
    }


@pytest.fixture
def fill_character_settings(dash_page: Page):
    """Helper to fill in character settings."""
    def _fill(ab=68, str_mod=21, keen=True, improved_crit=True):
        # Fill Attack Bonus
        ab_input = dash_page.locator("#ab-input")
        ab_input.fill(str(ab))

        # Fill STR Modifier
        str_input = dash_page.locator("#str-mod-input")
        str_input.fill(str(str_mod))

        # Set Keen checkbox
        keen_checkbox = dash_page.locator("#keen-switch")
        if keen != keen_checkbox.is_checked():
            keen_checkbox.click()

        # Set Improved Critical checkbox
        ic_checkbox = dash_page.locator("#improved-crit-switch")
        if improved_crit != ic_checkbox.is_checked():
            ic_checkbox.click()

    return _fill


@pytest.fixture
def check_no_console_errors(page: Page):
    """Check that there are no JavaScript console errors."""
    errors = []

    def on_console_message(msg):
        if msg.type == "error":
            errors.append(msg.text)

    page.on("console", on_console_message)

    yield

    # Assert no errors after test
    assert len(errors) == 0, f"Console errors found: {errors}"
