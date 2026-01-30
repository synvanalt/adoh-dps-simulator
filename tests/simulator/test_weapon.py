import pytest
from simulator.weapon import Weapon
from simulator.config import Config
from simulator.damage_roll import DamageRoll


def test_weapon_dmg_is_damage_roll():
    cfg = Config()
    weapon = Weapon('Spear', cfg)

    assert 'physical' in weapon.dmg
    dmg_roll = weapon.dmg['physical']
    assert isinstance(dmg_roll, DamageRoll)
    assert dmg_roll.dice == 1
    assert dmg_roll.sides == 8
    assert dmg_roll.flat == 0


def test_strength_bonus_returns_damage_roll():
    cfg = Config()
    cfg.STR_MOD = 15
    cfg.COMBAT_TYPE = 'melee'
    weapon = Weapon('Longsword', cfg)

    str_bonus = weapon.strength_bonus()
    assert 'physical' in str_bonus
    assert isinstance(str_bonus['physical'], DamageRoll)
    assert str_bonus['physical'].flat == 15


def test_enhancement_bonus_returns_damage_roll():
    cfg = Config()
    cfg.ENHANCEMENT_SET_BONUS = 3
    weapon = Weapon('Longsword', cfg)

    enh_bonus = weapon.enhancement_bonus()
    # Should have a damage type key with DamageRoll value
    assert len(enh_bonus) == 1
    dmg_type, dmg_roll = next(iter(enh_bonus.items()))
    assert isinstance(dmg_roll, DamageRoll)
    assert dmg_roll.dice == 0
    assert dmg_roll.sides == 0


def test_crit_threat_calculation_base():
    cfg = Config()
    cfg.KEEN = False
    cfg.IMPROVED_CRIT = False
    cfg.WEAPONMASTER = False
    weapon = Weapon('Scimitar', cfg)  # Base threat 18-20

    assert weapon.crit_threat == 18


def test_crit_threat_with_keen():
    cfg = Config()
    cfg.KEEN = True
    cfg.IMPROVED_CRIT = False
    cfg.WEAPONMASTER = False
    weapon = Weapon('Scimitar', cfg)  # Base threat 18-20 (range of 3)

    # Keen doubles range: 18 - 3 = 15
    assert weapon.crit_threat == 15


def test_crit_threat_with_keen_and_improved_crit():
    cfg = Config()
    cfg.KEEN = True
    cfg.IMPROVED_CRIT = True
    cfg.WEAPONMASTER = False
    weapon = Weapon('Scimitar', cfg)

    # Both double: 18 - 3 - 3 = 12
    assert weapon.crit_threat == 12


def test_crit_multiplier_base():
    cfg = Config()
    cfg.WEAPONMASTER = False
    weapon = Weapon('Scimitar', cfg)  # Base multiplier x2

    assert weapon.crit_multiplier == 2


def test_crit_multiplier_weaponmaster():
    cfg = Config()
    cfg.WEAPONMASTER = True
    weapon = Weapon('Scythe', cfg)  # Base multiplier x4

    # WM adds +1 to multiplier
    assert weapon.crit_multiplier == 5


def test_strength_bonus_melee():
    cfg = Config()
    cfg.STR_MOD = 15
    cfg.COMBAT_TYPE = 'melee'
    cfg.TWO_HANDED = False
    weapon = Weapon('Longsword', cfg)

    str_bonus = weapon.strength_bonus()
    assert str_bonus['physical'].flat == 15


def test_strength_bonus_two_handed():
    cfg = Config()
    cfg.STR_MOD = 15
    cfg.COMBAT_TYPE = 'melee'
    cfg.TWO_HANDED = True
    weapon = Weapon('Greatsword_Desert', cfg)

    str_bonus = weapon.strength_bonus()
    # Two-handed gets 1.5x STR
    assert str_bonus['physical'].flat == 30


def test_strength_bonus_ranged_with_mighty():
    cfg = Config()
    cfg.STR_MOD = 15
    cfg.MIGHTY = 10
    cfg.COMBAT_TYPE = 'ranged'
    weapon = Weapon('Longbow_FireDragon', cfg)

    str_bonus = weapon.strength_bonus()
    # Ranged is capped by Mighty
    assert str_bonus['physical'].flat == 10


def test_strength_bonus_auto_mighty_weapon():
    cfg = Config()
    cfg.STR_MOD = 15
    cfg.COMBAT_TYPE = 'ranged'
    weapon = Weapon('Darts', cfg)

    str_bonus = weapon.strength_bonus()
    # Darts are auto-mighty, get full STR
    assert str_bonus['physical'].flat == 15
