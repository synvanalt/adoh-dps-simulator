"""Burst damage effect for legendary weapons without special mechanics."""

from simulator.legendary_effects.base import LegendaryEffect
from simulator.damage_roll import DamageRoll


class BurstDamageEffect(LegendaryEffect):
    """Base class for legendary effects that only add burst damage.

    This is used by most legendary weapons (30+ weapons) that just add
    damage when the legendary effect procs, without any special mechanics
    like AB bonuses, AC reduction, or immunity factors.
    """

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        """Roll damage for all damage types in legend_dict.

        Args:
            legend_dict: Dict with damage types as keys, lists of DamageRoll objects as values
            stats_collector: StatsCollector (unused for burst damage)
            crit_multiplier: Critical multiplier (unused for burst damage)
            attack_sim: AttackSimulator for rolling damage dice

        Returns:
            (burst_effects, persistent_effects)
            - burst: {'damage_sums': {type: rolled_value}}
            - persistent: {} (no persistent effects for burst damage)
        """
        damage_sums = {}

        for dmg_type, dmg_list in legend_dict.items():
            # Skip non-damage keys
            if dmg_type in ('proc', 'effect'):
                continue

            # Roll damage for each DamageRoll in this type
            for dmg_roll in dmg_list:
                damage_sums[dmg_type] = damage_sums.get(dmg_type, 0) + \
                    attack_sim.damage_roll(dmg_roll.dice, dmg_roll.sides, dmg_roll.flat)

        burst = {'damage_sums': damage_sums}
        persistent = {}

        return burst, persistent
