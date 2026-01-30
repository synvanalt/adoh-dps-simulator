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
    """DEPRECATED: Use test_heavy_flail_effect_returns_persistent_common_damage instead.

    This test is kept for backwards compatibility but tests the old behavior.
    """
    stats = StatsCollector()
    effect = HeavyFlailEffect()

    legend_dict = {
        'proc': 0.05,
        'physical': [[0, 0, 5]]
    }

    burst, persistent = effect.apply(legend_dict, stats, crit_multiplier=1, attack_sim=None)

    # Old test updated to use new tuple interface
    assert 'common_damage' in persistent
    assert persistent['common_damage'] == [0, 0, 5, 'physical']


def test_crushing_blow_effect_reduces_physical_immunity():
    """DEPRECATED: Use test_crushing_blow_returns_damage_and_immunity instead.

    This test is kept for backwards compatibility but tests the old behavior.
    """
    stats = StatsCollector()
    effect = CrushingBlowEffect()

    legend_dict = {
        'proc': 0.20,
    }

    burst, persistent = effect.apply(legend_dict, stats, crit_multiplier=1, attack_sim=None)

    # Old test updated to use new tuple interface
    assert 'immunity_factors' in persistent
    assert persistent['immunity_factors'] == {'physical': -0.05}
    assert burst['damage_sums'] == {}


def test_heavy_flail_effect_returns_persistent_common_damage():
    """Test that Heavy Flail returns common_damage as persistent effect."""
    from simulator.legendary_effects.heavy_flail_effect import HeavyFlailEffect
    from simulator.stats_collector import StatsCollector

    stats = StatsCollector()
    effect = HeavyFlailEffect()

    legend_dict = {
        'proc': 0.05,
        'physical': [[0, 0, 5]]
    }

    burst, persistent = effect.apply(legend_dict, stats, 1, None)

    # Should have NO burst damage (Heavy Flail is pure persistent)
    assert burst == {}

    # Should have persistent common_damage
    assert 'common_damage' in persistent
    assert persistent['common_damage'] == [0, 0, 5, 'physical']


def test_crushing_blow_returns_damage_and_immunity():
    """Test that Crushing Blow returns damage and immunity factor."""
    from simulator.legendary_effects.crushing_blow_effect import CrushingBlowEffect
    from simulator.stats_collector import StatsCollector
    from simulator.attack_simulator import AttackSimulator
    from simulator.weapon import Weapon
    from simulator.config import Config

    cfg = Config()
    weapon = Weapon('Club_Stone', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    effect = CrushingBlowEffect()
    legend_dict = {
        'proc': 0.05,
        'effect': 'crushing_blow'
    }

    burst, persistent = effect.apply(legend_dict, stats, 1, attack_sim)

    # Should have burst damage from legend_dict (if any damage types present)
    # Note: This specific legend_dict has no damage, so damage_sums will be empty
    assert 'damage_sums' in burst

    # Should have persistent immunity factor
    assert 'immunity_factors' in persistent
    assert persistent['immunity_factors'] == {'physical': -0.05}


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


def test_perfect_strike_effect_adds_ab_bonus():
    """Test that PerfectStrikeEffect adds +2 AB bonus as persistent effect."""
    from simulator.legendary_effects.perfect_strike_effect import PerfectStrikeEffect
    from simulator.stats_collector import StatsCollector
    from simulator.attack_simulator import AttackSimulator
    from simulator.weapon import Weapon
    from simulator.config import Config

    cfg = Config()
    weapon = Weapon('Darts', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    effect = PerfectStrikeEffect()
    legend_dict = {
        'proc': 0.05,
        'pure': [[4, 6, 0]]
    }

    burst, persistent = effect.apply(legend_dict, stats, 1, attack_sim)

    # Should have burst damage (from parent SimpleDamageEffect)
    assert 'damage_sums' in burst
    assert 'pure' in burst['damage_sums']

    # Should have persistent AB bonus
    assert 'ab_bonus' in persistent
    assert persistent['ab_bonus'] == 2


def test_sunder_effect_adds_ac_reduction():
    """Test that SunderEffect adds -2 AC reduction as persistent effect."""
    from simulator.legendary_effects.sunder_effect import SunderEffect
    from simulator.stats_collector import StatsCollector
    from simulator.attack_simulator import AttackSimulator
    from simulator.weapon import Weapon
    from simulator.config import Config

    cfg = Config()
    weapon = Weapon('Light Flail', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    effect = SunderEffect()
    legend_dict = {
        'proc': 0.05,
        'effect': 'sunder'
    }

    burst, persistent = effect.apply(legend_dict, stats, 1, attack_sim)

    # Should have persistent AC reduction
    assert 'ac_reduction' in persistent
    assert persistent['ac_reduction'] == -2


def test_inconsequence_effect_random_damage():
    """Test that InconsequenceEffect applies random Pure/Sonic/nothing."""
    from simulator.legendary_effects.inconsequence_effect import InconsequenceEffect
    from simulator.stats_collector import StatsCollector
    from simulator.attack_simulator import AttackSimulator
    from simulator.weapon import Weapon
    from simulator.config import Config

    cfg = Config()
    weapon = Weapon('Kukri_Inconseq', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    effect = InconsequenceEffect()
    legend_dict = {
        'proc': 'on_crit',
        'effect': 'inconsequence'
    }

    # Run multiple times to test randomness
    results = {'pure': 0, 'sonic': 0, 'nothing': 0}

    for _ in range(100):
        burst, persistent = effect.apply(legend_dict, stats, 2, attack_sim)

        damage_sums = burst.get('damage_sums', {})

        if 'pure' in damage_sums:
            results['pure'] += 1
            assert damage_sums['pure'] > 0
        elif 'sonic' in damage_sums:
            results['sonic'] += 1
            assert damage_sums['sonic'] > 0
        else:
            results['nothing'] += 1

        # Should have no persistent effects
        assert persistent == {}

    # Rough probability check (25% each, 50% nothing)
    # Allow wide range due to randomness
    assert 10 < results['pure'] < 40
    assert 10 < results['sonic'] < 40
    assert 30 < results['nothing'] < 70


def test_registry_has_all_legendary_weapons():
    """Verify that all legendary weapons have registered effects."""
    from simulator.legendary_effects.registry import LegendaryEffectRegistry
    from weapons_db import PURPLE_WEAPONS

    registry = LegendaryEffectRegistry()

    # Get all legendary weapons from weapons_db
    legendary_weapons = []
    for weapon_name, props in PURPLE_WEAPONS.items():
        if 'legendary' in props:
            legendary_weapons.append(weapon_name)

    # Verify each has a registered effect
    missing = []
    for weapon_name in legendary_weapons:
        if registry.get_effect(weapon_name) is None:
            missing.append(weapon_name)

    assert len(missing) == 0, f"Missing effects for: {missing}"
