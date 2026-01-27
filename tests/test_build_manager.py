"""
Unit tests for build manager UI component.

Tests the build manager UI component creation and functionality.
"""

import pytest
from dash import html
import dash_bootstrap_components as dbc

from components.build_manager import (
    get_default_build_config,
    create_default_builds,
    build_build_manager
)
from simulator.config import Config


class TestBuildManagerComponent:
    """Test build manager UI component."""

    def test_build_manager_returns_html_div(self):
        """Test that build_build_manager returns an html.Div."""
        component = build_build_manager()
        assert isinstance(component, html.Div)

    def test_component_can_be_rendered(self):
        """Test that component can be rendered without errors."""
        try:
            component = build_build_manager()
            assert component is not None
        except Exception as e:
            pytest.fail(f"Failed to create build manager component: {e}")


class TestDefaultBuilds:
    """Test default builds."""

    def test_creates_one_build(self):
        """Test that one build is created."""
        builds = create_default_builds()
        assert len(builds) == 1
        assert builds[0]['name'] == 'Build 1'

    def test_default_config_complete(self):
        """Test config completeness."""
        config = get_default_build_config()
        assert 'AB' in config
        assert 'ADDITIONAL_DAMAGE' in config
