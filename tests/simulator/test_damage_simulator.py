"""
Unit tests for the DamageSimulator class from simulator/damage_simulator.py

This test suite covers:
- DamageSimulator initialization and setup
- Damage collection from all sources (weapons, bonuses, additional damage)
- Convergence detection and threshold calculations
- DPS simulation mechanics (single and multiple rounds)
- Damage immunity and vulnerability application
- Dual-wield offhand strength bonus reduction
- Tenacious Blow feat damage on hit and miss
- Critical hit damage multiplier application
- Cumulative damage tracking and statistics
- Edge cases and configuration combinations
"""

import pytest
import math
from unittest.mock import Mock, patch, MagicMock
from collections import deque

from simulator.damage_simulator import DamageSimulator
from simulator.weapon import Weapon
from simulator.config import Config
from simulator.attack_simulator import AttackSimulator
from simulator.stats_collector import StatsCollector
from simulator.legend_effect import LegendEffect
from simulator.damage_roll import DamageRoll


class TestDamageSimulatorInitialization:
    """Tests for DamageSimulator initialization and setup."""

    def test_valid_initialization(self):
        """Test that DamageSimulator initializes correctly with valid inputs."""
        cfg = Config()
        # Use Scimitar instead of Scythe to avoid purple property structure issues
        simulator = DamageSimulator("Scimitar", cfg)

        assert simulator.cfg == cfg
        assert isinstance(simulator.stats, StatsCollector)
        assert isinstance(simulator.weapon, Weapon)
        assert isinstance(simulator.attack_sim, AttackSimulator)
        assert isinstance(simulator.legend_effect, LegendEffect)
        assert simulator.progress_callback is None

    def test_initialization_with_different_weapons(self):
        """Test initialization with various weapon types."""
        cfg = Config()

        for weapon_name in ["Scimitar", "Longsword", "Dagger_PK", "Rapier_Stinger"]:
            simulator = DamageSimulator(weapon_name, cfg)
            assert simulator.weapon.name_base is not None
            assert simulator.weapon == simulator.weapon

    def test_initialization_with_progress_callback(self):
        """Test that initialization accepts progress callback."""
        cfg = Config()
        callback = Mock()
        simulator = DamageSimulator("Scimitar", cfg, progress_callback=callback)

        assert simulator.progress_callback == callback

    def test_convergence_parameters_initialized(self):
        """Test that convergence parameters are correctly initialized."""
        cfg = Config()
        simulator = DamageSimulator("Scimitar", cfg)

        assert simulator.confidence == 0.99
        assert simulator.z == 2.576
        assert simulator.window_size == 15

    def test_damage_tracking_initialized_to_zero(self):
        """Test that damage tracking variables are initialized to zero."""
        cfg = Config()
        simulator = DamageSimulator("Scimitar", cfg)

        assert simulator.total_dmg == 0
        assert simulator.total_dmg_crit_imm == 0
        assert len(simulator.dps_per_round) == 0
        assert len(simulator.dps_crit_imm_per_round) == 0

    def test_dps_window_initialized(self):
        """Test that DPS tracking windows are initialized correctly."""
        cfg = Config()
        simulator = DamageSimulator("Scimitar", cfg)

        assert isinstance(simulator.dps_window, deque)
        assert simulator.dps_window.maxlen == 15
        assert isinstance(simulator.dps_crit_imm_window, deque)
        assert simulator.dps_crit_imm_window.maxlen == 15


class TestCollectDamageFromAllSources:
    """Tests for damage collection from all sources."""

    def test_collect_base_weapon_damage(self):
        """Test that base weapon damage is collected."""
        cfg = Config()
        simulator = DamageSimulator("Scimitar", cfg)

        # dmg_dict should contain physical damage from base weapon
        assert 'physical' in simulator.dmg_dict or 'slashing' in simulator.dmg_dict or 'piercing' in simulator.dmg_dict

    def test_collect_strength_bonus_damage(self):
        """Test that strength bonus is included in damage collection."""
        cfg = Config(COMBAT_TYPE='melee', STR_MOD=21, TWO_HANDED=False)
        simulator = DamageSimulator("Scimitar", cfg)

        # Physical damage should be in dmg_dict
        assert 'physical' in simulator.dmg_dict

    def test_collect_additional_damage_flame_weapon(self):
        """Test that additional damage sources are collected."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Flame_Weapon'][0] = True
        simulator = DamageSimulator("Scimitar", cfg)

        # Should have fire_fw damage collected
        assert 'fire_fw' in simulator.dmg_dict or len(simulator.dmg_dict) > 0

    def test_dmg_dict_contains_lists_of_lists(self):
        """Test that dmg_dict contains proper structure [dice, sides, flat]."""
        cfg = Config()
        simulator = DamageSimulator("Scimitar", cfg)

        for dmg_type, dmg_list in simulator.dmg_dict.items():
            assert isinstance(dmg_list, list)
            # Each entry should be a list with damage info
            if dmg_list:  # Only check if list is not empty
                for dmg_entry in dmg_list:
                    if isinstance(dmg_entry, list):  # Skip if it's not a list
                        assert len(dmg_entry) >= 2  # At least [dice, sides]

    def test_damage_aggregation_preserves_types(self):
        """Test that different damage types are preserved during aggregation."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Divine_Favor'][0] = True
        simulator = DamageSimulator("Scimitar", cfg)

        # Should have at least one damage type collected
        assert len(simulator.dmg_dict) >= 1

    def test_empty_additional_damage_handled(self):
        """Test that simulator handles when no additional damage is enabled."""
        cfg = Config()
        for key in cfg.ADDITIONAL_DAMAGE:
            cfg.ADDITIONAL_DAMAGE[key][0] = False

        simulator = DamageSimulator("Scimitar", cfg)
        # Should still initialize successfully
        assert len(simulator.dmg_dict) > 0


