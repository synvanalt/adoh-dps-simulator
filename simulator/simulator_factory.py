"""Factory for creating simulator instances with dependency injection.

This factory decouples instantiation logic from the simulators themselves,
making it easier to test components in isolation.
"""

from typing import Optional, Callable
from collections import deque
from simulator.config import Config
from simulator.weapon import Weapon
from simulator.attack_simulator import AttackSimulator
from simulator.stats_collector import StatsCollector
from simulator.legend_effect import LegendEffect


class SimulatorFactory:
    """Factory for creating simulator instances."""

    def __init__(self, config: Config):
        """Initialize factory with configuration.

        Args:
            config: Configuration instance to use for all created simulators
        """
        self.config = config

    def create_damage_simulator(
        self,
        weapon_name: str,
        stats_collector: Optional[StatsCollector] = None,
        progress_callback: Optional[Callable[..., None]] = None
    ) -> 'DamageSimulator':
        """Create a DamageSimulator with all dependencies.

        Args:
            weapon_name: Name of weapon to simulate
            stats_collector: Optional custom stats collector (creates new if None)
            progress_callback: Optional callback for progress updates

        Returns:
            Configured DamageSimulator instance
        """
        from simulator.damage_simulator import DamageSimulator
        from copy import deepcopy

        # Create dependencies
        stats = stats_collector or StatsCollector()
        weapon = Weapon(weapon_name, config=self.config)
        attack_sim = AttackSimulator(weapon_obj=weapon, config=self.config)
        legend_effect = LegendEffect(
            stats_obj=stats,
            weapon_obj=weapon,
            attack_sim=attack_sim
        )

        # Create simulator with injected dependencies
        simulator = DamageSimulator.__new__(DamageSimulator)
        simulator.cfg = self.config
        simulator.stats = stats
        simulator.weapon = weapon
        simulator.attack_sim = attack_sim
        simulator.legend_effect = legend_effect
        simulator.progress_callback = progress_callback

        # Initialize remaining state (damage dicts, convergence params, etc.)
        simulator.dmg_type_names = []
        simulator.dmg_dict = {}
        simulator.dmg_dict_legend = {}
        simulator.collect_damage_from_all_sources()

        # Convergence params
        z_values = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        simulator.confidence = 0.99
        simulator.z = z_values.get(simulator.confidence, 2.576)
        simulator.window_size = 15

        # Convergence tracking - crit allowed
        simulator.total_dmg = 0
        simulator.dps_window = deque(maxlen=simulator.window_size)
        simulator.dps_rolling_avg = []
        simulator.dps_per_round = []
        simulator.cumulative_damage_per_round = []

        # Convergence tracking - crit immune
        simulator.total_dmg_crit_imm = 0
        simulator.dps_crit_imm_window = deque(maxlen=simulator.window_size)
        simulator.dps_crit_imm_rolling_avg = []
        simulator.dps_crit_imm_per_round = []
        simulator.cumulative_damage_by_type = {}

        # Cache damage dictionaries
        simulator.dmg_dict_base = deepcopy(simulator.dmg_dict)

        return simulator
