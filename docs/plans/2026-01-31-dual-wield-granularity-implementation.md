# Dual-Wield Granularity Enhancement - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Separate dual-wield from AB progressions and add granular feat-based control (TWF, Ambidexterity, Improved TWF).

**Architecture:** Refactor Config to add 4 new dual-wield fields, clean up AB_PROGRESSIONS (24→15 entries), refactor attack_simulator.py to calculate separate primary/off-hand penalties, update UI to move Character Size under dual-wield section and add 3 feat toggles, update callbacks for show/hide and config integration.

**Tech Stack:** Python 3.12, Dash/Plotly, pytest

---

## Task 1: Update Config Data Model

**Files:**
- Modify: `simulator/config.py:1-125`

### Step 1: Add new dual-wield fields to Config dataclass

```python
# After TOON_SIZE (around line 67), add:
# DUAL-WIELD SETTINGS
DUAL_WIELD: bool = False
TWO_WEAPON_FIGHTING: bool = True
AMBIDEXTERITY: bool = True
IMPROVED_TWF: bool = True
```

### Step 2: Update AB_PROGRESSIONS dictionary

Replace lines 37-65 with markers-based progressions (remove 12 dual-wield variants):

```python
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
```

### Step 3: Verify config changes

Run: `python -c "from simulator.config import Config; c = Config(); print(len(c.AB_PROGRESSIONS)); print(c.DUAL_WIELD)"`

Expected: `15` and `False`

### Step 4: Commit config changes

```bash
git add simulator/config.py
git commit -m "feat: add dual-wield config fields and clean up AB progressions

- Add 4 new dual-wield boolean fields (DUAL_WIELD, TWO_WEAPON_FIGHTING, AMBIDEXTERITY, IMPROVED_TWF)
- Remove 12 dual-wield variants from AB_PROGRESSIONS (24→15 entries)
- Add string markers for special attacks (hasted, flurry, bspeed, rapid, shifter)"
```

---

## Task 2: Add Helper Methods to AttackSimulator

**Files:**
- Modify: `simulator/attack_simulator.py:1-257`

### Step 1: Write test for _is_valid_dw_config

Add to `tests/simulator/test_attack_simulator.py` after existing tests:

```python
def test_is_valid_dw_config_medium_with_medium():
    """Medium character CAN dual-wield Medium weapon"""
    cfg = Config()
    cfg.TOON_SIZE = 'M'
    weapon = Weapon("Spear_Riftmaker", cfg)  # Medium weapon
    attack_sim = AttackSimulator(weapon, cfg)
    assert attack_sim._is_valid_dw_config() == True

def test_is_valid_dw_config_small_with_medium():
    """Small character CANNOT dual-wield Medium weapon"""
    cfg = Config()
    cfg.TOON_SIZE = 'S'
    cfg.AB_PROG = "4APR Classic"  # Use valid progression
    weapon = Weapon("Spear_Riftmaker", cfg)  # Medium weapon
    attack_sim = AttackSimulator(weapon, cfg)
    assert attack_sim._is_valid_dw_config() == False

def test_is_valid_dw_config_large_with_tiny():
    """Large character CANNOT dual-wield Tiny weapon"""
    cfg = Config()
    cfg.TOON_SIZE = 'L'
    cfg.AB_PROG = "4APR Classic"
    weapon = Weapon("Dagger_Heartseeker", cfg)  # Tiny weapon
    attack_sim = AttackSimulator(weapon, cfg)
    assert attack_sim._is_valid_dw_config() == False

def test_is_valid_dw_config_large_weapon():
    """Large weapons CANNOT be dual-wielded (except double-sided)"""
    cfg = Config()
    cfg.TOON_SIZE = 'M'
    cfg.AB_PROG = "4APR Classic"
    weapon = Weapon("Greatsword_Stormblade", cfg)  # Large weapon
    attack_sim = AttackSimulator(weapon, cfg)
    assert attack_sim._is_valid_dw_config() == False
```

### Step 2: Run tests to verify they fail

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/simulator/test_attack_simulator.py::test_is_valid_dw_config_medium_with_medium -v`

Expected: AttributeError: 'AttackSimulator' object has no attribute '_is_valid_dw_config'

### Step 3: Implement _is_valid_dw_config method

Add after `calculate_attack_bonus` method (around line 37):

```python
def _is_valid_dw_config(self):
    """
    Check if dual-wielding is valid for character/weapon size combination.

    Valid combinations:
    - Medium: M, S, T, Double-sided
    - Small: S, T
    - Large: M, S

    :return: True if valid, False if illegal configuration
    """
    toon_size = self.cfg.TOON_SIZE
    weapon_size = self.weapon.size

    # Special: Medium can dual-wield double-sided (even though Large)
    if (toon_size == 'M'
        and self.weapon.name_base in DOUBLE_SIDED_WEAPONS
        and not self.cfg.SHAPE_WEAPON_OVERRIDE):
        return True

    # Large weapons cannot be dual-wielded
    if weapon_size == 'L':
        return False

    # Small cannot dual-wield Medium
    if toon_size == 'S' and weapon_size == 'M':
        return False

    # Large cannot dual-wield Tiny
    if toon_size == 'L' and weapon_size == 'T':
        return False

    return True
