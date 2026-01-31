# Dual-Wielding Granularity Enhancement - Design Document

**Date:** 2026-01-31
**Author:** Design Session with User
**Status:** Ready for Implementation

## Overview

Expand the simulator's dual-wielding system to provide granular feat-based control. Currently, dual-wield configurations are hardcoded into AB progression options (e.g., "5APR & Dual-Wield"). This design separates dual-wield into a toggleable feature with individual feat controls.

## Goals

1. **Separate Concerns**: Remove dual-wield from AB progression names
2. **Granular Control**: Allow users to toggle individual dual-wield feats
3. **Accurate Penalties**: Calculate separate penalties for primary and off-hand attacks based on feat selection
4. **Maintainability**: Reduce AB_PROGRESSIONS dictionary from 24 to 15 entries

## UI Changes

### Character Settings Component

**Removed from AB Progressions:**
- All 12 dual-wield variants (e.g., "4APR & Dual-Wield", "5APR & Dual-Wield & B.Speed")
- Keep only 15 base progressions

**New Collapsible Section (after AB Progression dropdown):**

1. **Master Toggle**: Dual-Wield (default: OFF)
   - Component: `dbc.Switch` with id `'dual-wield-switch'`
   - When OFF: hides all sub-widgets

2. **Dual-Wield Settings** (shown only when master toggle is ON):
   - **Character Size** dropdown (moved from current location)
     - Purpose: Determines weapon "light" status for penalty calculation
     - Only relevant when dual-wielding

   - **Two-Weapon Fighting** switch (default: ON)
     - Reduces penalties from -6/-10 to -4/-8 (primary/off-hand)

   - **Ambidexterity** switch (default: ON)
     - Reduces off-hand penalty by 4

   - **Improved Two-Weapon Fighting** switch (default: ON)
     - Grants second off-hand attack at -5 penalty

### Widget Structure

```python
# Pattern-matching IDs for show/hide control
{'type': 'dw-row', 'name': 'character-size'}
{'type': 'dw-row', 'name': 'two-weapon-fighting'}
{'type': 'dw-row', 'name': 'ambidexterity'}
{'type': 'dw-row', 'name': 'improved-twf'}
```

## Data Model Changes

### Config.py

**New Fields:**

```python
# DUAL-WIELD SETTINGS
DUAL_WIELD: bool = False
TWO_WEAPON_FIGHTING: bool = True
AMBIDEXTERITY: bool = True
IMPROVED_TWF: bool = True
```

**Updated AB_PROGRESSIONS:**

Add string markers for special attacks that don't receive dual-wield penalties:
- `"hasted"` - Haste attack (offset: 0)
- `"flurry"` - Flurry of Blows (offset: -5 from first special)
- `"bspeed"` - Blinding Speed (offset: -5 or -10 depending on position)
- `"rapid"` - Rapid Shot (offset: -5 from first special)
- `"shifter"` - Shifter extra attack (offset: -5 from first special)

**Example progressions with markers:**

```python
AB_PROGRESSIONS: Dict[str, List[Union[int, str]]] = field(default_factory=lambda: {
    "4APR Classic":                     [0, -5, -10, "hasted"],
    "4APR & Blinding Speed":            [0, -5, -10, "hasted", "bspeed"],
    "5APR Classic":                     [0, -5, -10, -15, "hasted"],
    "5APR & R.Shot & B.Speed":          [0, -5, -10, -15, "hasted", "rapid", "bspeed"],
    "Monk 6APR & Flurry":               [0, -3, -6, -9, -12, "hasted", "flurry"],
    "Monk 7APR & Flurry & B.Speed":     [0, -3, -6, -9, -12, -15, "hasted", "flurry", "bspeed"],
    # ... 15 total progressions
})
```

**Special Attack Offset Rule:**
- 1st special attack (usually "hasted"): offset 0
- 2nd special attack: offset -5
- 3rd special attack: offset -10

## Core Logic Changes (attack_simulator.py)

### Dual-Wield Penalty Calculation

