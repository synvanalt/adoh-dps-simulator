"""Perfect Strike legendary effect (+2 AB bonus)."""

from simulator.legendary_effects.simple_damage_effect import SimpleDamageEffect


class PerfectStrikeEffect(SimpleDamageEffect):
    """Perfect Strike: Burst damage + persistent +2 AB bonus.

    Used by legendary weapons that grant +2 AB bonus during the
    legendary effect duration window (5 rounds).
    """

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        """Apply Perfect Strike effect.

        Returns:
            (burst_effects, persistent_effects)
            - burst: damage from parent SimpleDamageEffect
            - persistent: {'ab_bonus': 2}
        """
        # Get standard burst damage from parent
        burst, persistent = super().apply(legend_dict, stats_collector,
                                         crit_multiplier, attack_sim)

        # Add persistent AB bonus
        persistent['ab_bonus'] = 2

        return burst, persistent
