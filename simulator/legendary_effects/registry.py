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
        from simulator.legendary_effects.heavy_flail_effect import HeavyFlailEffect
        from simulator.legendary_effects.crushing_blow_effect import CrushingBlowEffect

        self.register('Heavy Flail', HeavyFlailEffect())
        self.register('Club_Stone', CrushingBlowEffect())

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
            LegendaryEffect instance or None if weapon has no special effect
        """
        return self._effects.get(weapon_name)