**Penalty Table:**

| TWF | Ambidexterity | Light Weapon | Primary | Off-hand |
|-----|---------------|--------------|---------|----------|
| No  | No            | No           | -6      | -10      |
| No  | Yes           | No           | -6      | -6       |
| No  | No            | Yes          | -4      | -8       |
| No  | Yes           | Yes          | -4      | -4       |
| Yes | No            | No           | -4      | -8       |
| Yes | Yes           | No           | -4      | -4       |
| Yes | No            | Yes          | -2      | -6       |
| Yes | Yes           | Yes          | -2      | -2       |

**Calculation Formula:**

```python
primary_penalty = -6
offhand_penalty = -10

if TWO_WEAPON_FIGHTING:
    primary_penalty += 2
    offhand_penalty += 2

if AMBIDEXTERITY:
    offhand_penalty += 4

if is_weapon_light():
    primary_penalty += 2
    offhand_penalty += 2
```

### Light Weapon Determination

**Valid Dual-Wield Configurations:**

| Character Size | Valid Weapon Sizes | Notes |
|----------------|-------------------|-------|
| Medium         | M, S, T, Double-sided | Double-sided are Large but allowed |
| Small          | S, T | Cannot wield Medium or larger |
| Large          | M, S | Cannot wield Tiny (too small) |

**Light Weapon (gets +2 penalty reduction):**
- Large character + Medium/Small weapon
- Medium character + Small/Tiny weapon OR Double-sided weapon
- Small character + Tiny weapon

### New Methods

**1. `_is_valid_dw_config()` - Validation**

```python
def _is_valid_dw_config(self):
    """Check if dual-wielding is valid for character/weapon size combination"""
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

**2. `_is_weapon_light()` - Light Weapon Check**

```python
def _is_weapon_light(self):
    """Determine if weapon counts as 'light' for dual-wielding"""
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

**3. `calculate_dw_penalties()` - Penalty Calculation**

```python
def calculate_dw_penalties(self):
    """Calculate primary and off-hand penalties based on feats and weapon size"""
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

**4. `_build_simple_progression()` - Non-Dual-Wield Mode**

```python
def _build_simple_progression(self, attack_prog_offsets):
    """Build attack progression when dual-wield is disabled"""
    attack_prog = []
    special_attack_count = 0

    for offset in attack_prog_offsets:
        if isinstance(offset, str):
            # Special attacks: 0, -5, -10 progression
            special_offset = special_attack_count * -5
            attack_prog.append(self.ab + special_offset)
            special_attack_count += 1
        else:
            # Regular integer offset
            attack_prog.append(self.ab + offset)

    return attack_prog
```

**5. `_build_dw_progression()` - Dual-Wield Mode**

```python
def _build_dw_progression(self, attack_prog_offsets, primary_penalty, offhand_penalty):
    """Build attack progression when dual-wield is enabled"""
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

**6. `get_attack_progression()` - Refactored Main Method**

```python
def get_attack_progression(self):
    """Determine the attack progression (list of AB)"""
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

## Callback Changes

### New Callback: Show/Hide Dual-Wield Section

**File:** `callbacks/ui_callbacks.py`

```python
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

### Updated Callbacks

**1. Config Update Callback** (`callbacks/core_callbacks.py`)

Add inputs:
```python
Input('dual-wield-switch', 'value'),
Input('two-weapon-fighting-switch', 'value'),
Input('ambidexterity-switch', 'value'),
Input('improved-twf-switch', 'value'),
```

Add config updates:
```python
cfg.DUAL_WIELD = dual_wield
cfg.TWO_WEAPON_FIGHTING = two_weapon_fighting
cfg.AMBIDEXTERITY = ambidexterity
cfg.IMPROVED_TWF = improved_twf
```

**2. Reset to Defaults Callback** (`callbacks/build_callbacks.py` or similar)

Add outputs:
```python
Output('dual-wield-switch', 'value'),
Output('two-weapon-fighting-switch', 'value'),
Output('ambidexterity-switch', 'value'),
Output('improved-twf-switch', 'value'),
```

