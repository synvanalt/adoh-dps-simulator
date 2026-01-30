"""Heavy Flail legendary effect implementation."""

from copy import deepcopy
from simulator.legendary_effects.base import LegendaryEffect


class HeavyFlailEffect(LegendaryEffect):
    """Heavy Flail: Persistent +5 physical damage as common damage.

    Unlike other effects, Heavy Flail adds NO burst damage.
    It only adds persistent common_damage that continues throughout
    the legendary window (5 rounds).
    """

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        """Heavy Flail's 5 physical damage is added as persistent common damage.

        Common damage is added to regular damage totals before applying immunities
        and persists throughout the legendary effect duration window.

        Returns:
            (burst_effects, persistent_effects)
            - burst: {} (no burst damage)
            - persistent: {'common_damage': [0, 0, 5, 'physical']}
        """
        burst = {}
        persistent = {}

        if 'physical' in legend_dict:
            hflail_phys_dmg = deepcopy(legend_dict['physical'][0])
            # hflail_phys_dmg is [dice, sides, flat] or [dice, sides, flat, proc]
            common_dmg = list(hflail_phys_dmg)

            # Remove proc (last element) if present
            if len(common_dmg) > 3:
                common_dmg.pop(-1)

            # Add damage type at end: [dice, sides, flat, type]
            common_dmg.append('physical')

            # Common damage is PERSISTENT (continues during window)
            persistent['common_damage'] = common_dmg

        return burst, persistent
