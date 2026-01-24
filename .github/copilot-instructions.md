# Copilot Instructions for adoh-dps-simulator Repository

## Repository Overview

**ADOH DPS Simulator** is a web-based simulator for calculating damage-per-second (DPS) metrics for ADOH (A Dawn of Heroes), a famous action-oriented Neverwinter Nights server. It simulates attack sequences, weapon damage, critical hits, and various character buffs/feats to provide comprehensive damage analysis.

- **Type:** Python web application (Dash/Flask-based UI with Python simulation engine)
- **Size:** Medium (~50 core Python files, ~1500 LOC)
- **Primary Language:** Python 3.12.3
- **Main Frameworks:** Dash, Plotly, Pandas, NumPy
- **Target Runtime:** Python 3.12+ (gunicorn for production)

## Project Structure

### Core Architecture

```
project_root/
├── app.py                 # Main Dash application entry point; initializes layout and callbacks
├── weapons_db.py          # Weapon property database (damage, threat ranges, multipliers)
├── simulator/             # Core DPS simulation logic
│   ├── config.py          # Config dataclass with all simulation parameters
│   ├── weapon.py          # Weapon class; calculates damage aggregation and modifiers
│   ├── attack_simulator.py # AttackSimulator class; simulates d20 rolls, hits, crits, damage
│   ├── damage_simulator.py # DamageSimulator class; orchestrates full damage simulation
│   ├── legend_effect.py    # LegendEffect class; handles legendary weapon proc effects
│   └── stats_collector.py  # StatsCollector class; collects simulation statistics
├── components/            # Dash UI components (modular page sections)
│   ├── navbar.py
│   ├── character_settings.py
│   ├── additional_damage.py
│   ├── simulation_settings.py
│   ├── results_tab.py
│   ├── reference_tab.py
│   ├── plots.py
│   ├── progress_modal.py
│   └── __pycache__/
├── callbacks/             # Dash callback handlers (input/output logic)
│   ├── core_callbacks.py   # Main simulation trigger and result handling
│   ├── ui_callbacks.py     # UI state and interaction handling
│   ├── plots_callbacks.py  # Chart generation callbacks
│   ├── validation_callbacks.py  # Input validation
│   └── __pycache__/
├── tests/                 # Pytest unit test suite
│   ├── test_weapon.py     # tests covering Weapon class
│   ├── test_attack_simulator.py # tests covering AttackSimulator class
│   ├── README.md          # Test documentation
│   └── __pycache__/
├── scripts/               # Utility scripts (not tracked, used for analysis)
├── assets/                # Static assets (favicon, CSS)
├── cache/                 # Diskcache directory (auto-created, .gitignore'd)
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku deployment configuration
└── .gitignore            # Excludes cache/, scripts/, __pycache__/, .idea/
```

### Key Files and Their Purposes

