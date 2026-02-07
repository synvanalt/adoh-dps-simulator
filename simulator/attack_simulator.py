from copy import deepcopy
from math import floor
from simulator.weapon import Weapon
from simulator.config import Config
from simulator.constants import DOUBLE_SIDED_WEAPONS, AUTO_MIGHTY_WEAPONS, AMMO_BASED_WEAPONS
import random


class AttackSimulator:
    def __init__(self, weapon_obj: Weapon, config: Config, offhand_weapon_obj: Weapon = None):
        self.cfg = config
        self.weapon = weapon_obj
        self.offhand_weapon = offhand_weapon_obj  # Custom offhand weapon (can be None)
        self.defender_ac = self.cfg.TARGET_AC
        self.ab_capped = self.cfg.AB_CAPPED
        self.ab = self.calculate_attack_bonus()

        # Calculate offhand AB if custom offhand is enabled
        self.offhand_ab = self._calculate_offhand_ab()
        self.offhand_ab_capped = self._calculate_offhand_ab_capped()

        self.dual_wield = False                # Flag for Dual-Wield attack progression
        self.valid_dual_wield_config = True    # Flag for valid Dual-Wield configuration

        # Track offhand attack indices for DamageSimulator
        self.offhand_attack_indices = []

        self.attack_prog = self.get_attack_progression()
        self.attacks_per_round = len(self.attack_prog)

        (self.hit_chance_list, self.crit_chance_list, self.noncrit_chance_list) = self.calculate_hit_chances()

    def _calculate_ab_for_weapon(self, weapon: Weapon, base_ab: int, ab_cap: int) -> int:
        """Calculate attack bonus for a given weapon, applying enhancement bonuses and cap.

        Args:
            weapon: The weapon to calculate AB for
            base_ab: The base attack bonus before weapon enhancements
            ab_cap: The maximum AB cap to apply

        Returns:
            The calculated attack bonus, capped appropriately
        """
        if weapon.purple_props['enhancement'] > 7:
            ab = base_ab + (weapon.purple_props['enhancement'] - 7)
            return min(ab, ab_cap)
        elif (self.cfg.DAMAGE_VS_RACE
              and weapon.vs_race_key in weapon.purple_props
              and 'enhancement' in weapon.purple_props[weapon.vs_race_key]):
            ab = base_ab + (weapon.purple_props[weapon.vs_race_key]['enhancement'] - 7)
            return min(ab, ab_cap)
        else:
            return base_ab

    def calculate_attack_bonus(self):
        """Calculate the attack bonus (AB) based on weapon enhancement and cap it if necessary"""
        return self._calculate_ab_for_weapon(self.weapon, self.cfg.AB, self.ab_capped)

    def _calculate_offhand_ab(self):
        """Calculate the offhand AB, using the same logic as mainhand."""
        if not self.cfg.DUAL_WIELD:
            return self.ab

        # Determine base AB for offhand
        base_offhand_ab = self.cfg.OFFHAND_AB if self.cfg.CUSTOM_OFFHAND_AB else self.cfg.AB
        offhand_ab_cap = self._calculate_offhand_ab_capped()

        # Apply enhancement bonus from offhand weapon if custom offhand is enabled
        if self.cfg.CUSTOM_OFFHAND_WEAPON and self.offhand_weapon:
            return self._calculate_ab_for_weapon(self.offhand_weapon, base_offhand_ab, offhand_ab_cap)

        return base_offhand_ab

    def _calculate_offhand_ab_capped(self):
        """Calculate the offhand AB cap based on mainhand AB cap and custom offhand AB."""
        if not self.cfg.CUSTOM_OFFHAND_AB:
            return self.ab_capped

        # OFFHAND_AB_CAPPED = AB_CAPPED - (AB - OFFHAND_AB)
        return self.ab_capped - (self.cfg.AB - self.cfg.OFFHAND_AB)

    def _get_offhand_weapon_size(self):
        """Get the size of the offhand weapon."""
        if self.cfg.CUSTOM_OFFHAND_WEAPON and self.offhand_weapon:
            return self.offhand_weapon.size
        return self.weapon.size  # Same as mainhand if no custom offhand

    def _is_valid_dw_config(self):
        """
        Check if dual-wielding is valid for character/weapon size combination.

        Valid combinations:
        - Medium: M, S, T, Double-sided (mainhand); M, S, T (offhand)
        - Small: S, T (both)
        - Large: L mainhand ONLY if offhand is M or S; M, S mainhand with M, S offhand

        :return: True if valid, False if invalid configuration
        """
        character_size = self.cfg.CHARACTER_SIZE
        mainhand_size = self.weapon.size
        offhand_size = self._get_offhand_weapon_size()

        # Special: Medium can dual-wield double-sided (even though "Large" sized, they count as light offhand)
        if (character_size == 'M'
            and self.weapon.name_base in DOUBLE_SIDED_WEAPONS
            and not self.cfg.SHAPE_WEAPON_OVERRIDE):
            return True

        # Ranged weapons cannot be dual-wielded (mainhand check)
        if (self.weapon.name_base in AUTO_MIGHTY_WEAPONS or
                self.weapon.name_base in AMMO_BASED_WEAPONS):
            return False

        # Check offhand weapon if custom
        if self.cfg.CUSTOM_OFFHAND_WEAPON and self.offhand_weapon:
            # Offhand cannot be ranged weapon
            if (self.offhand_weapon.name_base in AUTO_MIGHTY_WEAPONS or
                    self.offhand_weapon.name_base in AMMO_BASED_WEAPONS):
                return False
            # Offhand cannot be Large
            if offhand_size == 'L':
                return False

        # Large mainhand: only valid if Large character AND offhand is M or S
        if mainhand_size == 'L':
            if character_size == 'L' and offhand_size in ('M', 'S'):
                return True
            return False

        # Small cannot dual-wield Medium (mainhand)
        if character_size == 'S' and mainhand_size == 'M':
            return False

        # Small cannot dual-wield Medium (offhand)
        if character_size == 'S' and offhand_size == 'M':
            return False

        # Large cannot dual-wield Tiny
        if character_size == 'L' and mainhand_size == 'T':
            return False
        if character_size == 'L' and offhand_size == 'T':
            return False

        return True

    def _is_weapon_light(self, weapon_size=None):
        """
        Determine if the weapon is considered "light" for this character size.

        Light weapon definition:
        - Weapon is smaller than character size
        - Example: Small weapon is light for Medium/Large, but not for Small

        :param weapon_size: Optional weapon size to check. If None, uses mainhand weapon size.
        :return: True if light weapon, False otherwise
        """
        size_order = {'T': 0, 'S': 1, 'M': 2, 'L': 3}
        character_size_value = size_order[self.cfg.CHARACTER_SIZE]

        if weapon_size is None:
            weapon_size = self.weapon.size
        weapon_size_value = size_order[weapon_size]

        return weapon_size_value < character_size_value

    def calculate_dw_penalties(self):
        """
        Calculate dual-wield attack penalties for primary and off-hand.
        Uses OFFHAND weapon size to determine if offhand is light (game-accurate).

        Base penalties (no feats):
        - Light offhand weapon: -4 primary / -8 off-hand
        - Non-light offhand weapon: -6 primary / -10 off-hand

        With Two-Weapon Fighting:
        - Light offhand weapon: -2 primary / -6 off-hand
        - Non-light offhand weapon: -4 primary / -8 off-hand

        With Ambidexterity (requires TWF):
        - Off-hand penalty reduced by 4

        With both TWF + Ambidexterity:
        - Light offhand weapon: -2 primary / -2 off-hand
        - Non-light offhand weapon: -4 primary / -4 off-hand

        :return: Tuple of (primary_penalty, offhand_penalty)
        """
        # Use offhand weapon size for penalty calculation (game-accurate)
        offhand_size = self._get_offhand_weapon_size()
        is_light = self._is_weapon_light(offhand_size)
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

        return primary_penalty, offhand_penalty

    def _build_simple_progression(self, attack_prog_offsets):
        """Build attack progression when dual-wield is disabled."""
        attack_prog = []
        special_attack_count = 0

        for offset in attack_prog_offsets:
            if isinstance(offset, str):
                special_offset = special_attack_count * -5
                attack_prog.append(self.ab + special_offset)
                special_attack_count += 1
            else:
                attack_prog.append(self.ab + offset)

        return attack_prog

    def _build_dw_progression(self, attack_prog_offsets, primary_penalty, offhand_penalty):
        """Build attack progression when dual-wield is enabled."""
        attack_prog = []
        special_attack_count = 0

        for offset in attack_prog_offsets:
            if isinstance(offset, str):
                special_offset = special_attack_count * -5
                attack_prog.append(self.ab + special_offset)
                special_attack_count += 1
            else:
                attack_prog.append(self.ab + primary_penalty + offset)

        # Track offhand attack indices
        offhand_start_idx = len(attack_prog)

        # Use offhand AB for offhand attacks, capped appropriately
        offhand_ab_effective = min(self.offhand_ab + offhand_penalty, self.offhand_ab_capped)
        attack_prog.append(offhand_ab_effective)
        self.offhand_attack_indices.append(offhand_start_idx)

        if self.cfg.IMPROVED_TWF:
            offhand_ab_effective_2 = offhand_ab_effective - 5
            attack_prog.append(offhand_ab_effective_2)
            self.offhand_attack_indices.append(offhand_start_idx + 1)

        return attack_prog

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

        threat_range_max = 20

        # Get offhand crit_threat if custom offhand weapon is enabled
        offhand_crit_threat = self.weapon.crit_threat  # Default to mainhand
        if self.cfg.CUSTOM_OFFHAND_WEAPON and self.offhand_weapon:
            offhand_crit_threat = self.offhand_weapon.crit_threat

        for idx, ab in enumerate(self.attack_prog):
            hit_chance = max(0.05, min(0.95, (21 + ab - self.defender_ac) * 0.05))
            hit_chance_list.append(hit_chance)

            threat_hit_chance = max(0.0, min(1.0, (21 + ab - self.defender_ac) * 0.05))

            # Use appropriate crit_threat based on whether this is an offhand attack
            if idx in self.offhand_attack_indices:
                crit_threat = offhand_crit_threat
            else:
                crit_threat = self.weapon.crit_threat

            # Calculate the chance for -attempting- a critical-hit threat roll:
            threat_roll_chance = (threat_range_max - crit_threat + 1) * 0.05

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

    def get_offhand_legend_proc_rate_theoretical(self):
        """
        :return: The theoretical chance to trigger a legend proc for offhand weapon
        """
        if not self.cfg.CUSTOM_OFFHAND_WEAPON or not self.offhand_weapon:
            return 0.0

        legend_proc_rate = 0.0
        purple_props = self.offhand_weapon.purple_props
        legendary = purple_props.get('legendary') if isinstance(purple_props, dict) else None
        if legendary:
            proc = legendary.get('proc')
            if isinstance(proc, (float, int)):  # Proc is percentage (numeric)
                legend_proc_rate = float(proc)
            elif isinstance(proc, str):         # Proc is 'on_crit'
                # Calculate crit chance for offhand attacks only
                if self.offhand_attack_indices:
                    offhand_crit_chances = [self.crit_chance_list[i] for i in self.offhand_attack_indices if i < len(self.crit_chance_list)]
                    offhand_hit_chances = [self.hit_chance_list[i] for i in self.offhand_attack_indices if i < len(self.hit_chance_list)]
                    if offhand_hit_chances and sum(offhand_hit_chances) > 0:
                        legend_proc_rate = sum(offhand_crit_chances) / sum(offhand_hit_chances)
            else:
                legend_proc_rate = 0.0

        return legend_proc_rate

    def get_attack_progression(self):
        """
        Determine the attack progression of the character (list of AB).

        If dual-wield is disabled: return base progression with markers converted to offsets
        If dual-wield is enabled: apply penalties and add off-hand attacks

        :return: List of ABs, e.g., [66, 61, 56, 68, 64, 59]
        """
        attack_prog_selected = self.cfg.AB_PROG
        attack_prog_offsets = deepcopy(self.cfg.AB_PROGRESSIONS[attack_prog_selected])

        # Non-dual-wield mode
        if not self.cfg.DUAL_WIELD:
            return self._build_simple_progression(attack_prog_offsets)

        # Dual-wield mode
        self.dual_wield = True

        # Validate configuration
        if not self._is_valid_dw_config():
            self.valid_dual_wield_config = False
            self.ab = 0
            return [0] * len(attack_prog_offsets)

        # Calculate penalties and build progression
        primary_penalty, offhand_penalty = self.calculate_dw_penalties()
        return self._build_dw_progression(attack_prog_offsets, primary_penalty, offhand_penalty)

    def attack_roll(self, attacker_ab: int, defender_ac_modifier: int = 0, crit_threat: int = None):
        """
        Perform an attack roll against the defender.

        :param attacker_ab: AB of attacker
        :param defender_ac_modifier: AC modifier of the defender, e.g., -2 for legendary Sunder effect
        :param crit_threat: Critical threat range minimum. If None, uses mainhand weapon's crit_threat.
                           Pass offhand weapon's crit_threat for offhand attacks.
        :return: Tuple of (outcome, roll) where outcome is 'miss', 'hit', or 'critical_hit'
        """
        roll = random.randint(1, 20)        # Roll a 1d20
        defender_ac = self.defender_ac + defender_ac_modifier

        # Use provided crit_threat or default to mainhand weapon
        effective_crit_threat = crit_threat if crit_threat is not None else self.weapon.crit_threat

        if roll == 1:                             # Auto-miss on a natural 1
            return 'miss', roll
        elif (roll + attacker_ab) >= defender_ac or roll == 20:       # Check if a hit or miss, auto-hit on a natural 20
            if roll >= effective_crit_threat:
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
