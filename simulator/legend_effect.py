from simulator.weapon import Weapon
from simulator.stats_collector import StatsCollector
from simulator.attack_simulator import AttackSimulator
from simulator.legendary_effects import LegendaryEffectRegistry
from copy import deepcopy
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

        self.legend_effect_duration = 5  # Duration of the legendary effect in rounds
        self.legend_attacks_left = 0  # Track remaining attacks that benefit from legendary property

    def legend_proc(self, legend_proc_identifier: float):
        roll_threshold = 100 - (legend_proc_identifier * 100)  # Roll above it triggers the property
        legend_roll = random.randint(1, 100)
        if legend_roll > roll_threshold:
            self.stats.legend_procs += 1
            self.legend_attacks_left = self.attack_sim.attacks_per_round * self.legend_effect_duration  # Reset\apply duration (5 rounds) for some unique properties
            return True
        else:
            return False

    def ab_bonus(self):
        relevant_legend_weapons = ['Darts']
        if (self.legend_attacks_left > 0) and (self.weapon.name_purple in relevant_legend_weapons):
            legend_ab_bonus = 2
        else:
            legend_ab_bonus = 0
        return legend_ab_bonus

    def ac_reduction(self):
        relevant_legend_weapons = ['Light Flail', 'Greatsword_Legion']
        if (self.legend_attacks_left > 0) and (self.weapon.name_purple in relevant_legend_weapons):
            legend_ac_reduction = -2
        else:
            legend_ac_reduction = 0
        return legend_ac_reduction

    def get_legend_damage(self, legend_dict: dict, crit_multiplier: int):
        """
        * Calculate if legend proc is triggered or not (roll based on % of the legend property)
        * Roll and store the damage results
        * Track legend procs for correctly applying unique properties, such as:
            ** Darts' +2 AB
            ** Heavy Flail's +5 Physical damage
            ** Club's reduction of Physical immunities (damage vulnerability)

        :param legend_dict: dict, summary of damage dice per type, e.g., {'proc': 0.05, 'fire': [1, 30, 7], ... , 'effect': 'sunder'}
        :param crit_multiplier: int, the critical multiplier, 1 if ordinary hit, >1 if critical hit
        :return:
            legend_dict_sums: dict, summary of damage to inflict per type, e.g., {'cold': 7, 'pure': 11}
            legend_dmg_common: list, legendary damage that should be added to "common" damage summary,
                               "common" means it must be added to the regular damage totals, before applying immunities
            legend_imm_factors: dict, factor to apply to target's damage immunity\vulnerability
        """
        legend_dict_sums = defaultdict(int)  # Changed from {}
        legend_dmg_common = []          # Store common damage added by legendary proc (e.g., Heavy Flail)
        legend_imm_factors = {}         # Store damage immunity factors

        if not legend_dict:  # If the dict is empty, return empty results
            return legend_dict_sums, legend_dmg_common, legend_imm_factors

        # Legend entries are stored as { 'proc': 0.05, 'fire': [1, 30, 7], ... , 'effect': 'sunder' }
        proc = legend_dict['proc'] if 'proc' in legend_dict.keys() else None

        def add_legend_dmg():
            # Check if weapon has a registered custom effect
            custom_effect = self.registry.get_effect(self.weapon.name_purple)

            if custom_effect:
                effect_result = custom_effect.apply(
                    legend_dict,
                    self.stats,
                    crit_multiplier,
                    self.attack_sim
                )

                # Apply damage from custom effect
                for dmg_type, dmg_value in effect_result.get('damage_sums', {}).items():
                    legend_dict_sums[dmg_type] += dmg_value

                # Handle common damage
                if effect_result.get('common_damage'):
                    legend_dmg_common.extend(effect_result['common_damage'])

                # Handle immunity factors
                legend_imm_factors.update(effect_result.get('immunity_factors', {}))

            else:
                # Default behavior for weapons without custom effects
                for dmg_type, dmg_list in legend_dict.items():
                    if dmg_type in ('proc', 'effect'):
                        continue
                    for dmg_sublist in dmg_list:
                        # dmg_sublist may be [dice, sides] or [dice, sides, flat]
                        num_dice = dmg_sublist[0]
                        num_sides = dmg_sublist[1]
                        flat_dmg = dmg_sublist[2] if len(dmg_sublist) > 2 else 0
                        legend_dict_sums[dmg_type] += self.attack_sim.damage_roll(num_dice, num_sides, flat_dmg)

        def get_immunity_factors():
            # Skip if weapon has custom effect (immunity factors already handled by registry)
            if self.registry.get_effect(self.weapon.name_purple):
                return

            physical_imm_factor_weapons = ['Club_Stone']    # Crushing Blow legendary property, -5% physical immunity
            if self.weapon.name_purple in physical_imm_factor_weapons:
                legend_imm_factors['physical'] = -0.05

        if isinstance(proc, (int, float)):  # Legendary property triggers on-hit, by percentage
            if self.legend_proc(proc): # Check if the legendary property is triggered
                add_legend_dmg()
                get_immunity_factors()

            elif self.legend_attacks_left > 0:
                self.legend_attacks_left = self.legend_attacks_left - 1
                # Heavy Flail continues to apply damage during duration window
                if self.weapon.name_purple == 'Heavy Flail':
                    add_legend_dmg()
                get_immunity_factors()

        elif isinstance (proc, str) and crit_multiplier > 1:    # Legendary property triggers by crit-hit
            self.stats.legend_procs += 1
            add_legend_dmg()

        # Convert back to regular dict before returning
        return dict(legend_dict_sums), legend_dmg_common, legend_imm_factors
