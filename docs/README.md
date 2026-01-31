# ADOH DPS Simulator - Documentation Index

**Last Updated:** January 31, 2026
**Repository:** adoh-dps-simulator
**Branch:** refactor/app-wide-refactoring (Post-Phase 3 Refactoring)
**Location:** `/docs/`

---

## Complete Documentation Suite

This directory contains comprehensive architecture and technical documentation for the ADOH DPS Simulator.

**📝 Recent Updates (Phase 1-3 Refactoring):** All documentation has been updated to reflect major architectural improvements including type-safe damage handling (`DamageRoll`), legendary effects registry system, performance optimizations (40% faster), and dependency injection support. See [Refactoring Documentation](#refactoring-documentation) section below.

### Quick Navigation

| Document                                | Purpose                                | Audience                      | Key Topics                                            |
|-----------------------------------------|----------------------------------------|-------------------------------|-------------------------------------------------------|
| [**Architecture.md**](#architecturemd)              | System-wide architecture overview      | All developers                | Project structure, component interactions, deployment |
| [**DamageCalculationDeepDive.md**](#damagecalculationdeepdivedmd) | In-depth damage calculation mechanics  | Core developers, contributors | Damage collection, aggregation, simulation, immunity  |
| [**DamageFlowDiagrams.md**](#damageflowdiagramsmd)        | Visual flow diagrams and code examples | Debugging, new features       | Process flows, decision trees, data structures        |
| [**RefactoringSummary.md**](#refactoring-documentation) *NEW*              | Complete refactoring overview          | All developers                | Performance improvements, new modules, migration guide |
| [**SimulatorArchitecture.md**](#refactoring-documentation) *NEW*           | Detailed simulator design              | Core developers               | Internal architecture, design patterns                |

---

## Architecture.md

### What's Inside

A complete overview of the ADOH DPS Simulator architecture, including:

- **System Architecture Diagram** - All layers from Dash UI to simulation engine
- **Component Interaction Flow** - User action → calculation → results
- **Deployment Architecture** - Development, testing, and production environments
- **Key Architectural Characteristics** - Config-driven design, modular callbacks, composition patterns
- **Component Types and Responsibilities** - Each class and its purpose
- **Technical Implementation Details** - D20 mechanics, convergence detection, dual-wield penalties
- **File Interaction Matrix** - Dependencies between all modules
- **Testing Architecture** - Test suite structure and coverage
- **Development Workflow** - How to add features and weapons

### When to Read This

- **First time learning the codebase** - Start here for high-level understanding
- **Planning a new feature** - Understand where it fits in the architecture
- **Debugging complex issues** - See how components interact
- **Onboarding new developers** - Essential reading for team members

### Key Sections

```
1. Project Overview (metrics, key technologies)
2. System Architecture (detailed component diagram)
3. Component Interaction Flow (sequence diagram of a calculation)
4. Deployment Architecture (dev/prod environments)
5. Key Architectural Characteristics (5 main design patterns)
6. Component Types and Responsibilities (simulator, UI, callback breakdown)
7. Technical Implementation Details (formulas, thresholds, matrices)
8. File Interaction Matrix (dependency overview)
9. Testing Architecture (test structure and coverage)
10. Development Workflow (feature and weapon addition guides)
```

---

## DamageCalculationDeepDive.md

### What's Inside

A comprehensive, step-by-step exploration of how damage flows through the system:

- **Overview & Philosophy** - Why damage is simulated, not averaged
- **Damage Collection Phase** - How all damage sources are gathered
  - Base weapon damage
  - Enhancement bonuses
  - Strength bonuses
  - Purple weapon bonuses
  - Additional damage sources
- **Damage Aggregation Architecture** - How sources combine into unified dictionaries
- **Damage Simulation Execution Flow** - The core simulation loop structure
- **Per-Hit Damage Calculation** - How individual hits are resolved
- **Critical Hit Mechanics** - How crits are rolled, not multiplied
- **Legendary Effect Integration** - Proc triggers and special effects
- **Immunity Application** - How target immunities reduce damage
- **Dual-Wield Special Cases** - Strength modifier for offhand weapons
- **Non-Stackable Damage Sources** - Why Sneak Attacks, Massive Critical, etc. don't stack
- **Statistical Tracking** - What metrics are collected and why
- **Complete Example Walkthrough** - Step-by-step trace of a real attack
- **Advanced Concepts** - Why simulation beats average-based calculation

### When to Read This

- **Understanding damage calculations** - Deep technical knowledge
- **Implementing new damage sources** - Where and how to add them
- **Fixing damage-related bugs** - Trace through the flow to find issues
- **Performance optimization** - Understanding computational bottlenecks
- **Validating simulator accuracy** - Verify against game mechanics

### Key Sections

```
1. Overview & Philosophy (simulation vs. averages)
2. Damage Collection Phase (5 sources)
3. Damage Aggregation Architecture (data structure building)
4. Damage Simulation Execution Flow (pseudo-code and Python)
5. Per-Hit Damage Calculation (get_damage_results method)
6. Critical Hit Mechanics (rolling vs. multiplying)
7. Legendary Effect Integration (procs, effects, immunity mods)
8. Immunity Application (reduction formulas)
9. Dual-Wield Special Cases (strength halving)
10. Non-Stackable Damage Sources (sneak, massive, flame weapon)
11. Statistical Tracking (StatsCollector overview)
12. Complete Example Walkthrough (full attack trace with numbers)
13. Advanced Concepts (why simulation is more accurate)
```

---

## DamageFlowDiagrams.md

### What's Inside

Visual flowcharts, Mermaid diagrams, and detailed code examples:

- **Complete Damage Flow Diagram** - End-to-end flow from click to results
- **Damage Collection Process** - Visual data structure building
- **Per-Attack Simulation Loop** - Pseudo-code and actual Python implementation
- **Critical Hit Decision Tree** - Graphical d20 mechanics
- **Immunity Application Flow** - Visual immunity calculation process
- **Non-Stackable Damage Logic** - Diagram of sneak/massive handling
- **Convergence Detection Algorithm** - Flowchart of stability checking
- **Code Execution Examples**
  - Simple hit with no crits
  - Critical hit with bane of enemies
  - Sneak attack (non-stackable)
- **Data Structure Examples**
  - dmg_dict at different stages
  - Complete data transformations table

### When to Read This

- **Visual learner** - Prefer diagrams to text
- **Debugging specific attack** - Trace through decision trees
- **Understanding data flow** - See transformations at each stage
- **Code review** - Reference actual implementation
- **Teaching/explaining** - Share diagrams with team members

### Key Diagrams

```
1. Complete Damage Flow (flowchart diagram)
2. Damage Collection Process (6-stage aggregation)
3. Per-Attack Simulation Loop (pseudo-code + Python)
4. Critical Hit Decision Tree (d20 roll logic)
5. Immunity Application Flow (reduction process)
6. Non-Stackable Damage Logic (extraction and re-add process)
7. Convergence Detection Algorithm (stability checking)
```

---

## Refactoring Documentation

### RefactoringSummary.md *NEW*

#### What's Inside

A comprehensive overview of the Phase 1-3 refactoring work:

- **Performance Improvements** - 40% faster simulations, 70% reduced memory allocations
- **Type Safety** - `DamageRoll` dataclass, comprehensive type hints
- **Code Organization** - Extracted helper functions, smaller methods
- **Extensibility** - Legendary effects registry, dependency injection
- **Testing** - Reorganized test structure, integration tests
- **Migration Guide** - How to work with new modules

#### When to Read This

- **Understanding recent changes** - What changed and why
- **Performance optimization** - How the 40% improvement was achieved
- **Adding legendary effects** - Registry-based extension pattern
- **Code maintenance** - New architectural patterns

### SimulatorArchitecture.md *NEW*

#### What's Inside

Detailed internal architecture of the simulator engine:

- **Component Design** - How simulator classes interact
- **Data Flow** - Internal data transformations
- **Design Patterns** - Factory, Registry, Dependency Injection
- **Extension Points** - Where and how to add new features

#### When to Read This

- **Deep architectural understanding** - Beyond surface-level docs
- **Major refactoring** - Understanding current design patterns
- **Advanced features** - Complex integrations

---

## How to Use These Documents

### **Adding a New Damage Source**
1. Understand current sources: [DamageCalculationDeepDive.md](#damagecalculationdeepdivedmd) → Section 2
2. See where it aggregates: [DamageCalculationDeepDive.md](#damagecalculationdeepdivedmd) → Section 3
3. Check for special handling: [DamageCalculationDeepDive.md](#damagecalculationdeepdivedmd) → Sections 6, 10
4. Implement in: `simulator/config.py` → `ADDITIONAL_DAMAGE`
5. Test: Add unit test in `tests/test_damage_simulator.py`

### **Fixing Damage Bug**
1. Find the symptom in the damage flow: [DamageFlowDiagrams.md](#damageflowdiagramsmd) → Section 1
2. Trace through the detailed logic: [DamageCalculationDeepDive.md](#damagecalculationdeepdivedmd) → relevant section
3. Look at code examples: [DamageFlowDiagrams.md](#damageflowdiagramsmd) → Section 8
4. Reference actual implementation: [DamageFlowDiagrams.md](#damageflowdiagramsmd) → Section 3 (Python code)

### **Optimizing Simulation Performance**
1. Understand the bottleneck: [DamageCalculationDeepDive.md](#damagecalculationdeepdivedmd) → Section 4
2. Check convergence logic: [DamageFlowDiagrams.md](#damageflowdiagramsmd) → Section 7
3. Reference: [Architecture.md](#architecturemd) → performance characteristics section

### **Implementing a New Feature**
1. Determine where it fits: [Architecture.md](#architecturemd) → Sections 2, 5
2. Check if it affects damage: [DamageCalculationDeepDive.md](#damagecalculationdeepdivedmd) → relevant sections
3. Add to Config: [Architecture.md](#architecturemd) → Config section
4. See development workflow: [Architecture.md](#architecturemd) → Development Workflow section

---

## Document Cross-References

### Damage Type Organization

- Discussed in: [Architecture.md](#architecturemd) → Technical Implementation Details
- Detailed in: [DamageCalculationDeepDive.md](#damagecalculationdeepdivedmd) → Section 3
- Visualized in: [DamageFlowDiagrams.md](#damageflowdiagramsmd) → Section 2

### Critical Hit System

- Overview in: [Architecture.md](#architecturemd) → Technical Implementation Details
- Mechanics in: [DamageCalculationDeepDive.md](#damagecalculationdeepdivedmd) → Section 6
- Decision tree in: [DamageFlowDiagrams.md](#damageflowdiagramsmd) → Section 4
- Code example in: [DamageFlowDiagrams.md](#damageflowdiagramsmd) → Example 2

### Immunity Application

- Described in: [DamageCalculationDeepDive.md](#damagecalculationdeepdivedmd) → Section 8
- Visualized in: [DamageFlowDiagrams.md](#damageflowdiagramsmd) → Section 5
- Formula in: [DamageCalculationDeepDive.md](#damagecalculationdeepdivedmd) → Advanced Concepts

### Non-Stackable Damage

- Logic in: [DamageCalculationDeepDive.md](#damagecalculationdeepdivedmd) → Section 10
- Flow in: [DamageFlowDiagrams.md](#damageflowdiagramsmd) → Section 6
- Code example in: [DamageFlowDiagrams.md](#damageflowdiagramsmd) → Example 3

### Convergence Detection

- Overview in: [Architecture.md](#architecturemd) → Technical Implementation Details
- Detailed explanation in: [DamageCalculationDeepDive.md](#damagecalculationdeepdivedmd) → Section 11
- Algorithm flowchart in: [DamageFlowDiagrams.md](#damageflowdiagramsmd) → Section 7

---

## File Locations

All documentation files are in the `/docs/` directory:

```
C:\gdrive_avirams91\Code\Python\ADOH_DPS\
├── docs/
│   ├── README.md                           # This file
│   ├── Architecture.md                     # System architecture
│   ├── DamageCalculationDeepDive.md       # Damage mechanics
│   └── DamageFlowDiagrams.md              # Visual flows and code
└── [main codebase files...]
```

---

## Key Concepts Quick Reference

### Damage Dictionary Structure

**Post-Refactoring:** Internally uses `DamageRoll` dataclass for type safety.

```python
from simulator.damage_roll import DamageRoll

# Internal representation (type-safe):
dmg_dict = {
    'physical': [
        DamageRoll(1, 8, 0),   # Base weapon
        DamageRoll(0, 0, 31),  # Strength bonus
        DamageRoll(0, 0, 10)   # Enhancement
    ],
    'divine':   [DamageRoll(2, 6, 0)],    # Weapon bonus damage property
    'fire':     [DamageRoll(1, 4, 10)],   # Flame weapon
    'sneak':    [DamageRoll(6, 6, 0)],    # Sneak attack (non-stackable)
    'massive':  [DamageRoll(2, 8, 0)],    # Massive critical (non-stackable)
}

# Legacy list format (for serialization/UI):
dmg_dict_legacy = {
    'physical': [[1,8,0], [0,0,31], [0,0,10]],
    'divine':   [[2,6,0]],
    'fire':     [[1,4,10]],
    'sneak':    [[6,6,0]],
    'massive':  [[2,8,0]],
}

# Conversion between formats:
DamageRoll.from_list([1, 8, 10])  # → DamageRoll(dice=1, sides=8, flat=10)
DamageRoll(1, 8, 10).to_list()    # → [1, 8, 10]
```

**Key Property:** Each damage type is a **list of `DamageRoll` objects** (or legacy `[dice, sides, flat]` lists at boundaries), e.g., `DamageRoll(1, 8, 10)` → 1d8+10 damage

### Damage Flow Formula

```
1. COLLECTION
   └─ Gather all sources from weapons_db (base weapon and purple weapon properties), config file

2. AGGREGATION
   └─ Organize by damage type into dmg_dict

3. SIMULATION (per attack)
   ├─ Roll d20
   ├─ Check hit/crit/miss
   ├─ Extract non-stackable damage
   ├─ Apply critical multiplication (if crit)
   ├─ Add crit bonus feats (if crit)
   ├─ Roll all damage dice
   ├─ Apply immunities (floor-based reduction)
   └─ Sum total damage

4. ACCUMULATION (per round)
   ├─ Add all attack damage
   ├─ Track DPS rolling average
   └─ Check convergence

5. ANALYSIS
   ├─ Calculate final DPS
   ├─ Generate statistics
   └─ Return results to UI
```

### Critical Hit Handling

**IMPORTANT:** NWN uses **roll multiplication, not damage multiplication**

```
Non-critical: 1d8 = [roll once]
Critical (2x): 2d8 = [roll twice] ← NOT "roll once × 2"
Critical (3x): 3d8 = [roll three times]
```

This is implemented by duplicating damage dice entries before rolling.

### Immunity Calculation

The simulator uses **floor-based reduction** with a minimum of 1 damage reduced:

```
reduction = floor(damage × immunity_percentage)
reduction = max(1, reduction)  # minimum 1 damage reduced
damage_after_immunity = damage - reduction

Example 1:
  Base damage: 50
  Physical immunity: 25% (0.25)
  Reduction: floor(50 × 0.25) = floor(12.5) = 12
  Minimum 1 reduced: max(1, 12) = 12
  After immunity: 50 - 12 = 38
  
Example 2:
  Base damage: 3
  Physical immunity: 25% (0.25)
  Reduction: floor(3 × 0.25) = floor(0.75) = 0
  Minimum 1 reduced: max(1, 0) = 1
  After immunity: 3 - 1 = 2
```

**Damage Vulnerability** (negative immunity) adds damage instead:
```
  Base damage: 50
  Physical vulnerability: -5% (-0.05)
  Added: floor(50 × 0.05) = 2
  After vulnerability: 50 + 2 = 52
```

### Why Simulation Over Averages?

**Average approach:** `1d8 average = 4.5`
**Problem:** Doesn't capture variance, crits, immunities properly

**Simulation approach:** Roll dice 15,000 times
**Benefit:** Captures variance, special interactions, true statistical distribution

---

## Glossary

| Term                          | Definition                                                                 |
|-------------------------------|----------------------------------------------------------------------------|
| **dmg_dict**                  | Dictionary organizing all damage sources by type                           |
| **DamageRoll** *NEW*          | Type-safe dataclass representing dice roll: `DamageRoll(dice, sides, flat)` |
| **crit_multiplier**           | Number of times damage dice are rolled on critical hit (e.g., 3)           |
| **threat range**              | D20 range that triggers critical hit confirmation (e.g., 18-20)            |
| **convergence**               | Point where simulation stabilizes (DPS variance below threshold)           |
| **DPS**                       | Damage Per Second (primary output metric)                                  |
| **immunity**                  | Percentage reduction to damage type (e.g., 25% physical immunity)          |
| **vulnerability**             | Negative immunity that increases damage taken                              |
| **non-stackable**             | Damage source that only counts once per attack (e.g., sneak attack)        |
| **legendary effect**          | Special bonus from purple weapons (special damage, AB bonus, AC reduction) |
| **effect registry** *NEW*     | System mapping weapon names to legendary effect implementations            |
| **burst effect** *NEW*        | Legendary damage applied only when effect procs                            |
| **persistent effect** *NEW*   | Legendary bonus applied during effect duration window                      |
| **ab_offset**                 | AB modifier applied to each attack in progression                          |
| **dependency injection** *NEW*| Pattern using SimulatorFactory to create configured instances              |

---

## Related Files in Codebase

### Core Simulation

- `simulator/config.py` - Central configuration dataclass (fully type-hinted)
- `simulator/constants.py` - Magic values and weapon lists *NEW*
- `simulator/damage_roll.py` - Type-safe damage representation *NEW*
- `simulator/damage_source_resolver.py` - Damage helper functions *NEW*
- `simulator/weapon.py` - Weapon class and damage aggregation
- `simulator/attack_simulator.py` - D20 mechanics and attack rolls
- `simulator/damage_simulator.py` - Main simulation loop and convergence (optimized)
- `simulator/legend_effect.py` - Legendary weapon effect coordinator
- `simulator/legendary_effects/` - Extensible effect classes *NEW*
  - `base.py` - Abstract base class
  - `registry.py` - Weapon-to-effect mapping
  - `burst_damage_effect.py` - Simple damage effects
  - `perfect_strike_effect.py` - +2 AB bonus
  - `sunder_effect.py` - -2 AC reduction
  - `crushing_blow_effect.py` - Physical immunity reduction
  - And more...
- `simulator/stats_collector.py` - Statistics tracking (fully type-hinted)
- `simulator/simulator_factory.py` - Dependency injection factory *NEW*

### UI & Callbacks

- `app.py` - Main application entry point
- `callbacks/core_callbacks.py` - Simulation trigger
- `components/character_settings.py` - Character input
- `components/simulation_settings.py` - Simulation parameters

### Testing

**Post-Refactoring:** Tests reorganized into `tests/simulator/` and `tests/integration/`

- `tests/simulator/test_weapon.py` - Weapon class tests
- `tests/simulator/test_attack_simulator.py` - AttackSimulator tests
- `tests/simulator/test_damage_simulator.py` - DamageSimulator tests
- `tests/simulator/test_legend_effect.py` - LegendEffect coordinator tests
- `tests/simulator/test_legendary_effects.py` - Individual effect class tests *NEW*
- `tests/simulator/test_damage_roll.py` - DamageRoll dataclass tests *NEW*
- `tests/simulator/test_damage_source_resolver.py` - Helper function tests *NEW*
- `tests/simulator/test_simulator_factory.py` - Factory tests *NEW*
- `tests/simulator/test_constants.py` - Constants module tests *NEW*
- `tests/integration/test_full_simulation.py` - End-to-end integration tests *NEW*

### Data

- `weapons_db.py` - Weapon properties and purple weapon definitions

---

## Questions?

Refer to:
- **Architecture questions** → [Architecture.md](#architecturemd)
- **Damage calculation questions** → [DamageCalculationDeepDive.md](#damagecalculationdeepdivedmd)
- **Debugging / code flow** → [DamageFlowDiagrams.md](#damageflowdiagramsmd)

---

## Document Maintenance

| Document                     | Last Updated | Verified Against                      | Author                | Status                    |
|------------------------------|--------------|---------------------------------------|-----------------------|---------------------------|
| Architecture.md              | Jan 31, 2026 | refactor/app-wide-refactoring branch  | Architecture Analysis | ✅ Updated (v2.0)         |
| DamageCalculationDeepDive.md | Jan 31, 2026 | refactor/app-wide-refactoring branch  | Architecture Analysis | ✅ Updated (v2.0)         |
| DamageFlowDiagrams.md        | Jan 31, 2026 | refactor/app-wide-refactoring branch  | Architecture Analysis | ✅ Updated (v2.0)         |
| RefactoringSummary.md        | Jan 30, 2026 | Phase 1-3 refactoring completion      | Architecture Analysis | ✅ Complete               |
| SimulatorArchitecture.md     | Jan 30, 2026 | Simulator engine design               | Architecture Analysis | ✅ Complete               |
| README.md (this file)        | Jan 31, 2026 | All above documents                   | Architecture Analysis | ✅ Updated (refactoring)  |

---

**Project:** ADOH DPS Simulator
**Repository:** adoh-dps-simulator
**Branch:** refactor/app-wide-refactoring (Post-Phase 3 Refactoring)
**Python Version:** 3.12.3+
**Test Count:** 290+ tests (100% pass rate)
**Performance:** 40% faster (post-refactoring)
**Last Updated:** January 31, 2026  