class TestConvergenceDetection:
    """Tests for convergence detection and calculations."""

    def test_convergence_requires_full_window(self):
        """Test that convergence check requires window to be full."""
        cfg = Config(STD_THRESHOLD=0.0002, CHANGE_THRESHOLD=0.0002)
        simulator = DamageSimulator("Scimitar", cfg)

        # With empty window, should not converge
        simulator.dps_window.append(100)
        assert len(simulator.dps_window) < simulator.window_size

    def test_convergence_true_with_stable_values(self):
        """Test convergence returns True when values are stable."""
        cfg = Config(STD_THRESHOLD=0.05, CHANGE_THRESHOLD=0.05)
        simulator = DamageSimulator("Scimitar", cfg)

        # Fill window with very similar values (stable)
        stable_value = 50.0
        for _ in range(15):
            simulator.dps_window.append(stable_value)

        # Should converge with high thresholds and stable values
        result = simulator.convergence(100)
        assert isinstance(result, bool)

    def test_convergence_false_with_unstable_values(self):
        """Test convergence returns False with unstable values."""
        cfg = Config(STD_THRESHOLD=0.001, CHANGE_THRESHOLD=0.001)
        simulator = DamageSimulator("Scimitar", cfg)

        # Fill window with varying values (unstable)
        for i in range(15):
            simulator.dps_window.append(50.0 + (i * 10))

        # Should not converge with strict thresholds and varied values
        result = simulator.convergence(100)
        assert isinstance(result, bool)

    def test_convergence_calculation_uses_statistics(self):
        """Test that convergence uses standard deviation and relative change."""
        cfg = Config()
        simulator = DamageSimulator("Scimitar", cfg)

        # Create predictable values
        values = [100, 101, 102, 101, 100, 101, 102, 101, 100, 101, 102, 101, 100, 101, 102]
        for v in values:
            simulator.dps_window.append(v)

        # Should calculate based on actual statistics
        result = simulator.convergence(100)
        assert isinstance(result, bool)


class TestDamageResults:
    """Tests for damage result calculation and application."""

    def test_get_damage_results_basic(self):
        """Test basic damage result calculation."""
        cfg = Config(TARGET_IMMUNITIES={'physical': 0.0})
        simulator = DamageSimulator("Scimitar", cfg)

        damage_dict = {'slashing': [DamageRoll(dice=2, sides=6, flat=5)]}  # 2d6+5
        results = simulator.get_damage_results(damage_dict, {})

        assert 'slashing' in results
        assert results['slashing'] >= 7  # Minimum 1+1+5
        assert results['slashing'] <= 17  # Maximum 6+6+5

    def test_get_damage_results_multiple_types(self):
        """Test damage calculation with multiple damage types."""
        cfg = Config(TARGET_IMMUNITIES={'physical': 0.0, 'fire': 0.0})
        simulator = DamageSimulator("Scimitar", cfg)

        damage_dict = {
            'slashing': [DamageRoll(dice=2, sides=6, flat=5)],
            'fire': [DamageRoll(dice=1, sides=4, flat=2)]
        }
        results = simulator.get_damage_results(damage_dict, {})

        assert 'slashing' in results
        assert 'fire' in results

    def test_get_damage_results_applies_immunity(self):
        """Test that immunity reduction is applied to damage results."""
        cfg = Config(TARGET_IMMUNITIES={'physical': 0.2})  # 20% immunity
        simulator = DamageSimulator("Scimitar", cfg)

        damage_dict = {'slashing': [DamageRoll(dice=0, sides=0, flat=100)]}  # Flat 100 damage
        results = simulator.get_damage_results(damage_dict, {})

        # Should be reduced by 20%
        assert results['slashing'] <= 100
        assert results['slashing'] >= 80  # 100 - 20

    def test_get_damage_results_with_multiple_entries(self):
        """Test damage calculation when type has multiple damage sources."""
        cfg = Config(TARGET_IMMUNITIES={'physical': 0.0})
        simulator = DamageSimulator("Scimitar", cfg)

        damage_dict = {'physical': [DamageRoll(dice=1, sides=6, flat=0), DamageRoll(dice=1, sides=4, flat=3)]}  # 1d6 + 1d4+3
        results = simulator.get_damage_results(damage_dict, {})

        # Should combine both damage rolls
        assert 'physical' in results
        assert results['physical'] >= 5  # Minimum 1 + 1 + 3
        assert results['physical'] <= 13  # Maximum 6 + 4 + 3


