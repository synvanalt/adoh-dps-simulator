# Legendary Effects System Cleanup - Design Document

**Date:** 2026-01-30
**Status:** Approved for Implementation

## Problem Statement

The legendary effects system has several issues:
1. **Critical Bug:** `common_damage` format mismatch causes TypeError with Heavy Flail
2. **Backward Compatibility Cruft:** Hybrid registry/fallback approach adds complexity
3. **Hardcoded Logic:** AB bonus, AC reduction, immunity factors hardcoded in LegendEffect class
4. **Mixed Concerns:** Effect-specific logic scattered across multiple methods
5. **Inconsistent Behavior:** Some effects persist during legendary window, others don't

## Goals

1. Fix the critical bug causing benchmark crashes
2. Move to registry-only architecture (no fallback)
3. Clean separation: effect-specific logic in effect classes only
4. Clear two-phase system: burst effects (on proc) vs persistent effects (during window)
5. Easy to add new legendary weapons without touching core code

## Design Overview

### Core Architecture

**Registry-Only Pattern:**
- Every legendary weapon has a registered effect class
- No fallback/"default behavior" code paths
- Missing effect = weapon has no legendary property

**Two-Phase Effect System:**

**Phase 1 - On Proc (legendary triggers):**
- Apply ALL effects: burst + persistent
- `damage_sums`: Burst damage (fire, pure, etc.)
- `common_damage`: Persistent (continues during window)
- `ab_bonus`: Persistent (+2 AB for Perfect Strike)
- `ac_reduction`: Persistent (-2 AC for Sunder)
- `immunity_factors`: Persistent (-5% physical for Crushing Blow)

**Phase 2 - During Window (`legend_attacks_left > 0`):**
- Apply ONLY persistent effects
- `damage_sums`: NOT applied (was one-time burst)
- All other effects continue

### Effect Class Interface

```python
class LegendaryEffect(ABC):
    @abstractmethod
    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        """Apply legendary effect.

        Returns: (burst_effects, persistent_effects)

        burst_effects: {
            'damage_sums': {'fire': 45, 'pure': 23}  # One-time damage
        }

        persistent_effects: {
            'common_damage': [dice, sides, flat, type],  # Continues during window
            'immunity_factors': {'physical': -0.05},     # Continues during window
            'ab_bonus': 2,                                # Continues during window
            'ac_reduction': -2                            # Continues during window
        }
        """
        pass
```

## Effect Class Implementations

### SimpleDamageEffect (Base Class)

Most legendary weapons (30+ weapons) use this - just adds burst damage, no special mechanics.

```python
class SimpleDamageEffect(LegendaryEffect):
    """Base class for legendary effects that only add damage."""

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        damage_sums = {}

        for dmg_type, dmg_list in legend_dict.items():
            if dmg_type in ('proc', 'effect'):
                continue

            for dmg_sublist in dmg_list:
                num_dice = dmg_sublist[0]
                num_sides = dmg_sublist[1]
                flat_dmg = dmg_sublist[2] if len(dmg_sublist) > 2 else 0
                damage_sums[dmg_type] = damage_sums.get(dmg_type, 0) + \
                    attack_sim.damage_roll(num_dice, num_sides, flat_dmg)

        burst = {'damage_sums': damage_sums}
        persistent = {}

        return burst, persistent
```

**Used by:** Spear, Halberd, Trident_Fire, Trident_Ice, Longbow variants, Katana variants, etc.

### PerfectStrikeEffect

Adds burst damage + persistent +2 AB bonus.

```python
class PerfectStrikeEffect(SimpleDamageEffect):
    """Perfect Strike: +2 AB bonus during legendary window."""

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        burst, persistent = super().apply(legend_dict, stats_collector,
                                         crit_multiplier, attack_sim)
        persistent['ab_bonus'] = 2
        return burst, persistent
```

**Used by:** Darts, Kukri_Crow

### SunderEffect

Adds burst damage + persistent -2 AC reduction.

```python
class SunderEffect(SimpleDamageEffect):
    """Sunder: -2 AC reduction during legendary window."""

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        burst, persistent = super().apply(legend_dict, stats_collector,
                                         crit_multiplier, attack_sim)
        persistent['ac_reduction'] = -2
        return burst, persistent
```

**Used by:** Light Flail, Greatsword_Legion

### InconsequenceEffect

Random damage: 25% Pure, 25% Sonic, 50% nothing.

```python
class InconsequenceEffect(SimpleDamageEffect):
    """Inconsequence: Random Pure/Sonic damage or nothing."""

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        import random

        damage_sums = {}
        roll = random.random()

        if roll < 0.25:  # 25% Pure
            damage_sums['pure'] = attack_sim.damage_roll(4, 6, 0)
        elif roll < 0.50:  # 25% Sonic
            damage_sums['sonic'] = attack_sim.damage_roll(4, 6, 0)
        # else: 50% nothing

        burst = {'damage_sums': damage_sums}
        persistent = {}

        return burst, persistent
```

