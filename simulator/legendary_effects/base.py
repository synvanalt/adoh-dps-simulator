"""Base interface for legendary weapon effects."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class LegendaryEffect(ABC):
    """Abstract base class for legendary weapon effects.

    Each legendary weapon with unique behavior should implement this interface.
    """

    @abstractmethod
    def apply(
        self,
        legend_dict: Dict[str, Any],
        stats_collector,
        crit_multiplier: int,
        attack_sim
    ) -> Dict[str, Any]:
        """Apply the legendary effect and return damage results.

        Args:
            legend_dict: Dictionary with legendary properties (proc, damage, effect)
            stats_collector: StatsCollector instance for tracking procs
            crit_multiplier: Critical hit multiplier (1 for normal hit)
            attack_sim: AttackSimulator instance for damage rolls

        Returns:
            Dictionary with:
            - 'damage_sums': Dict of damage by type
            - 'common_damage': List for damage added to common pool (optional)
            - 'immunity_factors': Dict of immunity modifiers (optional)
        """
        pass
