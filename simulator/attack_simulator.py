from copy import deepcopy
from math import floor
from simulator.weapon import Weapon
from simulator.config import Config
from simulator.constants import DOUBLE_SIDED_WEAPONS
import random


class AttackSimulator:
    def __init__(self, weapon_obj: Weapon, config: Config):
        self.cfg = config
        self.weapon = weapon_obj
        self.defender_ac = self.cfg.TARGET_AC
        self.ab_capped = self.cfg.AB_CAPPED
        self.ab = self.calculate_attack_bonus()

        self.dual_wield = False                 # Flag for Dual-Wield attack progression
        self.illegal_dual_wield_config = False  # Flag for illegal Dual-Wield configuration

        self.attack_prog = self.get_attack_progression()
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

    def _is_valid_dw_config(self):
        """
        Check if dual-wielding is valid for character/weapon size combination.

        Valid combinations:
        - Medium: M, S, T, Double-sided
        - Small: S, T
        - Large: M, S

        :return: True if valid, False if illegal configuration
        """
        toon_size = self.cfg.TOON_SIZE
        weapon_size = self.weapon.size

        # Special: Medium can dual-wield double-sided (even though Large)
        if (toon_size == 'M'
            and self.weapon.name_base in DOUBLE_SIDED_WEAPONS
            and not self.cfg.SHAPE_WEAPON_OVERRIDE):
            return True

        # Large weapons cannot be dual-wielded
        if weapon_size == 'L':
            return False

        # Small cannot dual-wield Medium
        if toon_size == 'S' and weapon_size == 'M':
            return False

        # Large cannot dual-wield Tiny
        if toon_size == 'L' and weapon_size == 'T':
            return False

        return True

    def _is_weapon_light(self):
        """
        Determine if the weapon is considered "light" for this character size.

        Light weapon definition:
        - Weapon is smaller than character size
        - Example: Small weapon is light for Medium/Large, but not for Small

        :return: True if light weapon, False otherwise
        """
        size_order = {'T': 0, 'S': 1, 'M': 2, 'L': 3}
        toon_size_value = size_order[self.cfg.TOON_SIZE]
        weapon_size_value = size_order[self.weapon.size]

        return weapon_size_value < toon_size_value

    def calculate_dw_penalties(self):
        """
        Calculate dual-wield attack penalties for primary and off-hand.

        Base penalties (no feats):
        - Light weapon: -4 primary / -8 off-hand
        - Non-light weapon: -6 primary / -10 off-hand

        With Two-Weapon Fighting:
        - Light weapon: -2 primary / -6 off-hand
        - Non-light weapon: -4 primary / -8 off-hand

        With Ambidexterity (requires TWF):
        - Off-hand penalty reduced by 4

        With both TWF + Ambidexterity:
        - Light weapon: -2 primary / -2 off-hand
        - Non-light weapon: -4 primary / -4 off-hand

        :return: Tuple of (primary_penalty, offhand_penalty)
        """
        is_light = self._is_weapon_light()
        has_twf = self.cfg.TWO_WEAPON_FIGHTING
        has_ambi = self.cfg.AMBIDEXTERITY

        # Base penalties
        if is_light:
            primary_penalty = -4
            offhand_penalty = -8
        else:
            primary_penalty = -6
            offhand_penalty = -10

        # Apply Two-Weapon Fighting feat
        if has_twf:
            primary_penalty += 2  # -4 becomes -2, or -6 becomes -4
            offhand_penalty += 2  # -8 becomes -6, or -10 becomes -8

        # Apply Ambidexterity feat (requires TWF to be meaningful)
        if has_twf and has_ambi:
            offhand_penalty += 4  # -6 becomes -2, or -8 becomes -4

        return (primary_penalty, offhand_penalty)

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

    def get_attack_progression(self):
        """
        Determine the attack progression of the character (list of AB). Takes into account:
        - attack_prog_offsets: List of attacks AB offsets, e.g., [0, -5, -10, -15, 'dw_hasted', 0, -5]
        - toon_size: Size of the attacker, in addition to weapon size, it's used to determine Dual-Wield penalty
        :return: List of ABs (after applying the DW penalty if applicable, e.g., [68, 63, 58, 53, 70, 68, 63])
        """

        attack_prog_selected = self.cfg.AB_PROG
        attack_prog_offsets = deepcopy(self.cfg.AB_PROGRESSIONS[attack_prog_selected]) # List of integers, looks like [0, -5, -15, -20, 0]
        toon_size = self.cfg.TOON_SIZE
        dw_penalty = 0  # Default no penalty

        # Apply dual-wield penalty based on character size and weapon size
        if 'Dual-Wield' in attack_prog_selected:
            # Set Dual-Wield flag to True so other methods can use it
            self.dual_wield = True

            # -4 AB penalty cases
            if ((toon_size == 'M' and self.weapon.size == 'M') or
                    (toon_size == 'S' and self.weapon.size == 'S')):
                dw_penalty = -4

            # Special case for Double-Sided weapon
            elif (toon_size == 'M'
                  and self.weapon.name_base in DOUBLE_SIDED_WEAPONS
                  and not self.cfg.SHAPE_WEAPON_OVERRIDE):
                dw_penalty = -2

            # -2 AB penalty cases
            elif ((toon_size == 'L' and self.weapon.size in ['M', 'S', 'T']) or
                  (toon_size == 'M' and self.weapon.size in ['S', 'T']) or
                  (toon_size == 'S' and self.weapon.size == 'T')):
                dw_penalty = -2

            # All other combinations, practically rendering this config useless
            else:
                self.illegal_dual_wield_config = True  # Cannot Dual-Wield with this toon size and weapon size combination
                self.ab = 0  # Set AB to 0 to avoid further errors
                return [0] * len(attack_prog_offsets)  # Return zeroed attack progression to avoid further errors

            # Apply the correct dual-wield AB offsets for additional attacks (Hasted, Flurry of Blows, Blinding Speed)
            if "dw_hasted" in attack_prog_offsets:
                hasted_attack_idx = attack_prog_offsets.index("dw_hasted")  # If DW, Haste attack doesn't suffer penalty
                attack_prog_offsets[hasted_attack_idx] = -1 * dw_penalty

                if ("dw_flurry" in attack_prog_offsets) and ("dw_bspeed" in attack_prog_offsets):
                    flurry_attack_idx = attack_prog_offsets.index("dw_flurry")  # If DW, Flurry should get -5 after Hasted attack
                    attack_prog_offsets[flurry_attack_idx] = -1 * dw_penalty - 5
                    bspeed_attack_idx = attack_prog_offsets.index("dw_bspeed")  # If DW, B.Speed should get -10 after Flurry attack
                    attack_prog_offsets[bspeed_attack_idx] = -1 * dw_penalty - 10

                elif "dw_flurry" in attack_prog_offsets:
                    flurry_attack_idx = attack_prog_offsets.index("dw_flurry")  # If DW, Flurry should get -5 after Hasted attack
                    attack_prog_offsets[flurry_attack_idx] = -1 * dw_penalty - 5

                elif "dw_bspeed" in attack_prog_offsets:
                    bspeed_attack_idx = attack_prog_offsets.index("dw_bspeed")  # If DW, B.Speed should get -5 after Hasted attack
                    attack_prog_offsets[bspeed_attack_idx] = -1 * dw_penalty - 5

            # No 'dw_hasted' marker found in attack progression offsets, but Dual-Wield option was selected (error)
            else:
                raise ValueError("Dual-Wield attack progression is missing 'dw_hasted' marker.")

        # Apply the dual-wield penalty to the main Attack Bonus
        self.ab = self.ab + dw_penalty

        # Build the final attack progression list
        # Convert string markers to numeric offsets (temporary fix until Task 4 refactoring)
        numeric_offsets = []
        for offset in attack_prog_offsets:
            if isinstance(offset, str):
                # String markers for special attacks all get 0 offset for now
                numeric_offsets.append(0)
            else:
                numeric_offsets.append(offset)

        attack_prog = [(self.ab + ab_offset) for ab_offset in numeric_offsets]
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
