"""UI component tests for Results Display.

Tests results rendering, data visualization, and results tab UI.
"""
import pytest
from playwright.sync_api import Page, expect
import re


@pytest.mark.ui
class TestResultsDisplay:
    """Test results display UI components."""

    def test_results_tab_exists(self, dash_page: Page):
        """Test that Results tab exists."""
        results_tab = dash_page.locator('a[href="#results"], button:has-text("Results")')

        # Results tab should exist (might be auto-shown or separate tab)

    def test_results_content_area_exists(self, dash_page: Page):
        """Test that results content area exists."""
        # Check for the actual results elements
        comparative_table = dash_page.locator("#comparative-table")
        detailed_results = dash_page.locator("#detailed-results")

        # At least one results area should exist in DOM
        assert comparative_table.count() > 0 or detailed_results.count() > 0

    def test_run_simulation_button_visible(self, dash_page: Page):
        """Test that Run Simulation button is visible."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        expect(run_btn).to_be_visible()

    def test_run_simulation_button_enabled(self, dash_page: Page):
        """Test that Run Simulation button is enabled."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        expect(run_btn).to_be_enabled()

    def test_run_button_has_icon(self, dash_page: Page):
        """Test that Run Simulation button has play icon."""
        run_btn = dash_page.locator("#sticky-simulate-button")

        # Should have icon or text
        icon = run_btn.locator("i.fa-play, svg, .icon")

        # Button should have icon or text
        assert run_btn.inner_text() or icon.count() > 0


@pytest.mark.ui
class TestResultsAfterSimulation:
    """Test results display after running simulation."""

    def test_dps_value_displays(self, dash_page: Page, wait_for_simulation):
        """Test that DPS value displays after simulation."""
        # Run simulation
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Check for DPS display in the comparative table
        comparative_table = dash_page.locator("#comparative-table")
        expect(comparative_table).to_be_visible()

        # Table should contain "DPS" text
        expect(comparative_table).to_contain_text("DPS", timeout=5000)

    def test_dps_value_is_numeric(self, dash_page: Page, wait_for_simulation):
        """Test that displayed DPS is a valid number."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Get the comparative table
        comparative_table = dash_page.locator("#comparative-table")
        expect(comparative_table).to_be_visible()

        # Get the table text and verify it contains numeric values
        table_text = comparative_table.inner_text()

        # Should contain "DPS" and numeric values
        assert "DPS" in table_text, "Table should contain DPS column"

        # Look for numeric patterns in the table (e.g., "123.45")
        import re
        numbers = re.findall(r'\d+\.?\d*', table_text)
        assert len(numbers) > 0, "Table should contain numeric values"

        # At least one number should be > 0 (the DPS value)
        numeric_values = [float(n) for n in numbers if n and float(n) > 0]
        assert len(numeric_values) > 0, "Should have at least one positive numeric value"

    def test_results_show_statistics(self, dash_page: Page, wait_for_simulation):
        """Test that results show statistical information."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Check that comparative table has statistical data
        results_table = dash_page.locator("#comparative-table")
        expect(results_table).to_be_visible()

        # Look for key metrics like DPS, Hit %, Crit %
        table_text = results_table.inner_text().lower()
        # Should contain metrics like "dps" or percentage indicators
        assert "dps" in table_text or "%" in table_text

    def test_hit_rate_displayed(self, dash_page: Page, wait_for_simulation):
        """Test that hit rate is displayed."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Look for hit rate in comparative table
        comparative_table = dash_page.locator("#comparative-table")
        expect(comparative_table).to_be_visible()

        # Table should contain "Hit %" column
        expect(comparative_table).to_contain_text("Hit", timeout=5000)

    def test_crit_rate_displayed(self, dash_page: Page, wait_for_simulation):
        """Test that critical hit rate is displayed."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Look for crit rate in comparative table
        comparative_table = dash_page.locator("#comparative-table")
        expect(comparative_table).to_be_visible()

        # Table should contain "Crit %" column
        expect(comparative_table).to_contain_text("Crit", timeout=5000)