```

### Step 4: Run validation tests

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/simulator/test_attack_simulator.py::test_is_valid_dw_config -v -k "is_valid"`

Expected: All 4 tests PASS

### Step 5: Write test for _is_weapon_light

Add to test file:

```python
def test_is_weapon_light_medium_with_small():
    """Medium character with Small weapon = light"""
    cfg = Config()
    cfg.TOON_SIZE = 'M'
    weapon = Weapon("Shortsword_Sunblade", cfg)  # Small weapon
    attack_sim = AttackSimulator(weapon, cfg)
    assert attack_sim._is_weapon_light() == True

def test_is_weapon_light_medium_with_medium():
    """Medium character with Medium weapon = NOT light"""
    cfg = Config()
    cfg.TOON_SIZE = 'M'
    weapon = Weapon("Spear_Riftmaker", cfg)  # Medium weapon
    attack_sim = AttackSimulator(weapon, cfg)
    assert attack_sim._is_weapon_light() == False

def test_is_weapon_light_large_with_medium():
    """Large character with Medium weapon = light"""
    cfg = Config()
    cfg.TOON_SIZE = 'L'
    weapon = Weapon("Spear_Riftmaker", cfg)  # Medium weapon
    attack_sim = AttackSimulator(weapon, cfg)
    assert attack_sim._is_weapon_light() == True
```

### Step 6: Run tests to verify they fail

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/simulator/test_attack_simulator.py::test_is_weapon_light_medium_with_small -v`

Expected: AttributeError: '_is_weapon_light'

### Step 7: Implement _is_weapon_light method

Add after `_is_valid_dw_config`:

```python
def _is_weapon_light(self):
    """
    Determine if weapon counts as 'light' for dual-wielding.
    Light weapons provide +2 penalty reduction for both hands.

    :return: True if weapon is light, False otherwise
    """
    toon_size = self.cfg.TOON_SIZE

    # Double-sided weapons count as light
    if (toon_size == 'M'
        and self.weapon.name_base in DOUBLE_SIDED_WEAPONS
        and not self.cfg.SHAPE_WEAPON_OVERRIDE):
        return True

    # Weapon smaller than wielder
    if ((toon_size == 'L' and self.weapon.size in ['M', 'S']) or
        (toon_size == 'M' and self.weapon.size in ['S', 'T']) or
        (toon_size == 'S' and self.weapon.size == 'T')):
        return True

    return False
```

### Step 8: Run light weapon tests

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/simulator/test_attack_simulator.py::test_is_weapon_light -v -k "is_weapon_light"`

Expected: All 3 tests PASS

### Step 9: Write test for calculate_dw_penalties

Add to test file:

```python
def test_calculate_dw_penalties_no_feats_normal_weapon():
    """No feats, normal weapon: -6/-10"""
    cfg = Config()
    cfg.TWO_WEAPON_FIGHTING = False
    cfg.AMBIDEXTERITY = False
    cfg.TOON_SIZE = 'M'
    weapon = Weapon("Spear_Riftmaker", cfg)  # Medium weapon (not light for Medium)
    attack_sim = AttackSimulator(weapon, cfg)
    primary, offhand = attack_sim.calculate_dw_penalties()
    assert primary == -6
    assert offhand == -10

def test_calculate_dw_penalties_twf_only():
    """TWF only: -4/-8"""
    cfg = Config()
    cfg.TWO_WEAPON_FIGHTING = True
    cfg.AMBIDEXTERITY = False
    cfg.TOON_SIZE = 'M'
    weapon = Weapon("Spear_Riftmaker", cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    primary, offhand = attack_sim.calculate_dw_penalties()
    assert primary == -4
    assert offhand == -8

def test_calculate_dw_penalties_all_feats_light_weapon():
    """TWF + Ambi + Light: -2/-2"""
    cfg = Config()
    cfg.TWO_WEAPON_FIGHTING = True
    cfg.AMBIDEXTERITY = True
    cfg.TOON_SIZE = 'M'
    weapon = Weapon("Shortsword_Sunblade", cfg)  # Small weapon (light for Medium)
    attack_sim = AttackSimulator(weapon, cfg)
    primary, offhand = attack_sim.calculate_dw_penalties()
    assert primary == -2
    assert offhand == -2
```

