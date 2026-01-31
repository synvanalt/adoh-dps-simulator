"""Helper functions for resolving and aggregating damage sources.

This module contains pure functions for damage calculations that were
previously nested inside the Weapon class.
"""

from typing import Dict, List, Union, Any
from simulator.damage_roll import DamageRoll
from simulator.constants import PHYSICAL_DAMAGE_TYPES


def calculate_avg_dmg(dmg_obj: Union[DamageRoll, List[int]]) -> float:
    """Calculate the average value of a damage roll.

    Args:
        dmg_obj: Either a DamageRoll or legacy [dice, sides, flat] list

    Returns:
        Average damage value: dice * ((1 + sides) / 2) + flat
    """
    if isinstance(dmg_obj, DamageRoll):
        return dmg_obj.average()

    # Legacy list format support
    num_dice = dmg_obj[0]
    num_sides = dmg_obj[1]
    flat_dmg = dmg_obj[2] if len(dmg_obj) > 2 else 0
    return num_dice * ((1 + num_sides) / 2) + flat_dmg


def unpack_and_merge_vs_race(
    data_dict: Dict[str, Any],
    damage_vs_race_enabled: bool
) -> Dict[str, Any]:
    """Unpack nested 'vs_race' dictionaries and resolve conflicts.

    When vs_race damage exists for a damage type that already has a value,
    this function keeps whichever has the higher average damage.

    Args:
        data_dict: Dictionary with damage properties, may contain 'vs_race_*' keys
        damage_vs_race_enabled: Whether vs_race damage should be unpacked

    Returns:
        Merged dictionary with vs_race conflicts resolved
    """
    # Create a new dictionary for the merged results
    # Initialize it with all non-'vs_race' and non-'enhancement' items
    merged_dict = {
        k: v for k, v in data_dict.items()
        if not k.startswith('vs_race') and k != 'enhancement'
    }

    # Process 'vs_race' keys for unpacking and conflict resolution
    for key, sub_dict in data_dict.items():
        if key.startswith('vs_race') and isinstance(sub_dict, dict) and damage_vs_race_enabled:
            for sub_key, sub_value in sub_dict.items():
                # Check for conflict
                if sub_key in merged_dict:
                    # 1. Calculate the average for the existing value
                    avg_existing = calculate_avg_dmg(merged_dict[sub_key])
                    # 2. Calculate the average for the new value
                    avg_new = calculate_avg_dmg(sub_value)
                    # 3. Resolve conflict: keep the one with the higher average
                    if avg_new > avg_existing:
                        merged_dict[sub_key] = sub_value
                    # If avg_new <= avg_existing, the existing value is kept (no change needed)
                elif sub_key == 'enhancement':
                    # Skip enhancement here; it will be handled separately
                    continue
                else:
                    # No conflict, simply add the new key/value pair
                    merged_dict[sub_key] = sub_value

    return merged_dict


def merge_enhancement_bonus(
    data_dict: Dict[str, Any],
    enhancement_dmg_dict: Dict[str, Union[DamageRoll, List[int]]]
) -> tuple[Dict[str, Any], bool]:
    """Merge enhancement bonus damage with weapon damage properties.

    If enhancement damage type conflicts with existing physical damage,
    keeps whichever has higher average damage (they don't stack).

    Args:
        data_dict: Weapon damage properties dictionary
        enhancement_dmg_dict: Enhancement bonus damage (single damage type)

    Returns:
        Tuple of (merged_dict, warning_flag) where warning_flag indicates
        if a conflict was detected
    """
    dmg_type_eb, dmg_values_eb = next(iter(enhancement_dmg_dict.items()))
    avg_dmg_eb = calculate_avg_dmg(dmg_values_eb)
    warning_flag = False

    if dmg_type_eb not in PHYSICAL_DAMAGE_TYPES:
        raise ValueError(
            f"Enhancement damage type '{dmg_type_eb}' is not a valid physical damage type."
        )

    elif dmg_type_eb in data_dict.keys():
        avg_dmg_purple = calculate_avg_dmg(data_dict[dmg_type_eb])
        warning_flag = True
        # Compare average damages and keep the higher one (no stacking of same physical damage type):
        if avg_dmg_eb > avg_dmg_purple:
            data_dict[dmg_type_eb] = dmg_values_eb
    else:
        data_dict[dmg_type_eb] = dmg_values_eb

    return data_dict, warning_flag
