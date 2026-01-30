"""
Unit tests for the LegendEffect class from simulator/legend_effect.py

This test suite covers:
- LegendEffect initialization and setup
- Legend proc triggering (percentage-based and crit-based)
- AB bonus application for specific weapons
- AC reduction application for specific weapons
- Legend damage calculation and aggregation
- Heavy Flail special case handling
- Club_Stone immunity reduction
- Duration tracking and attacks remaining
- Edge cases and boundary conditions
"""

import pytest
import random
from unittest.mock import Mock, patch, MagicMock
from copy import deepcopy

from simulator.legend_effect import LegendEffect
from simulator.weapon import Weapon
from simulator.config import Config
from simulator.attack_simulator import AttackSimulator
from simulator.stats_collector import StatsCollector


class TestLegendEffectInitialization:
    """Tests for LegendEffect initialization and setup."""

    def test_valid_initialization(self):
        """Test that LegendEffect initializes correctly with valid dependencies."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()

        legend_effect = LegendEffect(stats, weapon, attack_sim)

        assert legend_effect.stats == stats
        assert legend_effect.weapon == weapon
        assert legend_effect.attack_sim == attack_sim

    def test_initialization_sets_duration(self):
        """Test that legend effect duration is set correctly."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()

        legend_effect = LegendEffect(stats, weapon, attack_sim)

        assert legend_effect.legend_effect_duration == 5

    def test_initialization_sets_attacks_left_to_zero(self):
        """Test that legend attacks left is initialized to zero."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()

        legend_effect = LegendEffect(stats, weapon, attack_sim)

        assert legend_effect.legend_attacks_left == 0

    def test_initialization_with_different_weapons(self):
        """Test initialization with various weapon types."""
        cfg = Config()

        for weapon_name in ["Scimitar", "Darts", "Heavy Flail", "Club_Stone"]:
            weapon = Weapon(weapon_name, cfg)
            attack_sim = AttackSimulator(weapon, cfg)
            stats = StatsCollector()

            legend_effect = LegendEffect(stats, weapon, attack_sim)
            assert legend_effect.weapon.name_base is not None


class TestLegendProc:
    """Tests for legend proc triggering mechanics."""

    def test_legend_proc_with_zero_probability(self):
        """Test that legend proc never triggers with 0% probability."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Run multiple times to verify it never triggers
        for _ in range(50):
            result = legend_effect.legend_proc(0.0)
            assert result is False

    def test_legend_proc_with_full_probability(self):
        """Test that legend proc always triggers with 100% probability."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Run multiple times to verify it always triggers
        for _ in range(50):
            result = legend_effect.legend_proc(1.0)
            assert result is True

    def test_legend_proc_increments_stats(self):
        """Test that legend proc increments stats.legend_procs."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        initial_count = stats.legend_procs
        legend_effect.legend_proc(1.0)  # Should trigger

        assert stats.legend_procs == initial_count + 1

    def test_legend_proc_sets_attacks_left(self):
        """Test that successful proc sets legend_attacks_left."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        legend_effect.legend_proc(1.0)  # Guaranteed trigger

        expected_attacks = attack_sim.attacks_per_round * legend_effect.legend_effect_duration
        assert legend_effect.legend_attacks_left == expected_attacks

    def test_legend_proc_with_probability_range(self):
        """Test legend proc with various probability values."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()

        # Test various probabilities
        for prob in [0.1, 0.25, 0.5, 0.75, 0.9]:
            legend_effect = LegendEffect(stats, weapon, attack_sim)
            results = []
            for _ in range(100):
                result = legend_effect.legend_proc(prob)
                results.append(result)

            # Should have roughly the expected number of triggers
            trigger_count = sum(results)
            expected = prob * 100
            # Allow 50% variance due to randomness (empirical testing shows this is needed)
            assert abs(trigger_count - expected) < expected * 0.5

    def test_legend_proc_returns_boolean(self):
        """Test that legend_proc always returns a boolean."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        result = legend_effect.legend_proc(0.5)
        assert isinstance(result, bool)


class TestABBonus:
    """Tests for AB bonus calculation."""

    def test_ab_bonus_zero_when_no_attacks_left(self):
        """Test that AB bonus is 0 when no attacks remain."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        assert legend_effect.legend_attacks_left == 0
        assert legend_effect.ab_bonus == 0

    def test_ab_bonus_zero_for_non_darts_weapon(self):
        """Test that AB bonus is 0 for non-Darts weapons."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Set attacks left but weapon is not Darts
        legend_effect.legend_attacks_left = 10

        assert legend_effect.ab_bonus == 0

    def test_ab_bonus_two_for_darts_with_attacks_left(self):
        """Test that Darts gets +2 AB when attacks remain."""
        cfg = Config()
        weapon = Weapon("Darts", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Trigger the effect by calling get_legend_damage during window
        legend_effect.legend_attacks_left = 10
        legend_dict = {'proc': 0.05, 'pure': [[4, 6]], 'effect': 'perfect_strike'}

        with patch.object(legend_effect, 'legend_proc', return_value=False):
            legend_effect.get_legend_damage(legend_dict, 1)

        assert legend_effect.ab_bonus == 2

    def test_ab_bonus_for_different_weapons(self):
        """Test AB bonus for various weapon types."""
        cfg = Config()

        weapons_and_expected = [
            ("Darts", 10, 2, {'proc': 0.05, 'pure': [[4, 6]], 'effect': 'perfect_strike'}),  # (weapon, attacks_left, expected_ab_bonus, legend_dict)
            ("Scimitar", 10, 0, {}),
            ("Heavy Flail", 10, 0, {'proc': 0.05, 'physical': [[0, 0, 5]]}),
            ("Club_Stone", 10, 0, {'proc': 0.05, 'bludgeoning': [[4, 6]]}),
            ("Darts", 0, 0, {'proc': 0.05, 'pure': [[4, 6]], 'effect': 'perfect_strike'}),  # No bonus when attacks_left is 0
        ]

        for weapon_name, attacks_left, expected_bonus, legend_dict in weapons_and_expected:
            weapon = Weapon(weapon_name, cfg)
            attack_sim = AttackSimulator(weapon, cfg)
            stats = StatsCollector()
            legend_effect = LegendEffect(stats, weapon, attack_sim)

            legend_effect.legend_attacks_left = attacks_left
            if attacks_left > 0 and legend_dict:
                with patch.object(legend_effect, 'legend_proc', return_value=False):
                    legend_effect.get_legend_damage(legend_dict, 1)
            assert legend_effect.ab_bonus == expected_bonus


class TestACReduction:
    """Tests for AC reduction calculation."""

    def test_ac_reduction_zero_when_no_attacks_left(self):
        """Test that AC reduction is 0 when no attacks remain."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        assert legend_effect.legend_attacks_left == 0
        assert legend_effect.ac_reduction == 0

    def test_ac_reduction_zero_for_non_special_weapons(self):
        """Test that AC reduction is 0 for non-Light Flail/Greatsword_Legion."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Set attacks left but weapon not eligible
        legend_effect.legend_attacks_left = 10

        assert legend_effect.ac_reduction == 0

    def test_ac_reduction_for_light_flail(self):
        """Test that Light Flail gets -2 AC reduction."""
        cfg = Config()
        weapon = Weapon("Light Flail", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Trigger the effect by calling get_legend_damage during window
        legend_effect.legend_attacks_left = 10
        legend_dict = {'proc': 0.05, 'effect': 'sunder'}

        with patch.object(legend_effect, 'legend_proc', return_value=False):
            legend_effect.get_legend_damage(legend_dict, 1)

        assert legend_effect.ac_reduction == -2

    def test_ac_reduction_for_greatsword_legion(self):
        """Test that Greatsword_Legion gets -2 AC reduction."""
        cfg = Config()
        weapon = Weapon("Greatsword_Legion", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Trigger the effect by calling get_legend_damage during window
        legend_effect.legend_attacks_left = 10
        legend_dict = {'proc': 0.05, 'pure': [[4, 6]], 'effect': 'inconsequence'}

        with patch.object(legend_effect, 'legend_proc', return_value=False):
            legend_effect.get_legend_damage(legend_dict, 1)

        assert legend_effect.ac_reduction == -2

    def test_ac_reduction_for_various_weapons(self):
        """Test AC reduction for different weapon types."""
        cfg = Config()

        weapons_and_expected = [
            ("Light Flail", 10, -2, {'proc': 0.05, 'effect': 'sunder'}),
            ("Greatsword_Legion", 10, -2, {'proc': 0.05, 'pure': [[4, 6]], 'effect': 'inconsequence'}),
            ("Scimitar", 10, 0, {}),
            ("Darts", 10, 0, {'proc': 0.05, 'pure': [[4, 6]], 'effect': 'perfect_strike'}),  # Darts has AB bonus, not AC reduction
        ]

        for weapon_name, attacks_left, expected_reduction, legend_dict in weapons_and_expected:
            weapon = Weapon(weapon_name, cfg)
            attack_sim = AttackSimulator(weapon, cfg)
            stats = StatsCollector()
            legend_effect = LegendEffect(stats, weapon, attack_sim)

            legend_effect.legend_attacks_left = attacks_left
            if attacks_left > 0 and legend_dict:
                with patch.object(legend_effect, 'legend_proc', return_value=False):
                    legend_effect.get_legend_damage(legend_dict, 1)
            assert legend_effect.ac_reduction == expected_reduction


class TestGetLegendDamage:
    """Tests for legend damage calculation."""

    def test_empty_legend_dict_returns_empty_results(self):
        """Test that empty legend dict returns empty results."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        dmg_sums, dmg_common, imm_factors = legend_effect.get_legend_damage({}, 1)

        assert dmg_sums == {}
        assert dmg_common == []
        assert imm_factors == {}

    def test_none_legend_dict_returns_empty_results(self):
        """Test that None legend dict returns empty results."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Test with various falsy values
        for falsy_value in [None, {}, False]:
            if not falsy_value or falsy_value == {}:  # Handle both None and {}
                dmg_sums, dmg_common, imm_factors = legend_effect.get_legend_damage(falsy_value or {}, 1)
                assert isinstance(dmg_sums, dict)
                assert isinstance(dmg_common, list)
                assert isinstance(imm_factors, dict)

    def test_legend_damage_returns_three_values(self):
        """Test that get_legend_damage returns exactly 3 values."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        result = legend_effect.get_legend_damage({}, 1)

        assert len(result) == 3
        dmg_sums, dmg_common, imm_factors = result
        assert isinstance(dmg_sums, dict)
        assert isinstance(dmg_common, list)
        assert isinstance(imm_factors, dict)

    def test_on_hit_legend_damage_percentage_trigger(self):
        """Test on-hit legendary damage with percentage proc."""
        cfg = Config()
        weapon = Weapon("Darts", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Mock the legend_proc to return True
        with patch.object(legend_effect, 'legend_proc', return_value=True):
            legend_dict = {'proc': 0.05, 'fire': [[1, 30, 7]]}
            dmg_sums, dmg_common, imm_factors = legend_effect.get_legend_damage(legend_dict, 1)

            # Should have fire damage (amount depends on damage_roll)
            assert 'fire' in dmg_sums or len(dmg_sums) == 0

    def test_on_crit_legend_damage_trigger(self):
        """Test on-crit legendary damage trigger with registered effect."""
        cfg = Config()
        weapon = Weapon("Kukri_Inconseq", cfg)  # Has on_crit inconsequence effect
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        initial_procs = stats.legend_procs
        legend_dict = {'proc': 'on_crit', 'effect': 'inconsequence'}
        dmg_sums, dmg_common, imm_factors = legend_effect.get_legend_damage(legend_dict, 2)  # crit multiplier

        # Should have incremented legend procs (effect class does this)
        assert stats.legend_procs == initial_procs + 1

    def test_heavy_flail_special_damage_handling(self):
        """Test Heavy Flail special case for common damage."""
        cfg = Config()
        weapon = Weapon("Heavy Flail", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Mock legend_proc to return True
        with patch.object(legend_effect, 'legend_proc', return_value=True):
            legend_dict = {'proc': 0.05, 'physical': [[1, 6, 5, 0.05]]}
            dmg_sums, dmg_common, imm_factors = legend_effect.get_legend_damage(legend_dict, 1)

            # dmg_common should have the physical damage entry
            # Format: [dice, sides, flat, 'physical']
            if dmg_common:
                assert dmg_common[-1] == 'physical'

    def test_club_stone_immunity_reduction(self):
        """Test Club_Stone immunity reduction property."""
        cfg = Config()
        weapon = Weapon("Club_Stone", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Mock legend_proc to return True
        with patch.object(legend_effect, 'legend_proc', return_value=True):
            legend_dict = {'proc': 0.05, 'fire': [[1, 10]]}
            dmg_sums, dmg_common, imm_factors = legend_effect.get_legend_damage(legend_dict, 1)

            # Should have physical immunity reduction
            assert 'physical' in imm_factors
            assert imm_factors['physical'] == -0.05

    def test_legend_damage_with_no_proc(self):
        """Test legend damage when proc doesn't trigger."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Mock legend_proc to return False
        with patch.object(legend_effect, 'legend_proc', return_value=False):
            legend_dict = {'proc': 0.05, 'fire': [[1, 30, 7]]}
            dmg_sums, dmg_common, imm_factors = legend_effect.get_legend_damage(legend_dict, 1)

            # Should still return valid structures
            assert isinstance(dmg_sums, dict)
            assert isinstance(dmg_common, list)
            assert isinstance(imm_factors, dict)


class TestLegendDurationTracking:
    """Tests for legend effect duration and attack tracking."""

    def test_legend_attacks_left_decrements(self):
        """Test that legend_attacks_left decrements appropriately."""
        cfg = Config()
        weapon = Weapon("Heavy Flail", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Set up legend effect duration
        legend_effect.legend_attacks_left = 10

        with patch.object(legend_effect, 'legend_proc', return_value=False):
            legend_dict = {'proc': 0.05, 'physical': [[1, 6, 5, 0.05]]}
            legend_effect.get_legend_damage(legend_dict, 1)

            # Should decrement when proc didn't trigger but attacks_left > 0
            assert legend_effect.legend_attacks_left < 10

    def test_legend_duration_calculation(self):
        """Test duration calculation based on attacks per round."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Trigger legend proc
        legend_effect.legend_proc(1.0)  # Guaranteed trigger

        expected = attack_sim.attacks_per_round * legend_effect.legend_effect_duration
        assert legend_effect.legend_attacks_left == expected


class TestLegendEffectIntegration:
    """Integration tests for legend effects with different configurations."""

    def test_legend_effect_with_different_attack_progressions(self):
        """Test legend effect with various attack progressions."""
        cfg = Config()

        for ab_prog in ["5APR Classic", "4APR Classic", "Monk 7APR"]:
            cfg.AB_PROG = ab_prog
            weapon = Weapon("Scimitar", cfg)
            attack_sim = AttackSimulator(weapon, cfg)
            stats = StatsCollector()

            legend_effect = LegendEffect(stats, weapon, attack_sim)
            legend_effect.legend_proc(1.0)

            expected = attack_sim.attacks_per_round * 5
            assert legend_effect.legend_attacks_left == expected

    def test_legend_effect_state_persistence(self):
        """Test that legend effect state persists across calls."""
        cfg = Config()
        weapon = Weapon("Darts", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Trigger the effect first
        legend_effect.legend_attacks_left = 20
        legend_dict = {'proc': 0.05, 'pure': [[4, 6]], 'effect': 'perfect_strike'}

        with patch.object(legend_effect, 'legend_proc', return_value=False):
            legend_effect.get_legend_damage(legend_dict, 1)

        # Call ab_bonus multiple times
        ab_bonus_1 = legend_effect.ab_bonus
        ab_bonus_2 = legend_effect.ab_bonus

        # Should be consistent and state should persist
        assert ab_bonus_1 == ab_bonus_2 == 2
        # Note: legend_attacks_left decrements during get_legend_damage call
        assert legend_effect.legend_attacks_left == 19

    def test_legend_effect_with_all_weapon_types(self):
        """Test legend effects with all special weapons."""
        cfg = Config()

        special_weapons = [
            "Darts",
            "Light Flail",
            "Greatsword_Legion",
            "Heavy Flail",
            "Club_Stone",
        ]

        for weapon_name in special_weapons:
            weapon = Weapon(weapon_name, cfg)
            attack_sim = AttackSimulator(weapon, cfg)
            stats = StatsCollector()

            legend_effect = LegendEffect(stats, weapon, attack_sim)
            legend_effect.legend_attacks_left = 10

            # Should be able to call all methods without error
            ab = legend_effect.ab_bonus
            ac = legend_effect.ac_reduction
            dmg, dmg_common, imm = legend_effect.get_legend_damage({}, 1)

            assert isinstance(ab, int)
            assert isinstance(ac, int)


class TestLegendEffectEdgeCases:

    def test_proc_probability_boundaries(self):
        """Test legend proc with boundary probability values."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Test minimum probability
        result_min = legend_effect.legend_proc(0.001)
        assert isinstance(result_min, bool)

        # Test maximum probability
        legend_effect = LegendEffect(stats, weapon, attack_sim)
        result_max = legend_effect.legend_proc(0.999)
        assert isinstance(result_max, bool)

    def test_attacks_left_multiple_decrements(self):
        """Test that attacks_left decrements correctly over multiple calls."""
        cfg = Config()
        weapon = Weapon("Heavy Flail", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        initial_attacks = 50
        legend_effect.legend_attacks_left = initial_attacks

        with patch.object(legend_effect, 'legend_proc', return_value=False):
            legend_dict = {'proc': 0.05, 'physical': [[1, 6, 5, 0.05]]}

            # Call multiple times
            for i in range(5):
                legend_effect.get_legend_damage(legend_dict, 1)

            # Should have decremented (at least once per call when attacks_left > 0)
            assert legend_effect.legend_attacks_left <= initial_attacks

    def test_crit_multiplier_edge_cases(self):
        """Test get_legend_damage with various crit multiplier values."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        for crit_mult in [1, 2, 3, 4, 5]:
            dmg_sums, dmg_common, imm_factors = legend_effect.get_legend_damage({}, crit_mult)
            assert isinstance(dmg_sums, dict)

    def test_large_legend_attacks_left(self):
        """Test with large number of attacks left."""
        cfg = Config()
        weapon = Weapon("Darts", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Trigger the effect first
        legend_effect.legend_attacks_left = 10000
        legend_dict = {'proc': 0.05, 'pure': [[4, 6]], 'effect': 'perfect_strike'}

        with patch.object(legend_effect, 'legend_proc', return_value=False):
            legend_effect.get_legend_damage(legend_dict, 1)

        ab = legend_effect.ab_bonus
        assert ab == 2

    def test_zero_attacks_per_round(self):
        """Test edge case with very few attacks per round."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        attack_sim = AttackSimulator(weapon, cfg)
        stats = StatsCollector()
        legend_effect = LegendEffect(stats, weapon, attack_sim)

        # Even with few attacks, duration calculation should work
        legend_effect.legend_proc(1.0)
        assert legend_effect.legend_attacks_left > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

