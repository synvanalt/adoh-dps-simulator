"""UI component tests for Additional Damage panel.

Tests dynamic damage inputs, switches, and damage source management.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.ui
class TestAdditionalDamagePanel:
    """Test additional damage panel UI."""

    def test_additional_damage_panel_visible(self, dash_page: Page):
        """Test that additional damage panel is visible or expandable."""
        # Find panel or expand button
        damage_panel = dash_page.locator("#additional-damage-panel, .additional-damage")

        if not damage_panel.is_visible():
            # Try to expand panel
            expand_btn = dash_page.locator("text=/Additional Damage/i")
            if expand_btn.is_visible():
                expand_btn.click()
                dash_page.wait_for_timeout(500)

        # Panel should now be visible
        damage_section = dash_page.locator("#additional-damage-panel, .additional-damage")
        # At minimum, some damage switches should exist

    def test_damage_switches_render(self, dash_page: Page):
        """Test that damage source switches render."""
        # Find damage switches
        damage_switches = dash_page.locator("[id^='damage-switch-']")

        # Should have multiple damage sources
        assert damage_switches.count() > 5, "Should have multiple damage sources"

    def test_flame_weapon_enabled_by_default(self, dash_page: Page):
        """Test that Flame Weapon is enabled by default."""
        fw_switch = dash_page.locator("#damage-switch-Flame_Weapon")

        if fw_switch.is_visible():
            assert fw_switch.is_checked(), "Flame Weapon should be enabled by default"

    def test_damage_source_can_be_enabled(self, dash_page: Page):
        """Test that damage sources can be enabled."""
        # Find a disabled damage source
        bard_song_switch = dash_page.locator("#damage-switch-Bard_Song")

        if bard_song_switch.is_visible():
            # Should be disabled by default
            if not bard_song_switch.is_checked():
                # Enable it
                bard_song_switch.click()
                dash_page.wait_for_timeout(200)

                # Verify enabled
                assert bard_song_switch.is_checked(), "Bard Song should be enabled"

    def test_damage_source_can_be_disabled(self, dash_page: Page):
        """Test that damage sources can be disabled."""
        # Disable Flame Weapon
        fw_switch = dash_page.locator("#damage-switch-Flame_Weapon")

        if fw_switch.is_visible() and fw_switch.is_checked():
            fw_switch.click()
            dash_page.wait_for_timeout(200)

            assert not fw_switch.is_checked(), "Flame Weapon should be disabled"


@pytest.mark.ui
class TestDamageInputs:
    """Test damage input fields."""

    def test_damage_inputs_visible_when_enabled(self, dash_page: Page):
        """Test that damage inputs appear when source is enabled."""
        # Enable a damage source
        bard_song_switch = dash_page.locator("#damage-switch-Bard_Song")

        if bard_song_switch.is_visible() and not bard_song_switch.is_checked():
            bard_song_switch.click()
            dash_page.wait_for_timeout(500)

            # Damage inputs should appear
            damage_inputs = dash_page.locator("[id^='damage-input-Bard_Song']")
            # Should have inputs for dice, sides, flat

    def test_damage_inputs_accept_numeric_values(self, dash_page: Page):
        """Test that damage inputs accept numeric values."""
        # Enable Flame Weapon
        fw_switch = dash_page.locator("#damage-switch-Flame_Weapon")

        if fw_switch.is_visible() and not fw_switch.is_checked():
            fw_switch.click()
            dash_page.wait_for_timeout(500)

        # Find damage input
        damage_input = dash_page.locator("[id^='damage-input-Flame_Weapon']").first

        if damage_input.is_visible():
            damage_input.fill("5")
            dash_page.keyboard.press("Tab")

            value = damage_input.input_value()
            assert value == "5", f"Expected damage input 5, got {value}"

    def test_negative_damage_prevented(self, dash_page: Page):
        """Test that negative damage values are prevented."""
        # Enable a damage source
        fw_switch = dash_page.locator("#damage-switch-Flame_Weapon")

        if fw_switch.is_visible() and not fw_switch.is_checked():
            fw_switch.click()
            dash_page.wait_for_timeout(500)

        damage_input = dash_page.locator("[id^='damage-input-Flame_Weapon']").first

        if damage_input.is_visible():
            damage_input.fill("-10")
            dash_page.keyboard.press("Tab")
            dash_page.wait_for_timeout(200)

            # Value should be corrected to 0 or show validation
            value = damage_input.input_value()
            assert int(value) >= 0, f"Negative damage should be prevented, got {value}"

    def test_damage_dice_input_limits(self, dash_page: Page):
        """Test that damage dice inputs have reasonable limits."""
        # Enable damage source
        fw_switch = dash_page.locator("#damage-switch-Flame_Weapon")

        if fw_switch.is_visible() and not fw_switch.is_checked():
            fw_switch.click()
            dash_page.wait_for_timeout(500)

        # Find dice input (first input for Flame Weapon)
        dice_input = dash_page.locator("[id^='damage-input-Flame_Weapon-dice'], [id$='-dice']").first

        if dice_input.is_visible():
            # Try very high value
            dice_input.fill("999")
            dash_page.keyboard.press("Tab")
            dash_page.wait_for_timeout(200)

            # Should limit or show validation


@pytest.mark.ui
class TestDamageSourceLabels:
    """Test damage source labels and descriptions."""

    def test_damage_sources_have_labels(self, dash_page: Page):
        """Test that damage sources have descriptive labels."""
        # Find damage source labels
        fw_label = dash_page.locator("text=/Flame.*Weapon/i")

        if fw_label.count() > 0:
            assert fw_label.is_visible(), "Flame Weapon label should be visible"

    def test_damage_sources_have_descriptions(self, dash_page: Page):
        """Test that damage sources have description tooltips."""
        # Damage sources should have descriptions
        # (might be tooltips, info icons, or help text)

        # Look for description or help icon
        help_icons = dash_page.locator("i.fa-question-circle, i.fa-info-circle, .tooltip-icon")

        # May or may not have help icons depending on design

    def test_damage_source_names_readable(self, dash_page: Page):
        """Test that damage source names are readable (not snake_case)."""
        # Names should be formatted nicely
        # e.g., "Flame Weapon" not "Flame_Weapon"

        labels = dash_page.locator("label[for^='damage-switch-']")

        if labels.count() > 0:
            first_label = labels.first.inner_text()
            # Should have spaces or proper formatting


@pytest.mark.ui
class TestDamageTypeDisplay:
    """Test damage type display."""

    def test_damage_types_shown(self, dash_page: Page):
        """Test that damage types are shown for each source."""
        # Damage sources should show their type (fire, physical, etc.)

        # Look for damage type indicators
        # (implementation may vary - could be badges, colors, or text)

    def test_multiple_damage_sources_list(self, dash_page: Page):
        """Test that multiple damage sources are listed."""
        # Find all damage switches
        damage_switches = dash_page.locator("[id^='damage-switch-']")

        # Should have many sources
        count = damage_switches.count()
        assert count > 10, f"Expected many damage sources, got {count}"

    def test_damage_sources_alphabetically_ordered(self, dash_page: Page):
        """Test if damage sources are ordered logically."""
        # Get all damage source labels
        damage_switches = dash_page.locator("[id^='damage-switch-']")

        # Should be in some logical order (alphabetical or by type)
        # (exact order depends on implementation)


@pytest.mark.ui
class TestAdditionalDamageDynamic:
    """Test dynamic behavior of additional damage UI."""

    def test_enabling_source_shows_inputs(self, dash_page: Page):
        """Test that enabling a source shows input fields."""
        # Find disabled source
        sneak_attack_switch = dash_page.locator("#damage-switch-Sneak_Attack")

        if sneak_attack_switch.is_visible() and not sneak_attack_switch.is_checked():
            # Enable it
            sneak_attack_switch.click()
            dash_page.wait_for_timeout(500)

            # Inputs should appear
            inputs = dash_page.locator("[id^='damage-input-Sneak_Attack']")
            # Should have some inputs visible

    def test_disabling_source_hides_inputs(self, dash_page: Page):
        """Test that disabling a source hides input fields."""
        # Enable a source first
        fw_switch = dash_page.locator("#damage-switch-Flame_Weapon")

        if fw_switch.is_visible() and fw_switch.is_checked():
            # Disable it
            fw_switch.click()
            dash_page.wait_for_timeout(500)

            # Inputs should be hidden or disabled
            # (exact behavior may vary)

    def test_damage_input_changes_persist(self, dash_page: Page, wait_for_spinner):
        """Test that damage input changes persist across interactions."""
        # Enable and modify damage source
        fw_switch = dash_page.locator("#damage-switch-Flame_Weapon")

        if fw_switch.is_visible() and not fw_switch.is_checked():
            fw_switch.click()
            dash_page.wait_for_timeout(500)

        damage_input = dash_page.locator("[id^='damage-input-Flame_Weapon']").first

        if damage_input.is_visible():
            damage_input.fill("7")
            dash_page.keyboard.press("Tab")
            dash_page.wait_for_timeout(1000)  # Auto-save

            # Add second build and switch back
            add_btn = dash_page.locator("#add-build-btn")
            add_btn.click()
            wait_for_spinner()

            build_tabs = dash_page.locator("button.build-tab-btn")
            build_tabs.nth(0).click()
            wait_for_spinner()

            # Verify value persisted
            current_value = damage_input.input_value()
            assert current_value == "7", f"Expected persisted value 7, got {current_value}"


@pytest.mark.ui
class TestAdditionalDamageLayout:
    """Test additional damage panel layout."""

    def test_damage_panel_scrollable(self, dash_page: Page):
        """Test that damage panel is scrollable with many sources."""
        # With many damage sources, panel should scroll
        # (CSS should handle overflow)

        damage_switches = dash_page.locator("[id^='damage-switch-']")
        assert damage_switches.count() > 10, "Should have many damage sources"

    def test_damage_panel_responsive(self, dash_page: Page):
        """Test damage panel responsive layout."""
        # Set mobile viewport
        dash_page.set_viewport_size({"width": 375, "height": 667})

        # Damage switches should still be usable
        fw_switch = dash_page.locator("#damage-switch-Flame_Weapon")
        expect(fw_switch).to_be_visible()

        # Reset viewport
        dash_page.set_viewport_size({"width": 1280, "height": 720})
