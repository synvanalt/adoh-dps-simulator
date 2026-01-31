"""Tests for damage source resolver helper functions."""

import pytest
from simulator.damage_source_resolver import (
    calculate_avg_dmg,
    unpack_and_merge_vs_race,
    merge_enhancement_bonus,
)
from simulator.damage_roll import DamageRoll


class TestCalculateAvgDmg:
    """Test calculate_avg_dmg function."""

    def test_with_damage_roll(self):
        """Test average calculation with DamageRoll object."""
        dmg = DamageRoll(dice=2, sides=6, flat=5)
        assert calculate_avg_dmg(dmg) == 12.0  # 2*3.5 + 5

    def test_with_damage_roll_no_flat(self):
        """Test DamageRoll with zero flat bonus."""
        dmg = DamageRoll(dice=1, sides=8, flat=0)
        assert calculate_avg_dmg(dmg) == 4.5  # 1*4.5 + 0

    def test_with_legacy_list_three_elements(self):
        """Test legacy [dice, sides, flat] format."""
        dmg_list = [2, 6, 5]
        assert calculate_avg_dmg(dmg_list) == 12.0

    def test_with_legacy_list_two_elements(self):
        """Test legacy [dice, sides] format (no flat bonus)."""
        dmg_list = [1, 8]
        assert calculate_avg_dmg(dmg_list) == 4.5


class TestUnpackAndMergeVsRace:
    """Test unpack_and_merge_vs_race function."""

    def test_no_vs_race_disabled(self):
        """When vs_race is disabled, leave data unchanged except filtering."""
        data = {
            'fire': [2, 6, 0],
            'cold': [1, 8, 3],
            'enhancement': 5,
        }
        result = unpack_and_merge_vs_race(data, damage_vs_race_enabled=False)
        # Should exclude 'enhancement' key
        assert result == {'fire': [2, 6, 0], 'cold': [1, 8, 3]}

    def test_no_vs_race_key_present(self):
        """When no vs_race keys exist, return filtered dict."""
        data = {'fire': [2, 6, 0], 'cold': [1, 8, 3]}
        result = unpack_and_merge_vs_race(data, damage_vs_race_enabled=True)
        assert result == {'fire': [2, 6, 0], 'cold': [1, 8, 3]}

    def test_with_vs_race_unpacking(self):
        """Unpack vs_race dictionary into parent when enabled."""
        data = {
            'fire': [2, 6, 0],
            'vs_race_undead': {
                'fire': [4, 6, 0],  # Higher average, should replace
                'divine': [2, 8, 0],
            }
        }
        result = unpack_and_merge_vs_race(data, damage_vs_race_enabled=True)
        assert result == {'fire': [4, 6, 0], 'divine': [2, 8, 0]}

    def test_vs_race_keeps_higher_damage(self):
        """When vs_race has lower damage, keep original."""
        data = {
            'fire': [10, 10, 0],  # avg = 55
            'vs_race_undead': {
                'fire': [1, 4, 0],  # avg = 2.5, lower
            }
        }
        result = unpack_and_merge_vs_race(data, damage_vs_race_enabled=True)
        assert result == {'fire': [10, 10, 0]}

    def test_vs_race_disabled_with_vs_race_key(self):
        """When vs_race disabled, ignore vs_race keys."""
        data = {
            'fire': [2, 6, 0],
            'vs_race_undead': {
                'fire': [4, 6, 0],
            }
        }
        result = unpack_and_merge_vs_race(data, damage_vs_race_enabled=False)
        # Should only include non-vs_race keys
        assert result == {'fire': [2, 6, 0]}

    def test_vs_race_with_damage_roll_objects(self):
        """Test with DamageRoll objects instead of lists."""
        data = {
            'fire': DamageRoll(dice=2, sides=6, flat=0),
            'vs_race_undead': {
                'fire': DamageRoll(dice=4, sides=6, flat=0),  # Higher
                'divine': DamageRoll(dice=2, sides=8, flat=0),
            }
        }
        result = unpack_and_merge_vs_race(data, damage_vs_race_enabled=True)
        assert result['fire'] == DamageRoll(dice=4, sides=6, flat=0)
        assert result['divine'] == DamageRoll(dice=2, sides=8, flat=0)

    def test_vs_race_skips_enhancement_in_nested_dict(self):
        """Enhancement key inside vs_race should be skipped."""
        data = {
            'fire': [2, 6, 0],
            'vs_race_undead': {
                'fire': [4, 6, 0],
                'enhancement': 7,  # Should be skipped
            }
        }
        result = unpack_and_merge_vs_race(data, damage_vs_race_enabled=True)
        assert result == {'fire': [4, 6, 0]}
        assert 'enhancement' not in result


class TestMergeEnhancementBonus:
    """Test merge_enhancement_bonus function."""

    def test_no_conflict_adds_enhancement(self):
        """When no conflict, add enhancement damage."""
        data = {'fire': [2, 6, 0]}
        enhancement = {'slashing': DamageRoll(dice=0, sides=0, flat=5)}
        result, warning = merge_enhancement_bonus(data, enhancement)
        assert result == {
            'fire': [2, 6, 0],
            'slashing': DamageRoll(dice=0, sides=0, flat=5)
        }
        assert warning is False

    def test_conflict_enhancement_higher(self):
        """When enhancement has higher damage, replace and warn."""
        data = {'slashing': [1, 4, 0]}  # avg = 2.5
        enhancement = {'slashing': DamageRoll(dice=0, sides=0, flat=5)}  # avg = 5
        result, warning = merge_enhancement_bonus(data, enhancement)
        assert result == {'slashing': DamageRoll(dice=0, sides=0, flat=5)}
        assert warning is True

    def test_conflict_existing_higher(self):
        """When existing damage is higher, keep it and warn."""
        data = {'piercing': DamageRoll(dice=2, sides=10, flat=0)}  # avg = 11
        enhancement = {'piercing': DamageRoll(dice=0, sides=0, flat=3)}  # avg = 3
        result, warning = merge_enhancement_bonus(data, enhancement)
        assert result == {'piercing': DamageRoll(dice=2, sides=10, flat=0)}
        assert warning is True

    def test_invalid_damage_type_raises_error(self):
        """Non-physical enhancement damage type should raise ValueError."""
        data = {'fire': [2, 6, 0]}
        enhancement = {'magical': DamageRoll(dice=0, sides=0, flat=5)}
        with pytest.raises(ValueError, match="not a valid physical damage type"):
            merge_enhancement_bonus(data, enhancement)

    def test_multiple_damage_types_preserved(self):
        """Other damage types should be preserved."""
        data = {
            'fire': [2, 6, 0],
            'cold': [1, 8, 3],
            'bludgeoning': [1, 4, 0]  # avg = 2.5
        }
        enhancement = {'bludgeoning': DamageRoll(dice=0, sides=0, flat=6)}  # avg = 6
        result, warning = merge_enhancement_bonus(data, enhancement)
        assert result['fire'] == [2, 6, 0]
        assert result['cold'] == [1, 8, 3]
        assert result['bludgeoning'] == DamageRoll(dice=0, sides=0, flat=6)
        assert warning is True
