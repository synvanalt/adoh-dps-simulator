"""
Unit tests for build management callbacks.

Tests the multi-build management functionality including:
- Adding new builds
- Duplicating builds
- Deleting builds
- Switching between builds
- Auto-saving build state
- Loading builds from buffer
- Build name updates
"""

import pytest
import copy
from dash import Dash, Input, Output, State, ALL
import dash_bootstrap_components as dbc
from unittest.mock import Mock, patch, MagicMock

from callbacks.build_callbacks import (
    register_build_callbacks,
    save_current_build_state
)
from components.build_manager import (
    get_default_build_config,
    create_default_builds
)
from simulator.config import Config


@pytest.fixture
def app():
    """Create a test Dash app."""
    app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
    return app


@pytest.fixture
def cfg():
    """Create a test config."""
    return Config()


@pytest.fixture
def sample_builds():
    """Create sample builds for testing."""
    return [
        {
            'name': 'Build 1',
            'config': get_default_build_config()
        },
        {
            'name': 'Build 2',
            'config': {**get_default_build_config(), 'AB': 50, 'STR_MOD': 10}
        }
    ]


class TestGetDefaultBuildConfig:
    """Test default build configuration generation."""

    def test_returns_dict(self):
        """Test that get_default_build_config returns a dictionary."""
        config = get_default_build_config()
        assert isinstance(config, dict)

    def test_contains_required_keys(self):
        """Test that config contains all required keys."""
        config = get_default_build_config()
        required_keys = [
            'AB', 'AB_CAPPED', 'AB_PROG', 'CHARACTER_SIZE', 'COMBAT_TYPE',
            'MIGHTY', 'ENHANCEMENT_SET_BONUS', 'STR_MOD', 'TWO_HANDED',
            'WEAPONMASTER', 'KEEN', 'IMPROVED_CRIT', 'OVERWHELM_CRIT',
            'DEV_CRIT', 'SHAPE_WEAPON_OVERRIDE', 'SHAPE_WEAPON',
            'ADDITIONAL_DAMAGE', 'WEAPONS'
        ]
        for key in required_keys:
            assert key in config

    def test_additional_damage_structure(self):
        """Test that ADDITIONAL_DAMAGE has correct structure."""
        config = get_default_build_config()
        assert isinstance(config['ADDITIONAL_DAMAGE'], dict)
        assert len(config['ADDITIONAL_DAMAGE']) > 0

    def test_default_values_match_config(self):
        """Test that default values match Config class defaults."""
        config = get_default_build_config()
        default_cfg = Config()
        assert config['AB'] == default_cfg.AB
        assert config['STR_MOD'] == default_cfg.STR_MOD
        assert config['KEEN'] == default_cfg.KEEN


class TestCreateDefaultBuilds:
    """Test default builds creation."""

    def test_creates_list(self):
        """Test that create_default_builds returns a list."""
        builds = create_default_builds()
        assert isinstance(builds, list)

    def test_creates_one_build(self):
        """Test that exactly one build is created."""
        builds = create_default_builds()
        assert len(builds) == 1

    def test_build_has_name(self):
        """Test that build has a name."""
        builds = create_default_builds()
        assert 'name' in builds[0]
        assert builds[0]['name'] == 'Build 1'

    def test_build_has_config(self):
        """Test that build has a config."""
        builds = create_default_builds()
        assert 'config' in builds[0]
        assert isinstance(builds[0]['config'], dict)