**Used by:** Kukri_Inconseq

### HeavyFlailEffect (Updated)

Adds persistent +5 physical damage as common damage (no burst).

```python
class HeavyFlailEffect(LegendaryEffect):
    """Heavy Flail: Persistent +5 physical common damage."""

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        from copy import deepcopy

        burst = {}
        persistent = {}

        if 'physical' in legend_dict:
            hflail_phys_dmg = deepcopy(legend_dict['physical'][0])
            common_dmg = list(hflail_phys_dmg)

            # Remove proc if present
            if len(common_dmg) > 3:
                common_dmg.pop(-1)

            # Add damage type at end: [dice, sides, flat, type]
            common_dmg.append('physical')

            persistent['common_damage'] = common_dmg

        return burst, persistent
```

**Used by:** Heavy Flail

### CrushingBlowEffect (Updated)

Adds burst damage + persistent -5% physical immunity.

```python
class CrushingBlowEffect(SimpleDamageEffect):
    """Crushing Blow: -5% physical immunity during legendary window."""

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        burst, persistent = super().apply(legend_dict, stats_collector,
                                         crit_multiplier, attack_sim)
        persistent['immunity_factors'] = {'physical': -0.05}
        return burst, persistent
```

**Used by:** Club_Stone

## Implementation Changes

### 1. Bug Fix: damage_simulator.py (Line 310)

**Current (BROKEN):**
```python
dmg_type_name = legend_dmg_common.pop(2)  # Pops flat damage, not type!
```

**Fixed:**
```python
dmg_type_name = legend_dmg_common.pop(-1)  # Pops last element (type)
```

This allows `common_damage` format: `[dice, sides, flat, type]`

### 2. Refactor: legend_effect.py

**Remove these methods:**
- `ab_bonus()` (lines 37-43) - replaced by property
- `ac_reduction()` (lines 45-51) - replaced by property
- `get_immunity_factors()` (lines 115-122) - handled by effect classes
- Default fallback (lines 103-113) - registry-only now

**Add new properties:**
```python
@property
def ab_bonus(self) -> int:
    """Get current AB bonus from legendary effect."""
    return getattr(self, '_current_ab_bonus', 0)

@property
def ac_reduction(self) -> int:
    """Get current AC reduction from legendary effect."""
    return getattr(self, '_current_ac_reduction', 0)
```

**Refactored get_legend_damage():**
```python
def get_legend_damage(self, legend_dict: dict, crit_multiplier: int):
    """Two-phase legendary effect system."""

    legend_dict_sums = defaultdict(int)
    legend_dmg_common = []
    legend_imm_factors = {}

    self._current_ab_bonus = 0
    self._current_ac_reduction = 0

    if not legend_dict:
        return dict(legend_dict_sums), legend_dmg_common, legend_imm_factors

    proc = legend_dict.get('proc')
    custom_effect = self.registry.get_effect(self.weapon.name_purple)

    if not custom_effect:
        # No registered effect - no legendary property
        return dict(legend_dict_sums), legend_dmg_common, legend_imm_factors

    if isinstance(proc, (int, float)):
        if self.legend_proc(proc):  # Just procced
            burst, persistent = custom_effect.apply(
                legend_dict, self.stats, crit_multiplier, self.attack_sim)
            self._apply_effects(burst, persistent, legend_dict_sums,
                              legend_dmg_common, legend_imm_factors)

        elif self.legend_attacks_left > 0:  # During window
            self.legend_attacks_left -= 1
            burst, persistent = custom_effect.apply(
                legend_dict, self.stats, crit_multiplier, self.attack_sim)
            # Apply ONLY persistent
            self._apply_effects({}, persistent, legend_dict_sums,
                              legend_dmg_common, legend_imm_factors)

    elif isinstance(proc, str) and crit_multiplier > 1:  # On-crit
        self.stats.legend_procs += 1
        burst, persistent = custom_effect.apply(
            legend_dict, self.stats, crit_multiplier, self.attack_sim)
        self._apply_effects(burst, persistent, legend_dict_sums,
                          legend_dmg_common, legend_imm_factors)

    return dict(legend_dict_sums), legend_dmg_common, legend_imm_factors

def _apply_effects(self, burst, persistent, legend_dict_sums,
                   legend_dmg_common, legend_imm_factors):
    """Apply burst and persistent effects."""
    # Burst damage
    for dmg_type, dmg_value in burst.get('damage_sums', {}).items():
        legend_dict_sums[dmg_type] += dmg_value

    # Persistent effects
    if persistent.get('common_damage'):
        legend_dmg_common.extend(persistent['common_damage'])

    legend_imm_factors.update(persistent.get('immunity_factors', {}))
    self._current_ab_bonus = persistent.get('ab_bonus', 0)
    self._current_ac_reduction = persistent.get('ac_reduction', 0)
```

