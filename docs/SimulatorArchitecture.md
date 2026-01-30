# Simulator Architecture

## Overview

The ADOH DPS Simulator uses a modular, object-oriented architecture with clear separation of concerns. The simulator has been refactored to improve performance, maintainability, and extensibility.

## Core Components

### 1. Configuration (`simulator/config.py`)

**Purpose**: Centralized configuration management using dataclasses

**Key Features**:
- All simulation parameters in one place
- Serializable to/from JSON for Dash storage
- Type-safe with comprehensive type hints

**Usage**:
```python
cfg = Config()
cfg.AB = 70
cfg.KEEN = True
```

### 2. Weapon (`simulator/weapon.py`)

**Purpose**: Weapon property management and damage source aggregation

**Key Responsibilities**:
- Load base weapon properties from `weapons_db.py`
- Calculate critical hit threat range and multiplier
- Compute enhancement bonuses and strength modifiers
- Aggregate all damage sources into structured format

**Key Methods**:
- `get_crit_threat()`: Calculate threat range based on feats
- `enhancement_bonus()`: Compute weapon enhancement damage
- `strength_bonus()`: Calculate STR modifier damage
- `aggregate_damage_sources()`: Collect all damage sources

### 3. AttackSimulator (`simulator/attack_simulator.py`)

**Purpose**: Attack roll mechanics and hit chance calculations

**Key Responsibilities**:
- Build attack progression with dual-wield penalties
- Calculate theoretical hit/crit chances
- Perform attack and damage rolls
- Apply damage immunity/vulnerability

**Key Methods**:
- `get_attack_progression()`: Build AB progression list
- `calculate_hit_chances()`: Compute theoretical hit/crit rates
- `attack_roll()`: Simulate d20 attack roll
- `damage_roll()`: Simulate damage dice roll
- `damage_immunity_reduction()`: Apply target immunities

### 4. DamageSimulator (`simulator/damage_simulator.py`)

**Purpose**: Main simulation orchestration and DPS calculation

**Key Responsibilities**:
- Run multi-round combat simulation
- Track damage totals and convergence
- Handle critical hit multiplication
- Manage special damage cases (Tenacious Blow, Sneak Attack, etc.)

**Key Methods**:
- `simulate_dps()`: Main simulation loop
- `_setup_dual_wield_tracking()`: Initialize DW tracking
- `_calculate_final_statistics()`: Compute final DPS metrics
- `collect_damage_from_all_sources()`: Build damage dictionaries
- `get_damage_results()`: Roll damage and apply immunities
- `convergence()`: Check if simulation has converged

### 5. LegendEffect (`simulator/legend_effect.py`)

**Purpose**: Handle legendary weapon proc mechanics

**Key Responsibilities**:
- Determine if legendary effect triggers
- Calculate legendary damage
- Apply unique weapon effects (AB bonuses, AC reduction, immunity modifiers)
- Track legendary proc duration

**Key Methods**:
- `legend_proc()`: Roll for legendary effect trigger
- `get_legend_damage()`: Calculate legendary damage results
- `ab_bonus()`: Get AB bonus from active legendary effects
- `ac_reduction()`: Get AC reduction from active legendary effects

### 6. StatsCollector (`simulator/stats_collector.py`)

**Purpose**: Track simulation statistics

**Key Responsibilities**:
- Count attempts, hits, crits, legendary procs
- Calculate hit rates and crit rates per attack
- Compute percentages for results display

## Supporting Modules

### DamageRoll (`simulator/damage_roll.py`)

**Purpose**: Type-safe representation of damage rolls

Replaces legacy `[dice, sides, flat]` lists with a dataclass:

```python
@dataclass
class DamageRoll:
    dice: int
    sides: int
    flat: int = 0

    def average(self) -> float:
        return self.dice * ((1 + self.sides) / 2) + self.flat
```

**Benefits**:
- Clear, self-documenting code
- IDE autocomplete support
- Easier testing and validation

### Constants (`simulator/constants.py`)

**Purpose**: Centralize magic values and commonly used lists

Examples:
- `LEGEND_EFFECT_DURATION = 5`
- `DOUBLE_SIDED_WEAPONS = ['Dire Mace', 'Double Axe', 'Two-Bladed Sword']`
- `PHYSICAL_DAMAGE_TYPES = ['slashing', 'piercing', 'bludgeoning']`

