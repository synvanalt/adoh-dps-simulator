"""Registry for legendary weapon effects."""

from typing import Dict, Optional
from simulator.legendary_effects.base import LegendaryEffect


class LegendaryEffectRegistry:
    """Registry mapping weapon names to their legendary effect handlers."""

    def __init__(self):
        """Initialize registry with all known legendary effects."""
        self._effects: Dict[str, LegendaryEffect] = {}
        self._register_default_effects()

    def _register_default_effects(self):
        """Register all default legendary effects."""
        from simulator.legendary_effects.burst_damage_effect import BurstDamageEffect
        from simulator.legendary_effects.perfect_strike_effect import PerfectStrikeEffect
        from simulator.legendary_effects.sunder_effect import SunderEffect
        from simulator.legendary_effects.inconsequence_effect import InconsequenceEffect
        from simulator.legendary_effects.heavy_flail_effect import HeavyFlailEffect
        from simulator.legendary_effects.crushing_blow_effect import CrushingBlowEffect

        # Special mechanics effects
        self.register('Darts', PerfectStrikeEffect())
        self.register('Kukri_Crow', PerfectStrikeEffect())

        self.register('Light Flail', SunderEffect())
        self.register('Greatsword_Legion', SunderEffect())

        self.register('Kukri_Inconseq', InconsequenceEffect())
        self.register('Heavy Flail', HeavyFlailEffect())
        self.register('Club_Stone', CrushingBlowEffect())

        # Burst damage-only effects (shared instance for efficiency)
        burst = BurstDamageEffect()

        burst_damage_weapons = [
            'Halberd', 'Spear', 'Trident_Fire', 'Trident_Ice',
            'Dire Mace', 'Double Axe',
            'Heavy Crossbow', 'Light Crossbow',
            'Longbow_FireDragon', 'Longbow_FireCeles',
            'Longbow_ElecDragon', 'Longbow_ElecCeles',
            'Kama', 'Quarterstaff_Hanged', 'Greatsword_Tyr',
            'Bastard Sword_Vald', 'Katana_Kin', 'Katana_Soul',
            'Longsword', 'Rapier_Stinger', 'Rapier_Touch',
            'Warhammer_Mjolnir', 'Club_Fish', 'Dagger_FW',
            'Handaxe_Ichor', 'Light Hammer', 'Mace', 'Whip'
        ]

        for weapon in burst_damage_weapons:
            self.register(weapon, burst)

    def register(self, weapon_name: str, effect: LegendaryEffect):
        """Register a legendary effect for a weapon.

        Args:
            weapon_name: Name of the weapon
            effect: LegendaryEffect implementation
        """
        self._effects[weapon_name] = effect

    def get_effect(self, weapon_name: str) -> Optional[LegendaryEffect]:
        """Get the legendary effect for a weapon.

        Args:
            weapon_name: Name of the weapon

        Returns:
            LegendaryEffect instance or None if weapon has no registered effect
        """
        return self._effects.get(weapon_name)
