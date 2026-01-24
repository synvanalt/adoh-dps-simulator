# ADOH DPS Simulator - Architecture Documentation

**Last Updated:** January 23, 2026  
**Application:** ADOH DPS Simulator - Neverwinter Nights Damage-Per-Second Simulator  
**Stack:** Python 3.12+ | Dash/Flask | Plotly | NumPy/Pandas  
**Repository:** adoh-dps-simulator

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Component Interaction Flow](#component-interaction-flow)
4. [Deployment Architecture](#deployment-architecture)
5. [Key Architectural Characteristics](#key-architectural-characteristics)
6. [Component Types and Responsibilities](#component-types-and-responsibilities)
7. [Technical Implementation Details](#technical-implementation-details)

---

## Project Overview

The **ADOH DPS Simulator** is a web-based damage-per-second simulator for the Neverwinter Nights game. It provides comprehensive damage analysis by simulating attack sequences, weapon mechanics, critical hits, and character buffs/feats.

### Core Purpose

- Simulate D20 attack rolls and hit calculations
- Model weapon damage aggregation with multiple damage types
- Calculate critical hit mechanics with threat ranges
- Apply character-specific modifiers (dual-wield, feats, buffs)
- Provide real-time DPS statistics with convergence tracking

### Key Metrics

- **Codebase Size:** ~50 core Python files, ~1,500+ LOC
- **Test Coverage:** 283 unit tests with 100% pass rate
- **Architecture Pattern:** Config-driven, modular callbacks, component-based UI
- **Key Features:** Critical hit simulation, legendary weapon effects

---

## System Architecture

[![](https://mermaid.ink/img/pako:eNqFV8uK40YU_ZVCDSED6h6123bLJgzIktzjxC9sdzckDqYslW3RsiSq5Encj1USSGaRgUxgyBAIEwhZhpBNVvmY_oHkE3JVpadf45WtOvfcW6fOvSXfSZZvE6kuzSkOFmjUGHsIPmw1FQ_G0jWZIi0IXMfCoeN7qI3XhI4lgYs-Wr__2Vj675fXfyIDs0Ue_NGUPn2Gg-AkWPOvH3aw4yHTC-ka9X3HC5-Mpc8zJl3Tn5uc64d_kOGwGwtbC8IjG9i6mVN_5dnoY3-KOtjD86iMOJp49tjbKv2yhXR_Gfge8UK2XXhXu2poA57vx99RF7-YYpoFFCt7rg0mQ3ME4Me3P_379yukLzDFVkgoGpIwdLw543VqDRkNnVsioybBISuQaIbRGrV6Xa0t9vgb0mzbiXTCLki3hB2hPvaIy5maLl4SdE0wlCOjBjxH_gy0I0uHMBmR0DopsA9bnbhCOIqXUMRy5YoTKxQ4wnROQqTpMhpEcgJVa7lceVAHKZY7MIeX7dFQEH6LBoStXJBxhKecyOgP0TCEDCx0rM3Ipjkwu7o4y9dvIXZGKPEskkaLfaE-9QNCt1L3270k8Xeo7_q5tNEvd83l35C3P-hdQM1R3OOrvyLqOSWMoY5vY_c9TtGx607BYtsm0XsDc6I3hEu-BntQghK0UNSCRxMreZRaPXcAI-rMwa1Fs1-2Etrv_0CRUwukK2cXJchNYu8vyWb3RKIllGAAIVuRNYie7SDmaqIL4hHKKy4SX2ltwfv48zfoCruOLbZV5H6RLuxI0PKCVZiLffKe88iJZ3pzB7y_42C6zdZFriF9b-bMeTomon361OIPs32CaBSaTWBXuzZ7bWr9XpeL-OZdxBs7VXcxYxvsX_CllH3L0-iDuK2LKbTRSNM_mUDDijnwK9LCEOQaJsQbaTBfnaQP0oRGSUEdYi2wBx1YzGFoHe3CTHOAxUQl-3LYfHVHjtxJ9ChMYwYCwnoxW9u8MLsGP4t3qE3mcKjmbEascCOLy5cmhK-lKUAwCwn8xi6GIy2ZAy_5sGG677qA26qfRYsTK1kttIyYUNCFoCLMwfd5z8Ah3rab8MVwYogGe_NV5g2GopApZuKqEq5gE3u63xk7a4CLFB0fP7tvRcMYWuWWsHsxJg6sx_PpACKeCwcQosGLgEvG2aMbubjQ9rHN80btl5QeVxFTw2F4wB5GDJkRt5GXgR2BYI_3yW1zGJSM-CQtFyePuk9v6r2A7BbeC4mv0r3r6f2W1BFLzFHxFE2Uj3ckJOaAeAoWixWoTKz8GcRK7wUIax4AZAPnAEj08AEAb8akUpEzMwSaUX95n-uSLdj2ZrKy9mxmJ6BoPBauXcK9OXNct37UbFYb1YYMU8q_IfUjvVbSSpoMc8Gn9aPZbJaP4uaO48qmbujlNE5pnJfUyr44XkGa0KxWjTSwWak1FSUJVBQlH5iTVQTXKuapcZYGl841s6rsyZoTQwRrqqGaWlZySVWN01ywJMNLvWNL9ZCuiCwtCV3i6Kd0F9GOpXABLxFjqQ5fbUxvomH3ADEB9j71_WUSBu_c84VUn2GXwa8VbwHDwTAsMwjMMEJ1eJsMpXq1dnrKSaT6nfSlVD-uVConqlpWleqZUqmd1VRZWkt1tXJSLsFHUc_L1YpafpClW561dHJ2Wjs_LddKNTgBpVaTJQIvyT7tiP8p_O_Kw__nqiCZ?type=png)](https://mermaid.live/edit#pako:eNqFV8uK40YU_ZVCDSED6h6123bLJgzIktzjxC9sdzckDqYslW3RsiSq5Encj1USSGaRgUxgyBAIEwhZhpBNVvmY_oHkE3JVpadf45WtOvfcW6fOvSXfSZZvE6kuzSkOFmjUGHsIPmw1FQ_G0jWZIi0IXMfCoeN7qI3XhI4lgYs-Wr__2Vj675fXfyIDs0Ue_NGUPn2Gg-AkWPOvH3aw4yHTC-ka9X3HC5-Mpc8zJl3Tn5uc64d_kOGwGwtbC8IjG9i6mVN_5dnoY3-KOtjD86iMOJp49tjbKv2yhXR_Gfge8UK2XXhXu2poA57vx99RF7-YYpoFFCt7rg0mQ3ME4Me3P_379yukLzDFVkgoGpIwdLw543VqDRkNnVsioybBISuQaIbRGrV6Xa0t9vgb0mzbiXTCLki3hB2hPvaIy5maLl4SdE0wlCOjBjxH_gy0I0uHMBmR0DopsA9bnbhCOIqXUMRy5YoTKxQ4wnROQqTpMhpEcgJVa7lceVAHKZY7MIeX7dFQEH6LBoStXJBxhKecyOgP0TCEDCx0rM3Ipjkwu7o4y9dvIXZGKPEskkaLfaE-9QNCt1L3270k8Xeo7_q5tNEvd83l35C3P-hdQM1R3OOrvyLqOSWMoY5vY_c9TtGx607BYtsm0XsDc6I3hEu-BntQghK0UNSCRxMreZRaPXcAI-rMwa1Fs1-2Etrv_0CRUwukK2cXJchNYu8vyWb3RKIllGAAIVuRNYie7SDmaqIL4hHKKy4SX2ltwfv48zfoCruOLbZV5H6RLuxI0PKCVZiLffKe88iJZ3pzB7y_42C6zdZFriF9b-bMeTomon361OIPs32CaBSaTWBXuzZ7bWr9XpeL-OZdxBs7VXcxYxvsX_CllH3L0-iDuK2LKbTRSNM_mUDDijnwK9LCEOQaJsQbaTBfnaQP0oRGSUEdYi2wBx1YzGFoHe3CTHOAxUQl-3LYfHVHjtxJ9ChMYwYCwnoxW9u8MLsGP4t3qE3mcKjmbEascCOLy5cmhK-lKUAwCwn8xi6GIy2ZAy_5sGG677qA26qfRYsTK1kttIyYUNCFoCLMwfd5z8Ah3rab8MVwYogGe_NV5g2GopApZuKqEq5gE3u63xk7a4CLFB0fP7tvRcMYWuWWsHsxJg6sx_PpACKeCwcQosGLgEvG2aMbubjQ9rHN80btl5QeVxFTw2F4wB5GDJkRt5GXgR2BYI_3yW1zGJSM-CQtFyePuk9v6r2A7BbeC4mv0r3r6f2W1BFLzFHxFE2Uj3ckJOaAeAoWixWoTKz8GcRK7wUIax4AZAPnAEj08AEAb8akUpEzMwSaUX95n-uSLdj2ZrKy9mxmJ6BoPBauXcK9OXNct37UbFYb1YYMU8q_IfUjvVbSSpoMc8Gn9aPZbJaP4uaO48qmbujlNE5pnJfUyr44XkGa0KxWjTSwWak1FSUJVBQlH5iTVQTXKuapcZYGl841s6rsyZoTQwRrqqGaWlZySVWN01ywJMNLvWNL9ZCuiCwtCV3i6Kd0F9GOpXABLxFjqQ5fbUxvomH3ADEB9j71_WUSBu_c84VUn2GXwa8VbwHDwTAsMwjMMEJ1eJsMpXq1dnrKSaT6nfSlVD-uVConqlpWleqZUqmd1VRZWkt1tXJSLsFHUc_L1YpafpClW561dHJ2Wjs_LddKNTgBpVaTJQIvyT7tiP8p_O_Kw__nqiCZ)
```mermaid
graph TB
    subgraph "Web Application Layer"
        APP["📱 Dash Application<br/>app.py<br/>(Main Entry Point)"]
        CACHE["💾 Diskcache<br/>Background Job Manager"]
    end

    subgraph "UI Components Layer"
        NAVBAR["🔧 Navbar Component"]
        CHAR_SET["⚙️ Character Settings<br/>AB, Size, Feats"]
        ADDITIONAL["💥 Additional Damage Panel<br/>Flame Weapon, Bane of Enemies, etc."]
        SIM_SET["📊 Simulation Settings<br/>Target AC, Rounds, Immunities"]
        RESULTS["📈 Results Tab<br/>DPS Statistics"]
        REFERENCE["📚 Reference Tab<br/>Weapon Properties"]
        PLOTS["📉 Plots Tab<br/>Plotly Charts"]
        PROGRESS["⏳ Progress Modal"]
    end

    subgraph "Callback Layer"
        CORE_CB["🔄 Core Callbacks<br/>core_callbacks.py<br/>(Simulation Trigger)"]
        UI_CB["🎯 UI Callbacks<br/>ui_callbacks.py<br/>(State Management)"]
        PLOT_CB["📊 Plots Callbacks<br/>plots_callbacks.py<br/>(Chart Generation)"]
        VAL_CB["✅ Validation Callbacks<br/>validation_callbacks.py<br/>(Input Validation)"]
    end

    subgraph "Simulation Engine Layer"
        CONFIG["⚙️ Config<br/>simulator/config.py<br/>(Central Configuration)"]
        WEAPON["🗡️ Weapon Class<br/>simulator/weapon.py<br/>(Weapon Properties & Damage)"]
        ATTACK_SIM["💢 AttackSimulator<br/>simulator/attack_simulator.py<br/>(D20 Mechanics)"]
        DAMAGE_SIM["🎯 DamageSimulator<br/>simulator/damage_simulator.py<br/>(Simulation Orchestrator)"]
        LEGEND["⚡ LegendEffect<br/>simulator/legend_effect.py<br/>(Proc Effects)"]
        STATS["📊 StatsCollector<br/>simulator/stats_collector.py<br/>(Statistics Tracking)"]
    end

    subgraph "Data Layer"
        WEAPONS_DB["🗃️ Weapons Database<br/>weapons_db.py<br/>(Weapon Properties)"]
    end

    APP -->|Initializes| UI_CB
    APP -->|Initializes| CORE_CB
    APP -->|Initializes| PLOT_CB
    APP -->|Initializes| VAL_CB
    APP -->|Uses| CACHE
    APP -->|Loads| CONFIG

    CORE_CB -->|Instantiates| DAMAGE_SIM
    CORE_CB -->|Updates UI| RESULTS
    CORE_CB -->|Updates UI| PROGRESS

    UI_CB -->|Updates| CHAR_SET
    UI_CB -->|Updates| ADDITIONAL
    UI_CB -->|Updates| SIM_SET
    UI_CB -->|Updates| REFERENCE

    PLOT_CB -->|Generates| PLOTS
    VAL_CB -->|Validates| CHAR_SET

    DAMAGE_SIM -->|Uses| CONFIG
    DAMAGE_SIM -->|Uses| WEAPON
    DAMAGE_SIM -->|Uses| ATTACK_SIM
    DAMAGE_SIM -->|Uses| LEGEND
    DAMAGE_SIM -->|Uses| STATS

    WEAPON -->|Loads from| WEAPONS_DB
    WEAPON -->|Uses| CONFIG
    ATTACK_SIM -->|Uses| WEAPON
    ATTACK_SIM -->|Uses| CONFIG

    style APP fill:#FF6B6B,stroke:#C92A2A,color:#fff
    style CACHE fill:#4ECDC4,stroke:#0B7285,color:#fff
    style CONFIG fill:#FFE66D,stroke:#F59F00,color:#000
    style DAMAGE_SIM fill:#95E1D3,stroke:#27AE60,color:#fff
    style ATTACK_SIM fill:#A8D8EA,stroke:#0288D1,color:#fff
```

---

## Component Interaction Flow

This diagram shows the runtime data flow when a user initiates a DPS simulation:
[![](https://mermaid.ink/img/pako:eNqFVV1v0zAU_SuWn0AKWZo1WxuhSaMdYhJDaGUgob54yW1qzbGL7QBj2hsPiAckPt55AYk3_ho_gRvbySotglaq6vice889vte5ooUqgebUwKsGZAFzzirN6qUk-NkwbXnBN0xacmZAE2bIn--ff7jFAOTYAz79wr_3z_XOwUzVGyVBWnMbPVMaPP7be7fwDCbEOSsuBggLXof4v8mc1azyDHzcCGbVgKAjWXEZknz5SQKSK-mIfncgj2XWeNLXj27FDW6aUJEQUAxmOwXTiJ75oVs72pybjWCXS-lprX_3Dg7OjnMyirF4ueJVg3YswFouK8-5c_ggIi-AoYMROZxFBGwR3w0BjpHempaTFAMIXlx05QF50FirQqYW00N3Y_KcCV62oGO5abpjCSAMkJNxjFvGYkG8hXmje4-dsDfcroNoz8dtpHs_c5K1ETjSBX_nj6gvwlo82j5Y5DYfQwWyPFqt0NbtcE7NXuuOczwoIQvV6AK8QyutanIoRPdwSM1-TI7eQtFgLTfnTx4rtfEmj7IoSRKiVSNLE9z1vwIx5LSRQTY5dRC_1358hq1Up6iUlGlCVkoTYMWaMMf8B2UOFnTdNukjbndmGn9OuPlvkuBFn8debmCA4zo57x28aWWPRdu3672htc5P0Pk1YNl40K9BV-3l4B1bPJsTu9Zg1kqUwTEm7DYQex9lQXmjKZypFzSNyUMuXX_cEuXALQzhYYJwSJIYQ9pGSzJ_uugmK1QhDJCT9jLxB0SeAJS3U2_1AwrFKWu2G2LQkJCmG1Sc1LONm51u0p-x80Fk2iNna7wgzM5ToTq5bnLb-UcczmO4GFxZh2jJpeGGRrTSvKS51Q1EtMYOYe2SXrUhltSuoYYlzfFvyfTFki7lNXLwEnqpVN3RsKOrNc1XDP2JaOP0hNu9f6qxYtAz9M3SfJKmuy4Kza_oW5qPsiwe702naTaejrPxKN2L6CXN72XjJJ6ko-kkG-1me8n-_nVE37nEaZykk90JbiTjJMXvfkSh5DjqJ_4t4142138BZp4dSA?type=png)](https://mermaid.live/edit#pako:eNqFVV1v0zAU_SuWn0AKWZo1WxuhSaMdYhJDaGUgob54yW1qzbGL7QBj2hsPiAckPt55AYk3_ho_gRvbySotglaq6vice889vte5ooUqgebUwKsGZAFzzirN6qUk-NkwbXnBN0xacmZAE2bIn--ff7jFAOTYAz79wr_3z_XOwUzVGyVBWnMbPVMaPP7be7fwDCbEOSsuBggLXof4v8mc1azyDHzcCGbVgKAjWXEZknz5SQKSK-mIfncgj2XWeNLXj27FDW6aUJEQUAxmOwXTiJ75oVs72pybjWCXS-lprX_3Dg7OjnMyirF4ueJVg3YswFouK8-5c_ggIi-AoYMROZxFBGwR3w0BjpHempaTFAMIXlx05QF50FirQqYW00N3Y_KcCV62oGO5abpjCSAMkJNxjFvGYkG8hXmje4-dsDfcroNoz8dtpHs_c5K1ETjSBX_nj6gvwlo82j5Y5DYfQwWyPFqt0NbtcE7NXuuOczwoIQvV6AK8QyutanIoRPdwSM1-TI7eQtFgLTfnTx4rtfEmj7IoSRKiVSNLE9z1vwIx5LSRQTY5dRC_1358hq1Up6iUlGlCVkoTYMWaMMf8B2UOFnTdNukjbndmGn9OuPlvkuBFn8debmCA4zo57x28aWWPRdu3672htc5P0Pk1YNl40K9BV-3l4B1bPJsTu9Zg1kqUwTEm7DYQex9lQXmjKZypFzSNyUMuXX_cEuXALQzhYYJwSJIYQ9pGSzJ_uugmK1QhDJCT9jLxB0SeAJS3U2_1AwrFKWu2G2LQkJCmG1Sc1LONm51u0p-x80Fk2iNna7wgzM5ToTq5bnLb-UcczmO4GFxZh2jJpeGGRrTSvKS51Q1EtMYOYe2SXrUhltSuoYYlzfFvyfTFki7lNXLwEnqpVN3RsKOrNc1XDP2JaOP0hNu9f6qxYtAz9M3SfJKmuy4Kza_oW5qPsiwe702naTaejrPxKN2L6CXN72XjJJ6ko-kkG-1me8n-_nVE37nEaZykk90JbiTjJMXvfkSh5DjqJ_4t4142138BZp4dSA)
```mermaid
sequenceDiagram
    participant User as 👤 User
    participant UI as 🎨 UI<br/>Components
    participant Core as 🔄 Core<br/>Callbacks
    participant Sim as 🎯 Damage<br/>Simulator
    participant Engine as 💥 Simulation<br/>Engine
    participant Stats as 📊 Statistics<br/>Collector
    participant Results as 📈 Results<br/>Display

    User->>UI: 1. Configure Settings<br/>(AB, Weapon, AC, etc.)
    UI->>Core: 2. Click Simulate Button
    Core->>Core: 3. Validate Inputs
    Core->>Sim: 4. Instantiate DamageSimulator<br/>with Config
    Sim->>Engine: 5. Initialize<br/>Weapon, AttackSimulator,<br/>LegendEffect
    Sim->>Sim: 6. Collect Damage Sources<br/>from All Sources
    Sim->>Engine: 7. Execute Simulation Loop<br/>(15,000 rounds)
    
    loop Run Attack Rounds
        Engine->>Engine: Roll d20 for each attack
        Engine->>Engine: Determine Hit/Crit/Miss
        Engine->>Engine: Roll Damage for each type
        Engine->>Stats: Collect Statistics
    end
    
    Engine->>Sim: 8. Check Convergence<br/>(STD threshold)
    alt Convergence Reached
        Sim->>Stats: 9. Finalize Statistics
        Stats->>Results: 10. Return DPS Results
    else More Rounds Needed
        Sim->>Engine: 7. Continue Simulation
    end
    
    Results->>UI: 11. Update Results Tab
    Results->>UI: 12. Update Charts/Plots
    UI->>User: 13. Display DPS Analysis
```

---

## Key Architectural Characteristics

### 1. **Config-Driven Architecture**

The entire application is driven by a central `Config` dataclass that contains all user-configurable parameters:

```python
# From simulator/config.py
@dataclass
class Config:
    # Target Settings
    TARGET_AC: int = 65
    TARGET_IMMUNITIES_FLAG: bool = True
    TARGET_IMMUNITIES: Dict[str, float] = {...}
    
    # Simulation Settings
    ROUNDS: int = 15000
    STD_THRESHOLD: float = 0.0002
    
    # Character Settings
    AB: int = 68
    STR_MOD: int = 21
    KEEN: bool = True
    IMPROVED_CRIT: bool = True
    
    # Weapon & Additional Damage
    DEFAULT_WEAPONS: List[str] = ["Spear"]
    ADDITIONAL_DAMAGE: Dict[str, Any] = {...}
```

**Benefits:**
- Centralized parameter management
- Easy to modify simulation behavior globally
- Supports complex feature combinations
- Enables comprehensive testing

### 2. **Modular Callback Architecture**

Callbacks are organized into four independent modules that register callbacks separately:

| Module                    | Responsibility                                               |
|---------------------------|--------------------------------------------------------------|
| `core_callbacks.py`       | Simulation trigger, result handling, background jobs         |
| `ui_callbacks.py`         | UI state management, component visibility, reference updates |
| `plots_callbacks.py`      | Chart generation and data visualization                      |
| `validation_callbacks.py` | Input validation and constraint checking                     |

**Pattern:** Each module has a `register_*_callbacks(app, cfg)` function called in `app.py`.

### 3. **Composition Over Inheritance**

The simulation engine uses composition with dependency injection:

```
DamageSimulator
├── Weapon (weapon properties)
├── AttackSimulator (D20 mechanics)
├── LegendEffect (proc effects)
└── StatsCollector (statistics tracking)
```

Each class has a single responsibility and is composed with its dependencies.

### 4. **Background Job Management**

Complex simulations run in the background using Diskcache:

```python
cache = diskcache.Cache('./cache')
background_callback_manager = DiskcacheManager(cache)
```

**Use Case:** 15,000-round simulations with progress tracking don't block the UI.

### 5. **Component-Based UI**

UI is split into modular, reusable component functions:

```
components/
├── navbar.py                  # Navigation bar
├── character_settings.py       # Character input section
├── additional_damage.py        # Extra damage sources
├── simulation_settings.py      # Simulation parameters
├── results_tab.py            # Results display
├── reference_tab.py          # Weapon/immunity reference
├── plots.py                  # Chart components
└── progress_modal.py         # Progress indicator
```

Each returns a Dash component tree that can be composed into the main layout.

---

## Component Types and Responsibilities

### **Simulator Components** (Core Engine)

#### 1. **Config** (`simulator/config.py`)
- **Type:** Dataclass configuration container
- **Responsibility:** Store all simulation parameters
- **Key Methods:** `asdict()` for serialization
- **Immutable During Run:** Yes (copied for each simulation)

#### 2. **Weapon** (`simulator/weapon.py`)
- **Type:** Weapon property calculator
- **Responsibility:** Load weapon stats, calculate threat ranges, critical multipliers, enhancement bonuses
- **Key Methods:**
  - `get_crit_threat()` - Calculate critical threat range
  - `crit_multiplier()` - Calculate crit damage multiplier
  - `aggregate_damage_sources()` - Combine all damage sources
- **Dependencies:** WEAPON_PROPERTIES database, Config

#### 3. **AttackSimulator** (`simulator/attack_simulator.py`)
- **Type:** D20 mechanics engine
- **Responsibility:** Simulate hit rolls, critical hits, and threat rolls
- **Key Methods:**
  - `calculate_attack_bonus()` - Compute AB with weapon bonuses
  - `calculate_hit_chances()` - Determine hit/crit probabilities
  - `d20_roll_attack()` - Simulate single attack roll
  - `roll_damage()` - Roll damage dice for hit
- **Dependencies:** Weapon, Config
- **Core Logic:** D20 system mechanics (always hits on 20, always misses on 1)

#### 4. **DamageSimulator** (`simulator/damage_simulator.py`)
- **Type:** Simulation orchestrator
- **Responsibility:** Execute full damage simulation with convergence tracking
- **Key Methods:**
  - `collect_damage_from_all_sources()` - Aggregate all damage
  - `run_attack_round()` - Execute single round
  - `run_simulation()` - Execute full simulation with convergence
  - `check_convergence()` - Determine if simulation is stable
- **Dependencies:** Weapon, AttackSimulator, LegendEffect, StatsCollector, Config
- **Key Feature:** Rolling window convergence using standard deviation threshold

#### 5. **LegendEffect** (`simulator/legend_effect.py`)
- **Type:** Legendary weapon effect processor
- **Responsibility:** Apply legendary weapon proc effects (e.g., Sunder, Terrifying Crescent)
- **Key Methods:**
  - `apply_effect()` - Apply legendary weapon effect
  - `chance_to_proc()` - Determine proc chance
- **Dependencies:** StatsCollector, Weapon, AttackSimulator

#### 6. **StatsCollector** (`simulator/stats_collector.py`)
- **Type:** Statistics aggregator
- **Responsibility:** Collect and organize simulation statistics by damage type
- **Key Methods:**
  - `add_damage()` - Record damage hit
  - `get_summary()` - Return aggregated statistics
  - `get_dps()` - Calculate DPS from collected data
- **Data Tracked:** Damage by type, round count, min/max damage, average DPS

### **UI Components** (Dash)

Each component function returns a Dash component tree:

| Component                | Elements                    | Purpose                              |
|--------------------------|-----------------------------|--------------------------------------|
| `navbar.py`              | Header, branding            | Navigation and title                 |
| `character_settings.py`  | Input fields, tooltips      | AB, size, feats configuration        |
| `simulation_settings.py` | Dropdowns, inputs, switches | AC, rounds, immunities               |
| `additional_damage.py`   | Dynamic rows, toggles       | Extra damage source management       |
| `results_tab.py`         | Tables, cards               | DPS statistics display               |
| `reference_tab.py`       | Tables                      | Weapon properties reference          |
| `plots.py`               | Plotly graphs               | DPS distribution, damage charts      |
| `progress_modal.py`      | Modal, spinner              | Progress indicator during simulation |

### **Callback Modules** (State Management)

| Module                    | Callbacks                                      | Pattern                      |
|---------------------------|------------------------------------------------|------------------------------|
| `core_callbacks.py`       | `simulate-button` click → simulation → results | Background job with progress |
| `ui_callbacks.py`         | Input changes → component updates              | Real-time UI state           |
| `plots_callbacks.py`      | Results store → chart updates                  | Reactive chart generation    |
| `validation_callbacks.py` | Input → validation feedback                    | Constraint enforcement       |

---

## Technical Implementation Details

### **D20 Attack Mechanics**

The `AttackSimulator` implements NWN D20 rules:

```
Hit Chance = max(0.05, min(0.95, (21 + AB - AC) * 0.05))
```

- Natural 20 (roll = 20) always hits
- Natural 1 (roll = 1) always misses
- Threat range depends on weapon and feats (KEEN, IMPROVED_CRIT, WEAPONMASTER)
- Critical hit confirmed if threat roll hits

### **Convergence Detection**

Simulation continues until a rolling 15-round window stabilizes:

```python
# Standard deviation of DPS in last 15 rounds < threshold
if std_dev(dps_window) < STD_THRESHOLD:
    convergence_reached = True
```

Default: `STD_THRESHOLD = 0.0002` (0.02% variation)

### **Damage Immunity Stacking**

Multiple immunities stack additively:

```
Final Damage = Base Damage * (1 - sum(immunity_percentages))
```

Example: 25% physical + 25% fire = 50% total reduction (multiplicative on remaining damage)

### **Critical Hit Multiplier**

Applied per damage type:

```
Crit Damage = Base Damage * Multiplier
```

Example: 2.0x multiplier for most weapons, 3.0x for some (Scythe)

### **Additional Damage Sources**

Handled as per-source dictionaries:

```python
ADDITIONAL_DAMAGE: {
    "Flame_Weapon": [enabled, {'fire': [1, 4, 10]}],
    "Bane_of_Enemies": [enabled, {'physical': [2, 6, 0]}],
    # ...
}
```

Each enabled source adds dice to the damage pool per hit.

---

## Data Models

### **Weapon Representation**

```python
WEAPON_PROPERTIES: {
    'Spear': {
        'dmg': [1, 8, 'piercing'],     # [dice, sides, type]
        'threat': 20,                   # Threat range start
        'multiplier': 2,                # Critical multiplier
        'size': 'M'                     # S/M/L
    }
}

PURPLE_WEAPONS: {
    'Spear_PK': {
        'enhancement': 7,               # Base enhancement
        'undead': {'enhancement': 10},  # Race-specific bonus
        'legendary': {
            'proc': 0.05,               # Proc chance
            'fire': [1, 30],            # Proc damage
            'effect': 'sunder'          # Proc effect
        }
    }
}
```

### **Damage Dictionary Structure**

```python
dmg_dict: {
    'physical': [[1, 8], [2, 6, 10]],   # Weapon + additional sources
    'fire': [[1, 4, 10]],               # Flame weapon
    'negative': [[1, 6]],               # Negative damage
}
```

Organized by damage type for per-type immunity application.

### **Statistics Structure**

```python
stats: {
    'total_damage': 15420.5,
    'total_crits': 145,
    'total_hits': 850,
    'dps': 102.8,
    'damage_by_type': {
        'physical': 12340.2,
        'fire': 3080.3,
    }
}
```

---

## File Interaction Matrix

| File                      | Imports                                                  | Imported By                                  | Purpose                   |
|---------------------------|----------------------------------------------------------|----------------------------------------------|---------------------------|
| `config.py`               | -                                                        | All simulator classes, callbacks             | Central configuration     |
| `weapon.py`               | `config.py`, `weapons_db.py`                             | `attack_simulator.py`, `damage_simulator.py` | Weapon properties         |
| `attack_simulator.py`     | `weapon.py`, `config.py`                                 | `damage_simulator.py`                        | D20 mechanics             |
| `damage_simulator.py`     | All simulator classes                                    | `core_callbacks.py`                          | Simulation orchestration  |
| `legend_effect.py`        | `weapon.py`, `attack_simulator.py`, `stats_collector.py` | `damage_simulator.py`                        | Legendary effects         |
| `stats_collector.py`      | -                                                        | `damage_simulator.py`, `legend_effect.py`    | Statistics tracking       |
| `weapons_db.py`           | -                                                        | `weapon.py`                                  | Weapon database           |
| `core_callbacks.py`       | All simulator classes                                    | `app.py`                                     | Simulation trigger        |
| `ui_callbacks.py`         | `config.py`, `weapons_db.py`                             | `app.py`                                     | UI state                  |
| `plots_callbacks.py`      | `plotly.graph_objects`                                   | `app.py`                                     | Chart generation          |
| `validation_callbacks.py` | `config.py`                                              | `app.py`                                     | Input validation          |
| `app.py`                  | All components, all callbacks                            | Entry point                                  | Application orchestration |

---

## Performance Characteristics

| Metric          | Value  | Notes                          |
|-----------------|--------|--------------------------------|
| Simulation Time | 5-10s  | 15,000 rounds with convergence |
| Memory Usage    | ~50MB  | Per simulation instance        |
| Test Suite      | ~1.5s  | 283 tests on Python 3.12.3     |
| UI Response     | <100ms | Real-time input feedback       |
| Cache Overhead  | <10MB  | Diskcache for background jobs  |

---

## Development Workflow

### Adding a New Feature

1. **Add to Config** (`simulator/config.py`)
   - Define new parameter with sensible default

2. **Modify Simulator** (appropriate simulator file)
   - Implement feature logic
   - Add dependency injection if needed

3. **Add Tests** (`tests/test_*.py`)
   - Test edge cases
   - Verify integration with existing features

4. **Add UI Component** (`components/` or update existing)
   - Create input/display element
   - Add to layout in `app.py`

5. **Add Callback** (`callbacks/` or update existing)
   - Register callback to handle new input
   - Validate input
   - Trigger simulation if needed

6. **Test & Validate**
   - Run `pytest tests/ -v`
   - Verify UI loads with `python app.py`
   - Test feature end-to-end

### Adding a New Weapon

1. Add to base weapon properties to `weapons_db.py`:
   ```python
   WEAPON_PROPERTIES['NewWeapon'] = {
       'dmg': [1, 10, 'slashing'],
       'threat': 20,
       'multiplier': 2,
       'size': 'M'
   }
   ```

2. Add to purple weapon properties to `weapons_db.py`:
   ```python
   PURPLE_WEAPONS['NewWeapon_PK'] = {
       'enhancement': 7,
       'fire': [1, 6, 0],
       'legendary': { 'proc': 0.05, 'fire': [1, 30] }
   }
   ```

3. Update dropdown in `character_settings.py`

4. Test in UI or add to test suite

---

## Known Limitations & Future Improvements

### Current Limitations

1. **No UI Testing** - Component testing is Phase 2
2. **No Database** - All data stored in Python dicts/files
3. **Single-User** - No multi-user support
4. **No Undo/Redo** - Session storage only

### Potential Improvements

1. Add database backend (PostgreSQL)
2. Implement user accounts and saved simulations
3. Add API endpoints for headless usage
4. Create component unit test suite
5. Add simulation result export (CSV, JSON)
6. Implement advanced filtering in results

---

## Conclusion

The ADOH DPS Simulator uses a **config-driven, modular architecture** with clear separation between:

- **Simulation Engine** (D20 mechanics, weapon calculations)
- **UI Layer** (Dash components, callbacks)
- **Data Layer** (Config, weapons database)
- **Testing Layer** (pytest suite)

---

**Document Generated:** January 23, 2026  
**Architecture Version:** 1.1  
**Last Code Review:** January 23, 2026 (All 283 tests passing)
