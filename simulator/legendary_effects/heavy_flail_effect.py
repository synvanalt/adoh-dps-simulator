"""Heavy Flail legendary effect implementation."""

from copy import deepcopy
from simulator.legendary_effects.base import LegendaryEffect


class HeavyFlailEffect(LegendaryEffect):
    """Heavy Flail adds physical damage to common damage pool."""

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        """Heavy Flail's 5 bludgeoning damage is added as 'common' damage.

        Common damage is added to regular damage totals before applying immunities.
        """
        result = {
            'damage_sums': {},
            'common_damage': None,
            'immunity_factors': {},
        }

        if 'physical' in legend_dict:
            hflail_phys_dmg = deepcopy(legend_dict['physical'][0])
            # hflail_phys_dmg is [dice, sides, flat] or [dice, sides, flat, proc]
            common_dmg = list(hflail_phys_dmg)

            # Remove proc (last element) if present and append damage type
            if len(common_dmg) > 3:
                common_dmg.pop(-1)
            common_dmg.append('physical')

            result['common_damage'] = common_dmg

        return result
