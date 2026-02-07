from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Union


@dataclass
class Config:
    # USER INPUTS - TARGET
    TARGET_AC: int = 65
    TARGET_IMMUNITIES_FLAG: bool = True
    TARGET_IMMUNITIES: Dict[str, float] = field(default_factory=lambda: {
        "pure": 0.0,
        "magical": 0.1,
        "positive": 0.1,
        "divine": 0.1,
        "negative": 0.25,
        "sonic": 0.25,
        "acid": 0.25,
        "electrical": 0.25,
        "cold": 0.25,
        "fire": 0.25,
        "physical": 0.25,
    })

    # SIMULATION SETTINGS
    DEFAULT_WEAPONS: List[str] = field(default_factory=lambda: ["Spear"])
    ROUNDS: int = 15000
    DAMAGE_LIMIT_FLAG: bool = False
    DAMAGE_LIMIT: int = 6000
    DAMAGE_VS_RACE: bool = False
    CHANGE_THRESHOLD: float = 0.0002
    STD_THRESHOLD: float = 0.0002

    # USER INPUTS - CHARACTER
    AB: int = 68
    AB_CAPPED: int = 70
    AB_PROG: str = "5APR Classic"
    AB_PROGRESSIONS: Dict[str, List[Union[int, str]]] = field(default_factory=lambda: {
        "4APR Classic":                     [0, -5, -10, "hasted"],
        "4APR & Blinding Speed":            [0, -5, -10, "hasted", "bspeed"],
        "4APR & Rapid Shot":                [0, -5, -10, "hasted", "rapid"],
        "4APR & R.Shot & B.Speed":          [0, -5, -10, "hasted", "rapid", "bspeed"],
        "5APR Classic":                     [0, -5, -10, -15, "hasted"],
        "5APR Shifter":                     [0, -5, -10, "hasted", "shifter"],
        "5APR & Blinding Speed":            [0, -5, -10, -15, "hasted", "bspeed"],
        "5APR & Rapid Shot":                [0, -5, -10, -15, "hasted", "rapid"],
        "5APR & R.Shot & B.Speed":          [0, -5, -10, -15, "hasted", "rapid", "bspeed"],
        "Monk 6APR":                        [0, -3, -6, -9, -12, "hasted"],
        "Monk 6APR & Flurry":               [0, -3, -6, -9, -12, "hasted", "flurry"],
        "Monk 6APR & Flurry & B.Speed":     [0, -3, -6, -9, -12, "hasted", "flurry", "bspeed"],
        "Monk 7APR":                        [0, -3, -6, -9, -12, -15, "hasted"],
        "Monk 7APR & Flurry":               [0, -3, -6, -9, -12, -15, "hasted", "flurry"],
        "Monk 7APR & Flurry & B.Speed":     [0, -3, -6, -9, -12, -15, "hasted", "flurry", "bspeed"],
    })

    # DUAL-WIELD SETTINGS
    DUAL_WIELD: bool = False
    CHARACTER_SIZE: str = "M"        # "S" / "M" / "L"
    TWO_WEAPON_FIGHTING: bool = True
    AMBIDEXTERITY: bool = True
    IMPROVED_TWF: bool = True
    CUSTOM_OFFHAND_WEAPON: bool = False
    OFFHAND_WEAPON: str = "Scimitar"
    OFFHAND_AB: int = 68  # Default same as AB
    OFFHAND_KEEN: bool = True
    OFFHAND_IMPROVED_CRIT: bool = True
    OFFHAND_OVERWHELM_CRIT: bool = False
    OFFHAND_DEV_CRIT: bool = False
    OFFHAND_WEAPONMASTER_THREAT: bool = False

    COMBAT_TYPE: str = "melee"  # "melee" or "ranged"
    MIGHTY: int = 0
    ENHANCEMENT_SET_BONUS: int = 3  # 1/2/3 (for example, +3 for Pure Green Vengeful set)
    STR_MOD: int = 21
    TWO_HANDED: bool = False
    WEAPONMASTER: bool = False
    KEEN: bool = True
    IMPROVED_CRIT: bool = True
    OVERWHELM_CRIT: bool = False
    DEV_CRIT: bool = False
    SHAPE_WEAPON_OVERRIDE: bool = False
    SHAPE_WEAPON: str = "Scythe"

    # EXTRA DAMAGE SOURCES: name: [enabled, {damage_type: [dice, sides, flat]}, description]
    ADDITIONAL_DAMAGE: Dict[str, Any] = field(default_factory=lambda: {
        "Bane_of_Enemies":  [False, {'physical':    [2, 6, 0]},     "Ranger epic feat, Physical damage bonus vs favored enemies."],
        "Bard_Song":        [False, {'physical':    [0, 0, 3]},     "Physical damage bonus from Bard song."],
        "Blade_Thirst":     [False, {'physical':    [0, 0, 6]},     "Ranger spell, Physical damage bonus."],
        "Bless_Weapon":     [False, {'divine':      [2, 6, 0]},     "Divine damage bonus (weapon property) vs Undead."],
        "Darkfire":         [False, {'fire_fw':     [1, 6, 10]},    "Fire damage bonus (on-hit property)."],
        "Death_Attack":     [False, {'death':       [3, 6, 0]},     "Physical damage bonus on Death Attacks."],
        "Defeaning_Clang":  [False, {'sonic':       [0, 0, 3]},     "Paladin spell, Sonic damage bonus (weapon property)."],
        "Divine_Favor":     [False, {'magical':     [0, 0, 5]},     "Paladin/Cleric spell, Magical damage bonus."],
        "Divine_Might":     [False, {'divine':      [0, 0, 11]},    "Paladin/Blackguard feat, Divine damage bonus."],
        "Divine_Wrath":     [False, {'pure':        [0, 0, 13]},    "Divine Champion feat, Pure damage bonus."],
        "Domain_STR_Evil":  [False, {'negative':    [0, 0, 15]},    "Cleric domain, Negative damage bonus (evil alignment)."],
        "Domain_STR_Good":  [False, {'divine':      [0, 0, 15]},    "Cleric domain, Divine damage bonus (good/neutral alignment)."],
        "Enchant_Arrow":    [False, {'physical':    [0, 0, 15]},    "Arcane Archer feat, Physical damage bonus."],
        "Favored_Enemy":    [False, {'physical':    [0, 0, 9]},     "Ranger feat, Physical damage bonus vs favored enemies."],
        "Flame_Weapon":     [True,  {'fire_fw':     [1, 4, 10]},    "Fire damage bonus (on-hit property)."],
        "Set_Bonus_Damage": [False, {'pure':        [1, 4, 0]},     "Pure damage bonus (weapon property) from equipment Set Bonus."],
        "Sneak_Attack":     [False, {'sneak':       [5, 6, 0]},     "Physical damage bonus on Sneak Attacks."],
        "Tenacious_Blow":   [False, {'physical':    [0, 0, 8]},     "For double-sided weapons only: +8 Physical bonus damage on-hit, +4 Pure bonus damage on-miss."],
        "Weapon_Spec":      [False, {'physical':    [0, 0, 2]},     "Fighter feat, Physical damage bonus."],
        "Weapon_Spec_Epic": [False, {'physical':    [0, 0, 4]},     "Fighter feat, Physical damage bonus."],
    })


if __name__ == '__main__':
    # --- Usage example ---
    cfg = Config()

    # Access like dataclass
    print(cfg.AB)
    print(cfg.AB_PROGRESSIONS["Classic 5APR"])

    # Update dynamically from a Dash widget
    cfg.AB = 72
    cfg.ADDITIONAL_DAMAGE["Darkfire"][0] = True

    print(cfg.AB)
    print(cfg.ADDITIONAL_DAMAGE["Darkfire"])

    # Convert to dict for JSON / dcc.Store
    config_dict = asdict(cfg)

    # Restore from JSON:
    # Config(**json_data)