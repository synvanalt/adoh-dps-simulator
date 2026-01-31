from simulator.weapon import Weapon
from simulator.stats_collector import StatsCollector
from simulator.attack_simulator import AttackSimulator
from simulator.legendary_effects import LegendaryEffectRegistry
from simulator.constants import LEGEND_EFFECT_DURATION
from collections import defaultdict
import random


class LegendEffect:
    _registry = None  # Class-level shared registry

    def __init__(self, stats_obj: StatsCollector, weapon_obj: Weapon, attack_sim: AttackSimulator):
        self.stats = stats_obj
        self.weapon = weapon_obj
        self.attack_sim = attack_sim

        # Initialize shared registry once
        if LegendEffect._registry is None:
            LegendEffect._registry = LegendaryEffectRegistry()

        self.registry = LegendEffect._registry

        self.legend_effect_duration = LEGEND_EFFECT_DURATION  # Use constant from simulator/constants.py
        self.legend_attacks_left = 0  # Track remaining attacks that benefit from legendary property

        # State for persistent effects
        self._current_ab_bonus = 0
        self._current_ac_reduction = 0

    # Determine if legendary property procs on hit
    def legend_proc(self, legend_proc_identifier: float):
        roll_threshold = 100 - (legend_proc_identifier * 100)  # Roll above it triggers the property
        legend_roll = random.randint(1, 100)
        if legend_roll > roll_threshold:
            return True
        else:
            return False

    @property
    def ab_bonus(self) -> int:
        """Get current AB bonus from legendary effect."""
        return getattr(self, '_current_ab_bonus', 0)

    @property
    def ac_reduction(self) -> int:
        """Get current AC reduction from legendary effect."""
        return getattr(self, '_current_ac_reduction', 0)

    def get_legend_damage(self, legend_dict: dict, crit_multiplier: int):
        """Calculate legendary damage with two-phase effect system.

        Phase 1 - On Proc: Apply burst + persistent effects
        Phase 2 - During Window: Apply only persistent effects

        Returns:
            legend_dict_sums: Dict of burst damage by type
            legend_dmg_common: List of persistent common damage
            legend_imm_factors: Dict of persistent immunity factors
        """
        legend_dict_sums = defaultdict(int)
        legend_dmg_common = []
        legend_imm_factors = {}

        # Reset persistent effects
        self._current_ab_bonus = 0
        self._current_ac_reduction = 0

        if not legend_dict:  # If the dict is empty, return empty results
            return dict(legend_dict_sums), legend_dmg_common, legend_imm_factors

        proc = legend_dict.get('proc')
        custom_effect = self.registry.get_effect(self.weapon.name_purple)

        if not custom_effect:
            # No registered effect - weapon has no legendary property
            return dict(legend_dict_sums), legend_dmg_common, legend_imm_factors

        # Legendary property triggers on-hit, by percentage
        if isinstance(proc, (int, float)):
            # Phase 1: Just procced
            if self.legend_proc(proc):
                self.stats.legend_procs += 1    # Update proc count
                self.legend_attacks_left = self.attack_sim.attacks_per_round * self.legend_effect_duration  # Reset/apply duration (5 rounds)

                # Get legendary effects outcomes
                burst, persistent = custom_effect.apply(
                    legend_dict, self.stats, crit_multiplier, self.attack_sim)

                # Apply BOTH burst and persistent
                self._apply_effects(burst, persistent, legend_dict_sums,
                                  legend_dmg_common, legend_imm_factors)

            # Phase 2: During window
            elif self.legend_attacks_left > 0:
                self.legend_attacks_left -= 1   # Decrement remaining attacks

                # Get legendary effects outcomes
                burst, persistent = custom_effect.apply(
                    legend_dict, self.stats, crit_multiplier, self.attack_sim)

                # Apply ONLY persistent (ignore burst)
                self._apply_effects({}, persistent, legend_dict_sums,
                                  legend_dmg_common, legend_imm_factors)

        # Legendary property triggers on crit-hit
        elif isinstance(proc, str) and crit_multiplier > 1:
            self.stats.legend_procs += 1    # Update proc count

            # Get legendary effects outcomes
            burst, persistent = custom_effect.apply(
                legend_dict, self.stats, crit_multiplier, self.attack_sim)

            # Apply BOTH burst and persistent
            self._apply_effects(burst, persistent, legend_dict_sums,
                              legend_dmg_common, legend_imm_factors)

        # Convert back to regular dict before returning
        return dict(legend_dict_sums), legend_dmg_common, legend_imm_factors

    def _apply_effects(self, burst, persistent, legend_dict_sums,
                       legend_dmg_common, legend_imm_factors):
        """Helper to apply burst and persistent effects.

        Args:
            burst: Dict with 'damage_sums' key
            persistent: Dict with 'common_damage', 'immunity_factors', 'ab_bonus', 'ac_reduction' keys
            legend_dict_sums: defaultdict to accumulate damage
            legend_dmg_common: List to extend with common damage
            legend_imm_factors: Dict to update with immunity factors
        """
        # Apply burst damage
        for dmg_type, dmg_value in burst.get('damage_sums', {}).items():
            legend_dict_sums[dmg_type] += dmg_value

        # Apply persistent effects
        if persistent.get('common_damage'):
            legend_dmg_common.extend(persistent['common_damage'])

        legend_imm_factors.update(persistent.get('immunity_factors', {}))

        # Store for property access
        self._current_ab_bonus = persistent.get('ab_bonus', 0)
        self._current_ac_reduction = persistent.get('ac_reduction', 0)