### Step 10: Run penalty tests to verify they fail

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/simulator/test_attack_simulator.py::test_calculate_dw_penalties_no_feats_normal_weapon -v`

Expected: AttributeError: 'calculate_dw_penalties'

### Step 11: Implement calculate_dw_penalties method

Add after `_is_weapon_light`:

```python
def calculate_dw_penalties(self):
    """
    Calculate primary and off-hand penalties based on feats and weapon size.

    Penalty matrix:
    - Base: -6 primary, -10 off-hand
    - TWF feat: +2 to both
    - Ambidexterity: +4 to off-hand
    - Light weapon: +2 to both

    :return: Tuple of (primary_penalty, offhand_penalty)
    """
    primary_penalty = -6
    offhand_penalty = -10

    is_light = self._is_weapon_light()

    if self.cfg.TWO_WEAPON_FIGHTING:
        primary_penalty += 2
        offhand_penalty += 2

    if self.cfg.AMBIDEXTERITY:
        offhand_penalty += 4

    if is_light:
        primary_penalty += 2
        offhand_penalty += 2

    return primary_penalty, offhand_penalty
```

### Step 12: Run penalty tests

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/simulator/test_attack_simulator.py::test_calculate_dw_penalties -v -k "calculate_dw_penalties"`

Expected: All 3 tests PASS

### Step 13: Commit helper methods

```bash
git add simulator/attack_simulator.py tests/simulator/test_attack_simulator.py
git commit -m "feat: add dual-wield helper methods to AttackSimulator

- Add _is_valid_dw_config() to validate character/weapon size combinations
- Add _is_weapon_light() to determine if weapon counts as light
- Add calculate_dw_penalties() to calculate primary/off-hand penalties
- Add comprehensive tests for all helper methods"
```

---

## Task 3: Add Progression Building Methods

**Files:**
- Modify: `simulator/attack_simulator.py:1-300`
- Modify: `tests/simulator/test_attack_simulator.py`

### Step 1: Write test for _build_simple_progression

Add to test file:

```python
def test_build_simple_progression_with_markers():
    """Test simple progression converts markers to offsets"""
    cfg = Config()
    cfg.AB = 68
    cfg.AB_PROG = "4APR & Blinding Speed"  # [0, -5, -10, "hasted", "bspeed"]
    cfg.DUAL_WIELD = False
    weapon = Weapon("Spear_Riftmaker", cfg)
    attack_sim = AttackSimulator(weapon, cfg)

    # Manually call helper to test it
    offsets = [0, -5, -10, "hasted", "bspeed"]
    result = attack_sim._build_simple_progression(offsets)

    # Expected: [68, 63, 58, 68, 63]
    # Main attacks: 68+0=68, 68-5=63, 68-10=58
    # Special attacks: hasted at 0=68, bspeed at -5=63
    assert result == [68, 63, 58, 68, 63]

def test_build_simple_progression_three_specials():
    """Test special attacks follow 0, -5, -10 progression"""
    cfg = Config()
    cfg.AB = 70
    cfg.DUAL_WIELD = False
    weapon = Weapon("Spear_Riftmaker", cfg)
    attack_sim = AttackSimulator(weapon, cfg)

    offsets = [0, "hasted", "rapid", "bspeed"]
    result = attack_sim._build_simple_progression(offsets)

    # Expected: [70, 70, 65, 60]
    # Main: 70+0=70
    # Specials: hasted=70, rapid=65, bspeed=60
    assert result == [70, 70, 65, 60]
```

### Step 2: Run tests to verify they fail

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/simulator/test_attack_simulator.py::test_build_simple_progression_with_markers -v`

Expected: AttributeError: '_build_simple_progression'

### Step 3: Implement _build_simple_progression

Add after `calculate_dw_penalties`:

```python
def _build_simple_progression(self, attack_prog_offsets):
    """
    Build attack progression when dual-wield is disabled.
    Convert string markers to their actual AB offsets.

    Special attacks follow progression: 1st at 0, 2nd at -5, 3rd at -10

    :param attack_prog_offsets: List of offsets and markers, e.g., [0, -5, -10, "hasted", "bspeed"]
    :return: List of ABs, e.g., [68, 63, 58, 68, 63]
    """
    attack_prog = []
    special_attack_count = 0

    for offset in attack_prog_offsets:
        if isinstance(offset, str):
            # Marker for special attack (hasted, flurry, bspeed, etc.)
            # Apply progression: 0, -5, -10
            special_offset = special_attack_count * -5
            attack_prog.append(self.ab + special_offset)
            special_attack_count += 1
        else:
            # Regular integer offset
            attack_prog.append(self.ab + offset)

    return attack_prog
```

### Step 4: Run simple progression tests

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/simulator/test_attack_simulator.py::test_build_simple_progression -v -k "build_simple"`

Expected: All 2 tests PASS

### Step 5: Write test for _build_dw_progression

Add to test file:

