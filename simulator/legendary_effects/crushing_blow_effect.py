"""Club_Stone (Crushing Blow) legendary effect implementation."""

from simulator.legendary_effects.base import LegendaryEffect


class CrushingBlowEffect(LegendaryEffect):
    """Club_Stone reduces target's physical immunity by 5%."""

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        """Apply -5% physical immunity on proc."""
        result = {
            'damage_sums': {},
            'common_damage': None,
            'immunity_factors': {'physical': -0.05},
        }

        return result
