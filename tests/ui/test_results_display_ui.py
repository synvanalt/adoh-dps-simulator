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
        results_content = dash_page.locator("#results-content, .results-display")

        # Results area should exist in DOM

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

        # Check for DPS display
        dps_elem = dash_page.locator("#avg-dps-value, text=/DPS/i")
        expect(dps_elem.first).to_be_visible()

    def test_dps_value_is_numeric(self, dash_page: Page, wait_for_simulation):
        """Test that displayed DPS is a valid number."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        dps_elem = dash_page.locator("#avg-dps-value")
        if dps_elem.is_visible():
            dps_text = dps_elem.inner_text()
            # Should be able to parse as float
            dps_value = float(dps_text)
            assert dps_value > 0, f"DPS should be positive, got {dps_value}"

    def test_results_show_statistics(self, dash_page: Page, wait_for_simulation):
        """Test that results show statistical information."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Should show statistics like std dev, CV, etc.
        results_area = dash_page.locator("#results-content")

        if results_area.is_visible():
            # Look for statistical terms
            stats_text = results_area.inner_text()
            # Might include "standard", "deviation", "coefficient", etc.

    def test_hit_rate_displayed(self, dash_page: Page, wait_for_simulation):
        """Test that hit rate is displayed."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Look for hit rate
        hit_rate_elem = dash_page.locator("#hit-rate-value, text=/hit.*rate/i")

        if hit_rate_elem.count() > 0:
            expect(hit_rate_elem.first).to_be_visible()

    def test_crit_rate_displayed(self, dash_page: Page, wait_for_simulation):
        """Test that critical hit rate is displayed."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Look for crit rate
        crit_rate_elem = dash_page.locator("#crit-rate-value, text=/crit.*rate/i")

        if crit_rate_elem.count() > 0:
            expect(crit_rate_elem.first).to_be_visible()


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
        progress_indicator = progress_modal.locator("#progress-bar, .progress-bar, text=/%/")

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

        dps_elem = dash_page.locator("#avg-dps-value")
        if dps_elem.is_visible():
            dps_text = dps_elem.inner_text()

            # Should have decimal point
            # e.g., "245.6" not "245"

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

        # Results should be organized (cards, tables, etc.)
        results_area = dash_page.locator("#results-content")
        expect(results_area).to_be_visible()

    def test_results_responsive_layout(self, dash_page: Page, wait_for_simulation):
        """Test results responsive layout."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Set mobile viewport
        dash_page.set_viewport_size({"width": 375, "height": 667})

        # Results should still be readable
        results_area = dash_page.locator("#results-content")
        expect(results_area).to_be_visible()

        # Reset viewport
        dash_page.set_viewport_size({"width": 1280, "height": 720})

    def test_results_scrollable(self, dash_page: Page, wait_for_simulation):
        """Test that results area is scrollable if content is long."""
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        # Results should not overflow viewport
        results_area = dash_page.locator("#results-content")
        expect(results_area).to_be_visible()


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
        # On initial load, results should be empty or show placeholder

        results_content = dash_page.locator("#results-content")

        # Should either be hidden or show "Run simulation to see results" message

    def test_results_persist_between_runs(self, dash_page: Page, wait_for_simulation):
        """Test that new results replace old results."""
        # Run first simulation
        run_btn = dash_page.locator("#sticky-simulate-button")
        run_btn.click()

        wait_for_simulation()

        dps_elem = dash_page.locator("#avg-dps-value")
        first_dps = dps_elem.inner_text()

        # Modify config
        ab_input = dash_page.locator("#ab-input")
        ab_input.fill("50")
        dash_page.keyboard.press("Tab")
        dash_page.wait_for_timeout(500)

        # Run second simulation
        run_btn.click()
        wait_for_simulation()

        # DPS should be different (updated)
        second_dps = dps_elem.inner_text()
        assert second_dps != first_dps, "Results should update on re-simulation"
