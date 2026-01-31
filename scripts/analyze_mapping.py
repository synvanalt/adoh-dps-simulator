import csv

# Current PURPLE_WEAPONS keys from weapons_db.py
purple_weapons_keys = [
    'Halberd',
    'Heavy Flail',
    'Greataxe',
    'Greatsword_Desert',
    'Greatsword_Legion',
    'Greatsword_Tyr',
    'Scythe',
    'Spear',
    'Trident_Fire',
    'Trident_Ice',
    'Dire Mace',
    'Double Axe',
    'Two-Bladed Sword',
    'Darts',
    'Throwing Axes',
    'Heavy Crossbow',
    'Light Crossbow',
    'Longbow',
    'Shortbow',
    'Sling',
    'Gloves_Shandy',
    'Gloves_Adam',
    'Kama',
    'Quarterstaff_IcyFire',
    'Quarterstaff_Hanged',
    'Shuriken',
    'Bastard Sword_Reaver',
    'Bastard Sword_Vald',
    'Battleaxe',
    'Dwarven Waraxe',
    'Katana_Kin',
    'Katana_Soul',
    'Light Flail',
    'Longsword',
    'Morningstar',
    'Rapier_Stinger',
    'Rapier_Touch',
    'Scimitar',
    'Warhammer_Dementia',
    'Warhammer_Mjolnir',
    'Club_Fish',
    'Club_Stone',
    'Dagger_FW',
    'Dagger_PK',
    'Handaxe_Adam',
    'Handaxe_Ichor',
    'Kukri',
    'Light Hammer',
    'Mace',
    'Shortsword_Adam',
    'Shortsword_Cleaver',
    'Sickle',
    'Whip',
]

# Mapping from CSV name to PURPLE_WEAPONS key
# Based on weapon type and context clues
mapping = {
    'Adamantium Plate Gauntlets': 'Gloves_Adam',
    'Adamantium Sword': 'Shortsword_Adam',
    "Ahriman's Halberd of Sacrifice": 'Halberd',
    'Axe of Caged Souls': 'Greataxe',
    'Bone Axe of Black Ichor': 'Handaxe_Ichor',
    "Bria's Sickle of the Forest": 'Sickle',
    'Cleaver': 'Shortsword_Cleaver',
    'Elemental Impaler': 'Spear',
    'Faith Slayer Axe': 'Battleaxe',
    "Felicia's Swift Reply": 'Light Crossbow',
    'Final Word': 'Dagger_FW',
    'Fist of the Thundercaller': 'Mace',
    'Frost Lance': 'Trident_Ice',
    'Frost Reaver': 'Bastard Sword_Reaver',
    'Frostbite': 'Longsword',
    'Hammer of Dementia': 'Warhammer_Dementia',
    'Hammer of the Frozen North': 'Light Hammer',
    "Harvest's Blessing": 'Kama',
    'Hell Shooter': 'Longbow',
    'Inconsequence': 'Kukri',
    'Katanakin': 'Katana_Kin',
    "Lesser Ahriman's Trident": 'Trident_Fire',
    "Lesser Valdimirs Sword": 'Bastard Sword_Vald',
    "Lightning's Flight": 'Shortbow',
    "Mastadon's Bone Crusher": 'Dire Mace',
    'Meat Carver': 'Scimitar',
    'Phase Killer': 'Dagger_PK',
    'Poorly Preserved Black Herring': 'Club_Fish',
    'Reclaimed Adamantium Axe': 'Handaxe_Adam',
    'Scepter of the Brightest Night': 'N/A',  # Staff - not in PURPLE_WEAPONS
    'Screamer': 'Throwing Axes',
    'Serial Killer': 'Scythe',
    'Shadowsteel Star': 'Shuriken',
    'Sling of Mischief': 'Sling',
    'Soulslicer': 'Katana_Soul',
    'Spider-Infused Bolts': 'N/A',  # Ammo - not in PURPLE_WEAPONS
    "Staff of Hanged Men": 'Quarterstaff_Hanged',
    'Stinger': 'Rapier_Stinger',
    'Sunfire Arbalest': 'Heavy Crossbow',
    'Touch of Death': 'Rapier_Touch',
    "Tyr's Vengful Gaze": 'Greatsword_Tyr',
    'Wyrm Slayer Axe': 'Dwarven Waraxe',
}

# Read the CSV and display mappings
with open('ADOH - BOSS ITEMS - REBALANCE - Purple Items.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        item_name = row.get('Item Name', '').strip()
        new_col = row.get('NEW', '').strip()
        if item_name in mapping and mapping[item_name] != 'N/A':
            print(f"CSV: {item_name}")
            print(f"→ PURPLE_WEAPONS key: {mapping[item_name]}")
            print(f"Changes: {new_col[:80]}..." if len(new_col) > 80 else f"Changes: {new_col}")
            print()

