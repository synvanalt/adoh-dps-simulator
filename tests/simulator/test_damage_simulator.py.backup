import pytest
from simulator.damage_simulator import DamageSimulator
from simulator.config import Config


def test_setup_dual_wield_tracking_non_dw():
    cfg = Config()
    cfg.AB_PROG = "5APR Classic"
    sim = DamageSimulator('Spear', cfg)

    result = sim._setup_dual_wield_tracking()
    assert result['is_dual_wield'] is False
    assert result['offhand_attack_1_idx'] is None
    assert result['offhand_attack_2_idx'] is None
    assert result['str_idx'] is None


def test_setup_dual_wield_tracking_with_dw():
    cfg = Config()
    cfg.AB_PROG = "5APR & Dual-Wield"
    cfg.TOON_SIZE = "M"
    sim = DamageSimulator('Longsword', cfg)

    result = sim._setup_dual_wield_tracking()
    assert result['is_dual_wield'] is True
    assert result['offhand_attack_1_idx'] is not None
    assert result['offhand_attack_2_idx'] is not None
    assert result['str_idx'] is not None


def test_calculate_final_statistics_zero_rounds():
    cfg = Config()
    sim = DamageSimulator('Spear', cfg)
    sim.stats.hits = 0
    sim.attack_sim.illegal_dual_wield_config = True

    result = sim._calculate_final_statistics(round_num=0)

    assert result['dps_mean'] == 0
    assert result['dps_stdev'] == 0
    assert result['dpr'] == 0