```python
def test_build_dw_progression_basic():
    """Test DW progression applies penalties correctly"""
    cfg = Config()
    cfg.AB = 68
    cfg.DUAL_WIELD = True
    cfg.TWO_WEAPON_FIGHTING = True
    cfg.AMBIDEXTERITY = True
    cfg.TOON_SIZE = 'M'
    cfg.IMPROVED_TWF = True
    weapon = Weapon("Shortsword_Sunblade", cfg)  # Small weapon, light for Medium
    attack_sim = AttackSimulator(weapon, cfg)

    # TWF + Ambi + Light = -2/-2
    primary_penalty = -2
    offhand_penalty = -2
    offsets = [0, -5, -10, "hasted"]

    result = attack_sim._build_dw_progression(offsets, primary_penalty, offhand_penalty)

    # Expected: main-hand [66, 61, 56], hasted [68], off-hand [66, 61]
    # Main-hand: 68-2=66, 68-2-5=61, 68-2-10=56
    # Hasted: 68+0=68 (no penalty)
    # Off-hand: 68-2=66, 68-2-5=61
    assert result == [66, 61, 56, 68, 66, 61]

def test_build_dw_progression_no_improved_twf():
    """Test DW without Improved TWF gives only 1 off-hand attack"""
    cfg = Config()
    cfg.AB = 68
    cfg.DUAL_WIELD = True
    cfg.IMPROVED_TWF = False
    cfg.TWO_WEAPON_FIGHTING = True
    cfg.TOON_SIZE = 'M'
    weapon = Weapon("Spear_Riftmaker", cfg)  # Medium weapon, not light
    attack_sim = AttackSimulator(weapon, cfg)

    # TWF only, not light = -4/-8
    primary_penalty = -4
    offhand_penalty = -8
    offsets = [0, -5, "hasted"]

    result = attack_sim._build_dw_progression(offsets, primary_penalty, offhand_penalty)

    # Expected: main [64, 59], hasted [68], off-hand [60]
    assert result == [64, 59, 68, 60]
```

### Step 6: Run tests to verify they fail

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/simulator/test_attack_simulator.py::test_build_dw_progression_basic -v`

Expected: AttributeError: '_build_dw_progression'

### Step 7: Implement _build_dw_progression

Add after `_build_simple_progression`:

```python
def _build_dw_progression(self, attack_prog_offsets, primary_penalty, offhand_penalty):
    """
    Build attack progression when dual-wield is enabled.
    Apply primary penalty to main-hand attacks, keep special attacks penalty-free,
    and append off-hand attacks with offhand penalty.

    :param attack_prog_offsets: List of offsets and markers
    :param primary_penalty: Penalty for main-hand attacks (e.g., -4)
    :param offhand_penalty: Penalty for off-hand attacks (e.g., -4)
    :return: List of ABs, e.g., [64, 59, 54, 68, 64, 59]
    """
    attack_prog = []
    special_attack_count = 0

    # Process main-hand and special attacks
    for offset in attack_prog_offsets:
        if isinstance(offset, str):
            # Special attacks don't get DW penalty, but follow 0, -5, -10 progression
            special_offset = special_attack_count * -5
            attack_prog.append(self.ab + special_offset)
            special_attack_count += 1
        else:
            # Main-hand attacks get primary penalty
            attack_prog.append(self.ab + primary_penalty + offset)

    # Add off-hand attacks
    attack_prog.append(self.ab + offhand_penalty)

    if self.cfg.IMPROVED_TWF:
        attack_prog.append(self.ab + offhand_penalty - 5)

    return attack_prog
```

### Step 8: Run DW progression tests

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/simulator/test_attack_simulator.py::test_build_dw_progression -v -k "build_dw"`

Expected: All 2 tests PASS

### Step 9: Commit progression building methods

```bash
git add simulator/attack_simulator.py tests/simulator/test_attack_simulator.py
git commit -m "feat: add attack progression building methods

- Add _build_simple_progression() for non-dual-wield mode
- Add _build_dw_progression() for dual-wield mode with penalty application
- Add tests for both progression builders with various configurations"
```

---

## Task 4: Refactor get_attack_progression

**Files:**
- Modify: `simulator/attack_simulator.py:109-178`
- Modify: `tests/simulator/test_attack_simulator.py`

### Step 1: Write integration test for refactored method

Add to test file:

