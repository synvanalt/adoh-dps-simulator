"""Inconsequence legendary effect (random Pure/Sonic/nothing)."""

import random
from simulator.legendary_effects.burst_damage_effect import BurstDamageEffect


class InconsequenceEffect(BurstDamageEffect):
    """Inconsequence: Random damage effect.

    25% chance: 4d6 Pure damage
    25% chance: 4d6 Sonic damage
    50% chance: Nothing happens
    """

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        """Apply Inconsequence effect with random outcome.

        Returns:
            (burst_effects, persistent_effects)
            - burst: {'damage_sums': {type: value}} or empty
            - persistent: {} (no persistent effects)
        """
        damage_sums = {}
        roll = random.random()  # 0.0 to 1.0

        if roll < 0.25:  # 25% Pure damage
            damage_sums['pure'] = attack_sim.damage_roll(4, 6, 0)
        elif roll < 0.50:  # 25% Sonic damage
            damage_sums['sonic'] = attack_sim.damage_roll(4, 6, 0)
        # else: 50% nothing happens

        burst = {'damage_sums': damage_sums}
        persistent = {}

        return burst, persistent
