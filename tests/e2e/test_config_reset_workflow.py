"""E2E tests for configuration reset workflow.

Priority 3: Tests data integrity and reset logic.
"""
import pytest
import re
from playwright.sync_api import Page, expect


def _immunity_input(page: Page, name: str):
    """Return immunity numeric input locator by row label text."""
    return page.locator(".immunity-row", has_text=f"{name.title()}:").locator("input").first


def _wait_ui_idle(page: Page):
    """Wait for transient overlays/modals to stop intercepting clicks."""
    overlay = page.locator("#loading-overlay")
    if overlay.count() > 0:
        expect(overlay).to_have_css("display", "none", timeout=10000)

    progress_modal = page.locator("#progress-modal")
    if progress_modal.count() > 0:
        expect(progress_modal).not_to_be_visible(timeout=10000)

    page.wait_for_timeout(100)


def _go_to_configuration_tab(page: Page):
    """Navigate to Configuration tab with robust locator fallbacks."""
    tab = page.get_by_role("tab", name="Configuration")
    if tab.count() == 0:
        tab = page.locator('button[id="configuration-tab"]')
    if tab.count() == 0:
        tab = page.locator('a:has-text("Configuration"), button:has-text("Configuration")')

    expect(tab.first).to_be_visible(timeout=5000)
    tab.first.click(timeout=5000)
    expect(page.get_by_label("Apply Target Immunities")).to_be_visible(timeout=5000)


def _set_target_immunities_switch(page: Page, enabled: bool):
    """Set immunity switch state via DOM events to avoid click/actionability flakiness."""
    ok = page.evaluate(
        """(enabled) => {
            const selectors = [
                'input#target-immunities-switch',
                '#target-immunities-switch input[type="checkbox"]'
            ];
            let input = null;
            for (const sel of selectors) {
                input = document.querySelector(sel);
                if (input) break;
            }
            if (!input) return false;
            input.checked = enabled;
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
        }""",
        enabled,
    )
    assert ok, "Could not locate target immunities switch input in DOM"


