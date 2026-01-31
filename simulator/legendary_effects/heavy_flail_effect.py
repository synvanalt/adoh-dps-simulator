"""Heavy Flail legendary effect implementation."""

from simulator.legendary_effects.base import LegendaryEffect
from simulator.damage_roll import DamageRoll


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
            - persistent: {'common_damage': {'physical': DamageRoll(...)}}
        """
        burst = {}
        persistent = {}

        if 'physical' in legend_dict:
            hflail_phys_roll = legend_dict['physical'][0]  # DamageRoll object

            # Common damage is PERSISTENT (continues during window)
            # Format: Dict[damage_type, DamageRoll]
            persistent['common_damage'] = {'physical': hflail_phys_roll}

        return burst, persistent
