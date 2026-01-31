WEAPON_PROPERTIES = {
    # Size column is used to determine DUAL-WIELD penalty
    # MELEE TWO-HANDED WEAPONS:
    'Halberd':          {'dmg': [1, 10, 'slashing & piercing'], 'threat': 20, 'multiplier': 3, 'size': 'L'},
    'Heavy Flail':      {'dmg': [1, 10, 'bludgeoning'],         'threat': 19, 'multiplier': 2, 'size': 'L'},
    'Greataxe':         {'dmg': [1, 12, 'slashing'],            'threat': 20, 'multiplier': 3, 'size': 'L'},
    'Greatsword':       {'dmg': [2, 6,  'slashing'],            'threat': 19, 'multiplier': 2, 'size': 'L'},
    'Scythe':           {'dmg': [2, 4,  'slashing & piercing'], 'threat': 20, 'multiplier': 4, 'size': 'L'},
    'Spear':            {'dmg': [1, 8,  'piercing'],            'threat': 20, 'multiplier': 3, 'size': 'L'},
    'Trident':          {'dmg': [1, 8,  'piercing'],            'threat': 20, 'multiplier': 2, 'size': 'L'},

    # DOUBLE-SIDED WEAPONS:
    'Dire Mace':        {'dmg': [1, 8, 'bludgeoning'],  'threat': 20, 'multiplier': 2, 'size': 'S'},
    'Double Axe':       {'dmg': [1, 8, 'bludgeoning'],  'threat': 20, 'multiplier': 3, 'size': 'S'},
    'Two-Bladed Sword': {'dmg': [1, 8, 'slashing'],     'threat': 19, 'multiplier': 2, 'size': 'S'},

    # RANGED WEAPONS - THROWING:
    'Darts':            {'dmg': [1, 4, 'piercing'],     'threat': 20, 'multiplier': 2, 'size': 'T'},
    'Throwing Axes':    {'dmg': [1, 6, 'slashing'],     'threat': 20, 'multiplier': 3, 'size': 'S'},

    # RANGED WEAPONS - AMMO-BASED:
    'Heavy Crossbow':   {'dmg': [1, 10, 'piercing'],   'threat': 18, 'multiplier': 2, 'size': 'L'},
    'Light Crossbow':   {'dmg': [1, 8,  'piercing'],    'threat': 18, 'multiplier': 2, 'size': 'M'},
    'Longbow':          {'dmg': [1, 8,  'piercing'],    'threat': 20, 'multiplier': 3, 'size': 'L'},
    'Shortbow':         {'dmg': [1, 6,  'piercing'],    'threat': 20, 'multiplier': 3, 'size': 'M'},
    'Sling':            {'dmg': [1, 4,  'bludgeoning'], 'threat': 20, 'multiplier': 2, 'size': 'S'},

    # MONK WEAPONS:
    'Gloves':           {'dmg': [1, 3, 'bludgeoning'], 'threat': 20, 'multiplier': 2, 'size': 'T'},
    'Kama':             {'dmg': [1, 6, 'slashing'],    'threat': 20, 'multiplier': 2, 'size': 'T'},
    'Quarterstaff':     {'dmg': [1, 6, 'bludgeoning'], 'threat': 20, 'multiplier': 2, 'size': 'L'},
    'Shuriken':         {'dmg': [1, 3, 'piercing'],    'threat': 20, 'multiplier': 2, 'size': 'T'},

    # MEDIUM WEAPONS:
    'Bastard Sword':    {'dmg': [1, 10, 'slashing'],   'threat': 19, 'multiplier': 2, 'size': 'M'},
    'Battleaxe':        {'dmg': [1, 8,  'slashing'],    'threat': 20, 'multiplier': 3, 'size': 'M'},
    'Dwarven Waraxe':   {'dmg': [1, 10, 'slashing'],   'threat': 20, 'multiplier': 3, 'size': 'M'},
    'Katana':           {'dmg': [1, 10, 'slashing'],   'threat': 19, 'multiplier': 2, 'size': 'M'},
    'Light Flail':      {'dmg': [1, 8,  'bludgeoning'], 'threat': 20, 'multiplier': 2, 'size': 'M'},
    'Longsword':        {'dmg': [1, 8,  'slashing'],    'threat': 19, 'multiplier': 2, 'size': 'M'},
    'Morningstar':      {'dmg': [1, 8,  'bludgeoning & piercing'],  'threat': 20, 'multiplier': 2, 'size': 'M'},
    'Rapier':           {'dmg': [1, 6,  'piercing'],    'threat': 18, 'multiplier': 2, 'size': 'M'},
    'Scimitar':         {'dmg': [1, 6,  'slashing'],    'threat': 18, 'multiplier': 2, 'size': 'M'},
    'Warhammer':        {'dmg': [1, 8,  'bludgeoning'], 'threat': 20, 'multiplier': 3, 'size': 'M'},

    # SMALL\TINY WEAPONS:
    'Club':             {'dmg': [1, 6, 'bludgeoning'], 'threat': 20, 'multiplier': 2, 'size': 'M'},
    'Dagger':           {'dmg': [1, 4, 'piercing'],    'threat': 19, 'multiplier': 2, 'size': 'T'},
    'Handaxe':          {'dmg': [1, 6, 'piercing'],    'threat': 20, 'multiplier': 3, 'size': 'T'},
    'Kukri':            {'dmg': [1, 4, 'piercing'],    'threat': 18, 'multiplier': 2, 'size': 'T'},
    'Light Hammer':     {'dmg': [1, 8, 'bludgeoning & piercing'],  'threat': 20, 'multiplier': 2, 'size': 'S'},
    'Mace':             {'dmg': [1, 6, 'bludgeoning'], 'threat': 20, 'multiplier': 2, 'size': 'S'},
    'Shortsword':       {'dmg': [1, 6, 'slashing'],    'threat': 19, 'multiplier': 2, 'size': 'S'},
    'Sickle':           {'dmg': [1, 6, 'slashing'],    'threat': 20, 'multiplier': 2, 'size': 'S'},
    'Whip':             {'dmg': [1, 6, 'slashing'],    'threat': 20, 'multiplier': 2, 'size': 'S'},
}
PURPLE_WEAPONS = {
    # MELEE TWO-HANDED WEAPONS:
    # HALBERD SNEAK WAS 2D6
    'Halberd': {'sneak': [2, 6], 'bludgeoning': [2, 12], 'massive': [0, 0, 200], 'legendary': {'proc': 0.05, 'fire': [1, 30], 'pure': [1, 30]}}, # Ahrim's Sacrifice, hold on hit, 43
    'Heavy Flail': {'slashing': [2, 12], 'negative': [2, 6], 'divine': [2, 6], 'magical': [2, 6], 'legendary': {'proc': 0.05, 'physical': [0, 0, 5]}}, # [0, 2.5, 'physical']], # None
    'Greataxe': {'bludgeoning': [2, 12], 'divine': [2, 8], 'fire': [2, 12], 'vs_race_undead': {'piercing': [2, 8]}}, # immune level drain
    'Greatsword_Desert': {'piercing': [2, 12], 'divine': [2, 8], 'fire': [2, 8], 'massive': [2, 12], 'pure': [1, 6]},  # Pure vs. Evil
    'Greatsword_Legion': {'piercing': [2, 12], 'divine': [2, 8], 'cold': [2, 8], 'massive': [2, 12], 'legendary': {'proc': 0.05, 'effect': 'sunder'}},  # Sunder effect (-2 AC for 2 rounds)
    'Greatsword_Tyr': {'bludgeoning': [2, 12], 'divine': [2, 12], 'fire': [2, 6], 'vs_race_undead_outsider': {'pure': [2, 8]}}, # Tyr
    'Scythe': {'bludgeoning': [2, 12], 'negative': [2, 6]},
    'Spear': {'bludgeoning': [2, 10], 'acid': [2, 6], 'cold': [2, 6], 'fire': [2, 6], 'electrical': [2, 6], 'legendary': {'proc': 0.05, 'acid': [2, 6], 'pure': [2, 6]}}, # [0, .35, 'acid'], [0, .35, 'pure']],  # freedom
    'Trident_Fire': {'slashing': [2, 12], 'fire': [2, 12], 'magical': [1, 12], 'negative': [1, 12]}, # Blind on hit, fire immune 20% cold vuln 10$
    'Trident_Ice': {'slashing': [2, 12], 'cold': [2, 12], 'magical': [2, 10], 'massive': [1, 10], 'legendary': {'proc': 'on_crit', 'cold': [2, 6], 'pure': [2, 6]}},  # Icy veng

    # DOUBLE-SIDED WEAPONS:
    'Dire Mace': {'slashing': [8, 6], 'magical': [2, 6]},   # 10% phys immune
    'Double Axe': {'bludgeoning': [7, 6], 'negative': [1, 12], 'massive': [0, 0, 10], 'legendary': {'proc': 0.05, 'physical': [2, 20]}},  # Wounding, vamp regen
    'Two-Bladed Sword': {'bludgeoning': [2, 12], 'positive': [2, 6], 'negative': [2, 6], 'massive': [2, 6]}, # +3 AC, on hit doom

    # RANGED WEAPONS - THROWING:
    'Darts': {'magical': [2, 6], 'pure': [2, 12], 'legendary': {'proc': 0.05, 'pure': [2, 12], 'effect': 'perfect_strike'}},  # [0, 0.65, 'pure']],  # none
    'Throwing Axes': {'sonic': [7, 6], 'massive': [1, 6]},  # silence on hit

    # RANGED WEAPONS - AMMO-BASED:
    'Heavy Crossbow': {'bludgeoning': [2, 12], 'acid': [2, 8], 'magical': [1, 12], 'fire': [2, 6], 'massive': [2, 8]}, # Was "Bolts"
    'Light Crossbow': {'bludgeoning': [2, 12], 'acid': [2, 8], 'magical': [1, 12], 'cold': [1, 10], 'massive': [1, 10]},
    'Longbow': {'bludgeoning': [2, 12], 'negative': [2, 8], 'magical': [1, 12], 'fire': [2, 6], 'massive': [2, 6], 'legendary': {'proc': 'on_crit', 'fire': [2, 6], 'pure': [2, 6]}},    # Was "Arrows"
    'Shortbow': {'bludgeoning': [2, 12], 'negative': [2, 8], 'magical': [1, 12], 'electrical': [1, 10], 'massive': [2, 8]},
    'Sling': {'piercing': [2, 8], 'fire': [2, 8], 'pure': [2, 6], 'divine': [2, 6]},  # was Bullets

    # MONK WEAPONS:
    'Gloves_Shandy': {'piercing': [2, 6], 'acid': [2, 6], 'magical': [2, 6], 'divine': [2, 6]},  # Legendary remove immunities
    'Gloves_Adam': {'slashing': [2, 8], 'pure': [2, 8], 'divine': [2, 8], 'sneak': [1, 6]},    # Doom
    'Kama': {'bludgeoning': [2, 8], 'divine': [2, 6], 'positive': [2, 6]},  # 4 regen, 5% neg & pos
    'Quarterstaff_IcyFire': {'slashing': [2, 10], 'cold': [2, 10], 'fire': [2, 10]},  # 10% fire/cold immune
    'Quarterstaff_Hanged': {'slashing': [2, 12], 'divine': [2, 6], 'negative': [2, 10], 'legendary': {'proc': 'on_crit', 'negative': [1, 8, 3]}},  # On-Crit Negative Energy Burst Level 5 (1d8+3 Negative)
    'Shuriken': {'bludgeoning': [2, 6], 'negative': [2, 6], 'pure': [2, 4], 'sneak': [2, 6]},

    # MEDIUM WEAPONS:
    'Bastard Sword_Reaver': {'bludgeoning': [7, 6], 'cold': [2, 8]}, # 5% Cold imm, On-hit Slow DC=42/50%/1round
    'Bastard Sword_Vald': {'bludgeoning': [2, 6], 'divine': [2, 6], 'magical': [2, 6], 'negative': [2, 6], 'sneak': [1, 6]}, # None
    'Battleaxe': {'bludgeoning': [2, 8], 'magical': [2, 8], 'negative': [2, 8]},  # divine resist 5/ 5% immune
    'Dwarven Waraxe': {'bludgeoning': [2, 8], 'acid': [2, 10], 'negative': [2, 8], 'vs_race_dragon': {'pure': [2, 6]}},    # +12 Enhancement vs. Dragons
    'Katana_Kin': {'bludgeoning': [7, 6], 'pure': [1, 10], 'legendary': {'proc': 0.05, 'physical': [2, 20]}},
    'Katana_Soul': {'bludgeoning': [2, 12], 'divine': [2, 6], 'sonic': [2, 8], 'legendary': {'proc': 0.05, 'fire': [2, 20]}}, # [0, 1.05, 'fire']],  On-Hit Level Drain DC=44, 5% Divine+Sonic imm
    'Light Flail': {'slashing': [7, 6], 'pure': [2, 8], 'legendary': {'proc': 0.05, 'effect': 'sunder'}},  # sunder
    'Longsword': {'bludgeoning': [2, 8], 'cold': [2, 12], 'magical': [2, 6], 'legendary': {'proc': 'on_crit', 'cold': [2, 6], 'pure': [2, 6]}},  # Icy Veng, 2d6 pierce v. undead
    'Morningstar': {'slashing': [2, 6], 'positive': [7, 6], 'massive': [1, 6]},  # divine extend, 10% pos immune
    'Rapier_Stinger': {'bludgeoning': [2, 12], 'acid': [2, 10], 'massive': [0, 0, 15], 'legendary': {'proc': 0.05, 'acid': [2, 6], 'pure': [2, 6]}},
    'Rapier_Touch': {'slashing': [2, 6], 'magical': [2, 6], 'cold': [2, 6], 'massive': [0, 0, 25]},  # + pp skill
    'Scimitar': {'bludgeoning': [7, 6], 'massive': [7, 6]},  # 5% phys immune
    'Warhammer_Dementia': {'slashing': [2, 8], 'positive': [2, 8], 'magical': [2, 8]},  # On-hit Confuse DC=44/5%/5rounds
    'Warhammer_Mjolnir': {'slashing': [7, 6], 'electrical': [2, 6], 'legendary': {'proc': 0.05, 'electrical': [20, 6]}},  # On-hit Chain Lightining lvl 20

    # SMALL\TINY WEAPONS:
    'Club_Fish': {'piercing': [2, 10], 'acid': [7, 6]},  # acid resist 20, on-hit stun
    'Club_Stone': {'piercing': [2, 8], 'sonic': [7, 6], 'legendary': {'proc': 0.05, 'effect': 'crushing_blow'}},  # 5% reduce immunities by 5% for 2 rounds
    'Dagger_FW': {'bludgeoning': [2, 6], 'divine': [2, 4], 'acid': [2, 4], 'pure': [2, 4], 'legendary': {'proc': 0.01, 'physical': [0, 0, 300]}}, # [0, 3, 'physical']],  # Leg Last Words
    'Dagger_PK': {'bludgeoning': [2, 6], 'negative': [2, 6], 'massive': [0, 0, 60]}, # Leg PHASE
    'Handaxe_Adam': {'bludgeoning': [2, 8], 'divine': [2, 6], 'pure': [2, 4]}, # On-hit Doom DC=44/25%/1round
    'Handaxe_Ichor': {'bludgeoning': [2, 6], 'negative': [2, 6], 'acid': [2, 8], 'legendary': {'proc': 0.05, 'acid': [2, 6], 'pure': [2, 6]}},    # [0, .35, 'acid'], [0, .35, 'pure']], # 10% acid immune, on hit poison
    'Kukri': {'bludgeoning': [2, 6], 'divine': [2, 6], 'magical': [2, 6], 'positive': [1, 4]},  # dmg vs alignment
    'Light Hammer': {'slashing': [2, 10], 'cold': [2, 12], 'magical': [1, 6], 'legendary': {'proc': 'on_crit', 'cold': [2, 6], 'pure': [2, 6]}},  # [0, .35, 'electrical'], [0, .35, 'pure']]
    'Mace': {'slashing': [2, 12], 'electrical': [2, 12], 'pure': [1, 6], 'legendary': {'proc': 0.05, 'electrical': [2, 6], 'pure': [2, 6]}}, # [0, .35, 'electrical'], [0, .35, 'pure']], # call Thunder, on-hit stun
    'Shortsword_Adam': {'bludgeoning': [2, 6], 'divine': [2, 6], 'pure': [2, 6]},
    'Shortsword_Cleaver': {'bludgeoning': [2, 6], 'acid': [2, 6], 'negative': [2, 6], 'massive': [2, 12]},  # regen/vampiric
    'Sickle': {'piercing': [2, 10], 'divine': [2, 10]},  # none
    'Whip': {'piercing': [2, 6], 'positive': [2, 8], 'acid': [2, 10], 'legendary': {'proc': 0.05, 'acid': [2, 12]}}, # [0, 0.65, 'acid']],  # acid rain
}
