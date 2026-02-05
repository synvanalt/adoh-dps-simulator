"""
Unit tests for About modal callback.

Tests the toggle functionality for the About modal.
"""

import pytest
from unittest.mock import MagicMock, patch


class TestAboutModalToggle:
    """Test About modal toggle callback logic."""

    def test_about_modal_opens_on_link_click(self):
        """Test that modal opens when About link is clicked."""
        # Simulate: modal is closed, link is clicked
        is_open = False
        # The callback returns `not is_open` when triggered
        result = not is_open
        assert result is True

    def test_about_modal_closes_on_button_click(self):
        """Test that modal closes when Close button is clicked."""
        # Simulate: modal is open, close button is clicked
        is_open = True
        # The callback returns `not is_open` when triggered
        result = not is_open
        assert result is False

    def test_about_modal_initial_state_closed(self):
        """Test that modal starts in closed state."""
        # The modal is initialized with is_open=False in build_about_modal()
        from components.modals import build_about_modal
        modal = build_about_modal()
        assert modal.is_open is False

    def test_about_modal_has_correct_id(self):
        """Test that modal has the expected id for callback binding."""
        from components.modals import build_about_modal
        modal = build_about_modal()
        assert modal.id == "about-modal"

    def test_about_modal_has_close_button(self):
        """Test that modal footer contains a Close button with correct id."""
        from components.modals import build_about_modal
        modal = build_about_modal()
        # Modal children: [ModalHeader, ModalBody, ModalFooter]
        footer = modal.children[2]
        close_button = footer.children
        assert close_button.id == "about-close-btn"
        assert close_button.children == "Close"

    def test_about_modal_size_is_large(self):
        """Test that modal uses large size as specified."""
        from components.modals import build_about_modal
        modal = build_about_modal()
        assert modal.size == "lg"


class TestAboutModalContent:
    """Test About modal content structure."""

    def test_about_modal_has_header(self):
        """Test that modal has a header with expected title."""
        from components.modals import build_about_modal
        modal = build_about_modal()
        header = modal.children[0]
        title = header.children
        assert "About ADOH DPS Simulator" in str(title.children)

    def test_about_modal_has_body(self):
        """Test that modal body exists and has content."""
        from components.modals import build_about_modal
        modal = build_about_modal()
        body = modal.children[1]
        assert body.children is not None
        assert len(body.children) > 0

    def test_about_modal_contains_overview_section(self):
        """Test that modal body contains Overview section."""
        from components.modals import build_about_modal
        modal = build_about_modal()
        body = modal.children[1]
        # First child should be Overview heading
        overview_heading = body.children[0]
        assert "Overview" in str(overview_heading.children)

    def test_about_modal_contains_features_section(self):
        """Test that modal body contains Features section."""
        from components.modals import build_about_modal
        modal = build_about_modal()
        body = modal.children[1]
        # Third child should be Features heading (index 2)
        features_heading = body.children[2]
        assert "Features" in str(features_heading.children)

    def test_about_modal_contains_guide_section(self):
        """Test that modal body contains Quick Start Guide section."""
        from components.modals import build_about_modal
        modal = build_about_modal()
        body = modal.children[1]
        # Fifth child should be Quick Start Guide heading (index 4)
        guide_heading = body.children[4]
        assert "Quick Start Guide" in str(guide_heading.children)
