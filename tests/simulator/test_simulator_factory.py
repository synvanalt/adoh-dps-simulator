import pytest
from simulator.simulator_factory import SimulatorFactory
from simulator.config import Config
from simulator.weapon import Weapon
from simulator.attack_simulator import AttackSimulator
from simulator.stats_collector import StatsCollector


def test_factory_creates_damage_simulator():
    cfg = Config()
    factory = SimulatorFactory(cfg)

    sim = factory.create_damage_simulator('Spear')

    assert sim is not None
    assert isinstance(sim.weapon, Weapon)
    assert isinstance(sim.attack_sim, AttackSimulator)
    assert isinstance(sim.stats, StatsCollector)


def test_factory_allows_custom_stats_collector():
    cfg = Config()
    factory = SimulatorFactory(cfg)
    custom_stats = StatsCollector()
    custom_stats.hits = 100  # Pre-populate for testing

    sim = factory.create_damage_simulator('Spear', stats_collector=custom_stats)

    assert sim.stats is custom_stats
    assert sim.stats.hits == 100


def test_factory_initializes_all_required_attributes():
    """Verify factory creates simulator with all necessary attributes."""
    cfg = Config()
    factory = SimulatorFactory(cfg)

    sim = factory.create_damage_simulator('Spear')

    # Check core dependencies
    assert sim.cfg is cfg
    assert hasattr(sim, 'weapon')
    assert hasattr(sim, 'attack_sim')
    assert hasattr(sim, 'stats')
    assert hasattr(sim, 'legend_effect')

    # Check damage dictionaries
    assert hasattr(sim, 'dmg_dict')
    assert hasattr(sim, 'dmg_dict_legend')
    assert hasattr(sim, 'dmg_dict_base')

    # Check convergence tracking attributes
    assert hasattr(sim, 'total_dmg')
    assert hasattr(sim, 'dps_window')
    assert hasattr(sim, 'dps_rolling_avg')
    assert hasattr(sim, 'dps_per_round')
    assert hasattr(sim, 'cumulative_damage_per_round')

    # Check crit immune tracking
    assert hasattr(sim, 'total_dmg_crit_imm')
    assert hasattr(sim, 'dps_crit_imm_window')
    assert hasattr(sim, 'dps_crit_imm_rolling_avg')
    assert hasattr(sim, 'dps_crit_imm_per_round')
    assert hasattr(sim, 'cumulative_damage_by_type')


def test_factory_simulator_behaves_like_normal_constructor():
    """Verify factory-created simulator behaves identically to constructor-created one."""
    cfg = Config()
    factory = SimulatorFactory(cfg)

    # Create using factory
    sim_factory = factory.create_damage_simulator('Spear')

    # Create using constructor
    from simulator.damage_simulator import DamageSimulator
    sim_constructor = DamageSimulator('Spear', cfg)

    # Compare key attributes
    assert sim_factory.weapon.name_base == sim_constructor.weapon.name_base
    assert sim_factory.confidence == sim_constructor.confidence
    assert sim_factory.window_size == sim_constructor.window_size
    assert len(sim_factory.dmg_dict) == len(sim_constructor.dmg_dict)
