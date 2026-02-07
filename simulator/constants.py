"""Constants used throughout the simulator.

This module centralizes magic values and commonly referenced lists
to improve maintainability and reduce duplication.
"""

# Legendary effect duration in rounds
LEGEND_EFFECT_DURATION = 5

# Weapon type lists
DOUBLE_SIDED_WEAPONS = ['Dire Mace', 'Double Axe', 'Two-Bladed Sword']

AUTO_MIGHTY_WEAPONS = ['Darts', 'Throwing Axes', 'Shuriken']

AMMO_BASED_WEAPONS = [
    'Heavy Crossbow',
    'Light Crossbow',
    'Longbow',
    'Shortbow',
    'Sling'
]

# Large-sized weapons (cannot be used as offhand)
LARGE_WEAPONS = [
    'Halberd',
    'Heavy Flail',
    'Greataxe',
    'Greatsword',
    'Scythe',
    'Spear',
    'Trident',
    'Dire Mace',
    'Double Axe',
    'Two-Bladed Sword',
    'Heavy Crossbow',
    'Longbow',
    'Quarterstaff',
]

# Damage type lists (ordered by game priority)
PHYSICAL_DAMAGE_TYPES = ['slashing', 'piercing', 'bludgeoning']
