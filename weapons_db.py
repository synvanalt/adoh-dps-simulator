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
    'Halberd': {'enhancement': 7, 'sneak': [2, 6], 'bludgeoning': [2, 12], 'massive': [0, 0, 200], 'legendary': {'proc': 0.1, 'fire': [1, 50], 'pure': [1, 50]}}, # Ahrim's Sacrifice, hold on hit, 43
    'Heavy Flail': {'enhancement': 7, 'slashing': [2, 12], 'negative': [2, 6], 'divine': [2, 6], 'magical': [2, 6], 'legendary': {'proc': 0.05, 'physical': [0, 0, 5]}}, # [0, 2.5, 'physical']], # None
    'Greataxe': {'enhancement': 7, 'bludgeoning': [2, 12], 'divine': [2, 8], 'fire': [2, 12], 'vs_race_undead': {'enhancement': 12, 'pure': [2, 12]}}, # immune level drain
    'Greatsword_Desert': {'enhancement': 7, 'piercing': [2, 12], 'divine': [2, 8], 'fire': [2, 8], 'massive': [2, 12]},  # Pure vs. Evil
    'Greatsword_Legion': {'enhancement': 7, 'piercing': [2, 12], 'divine': [2, 8], 'cold': [2, 8], 'massive': [2, 12], 'legendary': {'proc': 0.05, 'effect': 'sunder'}},  # Sunder effect (-2 AC for 2 rounds)
    'Greatsword_Tyr': {'enhancement': 7, 'bludgeoning': [2, 12], 'divine': [2, 12], 'fire': [2, 6], 'legendary': {'proc': 0.05, 'divine': [3, 6]}},  # 5% Sunbeam Level 5 (3d6 Divine / 10d6 vs Undead)
    'Scythe': {'enhancement': 10, 'bludgeoning': [2, 12], 'negative': [2, 6], 'pure': [0, 0, 10]},
    'Spear': {'enhancement': 7, 'bludgeoning': [2, 8], 'acid': [2, 6], 'cold': [2, 6], 'fire': [2, 6], 'electrical': [2, 6], 'legendary': {'proc': 0.05, 'acid': [4, 6], 'pure': [4, 6]}}, # Freedom
    'Trident_Fire': {'enhancement': 7, 'slashing': [2, 12], 'fire': [2, 12], 'magical': [1, 12], 'negative': [1, 12], 'legendary': {'proc': 0.05, 'fire': [10, 6]}},  # 5% Fireball lvl 10, Blind on-hit DC46 100% 1round, fire immune 20%, cold vuln 10%
    'Trident_Ice': {'enhancement': 7, 'slashing': [2, 12], 'cold': [2, 12], 'magical': [2, 10], 'massive': [1, 10], 'legendary': {'proc': 0.10, 'cold': [4, 6], 'pure': [4, 6]}},  # Icy veng

    # DOUBLE-SIDED WEAPONS:
    'Dire Mace': {'enhancement': 7, 'slashing': [8, 6], 'magical': [2, 6], 'legendary': {'proc': 'on_crit', 'sonic': [2, 10]}},   # 10% phys immune, potential stun
    'Double Axe': {'enhancement': 7, 'bludgeoning': [7, 6], 'negative': [1, 12], 'massive': [0, 0, 10], 'legendary': {'proc': 0.05, 'physical': [2, 20]}},  # Wounding, vamp regen
    'Two-Bladed Sword': {'enhancement': 7, 'bludgeoning': [2, 12], 'positive': [2, 6], 'negative': [2, 6], 'massive': [2, 6]}, # +3 AC, on hit doom

    # RANGED WEAPONS - THROWING:
    'Darts': {'enhancement': 7, 'magical': [2, 6], 'pure': [2, 12], 'legendary': {'proc': 0.05, 'pure': [4, 6], 'effect': 'perfect_strike'}},  # [0, 0.65, 'pure']],  # none
    'Throwing Axes': {'enhancement': 7, 'sonic': [7, 6], 'massive': [1, 6]},  # On-hit Silence DC46/100%/1round

    # RANGED WEAPONS - AMMO-BASED:
    'Heavy Crossbow': {'enhancement': 7, 'bludgeoning': [2, 12], 'acid': [2, 10], 'magical': [2, 8], 'fire': [2, 6], 'massive': [2, 8], 'legendary': {'proc': 'on_crit', 'fire': [6, 6]}}, # On-crit Firebrand lvl 6
    'Light Crossbow': {'enhancement': 7, 'bludgeoning': [2, 12], 'acid': [2, 10], 'magical': [2, 8], 'cold': [2, 6], 'massive': [1, 10], 'legendary': {'proc': 'on_crit', 'cold': [6, 6]}}, # On-crit Coldbrand lvl 6
    'Longbow_FireDragon': {'enhancement': 7, 'bludgeoning': [2, 12], 'negative': [2, 10], 'magical': [2, 8], 'fire': [2, 6], 'massive': [2, 6], 'legendary': {'proc': 'on_crit', 'fire': [4, 6], 'pure': [4, 6]}},
    'Longbow_FireCeles': {'enhancement': 7, 'bludgeoning': [7, 6], 'divine': [2, 10], 'fire': [2, 6], 'massive': [2, 6], 'legendary': {'proc': 'on_crit', 'fire': [4, 6], 'pure': [4, 6]}},
    'Longbow_ElecDragon': {'enhancement': 7, 'bludgeoning': [2, 12], 'negative': [2, 10], 'magical': [2, 8], 'electrical': [2, 6], 'legendary': {'proc': 0.1, 'electrical': [20, 6]}},  # On-hit Chain Lightining lvl 20
    'Longbow_ElecCeles': {'enhancement': 7, 'bludgeoning': [7, 6], 'divine': [2, 10], 'electrical': [2, 6], 'legendary': {'proc': 0.1, 'electrical': [20, 6]}},  # On-hit Chain Lightining lvl 20
    'Shortbow_Dragon': {'enhancement': 7, 'bludgeoning': [2, 12], 'negative': [2, 10], 'magical': [2, 8], 'electrical': [2, 6], 'massive': [2, 8]}, # SoV extend by 5 rounds, SoV immune, Elec 10% immune
    'Shortbow_Celes': {'enhancement': 7, 'bludgeoning': [7, 6], 'divine': [2, 10], 'magical': [2, 8], 'electrical': [2, 6], 'massive': [2, 8]},  # SoV extend by 5 rounds, SoV immune, Elec 10% immune
    'Sling': {'enhancement': 7, 'piercing': [2, 8], 'fire': [2, 8], 'pure': [2, 6], 'divine': [2, 6]},  # On-hit 5%: gain 20% movement speed for 30sec (can't stack)

    # MONK WEAPONS:
    'Gloves_Shandy': {'enhancement': 7, 'piercing': [2, 6], 'acid': [2, 6], 'magical': [2, 6], 'divine': [2, 6]},  # Legendary remove immunities
    'Gloves_Adam': {'enhancement': 7, 'slashing': [2, 8], 'pure': [2, 8], 'divine': [2, 8], 'sneak': [1, 6]},    # Doom - NEED MANUAL FIX
    'Kama': {'enhancement': 7, 'bludgeoning': [2, 8], 'divine': [2, 6], 'positive': [2, 6], 'legendary': {'proc': 0.05, 'effect': 'deep_cuts', 'damage': [2, 20]}},  # 4 regen, 5% neg & pos
    'Quarterstaff_IcyFire': {'enhancement': 7, 'slashing': [2, 10], 'cold': [2, 10], 'fire': [2, 10]},  # 10% fire/cold immune
    'Quarterstaff_Hanged': {'enhancement': 7, 'slashing': [2, 12], 'divine': [2, 6], 'negative': [2, 10], 'legendary': {'proc': 'on_crit', 'negative': [1, 8, 3]}},  # On-Crit Negative Energy Burst Level 5 (1d8+3 Negative)
    'Shuriken': {'enhancement': 7, 'bludgeoning': [2, 6], 'negative': [2, 6], 'pure': [2, 4], 'sneak': [2, 6]}, # On-hit 3%: gain 90% concealment for 1 round

    # MEDIUM WEAPONS:
    'Bastard Sword_Reaver': {'enhancement': 7, 'bludgeoning': [7, 6], 'cold': [2, 8]}, # 5% Cold imm, On-hit Slow DC42/100%/1round
    'Bastard Sword_Vald': {'enhancement': 7, 'bludgeoning': [2, 6], 'divine': [2, 6], 'magical': [2, 6], 'negative': [2, 6], 'sneak': [1, 6], 'legendary': {'proc': 0.05, 'pure': [10, 6]}}, # 2d6 Pure per second in 2.25 radius, lasts 5 seconds
    'Battleaxe': {'enhancement': 7, 'bludgeoning': [2, 8], 'magical': [2, 8], 'negative': [2, 8], 'vs_race_good': {'pure': [2, 12]}},  # Divine resist 5/-, Divine 5% immune
    'Dwarven Waraxe': {'enhancement': 7, 'bludgeoning': [2, 8], 'acid': [2, 10], 'negative': [2, 8], 'vs_race_dragon': {'enhancement': 12, 'pure': [4, 10]}},    # +12 Enhancement vs. Dragons, Immunity Knockdown & Fear
    'Katana_Kin': {'enhancement': 7, 'bludgeoning': [7, 6], 'pure': [1, 10], 'legendary': {'proc': 0.10, 'physical': [2, 20]}},
    'Katana_Soul': {'enhancement': 7, 'bludgeoning': [2, 12], 'divine': [2, 6], 'sonic': [2, 8], 'legendary': {'proc': 0.10, 'fire': [2, 20]}}, # On-Hit Level Drain DC=44, 5% Divine+Sonic imm
    'Light Flail': {'enhancement': 7, 'slashing': [7, 6], 'pure': [2, 8], 'legendary': {'proc': 0.05, 'effect': 'sunder'}},  # sunder
    'Longsword': {'enhancement': 7, 'bludgeoning': [2, 8], 'cold': [2, 12], 'magical': [2, 6], 'vs_race_undead': {'piercing': [2, 6]}, 'legendary': {'proc': 'on_crit', 'cold': [4, 6], 'pure': [4, 6]}},  # Icy Veng, 2d6 pierce v. undead
    'Morningstar': {'enhancement': 7, 'slashing': [2, 6], 'positive': [7, 6], 'massive': [1, 6]},  # divine extend, 10% pos immune
    'Rapier_Stinger': {'enhancement': 7, 'bludgeoning': [2, 12], 'acid': [2, 10], 'massive': [0, 0, 15], 'legendary': {'proc': 0.05, 'acid': [4, 6], 'pure': [4, 6]}},
    'Rapier_Touch': {'enhancement': 7, 'slashing': [2, 6], 'magical': [2, 6], 'cold': [2, 6], 'massive': [0, 0, 25], 'legendary': {'proc': 'on_crit', 'negative': [1, 8, 3]}},  # On-Crit Negative Energy Burst Level 5 (1d8+3 Negative), + pp skill
    'Scimitar': {'enhancement': 7, 'bludgeoning': [7, 6], 'massive': [7, 6]},  # 5% phys immune, On-crit heal 2% missing HP
    'Warhammer_Dementia': {'enhancement': 7, 'slashing': [2, 8], 'positive': [2, 8], 'magical': [2, 8]},  # On-hit Confuse DC=44/50%/2rounds, On-hit 5% reduce Conc by 10
    'Warhammer_Mjolnir': {'enhancement': 7, 'slashing': [7, 6], 'electrical': [2, 6], 'legendary': {'proc': 0.05, 'electrical': [20, 6]}},  # On-hit Chain Lightining lvl 20

    # SMALL\TINY WEAPONS:
    'Club_Fish': {'enhancement': 7, 'piercing': [2, 10], 'acid': [7, 6], 'legendary': {'proc': 0.05, 'acid': [4, 6], 'pure': [4, 6]}},  # Acid 20/-
    'Club_Stone': {'enhancement': 7, 'piercing': [2, 8], 'sonic': [7, 6], 'legendary': {'proc': 0.05, 'effect': 'crushing_blow'}},  # 5% reduce immunities by 5% for 2 rounds
    'Dagger_FW': {'enhancement': 7, 'bludgeoning': [2, 6], 'divine': [2, 4], 'acid': [2, 4], 'pure': [2, 4], 'legendary': {'proc': 0.02, 'physical': [0, 0, 300]}}, # [0, 3, 'physical']],  # Leg Last Words
    'Dagger_PK': {'enhancement': 7, 'bludgeoning': [2, 6], 'negative': [2, 6], 'massive': [0, 0, 80]}, # On-hit 5%: gain 90% concealment for 1 round
    'Handaxe_Adam': {'enhancement': 7, 'bludgeoning': [2, 8], 'divine': [2, 6], 'pure': [2, 4], 'sneak': [1, 6]}, # On-hit 5%: receive 5% phys immune 2 rounds (stacks)
    'Handaxe_Ichor': {'enhancement': 7, 'bludgeoning': [2, 6], 'negative': [2, 6], 'acid': [2, 8], 'legendary': {'proc': 0.05, 'acid': [4, 6], 'pure': [4, 6]}},  # 10% acid immune, on-hit poison
    'Kukri_Crow': {'enhancement': 7, 'bludgeoning': [2, 12], 'divine': [2, 8], 'legendary': {'proc': 0.05, 'pure': [4, 6], 'effect': 'perfect_strike'}},  # Legend Effect TBD
    'Kukri_Inconseq': {'enhancement': 7, 'bludgeoning': [2, 6], 'divine': [2, 6], 'magical': [2, 6], 'vs_race_good_evil': {'positive': [1, 4]}, 'legendary': {'proc': 'on_crit', 'effect': 'inconsequence'}},  # Legend Effect TBD
    'Light Hammer': {'enhancement': 7, 'slashing': [2, 10], 'cold': [2, 12], 'magical': [1, 6], 'legendary': {'proc': 'on_crit', 'cold': [4, 6], 'pure': [4, 6]}},
    'Mace': {'enhancement': 7, 'slashing': [2, 12], 'electrical': [2, 12], 'pure': [1, 6], 'legendary': {'proc': 0.05, 'electrical': [4, 6], 'pure': [4, 6]}}, # call Thunder, on-hit Stun 44DC 50%/1round
    'Shortsword_Adam': {'enhancement': 7, 'bludgeoning': [2, 6], 'divine': [2, 6], 'pure': [2, 6]},   # On-hit 5%: receive 5% phys immune 2 rounds (stacks)
    'Shortsword_Cleaver': {'enhancement': 7, 'bludgeoning': [2, 6], 'acid': [2, 6], 'negative': [2, 6], 'massive': [2, 12]},  # 5% on-hit: target receives 5% miss chance (stacks), Vamp regen +5
    'Sickle': {'enhancement': 7, 'piercing': [2, 10], 'divine': [2, 10]},  # Creeping Doom +1000 dmg
    'Whip': {'enhancement': 7, 'piercing': [2, 6], 'positive': [2, 8], 'acid': [2, 10], 'legendary': {'proc': 0.05, 'acid': [2, 12]}}, # [0, 0.65, 'acid']],  # acid rain
}
