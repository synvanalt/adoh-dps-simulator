import pytest
from simulator.damage_roll import DamageRoll


def test_damage_roll_with_all_fields():
    dmg = DamageRoll(dice=2, sides=6, flat=5)
    assert dmg.dice == 2
    assert dmg.sides == 6
    assert dmg.flat == 5


def test_damage_roll_with_default_flat():
    dmg = DamageRoll(dice=1, sides=8)
    assert dmg.dice == 1
    assert dmg.sides == 8
    assert dmg.flat == 0


def test_damage_roll_from_list_with_flat():
    dmg = DamageRoll.from_list([2, 6, 5])
    assert dmg.dice == 2
    assert dmg.sides == 6
    assert dmg.flat == 5


def test_damage_roll_from_list_without_flat():
    dmg = DamageRoll.from_list([1, 8])
    assert dmg.dice == 1
    assert dmg.sides == 8
    assert dmg.flat == 0


def test_damage_roll_to_list():
    dmg = DamageRoll(dice=2, sides=6, flat=5)
    assert dmg.to_list() == [2, 6, 5]


def test_damage_roll_average():
    dmg = DamageRoll(dice=2, sides=6, flat=3)
    # 2 * ((1+6)/2) + 3 = 2 * 3.5 + 3 = 10.0
    assert dmg.average() == 10.0
