"""Club_Stone (Crushing Blow) legendary effect implementation."""

from simulator.legendary_effects.simple_damage_effect import SimpleDamageEffect


class CrushingBlowEffect(SimpleDamageEffect):
    """Crushing Blow: Burst damage + persistent -5% physical immunity.

    Reduces target's physical immunity by 5% during the legendary
    effect duration window (5 rounds).
    """

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        """Apply Crushing Blow effect.

        Returns:
            (burst_effects, persistent_effects)
            - burst: damage from parent SimpleDamageEffect
            - persistent: {'immunity_factors': {'physical': -0.05}}
        """
        # Get standard burst damage from parent
        burst, persistent = super().apply(legend_dict, stats_collector,
                                         crit_multiplier, attack_sim)

        # Add persistent immunity reduction
        persistent['immunity_factors'] = {'physical': -0.05}

        return burst, persistent