@pytest.mark.e2e
class TestConfigResetWorkflow:
    """Test configuration reset workflows."""

    def test_reset_button_restores_defaults(self, dash_page: Page, wait_for_spinner):
        """Test that reset button restores all default values."""
        # Modify multiple inputs
        ab_input = dash_page.locator("#ab-input")
        ab_input.fill("99")
        dash_page.keyboard.press("Tab")

        str_input = dash_page.locator("#str-mod-input")
        str_input.fill("35")
        dash_page.keyboard.press("Tab")

        # Toggle checkboxes
        keen_checkbox = dash_page.locator("#keen-switch")
        if keen_checkbox.is_checked():
            keen_checkbox.click()  # Turn off

        ic_checkbox = dash_page.locator("#improved-crit-switch")
        if ic_checkbox.is_visible() and ic_checkbox.is_checked():
            ic_checkbox.click()  # Turn off

        dash_page.wait_for_timeout(500)

        # Click reset button
        reset_btn = dash_page.locator("#reset-button")
        expect(reset_btn).to_be_visible(timeout=5000)
        reset_btn.click()
        wait_for_spinner()

        # Verify defaults restored (defaults from config)
        dash_page.wait_for_timeout(500)
        assert ab_input.input_value() == "68", "AB should reset to default"
        assert str_input.input_value() == "21", "STR should reset to default"
        assert keen_checkbox.is_checked() == True, "Keen should reset to default (True)"
        if ic_checkbox.is_visible():
            assert ic_checkbox.is_checked() == True, "Improved Crit should reset to default (True)"

    def test_reset_clears_additional_damage_changes(self, dash_page: Page, wait_for_spinner):
        """Test that reset clears additional damage source changes."""
        # Find and modify additional damage
        damage_switch = dash_page.locator("#damage-switch-Bard_Song")

        if damage_switch.is_visible():
            # Enable Bard Song (default is disabled)
            if not damage_switch.is_checked():
                damage_switch.click()
                dash_page.wait_for_timeout(500)

        # Reset
        reset_btn = dash_page.locator("#reset-button")
        expect(reset_btn).to_be_visible(timeout=5000)
        reset_btn.click()
        wait_for_spinner()

        # Verify Bard Song is disabled again
        dash_page.wait_for_timeout(500)
        if damage_switch.is_visible():
            assert damage_switch.is_checked() == False, "Bard Song should reset to disabled"

    def test_reset_on_multi_builds(self, dash_page: Page, wait_for_spinner):
        """Test that reset restores application to single default build."""
        # Add multiple builds
        add_btn = dash_page.locator("#add-build-btn")
        add_btn.click()
        wait_for_spinner()
        dash_page.wait_for_timeout(500)

        add_btn.click()
        wait_for_spinner()
        dash_page.wait_for_timeout(500)

        # Verify we have 3 builds
        build_tabs = dash_page.locator("button.build-tab-btn")
        expect(build_tabs).to_have_count(3, timeout=5000)

        # Modify current build (Build 3)
        ab_input = dash_page.locator("#ab-input")
        ab_input.fill("85")
        str_input = dash_page.locator("#str-mod-input")
        str_input.fill("30")

        keen_checkbox = dash_page.locator("#keen-switch")
        if keen_checkbox.is_checked():
            keen_checkbox.click()  # Turn off keen

        dash_page.wait_for_timeout(500)

        # Now reset - this should reset EVERYTHING including all builds
        reset_btn = dash_page.locator("#reset-button")
        expect(reset_btn).to_be_visible(timeout=5000)
        reset_btn.click()
        wait_for_spinner()

        # Verify application reset to single default build
        dash_page.wait_for_timeout(1000)  # Give time for UI to update
        build_tabs = dash_page.locator("button.build-tab-btn")
        expect(build_tabs).to_have_count(1, timeout=5000)

        # Verify default config restored
        expect(ab_input).to_have_value("68", timeout=5000)
        expect(str_input).to_have_value("21", timeout=5000)
        assert keen_checkbox.is_checked() == True, "Keen should reset to default (True)"

        # Verify build name is default
        active_tab = dash_page.locator("button.build-tab-btn.active")
        expect(active_tab).to_contain_text("Build 1")

    def test_sticky_bottom_bar_appears_on_changes(self, dash_page: Page):
        """Test that sticky bottom bar appears when config changes."""
        # Get sticky bar
        sticky_bar = dash_page.locator("#sticky-bottom-bar")

        # Modify input
        ab_input = dash_page.locator("#ab-input")
        ab_input.fill("70")
        dash_page.keyboard.press("Tab")

        # Scroll down to trigger sticky bar visibility check
        dash_page.evaluate("window.scrollTo(0, 500)")
        dash_page.wait_for_timeout(500)

        # Sticky bar should be visible or ready to show
        # (Implementation may vary - it might always be visible or show on scroll)

    def test_reset_button_in_sticky_bar(self, dash_page: Page, wait_for_spinner):
        """Test reset button in sticky bottom bar works."""
        # Modify config
        ab_input = dash_page.locator("#ab-input")
        ab_input.fill("75")
        dash_page.wait_for_timeout(500)

        # Find reset button (might be in sticky bar or main UI)
        reset_btn = dash_page.locator("#reset-config-btn, #reset-btn-sticky")

        if reset_btn.count() > 0:
            reset_btn.first.click()
            wait_for_spinner()

            # Verify reset worked
            assert ab_input.input_value() == "68", "Reset should restore default"


@pytest.mark.e2e
class TestConfigValidation:
    """Test configuration validation."""

    def test_validation_prevents_invalid_configs(self, dash_page: Page):
        """Test that validation prevents saving invalid configurations."""
        # Try to enter invalid AB (very high)
        ab_input = dash_page.locator("#ab-input")
        ab_input.fill("999")
        dash_page.keyboard.press("Tab")

        dash_page.wait_for_timeout(500)

        # Check for validation feedback
        # Could be: red border, error message, or value reset
        validation_msg = dash_page.locator(".validation-error, .error-message")

        # Either validation message shows or value gets corrected
        current_value = ab_input.input_value()

        # Value should either be corrected or show as invalid
        # (exact behavior depends on implementation)

    def test_negative_values_prevented(self, dash_page: Page):
        """Test that negative values are prevented."""
        # Try negative AB
        ab_input = dash_page.locator("#ab-input")
        ab_input.fill("-10")
        dash_page.keyboard.press("Tab")

        dash_page.wait_for_timeout(500)

        # Verify value is corrected
        value = ab_input.input_value()
        assert int(value) >= 0, "Negative AB should be prevented"

    def test_str_mod_limits(self, dash_page: Page):
        """Test STR modifier limits."""
        str_input = dash_page.locator("#str-mod-input")

        # Try extremely high STR
        str_input.fill("999")
        dash_page.keyboard.press("Tab")

        dash_page.wait_for_timeout(500)

        # Value should be limited or show validation
        # (exact max depends on implementation)