```python
def test_get_attack_progression_dual_wield_disabled():
    """Test progression when dual-wield is disabled"""
    cfg = Config()
    cfg.AB = 68
    cfg.AB_PROG = "4APR & Blinding Speed"
    cfg.DUAL_WIELD = False
    weapon = Weapon("Spear_Riftmaker", cfg)
    attack_sim = AttackSimulator(weapon, cfg)

    result = attack_sim.get_attack_progression()

    # Expected: [68, 63, 58, 68, 63]
    assert result == [68, 63, 58, 68, 63]
    assert attack_sim.dual_wield == False

def test_get_attack_progression_dual_wield_enabled():
    """Test progression when dual-wield is enabled with all feats"""
    cfg = Config()
    cfg.AB = 68
    cfg.AB_PROG = "5APR Classic"
    cfg.DUAL_WIELD = True
    cfg.TWO_WEAPON_FIGHTING = True
    cfg.AMBIDEXTERITY = True
    cfg.IMPROVED_TWF = True
    cfg.TOON_SIZE = 'M'
    weapon = Weapon("Shortsword_Sunblade", cfg)  # Light weapon
    attack_sim = AttackSimulator(weapon, cfg)

    result = attack_sim.get_attack_progression()

    # Expected: main [66, 61, 56, 51], hasted [68], off-hand [66, 61]
    # -2/-2 penalties (TWF + Ambi + Light)
    assert result == [66, 61, 56, 51, 68, 66, 61]
    assert attack_sim.dual_wield == True

def test_get_attack_progression_illegal_dw_config():
    """Test illegal DW config returns zeroed progression"""
    cfg = Config()
    cfg.AB = 68
    cfg.AB_PROG = "4APR Classic"
    cfg.DUAL_WIELD = True
    cfg.TOON_SIZE = 'S'
    weapon = Weapon("Spear_Riftmaker", cfg)  # Medium weapon, illegal for Small
    attack_sim = AttackSimulator(weapon, cfg)

    result = attack_sim.get_attack_progression()

    # Expected: all zeros
    assert all(ab == 0 for ab in result)
    assert attack_sim.illegal_dual_wield_config == True
    assert attack_sim.ab == 0
```

### Step 2: Run integration tests to see current behavior

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/simulator/test_attack_simulator.py::test_get_attack_progression_dual_wield_disabled -v`

Expected: FAIL (wrong values because old logic still in place)

### Step 3: Refactor get_attack_progression method

Replace the entire `get_attack_progression` method (lines 109-178) with:

```python
def get_attack_progression(self):
    """
    Determine the attack progression of the character (list of AB).

    If dual-wield is disabled: return base progression with markers converted to offsets
    If dual-wield is enabled: apply penalties and add off-hand attacks

    :return: List of ABs, e.g., [66, 61, 56, 68, 64, 59]
    """
    attack_prog_selected = self.cfg.AB_PROG
    attack_prog_offsets = deepcopy(self.cfg.AB_PROGRESSIONS[attack_prog_selected])

    # Non-dual-wield mode
    if not self.cfg.DUAL_WIELD:
        return self._build_simple_progression(attack_prog_offsets)

    # Dual-wield mode
    self.dual_wield = True

    # Validate configuration
    if not self._is_valid_dw_config():
        self.illegal_dual_wield_config = True
        self.ab = 0
        return [0] * len(attack_prog_offsets)

    # Calculate penalties and build progression
    primary_penalty, offhand_penalty = self.calculate_dw_penalties()
    return self._build_dw_progression(attack_prog_offsets, primary_penalty, offhand_penalty)
```

### Step 4: Run integration tests

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/simulator/test_attack_simulator.py::test_get_attack_progression -v -k "get_attack_progression"`

Expected: All 3 tests PASS

### Step 5: Run full attack_simulator test suite

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/simulator/test_attack_simulator.py -v`

Expected: Some existing tests may FAIL (tests using old dual-wield progressions)

### Step 6: Update existing dual-wield tests

Find and update tests that reference old progressions. Replace progression names like "5APR & Dual-Wield" with "5APR Classic" + cfg.DUAL_WIELD = True.

Example update pattern:
```python
# OLD:
cfg.AB_PROG = "5APR & Dual-Wield"

# NEW:
cfg.AB_PROG = "5APR Classic"
cfg.DUAL_WIELD = True
cfg.TWO_WEAPON_FIGHTING = True
cfg.AMBIDEXTERITY = True
cfg.IMPROVED_TWF = True
```

### Step 7: Run full test suite again

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/simulator/test_attack_simulator.py -v`

Expected: All tests PASS

### Step 8: Commit refactored progression logic

```bash
git add simulator/attack_simulator.py tests/simulator/test_attack_simulator.py
git commit -m "refactor: rewrite get_attack_progression with new dual-wield logic

- Replace old dual-wield progression logic with helper method calls
- Add integration tests for dual-wield enabled/disabled/illegal
- Update existing tests to use new config-based dual-wield approach"
```

---

## Task 5: Update Character Settings UI

**Files:**
- Modify: `components/character_settings.py:84-106,328`

### Step 1: Move Character Size dropdown code

Extract lines 84-106 (Character Size section) and prepare to relocate after dual-wield section.

### Step 2: Add dual-wield master toggle

Insert after AB Progression dropdown (after line 82), before Character Size:

```python
# Dual-Wield Master Toggle
dbc.Row([
    dbc.Col(dbc.Switch(
        id='dual-wield-switch',
        label='Dual-Wield',
        value=cfg.DUAL_WIELD,
        persistence=True,
        persistence_type=persist_type,
    ), xs=12, md=12),
    dbc.Tooltip(
        "Enable dual-wielding to access off-hand attacks and feat configuration. "
        "When enabled, configure Two-Weapon Fighting, Ambidexterity, and Improved TWF feats.",
        target='dual-wield-switch',
        placement='left',
        delay={'show': tooltip_delay},
    ),
], class_name='switcher'),
```

