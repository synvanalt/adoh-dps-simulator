"""Simple damage effect for legendary weapons without special mechanics."""

from simulator.legendary_effects.base import LegendaryEffect


class SimpleDamageEffect(LegendaryEffect):
    """Base class for legendary effects that only add burst damage.

    This is used by most legendary weapons (30+ weapons) that just add
    damage when the legendary effect procs, without any special mechanics
    like AB bonuses, AC reduction, or immunity factors.
    """

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        """Roll damage for all damage types in legend_dict.

        Args:
            legend_dict: Dict with damage types as keys, lists of [dice, sides, flat] as values
            stats_collector: StatsCollector (unused for simple damage)
            crit_multiplier: Critical multiplier (unused for simple damage)
            attack_sim: AttackSimulator for rolling damage dice

        Returns:
            (burst_effects, persistent_effects)
            - burst: {'damage_sums': {type: rolled_value}}
            - persistent: {} (no persistent effects for simple damage)
        """
        damage_sums = {}

        for dmg_type, dmg_list in legend_dict.items():
            # Skip non-damage keys
            if dmg_type in ('proc', 'effect'):
                continue

            # Roll damage for each entry of this type
            for dmg_sublist in dmg_list:
                num_dice = dmg_sublist[0]
                num_sides = dmg_sublist[1]
                flat_dmg = dmg_sublist[2] if len(dmg_sublist) > 2 else 0

                damage_sums[dmg_type] = damage_sums.get(dmg_type, 0) + \
                    attack_sim.damage_roll(num_dice, num_sides, flat_dmg)

        burst = {'damage_sums': damage_sums}
        persistent = {}

        return burst, persistent