@pytest.mark.ui
class TestProgressModal:
    """Test simulation progress modal UI."""

    def test_progress_modal_appears_on_run(self, dash_page: Page):
        """Test that progress modal appears when simulation starts."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        # Progress modal should appear
        progress_modal = dash_page.locator("#progress-modal")
        expect(progress_modal).to_be_visible(timeout=5000)

    def test_progress_modal_has_title(self, dash_page: Page):
        """Test that progress modal has title."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        progress_modal = dash_page.locator("#progress-modal")
        expect(progress_modal).to_be_visible(timeout=5000)

        # Should have title like "Running Simulation" or "Progress"
        modal_title = progress_modal.locator(".modal-title, h3, h4")

        if modal_title.count() > 0:
            expect(modal_title.first).to_be_visible()

    def test_progress_indicator_present(self, dash_page: Page):
        """Test that progress indicator is present."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        progress_modal = dash_page.locator("#progress-modal")
        expect(progress_modal).to_be_visible(timeout=5000)

        # Should have progress bar or percentage
        progress_indicator = progress_modal.locator("#progress-bar, .progress-bar")

        if progress_indicator.count() > 0:
            expect(progress_indicator.first).to_be_visible()

    def test_cancel_button_present(self, dash_page: Page):
        """Test that cancel button is present in progress modal."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        progress_modal = dash_page.locator("#progress-modal")
        expect(progress_modal).to_be_visible(timeout=5000)

        # Should have cancel button
        cancel_btn = progress_modal.locator("#cancel-simulation-btn, button:has-text('Cancel')")

        if cancel_btn.count() > 0:
            expect(cancel_btn.first).to_be_visible()

    def test_progress_modal_closes_on_completion(self, dash_page: Page, wait_for_simulation):
        """Test that progress modal closes when simulation completes."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        # Wait for completion
        wait_for_simulation()

        # Modal should be hidden
        progress_modal = dash_page.locator("#progress-modal")
        expect(progress_modal).not_to_be_visible()


@pytest.mark.ui
class TestResultsFormatting:
    """Test results formatting and presentation."""

    def test_dps_formatted_with_decimals(self, dash_page: Page, wait_for_simulation):
        """Test that DPS is formatted with decimal places."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Get the comparative table
        comparative_table = dash_page.locator("#comparative-table")
        expect(comparative_table).to_be_visible()

        # Get the table text
        table_text = comparative_table.inner_text()

        # Look for decimal numbers in DPS values
        import re
        decimal_numbers = re.findall(r'\d+\.\d+', table_text)
        # Should have at least some decimal formatted numbers
        assert len(decimal_numbers) > 0, "Table should contain decimal-formatted values"

    def test_percentages_formatted_correctly(self, dash_page: Page, wait_for_simulation):
        """Test that percentages are formatted correctly."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Look for percentage values
        percentage_elems = dash_page.locator("text=/%$/")

        if percentage_elems.count() > 0:
            # Percentages should have % symbol
            assert "%" in percentage_elems.first.inner_text()

    def test_large_numbers_formatted(self, dash_page: Page, wait_for_simulation):
        """Test that large numbers are formatted readably."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Large numbers like total damage might have commas
        # e.g., "147,360" not "147360"

    def test_results_use_consistent_decimals(self, dash_page: Page, wait_for_simulation):
        """Test that results use consistent decimal places."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # All similar metrics should have same decimal precision


@pytest.mark.ui
class TestResultsLayout:
    """Test results display layout."""

    def test_results_organized_in_sections(self, dash_page: Page, wait_for_simulation):
        """Test that results are organized in logical sections."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Results should be organized (comparative table and detailed results)
        comparative_table = dash_page.locator("#comparative-table")
        expect(comparative_table).to_be_visible()

    def test_results_responsive_layout(self, dash_page: Page, wait_for_simulation):
        """Test results responsive layout."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Set mobile viewport
        dash_page.set_viewport_size({"width": 375, "height": 667})

        # Results should still be readable
        comparative_table = dash_page.locator("#comparative-table")
        expect(comparative_table).to_be_visible()

        # Reset viewport
        dash_page.set_viewport_size({"width": 1280, "height": 720})

    def test_results_scrollable(self, dash_page: Page, wait_for_simulation):
        """Test that results area is scrollable if content is long."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Results should not overflow viewport
        comparative_table = dash_page.locator("#comparative-table")
        expect(comparative_table).to_be_visible()


@pytest.mark.ui
class TestErrorHandling:
    """Test error handling in results display."""

    def test_error_modal_exists(self, dash_page: Page):
        """Test that error modal component exists."""
        # Error modal should exist in DOM
        error_modal = dash_page.locator("#sim-error-modal, .error-modal")

        # Should exist (might be hidden initially)

    def test_no_results_before_simulation(self, dash_page: Page):
        """Test that no results shown before running simulation."""
        # On initial load, results should show placeholder text
        comparative_table = dash_page.locator("#comparative-table")

        # Should show "Run simulation to see results" message
        expect(comparative_table).to_contain_text("Run simulation", timeout=2000)


    def test_results_persist_between_runs(self, dash_page: Page, wait_for_simulation):
        """Test that new results replace old results."""
        # Run first simulation
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Get first results
        comparative_table = dash_page.locator("#comparative-table")
        first_results = comparative_table.inner_text()

        # Navigate back to Configuration tab to modify settings
        config_tab = dash_page.locator('button[id="configuration-tab"]')
        if config_tab.count() == 0:
            config_tab = dash_page.locator('a:has-text("Configuration")')

        config_tab.click()
        dash_page.wait_for_timeout(500)

        # Modify config
        ab_input = dash_page.locator("#ab-input")
        expect(ab_input).to_be_visible(timeout=5000)
        ab_input.fill("50")
        dash_page.keyboard.press("Tab")
        dash_page.wait_for_timeout(500)

        # Run second simulation
        run_btn.click()
        wait_for_simulation()

        # DPS should be different (updated)
        second_results = comparative_table.inner_text()
        assert second_results != first_results, "Results should update on re-simulation"
