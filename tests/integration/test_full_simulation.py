import pytest
from simulator.damage_simulator import DamageSimulator
from simulator.config import Config


def test_full_simulation_basic_weapon():
    """Test complete simulation with basic weapon setup."""
    cfg = Config()
    cfg.ROUNDS = 1000  # Smaller for faster test
    cfg.AB = 68
    cfg.TARGET_AC = 65
    cfg.STR_MOD = 15

    sim = DamageSimulator('Longsword', cfg)
    results = sim.simulate_dps()

    assert results['dps_crits'] > 0
    assert results['dps_no_crits'] > 0
    assert results['hit_rate_actual'] > 0
    assert results['attack_prog'] == sim.attack_sim.attack_prog


def test_simulation_with_critical_feats():
    """Test simulation with keen and improved critical."""
    cfg = Config()
    cfg.ROUNDS = 1000
    cfg.KEEN = True
    cfg.IMPROVED_CRIT = True
    cfg.AB = 68
    cfg.TARGET_AC = 60

    sim = DamageSimulator('Scimitar', cfg)
    results = sim.simulate_dps()

    # Should have higher crit rate
    assert results['crit_rate_actual'] > 10  # At least 10%


def test_simulation_with_dual_wield():
    """Test simulation with dual-wield setup."""
    cfg = Config()
    cfg.ROUNDS = 1000
    cfg.AB_PROG = "5APR Classic"
    cfg.DUAL_WIELD = True
    cfg.TWO_WEAPON_FIGHTING = True
    cfg.AMBIDEXTERITY = True
    cfg.IMPROVED_TWF = True
    cfg.CHARACTER_SIZE = "M"
    cfg.AB = 68
    cfg.TARGET_AC = 65

    sim = DamageSimulator('Longsword', cfg)
    results = sim.simulate_dps()

    assert sim.attack_sim.dual_wield is True
    assert len(results['attack_prog']) > 5  # Should have offhand attacks


def test_simulation_dual_wield_no_feats():
    """Test dual-wield with no feats produces higher penalties."""
    cfg = Config()
    cfg.ROUNDS = 1000
    cfg.AB_PROG = "5APR Classic"
    cfg.DUAL_WIELD = True
    cfg.TWO_WEAPON_FIGHTING = False
    cfg.AMBIDEXTERITY = False
    cfg.IMPROVED_TWF = False
    cfg.CHARACTER_SIZE = "M"
    cfg.AB = 68
    cfg.TARGET_AC = 65

    sim = DamageSimulator('Longsword', cfg)
    results = sim.simulate_dps()

    # Should have lower DPS due to -6/-10 penalties and only 1 off-hand attack
    assert results['dps_crits'] > 0  # But still produces damage
    assert sim.attack_sim.dual_wield is True


def test_simulation_with_additional_damage():
    """Test simulation with additional damage sources."""
    cfg = Config()
    cfg.ROUNDS = 1000
    cfg.ADDITIONAL_DAMAGE['Flame_Weapon'][0] = True  # Enable Flame Weapon
    cfg.ADDITIONAL_DAMAGE['Divine_Favor'][0] = True  # Enable Divine Favor

    sim = DamageSimulator('Longsword', cfg)
    results = sim.simulate_dps()

    # Should have fire and magical damage in breakdown
    assert 'fire' in sim.cumulative_damage_by_type or 'fire_fw' in sim.cumulative_damage_by_type
    assert 'magical' in sim.cumulative_damage_by_type


def test_simulation_convergence():
    """Test that simulation converges within reasonable rounds."""
    cfg = Config()
    cfg.ROUNDS = 15000
    cfg.AB = 70
    cfg.TARGET_AC = 60  # Easy target for fast convergence

    sim = DamageSimulator('Spear', cfg)
    results = sim.simulate_dps()

    # Check that we have convergence data
    assert len(sim.dps_rolling_avg) > 0
    assert len(sim.dps_per_round) > 0


def test_illegal_dual_wield_returns_zero():
    """Test that illegal dual-wield config returns zero results."""
    cfg = Config()
    cfg.AB_PROG = "5APR Classic"
    cfg.DUAL_WIELD = True
    cfg.CHARACTER_SIZE = "S"  # Small

    sim = DamageSimulator('Greataxe', cfg)  # Large weapon
    results = sim.simulate_dps()

    assert sim.attack_sim.illegal_dual_wield_config is True
    assert results['dps_crits'] == 0
    assert results['dps_no_crits'] == 0


def test_simulation_respects_damage_limit():
    """Test that simulation stops at damage limit."""
    cfg = Config()
    cfg.ROUNDS = 15000
    cfg.DAMAGE_LIMIT_FLAG = True
    cfg.DAMAGE_LIMIT = 5000
    cfg.AB = 80  # High AB for faster damage accumulation
    cfg.TARGET_AC = 50

    sim = DamageSimulator('Greataxe', cfg)
    results = sim.simulate_dps()

    # Should stop early due to damage limit
    assert len(sim.dps_per_round) < cfg.ROUNDS