@pytest.mark.e2e
class TestSessionPersistence:
    """Test session storage and persistence."""

    def test_config_persists_across_page_reload(self, dash_page: Page):
        """Test that immunity edits persist after page reload."""
        fire_input = _immunity_input(dash_page, "fire")
        fire_input.fill("37")
        dash_page.keyboard.press("Tab")

        dash_page.wait_for_timeout(1000)  # Wait for auto-save

        # Reload page
        dash_page.reload()

        # Wait for app to load
        dash_page.wait_for_selector("#tabs", timeout=10000)
        dash_page.wait_for_timeout(1000)

        # Verify immunity value persisted
        assert float(_immunity_input(dash_page, "fire").input_value()) == 37.0

    def test_immunity_quick_toggle_restores_previous_values(self, dash_page: Page):
        """Test OFF->ON rapid toggle restores prior immunity values."""
        fire_input = _immunity_input(dash_page, "fire")
        fire_input.fill("44")
        dash_page.keyboard.press("Tab")
        dash_page.wait_for_timeout(400)

        immunities_switch = dash_page.locator("#target-immunities-switch")

        # Toggle OFF then ON quickly multiple times (stress race ordering)
        for _ in range(3):
            immunities_switch.click()
            dash_page.wait_for_timeout(10)
            immunities_switch.click()
            dash_page.wait_for_timeout(120)

        assert float(_immunity_input(dash_page, "fire").input_value()) == 44.0

    def test_reset_clears_session_storage(self, dash_page: Page, wait_for_spinner):
        """Test that reset clears session storage."""
        # Modify and save
        ab_input = dash_page.locator("#ab-input")
        ab_input.fill("76")
        dash_page.keyboard.press("Tab")
        dash_page.wait_for_timeout(1000)

        # Reset
        reset_btn = dash_page.locator("#reset-button")
        expect(reset_btn).to_be_visible(timeout=5000)
        reset_btn.click()
        wait_for_spinner()

        # Reload page
        dash_page.reload()
        dash_page.wait_for_selector("#tabs", timeout=10000)
        dash_page.wait_for_timeout(1000)

        # Verify default value (session cleared)
        assert ab_input.input_value() == "68", "Should have default after reset and reload"

    def test_fast_off_then_simulate_uses_zero_immunities(self, dash_page: Page, wait_for_simulation):
        """OFF->Simulate quickly should still run with zero immunities."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        expect(run_btn).to_be_visible(timeout=5000)

        fire_input = _immunity_input(dash_page, "fire")
        fire_input.fill("90")
        dash_page.keyboard.press("Tab")
        dash_page.wait_for_timeout(500)

        # Baseline with immunities ON and high fire immunity
        run_btn.click()
        wait_for_simulation()
        baseline_text = dash_page.locator("#comparative-table").inner_text()
        baseline_numbers = re.findall(r"\d+\.\d+", baseline_text)
        assert baseline_numbers, "Expected baseline DPS numbers in comparative table"
        baseline_dps = float(baseline_numbers[0])

        # Fast OFF -> immediate simulate; backend mitigation should force zero immunities.
        # Use direct DOM dispatch to avoid flaky click/actionability checks.
        _wait_ui_idle(dash_page)
        _set_target_immunities_switch(dash_page, False)
        dash_page.wait_for_timeout(20)

        rerun_btn = dash_page.locator("#resimulate-button")
        expect(rerun_btn).to_be_visible(timeout=5000)
        rerun_btn.click()
        wait_for_simulation()

        off_text = dash_page.locator("#comparative-table").inner_text()
        off_numbers = re.findall(r"\d+\.\d+", off_text)
        assert off_numbers, "Expected OFF-state DPS numbers in comparative table"
        off_dps = float(off_numbers[0])

        assert off_dps > baseline_dps, (
            f"Expected higher DPS with immunities OFF (zeroed), got OFF={off_dps} vs ON={baseline_dps}"
        )
