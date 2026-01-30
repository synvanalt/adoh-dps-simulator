from dataclasses import dataclass
from typing import List


@dataclass
class DamageRoll:
    """Represents a damage roll with dice, sides, and flat modifier.

    Example: 2d6+5 would be DamageRoll(dice=2, sides=6, flat=5)
    """
    dice: int
    sides: int
    flat: int = 0

    @classmethod
    def from_list(cls, dmg_list: List[int]) -> 'DamageRoll':
        """Create DamageRoll from legacy [dice, sides] or [dice, sides, flat] format.

        Args:
            dmg_list: List containing [dice, sides] or [dice, sides, flat]

        Returns:
            DamageRoll instance
        """
        dice = dmg_list[0]
        sides = dmg_list[1]
        flat = dmg_list[2] if len(dmg_list) > 2 else 0
        return cls(dice=dice, sides=sides, flat=flat)

    def to_list(self) -> List[int]:
        """Convert to legacy [dice, sides, flat] format.

        Returns:
            List containing [dice, sides, flat]
        """
        return [self.dice, self.sides, self.flat]

    def average(self) -> float:
        """Calculate average damage value.

        Returns:
            Average damage: dice * ((1 + sides) / 2) + flat
        """
        return self.dice * ((1 + self.sides) / 2) + self.flat
