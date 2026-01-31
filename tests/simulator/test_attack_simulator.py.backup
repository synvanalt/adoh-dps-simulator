import pytest
from simulator.attack_simulator import AttackSimulator
from simulator.weapon import Weapon
from simulator.config import Config


def test_calculate_attack_bonus_normal_weapon():
    cfg = Config()
    cfg.AB = 68
    weapon = Weapon('Longsword', cfg)
    attack_sim = AttackSimulator(weapon, cfg)

    assert attack_sim.ab == 68


def test_calculate_attack_bonus_high_enhancement():
    cfg = Config()
    cfg.AB = 68
    cfg.AB_CAPPED = 70
    # Scythe has +10 enhancement in weapons_db
    weapon = Weapon('Scythe', cfg)
    attack_sim = AttackSimulator(weapon, cfg)

    # Should add (10 - 7) = 3 to AB, capped at 70
    assert attack_sim.ab == 70


def test_hit_chance_calculation():
    cfg = Config()
    cfg.AB = 68
    cfg.TARGET_AC = 65
    weapon = Weapon('Longsword', cfg)
    attack_sim = AttackSimulator(weapon, cfg)

    hit_chance = attack_sim.get_hit_chance()
    # With AB 68 vs AC 65, should have high hit chance
    assert 0.0 < hit_chance < 1.0


def test_crit_chance_with_keen_and_improved_crit():
    cfg = Config()
    cfg.KEEN = True
    cfg.IMPROVED_CRIT = True
    # Scimitar has base threat 18-20
    weapon = Weapon('Scimitar', cfg)
    attack_sim = AttackSimulator(weapon, cfg)

    # With Keen + Improved Crit, threat should be significantly expanded
    assert attack_sim.weapon.crit_threat < 18


def test_dual_wield_penalty_medium_weapon():
    cfg = Config()
    cfg.AB = 68
    cfg.AB_PROG = "5APR & Dual-Wield"
    cfg.TOON_SIZE = "M"
    weapon = Weapon('Longsword', cfg)  # Medium weapon
    attack_sim = AttackSimulator(weapon, cfg)

    # Medium toon with medium weapon should get -4 penalty
    assert attack_sim.dual_wield is True
    assert attack_sim.ab == 64  # 68 - 4


def test_illegal_dual_wield_config():
    cfg = Config()
    cfg.AB = 68
    cfg.AB_PROG = "5APR & Dual-Wield"
    cfg.TOON_SIZE = "S"
    weapon = Weapon('Greatsword_Desert', cfg)  # Large weapon
    attack_sim = AttackSimulator(weapon, cfg)

    # Small toon can't dual-wield large weapon
    assert attack_sim.illegal_dual_wield_config is True
    assert attack_sim.ab == 0
