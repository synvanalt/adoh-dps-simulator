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
