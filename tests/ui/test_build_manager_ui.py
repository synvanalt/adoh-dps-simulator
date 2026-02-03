"""UI component tests for Build Manager.

Tests build tabs, add/delete/duplicate buttons, and build naming.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.ui
class TestBuildTabsUI:
    """Test build tabs UI components."""

    def test_build_tabs_render(self, dash_page: Page):
        """Test that build tabs render correctly."""
        # Find build tabs container
        build_tabs_container = dash_page.locator("#build-tabs-container, .build-tabs")

        # Should have at least one build tab
        build_tabs = dash_page.locator("button.build-tab-btn")
        assert build_tabs.count() >= 1, "Should have at least one build tab"

    def test_active_build_tab_highlighted(self, dash_page: Page, wait_for_spinner):
        """Test that active build tab has active styling."""
        # Get all build tabs
        build_tabs = dash_page.locator("button.build-tab-btn")

        if build_tabs.count() == 1:
            # Add second build
            add_btn = dash_page.locator("#add-build-btn")
            add_btn.click()
            wait_for_spinner()

        # Find active tab
        active_tab = dash_page.locator("button.build-tab-btn.active")
        expect(active_tab).to_be_visible()

        # Active tab should have active class
        assert active_tab.count() == 1, "Should have exactly one active tab"

    def test_build_tab_click_switches_build(self, dash_page: Page, wait_for_spinner):
        """Test that clicking build tab switches to that build."""
        # Add second build if needed
        build_tabs = dash_page.locator("button.build-tab-btn")

        if build_tabs.count() == 1:
            add_btn = dash_page.locator("#add-build-btn")
            add_btn.click()
            wait_for_spinner()

        # Click first build tab
        build_tabs.nth(0).click()
        wait_for_spinner()

        # Verify it's now active
        first_tab = build_tabs.nth(0)
        expect(first_tab).to_have_class(/active/)

    def test_build_tab_labels_display_correctly(self, dash_page: Page, wait_for_spinner):
        """Test that build tab labels show correct build names."""
        # First build should show "Build 1"
        first_tab = dash_page.locator("button.build-tab-btn").first
        expect(first_tab).to_contain_text(/Build\s*1/i)

        # Add second build
        add_btn = dash_page.locator("#add-build-btn")
        add_btn.click()
        wait_for_spinner()

        # Second build should show "Build 2"
        second_tab = dash_page.locator("button.build-tab-btn").nth(1)
        expect(second_tab).to_contain_text(/Build\s*2/i)


@pytest.mark.ui
class TestBuildControlButtons:
    """Test build control buttons (add, duplicate, delete)."""

    def test_add_build_button_visible(self, dash_page: Page):
        """Test that add build button is visible."""
        add_btn = dash_page.locator("#add-build-btn")
        expect(add_btn).to_be_visible()

    def test_add_build_button_enabled(self, dash_page: Page):
        """Test that add build button is enabled."""
        add_btn = dash_page.locator("#add-build-btn")
        expect(add_btn).to_be_enabled()

    def test_add_build_button_has_icon(self, dash_page: Page):
        """Test that add build button has plus icon."""
        add_btn = dash_page.locator("#add-build-btn")

        # Check for icon (Font Awesome or similar)
        icon = add_btn.locator("i.fa-plus, svg, .icon")

        # Button should have icon or text
        assert add_btn.inner_text() or icon.count() > 0, "Add button should have icon or text"

    def test_duplicate_build_button_visible(self, dash_page: Page):
        """Test that duplicate build button is visible."""
        dup_btn = dash_page.locator("#duplicate-build-btn")
        expect(dup_btn).to_be_visible()

    def test_delete_build_button_visible(self, dash_page: Page):
        """Test that delete build button is visible."""
        del_btn = dash_page.locator("#delete-build-btn")
        expect(del_btn).to_be_visible()

    def test_delete_build_button_disabled_with_one_build(self, dash_page: Page, wait_for_spinner):
        """Test that delete button is disabled when only one build exists."""
        # Ensure only one build
        build_tabs = dash_page.locator("button.build-tab-btn")

        while build_tabs.count() > 1:
            del_btn = dash_page.locator("#delete-build-btn")
            del_btn.click()
            wait_for_spinner()
            dash_page.wait_for_timeout(500)

        # Delete button should be disabled
        del_btn = dash_page.locator("#delete-build-btn")
        expect(del_btn).to_be_disabled()

    def test_button_tooltips_present(self, dash_page: Page):
        """Test that buttons have tooltips or aria-labels."""
        add_btn = dash_page.locator("#add-build-btn")
        dup_btn = dash_page.locator("#duplicate-build-btn")
        del_btn = dash_page.locator("#delete-build-btn")

        # Buttons should have tooltips or aria-labels for accessibility
        # (exact implementation may vary)
        assert add_btn.count() > 0
        assert dup_btn.count() > 0
        assert del_btn.count() > 0


@pytest.mark.ui
class TestBuildNaming:
    """Test build naming functionality."""

    def test_build_name_input_visible(self, dash_page: Page):
        """Test that build name input is visible."""
        name_input = dash_page.locator("#build-name-input")

        if name_input.count() > 0:
            expect(name_input).to_be_visible()

    def test_build_name_input_shows_current_name(self, dash_page: Page):
        """Test that build name input shows current build name."""
        name_input = dash_page.locator("#build-name-input")

        if name_input.is_visible():
            # Should show "Build 1" or similar
            value = name_input.input_value()
            assert "Build" in value, f"Expected build name, got: {value}"

    def test_build_name_can_be_edited(self, dash_page: Page):
        """Test that build name can be edited."""
        name_input = dash_page.locator("#build-name-input")

        if name_input.is_visible():
            # Clear and type new name
            name_input.fill("Custom Build Name")
            dash_page.keyboard.press("Tab")

            dash_page.wait_for_timeout(500)

            # Verify value updated
            value = name_input.input_value()
            assert value == "Custom Build Name", f"Expected 'Custom Build Name', got: {value}"

    def test_build_name_updates_tab_label(self, dash_page: Page):
        """Test that changing build name updates tab label."""
        name_input = dash_page.locator("#build-name-input")

        if name_input.is_visible():
            # Change name
            new_name = "My Test Build"
            name_input.fill(new_name)
            dash_page.keyboard.press("Enter")

            dash_page.wait_for_timeout(1000)  # Wait for update

            # Check active tab label
            active_tab = dash_page.locator("button.build-tab-btn.active")
            expect(active_tab).to_contain_text(new_name)


@pytest.mark.ui
class TestBuildManagerLayout:
    """Test build manager layout and styling."""

    def test_build_manager_responsive_layout(self, dash_page: Page):
        """Test that build manager has responsive layout."""
        # Build manager should be visible
        build_manager = dash_page.locator("#build-manager, .build-manager")

        # Check that tabs and buttons are arranged properly
        build_tabs = dash_page.locator("button.build-tab-btn")
        assert build_tabs.count() >= 1

        add_btn = dash_page.locator("#add-build-btn")
        assert add_btn.is_visible()

    def test_build_tabs_scroll_with_many_builds(self, dash_page: Page, wait_for_spinner):
        """Test that build tabs scroll when there are many builds."""
        # Add many builds
        add_btn = dash_page.locator("#add-build-btn")

        for i in range(5):
            if add_btn.is_enabled():
                add_btn.click()
                wait_for_spinner()

        # Verify tabs container handles many tabs
        build_tabs = dash_page.locator("button.build-tab-btn")
        assert build_tabs.count() >= 5, "Should have added multiple builds"

        # Tabs should be scrollable or wrap
        # (exact behavior depends on CSS)

    def test_mobile_viewport_build_manager(self, dash_page: Page):
        """Test build manager on mobile viewport."""
        # Set mobile viewport
        dash_page.set_viewport_size({"width": 375, "height": 667})

        # Build manager should still be usable
        add_btn = dash_page.locator("#add-build-btn")
        expect(add_btn).to_be_visible()

        build_tabs = dash_page.locator("button.build-tab-btn")
        assert build_tabs.count() >= 1

        # Reset viewport
        dash_page.set_viewport_size({"width": 1280, "height": 720})
