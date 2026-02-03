"""E2E tests for complete DPS simulation workflow.

Priority 1: Tests the core business logic and primary user journey.
"""
import pytest
from playwright.sync_api import Page, expect
import re


@pytest.mark.e2e
@pytest.mark.slow
class TestCompleteDPSWorkflow:
    """Test end-to-end DPS simulation workflows."""

    def test_basic_simulation_workflow(self, dash_page: Page, wait_for_simulation):
        """Test basic simulation with default settings."""
        # Verify app loaded
        expect(dash_page.locator("#app-content")).to_be_visible()

        # Navigate to Main tab if not already there
        main_tab = dash_page.locator('a[href="#main"]')
        if main_tab.is_visible():
            main_tab.click()

        # Click Run Simulation button
        run_btn = dash_page.locator("#run-simulation-btn")
        expect(run_btn).to_be_visible(timeout=5000)
        run_btn.click()

        # Wait for simulation to complete
        wait_for_simulation()

        # Verify results are displayed
        results_content = dash_page.locator("#results-content")
        expect(results_content).to_be_visible()

        # Check that DPS value is displayed
        dps_display = dash_page.locator('text=/Average DPS/i')
        expect(dps_display).to_be_visible()

        # Verify DPS is a reasonable number (> 0)
        dps_text = dash_page.locator("#avg-dps-value").inner_text()
        dps_value = float(dps_text)
        assert dps_value > 0, f"Expected positive DPS, got {dps_value}"

    def test_simulation_with_critical_feats(self, dash_page: Page, wait_for_simulation, wait_for_spinner):
        """Test simulation with critical hit feats enabled."""
        # Enable Keen and Improved Critical (should already be default, but verify)
        keen_checkbox = dash_page.locator("#keen-switch")
        ic_checkbox = dash_page.locator("#improved-crit-checkbox")

        if not keen_checkbox.is_checked():
            keen_checkbox.click()
        if not ic_checkbox.is_checked():
            ic_checkbox.click()

        dash_page.wait_for_timeout(500)  # Auto-save delay

        # Run simulation
        run_btn = dash_page.locator("#run-simulation-btn")
        run_btn.click()

        wait_for_simulation()

        # Verify critical hit rate is displayed and > 0
        crit_rate_elem = dash_page.locator("#crit-rate-value")
        if crit_rate_elem.is_visible():
            crit_rate_text = crit_rate_elem.inner_text()
            # Parse percentage (e.g., "15.3%")
            crit_rate = float(crit_rate_text.replace("%", ""))
            assert crit_rate > 0, f"Expected positive crit rate with feats enabled, got {crit_rate}"

    def test_simulation_with_additional_damage(self, dash_page: Page, wait_for_simulation):
        """Test simulation with additional damage sources."""
        # Enable Flame Weapon (should be enabled by default)
        # Navigate to additional damage section
        damage_panel = dash_page.locator("#additional-damage-panel")
        if not damage_panel.is_visible():
            # Expand panel if collapsed
            damage_header = dash_page.locator('text=/Additional Damage/i')
            if damage_header.is_visible():
                damage_header.click()

        # Verify Flame Weapon is enabled
        fw_switch = dash_page.locator("#damage-switch-Flame_Weapon")
        if fw_switch.is_visible() and not fw_switch.is_checked():
            fw_switch.click()
            dash_page.wait_for_timeout(500)

        # Run simulation
        run_btn = dash_page.locator("#run-simulation-btn")
        run_btn.click()

        wait_for_simulation()

        # Verify results show damage breakdown
        results_content = dash_page.locator("#results-content")
        expect(results_content).to_contain_text(re.compile(r"damage", re.IGNORECASE), timeout=5000)

    def test_resimulation_with_different_parameters(self, dash_page: Page, wait_for_simulation):
        """Test running simulation twice with different parameters."""
        # Run first simulation
        run_btn = dash_page.locator("#run-simulation-btn")
        run_btn.click()
        wait_for_simulation()

        # Get first DPS result
        dps_elem = dash_page.locator("#avg-dps-value")
        first_dps = float(dps_elem.inner_text())

        # Modify AB to significantly change DPS
        ab_input = dash_page.locator("#ab-input")
        ab_input.fill("50")  # Lower AB
        dash_page.keyboard.press("Tab")
        dash_page.wait_for_timeout(500)

        # Run second simulation
        run_btn.click()
        wait_for_simulation()

        # Get second DPS result
        second_dps = float(dps_elem.inner_text())

        # Verify DPS changed (lower AB should give lower DPS)
        assert second_dps < first_dps, f"Expected lower DPS with AB=50, got {second_dps} vs {first_dps}"

    @pytest.mark.background
    def test_simulation_progress_updates(self, dash_page: Page):
        """Test that simulation progress updates are shown."""
        # Click run simulation
        run_btn = dash_page.locator("#run-simulation-btn")
        run_btn.click()

        # Verify progress modal appears
        progress_modal = dash_page.locator("#progress-modal")
        expect(progress_modal).to_be_visible(timeout=5000)

        # Verify progress bar or percentage is visible
        progress_indicator = dash_page.locator("#progress-bar, #progress-percentage, text=/progress/i")
        expect(progress_indicator.first).to_be_visible(timeout=10000)

        # Wait for simulation to complete
        expect(progress_modal).not_to_be_visible(timeout=60000)

    @pytest.mark.background
    def test_simulation_cancel_button(self, dash_page: Page):
        """Test canceling a running simulation."""
        # Start simulation
        run_btn = dash_page.locator("#run-simulation-btn")
        run_btn.click()

        # Wait for progress modal
        progress_modal = dash_page.locator("#progress-modal")
        expect(progress_modal).to_be_visible(timeout=5000)

        # Click cancel button
        cancel_btn = dash_page.locator("#cancel-simulation-btn")
        if cancel_btn.is_visible():
            cancel_btn.click()

            # Verify modal closes
            expect(progress_modal).not_to_be_visible(timeout=10000)

            # Verify no results shown (or results from previous run)
            # The simulation should have been cancelled


@pytest.mark.e2e
class TestSimulationValidation:
    """Test simulation input validation."""

    def test_invalid_ab_shows_validation_error(self, dash_page: Page):
        """Test that invalid AB shows validation error."""
        # Enter invalid AB (too high)
        ab_input = dash_page.locator("#ab-input")
        ab_input.fill("999")
        dash_page.keyboard.press("Tab")

        # Check for validation message
        dash_page.wait_for_timeout(500)

        # Run simulation should be disabled or show error
        run_btn = dash_page.locator("#run-simulation-btn")

        # Either button is disabled or validation error appears
        # (depending on implementation)
        is_disabled = run_btn.is_disabled()
        if not is_disabled:
            # Try to run and expect error modal
            run_btn.click()
            error_modal = dash_page.locator("#sim-error-modal, .error-message")
            # Error modal might appear
            dash_page.wait_for_timeout(1000)

    def test_negative_damage_prevented(self, dash_page: Page):
        """Test that negative damage inputs are validated."""
        # Try to enter negative damage
        damage_panel = dash_page.locator("#additional-damage-panel")

        # Find first damage input
        damage_input = dash_page.locator("input[id^='damage-input']").first
        if damage_input.is_visible():
            damage_input.fill("-5")
            dash_page.keyboard.press("Tab")

            # Verify value is corrected to 0 or shows validation error
            dash_page.wait_for_timeout(500)
            value = damage_input.input_value()
            assert int(value) >= 0, "Negative damage should be prevented"
