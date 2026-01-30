import pytest
from simulator.legendary_effects.base import LegendaryEffect
from simulator.legendary_effects.registry import LegendaryEffectRegistry
from simulator.legendary_effects.heavy_flail_effect import HeavyFlailEffect
from simulator.legendary_effects.crushing_blow_effect import CrushingBlowEffect
from simulator.stats_collector import StatsCollector


def test_registry_get_effect():
    registry = LegendaryEffectRegistry()
    effect = registry.get_effect('Heavy Flail')

    assert effect is not None
    assert isinstance(effect, HeavyFlailEffect)


def test_registry_returns_none_for_unknown_weapon():
    registry = LegendaryEffectRegistry()
    effect = registry.get_effect('Unknown Weapon')

    assert effect is None


def test_heavy_flail_effect_applies_damage():
    stats = StatsCollector()
    effect = HeavyFlailEffect()

    legend_dict = {
        'proc': 0.05,
        'physical': [[0, 0, 5]]
    }

    result = effect.apply(legend_dict, stats, crit_multiplier=1, attack_sim=None)

    assert 'common_damage' in result
    assert result['common_damage'] == [0, 0, 5, 'physical']


def test_crushing_blow_effect_reduces_physical_immunity():
    stats = StatsCollector()
    effect = CrushingBlowEffect()

    legend_dict = {
        'proc': 0.20,
    }

    result = effect.apply(legend_dict, stats, crit_multiplier=1, attack_sim=None)

    assert 'immunity_factors' in result
    assert result['immunity_factors'] == {'physical': -0.05}
    assert result['common_damage'] is None
    assert result['damage_sums'] == {}


def test_base_interface_returns_two_tuple():
    """Verify that effect.apply() returns (burst, persistent) tuple."""
    from simulator.legendary_effects.base import LegendaryEffect
    from simulator.stats_collector import StatsCollector
    from typing import get_type_hints, Tuple

    # Check the type annotation on the base interface
    hints = get_type_hints(LegendaryEffect.apply)
    return_type = hints.get('return')

    # The return type should be a Tuple, not a Dict
    assert return_type is not None, "apply() must have a return type annotation"
    assert hasattr(return_type, '__origin__'), "Return type should be a generic type (Tuple)"
    assert return_type.__origin__ == tuple, f"Expected tuple, got {return_type.__origin__}"

    # Test a concrete implementation
    class TestEffect(LegendaryEffect):
        def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
            return {'damage_sums': {}}, {'ab_bonus': 0}

    effect = TestEffect()
    result = effect.apply({}, StatsCollector(), 1, None)

    assert isinstance(result, tuple)
    assert len(result) == 2
    burst, persistent = result
    assert isinstance(burst, dict)
    assert isinstance(persistent, dict)


def test_simple_damage_effect_rolls_damage():
    """Test that SimpleDamageEffect rolls damage correctly."""
    from simulator.legendary_effects.simple_damage_effect import SimpleDamageEffect
    from simulator.stats_collector import StatsCollector
    from simulator.attack_simulator import AttackSimulator
    from simulator.weapon import Weapon
    from simulator.config import Config

    cfg = Config()
    weapon = Weapon('Spear', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    effect = SimpleDamageEffect()
    legend_dict = {
        'proc': 0.05,
        'acid': [[4, 6, 0]],  # 4d6 acid
        'pure': [[4, 6, 0]]   # 4d6 pure
    }

    burst, persistent = effect.apply(legend_dict, stats, 1, attack_sim)

    # Should have burst damage
    assert 'damage_sums' in burst
    assert 'acid' in burst['damage_sums']
    assert 'pure' in burst['damage_sums']
    assert burst['damage_sums']['acid'] > 0
    assert burst['damage_sums']['pure'] > 0

    # Should have no persistent effects
    assert persistent == {}


def test_simple_damage_effect_skips_proc_and_effect_keys():
    """Test that SimpleDamageEffect ignores proc and effect keys."""
    from simulator.legendary_effects.simple_damage_effect import SimpleDamageEffect
    from simulator.stats_collector import StatsCollector
    from simulator.attack_simulator import AttackSimulator
    from simulator.weapon import Weapon
    from simulator.config import Config

    cfg = Config()
    weapon = Weapon('Spear', cfg)
    attack_sim = AttackSimulator(weapon, cfg)

    effect = SimpleDamageEffect()
    legend_dict = {
        'proc': 0.05,
        'effect': 'some_effect',
        'fire': [[1, 50, 0]]
    }

    burst, persistent = effect.apply(legend_dict, StatsCollector(), 1, attack_sim)

    # Should only have fire damage, not proc or effect
    assert 'proc' not in burst['damage_sums']
    assert 'effect' not in burst['damage_sums']
    assert 'fire' in burst['damage_sums']