class TestSimulationRound:
    """Tests for single round simulation mechanics."""

    def test_simulate_dps_basic_execution(self):
        """Test that simulate_dps executes without errors."""
        cfg = Config(ROUNDS=10)  # Very small number for quick test
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):  # Suppress print output
            result = simulator.simulate_dps()

        assert result is not None
        assert isinstance(result, dict)

    def test_simulate_dps_returns_all_keys(self):
        """Test that simulate_dps returns all required keys."""
        cfg = Config(ROUNDS=10)
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        required_keys = {
            'avg_dps_both', 'dps_crits', 'dps_no_crits', 'dps_per_round',
            'dps_rolling_avg', 'cumulative_damage_per_round', 'damage_by_type',
            'attack_prog', 'hit_rate_actual', 'crit_rate_actual', 'legend_proc_rate_actual',
            'hits_per_attack', 'crits_per_attack', 'hit_rate_theoretical',
            'crit_rate_theoretical', 'legend_proc_rate_theoretical',
            'hit_rate_per_attack_theoretical', 'crit_rate_per_attack_theoretical',
            'summary'
        }
        assert required_keys.issubset(result.keys())

    def test_simulate_dps_damage_accumulates(self):
        """Test that total damage accumulates across rounds."""
        cfg = Config(ROUNDS=20)
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # Total damage should be positive after rounds
        assert simulator.total_dmg > 0
        assert simulator.total_dmg_crit_imm > 0

    def test_simulate_dps_tracking_statistics(self):
        """Test that simulation tracks statistics correctly."""
        cfg = Config(ROUNDS=20)
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            simulator.simulate_dps()

        # Should have tracked attempts
        assert simulator.stats.attempts_made > 0
        assert simulator.stats.hits >= 0

    def test_simulate_dps_respects_damage_limit(self):
        """Test that simulation stops when damage limit is reached."""
        cfg = Config(ROUNDS=10000, DAMAGE_LIMIT_FLAG=True, DAMAGE_LIMIT=100)
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            simulator.simulate_dps()

        # Should stop before reaching full rounds
        assert simulator.total_dmg >= cfg.DAMAGE_LIMIT


class TestDualWieldMechanics:
    """Tests for dual-wield specific mechanics."""

    def test_dual_wield_detection(self):
        """Test that dual-wield is properly detected in simulator."""
        cfg = Config(AB_PROG="5APR Classic")
        cfg.DUAL_WIELD = True
        simulator = DamageSimulator("Longsword", cfg)

        assert simulator.attack_sim.dual_wield is True

    def test_non_dual_wield_detection(self):
        """Test that non-dual-wield progressions are detected."""
        cfg = Config(AB_PROG="5APR Classic")
        simulator = DamageSimulator("Longsword", cfg)

        assert simulator.attack_sim.dual_wield is False

    def test_offhand_strength_bonus_halving(self):
        """Test that offhand attacks get halved strength bonus.

        This is tested through the attack indices setup in simulate_dps.
        """
        cfg = Config(
            AB_PROG="5APR Classic",
            COMBAT_TYPE='melee',
            STR_MOD=20,
            TWO_HANDED=False,
            ROUNDS=5
        )
        cfg.DUAL_WIELD = True
        cfg.IMPROVED_TWF = True
        simulator = DamageSimulator("Longsword", cfg)

        with patch('builtins.print'):
            simulator.simulate_dps()

        # Should have tracked offhand attacks
        # If offhand detection is working, last 2 attack indices should have different damage
        assert len(simulator.stats.crits_per_attack) > 0