### Step 3: Add Character Size under dual-wield section

Replace old Character Size section with pattern-matching wrapper:

```python
# Character Size (shown only when dual-wield enabled)
dbc.Row([
    dbc.Col(dbc.Label(
        'Character Size:',
        html_for='toon-size-dropdown',
    ), xs=6, md=6),
    dbc.Col(dbc.Select(
        id='toon-size-dropdown',
        options=[
            {'label': 'Small', 'value': 'S'},
            {'label': 'Medium', 'value': 'M'},
            {'label': 'Large', 'value': 'L'}
        ],
        value=cfg.TOON_SIZE,
        persistence=True,
        persistence_type=persist_type,
    ), xs=6, md=6),
    dbc.Tooltip(
        "Used to determine dual-wield penalties based on weapon size. "
        "Smaller weapons relative to character size reduce penalties (light weapon bonus).",
        target='toon-size-dropdown',
        placement='right',
        delay={'show': tooltip_delay},
    ),
], class_name='', id={'type': 'dw-row', 'name': 'character-size'}, style={'display': 'none'}),
```

### Step 4: Add Two-Weapon Fighting switch

```python
# Two-Weapon Fighting feat
dbc.Row([
    dbc.Col(dbc.Switch(
        id='two-weapon-fighting-switch',
        label='Two-Weapon Fighting',
        value=cfg.TWO_WEAPON_FIGHTING,
        persistence=True,
        persistence_type=persist_type,
    ), xs=12, md=12),
    dbc.Tooltip(
        "Reduces dual-wield penalties from -6/-10 to -4/-8 (primary/off-hand). "
        "This feat is essential for effective dual-wielding.",
        target='two-weapon-fighting-switch',
        placement='left',
        delay={'show': tooltip_delay},
    ),
], class_name='switcher', id={'type': 'dw-row', 'name': 'two-weapon-fighting'}, style={'display': 'none'}),
```

### Step 5: Add Ambidexterity switch

```python
# Ambidexterity feat
dbc.Row([
    dbc.Col(dbc.Switch(
        id='ambidexterity-switch',
        label='Ambidexterity',
        value=cfg.AMBIDEXTERITY,
        persistence=True,
        persistence_type=persist_type,
    ), xs=12, md=12),
    dbc.Tooltip(
        "Reduces off-hand penalty by 4. Combined with TWF, brings penalties to -4/-4. "
        "With light weapon bonus, achieves optimal -2/-2 penalties.",
        target='ambidexterity-switch',
        placement='left',
        delay={'show': tooltip_delay},
    ),
], class_name='switcher', id={'type': 'dw-row', 'name': 'ambidexterity'}, style={'display': 'none'}),
```

### Step 6: Add Improved TWF switch

```python
# Improved Two-Weapon Fighting feat
dbc.Row([
    dbc.Col(dbc.Switch(
        id='improved-twf-switch',
        label='Improved Two-Weapon Fighting',
        value=cfg.IMPROVED_TWF,
        persistence=True,
        persistence_type=persist_type,
    ), xs=12, md=12),
    dbc.Tooltip(
        "Grants a second off-hand attack at -5 penalty. "
        "Without this feat, you only get one off-hand attack per round.",
        target='improved-twf-switch',
        placement='left',
        delay={'show': tooltip_delay},
    ),
], class_name='switcher', id={'type': 'dw-row', 'name': 'improved-twf'}, style={'display': 'none'}),
```

### Step 7: Test UI loads without errors

Run: `cd .worktrees/dual-wield-granularity && python app.py`

Visit http://localhost:8050 and verify:
- New dual-wield switch appears
- All 4 sub-widgets are hidden by default
- No console errors

### Step 8: Commit UI changes

```bash
git add components/character_settings.py
git commit -m "feat: add dual-wield UI section to character settings

- Add dual-wield master toggle switch
- Move Character Size dropdown under dual-wield section
- Add Three feat switches: TWF, Ambidexterity, Improved TWF
- All sub-widgets hidden by default (controlled by callback)
- Add descriptive tooltips for all new widgets"
```

---

## Task 6: Add Show/Hide Callback

**Files:**
- Modify: `callbacks/ui_callbacks.py:~330`

### Step 1: Add show/hide callback after existing callbacks

Add at end of `register_ui_callbacks` function (around line 330):

```python
# =========================================================================
# DUAL-WIELD SHOW/HIDE CALLBACK
# =========================================================================

@app.callback(
    [
        Output({'type': 'dw-row', 'name': 'character-size'}, 'style'),
        Output({'type': 'dw-row', 'name': 'two-weapon-fighting'}, 'style'),
        Output({'type': 'dw-row', 'name': 'ambidexterity'}, 'style'),
        Output({'type': 'dw-row', 'name': 'improved-twf'}, 'style'),
    ],
    Input('dual-wield-switch', 'value')
)
def toggle_dual_wield_section(dual_wield_enabled):
    """Show/hide dual-wield feat widgets based on master toggle"""
    if dual_wield_enabled:
        return [{'display': 'block'}] * 4
    else:
        return [{'display': 'none'}] * 4
```

