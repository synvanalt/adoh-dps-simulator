import pytest
from simulator.constants import (
    LEGEND_EFFECT_DURATION,
    DOUBLE_SIDED_WEAPONS,
    AUTO_MIGHTY_WEAPONS,
    PHYSICAL_DAMAGE_TYPES,
    AMMO_BASED_WEAPONS,
)


def test_legend_effect_duration():
    assert LEGEND_EFFECT_DURATION == 5


def test_double_sided_weapons_list():
    assert "Dire Mace" in DOUBLE_SIDED_WEAPONS
    assert "Double Axe" in DOUBLE_SIDED_WEAPONS
    assert "Two-Bladed Sword" in DOUBLE_SIDED_WEAPONS
    assert len(DOUBLE_SIDED_WEAPONS) == 3


def test_auto_mighty_weapons_list():
    assert "Darts" in AUTO_MIGHTY_WEAPONS
    assert "Throwing Axes" in AUTO_MIGHTY_WEAPONS
    assert "Shuriken" in AUTO_MIGHTY_WEAPONS
    assert len(AUTO_MIGHTY_WEAPONS) == 3


def test_physical_damage_types():
    assert PHYSICAL_DAMAGE_TYPES == ['slashing', 'piercing', 'bludgeoning']


def test_ammo_based_weapons():
    assert "Heavy Crossbow" in AMMO_BASED_WEAPONS
    assert "Longbow" in AMMO_BASED_WEAPONS
    assert len(AMMO_BASED_WEAPONS) == 5
