"""Sunder legendary effect (-2 AC reduction)."""

from simulator.legendary_effects.burst_damage_effect import BurstDamageEffect


class SunderEffect(BurstDamageEffect):
    """Sunder: Burst damage + persistent -2 AC reduction.

    Used by legendary weapons that reduce target AC by 2 during the
    legendary effect duration window (5 rounds).
    """

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        """Apply Sunder effect.

        Returns:
            (burst_effects, persistent_effects)
            - burst: damage from parent BurstDamageEffect
            - persistent: {'ac_reduction': -2}
        """
        # Get standard burst damage from parent
        burst, persistent = super().apply(legend_dict, stats_collector,
                                         crit_multiplier, attack_sim)

        # Add persistent AC reduction
        persistent['ac_reduction'] = -2

        return burst, persistent
