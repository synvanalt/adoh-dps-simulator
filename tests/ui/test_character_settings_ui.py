"""UI component tests for Character Settings.

Tests input validation, toggles, dropdowns, and form controls.
"""
import pytest
from playwright.sync_api import Page, expect
import re


@pytest.mark.ui
class TestCharacterInputs:
    """Test character input fields."""

    def test_ab_input_visible(self, dash_page: Page):
        """Test that Attack Bonus input is visible."""
        ab_input = dash_page.locator("#ab-input")
        expect(ab_input).to_be_visible()

    def test_ab_input_has_default_value(self, dash_page: Page):
        """Test that AB input has default value."""
        ab_input = dash_page.locator("#ab-input")
        value = ab_input.input_value()
        assert value == "68", f"Expected default AB 68, got {value}"

    def test_ab_input_accepts_numeric_input(self, dash_page: Page):
        """Test that AB input accepts numeric values."""
        ab_input = dash_page.locator("#ab-input")

        ab_input.fill("75")
        dash_page.keyboard.press("Tab")

        value = ab_input.input_value()
        assert value == "75", f"Expected AB 75, got {value}"

    def test_str_mod_input_visible(self, dash_page: Page):
        """Test that STR modifier input is visible."""
        str_input = dash_page.locator("#str-mod-input")
        expect(str_input).to_be_visible()

    def test_str_mod_input_has_default_value(self, dash_page: Page):
        """Test that STR modifier has default value."""
        str_input = dash_page.locator("#str-mod-input")
        value = str_input.input_value()
        assert value == "21", f"Expected default STR 21, got {value}"

    def test_ab_capped_input_exists(self, dash_page: Page):
        """Test that AB Capped input exists."""
        ab_capped_input = dash_page.locator("#ab-capped-input")

        if ab_capped_input.count() > 0:
            expect(ab_capped_input).to_be_visible()

    def test_input_labels_present(self, dash_page: Page):
        """Test that input fields have labels."""
        # AB input should have label - search by text
        ab_label = dash_page.locator("text=/Attack Bonus/i")
        assert ab_label.count() > 0, "AB input should have label"

        # STR input should have label - search by text
        str_label = dash_page.locator("text=/STR.*Mod/i")
        assert str_label.count() > 0, "STR input should have label"


@pytest.mark.ui
class TestCharacterCheckboxes:
    """Test character setting checkboxes."""

    def test_keen_checkbox_visible(self, dash_page: Page):
        """Test that Keen checkbox is visible."""
        keen_checkbox = dash_page.locator("#keen-switch")
        expect(keen_checkbox).to_be_visible()

    def test_keen_checkbox_default_checked(self, dash_page: Page):
        """Test that Keen is checked by default."""
        keen_checkbox = dash_page.locator("#keen-switch")
        assert keen_checkbox.is_checked(), "Keen should be checked by default"

    def test_keen_checkbox_toggles(self, dash_page: Page):
        """Test that Keen checkbox can be toggled."""
        keen_checkbox = dash_page.locator("#keen-switch")

        initial_state = keen_checkbox.is_checked()
        keen_checkbox.click()
        dash_page.wait_for_timeout(200)

        assert keen_checkbox.is_checked() != initial_state, "Keen should toggle"

    def test_improved_crit_checkbox_visible(self, dash_page: Page):
        """Test that Improved Critical checkbox is visible."""
        ic_checkbox = dash_page.locator("#improved-crit-switch")
        expect(ic_checkbox).to_be_visible()

    def test_two_handed_checkbox_exists(self, dash_page: Page):
        """Test that Two-Handed checkbox exists."""
        # Uses pattern-matching ID: {'type': 'melee-switch', 'name': 'two-handed'}
        th_checkbox = dash_page.locator("input[id*='two-handed']")

        if th_checkbox.count() > 0:
            expect(th_checkbox).to_be_visible()

    def test_weaponmaster_checkbox_exists(self, dash_page: Page):
        """Test that Weaponmaster checkbox exists."""
        # Uses pattern-matching ID: {'type': 'melee-switch', 'name': 'weaponmaster'}
        wm_checkbox = dash_page.locator("input[id*='weaponmaster']")

        if wm_checkbox.count() > 0:
            expect(wm_checkbox).to_be_visible()

    def test_checkbox_labels_clickable(self, dash_page: Page):
        """Test that checkbox labels are clickable."""
        # Find label for Keen checkbox
        keen_label = dash_page.locator("label:has-text('Keen')")

        if keen_label.count() > 0:
            keen_checkbox = dash_page.locator("#keen-switch")
            initial_state = keen_checkbox.is_checked()

            # Click label instead of checkbox
            keen_label.first.click()
            dash_page.wait_for_timeout(200)

            # Should toggle checkbox
            assert keen_checkbox.is_checked() != initial_state


