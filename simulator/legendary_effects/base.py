"""Base interface for legendary weapon effects."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple


class LegendaryEffect(ABC):
    """Abstract base class for legendary weapon effects.

    Each legendary weapon with unique behavior should implement this interface.
    Effects return two dictionaries: burst (one-time) and persistent (duration window).
    """

    @abstractmethod
    def apply(
        self,
        legend_dict: Dict[str, Any],
        stats_collector,
        crit_multiplier: int,
        attack_sim
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Apply the legendary effect and return damage results.

        Args:
            legend_dict: Dictionary with legendary properties (proc, damage, effect)
            stats_collector: StatsCollector instance for tracking procs
            crit_multiplier: Critical hit multiplier (1 for normal hit)
            attack_sim: AttackSimulator instance for damage rolls

        Returns:
            Tuple of (burst_effects, persistent_effects)

            burst_effects: Applied only when effect procs
                - 'damage_sums': Dict of rolled damage by type {type: value}

            persistent_effects: Applied during legendary window
                - 'common_damage': List [dice, sides, flat, type] to add to main damage
                - 'immunity_factors': Dict of immunity modifiers {type: factor}
                - 'ab_bonus': Int AB bonus to apply
                - 'ac_reduction': Int AC reduction to apply
        """
        pass