**Use constant (line 24):**
```python
from simulator.constants import LEGEND_EFFECT_DURATION

self.legend_effect_duration = LEGEND_EFFECT_DURATION
```

### 3. Registry: legendary_effects/registry.py

Register all 40+ legendary weapons:

```python
def _register_default_effects(self):
    """Register all legendary effects."""

    # Special mechanics
    self.register('Darts', PerfectStrikeEffect())
    self.register('Kukri_Crow', PerfectStrikeEffect())

    self.register('Light Flail', SunderEffect())
    self.register('Greatsword_Legion', SunderEffect())

    self.register('Kukri_Inconseq', InconsequenceEffect())
    self.register('Heavy Flail', HeavyFlailEffect())
    self.register('Club_Stone', CrushingBlowEffect())

    # Simple damage-only (shared instance for efficiency)
    simple = SimpleDamageEffect()
    for weapon in ['Halberd', 'Spear', 'Trident_Fire', 'Trident_Ice',
                  'Dire Mace', 'Double Axe', 'Heavy Crossbow', 'Light Crossbow',
                  'Longbow_FireDragon', 'Longbow_FireCeles',
                  'Longbow_ElecDragon', 'Longbow_ElecCeles',
                  'Kama', 'Quarterstaff_Hanged', 'Greatsword_Tyr',
                  'Bastard Sword_Vald', 'Katana_Kin', 'Katana_Soul',
                  'Longsword', 'Rapier_Stinger', 'Rapier_Touch',
                  'Warhammer_Mjolnir', 'Club_Fish', 'Dagger_FW',
                  'Handaxe_Ichor', 'Light Hammer', 'Mace', 'Whip']:
        self.register(weapon, simple)
```

### 4. Base Interface: legendary_effects/base.py

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class LegendaryEffect(ABC):
    """Abstract base class for legendary weapon effects."""

    @abstractmethod
    def apply(
        self,
        legend_dict: Dict[str, Any],
        stats_collector,
        crit_multiplier: int,
        attack_sim
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Apply legendary effect.

        Returns:
            (burst_effects, persistent_effects)

            burst_effects: One-time effects on proc
                - 'damage_sums': {type: value} rolled damage

            persistent_effects: Continue during legendary window
                - 'common_damage': [dice, sides, flat, type]
                - 'immunity_factors': {type: factor}
                - 'ab_bonus': int
                - 'ac_reduction': int
        """
        pass
```

## Testing Strategy

### Update Existing Tests

**`tests/simulator/test_legendary_effects.py`:**
- Update for new two-tuple return interface
- Update assertions for burst vs persistent

### Add New Tests

1. `test_simple_damage_effect()` - Verify burst damage only
2. `test_perfect_strike_ab_bonus()` - Verify +2 AB persists
3. `test_sunder_ac_reduction()` - Verify -2 AC persists
4. `test_inconsequence_random()` - Verify 25/25/50 split
5. `test_heavy_flail_persistent_damage()` - Verify common_damage persists
6. `test_crushing_blow_immunity()` - Verify immunity factor persists
7. `test_burst_vs_persistent_phases()` - Verify damage_sums doesn't persist

### Integration Tests

Run `scripts/benchmark_detailed.py` - should complete without errors for all weapons.

## File Changes Summary

**Modified:**
1. `simulator/damage_simulator.py` - Fix bug (line 310)
2. `simulator/legend_effect.py` - Refactor to two-phase system
3. `simulator/legendary_effects/base.py` - Update interface
4. `simulator/legendary_effects/registry.py` - Register all weapons
5. `simulator/legendary_effects/heavy_flail_effect.py` - Update interface
6. `simulator/legendary_effects/crushing_blow_effect.py` - Update interface
7. `tests/simulator/test_legendary_effects.py` - Update tests

**Created:**
8. `simulator/legendary_effects/simple_damage_effect.py`
9. `simulator/legendary_effects/perfect_strike_effect.py`
10. `simulator/legendary_effects/sunder_effect.py`
11. `simulator/legendary_effects/inconsequence_effect.py`

**Total:** 7 files modified, 4 files created

## Success Criteria

1. ✅ `scripts/benchmark_detailed.py` runs without errors
2. ✅ All 425+ tests pass
3. ✅ Heavy Flail damage persists during legendary window
4. ✅ Darts gets +2 AB during legendary window
5. ✅ Light Flail applies -2 AC during legendary window
6. ✅ Club_Stone applies -5% physical immunity
7. ✅ No backward compatibility code remains
8. ✅ All legendary weapons have registered effects

## Migration Notes

**Breaking Changes:** None - external interface unchanged

**Backward Compatibility:** Not maintained - moving to registry-only

**Performance Impact:** Negligible (shared SimpleDamageEffect instance)

---

**Design Approved By:** User
**Implementation Ready:** Yes