**Benefits**:
- Single source of truth
- Easier maintenance
- No scattered magic numbers

### DamageSourceResolver (`simulator/damage_source_resolver.py`)

**Purpose**: Pure functions for damage calculations

Extracted helper functions:
- `calculate_avg_dmg()`: Compute average damage value
- `unpack_and_merge_vs_race()`: Handle vs_race damage conflicts
- `merge_enhancement_bonus()`: Merge enhancement with weapon damage

**Benefits**:
- Independently testable
- Reusable across modules
- No hidden state

### SimulatorFactory (`simulator/simulator_factory.py`)

**Purpose**: Create simulator instances with dependency injection

Allows injecting custom components for testing:

```python
factory = SimulatorFactory(cfg)
custom_stats = StatsCollector()
sim = factory.create_damage_simulator('Spear', stats_collector=custom_stats)
```

**Benefits**:
- Easier unit testing
- Flexible composition
- Decoupled instantiation

## Legendary Effects System

### Architecture

The legendary effects system uses a **registry pattern** to map weapons to their unique effect handlers.

**Components**:

1. **Base Interface** (`legendary_effects\base.py`):
   ```python
   class LegendaryEffect(ABC):
       @abstractmethod
       def apply(self, legend_dict, stats, crit_mult, attack_sim):
           pass
   ```

2. **Registry** (`legendary_effects\registry.py`):
   Maps weapon names to effect implementations

3. **Effect Implementations**:
   - `HeavyFlailEffect`: Adds physical damage to common pool
   - `CrushingBlowEffect`: Reduces target physical immunity

### Adding New Legendary Effects

To add a new legendary weapon effect:

1. Create new file in `simulator\legendary_effects\`:
   ```python
   from simulator.legendary_effects.base import LegendaryEffect

   class MyWeaponEffect(LegendaryEffect):
       def apply(self, legend_dict, stats, crit_mult, attack_sim):
           # Custom logic here
           return {
               'damage_sums': {...},
               'common_damage': [...],
               'immunity_factors': {...}
           }
   ```

2. Register in `registry.py`:
   ```python
   def _register_default_effects(self):
       # ...
       self.register('My_Weapon', MyWeaponEffect())
   ```

**No changes to core simulator code required!**

## Data Flow

### Initialization Flow

```
Config → Weapon → AttackSimulator → LegendEffect
                ↓
          DamageSimulator
```

1. Config loaded/created
2. Weapon loads properties from weapons_db
3. AttackSimulator calculates hit chances
4. LegendEffect initialized with references
5. DamageSimulator collects damage sources

### Simulation Flow

```
For each round:
  For each attack:
    Roll attack → Hit? → Roll damage → Apply immunities → Sum
                           ↓
                   Check for crit → Multiply dice rolls
                           ↓
                   Check for legend proc → Add legend damage
```

### Damage Aggregation Flow

```
Weapon.aggregate_damage_sources()
  ↓
  1. Base weapon damage
  2. Enhancement bonus (merged if conflict)
  3. Strength bonus
  4. Purple weapon damage (vs_race merged)
  5. Additional damage sources (feats/buffs)
  ↓
DamageSimulator.collect_damage_from_all_sources()
  ↓
  Organize into dmg_dict and dmg_dict_legend
  ↓
  Cache for performance (dmg_dict_base)
