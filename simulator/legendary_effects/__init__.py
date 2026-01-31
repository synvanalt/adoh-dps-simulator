"""Legendary weapon effects system."""

from simulator.legendary_effects.base import LegendaryEffect
from simulator.legendary_effects.registry import LegendaryEffectRegistry
from simulator.legendary_effects.burst_damage_effect import BurstDamageEffect
from simulator.legendary_effects.perfect_strike_effect import PerfectStrikeEffect
from simulator.legendary_effects.sunder_effect import SunderEffect
from simulator.legendary_effects.inconsequence_effect import InconsequenceEffect
from simulator.legendary_effects.heavy_flail_effect import HeavyFlailEffect
from simulator.legendary_effects.crushing_blow_effect import CrushingBlowEffect

__all__ = [
    'LegendaryEffect',
    'LegendaryEffectRegistry',
    'BurstDamageEffect',
    'PerfectStrikeEffect',
    'SunderEffect',
    'InconsequenceEffect',
    'HeavyFlailEffect',
    'CrushingBlowEffect',
]