- **simulator/config.py**: Central configuration using dataclasses. Contains all user-configurable parameters (target AC, immunities, character AB, weapon selection, simulation rounds, etc.). Changes here affect entire simulator behavior.
- **simulator/weapon.py**: Loads weapon properties, calculates threat ranges, critical multipliers, enhancement bonuses, and strength bonuses. Aggregates all damage sources.
- **simulator/attack_simulator.py**: D20 mechanics engine. Simulates hit rolls, critical hits, threat rolls, and individual damage rolls. Most complex calculation logic lives here.
- **simulator/damage_simulator.py**: Orchestrates full damage simulation. Runs multiple attack rounds and tracks convergence (uses rolling statistics to determine when simulation has stabilized).
- **app.py**: Single-page Dash application. Initializes the UI layout with Bootstrap dark theme and registers all callbacks. Uses diskcache for background job state management.
- **tests/**: Comprehensive unit test suite. Tests are modular organized by class/feature.

## Build and Run Instructions

### Prerequisites

- **Python 3.12+** (verified on Python 3.12.3)
- **pip** package manager
- **Windows PowerShell** or equivalent terminal

### Environment Setup (Must Always Do This First)

```powershell
# Install dependencies (required every time requirements.txt changes)
pip install -r requirements.txt

# Install pytest for running tests (if not already installed)
pip install pytest
```

**Why this matters:** The diskcache and gunicorn packages are optional dependencies in requirements.txt. Always run pip install to ensure all packages are present, including:
- dash, dash-bootstrap-components, plotly (UI)
- numpy, pandas (data processing)
- dash[diskcache] (background jobs)
- gunicorn (production server)

### Running the Application

```powershell
# Start the development server
python app.py
```

- Server starts on `http://127.0.0.1:8050` (Dash default)
- Debug mode is enabled in app.py (debug=True)
- Press Ctrl+C to stop

**Expected behavior:**
- Application initializes successfully and displays a Dash startup message
- No errors about missing modules or import failures
- Web UI is accessible at the localhost address

### Running Tests

```powershell
# Run all tests with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_weapon.py -v

# Run specific test class
pytest tests/test_weapon.py::TestWeaponInitialization -v

# Run with coverage (if pytest-cov installed)
pytest tests/ --cov=simulator --cov=components --cov=callbacks
```

**Important:** Always run `pytest tests/ -v` after making changes to the simulator or weapon logic to ensure no regressions. Tests must pass before submitting a PR.

## Development Workflow

### Making Changes

1. **For simulator changes (weapon.py, attack_simulator.py, damage_simulator.py):**
   - Make your changes
   - Run `pytest tests/ -v` to validate
   - Check for any test failures
   - If tests fail, fix the logic or update tests if the change is intentional

2. **For UI/callback changes (components/*, callbacks/*):**
   - Changes don't require tests (UI testing phase is Phase 2)
   - Verify UI loads correctly with `python app.py`
   - Test user interactions manually

3. **For configuration changes (simulator/config.py):**
   - Config is a dataclass with extensive default parameters
   - Changes here affect all simulations
   - Run full test suite afterward

### Common Development Tasks

**Adding a new weapon:**
1. Edit `weapons_db.py` and add entry to `WEAPON_PROPERTIES` dict
2. Format: `'Weapon Name': {'dmg': [dice, sides, 'damage_type'], 'threat': 20, 'multiplier': 3, 'size': 'L'}`
3. Add corresponding entry to `PURPLE_WEAPONS` if applicable
4. Test with new weapon in web UI or add to test_weapon.py

**Adding a new configuration parameter:**
1. Add field to `Config` dataclass in `simulator/config.py`
2. Provide sensible default value
3. Update any affected callback/component if needed
4. Add corresponding test if it affects calculations

**Adding a new feature (e.g., damage type):**
1. Modify weapon damage representation in `simulator/weapon.py`
2. Update `simulator/attack_simulator.py` to handle new feature in damage calculations
3. Add tests to cover edge cases
4. Run `pytest tests/ -v` to verify

## Architecture Notes

### Data Flow

1. User configures parameters in UI components (character_settings, simulation_settings, etc.)
2. User clicks "Simulate" button
3. core_callbacks.py triggers DamageSimulator with configuration
4. DamageSimulator orchestrates: Weapon → AttackSimulator → LegendEffect → StatsCollector
5. Results stored in dcc.Store (session storage)
6. results_tab.py and plots.py components render the results

### Key Design Patterns

- **Config-driven:** All parameters centralized in Config dataclass
- **Composition over inheritance:** Simulator classes composed with dependencies injected
- **Modular callbacks:** Each callback module registers independently (ui_, core_, plots_, validation_)
- **Background jobs:** Complex simulations run in background with diskcache state management
- **Component-based UI:** Dash components built as reusable functions in components/

### Important Implementation Details

- **Threat ranges:** Calculated as minimum roll on d20 needed to threaten a critical hit (e.g., 18-20 threat range = threat value of 18)
- **Dual-wield penalties:** Size-based matrix stored in config, varies by weapon size combinations
- **Damage immunity:** Reduces damage by percentage based on config flags
- **Legendary effects:** Proc chances calculated per attack; effects applied in damage calculation phase
- **Convergence:** Simulation runs until rolling 15-round window stabilizes (STD_THRESHOLD check)
- **Crit exemption:** Simulations track both crit-allowed and crit-immune DPS separately

## Validation and CI/CD

### No Automated CI/CD Currently Configured

This repository does not have GitHub Actions workflows (.github/workflows/) set up. However, you should:

1. **Always run tests locally** before committing:
   ```powershell
   pytest tests/ -v
   ```

2. **Verify the app starts** before committing:
   ```powershell
   # Start in background, let it run for a few seconds, then Ctrl+C
   python app.py
   ```

3. **Check for import errors** by running:
   ```powershell
   python -c "import app; print('All imports successful')"
   ```

### Suggested Validation Steps for Code Changes

After making changes, execute this sequence:

```powershell
# 1. Verify imports and basic syntax
python -c "import simulator.config; import simulator.weapon; print('Imports OK')"

# 2. Run full test suite
pytest tests/ -v

# 3. Test application startup
python app.py  # (Ctrl+C to stop)
```

## Dependencies

### Core Requirements (from requirements.txt)

| Package                   | Version | Purpose                         |
|---------------------------|---------|---------------------------------|
| dash                      | latest  | Web framework and UI            |
| dash-bootstrap-components | latest  | Bootstrap theming               |
| plotly                    | latest  | Chart generation                |
| numpy                     | latest  | Numerical calculations          |
| pandas                    | latest  | Data processing                 |
| dash[diskcache]           | latest  | Background job state management |
| gunicorn                  | latest  | Production WSGI server          |

### Development Requirements

| Package | Version | Purpose                |
|---------|---------|------------------------|
| pytest  | 9.0.1+  | Unit testing framework |

Install dev requirements with:
```powershell
pip install pytest
```

## Adding New Features - Proven Pattern

### Recent Feature Implementations (December 2025)

Two major critical hit features were successfully added using a consistent pattern:

1. **Overwhelming Critical** - Adds physical damage bonus on crits (1d6/2d6/3d6 based on crit multiplier)
2. **Devastating Critical** - Adds pure damage bonus on crits (10/20/30 based on weapon size)

Both features passed 100% of tests (283/283 total, with 27 new tests added).

### Step-by-Step Feature Implementation Pattern

#### Step 1: Add Configuration Parameter
1. Add boolean parameter to `Config` dataclass in `simulator/config.py`
2. Place it logically near related parameters (e.g., after similar features)
3. Provide sensible default value (usually `False` for new features to maintain backward compatibility)
4. Use descriptive names in UPPERCASE_WITH_UNDERSCORES format

**Example:**
```python
OVERWHELM_CRIT: bool = False  # New physical damage on crits
DEV_CRIT: bool = False        # New pure damage on crits
```

#### Step 2: Add UI Component
1. Create toggle switch in appropriate `components/*.py` file (usually `character_settings.py`)
2. Use `dbc.Switch` component with:
   - Unique component ID (kebab-case, e.g., `dev-crit-switch`)
   - Clear, user-friendly label
   - Tooltip with explanation of what the feature does
   - Persistence enabled for user preferences
3. Place UI component logically near related features
4. Match component value to config parameter

**Example:**
```python
dbc.Switch(
    id='dev-crit-switch',
    label='Devastating Critical',
    value=cfg.DEV_CRIT,
    persistence=True,
    persistence_type=persist_type,
)
dbc.Tooltip(
    "On critical hit, adds pure damage based on weapon size: Tiny/Small +10, Medium +20, Large +30.",
    target='dev-crit-switch',
    placement='left',
    delay={'show': 500},
)
```

#### Step 3: Wire Up Callbacks
**In core_callbacks.py:**
1. Add `State` input for your new switch component
2. Add parameter to `run_calculation` function signature
3. Add config assignment line to update the configuration dict

**In ui_callbacks.py:**
1. Add `Output` for your switch in the reset callback
2. Add return value using `default_cfg.YOUR_PARAMETER`

**Pattern:**
```python
# In states list
State('dev-crit-switch', 'value'),

# In function signature
def run_calculation(..., dev_crit, ...):

# In config assignment
current_cfg['DEV_CRIT'] = dev_crit

# In reset callback output
Output('dev-crit-switch', 'value', allow_duplicate=True),

# In reset return values
default_cfg.DEV_CRIT,
```

#### Step 4: Implement Backend Logic
1. Add logic to `simulator/damage_simulator.py` in the appropriate location
2. Keep logic close to related features (e.g., both crit bonuses together)
3. Check the feature flag: `if self.cfg.FEATURE_NAME:`
4. Implement the calculation logic cleanly and documented
5. Add damage to appropriate type in `dmg_dict` dictionary

**Key Pattern for Critical Hit Bonuses:**
- Only apply on critical hits: `if crit_multiplier > 1:`
- Add to correct damage type: `dmg_dict.setdefault('damage_type', []).append(damage_value)`
- Use flat damage format: `[0, 0, amount]` for flat bonuses
- Use dice format: `[num_dice, num_sides]` for rolled damage

**Example:**
```python
if crit_multiplier > 1:
    if self.cfg.DEV_CRIT:
        if self.weapon.size in ['T', 'S']:
            dev_dmg = [0, 0, 10]
        elif self.weapon.size == 'M':
            dev_dmg = [0, 0, 20]
        else:
            dev_dmg = [0, 0, 30]
        dmg_dict.setdefault('pure', []).append(dev_dmg)
```

#### Step 5: Write Comprehensive Tests
1. Create new test class in `tests/test_damage_simulator.py` (or appropriate test file)
2. Test at least these scenarios:
   - Feature disabled by default
   - Feature can be enabled
   - Feature produces expected behavior when enabled
   - Feature produces no bonus when disabled
   - Feature works with related feats/features
   - Feature works with different weapon types
   - Feature only applies when expected (e.g., only on crits)
   - Feature produces correct damage type
3. Aim for 10-15 tests per feature for comprehensive coverage

**Testing Template:**
```python
class TestNewFeature:
    def test_feature_disabled_by_default(self):
        cfg = Config()
        assert cfg.NEW_FEATURE is False

    def test_feature_can_be_enabled(self):
        cfg = Config(NEW_FEATURE=True)
        assert cfg.NEW_FEATURE is True

    def test_feature_produces_expected_behavior(self):
        cfg = Config(NEW_FEATURE=True, AB=100, TARGET_AC=10, ROUNDS=50)
        simulator = DamageSimulator("Scimitar", cfg)
        with patch('builtins.print'):
            result = simulator.simulate_dps()
        assert result['dps_crits'] > 0
```

### Critical Implementation Details Learned

#### 1. **Backward Compatibility is Essential**
- Always default new features to `False` (disabled)
- Never change default behavior of existing features
- All existing tests must continue to pass
- Run full test suite after changes: `pytest tests/ -v`

#### 2. **UI Component Ordering Matters**
- Place new features logically near related features
- For critical hit features: "Keen" → "Improved Critical" → "Overwhelm Critical" → "Devastating Critical"
- This improves UX and makes sense thematically

#### 3. **Weapon Properties Are Accessible**
- Access weapon size via: `self.weapon.size` (returns 'T', 'S', 'M', 'L')
- Access crit multiplier via: `self.weapon.crit_multiplier`
- Access crit threat via: `self.weapon.crit_threat`
- These are set during Weapon initialization

#### 4. **Critical-Only Bonuses Require Gate Check**
- Always check: `if crit_multiplier > 1:` to ensure bonus only applies on crits
- This is the standard pattern for critical hit features
- Place within this gate to automatically benefit from crit-only behavior

#### 5. **Damage Dictionary Structure**
- Format: `dmg_dict[damage_type] = [[dice, sides], [dice, sides, flat], ...]`
- Can use `.setdefault()` to safely add new damage types
- Use `.append()` to add multiple entries of same type
- Damage is processed/rolled in `get_damage_results()` method

#### 6. **Test Strategy for Complex Features**
- Test default state first (simplest test)
- Test enable/disable functionality
- Test with each variant (e.g., all weapon sizes)
- Test integration with other features
- Test edge cases (multiple attacks, feat combinations)
- Compare enabled vs disabled for behavior verification
- Aim for 70% of test time on integration tests, 30% on unit tests

#### 7. **Documentation is Part of Implementation**
- Create 1-2 documentation files per feature explaining:
  - Feature specification and mechanics
  - Implementation approach
  - Testing coverage
  - User guide with examples
- This helps future maintainers understand intent and design

### Testing a New Feature Before Commit

```powershell
# 1. Run new feature's tests specifically
pytest tests/test_damage_simulator.py::TestNewFeature -v

# 2. Run all tests to check for regressions
pytest tests/ -v

# 3. Verify app still starts
python app.py  # (Ctrl+C after startup confirmation)

# 4. Check imports work
python -c "from simulator.config import Config; cfg = Config(); print('OK')"
```

### Common Pitfalls to Avoid

1. **Forgetting to update reset callback** - New UI switches won't reset properly
2. **Missing state in core_callbacks** - New switch won't connect to backend
3. **Not checking feature flag** - Bonus applies even when feature disabled
4. **Wrong damage type** - Bonus doesn't apply or applies incorrectly
5. **No tests for new features** - Regressions go undetected
6. **Breaking existing tests** - Changes affect unexpected parts of system
7. **Inconsistent naming** - Config param, UI ID, and callback param names don't align

### Example: Complete Feature Checklist

Before considering a feature "done":

- [ ] Config parameter added to `simulator/config.py`
- [ ] UI component added to `components/character_settings.py`
- [ ] Component state added to core callback states list
- [ ] Function parameter added to `run_calculation` signature
- [ ] Config assignment added to config dict building
- [ ] Reset callback output added
- [ ] Reset callback return value added
- [ ] Backend logic added to `simulator/damage_simulator.py`
- [ ] Feature flag check implemented (`if self.cfg.FEATURE_NAME:`)
- [ ] Logic produces expected behavior
- [ ] Tests written
- [ ] All new tests passing
- [ ] All existing tests still passing (no regressions)
- [ ] Integration tests with related features
- [ ] Documentation created
- [ ] Code reviewed and formatted consistently

## Known Issues and Workarounds

None currently documented. If errors occur during:

- **Import errors on startup:** Ensure `pip install -r requirements.txt` was run successfully
- **Test failures:** Verify Python 3.12+ is installed and all tests passed in baseline (283 tests as of Dec 2025)
- **UI not rendering:** Confirm port 8050 is not in use; close other Dash apps
- **New feature doesn't show up:** Ensure UI component ID matches state ID in callbacks exactly (kebab-case)
- **New feature doesn't work:** Check feature flag is being read correctly with `print()` debugging in damage_simulator.py

## Trust This Document

When implementing changes:

1. **Always trust the build and test instructions above** — run them exactly as written
2. **Verify your changes with pytest** before committing
3. **Do NOT search the codebase if this document provides the answer** — it covers all necessary details for common tasks
4. **Only search if:** You need to understand a specific callback behavior, modify a complex calculation, or need details about a specific component's implementation

---

**Last Updated:** January 23, 2026  
**Python Version Tested:** 3.12.3  
**Test Suite Status:** 283/283 passing

