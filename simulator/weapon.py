from weapons_db import WEAPON_PROPERTIES, PURPLE_WEAPONS
from simulator.config import Config
from simulator.damage_roll import DamageRoll
from simulator.constants import (
    PHYSICAL_DAMAGE_TYPES,
    AUTO_MIGHTY_WEAPONS,
    AMMO_BASED_WEAPONS,
    DOUBLE_SIDED_WEAPONS,
)
from simulator.damage_source_resolver import (
    unpack_and_merge_vs_race,
    merge_enhancement_bonus,
)
from copy import deepcopy


class Weapon:
    def __init__(self, weapon_name: str, config: Config):
        self.cfg = config
        self.name_base = weapon_name.split('_')[0]      # Example: Convert 'Dagger_PK' to 'Dagger'
        self.name_purple = weapon_name                  # Keep the full name 'Dagger_PK' for purple weapons management
        self.physical_dmg_types = PHYSICAL_DAMAGE_TYPES
        self.weapon_damage_stack_warning = False

        # Validate that the weapon exists in WEAPON_PROPERTIES
        if self.name_base not in WEAPON_PROPERTIES:
            raise ValueError(f"Weapon '{self.name_base}' not found in WEAPON_PROPERTIES")

        # Load weapon properties from the database
        # Example: 'Halberd': {'dmg': [1, 10, 'slashing & piercing'], 'threat': 20, 'multiplier': 3, 'size': 'L'},
        base_props = WEAPON_PROPERTIES[self.cfg.SHAPE_WEAPON] if self.cfg.SHAPE_WEAPON_OVERRIDE else WEAPON_PROPERTIES[self.name_base]

        self.purple_props = PURPLE_WEAPONS[self.name_purple]
        self.vs_race_key = self.get_vs_race_key()

        dice = base_props['dmg'][0]
        sides = base_props['dmg'][1]
        self.dmg_type = base_props['dmg'][2]
        self.dmg = {'physical': DamageRoll(dice=dice, sides=sides, flat=0)}
        self.threat_base = base_props['threat']
        self.multiplier_base = base_props['multiplier']
        self.size = base_props['size']

        self.crit_threat = self.get_crit_threat()
        self.crit_multiplier = self.crit_multiplier()

    def get_crit_threat(self):
        """
        :return: The minimum value of the weapon's threat range, e.g., for Scimitar (with range 18-20) it should be 18
        """
        threat_range_max = 20  # Always 20 in NWN
        threat_range_min = self.threat_base
        base_threat_range = (threat_range_max - threat_range_min + 1)

        if self.cfg.KEEN:
            threat_range_min -= base_threat_range
        if self.cfg.IMPROVED_CRIT:
            threat_range_min -= base_threat_range
        if self.cfg.WEAPONMASTER:
            threat_range_min -= 2

        return threat_range_min

    def crit_multiplier(self):
        """
        :return: Critical hit multiplier, e.g., for a non-WM character wielding Scimitar it should be 2
        """
        if self.cfg.WEAPONMASTER:  # Add +1 to the multiplier if character is a Weaponmaster
            multiplier = self.multiplier_base + 1
        else:
            multiplier = self.multiplier_base

        return multiplier

    def get_vs_race_key(self):
        """Check if there is any 'vs_race' entry inside purple weapon properties, if yes store the key name"""
        vs_race_key = None
        if self.cfg.DAMAGE_VS_RACE:
            for key in self.purple_props.keys():
                if "vs_race" in key:
                    vs_race_key = key
                    break  # Exit the loop once a match is found

        return vs_race_key

    def enhancement_bonus(self):
        # Find the effective base damage type (dmg_type_eb):
        dmg_type_list = self.dmg_type.split(" & ") if "&" in self.dmg_type else [self.dmg_type]
        for dmg_type in self.physical_dmg_types:    # 'slashing' / 'piercing' / 'bludgeoning' (ordered)
            if dmg_type in dmg_type_list:
                dmg_type_eb = dmg_type
                break  # Stop immediately once the first prioritized type is found
        else:
            raise ValueError(f"Invalid damage type in base weapon {self.name_base}: {self.dmg_type}")

        # Assigning the correct damage bonus:
        ammo_based_weapons = AMMO_BASED_WEAPONS
        if self.name_base in ammo_based_weapons:
            enhancement_dmg = 0
        elif (self.cfg.DAMAGE_VS_RACE
              and self.vs_race_key in self.purple_props
              and 'enhancement' in self.purple_props[self.vs_race_key]):
            enhancement_dmg = self.purple_props[self.vs_race_key]['enhancement'] + self.cfg.ENHANCEMENT_SET_BONUS
        else:
            enhancement_dmg = self.purple_props['enhancement'] + self.cfg.ENHANCEMENT_SET_BONUS

        return {dmg_type_eb: DamageRoll(dice=0, sides=0, flat=enhancement_dmg)}

    def strength_bonus(self):
        """
        :return: The flat physical damage added by Strength of the character
        """
        auto_mighty_throwing_weapons = AUTO_MIGHTY_WEAPONS

        if self.name_base in auto_mighty_throwing_weapons:  # Ranged weapons, but only for auto-mighty throwing weapons
            str_dmg = self.cfg.STR_MOD
        elif self.cfg.COMBAT_TYPE == 'ranged':  # Ranged weapons, excluding auto-mighty throwing weapons
            str_dmg = min(self.cfg.STR_MOD, self.cfg.MIGHTY)
        elif self.cfg.COMBAT_TYPE == 'melee':
            str_dmg = self.cfg.STR_MOD * 2 if self.cfg.TWO_HANDED else self.cfg.STR_MOD
        else:
            raise ValueError(f"Invalid combat type: {self.cfg.COMBAT_TYPE}. Expected 'melee' or 'ranged'.")

        return {'physical': DamageRoll(dice=0, sides=0, flat=str_dmg)}

    def aggregate_damage_sources(self):
        """
        :return: A dictionary of all damage sources (base weapon damage, strength bonus damage, etc.)
        Each item in the dictionary should be a list, and within it a sublist per damage type.
        For example: 'purple_dmg': [[2, 4, 'magical'], [1, 6, 'physical']]
        This master-list will later be looped over when damage is calculated.
        """
        purple_props_updated = unpack_and_merge_vs_race(
            self.purple_props,
            damage_vs_race_enabled=self.cfg.DAMAGE_VS_RACE
        )

        purple_props_updated, warning = merge_enhancement_bonus(
            purple_props_updated,
            self.enhancement_bonus()
        )
        self.weapon_damage_stack_warning = warning

        # Remove Tenacious Blow damage bonus if not wielding a double-sided weapon
        additional_dmg_copy = deepcopy(self.cfg.ADDITIONAL_DAMAGE)
        if ("Tenacious_Blow" in self.cfg.ADDITIONAL_DAMAGE
                and self.cfg.ADDITIONAL_DAMAGE["Tenacious_Blow"][0] is True
                and self.name_base not in DOUBLE_SIDED_WEAPONS):
            additional_dmg_copy["Tenacious_Blow"][0] = False    # Turn off Tenacious Blow for this instance

        # Aggregate all damage sources:
        dmg_src_dict = {
            'weapon_base_dmg': self.dmg,
            'weapon_bonus_dmg': purple_props_updated,
            'str_dmg': self.strength_bonus(),
            'additional_dmg': [v[1] for v in additional_dmg_copy.values() if v[0] is True],
        }
        return dmg_src_dict