### Step 2: Test show/hide functionality

Run: `cd .worktrees/dual-wield-granularity && python app.py`

Test:
1. Toggle dual-wield switch ON → all 4 widgets should appear
2. Toggle dual-wield switch OFF → all 4 widgets should hide

Expected: Widgets show/hide correctly

### Step 3: Commit callback

```bash
git add callbacks/ui_callbacks.py
git commit -m "feat: add dual-wield show/hide callback

- Toggle visibility of 4 dual-wield widgets based on master switch
- Uses pattern-matching IDs for clean implementation"
```

---

## Task 7: Update Config Callback

**Files:**
- Modify: `callbacks/core_callbacks.py`

### Step 1: Find main config update callback

Search for the callback that updates `config-store` based on user inputs.

Run: `cd .worktrees/dual-wield-granularity && grep -n "Output('config-store'" callbacks/core_callbacks.py | head -5`

### Step 2: Add dual-wield inputs to callback

Add these inputs to the existing callback (find appropriate location in input list):

```python
Input('dual-wield-switch', 'value'),
Input('two-weapon-fighting-switch', 'value'),
Input('ambidexterity-switch', 'value'),
Input('improved-twf-switch', 'value'),
```

### Step 3: Add parameter names to function signature

Add corresponding parameters to the callback function:

```python
dual_wield, two_weapon_fighting, ambidexterity, improved_twf,
```

### Step 4: Add config field updates in function body

Find where config fields are updated (e.g., `cfg.AB = ab`) and add:

```python
cfg.DUAL_WIELD = dual_wield
cfg.TWO_WEAPON_FIGHTING = two_weapon_fighting
cfg.AMBIDEXTERITY = ambidexterity
cfg.IMPROVED_TWF = improved_twf
```

### Step 5: Test config updates

Run: `cd .worktrees/dual-wield-granularity && python app.py`

Test:
1. Toggle dual-wield ON
2. Toggle TWF OFF
3. Run simulation
4. Check that config is correctly applied

Expected: Configuration updates work correctly

### Step 6: Commit config callback changes

```bash
git add callbacks/core_callbacks.py
git commit -m "feat: integrate dual-wield settings into config callback

- Add 4 new inputs for dual-wield switches
- Update config fields when dual-wield settings change
- Ensures dual-wield configuration propagates to simulator"
```

---

## Task 8: Update Reset Callback

**Files:**
- Modify: `callbacks/ui_callbacks.py:210-255`

### Step 1: Add outputs to reset_character_settings callback

Add to output list (after line 227):

```python
Output('dual-wield-switch', 'value', allow_duplicate=True),
Output('two-weapon-fighting-switch', 'value', allow_duplicate=True),
Output('ambidexterity-switch', 'value', allow_duplicate=True),
Output('improved-twf-switch', 'value', allow_duplicate=True),
```

Update the count in `return [dash.no_update] * 16` to `* 20`

### Step 2: Add default values to return statement

Add to return list (after line 254):

```python
False,  # DUAL_WIELD
True,   # TWO_WEAPON_FIGHTING
True,   # AMBIDEXTERITY
True,   # IMPROVED_TWF
```

### Step 3: Test reset functionality

Run: `cd .worktrees/dual-wield-granularity && python app.py`

Test:
1. Toggle dual-wield ON and change feat settings
2. Click reset button
3. Verify dual-wield returns to OFF and feats to ON

Expected: Reset works correctly

### Step 4: Commit reset changes

```bash
git add callbacks/ui_callbacks.py
git commit -m "feat: add dual-wield widgets to reset callback

- Reset dual-wield to OFF (default)
- Reset all feats to ON (default)
- Maintains consistency with Config defaults"
```

---

## Task 9: Update Build Callbacks

**Files:**
- Modify: `callbacks/build_callbacks.py` or wherever build duplication logic exists

### Step 1: Find build duplication callback

Run: `cd .worktrees/dual-wield-granularity && grep -n "duplicate.*build\|copy.*build" callbacks/build_callbacks.py -i`

### Step 2: Add dual-wield states to duplication callback

Add to State list:

```python
State('dual-wield-switch', 'value'),
State('two-weapon-fighting-switch', 'value'),
State('ambidexterity-switch', 'value'),
State('improved-twf-switch', 'value'),
```

### Step 3: Add parameters to function and include in duplication

Add parameters and include in the duplicated build data structure.

### Step 4: Test build duplication

Run: `cd .worktrees/dual-wield-granularity && python app.py`

Test:
1. Configure dual-wield settings
2. Duplicate build
3. Verify new build has same dual-wield settings

