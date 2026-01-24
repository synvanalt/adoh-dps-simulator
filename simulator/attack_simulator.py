from copy import deepcopy
from math import floor
from simulator.weapon import Weapon
from simulator.config import Config
import random


class AttackSimulator:
    def __init__(self, weapon_obj: Weapon, config: Config):
        self.cfg = config
        self.weapon = weapon_obj
        self.defender_ac = self.cfg.TARGET_AC
        self.ab_capped = self.cfg.AB_CAPPED
        self.ab = self.calculate_attack_bonus()

        attack_prog_selected = self.cfg.AB_PROG
        attack_prog_temp = deepcopy(self.cfg.AB_PROGRESSIONS[attack_prog_selected]) # List of integers, looks like [0, -5, -15, -20, 0]
        self.dual_wield = True if 'Dual-Wield' in attack_prog_selected else False   # Boolean for Dual-Wield state
        if self.dual_wield:     # Get Dual-Wield penalty and apply to attack_prog
            attack_prog_temp = self.apply_dual_wield_penalty(attack_prog_temp, self.cfg.TOON_SIZE)

        self.attack_prog = [(self.ab + ab_offset) for ab_offset in attack_prog_temp]
        self.attacks_per_round = len(self.attack_prog)

        (self.hit_chance_list, self.crit_chance_list, self.noncrit_chance_list) = self.calculate_hit_chances()

    def calculate_attack_bonus(self):
        """Calculate the attack bonus (AB) based on weapon enhancement and cap it if necessary"""
        if self.weapon.purple_props['enhancement'] > 7:     # Handle special weapons, e.g., Scythe +10 Enhancement
            ab = self.cfg.AB + (self.weapon.purple_props['enhancement'] - 7)
            ab = min(ab, self.ab_capped)
        elif (self.cfg.DAMAGE_VS_RACE
              and self.weapon.vs_race_key in self.weapon.purple_props
              and 'enhancement' in self.weapon.purple_props[self.weapon.vs_race_key]):
            ab = self.cfg.AB + (self.weapon.purple_props[self.weapon.vs_race_key]['enhancement'] - 7)
            ab = min(ab, self.ab_capped)
        else:
            ab = self.cfg.AB
        return ab

    def calculate_hit_chances(self):
        """
        Total average chance to hit for all attacks in round.

        About the hit_chance calculation:
        (21 + attack_bonus - armor_class) calculates how many rolls will succeed (meets it = beats it).
        Multiply by 0.05 to get the percentage (since each roll represents 5% of a 1d20).
        min(0.95, ...) ensures the hit chance doesn't exceed 95% (because a natural 1 is always a miss).
        max(0.05, ...) ensures the hit chance doesn't go below 5% (because a natural 20 is always a hit).
        """
        # Initialize lists to store chances for hit\crit-hit per attack in AB progression:
        hit_chance_list = []        # Chance to hit defender per attack, either crit or non-crit (chance for both)
        crit_chance_list = []       # Chance to crit-hit defender per attack
        noncrit_chance_list = []    # Chance to non-crit-hit defender per attack, i.e., P(hit) - P(crit-hit)

        # Calculate the chance for -attempting- a critical-hit threat roll:
        threat_range_max = 20
        threat_roll_chance = (threat_range_max - self.weapon.crit_threat + 1) * 0.05

        for ab in self.attack_prog:
            hit_chance = max(0.05, min(0.95, (21 + ab - self.defender_ac) * 0.05))
            hit_chance_list.append(hit_chance)

            threat_hit_chance = max(0.0, min(1.0, (21 + ab - self.defender_ac) * 0.05))

            # Every roll that is in the threat-range hits the target and qualifies for threat roll attempt:
            if hit_chance >= threat_roll_chance:
                crit_chance = threat_roll_chance * threat_hit_chance
                crit_chance_list.append(crit_chance)

                noncrit_chance = hit_chance - crit_chance
                noncrit_chance_list.append(noncrit_chance)

            # Some rolls in the threat-range MISS the target, therefore do not qualify for threat roll attempt:
            else:
                crit_chance = hit_chance * threat_hit_chance
                crit_chance_list.append(crit_chance)

                noncrit_chance = hit_chance - crit_chance
                noncrit_chance_list.append(noncrit_chance)

        return hit_chance_list, crit_chance_list, noncrit_chance_list

    def get_hit_chance(self):   # Hit % out of total attempts
        return sum(self.hit_chance_list) / len(self.hit_chance_list)

    def get_crit_chance(self):  # Crit % out of total attempts
        return sum(self.crit_chance_list) / len(self.crit_chance_list)

    def get_noncrit_chance(self):
        return sum(self.noncrit_chance_list) / len(self.noncrit_chance_list)

    def get_legend_proc_rate_theoretical(self):
        """
        :return: The theoretical chance to trigger a legend proc, based on the weapon's legend property
        """
        legend_proc_rate = 0.0
        purple_props = self.weapon.purple_props
        legendary = purple_props.get('legendary') if isinstance(purple_props, dict) else None
        if legendary:
            proc = legendary.get('proc')
            if isinstance(proc, (float, int)):  # Proc is percentage (numeric)
                legend_proc_rate = float(proc)
            elif isinstance(proc, str):         # Proc is 'on_crit'
                legend_proc_rate = self.get_crit_chance() / self.get_hit_chance()   # Crit % out of total HITS
            else:
                legend_proc_rate = 0.0

        return legend_proc_rate

    def apply_dual_wield_penalty(self, attack_prog: list, toon_size: str):
        """
        Determine the Dual-Wield penalty and apply it to list of attacks AB offsets
        :param attack_prog: List of Dual-Wield attacks AB offsets, e.g., [0, -5, -10, -15, 'dw_hasted', 0, -5]
        :param toon_size: Size of the attacker, in addition to weapon size, it's used to determine the DW penalty
        :return: List after applying the DW penalty, e.g., [-2, -7, -12, -17, 2, -2, -7]
        """
        double_sided_weapons = ['Dire Mace', 'Double Axe', 'Two-Bladed Sword']

        if ((toon_size == 'M' and self.weapon.size == 'M') or
                (toon_size == 'S' and self.weapon.size == 'S')):
            dw_penalty = -4
        elif toon_size == 'M' and self.weapon.name_base in double_sided_weapons:    # Special case for Double-Sided weapon
            dw_penalty = -2
        elif ((toon_size == 'L' and self.weapon.size in ['M', 'S', 'T']) or
              (toon_size == 'M' and self.weapon.size in ['S', 'T']) or
              (toon_size == 'S' and self.weapon.size == 'T')):
            dw_penalty = -2
        else:  # All other combinations, practically rendering this config useless
            dw_penalty = -99  # Cannot Dual-Wield with this toon size and weapon size combination

        if "dw_hasted" in attack_prog:
            hasted_attack_idx = attack_prog.index("dw_hasted")  # If DW, Haste attack doesn't suffer penalty
            attack_prog[hasted_attack_idx] = -1 * dw_penalty

            if ("dw_flurry" in attack_prog) and ("dw_bspeed" in attack_prog):
                flurry_attack_idx = attack_prog.index("dw_flurry")  # If DW, Flurry should get -5 after Hasted attack
                attack_prog[flurry_attack_idx] = -1 * dw_penalty - 5
                bspeed_attack_idx = attack_prog.index("dw_bspeed")  # If DW, B.Speed should get -10 after Flurry attack
                attack_prog[bspeed_attack_idx] = -1 * dw_penalty - 10

            elif "dw_flurry" in attack_prog:
                flurry_attack_idx = attack_prog.index("dw_flurry")  # If DW, Flurry should get -5 after Hasted attack
                attack_prog[flurry_attack_idx] = -1 * dw_penalty - 5

            elif "dw_bspeed" in attack_prog:
                bspeed_attack_idx = attack_prog.index("dw_bspeed")  # If DW, B.Speed should get -5 after Hasted attack
                attack_prog[bspeed_attack_idx] = -1 * dw_penalty - 5

        else:
            raise ValueError("Dual-Wield attack progression is missing 'dw_hasted' marker.")

        self.ab = self.ab + dw_penalty
        return attack_prog

    def attack_roll(self, attacker_ab: int, defender_ac_modifier: int = 0):
        """
        :param attacker_ab: AB of attacker
        :param defender_ac_modifier: AC modifier of the defender, e.g., -2 for legendary Sunder effect
        :return: String that specifies: 'miss', 'hit', 'critical_hit', and the d20 roll result
        """
        roll = random.randint(1, 20)        # Roll a 1d20
        defender_ac = self.defender_ac + defender_ac_modifier
        if roll == 1:                             # Auto-miss on a natural 1
            return 'miss', roll
        elif (roll + attacker_ab) >= defender_ac or roll == 20:       # Check if a hit or miss, auto-hit on a natural 20
            if roll >= self.weapon.crit_threat:
                # Threat roll does not auto-hit if a natural 20 is rolled, nor does it auto-miss if a natural 1 is rolled:
                threat_roll = random.randint(1, 20)
                threat_hit = (threat_roll + attacker_ab) >= defender_ac  # Boolean, True if Threat roll succeeds, False otherwise
                return 'critical_hit' if threat_hit is True else 'hit', roll
            else:
                return 'hit', roll
        else:
            return 'miss', roll

    @staticmethod
    def damage_roll(num_dice: int, num_sides: int, flat_dmg: int):
        """
        :param num_dice: The number of dice to roll, e.g., in 2d6 this value is 2
        :param num_sides: The number of sides of the die, e.g., in 2d6 this value is 6
        :param flat_dmg: Flat damage to be added to the roll, e.g., in 2d6+3 this value is 3
        :return: int, Damage roll results
        """
        if num_dice == 0 or num_sides == 0:  # no roll is performed, return only flat damage
            return flat_dmg
        else:
            total_dmg_roll = 0
            for i in range(num_dice):
                dmg_roll = random.randint(1, num_sides)
                total_dmg_roll += dmg_roll
            return total_dmg_roll + flat_dmg

    def damage_immunity_reduction(self, damage_sums: dict, imm_factors: dict):
        """
        This method is relevant only for the ROLL implementation
        :param damage_sums: Dictionary holding a sum of the total damage inflicted, per damage type, e.g., {'divine': 10}
        :param imm_factors: Dictionary holding the target immunity factors (for example -0.1 (10%) due to legend property
        :return: Damage to be inflicted after applying target immunities, e.g., if 10% divine, the final damage will be 9
        """
        target_imms = deepcopy(self.cfg.TARGET_IMMUNITIES)
        for dmg_type_name, imm_factor in imm_factors.items():
            current_imm = target_imms[dmg_type_name]
            target_imms[dmg_type_name] = current_imm + imm_factor

        for dmg_type_name, dmg_value in damage_sums.items():
            dmg_name_dict = {
                'fire_fw': 'fire',    # Fire from Flame Weapon is treated as normal fire damage for immunities
                'slashing': 'physical',
                'piercing': 'physical',
                'bludgeoning': 'physical'
            }
            corrected_dmg_type_name = dmg_name_dict.get(dmg_type_name, dmg_type_name)

            if corrected_dmg_type_name not in target_imms.keys():
                raise KeyError(f"Damage type '{corrected_dmg_type_name}' not found in TARGET_IMMUNITIES dictionary.")

            elif target_imms[corrected_dmg_type_name] > 0:  # Damage Immunity (Reduction)
                dmg_reduced = floor(dmg_value * target_imms[corrected_dmg_type_name])
                dmg_reduced = 1 if dmg_reduced < 1 else dmg_reduced
                dmg_after_immunity = max(0, dmg_value - dmg_reduced)

            elif target_imms[corrected_dmg_type_name] < 0:   # Damage Vulnerability
                dmg_added = floor(abs(dmg_value * target_imms[corrected_dmg_type_name]))
                dmg_after_immunity = dmg_value + dmg_added

            else:   # Immunity is 0%, No Immunity or Vulnerability
                dmg_after_immunity = dmg_value

            damage_sums[dmg_type_name] = dmg_after_immunity

        return damage_sums