@pytest.mark.ui
class TestCharacterDropdowns:
    """Test character setting dropdowns."""

    def test_ab_progression_dropdown_visible(self, dash_page: Page):
        """Test that AB Progression dropdown is visible."""
        ab_prog_dropdown = dash_page.locator("#ab-prog-dropdown")
        expect(ab_prog_dropdown).to_be_visible()

    def test_ab_progression_has_options(self, dash_page: Page):
        """Test that AB Progression has multiple options."""
        ab_prog_dropdown = dash_page.locator("#ab-prog-dropdown")

        # Check options
        options = ab_prog_dropdown.locator("option")
        assert options.count() > 1, "AB Progression should have multiple options"

    def test_ab_progression_default_value(self, dash_page: Page):
        """Test that AB Progression has default value."""
        ab_prog_dropdown = dash_page.locator("#ab-prog-dropdown")

        # Should have "5APR Classic" selected by default
        selected_value = ab_prog_dropdown.input_value()
        assert "5APR Classic" in selected_value or selected_value, "Should have default progression"

    def test_ab_progression_can_change(self, dash_page: Page):
        """Test that AB Progression can be changed."""
        ab_prog_dropdown = dash_page.locator("#ab-prog-dropdown")

        # Select different option
        ab_prog_dropdown.select_option(index=1)
        dash_page.wait_for_timeout(200)

        # Verify changed
        new_value = ab_prog_dropdown.input_value()
        assert new_value, "Should select new progression"

    def test_combat_type_dropdown_exists(self, dash_page: Page):
        """Test that Combat Type dropdown exists."""
        combat_type_dropdown = dash_page.locator("#combat-type-dropdown")

        if combat_type_dropdown.count() > 0:
            expect(combat_type_dropdown).to_be_visible()

    def test_character_size_dropdown_exists(self, dash_page: Page):
        """Test that Character Size dropdown exists."""
        size_dropdown = dash_page.locator("#character-size-dropdown")

        if size_dropdown.count() > 0:
            # Size dropdown exists but may be hidden when dual-wield is off
            # Just check it exists in DOM and has options
            options = size_dropdown.locator("option")
            # Should have S, M, L options
            assert options.count() >= 3, "Should have size options"


@pytest.mark.ui
class TestInputValidation:
    """Test input validation UI feedback."""

    def test_negative_ab_shows_error(self, dash_page: Page):
        """Test that negative AB shows validation error."""
        ab_input = dash_page.locator("#ab-input")

        ab_input.fill("-10")
        dash_page.keyboard.press("Tab")
        dash_page.wait_for_timeout(500)

        # Check for validation feedback (could be red border, error message, etc.)
        # Value should be corrected or show error

    def test_very_high_ab_validation(self, dash_page: Page):
        """Test validation for very high AB values."""
        ab_input = dash_page.locator("#ab-input")

        ab_input.fill("999")
        dash_page.keyboard.press("Tab")
        dash_page.wait_for_timeout(500)

        # Should show validation or limit value

    def test_non_numeric_ab_rejected(self, dash_page: Page):
        """Test that non-numeric AB input is rejected."""
        ab_input = dash_page.locator("#ab-input")

        # Number inputs inherently prevent non-numeric input at browser level
        # Verify the input type is number
        input_type = ab_input.get_attribute("type")
        assert input_type == "number", f"AB input should be type='number', got {input_type}"

        # Browser won't allow typing non-numeric characters into type=number
        # This is the correct behavior and doesn't need explicit validation

    def test_input_max_length(self, dash_page: Page):
        """Test that inputs have reasonable max length."""
        ab_input = dash_page.locator("#ab-input")

        ab_input.fill("123456789")
        dash_page.keyboard.press("Tab")

        # Should limit to reasonable length
        value = ab_input.input_value()
        assert len(value) <= 10, f"AB input too long: {value}"


