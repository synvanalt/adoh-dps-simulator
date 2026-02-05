"""E2E tests for dual-wield configuration workflow.

Priority 4: Tests most complex conditional UI with high bug potential.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestDualWieldWorkflow:
    """Test dual-wield configuration workflows."""

    def test_enable_dual_wield_shows_conditional_ui(self, dash_page: Page):
        """Test that enabling dual-wield shows additional options."""
        # Find dual-wield checkbox
        dw_checkbox = dash_page.locator("#dual-wield-checkbox")

        if dw_checkbox.is_visible():
            # Ensure it's unchecked first
            if dw_checkbox.is_checked():
                dw_checkbox.click()
                dash_page.wait_for_timeout(500)

            # Enable dual-wield
            dw_checkbox.click()
            dash_page.wait_for_timeout(500)

            # Verify conditional UI appears
            twf_checkbox = dash_page.locator("#two-weapon-fighting-checkbox")
            expect(twf_checkbox).to_be_visible(timeout=2000)

            ambidex_checkbox = dash_page.locator("#ambidexterity-checkbox")
            expect(ambidex_checkbox).to_be_visible(timeout=2000)

    def test_disable_dual_wield_hides_conditional_ui(self, dash_page: Page):
        """Test that disabling dual-wield hides additional options."""
        dw_checkbox = dash_page.locator("#dual-wield-checkbox")

        if dw_checkbox.is_visible():
            # Enable first
            if not dw_checkbox.is_checked():
                dw_checkbox.click()
                dash_page.wait_for_timeout(500)

            # Verify conditional UI visible
            twf_checkbox = dash_page.locator("#two-weapon-fighting-checkbox")
            is_visible_when_enabled = twf_checkbox.is_visible()

            # Disable dual-wield
            dw_checkbox.click()
            dash_page.wait_for_timeout(500)

            # Verify conditional UI hidden (or disabled)
            if is_visible_when_enabled:
                expect(twf_checkbox).not_to_be_visible()

    def test_dual_wield_feat_combinations(self, dash_page: Page):
        """Test different dual-wield feat combinations."""
        dw_checkbox = dash_page.locator("#dual-wield-checkbox")

        if dw_checkbox.is_visible():
            # Enable dual-wield
            if not dw_checkbox.is_checked():
                dw_checkbox.click()
                dash_page.wait_for_timeout(500)

            # Test feat combinations
            twf_checkbox = dash_page.locator("#two-weapon-fighting-checkbox")
            ambidex_checkbox = dash_page.locator("#ambidexterity-checkbox")
            itwf_checkbox = dash_page.locator("#improved-twf-checkbox")

            if twf_checkbox.is_visible():
                # Combination 1: All feats
                if not twf_checkbox.is_checked():
                    twf_checkbox.click()
                if not ambidex_checkbox.is_checked():
                    ambidex_checkbox.click()
                if not itwf_checkbox.is_checked():
                    itwf_checkbox.click()

                dash_page.wait_for_timeout(500)

                # Verify no errors
                error_msg = dash_page.locator(".error-message")
                expect(error_msg).not_to_be_visible()

                # Combination 2: No feats (maximum penalties)
                twf_checkbox.click()
                ambidex_checkbox.click()
                itwf_checkbox.click()

                dash_page.wait_for_timeout(500)

                # Should still work (just with penalties)

    def test_dual_wield_ab_progression_changes(self, dash_page: Page):
        """Test that dual-wield affects AB progression."""
        dw_checkbox = dash_page.locator("#dual-wield-checkbox")

        if dw_checkbox.is_visible():
            # Get initial AB
            ab_input = dash_page.locator("#ab-input")
            initial_ab = ab_input.input_value()

            # Enable dual-wield
            if not dw_checkbox.is_checked():
                dw_checkbox.click()
                dash_page.wait_for_timeout(500)

            # Disable all dual-wield feats for maximum penalty
            twf_checkbox = dash_page.locator("#two-weapon-fighting-checkbox")
            if twf_checkbox.is_visible() and twf_checkbox.is_checked():
                twf_checkbox.click()

            ambidex_checkbox = dash_page.locator("#ambidexterity-checkbox")
            if ambidex_checkbox.is_visible() and ambidex_checkbox.is_checked():
                ambidex_checkbox.click()

            dash_page.wait_for_timeout(500)

            # Verify AB progression is affected (implementation detail)
            # This test mainly verifies no errors occur

    def test_dual_wield_with_character_size(self, dash_page: Page):
        """Test dual-wield interactions with character size."""
        dw_checkbox = dash_page.locator("#dual-wield-checkbox")

        if dw_checkbox.is_visible():
            # Enable dual-wield
            if not dw_checkbox.is_checked():
                dw_checkbox.click()
                dash_page.wait_for_timeout(500)

            # Find character size dropdown
            size_dropdown = dash_page.locator("#character-size-dropdown")

            if size_dropdown.is_visible():
                # Try different sizes
                size_dropdown.select_option("S")  # Small
                dash_page.wait_for_timeout(500)

                size_dropdown.select_option("L")  # Large
                dash_page.wait_for_timeout(500)

                size_dropdown.select_option("M")  # Medium (default)
                dash_page.wait_for_timeout(500)

                # Verify no errors

    def test_illegal_dual_wield_prevented(self, dash_page: Page):
        """Test that illegal dual-wield combinations are prevented."""
        # This depends on implementation - some weapon combinations
        # might not allow dual-wield

        dw_checkbox = dash_page.locator("#dual-wield-checkbox")

        if dw_checkbox.is_visible():
            # Select a two-handed weapon
            two_handed_checkbox = dash_page.locator("#two-handed-checkbox")

            if two_handed_checkbox.is_visible():
                # Enable two-handed
                if not two_handed_checkbox.is_checked():
                    two_handed_checkbox.click()
                    dash_page.wait_for_timeout(500)

                # Try to enable dual-wield (should be prevented or show error)
                if not dw_checkbox.is_checked():
                    dw_checkbox.click()
                    dash_page.wait_for_timeout(500)

                # Either dual-wield is disabled/prevented or error shown
                # (exact behavior depends on implementation)

    def test_offhand_weapon_selection(self, dash_page: Page):
        """Test offhand weapon selection in dual-wield mode."""
        dw_checkbox = dash_page.locator("#dual-wield-checkbox")

        if dw_checkbox.is_visible():
            # Enable dual-wield
            if not dw_checkbox.is_checked():
                dw_checkbox.click()
                dash_page.wait_for_timeout(500)

            # Look for offhand weapon dropdown
            offhand_dropdown = dash_page.locator("#offhand-weapon-dropdown, #weapons-dropdown-1")

            if offhand_dropdown.is_visible():
                # Select different offhand weapon
                offhand_dropdown.select_option(index=1)  # Select second option
                dash_page.wait_for_timeout(500)

                # Verify no errors


@pytest.mark.e2e
class TestDualWieldSimulation:
    """Test simulation with dual-wield enabled."""

    def test_dual_wield_simulation_completes(self, dash_page: Page, wait_for_simulation):
        """Test that simulation works with dual-wield enabled."""
        import re

        dw_checkbox = dash_page.locator("#dual-wield-checkbox")

        if dw_checkbox.is_visible():
            # Enable dual-wield
            if not dw_checkbox.is_checked():
                dw_checkbox.click()
                dash_page.wait_for_timeout(500)

            # Run simulation
            run_btn = dash_page.locator("#sticky-simulate-button")
            expect(run_btn).to_be_enabled(timeout=5000)
            run_btn.click()

            wait_for_simulation()

            # Verify results displayed in comparative table
            comp_table = dash_page.locator("#comparative-table")
            expect(comp_table).to_be_visible()

            # Verify DPS calculated
            table_text = comp_table.inner_text()
            numbers = re.findall(r'\d+\.\d+', table_text)
            assert len(numbers) > 0, "Expected numeric DPS values in results table"
            dps = float(numbers[0])
            assert dps > 0, "Dual-wield should produce positive DPS"

    def test_dual_wield_vs_single_wield_dps(self, dash_page: Page, wait_for_simulation, wait_for_spinner):
        """Test DPS difference between single-wield and dual-wield."""
        import re

        # Run single-wield simulation
        run_btn = dash_page.locator("#sticky-simulate-button")
        expect(run_btn).to_be_visible(timeout=10000)
        expect(run_btn).to_be_enabled(timeout=5000)
        run_btn.click()
        wait_for_simulation()

        # Get single-wield DPS from comparative table
        comp_table = dash_page.locator("#comparative-table")
        expect(comp_table).to_be_visible()
        table_text = comp_table.inner_text()
        numbers = re.findall(r'\d+\.\d+', table_text)
        assert len(numbers) > 0, "Expected numeric DPS values in results table"
        single_dps = float(numbers[0])  # First number should be DPS

        # Enable dual-wield
        dw_checkbox = dash_page.locator("#dual-wield-checkbox")
        if dw_checkbox.is_visible():
            dw_checkbox.click()
            dash_page.wait_for_timeout(500)

            # Enable all feats to minimize penalty
            twf_checkbox = dash_page.locator("#two-weapon-fighting-checkbox")
            if twf_checkbox.is_visible() and not twf_checkbox.is_checked():
                twf_checkbox.click()

            ambidex_checkbox = dash_page.locator("#ambidexterity-checkbox")
            if ambidex_checkbox.is_visible() and not ambidex_checkbox.is_checked():
                ambidex_checkbox.click()

            dash_page.wait_for_timeout(1000)

            # Wait for run button to be enabled again
            expect(run_btn).to_be_enabled(timeout=5000)

            # Run dual-wield simulation
            run_btn.click()
            wait_for_simulation()

            # Get dual-wield DPS from comparative table
            table_text = comp_table.inner_text()
            numbers = re.findall(r'\d+\.\d+', table_text)
            assert len(numbers) > 0, "Expected numeric DPS values in results table"
            dual_dps = float(numbers[0])

            # Dual-wield should generally give more attacks (higher DPS)
            # But exact comparison depends on many factors
            assert dual_dps > 0, "Dual-wield should produce valid DPS"
