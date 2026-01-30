import pytest
from simulator.legendary_effects.base import LegendaryEffect
from simulator.legendary_effects.registry import LegendaryEffectRegistry
from simulator.legendary_effects.heavy_flail_effect import HeavyFlailEffect
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