Add return values:
```python
False,  # DUAL_WIELD
True,   # TWO_WEAPON_FIGHTING
True,   # AMBIDEXTERITY
True,   # IMPROVED_TWF
```

**3. Build Duplication Callback**

Add states to capture current dual-wield settings:
```python
State('dual-wield-switch', 'value'),
State('two-weapon-fighting-switch', 'value'),
State('ambidexterity-switch', 'value'),
State('improved-twf-switch', 'value'),
```

Include in duplicated build outputs.

## Testing Strategy

### Tests to Update

**File:** `tests/simulator/test_attack_simulator.py`

1. **Update Existing Dual-Wield Tests:**
   - Replace AB progression selection (e.g., "5APR & Dual-Wield") with base progression + DUAL_WIELD flag

2. **New Tests to Add:**

```python
def test_dual_wield_penalty_combinations():
    """Test all 8 feat combinations produce correct penalties"""
    # Test matrix of TWF x Ambi x Light (2^3 = 8 cases)

def test_dual_wield_illegal_configs():
    """Test illegal configurations are caught"""
    # Large weapon, Small+Medium, Large+Tiny

def test_dual_wield_off_hand_attacks():
    """Test off-hand attack count based on Improved TWF"""
    # With Improved TWF: 2 off-hand attacks
    # Without: 1 off-hand attack

def test_special_attacks_no_penalty():
    """Test that hasted/flurry/bspeed don't get DW penalties"""
    # Verify special attacks maintain 0, -5, -10 offsets

def test_light_weapon_determination():
    """Test weapon is correctly identified as light/normal"""
    # Test all size combinations
    # Test double-sided special case
```

## Edge Cases

1. **Weapon changes while dual-wield enabled:**
   - Switching from valid to invalid weapon triggers illegal config handling
   - Handled by existing recalculation logic

2. **Character size changes while dual-wield enabled:**
   - Same as above - handled by recalculation

3. **Invalid dual-wield configuration:**
   - Returns zeroed attack progression
   - Sets `illegal_dual_wield_config = True`
   - Existing output display shows error message to user

## Implementation Order

1. **`simulator/config.py`** - Data model foundation
2. **`simulator/attack_simulator.py`** - Core logic refactoring
3. **`components/character_settings.py`** - UI components
4. **`callbacks/ui_callbacks.py`** - Show/hide callback
5. **`callbacks/core_callbacks.py`** - Config update callback
6. **`callbacks/build_callbacks.py`** - Reset and duplication callbacks
7. **`tests/simulator/test_attack_simulator.py`** - Test updates

## Files Modified Summary

| File | Changes |
|------|---------|
| `simulator/config.py` | Add 4 new fields, update AB_PROGRESSIONS (remove 12, add markers to 15) |
| `simulator/attack_simulator.py` | Add 6 new methods, refactor `get_attack_progression()` |
| `components/character_settings.py` | Move Character Size, add dual-wield section with 4 widgets |
| `callbacks/ui_callbacks.py` | Add show/hide callback |
| `callbacks/core_callbacks.py` | Add 4 inputs, update config fields |
| `callbacks/build_callbacks.py` | Add 4 outputs to reset, add 4 states to duplication |
| `tests/simulator/test_attack_simulator.py` | Update existing tests, add 5+ new tests |

## Success Criteria

- [ ] AB_PROGRESSIONS reduced from 24 to 15 entries
- [ ] Dual-wield master toggle works (shows/hides sub-widgets)
- [ ] All 8 feat combinations produce correct penalties
- [ ] Illegal configurations return zeroed results
- [ ] Off-hand attacks count correct (1 or 2 based on Improved TWF)
- [ ] Special attacks (hasted, flurry, bspeed) maintain correct offsets
- [ ] All existing tests pass
- [ ] New dual-wield tests pass
- [ ] UI persistence works (session storage)
- [ ] Reset to defaults works
- [ ] Build duplication copies dual-wield settings