```

## Performance Optimizations

### 1. Damage Dictionary Caching

**Problem**: Deep copying damage dictionaries 60,000+ times per simulation

**Solution**: Pre-compute damage structures in `__init__`, use shallow copies in loop

**Impact**: 30-40% performance improvement

### 2. defaultdict for Accumulation

**Problem**: Repeated `pop()` + reassignment pattern

**Solution**: Use `defaultdict(int)` for damage sums

**Impact**: 5-10% performance improvement, cleaner code

### 3. Method Extraction

**Problem**: 245-line `simulate_dps()` method hard to optimize

**Solution**: Extract setup and statistics calculation to separate methods

**Impact**: Better profiling, easier to optimize specific parts

## Testing Strategy

### Unit Tests

Test individual components in isolation:
- `test_damage_roll.py`: DamageRoll dataclass
- `test_constants.py`: Constant values
- `test_weapon.py`: Weapon mechanics
- `test_attack_simulator.py`: Attack roll logic
- `test_damage_source_resolver.py`: Helper functions

### Integration Tests

Test complete simulation scenarios:
- `test_full_simulation.py`: End-to-end simulation
- Various configurations (dual-wield, feats, additional damage)
- Edge cases (illegal configs, convergence)

### Test-Driven Development

Follow TDD cycle:
1. Write failing test
2. Run test (verify failure)
3. Write minimal implementation
4. Run test (verify pass)
5. Commit

## Extension Points

### Adding New Game Mechanics

1. **New Feat/Buff**: Add to `Config.ADDITIONAL_DAMAGE`
2. **New Attack Progression**: Add to `Config.AB_PROGRESSIONS`
3. **New Weapon**: Add to `weapons_db.py` (no code changes)
4. **New Legendary Effect**: Create effect class + register
5. **New Damage Type**: Add to immunity system

### Future Enhancements

Potential improvements for future phases:

1. **Strategy Pattern for Damage Modifiers**: Each feat becomes a pluggable modifier
2. **Attack Progression Objects**: Replace string markers with dataclasses
3. **Batch Simulation**: Parallel weapon comparisons
4. **Damage Breakdown Visualization**: Pie charts by damage type
5. **Sensitivity Analysis**: AB/stat sweep tools

## File Organization

```
simulator/
├── config.py                    # Configuration dataclass
├── weapon.py                    # Weapon properties & damage
├── attack_simulator.py          # Attack rolls & hit chances
├── damage_simulator.py          # Main simulation engine
├── legend_effect.py             # Legendary proc mechanics
├── stats_collector.py           # Statistics tracking
├── damage_roll.py               # Type-safe damage representation
├── constants.py                 # Centralized constants
├── damage_source_resolver.py    # Pure helper functions
├── simulator_factory.py         # Dependency injection factory
└── legendary_effects/
    ├── __init__.py
    ├── base.py                  # Abstract base class
    ├── registry.py              # Effect registry
    ├── heavy_flail_effect.py    # Heavy Flail implementation
    └── crushing_blow_effect.py  # Crushing Blow implementation

tests/
├── simulator/
│   ├── test_damage_roll.py
│   ├── test_constants.py
│   ├── test_weapon.py
│   ├── test_attack_simulator.py
│   ├── test_damage_simulator.py
│   ├── test_damage_source_resolver.py
│   ├── test_simulator_factory.py
│   └── test_legendary_effects.py
└── integration/
    └── test_full_simulation.py
```

## Design Patterns Used

### 1. Strategy Pattern
**Where**: Legendary Effects System
**Why**: Allows adding new legendary weapon effects without modifying core simulator code

### 2. Registry Pattern
**Where**: LegendaryEffectRegistry
**Why**: Centralized mapping of weapons to their unique effect handlers

### 3. Factory Pattern
**Where**: SimulatorFactory
**Why**: Enables dependency injection for easier testing

### 4. Dataclass Pattern
**Where**: Config, DamageRoll
**Why**: Type-safe, immutable data structures with automatic methods

### 5. Single Responsibility Principle
**Where**: All modules
**Why**: Each class has one clear purpose (Config configures, Weapon manages properties, etc.)

## Maintenance Guide

### Adding a New Weapon

1. Add weapon to `weapons_db.py`:
   ```python
   STANDARD_WEAPONS['New_Weapon'] = {
       'type': 'longsword',
       'hands': 1,
       'size': 'M',
       # ... other properties
   }
   ```

2. If legendary, add to `PURPLE_WEAPONS`

3. If legendary with unique effect, create effect class and register

No simulator code changes needed!

### Modifying Simulation Logic

1. **Before making changes**: Run full test suite (`pytest tests/`)
2. **Make changes**: Follow TDD if adding functionality
3. **After changes**: Verify all 425 tests still pass
4. **Commit**: Use descriptive commit messages

### Performance Profiling

```python
import cProfile
import pstats

cfg = Config()
sim = DamageSimulator('Longsword', cfg)

profiler = cProfile.Profile()
profiler.enable()
results = sim.simulate_dps()
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

## Known Limitations

1. **Single Target**: Simulator only handles single-target DPS
2. **Turn-Based**: Doesn't model real-time combat timing
3. **Deterministic Immunities**: Target immunities don't change during simulation
4. **No Enemy Actions**: Target is passive (no attacks, spells, etc.)

These limitations are by design for the simulator's current scope.
