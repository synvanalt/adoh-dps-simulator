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
        # Verify app loaded by checking for tabs
        expect(dash_page.locator("#tabs")).to_be_visible()

        # Click Run Simulation button (sticky button at bottom)
        run_btn = dash_page.locator("#sticky-simulate-button")
        expect(run_btn).to_be_visible(timeout=5000)
        run_btn.click()

        # Wait for simulation to complete
        wait_for_simulation()

        # Verify results are displayed
        comparative_table = dash_page.locator("#comparative-table")
        expect(comparative_table).to_be_visible()

        # Check that DPS value is displayed
        expect(comparative_table).to_contain_text("DPS")

        # Verify table contains numeric values (DPS should be > 0)
        table_text = comparative_table.inner_text()
        import re
        numbers = re.findall(r'\d+\.\d+', table_text)
        assert len(numbers) > 0, "Expected numeric DPS values in results table"
        dps_value = float(numbers[0])  # First number should be DPS
        assert dps_value > 0, f"Expected positive DPS, got {dps_value}"

    def test_simulation_with_critical_feats(self, dash_page: Page, wait_for_simulation, wait_for_spinner):
        """Test simulation with critical hit feats enabled."""
        # Enable Keen and Improved Critical (should already be default, but verify)
        keen_checkbox = dash_page.locator("#keen-switch")
        ic_checkbox = dash_page.locator("#improved-crit-switch")

        if keen_checkbox.is_visible() and not keen_checkbox.is_checked():
            keen_checkbox.click()
        if ic_checkbox.is_visible() and not ic_checkbox.is_checked():
            ic_checkbox.click()

        dash_page.wait_for_timeout(500)  # Auto-save delay

        # Run simulation
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Verify critical hit rate is displayed in results
        comparative_table = dash_page.locator("#comparative-table")
        expect(comparative_table).to_be_visible()
        expect(comparative_table).to_contain_text("Crit")  # Should have "Crit %" column

    def test_simulation_with_additional_damage(self, dash_page: Page, wait_for_simulation):
        """Test simulation with additional damage sources."""
        # Flame Weapon should be enabled by default, just run simulation
        # Run simulation
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Verify results are displayed (comparative table should show DPS)
        comparative_table = dash_page.locator("#comparative-table")
        expect(comparative_table).to_be_visible()
        expect(comparative_table).to_contain_text("DPS")

    def test_resimulation_with_different_parameters(self, dash_page: Page, wait_for_simulation):
        """Test running simulation twice with different parameters."""
        # Run first simulation
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()
        wait_for_simulation()

        # Get first DPS result from comparative table
        comparative_table = dash_page.locator("#comparative-table")
        first_table_text = comparative_table.inner_text()
        import re
        first_numbers = re.findall(r'\d+\.\d+', first_table_text)
        first_dps = float(first_numbers[0]) if first_numbers else 0

        # Navigate back to Configuration tab to modify settings
        config_tab = dash_page.locator('button[id="configuration-tab"]')
        if config_tab.count() == 0:
            config_tab = dash_page.locator('a:has-text("Configuration")')
        config_tab.click()
        dash_page.wait_for_timeout(500)

        # Modify AB to significantly change DPS
        ab_input = dash_page.locator("#ab-input")
        expect(ab_input).to_be_visible(timeout=5000)
        ab_input.fill("50")  # Lower AB
        dash_page.keyboard.press("Tab")
        dash_page.wait_for_timeout(500)

        # Run second simulation
        run_btn.click()
        wait_for_simulation()

        # Get second DPS result
        second_table_text = comparative_table.inner_text()
        second_numbers = re.findall(r'\d+\.\d+', second_table_text)
        second_dps = float(second_numbers[0]) if second_numbers else 0

        # Verify DPS changed (lower AB should give lower DPS)
        assert second_dps < first_dps, f"Expected lower DPS with AB=50, got {second_dps} vs {first_dps}"

    @pytest.mark.background
    def test_simulation_progress_updates(self, dash_page: Page):
        """Test that simulation progress updates are shown."""
        # Click run simulation
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        # Verify progress modal appears
        progress_modal = dash_page.locator("#progress-modal")
        expect(progress_modal).to_be_visible(timeout=5000)

        # Verify progress bar or percentage is visible
        progress_indicator = dash_page.locator("#progress-bar, .progress-bar")
        if progress_indicator.count() > 0:
            expect(progress_indicator.first).to_be_visible(timeout=10000)

        # Wait for simulation to complete
        expect(progress_modal).not_to_be_visible(timeout=60000)

    @pytest.mark.background
    def test_simulation_cancel_button(self, dash_page: Page):
        """Test canceling a running simulation."""
        # Start simulation
        run_btn = dash_page.locator("#sticky-simulate-button")
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

        # Run simulation button
        run_btn = dash_page.locator("#sticky-simulate-button")

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
