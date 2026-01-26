# Copilot Instructions - ADOH DPS Simulator

## What This Is
Web-based DPS calculator for ADOH (A Dawn of Heroes), a Neverwinter Nights server. Simulates attack rolls, weapon damage, crits, and character buffs using Python/Dash.

## Critical Setup
```powershell
pip install -r requirements.txt  # ALWAYS run this first
python app.py                     # Starts on localhost:8050
pytest tests/ -v                  # Run after any simulator changes
```

## Architecture at a Glance
- **simulator/**: Core calculation engine (config.py, weapon.py, attack_simulator.py, damage_simulator.py)
- **components/**: Modular Dash UI sections
- **callbacks/**: Input/output handlers (core_, ui_, plots_, validation_)
- **weapons_db.py**: Weapon property definitions
- **tests/**: Pytest suite (all tests must pass)

## Adding Features - Follow This Pattern

### 1. Config Parameter (`simulator/config.py`)
```python
NEW_FEATURE: bool = False  # Default False for backward compatibility
```

### 2. UI Component (`components/character_settings.py`)
```python
dbc.Switch(
    id='feature-switch',  # kebab-case
    label='Feature Name',
    value=cfg.NEW_FEATURE,
    persistence=True,
)
```

### 3. Wire Callbacks
**In `callbacks/core_callbacks.py`:**
```python
State('feature-switch', 'value'),              # Add to states list
def run_calculation(..., new_feature, ...):    # Add to signature
    current_cfg['NEW_FEATURE'] = new_feature   # Assign to config dict
```

**In `callbacks/ui_callbacks.py`:**
```python
Output('feature-switch', 'value', allow_duplicate=True),  # Add to reset outputs
default_cfg.NEW_FEATURE,                                   # Add to reset returns
```

### 4. Implement Logic (`simulator/damage_simulator.py`)
```python
if self.cfg.NEW_FEATURE:
    # Your calculation logic
    dmg_dict.setdefault('damage_type', []).append([dice, sides, flat])
```

### 5. Write Tests (`tests/test_damage_simulator.py`)
Test: default state, enable/disable, expected behavior, integration with other features, edge cases.

## Key Implementation Details

**Critical Hit Bonuses:**
- Only apply on crits: `if crit_multiplier > 1:`
- Flat damage: `[0, 0, flat_amount]`
- Dice damage: `[num_dice, num_sides]`
- Dice & flat damage: `[num_dice, num_sides, flat_amount]`

**Weapon Properties:**
- `self.weapon.size` → 'T', 'S', 'M', 'L'
- `self.weapon.crit_multiplier` → 2, 3, 4
- `self.weapon.crit_threat` → 18, 19, 20

**Damage Dictionary:**
- `dmg_dict[type] = [[dice, sides], [dice, sides, flat], ...]`
- `legendary` weapon properties: `dmg_dict['legendary'] = {'proc': percent_chance, 'dmg_type': [[dice, sides, flat], ...]}`
- `vs_race` weapon properties: `dmg_dict['vs_race_*'] = [[dice, sides, flat], ...]`

## Pre-Commit Checklist
- [ ] All tests pass: `pytest tests/ -v`
- [ ] App starts: `python app.py`
- [ ] No import errors
- [ ] Feature flag defaults to False
- [ ] UI component ID matches callback state ID
- [ ] Reset callback updated

## Common Pitfalls
- Forgetting to update reset callback (new switches won't reset)
- Missing state in core_callbacks (switch won't connect)
- Not checking feature flag (bonus applies when disabled)
- Breaking existing tests (283 must all pass)

## When to Search Codebase
Only when this document doesn't answer your question. This covers 95% of common tasks.