Expected: Build duplication copies dual-wield config

### Step 5: Commit build callback changes

```bash
git add callbacks/build_callbacks.py
git commit -m "feat: include dual-wield settings in build duplication

- Add dual-wield states to duplication callback
- Ensures duplicated builds preserve dual-wield configuration"
```

---

## Task 10: Update Integration Tests

**Files:**
- Modify: `tests/integration/test_full_simulation.py`

### Step 1: Update test_simulation_with_dual_wield

Find the test and update to use new approach:

```python
def test_simulation_with_dual_wield():
    """Test simulation with dual-wield configuration"""
    cfg = Config()
    cfg.AB_PROG = "5APR Classic"  # Changed from "5APR & Dual-Wield"
    cfg.DUAL_WIELD = True
    cfg.TWO_WEAPON_FIGHTING = True
    cfg.AMBIDEXTERITY = True
    cfg.IMPROVED_TWF = True
    cfg.TOON_SIZE = 'M'
    # ... rest of test
```

### Step 2: Add new dual-wield configuration tests

Add new test for feat combinations:

```python
def test_simulation_dual_wield_no_feats():
    """Test dual-wield with no feats produces higher penalties"""
    cfg = Config()
    cfg.AB_PROG = "5APR Classic"
    cfg.DUAL_WIELD = True
    cfg.TWO_WEAPON_FIGHTING = False
    cfg.AMBIDEXTERITY = False
    cfg.IMPROVED_TWF = False
    cfg.TOON_SIZE = 'M'

    weapon = Weapon("Spear_Riftmaker", cfg)
    results = run_full_simulation(cfg, weapon)

    # Should have lower DPS due to -6/-10 penalties and only 1 off-hand attack
    assert results['avg_dpr'] > 0  # But still produces damage
```

### Step 3: Run integration tests

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/integration/test_full_simulation.py -v`

Expected: All tests PASS

### Step 4: Commit integration test updates

```bash
git add tests/integration/test_full_simulation.py
git commit -m "test: update integration tests for new dual-wield approach

- Replace old progression-based dual-wield with config flags
- Add test for dual-wield without feats
- Verify all integration tests pass with new logic"
```

---

## Task 11: Run Full Test Suite

**Files:**
- N/A (verification step)

### Step 1: Run complete test suite

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/ -v`

Expected: All 426+ tests PASS

### Step 2: If any tests fail, debug and fix

Identify failing tests and update them to use new dual-wield approach.

### Step 3: Run tests again after fixes

Run: `cd .worktrees/dual-wield-granularity && python -m pytest tests/ -v`

Expected: All tests PASS

### Step 4: Commit any final test fixes

```bash
git add tests/
git commit -m "test: fix remaining tests for dual-wield refactor

- Update all dual-wield references to use config flags
- Ensure complete test coverage for new dual-wield system"
```

---

## Task 12: Manual Testing & Validation

**Files:**
- N/A (manual testing)

### Step 1: Start application

Run: `cd .worktrees/dual-wield-granularity && python app.py`

### Step 2: Test UI interactions

1. **Dual-wield toggle**: Verify show/hide works
2. **Feat combinations**: Try all 8 combinations (2^3)
3. **Character sizes**: Test S/M/L with different weapons
4. **Invalid configs**: Try Small + Medium weapon (should show error in results)
5. **Persistence**: Reload page, verify settings persist
6. **Reset**: Verify reset button works

### Step 3: Test progression accuracy

Manually verify attack progressions match expected values:
- No DW: Simple progression with markers converted
- DW with all feats + light weapon: -2/-2 penalties
- DW no feats + heavy weapon: -6/-10 penalties

### Step 4: Document any issues

Create checklist of validation results.

### Step 5: Final verification commit

```bash
git add -A
git commit -m "chore: manual testing validation complete

All UI interactions tested:
- Dual-wield toggle show/hide: ✓
- All 8 feat combinations: ✓
- Character size variations: ✓
- Invalid config handling: ✓
- UI persistence: ✓
- Reset functionality: ✓"
```

---

## Success Criteria Checklist

After completing all tasks, verify:

- [ ] AB_PROGRESSIONS reduced from 24 to 15 entries
- [ ] Dual-wield master toggle shows/hides sub-widgets
- [ ] All 8 feat combinations produce correct penalties
- [ ] Illegal configurations return zeroed results
- [ ] Off-hand attacks: 1 without Improved TWF, 2 with it
- [ ] Special attacks maintain 0, -5, -10 offsets
- [ ] All 426+ tests pass
- [ ] New dual-wield tests cover helper methods and integrations
- [ ] UI persistence works correctly
- [ ] Reset to defaults works
- [ ] Build duplication copies dual-wield settings

---

## Post-Implementation

After all tasks complete and tests pass:

1. Run final full test suite
2. Create summary commit if needed
3. Use @superpowers:finishing-a-development-branch to decide next steps (merge, PR, etc.)