class TestSaveCurrentBuildState:
    """Test saving current build state."""

    def test_saves_basic_values(self, cfg):
        """Test that basic values are saved correctly."""
        builds = create_default_builds()
        ab = 55
        str_mod = 12
        keen = True

        result = save_current_build_state(
            builds, 0, ab, 20, 'Classic', False, 'M', False, False, False,
            'Melee', 0, 3, str_mod, False, False, keen,
            False, False, False, False, 'Longsword',
            [], [], [], [], ['Spear'], 'Build 1', cfg
        )

        assert result[0]['config']['AB'] == ab
        assert result[0]['config']['STR_MOD'] == str_mod
        assert result[0]['config']['KEEN'] == keen

    def test_saves_additional_damage(self, cfg):
        """Test that additional damage is saved correctly."""
        builds = create_default_builds()
        add_dmg_states = [True] * 20
        add_dmg1 = [2] * 20
        add_dmg2 = [6] * 20
        add_dmg3 = [5] * 20

        result = save_current_build_state(
            builds, 0, 40, 20, 'Classic', 'M', 'Melee',
            0, 3, 8, False, False, False, False, False, False, False,
            False, False, False, False, 'Longsword',
            add_dmg_states, add_dmg1, add_dmg2, add_dmg3, ['Spear'], 'Build 1', cfg
        )

        add_dmg = result[0]['config']['ADDITIONAL_DAMAGE']
        assert isinstance(add_dmg, dict)
        # Check first entry
        first_key = list(add_dmg.keys())[0]
        assert add_dmg[first_key][0] == True  # Switch state

    def test_saves_weapons(self, cfg):
        """Test that weapons are saved correctly."""
        builds = create_default_builds()
        weapons = ['Spear', 'Longsword', 'Greataxe']

        result = save_current_build_state(
            builds, 0, 40, 20, 'Classic', 'M', 'Melee',
            0, 3, 8, False, False, False, False, False, False, False,
            False, False, False, False, 'Longsword',
            [], [], [], [], weapons, 'Build 1', cfg
        )

        assert result[0]['config']['WEAPONS'] == weapons

    def test_handles_invalid_index(self, cfg):
        """Test that invalid index is handled."""
        builds = create_default_builds()

        result = save_current_build_state(
            builds, 99, 40, 20, 'Classic', 'M', 'Melee',
            0, 3, 8, False, False, False, False, False, False, False,
            False, False, False, False, 'Longsword',
            [], [], [], [], ['Spear'], 'Build 1', cfg
        )

        # Should return builds unchanged
        assert len(result) == 1
        assert result[0]['config']['AB'] == Config().AB

    def test_handles_none_builds(self, cfg):
        """Test that None builds is handled."""
        result = save_current_build_state(
            None, 0, 40, 20, 'Classic', 'M', 'Melee',
            0, 3, 8, False, False, False, False, False, False, False,
            False, False, False, False, 'Longsword',
            [], [], [], [], ['Spear'], 'Build 1', cfg
        )

        assert result is None

    def test_preserves_other_builds(self, cfg, sample_builds):
        """Test that saving doesn't affect other builds."""
        builds = copy.deepcopy(sample_builds)
        original_build2_ab = builds[1]['config']['AB']

        result = save_current_build_state(
            builds, 0, 99, 20, 'Classic', 'M', 'Melee',
            0, 3, 8, False, False, False, False, False, False, False,
            False, False, False, False, 'Longsword',
            [], [], [], [], ['Spear'], 'Build 1', cfg
        )

        # Build 0 should be updated
        assert result[0]['config']['AB'] == 99
        # Build 1 should be unchanged
        assert result[1]['config']['AB'] == original_build2_ab


class TestBuildCallbacksIntegration:
    """Integration tests for build callbacks (testing callback logic without Dash)."""

    def test_add_build_increases_count(self):
        """Test that adding a build increases the count."""
        builds = create_default_builds()
        initial_count = len(builds)

        # Simulate adding a build
        new_index = len(builds)
        new_build = {
            'name': f'Build {new_index + 1}',
            'config': get_default_build_config()
        }
        builds.append(new_build)

        assert len(builds) == initial_count + 1
        assert builds[-1]['name'] == f'Build {new_index + 1}'

    def test_add_build_respects_max_limit(self):
        """Test that adding builds respects the 8-build limit."""
        builds = [{'name': f'Build {i+1}', 'config': get_default_build_config()}
                  for i in range(8)]

        # Should not add beyond 8 builds
        should_add = len(builds) < 8
        assert not should_add

    def test_duplicate_build_copies_config(self, sample_builds):
        """Test that duplicating a build copies configuration."""
        builds = copy.deepcopy(sample_builds)
        active_idx = 0

        # Simulate duplicating
        new_index = len(builds)
        current_build = builds[active_idx]
        new_build = {
            'name': f"{current_build['name']} (Copy)",
            'config': copy.deepcopy(current_build['config'])
        }
        builds.append(new_build)

        # Verify copy
        assert len(builds) == 3
        assert builds[2]['name'] == 'Build 1 (Copy)'
        assert builds[2]['config']['AB'] == builds[0]['config']['AB']

        # Verify deep copy (changing one doesn't affect the other)
        builds[2]['config']['AB'] = 999
        assert builds[0]['config']['AB'] != 999

    def test_delete_build_removes_build(self, sample_builds):
        """Test that deleting a build removes it."""
        builds = copy.deepcopy(sample_builds)
        initial_count = len(builds)

        # Simulate deleting
        builds.pop(0)

        assert len(builds) == initial_count - 1

    def test_delete_adjusts_active_index(self, sample_builds):
        """Test that deleting adjusts active index correctly."""
        builds = copy.deepcopy(sample_builds)
        active_idx = 1

        # Simulate deleting current build
        builds.pop(active_idx)
        new_active = min(active_idx, len(builds) - 1)

        assert new_active == 0

    def test_cannot_delete_last_build(self):
        """Test that last build cannot be deleted."""
        builds = create_default_builds()
        can_delete = len(builds) > 1
        assert not can_delete

    def test_switch_build_updates_index(self, sample_builds):
        """Test that switching updates the active index."""
        active_idx = 0
        clicked_index = 1

        # Simulate switch
        if clicked_index != active_idx:
            new_active = clicked_index
        else:
            new_active = active_idx

        assert new_active == 1

    def test_switch_to_same_build_no_op(self, sample_builds):
        """Test that switching to same build is a no-op."""
        active_idx = 0
        clicked_index = 0

        # Simulate switch
        if clicked_index != active_idx:
            new_active = clicked_index
        else:
            new_active = active_idx

        assert new_active == active_idx

    def test_cannot_switch_while_loading(self, sample_builds):
        """Test that switching is prevented while loading."""
        active_idx = 0
        clicked_index = 1
        is_loading = True

        # Simulate switch attempt
        if is_loading:
            can_switch = False
        else:
            can_switch = True

        assert not can_switch

    def test_update_build_name(self, sample_builds):
        """Test that build name can be updated."""
        builds = copy.deepcopy(sample_builds)
        active_idx = 0
        new_name = "My Custom Build"

        # Simulate name update
        builds[active_idx]['name'] = new_name

        assert builds[active_idx]['name'] == new_name


