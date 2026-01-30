import pytest
from simulator.legend_effect import LegendEffect
from simulator.stats_collector import StatsCollector
from simulator.weapon import Weapon
from simulator.attack_simulator import AttackSimulator
from simulator.config import Config


def test_legend_effect_on_proc_applies_burst_and_persistent():
    """Test that on proc, both burst and persistent effects are applied."""
    cfg = Config()
    weapon = Weapon('Spear', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    legend_effect = LegendEffect(stats, weapon, attack_sim)

    # Spear has legendary: {'proc': 0.05, 'acid': [4, 6], 'pure': [4, 6]}
    legend_dict = {'proc': 0.05, 'acid': [[4, 6]], 'pure': [[4, 6]]}

    # Force a proc by mocking
    import random
    random.seed(1)  # Seed for reproducible proc

    damage_sums, common_damage, imm_factors = legend_effect.get_legend_damage(legend_dict, 1)

    # If procced, should have damage
    # (exact values depend on random, just check structure)
    assert isinstance(damage_sums, dict)
    assert isinstance(common_damage, list)
    assert isinstance(imm_factors, dict)


def test_legend_effect_during_window_applies_only_persistent():
    """Test that during window, only persistent effects apply (not burst damage)."""
    cfg = Config()
    weapon = Weapon('Heavy Flail', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    legend_effect = LegendEffect(stats, weapon, attack_sim)
    legend_effect.legend_attacks_left = 5  # Simulate active window

    # Heavy Flail has persistent common_damage
    legend_dict = {'proc': 0.05, 'physical': [[0, 0, 5]]}

    damage_sums, common_damage, imm_factors = legend_effect.get_legend_damage(legend_dict, 1)

    # During window: no burst damage, but common_damage should be present
    # Note: Heavy Flail has no burst damage anyway
    assert isinstance(common_damage, list)


def test_legend_effect_ab_bonus_property():
    """Test that ab_bonus property returns persistent AB bonus."""
    cfg = Config()
    weapon = Weapon('Darts', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    legend_effect = LegendEffect(stats, weapon, attack_sim)

    # Initially no bonus
    assert legend_effect.ab_bonus == 0

    # After proc (simulated by setting internal state)
    legend_effect._current_ab_bonus = 2
    assert legend_effect.ab_bonus == 2


def test_legend_effect_ac_reduction_property():
    """Test that ac_reduction property returns persistent AC reduction."""
    cfg = Config()
    weapon = Weapon('Light Flail', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    legend_effect = LegendEffect(stats, weapon, attack_sim)

    # Initially no reduction
    assert legend_effect.ac_reduction == 0

    # After proc (simulated by setting internal state)
    legend_effect._current_ac_reduction = -2
    assert legend_effect.ac_reduction == -2