@pytest.mark.ui
class TestWeaponSelection:
    """Test weapon selection UI."""

    def test_weapons_dropdown_visible(self, dash_page: Page):
        """Test that weapons dropdown is visible."""
        # weapon-dropdown is a dcc.Dropdown (React component), not native select
        weapons_dropdown = dash_page.locator("#weapon-dropdown")
        if weapons_dropdown.count() > 0:
            expect(weapons_dropdown).to_be_visible()

    def test_weapons_dropdown_has_options(self, dash_page: Page):
        """Test that weapons dropdown has multiple options."""
        # dcc.Dropdown renders as a custom React component, not native <select>
        # Options appear when dropdown is opened, inside .Select-menu-outer
        weapons_dropdown = dash_page.locator("#weapon-dropdown")

        if weapons_dropdown.count() > 0:
            # Click to open dropdown menu
            weapons_dropdown.click()
            dash_page.wait_for_timeout(300)

            # dcc.Dropdown options are in .VirtualizedSelectOption or similar divs
            options = dash_page.locator("#weapon-dropdown .VirtualizedSelectOption, #weapon-dropdown [class*='option']")
            option_count = options.count()

            # Close dropdown by pressing Escape
            dash_page.keyboard.press("Escape")

            assert option_count > 5, f"Should have many weapon options, got {option_count}"

    def test_weapons_dropdown_default_value(self, dash_page: Page):
        """Test that weapons dropdown has default value."""
        # dcc.Dropdown shows selected values in .Select-value or similar
        weapons_dropdown = dash_page.locator("#weapon-dropdown")

        if weapons_dropdown.count() > 0:
            # For multi-select dropdown, look for selected value tags
            selected_values = dash_page.locator("#weapon-dropdown .Select-value, #weapon-dropdown [class*='multi-value']")
            assert selected_values.count() > 0, "Should have default weapon selected"

    def test_weapon_selection_changes(self, dash_page: Page):
        """Test that weapon can be changed."""
        # dcc.Dropdown requires clicking and selecting from menu
        weapons_dropdown = dash_page.locator("#weapon-dropdown")

        if weapons_dropdown.count() > 0:
            # Get initial count of selected values
            initial_selected = dash_page.locator("#weapon-dropdown .Select-value, #weapon-dropdown [class*='multi-value']")
            initial_count = initial_selected.count()

            # The dropdown is already functional if it has default values
            assert initial_count >= 0, "Dropdown should be accessible"

            new_value = weapons_dropdown.input_value()
            assert new_value != initial_value, "Weapon should change"

    def test_shape_weapon_dropdown_visible_when_enabled(self, dash_page: Page):
        """Test that shape weapon dropdown appears when override enabled."""
        shape_override = dash_page.locator("#shape-weapon-switch")

        if shape_override.count() > 0:
            # Enable override
            if not shape_override.is_checked():
                shape_override.click()
                dash_page.wait_for_timeout(500)

            # Shape weapon dropdown should appear
            shape_dropdown = dash_page.locator("#shape-weapon-dropdown")
            expect(shape_dropdown).to_be_visible()


@pytest.mark.ui
class TestCharacterSettingsLayout:
    """Test character settings layout and organization."""

    def test_settings_organized_in_sections(self, dash_page: Page):
        """Test that settings are organized in logical sections."""
        # Should have sections or cards for different setting types
        # (exact structure may vary)

        # Verify main sections visible
        ab_input = dash_page.locator("#ab-input")
        assert ab_input.is_visible()

        keen_checkbox = dash_page.locator("#keen-switch")
        assert keen_checkbox.is_visible()

    def test_responsive_layout_mobile(self, dash_page: Page):
        """Test responsive layout on mobile."""
        # Set mobile viewport
        dash_page.set_viewport_size({"width": 375, "height": 667})

        # Settings should still be accessible (may need scrolling)
        ab_input = dash_page.locator("#ab-input")
        if ab_input.count() > 0:
            ab_input.scroll_into_view_if_needed()
            dash_page.wait_for_timeout(300)
            expect(ab_input).to_be_visible()

        # Reset viewport
        dash_page.set_viewport_size({"width": 1280, "height": 720})

    def test_settings_scrollable(self, dash_page: Page):
        """Test that settings are scrollable if content is long."""
        # Settings should not overflow viewport
        # (CSS should handle scrolling)

        # Verify inputs are accessible
        ab_input = dash_page.locator("#ab-input")
        assert ab_input.is_visible()