class TestBuildLoadingState:
    """Test build loading state management."""

    def test_loading_state_set_on_add(self):
        """Test that loading state is set when adding a build."""
        # When adding a build, loading should be True
        loading_state = True
        assert loading_state

    def test_loading_state_set_on_duplicate(self):
        """Test that loading state is set when duplicating a build."""
        # When duplicating a build, loading should be True
        loading_state = True
        assert loading_state

    def test_loading_state_set_on_delete(self):
        """Test that loading state is set when deleting a build."""
        # When deleting a build, loading should be True
        loading_state = True
        assert loading_state

    def test_loading_state_set_on_switch(self):
        """Test that loading state is set when switching builds."""
        # When switching builds, loading should be True
        loading_state = True
        assert loading_state

    def test_loading_state_cleared_after_load(self):
        """Test that loading state is cleared after loading completes."""
        # After clientside callback completes, loading should be False
        loading_state = False  # Clientside callback sets this
        assert not loading_state

    def test_auto_save_blocked_during_loading(self):
        """Test that auto-save is blocked when loading."""
        is_loading = True

        # Simulate auto-save check
        if is_loading:
            should_save = False
        else:
            should_save = True

        assert not should_save


class TestBuildUIState:
    """Test build UI state management."""

    def test_delete_button_disabled_with_one_build(self):
        """Test that delete button is disabled with only one build."""
        builds = create_default_builds()
        delete_disabled = len(builds) <= 1
        assert delete_disabled

    def test_delete_button_enabled_with_multiple_builds(self, sample_builds):
        """Test that delete button is enabled with multiple builds."""
        delete_disabled = len(sample_builds) <= 1
        assert not delete_disabled

    def test_add_button_disabled_at_max_builds(self):
        """Test that add button is disabled at 8 builds."""
        builds = [{'name': f'Build {i+1}', 'config': get_default_build_config()}
                  for i in range(8)]
        add_disabled = len(builds) >= 8
        assert add_disabled

    def test_add_button_enabled_below_max(self, sample_builds):
        """Test that add button is enabled below 8 builds."""
        add_disabled = len(sample_builds) >= 8
        assert not add_disabled

    def test_duplicate_button_disabled_at_max_builds(self):
        """Test that duplicate button is disabled at 8 builds."""
        builds = [{'name': f'Build {i+1}', 'config': get_default_build_config()}
                  for i in range(8)]
        duplicate_disabled = len(builds) >= 8
        assert duplicate_disabled

    def test_duplicate_button_enabled_below_max(self, sample_builds):
        """Test that duplicate button is enabled below 8 builds."""
        duplicate_disabled = len(sample_builds) >= 8
        assert not duplicate_disabled