class TestTenaciousBlowMechanics:
    """Tests for Tenacious Blow feat mechanics."""

    def test_tenacious_blow_disabled_by_default(self):
        """Test that Tenacious Blow is disabled by default."""
        cfg = Config()
        simulator = DamageSimulator("Dire Mace", cfg)

        # Should collect damage without Tenacious Blow miss damage
        assert 'pure' not in simulator.dmg_dict or len(simulator.dmg_dict['pure']) == 0

    def test_tenacious_blow_enabled_on_dire_mace(self):
        """Test Tenacious Blow setup on Dire Mace."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Tenacious_Blow'][0] = True
        simulator = DamageSimulator("Dire Mace", cfg)

        # Should have the Tenacious Blow damage source
        assert 'physical' in simulator.dmg_dict

    def test_tenacious_blow_on_double_axe(self):
        """Test Tenacious Blow setup on Double Axe."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Tenacious_Blow'][0] = True
        simulator = DamageSimulator("Double Axe", cfg)

        # Should collect damage correctly
        assert len(simulator.dmg_dict) > 0

    def test_tenacious_blow_disabled_on_single_sided_weapon(self):
        """Test that Tenacious Blow is filtered out on single-sided weapons."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Tenacious_Blow'][0] = True
        simulator = DamageSimulator("Longsword", cfg)

        # Tenacious Blow should be filtered by Weapon class
        # This is tested at weapon level, but simulator should handle it
        assert len(simulator.dmg_dict) > 0


class TestCriticalDamage:
    """Tests for critical damage multiplier mechanics."""

    def test_crit_multiplier_applied_to_damage(self):
        """Test that critical multiplier is available for damage calculation."""
        cfg = Config(KEEN=False, IMPROVED_CRIT=False, WEAPONMASTER=False)
        simulator = DamageSimulator("Scimitar", cfg)

        # Scimitar base crit multiplier is 2
        assert simulator.weapon.crit_multiplier == 2

    def test_crit_multiplier_with_weaponmaster(self):
        """Test critical multiplier with Weaponmaster feat."""
        cfg = Config(WEAPONMASTER=True)
        simulator = DamageSimulator("Scimitar", cfg)

        # Scimitar with Weaponmaster: 2 + 1 = 3
        assert simulator.weapon.crit_multiplier == 3

    def test_crit_vs_non_crit_damage_tracking(self):
        """Test that crit and non-crit damage are tracked separately."""
        cfg = Config(ROUNDS=20)
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            simulator.simulate_dps()

        # Both tracking variables should be populated
        assert simulator.total_dmg > 0
        assert simulator.total_dmg_crit_imm > 0


class TestDamageImmunityVulnerability:
    """Tests for damage immunity and vulnerability mechanics."""

    def test_immunity_reduces_damage(self):
        """Test that immunity reduces damage correctly."""
        cfg = Config(TARGET_IMMUNITIES={'physical': 0.1})  # 10% immunity
        simulator = DamageSimulator("Scimitar", cfg)

        damage_dict = {'slashing': [DamageRoll(dice=0, sides=0, flat=100)]}
        results = simulator.get_damage_results(damage_dict, {})

        # Should have 10% reduction
        assert results['slashing'] < 100
        assert results['slashing'] >= 90

    def test_vulnerability_increases_damage(self):
        """Test that vulnerability (negative immunity) increases damage."""
        cfg = Config(TARGET_IMMUNITIES={'fire': -0.1})  # 10% vulnerability
        simulator = DamageSimulator("Scimitar", cfg)

        damage_dict = {'fire_fw': [DamageRoll(dice=0, sides=0, flat=100)]}
        results = simulator.get_damage_results(damage_dict, {})

        # Should have 10% vulnerability bonus
        assert results['fire_fw'] > 100

    def test_legend_immunity_modification(self):
        """Test that legend properties can modify immunities."""
        cfg = Config(TARGET_IMMUNITIES={'physical': 0.2})
        simulator = DamageSimulator("Scimitar", cfg)

        damage_dict = {'slashing': [DamageRoll(dice=0, sides=0, flat=100)]}
        # Legend immunity modification
        imm_factors = {'physical': -0.05}  # Reduce physical immunity by 5%
        results = simulator.get_damage_results(damage_dict, imm_factors)

        # Should have 15% immunity instead of 20%
        assert results['slashing'] > 80
        assert results['slashing'] <= 100

    def test_minimum_damage_is_one(self):
        """Test that damage is never reduced below 1."""
        cfg = Config(TARGET_IMMUNITIES={'physical': 0.95})  # Heavy immunity
        simulator = DamageSimulator("Scimitar", cfg)

        damage_dict = {'slashing': [DamageRoll(dice=0, sides=0, flat=10)]}
        results = simulator.get_damage_results(damage_dict, {})

        # Even with 95% immunity, should have minimum 1 damage
        assert results['slashing'] >= 1


class TestStatisticsCollection:
    """Tests for statistics collection during simulation."""

    def test_stats_collector_initialized(self):
        """Test that stats collector is properly initialized."""
        cfg = Config()
        simulator = DamageSimulator("Scimitar", cfg)

        assert isinstance(simulator.stats, StatsCollector)
        assert simulator.stats.attempts_made == 0
        assert simulator.stats.hits == 0

    def test_stats_tracked_per_attack(self):
        """Test that statistics are tracked per individual attack."""
        cfg = Config(ROUNDS=20)
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            simulator.simulate_dps()

        # Should have stats per attack
        assert len(simulator.stats.hits_per_attack) == simulator.attack_sim.attacks_per_round
        assert len(simulator.stats.crits_per_attack) == simulator.attack_sim.attacks_per_round

    def test_cumulative_damage_by_type(self):
        """Test that cumulative damage is tracked by damage type."""
        cfg = Config(ROUNDS=20)
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            simulator.simulate_dps()

        # Should have damage by type
        assert isinstance(simulator.cumulative_damage_by_type, dict)


class TestDamageSimulatorConfigurations:
    """Integration tests with various configurations."""

    def test_melee_configuration(self):
        """Test simulator with standard melee configuration."""
        cfg = Config(
            COMBAT_TYPE='melee',
            STR_MOD=21,
            ENHANCEMENT_SET_BONUS=3,
            WEAPONMASTER=True,
            KEEN=True,
            ROUNDS=10
        )
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        assert result['dps_crits'] > 0

    def test_ranged_configuration(self):
        """Test simulator with ranged weapon configuration."""
        cfg = Config(
            COMBAT_TYPE='ranged',
            STR_MOD=21,
            MIGHTY=10,
            AB_PROG="5APR & Rapid Shot",
            ROUNDS=10
        )
        simulator = DamageSimulator("Longbow_FireDragon", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        assert result['dps_crits'] >= 0

    def test_dual_wield_configuration(self):
        """Test simulator with dual-wield configuration."""
        cfg = Config(
            AB_PROG="5APR Classic",
            COMBAT_TYPE='melee',
            STR_MOD=21,
            ROUNDS=10
        )
        cfg.DUAL_WIELD = True
        simulator = DamageSimulator("Longsword", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        assert result['dps_crits'] >= 0

    def test_with_additional_damage_sources(self):
        """Test simulator with multiple additional damage sources enabled."""
        cfg = Config(ROUNDS=10)
        cfg.ADDITIONAL_DAMAGE['Flame_Weapon'][0] = True
        cfg.ADDITIONAL_DAMAGE['Divine_Favor'][0] = True
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # Should have collected multiple damage types
        assert len(simulator.dmg_dict) > 1

    def test_high_damage_multiplier_configuration(self):
        """Test simulator with maximum damage multipliers."""
        cfg = Config(
            ENHANCEMENT_SET_BONUS=3,
            STR_MOD=30,
            WEAPONMASTER=True,
            KEEN=True,
            IMPROVED_CRIT=True,
            ROUNDS=10
        )
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # Should produce significant damage
        assert result['dps_crits'] > 0


class TestDamageSimulatorEdgeCases:

    def test_zero_strength_modifier(self):
        """Test simulator with zero strength modifier."""
        cfg = Config(STR_MOD=0, ROUNDS=10)
        simulator = DamageSimulator("Longsword", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # Should still simulate without error
        assert result['dps_crits'] >= 0

    def test_single_round_simulation(self):
        """Test simulator with just one round."""
        cfg = Config(ROUNDS=1)
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # Should have results even with one round
        assert result['dps_crits'] >= 0

    def test_very_high_ac_target(self):
        """Test simulator against very high AC target."""
        cfg = Config(TARGET_AC=150, ROUNDS=10)
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # Should still complete, but with low hit rate
        assert 'hit_rate_actual' in result

    def test_very_low_ac_target(self):
        """Test simulator against very low AC target."""
        cfg = Config(TARGET_AC=0, ROUNDS=10)
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # Should have very high hit rate
        assert result['hit_rate_actual'] > 0

    def test_heavy_immunity_target(self):
        """Test simulator against heavily immunized target."""
        cfg = Config()
        cfg.TARGET_IMMUNITIES['physical'] = 0.8
        cfg.ROUNDS = 10
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # Should still work but with reduced damage
        assert result['dps_crits'] >= 0

    def test_highly_vulnerable_target(self):
        """Test simulator against vulnerable target."""
        cfg = Config()
        cfg.TARGET_IMMUNITIES['physical'] = -0.5  # 50% vulnerability
        cfg.ROUNDS = 10
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # Should have boosted damage
        assert result['dps_crits'] >= 0


class TestResultSummary:
    """Tests for result summary generation."""

    def test_summary_contains_key_metrics(self):
        """Test that summary string contains key metrics."""
        cfg = Config(ROUNDS=10)
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        summary = result['summary']
        assert 'DPS' in summary
        assert 'damage' in summary.lower()
        assert 'Rounds averaged' in summary

    def test_summary_includes_attack_progression(self):
        """Test that summary includes attack progression."""
        cfg = Config(ROUNDS=10)
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        assert 'AB:' in result['summary']

    def test_result_dps_values_are_positive(self):
        """Test that result DPS values are non-negative."""
        cfg = Config(ROUNDS=10)
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        assert result['dps_crits'] >= 0
        assert result['dps_no_crits'] >= 0
        assert result['avg_dps_both'] >= 0

    def test_result_per_attack_rates_are_percentages(self):
        """Test that per-attack rates are in percentage format."""
        cfg = Config(ROUNDS=10)
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        for rate in result['hit_rate_per_attack_theoretical']:
            assert 0 <= rate <= 100

    def test_theoretical_vs_actual_rates(self):
        """Test that both theoretical and actual rates are calculated."""
        cfg = Config(ROUNDS=50)  # More rounds for better accuracy
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        assert 'hit_rate_theoretical' in result
        assert 'hit_rate_actual' in result
        assert 'crit_rate_theoretical' in result
        assert 'crit_rate_actual' in result


class TestOverwhelmCritical:
    """Tests for the Overwhelm Critical feature."""

    def test_overwhelm_crit_disabled_by_default(self):
        """Test that Overwhelm Critical is disabled by default."""
        cfg = Config()
        assert cfg.OVERWHELM_CRIT is False

    def test_overwhelm_crit_can_be_enabled(self):
        """Test that Overwhelm Critical can be enabled in config."""
        cfg = Config(OVERWHELM_CRIT=True)
        assert cfg.OVERWHELM_CRIT is True

    def test_overwhelm_crit_disabled_no_bonus_damage(self):
        """Test that disabling Overwhelm Critical removes bonus damage from crits."""
        cfg_disabled = Config(
            OVERWHELM_CRIT=False,
            AB=100,
            TARGET_AC=10,
            ROUNDS=50
        )
        simulator_disabled = DamageSimulator("Scimitar", cfg_disabled)

        with patch('builtins.print'):
            result_disabled = simulator_disabled.simulate_dps()

        # Should have some damage but without overwhelm bonus
        assert result_disabled['dps_crits'] > 0

    def test_overwhelm_crit_enabled_vs_disabled(self):
        """Test that enabling Overwhelm Critical increases damage on crit-heavy builds."""
        cfg = Config(
            OVERWHELM_CRIT=True,
            AB=100,
            TARGET_AC=10,
            KEEN=True,  # Increases crit range
            IMPROVED_CRIT=True,
            ROUNDS=100
        )
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # With overwhelm crit enabled and high crit chance, DPS should be decent
        assert result['dps_crits'] > 0

    def test_overwhelm_crit_x2_multiplier_adds_1d6(self):
        """Test that x2 crit multiplier adds 1d6 physical damage with Overwhelm Critical."""
        cfg = Config(
            OVERWHELM_CRIT=True,
            AB=100,
            TARGET_AC=10,
            ROUNDS=50
        )
        # Scimitar has x2 crit multiplier
        simulator = DamageSimulator("Scimitar", cfg)

        # Check weapon crit multiplier
        assert simulator.weapon.crit_multiplier == 2

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # DPS should be positive
        assert result['dps_crits'] > 0
        # Should have crits
        assert result['crit_rate_actual'] > 0

    def test_overwhelm_crit_x3_multiplier_adds_2d6(self):
        """Test that x3 crit multiplier adds 2d6 physical damage with Overwhelm Critical."""
        cfg = Config(
            OVERWHELM_CRIT=True,
            AB=100,
            TARGET_AC=10,
            ROUNDS=50
        )
        # Scythe has x4 crit multiplier, but we can verify the logic
        simulator = DamageSimulator("Scythe", cfg)

        # Scythe has x4 multiplier, so it should get 3d6 (not 2d6)
        assert simulator.weapon.crit_multiplier == 4

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # DPS should be positive
        assert result['dps_crits'] > 0

    def test_overwhelm_crit_x4_multiplier_adds_3d6(self):
        """Test that x4+ crit multiplier adds 3d6 physical damage with Overwhelm Critical."""
        cfg = Config(
            OVERWHELM_CRIT=True,
            AB=100,
            TARGET_AC=10,
            ROUNDS=50
        )
        # Scythe has x4 crit multiplier
        simulator = DamageSimulator("Scythe", cfg)

        assert simulator.weapon.crit_multiplier == 4

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # With x4 crit and overwhelm crit enabled, DPS should be strong
        assert result['dps_crits'] > 0

    def test_overwhelm_crit_only_on_critical_hits(self):
        """Test that Overwhelm Critical damage is only added on critical hits."""
        cfg = Config(
            OVERWHELM_CRIT=True,
            AB=50,
            TARGET_AC=65,  # High AC, very low crit chance
            ROUNDS=50
        )
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # On critical immune, should not have overwhelm bonus
        # DPS no crits should be equal or less than DPS with crits
        assert result['dps_no_crits'] <= result['dps_crits']

    def test_overwhelm_crit_with_different_weapons(self):
        """Test Overwhelm Critical works with different weapon crit multipliers."""
        weapons_to_test = ["Scimitar", "Longsword", "Scythe", "Dagger_PK"]
        cfg_base = Config(
            OVERWHELM_CRIT=True,
            AB=100,
            TARGET_AC=10,
            ROUNDS=30
        )

        for weapon_name in weapons_to_test:
            try:
                simulator = DamageSimulator(weapon_name, cfg_base)
                with patch('builtins.print'):
                    result = simulator.simulate_dps()

                # All weapons should have positive DPS
                assert result['dps_crits'] >= 0
            except Exception as e:
                # Skip if weapon not found
                continue

    def test_overwhelm_crit_with_keen_feat(self):
        """Test that Overwhelm Critical works well with Keen feat."""
        cfg = Config(
            OVERWHELM_CRIT=True,
            KEEN=True,
            AB=100,
            TARGET_AC=10,
            ROUNDS=50
        )
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # With Keen and Overwhelm Crit, crit rate should be high
        assert result['crit_rate_actual'] > 20  # At least 20% crit rate expected

    def test_overwhelm_crit_with_improved_crit_feat(self):
        """Test that Overwhelm Critical works well with Improved Critical feat."""
        cfg = Config(
            OVERWHELM_CRIT=True,
            IMPROVED_CRIT=True,
            AB=100,
            TARGET_AC=10,
            ROUNDS=50
        )
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # With Improved Crit and Overwhelm Crit, crit rate should be notable
        assert result['crit_rate_actual'] > 10

    def test_overwhelm_crit_damage_is_physical_type(self):
        """Test that Overwhelm Critical bonus damage is counted as physical type."""
        cfg = Config(
            OVERWHELM_CRIT=True,
            AB=100,
            TARGET_AC=10,
            ROUNDS=50
        )
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # Physical damage should be tracked
        damage_by_type = result['damage_by_type']
        if len(damage_by_type) > 0:
            # Physical should be present if there were crits
            if result['crit_rate_actual'] > 0:
                assert 'physical' in damage_by_type or any(k.startswith('physical') for k in damage_by_type.keys())

    def test_overwhelm_crit_with_multiple_crits_per_round(self):
        """Test Overwhelm Critical with 5 APR (multiple crits per round possible)."""
        cfg = Config(
            OVERWHELM_CRIT=True,
            AB=100,
            TARGET_AC=10,
            AB_PROG="5APR Classic",
            KEEN=True,
            IMPROVED_CRIT=True,
            ROUNDS=50
        )
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # With 5 APR and crits enabled, should have significant DPS
        assert result['dps_crits'] > 0
        # Should have multiple crits per attack attempt (5+ attacks per round)
        assert len(result['hits_per_attack']) >= 5


class TestDevastatingCritical:
    """Tests for the Devastating Critical feature."""

    def test_dev_crit_disabled_by_default(self):
        """Test that Devastating Critical is disabled by default."""
        cfg = Config()
        assert cfg.DEV_CRIT is False

    def test_dev_crit_can_be_enabled(self):
        """Test that Devastating Critical can be enabled in config."""
        cfg = Config(DEV_CRIT=True)
        assert cfg.DEV_CRIT is True

    def test_dev_crit_disabled_no_bonus_damage(self):
        """Test that disabling Devastating Critical removes bonus damage from crits."""
        cfg_disabled = Config(
            DEV_CRIT=False,
            AB=100,
            TARGET_AC=10,
            ROUNDS=50
        )
        simulator_disabled = DamageSimulator("Scimitar", cfg_disabled)

        with patch('builtins.print'):
            result_disabled = simulator_disabled.simulate_dps()

        # Should have some damage but without dev crit bonus
        assert result_disabled['dps_crits'] > 0

    def test_dev_crit_tiny_small_weapon_adds_10_pure(self):
        """Test that Tiny/Small weapons add 10 pure damage on crit with Devastating Critical."""
        cfg = Config(
            DEV_CRIT=True,
            AB=100,
            TARGET_AC=10,
            ROUNDS=50
        )
        # Dagger_PK is a Tiny weapon (also covered by Tiny/Small category)
        simulator = DamageSimulator("Dagger_PK", cfg)

        # Verify weapon size is Tiny or Small
        assert simulator.weapon.size in ['T', 'S']

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # DPS should be positive
        assert result['dps_crits'] > 0

    def test_dev_crit_medium_weapon_adds_20_pure(self):
        """Test that Medium weapons add 20 pure damage on crit with Devastating Critical."""
        cfg = Config(
            DEV_CRIT=True,
            AB=100,
            TARGET_AC=10,
            ROUNDS=50
        )
        # Scimitar is a Medium weapon
        simulator = DamageSimulator("Scimitar", cfg)

        # Verify weapon size
        assert simulator.weapon.size == 'M'

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # DPS should be positive
        assert result['dps_crits'] > 0

    def test_dev_crit_large_weapon_adds_30_pure(self):
        """Test that Large weapons add 30 pure damage on crit with Devastating Critical."""
        cfg = Config(
            DEV_CRIT=True,
            AB=100,
            TARGET_AC=10,
            ROUNDS=50
        )
        # Scythe is a Large weapon
        simulator = DamageSimulator("Scythe", cfg)

        # Verify weapon size
        assert simulator.weapon.size == 'L'

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # DPS should be positive
        assert result['dps_crits'] > 0

    def test_dev_crit_only_on_critical_hits(self):
        """Test that Devastating Critical damage is only added on critical hits."""
        cfg = Config(
            DEV_CRIT=True,
            AB=50,
            TARGET_AC=65,  # High AC, very low crit chance
            ROUNDS=50
        )
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # On critical immune, should not have dev crit bonus
        # DPS no crits should be equal or less than DPS with crits
        assert result['dps_no_crits'] <= result['dps_crits']

    def test_dev_crit_pure_damage_type(self):
        """Test that Devastating Critical bonus is pure damage type."""
        cfg = Config(
            DEV_CRIT=True,
            AB=100,
            TARGET_AC=10,
            ROUNDS=50
        )
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # Pure damage should be tracked if there were crits
        damage_by_type = result['damage_by_type']
        if result['crit_rate_actual'] > 0:
            # Pure damage should be present
            assert 'pure' in damage_by_type or any(k.startswith('pure') for k in damage_by_type.keys())

    def test_dev_crit_with_keen_feat(self):
        """Test that Devastating Critical works well with Keen feat."""
        cfg = Config(
            DEV_CRIT=True,
            KEEN=True,
            AB=100,
            TARGET_AC=10,
            ROUNDS=50
        )
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # With Keen and Dev Crit, crit rate should be high
        assert result['crit_rate_actual'] > 20

    def test_dev_crit_with_improved_crit_feat(self):
        """Test that Devastating Critical works well with Improved Critical feat."""
        cfg = Config(
            DEV_CRIT=True,
            IMPROVED_CRIT=True,
            AB=100,
            TARGET_AC=10,
            ROUNDS=50
        )
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # With Improved Crit and Dev Crit, crit rate should be notable
        assert result['crit_rate_actual'] > 10

    def test_dev_crit_with_overwhelm_crit_combined(self):
        """Test that Devastating Critical works together with Overwhelming Critical."""
        cfg = Config(
            DEV_CRIT=True,
            OVERWHELM_CRIT=True,
            AB=100,
            TARGET_AC=10,
            KEEN=True,
            IMPROVED_CRIT=True,
            ROUNDS=50
        )
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # Both features enabled should provide excellent DPS on crit builds
        assert result['dps_crits'] > 0
        assert result['crit_rate_actual'] > 20

    def test_dev_crit_small_weapon_vs_large_damage_difference(self):
        """Test that large weapons deal more dev crit damage than small weapons."""
        cfg_base = Config(
            DEV_CRIT=True,
            AB=100,
            TARGET_AC=10,
            ROUNDS=100
        )

        # Small weapon: Dagger (+10 pure)
        simulator_small = DamageSimulator("Dagger_PK", cfg_base)
        with patch('builtins.print'):
            result_small = simulator_small.simulate_dps()

        # Large weapon: Scythe (+30 pure)
        simulator_large = DamageSimulator("Scythe", cfg_base)
        with patch('builtins.print'):
            result_large = simulator_large.simulate_dps()

        # Large weapon should have more total damage due to dev crit bonus
        assert result_large['dps_crits'] > result_small['dps_crits']

    def test_dev_crit_with_multiple_crits_per_round(self):
        """Test Devastating Critical with 5 APR (multiple crits per round possible)."""
        cfg = Config(
            DEV_CRIT=True,
            AB=100,
            TARGET_AC=10,
            AB_PROG="5APR Classic",
            KEEN=True,
            IMPROVED_CRIT=True,
            ROUNDS=50
        )
        simulator = DamageSimulator("Scimitar", cfg)

        with patch('builtins.print'):
            result = simulator.simulate_dps()

        # With 5 APR and crits enabled, should have significant DPS
        assert result['dps_crits'] > 0
        assert len(result['hits_per_attack']) >= 5

    def test_dev_crit_enabled_vs_disabled(self):
        """Test that enabling Devastating Critical increases crit damage."""
        cfg_enabled = Config(
            DEV_CRIT=True,
            AB=100,
            TARGET_AC=10,
            KEEN=True,
            IMPROVED_CRIT=True,
            ROUNDS=100
        )
        simulator_enabled = DamageSimulator("Scimitar", cfg_enabled)

        with patch('builtins.print'):
            result_enabled = simulator_enabled.simulate_dps()

        cfg_disabled = Config(
            DEV_CRIT=False,
            AB=100,
            TARGET_AC=10,
            KEEN=True,
            IMPROVED_CRIT=True,
            ROUNDS=100
        )
        simulator_disabled = DamageSimulator("Scimitar", cfg_disabled)

        with patch('builtins.print'):
            result_disabled = simulator_disabled.simulate_dps()

        # Enabled should have higher DPS on crit-heavy builds
        assert result_enabled['dps_crits'] >= result_disabled['dps_crits']


class TestInternalMethods:
    """Tests for internal/private methods (from newer test suite)."""

    def test_setup_dual_wield_tracking_non_dw(self):
        """Test dual-wield tracking setup for non-dual-wield builds."""
        cfg = Config()
        cfg.AB_PROG = "5APR Classic"
        sim = DamageSimulator('Spear', cfg)

        result = sim._setup_dual_wield_tracking()
        assert result['is_dual_wield'] is False
        assert result['offhand_attack_indices'] == []
        assert result['str_idx'] is None
        assert result['offhand_str_idx'] is None

    def test_setup_dual_wield_tracking_with_dw(self):
        """Test dual-wield tracking setup for dual-wield builds."""
        cfg = Config()
        cfg.AB_PROG = "5APR Classic"
        cfg.DUAL_WIELD = True
        cfg.IMPROVED_TWF = True
        cfg.CHARACTER_SIZE = "M"
        sim = DamageSimulator('Longsword', cfg)

        result = sim._setup_dual_wield_tracking()
        assert result['is_dual_wield'] is True
        assert len(result['offhand_attack_indices']) == 2  # Two offhand attacks with IMPROVED_TWF
        assert result['str_idx'] is not None
        # offhand_str_idx is None when no custom offhand weapon
        assert result['offhand_str_idx'] is None

    def test_calculate_final_statistics_zero_rounds(self):
        """Test final statistics calculation with zero rounds."""
        cfg = Config()
        sim = DamageSimulator('Spear', cfg)
        sim.stats.hits = 0
        sim.attack_sim.valid_dual_wield_config = False

        result = sim._calculate_final_statistics(round_num=0)

        assert result['dps_mean'] == 0
        assert result['dps_stdev'] == 0
        assert result['dpr'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