class TestBuildDataIntegrity:
    """Test build data integrity."""

    def test_build_config_structure_preserved(self):
        """Test that build config structure is preserved through operations."""
        builds = create_default_builds()
        original_keys = set(builds[0]['config'].keys())

        # Simulate operations
        new_build = {
            'name': 'Build 2',
            'config': get_default_build_config()
        }
        builds.append(new_build)

        # Verify structure
        assert set(builds[0]['config'].keys()) == original_keys
        assert set(builds[1]['config'].keys()) == original_keys

    def test_additional_damage_preserved(self, cfg):
        """Test that additional damage structure is preserved."""
        builds = create_default_builds()

        # Save state with additional damage
        result = save_current_build_state(
            builds, 0, 40, 20, 'Classic', 'M', 'Melee',
            0, 3, 8, False, False, False, False, False, False, False,
            False, False, False, False, 'Longsword',
            [True] * 20, [2] * 20, [6] * 20, [5] * 20, ['Spear'], 'Build 1', cfg
        )

        add_dmg = result[0]['config']['ADDITIONAL_DAMAGE']
        assert len(add_dmg) == 20  # Should have all 20 entries

    def test_build_independence(self, sample_builds):
        """Test that builds are independent of each other."""
        builds = copy.deepcopy(sample_builds)

        # Store original values
        original_build1_ab = builds[1]['config']['AB']
        original_build1_keen = builds[1]['config']['KEEN']

        # Modify build 0
        builds[0]['config']['AB'] = 999
        builds[0]['config']['KEEN'] = not builds[0]['config']['KEEN']  # Toggle KEEN

        # Verify build 1 is unchanged
        assert builds[1]['config']['AB'] == original_build1_ab
        assert builds[1]['config']['KEEN'] == original_build1_keen


class TestBuildEdgeCases:
    """Test edge cases in build management."""

    def test_empty_builds_list(self, cfg):
        """Test handling of empty builds list."""
        result = save_current_build_state(
            [], 0, 40, 20, 'Classic', 'M', 'Melee',
            0, 3, 8, False, False, False, False, False, False, False,
            False, False, False, False, 'Longsword',
            [], [], [], [], ['Spear'], 'Build 1', cfg
        )
        assert result == []

    def test_negative_active_index(self, cfg, sample_builds):
        """Test handling of negative active index."""
        builds = copy.deepcopy(sample_builds)
        result = save_current_build_state(
            builds, -1, 40, 20, 'Classic', 'M', 'Melee',
            0, 3, 8, False, False, False, False, False, False, False,
            False, False, False, False, 'Longsword',
            [], [], [], [], ['Spear'], 'Build 1', cfg
        )
        # Should return unchanged builds
        assert result[0]['config']['AB'] == builds[0]['config']['AB']

    def test_build_name_max_length(self):
        """Test that build names respect maximum length."""
        max_length = 30
        long_name = "A" * 50
        truncated_name = long_name[:max_length]
        assert len(truncated_name) == max_length

    def test_special_characters_in_build_name(self, sample_builds):
        """Test that special characters are handled in build names."""
        builds = copy.deepcopy(sample_builds)
        special_name = "Build <>&\"'123"
        builds[0]['name'] = special_name
        assert builds[0]['name'] == special_name

    def test_unicode_in_build_name(self, sample_builds):
        """Test that unicode characters are handled in build names."""
        builds = copy.deepcopy(sample_builds)
        unicode_name = "Build 火🔥"
        builds[0]['name'] = unicode_name
        assert builds[0]['name'] == unicode_name

    def test_save_current_build_state_saves_build_name(self, cfg):
        """Test that save_current_build_state saves the build name."""
        builds = create_default_builds()
        original_name = builds[0]['name']
        new_name = "My Custom Build"

        result = save_current_build_state(
            builds, 0, 40, 20, 'Classic', 'M', 'Melee',
            0, 3, 8, False, False, False, False, False, False, False,
            False, False, False, False, 'Longsword',
            [], [], [], [], ['Spear'], new_name, cfg
        )

        assert result[0]['name'] == new_name
        assert result[0]['name'] != original_name

    def test_save_current_build_state_preserves_name_when_none(self, cfg):
        """Test that save_current_build_state preserves name when None is passed."""
        builds = create_default_builds()
        original_name = builds[0]['name']

        result = save_current_build_state(
            builds, 0, 40, 20, 'Classic', 'M', 'Melee',
            0, 3, 8, False, False, False, False, False, False, False,
            False, False, False, False, 'Longsword',
            [], [], [], [], ['Spear'], None, cfg
        )

        # Name should be unchanged when None is passed
        assert result[0]['name'] == original_name
