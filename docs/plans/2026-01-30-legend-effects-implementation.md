# Legendary Effects System Cleanup - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Fix critical bug and refactor legendary effects to registry-only architecture with two-phase effect system.

**Architecture:** Registry pattern with effect classes implementing burst (one-time) vs persistent (duration window) mechanics. All legendary weapons must have registered effects - no fallback behavior.

**Tech Stack:** Python 3.12, pytest, abstract base classes, Strategy pattern

---

## Task 1: Fix Critical Bug in damage_simulator.py

**Files:**
- Modify: `simulator/damage_simulator.py:310`

**Step 1: Write failing test**

Create `tests/simulator/test_damage_simulator_legend_bug.py`:

```python
import pytest
from simulator.damage_simulator import DamageSimulator
from simulator.config import Config


def test_heavy_flail_common_damage_format():
    """Test that Heavy Flail's common damage format is handled correctly.

    This was causing: TypeError: unsupported operand type(s) for +=: 'int' and 'str'
    because legend_dmg_common was [0, 0, 5, 'physical'] and code tried to pop index 2.
    """
    cfg = Config()
    cfg.ROUNDS = 100
    cfg.AB = 70
    cfg.TARGET_AC = 60

    # This should not crash
    sim = DamageSimulator('Heavy Flail', cfg)
    result = sim.simulate_dps()

    # Basic validation
    assert result['dps_crits'] >= 0
    assert result['dps_no_crits'] >= 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/simulator/test_damage_simulator_legend_bug.py -v`

Expected: FAIL with TypeError about unsupported operand type

**Step 3: Fix the bug**

In `simulator/damage_simulator.py`, line 310, change:

```python
# OLD (BROKEN):
dmg_type_name = legend_dmg_common.pop(2)

# NEW (FIXED):
dmg_type_name = legend_dmg_common.pop(-1)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/simulator/test_damage_simulator_legend_bug.py -v`

Expected: PASS

**Step 5: Run benchmark to verify fix**

Run: `python scripts/benchmark_detailed.py`

Expected: Completes without errors (may still fail on other weapons until registry is complete)

**Step 6: Commit**

```bash
git add simulator/damage_simulator.py tests/simulator/test_damage_simulator_legend_bug.py
git commit -m "fix: correct common_damage format handling in damage_simulator

- Change pop(2) to pop(-1) to get last element (damage type)
- Fixes TypeError when Heavy Flail legendary effect procs
- common_damage format is [dice, sides, flat, type] not [dice, sides, type]

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Update LegendaryEffect Base Interface

**Files:**
- Modify: `simulator/legendary_effects/base.py`

**Step 1: Write failing test**

Add to `tests/simulator/test_legendary_effects.py`:

```python
def test_base_interface_returns_two_tuple():
    """Verify that effect.apply() returns (burst, persistent) tuple."""
    from simulator.legendary_effects.base import LegendaryEffect
    from simulator.stats_collector import StatsCollector

    class TestEffect(LegendaryEffect):
        def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
            return {'damage_sums': {}}, {'ab_bonus': 0}

    effect = TestEffect()
    result = effect.apply({}, StatsCollector(), 1, None)

    assert isinstance(result, tuple)
    assert len(result) == 2
    burst, persistent = result
    assert isinstance(burst, dict)
    assert isinstance(persistent, dict)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/simulator/test_legendary_effects.py::test_base_interface_returns_two_tuple -v`

Expected: FAIL (current interface doesn't return tuple)

**Step 3: Update base interface**

In `simulator/legendary_effects/base.py`:

```python
"""Base interface for legendary weapon effects."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple


class LegendaryEffect(ABC):
    """Abstract base class for legendary weapon effects.

    Each legendary weapon with unique behavior should implement this interface.
    Effects return two dictionaries: burst (one-time) and persistent (duration window).
    """

    @abstractmethod
    def apply(
        self,
        legend_dict: Dict[str, Any],
        stats_collector,
        crit_multiplier: int,
        attack_sim
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Apply the legendary effect and return damage results.

        Args:
            legend_dict: Dictionary with legendary properties (proc, damage, effect)
            stats_collector: StatsCollector instance for tracking procs
            crit_multiplier: Critical hit multiplier (1 for normal hit)
            attack_sim: AttackSimulator instance for damage rolls

        Returns:
            Tuple of (burst_effects, persistent_effects)

            burst_effects: Applied only when effect procs
                - 'damage_sums': Dict of rolled damage by type {type: value}

            persistent_effects: Applied during legendary window
                - 'common_damage': List [dice, sides, flat, type] to add to main damage
                - 'immunity_factors': Dict of immunity modifiers {type: factor}
                - 'ab_bonus': Int AB bonus to apply
                - 'ac_reduction': Int AC reduction to apply
        """
        pass
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/simulator/test_legendary_effects.py::test_base_interface_returns_two_tuple -v`

Expected: PASS

**Step 5: Commit**

```bash
git add simulator/legendary_effects/base.py tests/simulator/test_legendary_effects.py
git commit -m "refactor: update LegendaryEffect interface to return two-tuple

- Return (burst_effects, persistent_effects) instead of single dict
- Burst effects apply only on proc (damage_sums)
- Persistent effects apply during legendary window (common_damage, ab_bonus, etc.)
- Add comprehensive docstring explaining new interface

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Create BurstDamageEffect Base Class

**Files:**
- Create: `simulator/legendary_effects/burst_damage_effect.py`
- Test: `tests/simulator/test_legendary_effects.py`

**Step 1: Write failing test**

Add to `tests/simulator/test_legendary_effects.py`:

```python
def test_burst_damage_effect_rolls_damage():
    """Test that BurstDamageEffect rolls damage correctly."""
    from simulator.legendary_effects.burst_damage_effect import BurstDamageEffect
    from simulator.stats_collector import StatsCollector
    from simulator.attack_simulator import AttackSimulator
    from simulator.weapon import Weapon
    from simulator.config import Config

    cfg = Config()
    weapon = Weapon('Spear', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    effect = BurstDamageEffect()
    legend_dict = {
        'proc': 0.05,
        'acid': [[4, 6, 0]],  # 4d6 acid
        'pure': [[4, 6, 0]]  # 4d6 pure
    }

    burst, persistent = effect.apply(legend_dict, stats, 1, attack_sim)

    # Should have burst damage
    assert 'damage_sums' in burst
    assert 'acid' in burst['damage_sums']
    assert 'pure' in burst['damage_sums']
    assert burst['damage_sums']['acid'] > 0
    assert burst['damage_sums']['pure'] > 0

    # Should have no persistent effects
    assert persistent == {}


def test_burst_damage_effect_skips_proc_and_effect_keys():
    """Test that BurstDamageEffect ignores proc and effect keys."""
    from simulator.legendary_effects.burst_damage_effect import BurstDamageEffect
    from simulator.stats_collector import StatsCollector

    effect = BurstDamageEffect()
    legend_dict = {
        'proc': 0.05,
        'effect': 'some_effect',
        'fire': [[1, 50, 0]]
    }

    burst, persistent = effect.apply(legend_dict, StatsCollector(), 1, None)

    # Should only have fire damage, not proc or effect
    assert 'proc' not in burst['damage_sums']
    assert 'effect' not in burst['damage_sums']
    assert 'fire' in burst['damage_sums']
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/simulator/test_legendary_effects.py::test_burst_damage_effect_rolls_damage -v`
Run: `pytest tests/simulator/test_legendary_effects.py::test_burst_damage_effect_skips_proc_and_effect_keys -v`

Expected: FAIL with ModuleNotFoundError

**Step 3: Create BurstDamageEffect**

Create `simulator/legendary_effects/burst_damage_effect.py`:

```python
"""Burst damage effect for legendary weapons without special mechanics."""

from simulator.legendary_effects.base import LegendaryEffect


class BurstDamageEffect(LegendaryEffect):
    """Base class for legendary effects that only add burst damage.

    This is used by most legendary weapons (30+ weapons) that just add
    damage when the legendary effect procs, without any special mechanics
    like AB bonuses, AC reduction, or immunity factors.
    """

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        """Roll damage for all damage types in legend_dict.

        Args:
            legend_dict: Dict with damage types as keys, lists of [dice, sides, flat] as values
            stats_collector: StatsCollector (unused for burst damage)
            crit_multiplier: Critical multiplier (unused for burst damage)
            attack_sim: AttackSimulator for rolling damage dice

        Returns:
            (burst_effects, persistent_effects)
            - burst: {'damage_sums': {type: rolled_value}}
            - persistent: {} (no persistent effects for burst damage)
        """
        damage_sums = {}

        for dmg_type, dmg_list in legend_dict.items():
            # Skip non-damage keys
            if dmg_type in ('proc', 'effect'):
                continue

            # Roll damage for each entry of this type
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

**Step 4: Run tests to verify they pass**

Run: `pytest tests/simulator/test_legendary_effects.py::test_burst_damage_effect_rolls_damage -v`
Run: `pytest tests/simulator/test_legendary_effects.py::test_burst_damage_effect_skips_proc_and_effect_keys -v`

Expected: All PASS

**Step 5: Commit**

```bash
git add simulator/legendary_effects/burst_damage_effect.py tests/simulator/test_legendary_effects.py
git commit -m "feat: add BurstDamageEffect base class for damage-only legendaries

- Base class for 30+ legendary weapons with no special mechanics
- Returns burst damage only, no persistent effects
- Skips 'proc' and 'effect' keys in legend_dict
- Rolls damage for all damage types

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Create PerfectStrikeEffect

**Files:**
- Create: `simulator/legendary_effects/perfect_strike_effect.py`
- Test: `tests/simulator/test_legendary_effects.py`

**Step 1: Write failing test**

Add to `tests/simulator/test_legendary_effects.py`:

```python
def test_perfect_strike_effect_adds_ab_bonus():
    """Test that PerfectStrikeEffect adds +2 AB bonus as persistent effect."""
    from simulator.legendary_effects.perfect_strike_effect import PerfectStrikeEffect
    from simulator.stats_collector import StatsCollector
    from simulator.attack_simulator import AttackSimulator
    from simulator.weapon import Weapon
    from simulator.config import Config

    cfg = Config()
    weapon = Weapon('Darts', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    effect = PerfectStrikeEffect()
    legend_dict = {
        'proc': 0.05,
        'pure': [[4, 6, 0]]
    }

    burst, persistent = effect.apply(legend_dict, stats, 1, attack_sim)

    # Should have burst damage (from parent BurstDamageEffect)
    assert 'damage_sums' in burst
    assert 'pure' in burst['damage_sums']

    # Should have persistent AB bonus
    assert 'ab_bonus' in persistent
    assert persistent['ab_bonus'] == 2
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/simulator/test_legendary_effects.py::test_perfect_strike_effect_adds_ab_bonus -v`

Expected: FAIL with ModuleNotFoundError

**Step 3: Create PerfectStrikeEffect**

Create `simulator/legendary_effects/perfect_strike_effect.py`:

```python
"""Perfect Strike legendary effect (+2 AB bonus)."""

from simulator.legendary_effects.burst_damage_effect import BurstDamageEffect


class PerfectStrikeEffect(BurstDamageEffect):
    """Perfect Strike: Burst damage + persistent +2 AB bonus.

    Used by legendary weapons that grant +2 AB bonus during the
    legendary effect duration window (5 rounds).
    """

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        """Apply Perfect Strike effect.

        Returns:
            (burst_effects, persistent_effects)
            - burst: damage from parent BurstDamageEffect
            - persistent: {'ab_bonus': 2}
        """
        # Get standard burst damage from parent
        burst, persistent = super().apply(legend_dict, stats_collector,
                                          crit_multiplier, attack_sim)

        # Add persistent AB bonus
        persistent['ab_bonus'] = 2

        return burst, persistent
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/simulator/test_legendary_effects.py::test_perfect_strike_effect_adds_ab_bonus -v`

Expected: PASS

**Step 5: Commit**

```bash
git add simulator/legendary_effects/perfect_strike_effect.py tests/simulator/test_legendary_effects.py
git commit -m "feat: add PerfectStrikeEffect for +2 AB legendary bonus

- Extends BurstDamageEffect with +2 AB bonus
- AB bonus persists during legendary window (5 rounds)
- Used by Darts and Kukri_Crow

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Create SunderEffect

**Files:**
- Create: `simulator/legendary_effects/sunder_effect.py`
- Test: `tests/simulator/test_legendary_effects.py`

**Step 1: Write failing test**

Add to `tests/simulator/test_legendary_effects.py`:

```python
def test_sunder_effect_adds_ac_reduction():
    """Test that SunderEffect adds -2 AC reduction as persistent effect."""
    from simulator.legendary_effects.sunder_effect import SunderEffect
    from simulator.stats_collector import StatsCollector
    from simulator.attack_simulator import AttackSimulator
    from simulator.weapon import Weapon
    from simulator.config import Config

    cfg = Config()
    weapon = Weapon('Light Flail', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    effect = SunderEffect()
    legend_dict = {
        'proc': 0.05,
        'effect': 'sunder'
    }

    burst, persistent = effect.apply(legend_dict, stats, 1, attack_sim)

    # Should have persistent AC reduction
    assert 'ac_reduction' in persistent
    assert persistent['ac_reduction'] == -2
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/simulator/test_legendary_effects.py::test_sunder_effect_adds_ac_reduction -v`

Expected: FAIL with ModuleNotFoundError

**Step 3: Create SunderEffect**

Create `simulator/legendary_effects/sunder_effect.py`:

```python
"""Sunder legendary effect (-2 AC reduction)."""

from simulator.legendary_effects.burst_damage_effect import BurstDamageEffect


class SunderEffect(BurstDamageEffect):
    """Sunder: Burst damage + persistent -2 AC reduction.

    Used by legendary weapons that reduce target AC by 2 during the
    legendary effect duration window (5 rounds).
    """

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        """Apply Sunder effect.

        Returns:
            (burst_effects, persistent_effects)
            - burst: damage from parent BurstDamageEffect
            - persistent: {'ac_reduction': -2}
        """
        # Get standard burst damage from parent
        burst, persistent = super().apply(legend_dict, stats_collector,
                                          crit_multiplier, attack_sim)

        # Add persistent AC reduction
        persistent['ac_reduction'] = -2

        return burst, persistent
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/simulator/test_legendary_effects.py::test_sunder_effect_adds_ac_reduction -v`

Expected: PASS

**Step 5: Commit**

```bash
git add simulator/legendary_effects/sunder_effect.py tests/simulator/test_legendary_effects.py
git commit -m "feat: add SunderEffect for -2 AC legendary reduction

- Extends BurstDamageEffect with -2 AC reduction
- AC reduction persists during legendary window (5 rounds)
- Used by Light Flail and Greatsword_Legion

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Create InconsequenceEffect

**Files:**
- Create: `simulator/legendary_effects/inconsequence_effect.py`
- Test: `tests/simulator/test_legendary_effects.py`

**Step 1: Write failing test**

Add to `tests/simulator/test_legendary_effects.py`:

```python
def test_inconsequence_effect_random_damage():
    """Test that InconsequenceEffect applies random Pure/Sonic/nothing."""
    from simulator.legendary_effects.inconsequence_effect import InconsequenceEffect
    from simulator.stats_collector import StatsCollector
    from simulator.attack_simulator import AttackSimulator
    from simulator.weapon import Weapon
    from simulator.config import Config

    cfg = Config()
    weapon = Weapon('Kukri_Inconseq', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    effect = InconsequenceEffect()
    legend_dict = {
        'proc': 'on_crit',
        'effect': 'inconsequence'
    }

    # Run multiple times to test randomness
    results = {'pure': 0, 'sonic': 0, 'nothing': 0}

    for _ in range(100):
        burst, persistent = effect.apply(legend_dict, stats, 2, attack_sim)

        damage_sums = burst.get('damage_sums', {})

        if 'pure' in damage_sums:
            results['pure'] += 1
            assert damage_sums['pure'] > 0
        elif 'sonic' in damage_sums:
            results['sonic'] += 1
            assert damage_sums['sonic'] > 0
        else:
            results['nothing'] += 1

        # Should have no persistent effects
        assert persistent == {}

    # Rough probability check (25% each, 50% nothing)
    # Allow wide range due to randomness
    assert 10 < results['pure'] < 40
    assert 10 < results['sonic'] < 40
    assert 30 < results['nothing'] < 70
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/simulator/test_legendary_effects.py::test_inconsequence_effect_random_damage -v`

Expected: FAIL with ModuleNotFoundError

**Step 3: Create InconsequenceEffect**

Create `simulator/legendary_effects/inconsequence_effect.py`:

```python
"""Inconsequence legendary effect (random Pure/Sonic/nothing)."""

import random
from simulator.legendary_effects.burst_damage_effect import BurstDamageEffect


class InconsequenceEffect(BurstDamageEffect):
    """Inconsequence: Random damage effect.

    25% chance: 4d6 Pure damage
    25% chance: 4d6 Sonic damage
    50% chance: Nothing happens
    """

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        """Apply Inconsequence effect with random outcome.

        Returns:
            (burst_effects, persistent_effects)
            - burst: {'damage_sums': {type: value}} or empty
            - persistent: {} (no persistent effects)
        """
        damage_sums = {}
        roll = random.random()  # 0.0 to 1.0

        if roll < 0.25:  # 25% Pure damage
            damage_sums['pure'] = attack_sim.damage_roll(4, 6, 0)
        elif roll < 0.50:  # 25% Sonic damage
            damage_sums['sonic'] = attack_sim.damage_roll(4, 6, 0)
        # else: 50% nothing happens

        burst = {'damage_sums': damage_sums}
        persistent = {}

        return burst, persistent
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/simulator/test_legendary_effects.py::test_inconsequence_effect_random_damage -v`

Expected: PASS

**Step 5: Commit**

```bash
git add simulator/legendary_effects/inconsequence_effect.py tests/simulator/test_legendary_effects.py
git commit -m "feat: add InconsequenceEffect for random legendary damage

- 25% Pure damage (4d6)
- 25% Sonic damage (4d6)
- 50% Nothing happens
- Used by Kukri_Inconseq

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Update HeavyFlailEffect and CrushingBlowEffect

**Files:**
- Modify: `simulator/legendary_effects/heavy_flail_effect.py`
- Modify: `simulator/legendary_effects/crushing_blow_effect.py`
- Test: `tests/simulator/test_legendary_effects.py`

**Step 1: Write failing tests**

Update existing tests in `tests/simulator/test_legendary_effects.py`:

```python
def test_heavy_flail_effect_returns_persistent_common_damage():
    """Test that Heavy Flail returns common_damage as persistent effect."""
    from simulator.legendary_effects.heavy_flail_effect import HeavyFlailEffect
    from simulator.stats_collector import StatsCollector

    stats = StatsCollector()
    effect = HeavyFlailEffect()

    legend_dict = {
        'proc': 0.05,
        'physical': [[0, 0, 5]]
    }

    burst, persistent = effect.apply(legend_dict, stats, 1, None)

    # Should have NO burst damage (Heavy Flail is pure persistent)
    assert burst == {}

    # Should have persistent common_damage
    assert 'common_damage' in persistent
    assert persistent['common_damage'] == [0, 0, 5, 'physical']


def test_crushing_blow_returns_damage_and_immunity():
    """Test that Crushing Blow returns damage and immunity factor."""
    from simulator.legendary_effects.crushing_blow_effect import CrushingBlowEffect
    from simulator.stats_collector import StatsCollector
    from simulator.attack_simulator import AttackSimulator
    from simulator.weapon import Weapon
    from simulator.config import Config

    cfg = Config()
    weapon = Weapon('Club_Stone', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    effect = CrushingBlowEffect()
    legend_dict = {
        'proc': 0.05,
        'effect': 'crushing_blow'
    }

    burst, persistent = effect.apply(legend_dict, stats, 1, attack_sim)

    # Should have burst damage from legend_dict (if any damage types present)
    # Note: This specific legend_dict has no damage, so damage_sums will be empty
    assert 'damage_sums' in burst

    # Should have persistent immunity factor
    assert 'immunity_factors' in persistent
    assert persistent['immunity_factors'] == {'physical': -0.05}
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/simulator/test_legendary_effects.py::test_heavy_flail_effect_returns_persistent_common_damage -v`
Run: `pytest tests/simulator/test_legendary_effects.py::test_crushing_blow_returns_damage_and_immunity -v`

Expected: FAIL (current interface returns single dict, not tuple)

**Step 3: Update HeavyFlailEffect**

Modify `simulator/legendary_effects/heavy_flail_effect.py`:

```python
"""Heavy Flail legendary effect implementation."""

from copy import deepcopy
from simulator.legendary_effects.base import LegendaryEffect


class HeavyFlailEffect(LegendaryEffect):
    """Heavy Flail: Persistent +5 physical damage as common damage.

    Unlike other effects, Heavy Flail adds NO burst damage.
    It only adds persistent common_damage that continues throughout
    the legendary window (5 rounds).
    """

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        """Heavy Flail's 5 physical damage is added as persistent common damage.

        Common damage is added to regular damage totals before applying immunities
        and persists throughout the legendary effect duration window.

        Returns:
            (burst_effects, persistent_effects)
            - burst: {} (no burst damage)
            - persistent: {'common_damage': [0, 0, 5, 'physical']}
        """
        burst = {}
        persistent = {}

        if 'physical' in legend_dict:
            hflail_phys_dmg = deepcopy(legend_dict['physical'][0])
            # hflail_phys_dmg is [dice, sides, flat] or [dice, sides, flat, proc]
            common_dmg = list(hflail_phys_dmg)

            # Remove proc (last element) if present
            if len(common_dmg) > 3:
                common_dmg.pop(-1)

            # Add damage type at end: [dice, sides, flat, type]
            common_dmg.append('physical')

            # Common damage is PERSISTENT (continues during window)
            persistent['common_damage'] = common_dmg

        return burst, persistent
```

**Step 4: Update CrushingBlowEffect**

Modify `simulator/legendary_effects/crushing_blow_effect.py`:

```python
"""Club_Stone (Crushing Blow) legendary effect implementation."""

from simulator.legendary_effects.burst_damage_effect import BurstDamageEffect


class CrushingBlowEffect(BurstDamageEffect):
    """Crushing Blow: Burst damage + persistent -5% physical immunity.

    Reduces target's physical immunity by 5% during the legendary
    effect duration window (5 rounds).
    """

    def apply(self, legend_dict, stats_collector, crit_multiplier, attack_sim):
        """Apply Crushing Blow effect.

        Returns:
            (burst_effects, persistent_effects)
            - burst: damage from parent BurstDamageEffect
            - persistent: {'immunity_factors': {'physical': -0.05}}
        """
        # Get standard burst damage from parent
        burst, persistent = super().apply(legend_dict, stats_collector,
                                          crit_multiplier, attack_sim)

        # Add persistent immunity reduction
        persistent['immunity_factors'] = {'physical': -0.05}

        return burst, persistent
```

**Step 5: Run tests to verify they pass**

Run: `pytest tests/simulator/test_legendary_effects.py::test_heavy_flail_effect_returns_persistent_common_damage -v`
Run: `pytest tests/simulator/test_legendary_effects.py::test_crushing_blow_returns_damage_and_immunity -v`

Expected: All PASS

**Step 6: Commit**

```bash
git add simulator/legendary_effects/heavy_flail_effect.py simulator/legendary_effects/crushing_blow_effect.py tests/simulator/test_legendary_effects.py
git commit -m "refactor: update HeavyFlail and CrushingBlow to new interface

- Update to return (burst, persistent) tuple
- HeavyFlail returns only persistent common_damage (no burst)
- CrushingBlow extends BurstDamageEffect with immunity factor
- Update tests for new interface

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Update Registry with All Effects

**Files:**
- Modify: `simulator/legendary_effects/registry.py`
- Modify: `simulator/legendary_effects/__init__.py`

**Step 1: Update __init__.py exports**

Modify `simulator/legendary_effects/__init__.py`:

```python
"""Legendary weapon effects system."""

from simulator.legendary_effects.base import LegendaryEffect
from simulator.legendary_effects.registry import LegendaryEffectRegistry
from simulator.legendary_effects.burst_damage_effect import BurstDamageEffect
from simulator.legendary_effects.perfect_strike_effect import PerfectStrikeEffect
from simulator.legendary_effects.sunder_effect import SunderEffect
from simulator.legendary_effects.inconsequence_effect import InconsequenceEffect
from simulator.legendary_effects.heavy_flail_effect import HeavyFlailEffect
from simulator.legendary_effects.crushing_blow_effect import CrushingBlowEffect

__all__ = [
    'LegendaryEffect',
    'LegendaryEffectRegistry',
    'BurstDamageEffect',
    'PerfectStrikeEffect',
    'SunderEffect',
    'InconsequenceEffect',
    'HeavyFlailEffect',
    'CrushingBlowEffect',
]
```

**Step 2: Write test for registry completeness**

Add to `tests/simulator/test_legendary_effects.py`:

```python
def test_registry_has_all_legendary_weapons():
    """Verify that all legendary weapons have registered effects."""
    from simulator.legendary_effects.registry import LegendaryEffectRegistry
    from weapons_db import PURPLE_WEAPONS

    registry = LegendaryEffectRegistry()

    # Get all legendary weapons from weapons_db
    legendary_weapons = []
    for weapon_name, props in PURPLE_WEAPONS.items():
        if 'legendary' in props:
            legendary_weapons.append(weapon_name)

    # Verify each has a registered effect
    missing = []
    for weapon_name in legendary_weapons:
        if registry.get_effect(weapon_name) is None:
            missing.append(weapon_name)

    assert len(missing) == 0, f"Missing effects for: {missing}"
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/simulator/test_legendary_effects.py::test_registry_has_all_legendary_weapons -v`

Expected: FAIL (most weapons not registered yet)

**Step 4: Update registry with all effects**

Modify `simulator/legendary_effects/registry.py`:

```python
"""Registry for legendary weapon effects."""

from typing import Dict, Optional
from simulator.legendary_effects.base import LegendaryEffect


class LegendaryEffectRegistry:
    """Registry mapping weapon names to their legendary effect handlers."""

    def __init__(self):
        """Initialize registry with all known legendary effects."""
        self._effects: Dict[str, LegendaryEffect] = {}
        self._register_default_effects()

    def _register_default_effects(self):
        """Register all default legendary effects."""
        from simulator.legendary_effects.burst_damage_effect import BurstDamageEffect
        from simulator.legendary_effects.perfect_strike_effect import PerfectStrikeEffect
        from simulator.legendary_effects.sunder_effect import SunderEffect
        from simulator.legendary_effects.inconsequence_effect import InconsequenceEffect
        from simulator.legendary_effects.heavy_flail_effect import HeavyFlailEffect
        from simulator.legendary_effects.crushing_blow_effect import CrushingBlowEffect

        # Special mechanics effects
        self.register('Darts', PerfectStrikeEffect())
        self.register('Kukri_Crow', PerfectStrikeEffect())

        self.register('Light Flail', SunderEffect())
        self.register('Greatsword_Legion', SunderEffect())

        self.register('Kukri_Inconseq', InconsequenceEffect())
        self.register('Heavy Flail', HeavyFlailEffect())
        self.register('Club_Stone', CrushingBlowEffect())

        # Burst damage-only effects (shared instance for efficiency)
        burst = BurstDamageEffect()

        burst_damage_weapons = [
            'Halberd', 'Spear', 'Trident_Fire', 'Trident_Ice',
            'Dire Mace', 'Double Axe',
            'Heavy Crossbow', 'Light Crossbow',
            'Longbow_FireDragon', 'Longbow_FireCeles',
            'Longbow_ElecDragon', 'Longbow_ElecCeles',
            'Kama', 'Quarterstaff_Hanged', 'Greatsword_Tyr',
            'Bastard Sword_Vald', 'Katana_Kin', 'Katana_Soul',
            'Longsword', 'Rapier_Stinger', 'Rapier_Touch',
            'Warhammer_Mjolnir', 'Club_Fish', 'Dagger_FW',
            'Handaxe_Ichor', 'Light Hammer', 'Mace', 'Whip'
        ]

        for weapon in burst_damage_weapons:
            self.register(weapon, burst)

    def register(self, weapon_name: str, effect: LegendaryEffect):
        """Register a legendary effect for a weapon.

        Args:
            weapon_name: Name of the weapon
            effect: LegendaryEffect implementation
        """
        self._effects[weapon_name] = effect

    def get_effect(self, weapon_name: str) -> Optional[LegendaryEffect]:
        """Get the legendary effect for a weapon.

        Args:
            weapon_name: Name of the weapon

        Returns:
            LegendaryEffect instance or None if weapon has no registered effect
        """
        return self._effects.get(weapon_name)
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/simulator/test_legendary_effects.py::test_registry_has_all_legendary_weapons -v`

Expected: PASS

**Step 6: Commit**

```bash
git add simulator/legendary_effects/registry.py simulator/legendary_effects/__init__.py tests/simulator/test_legendary_effects.py
git commit -m "feat: register all legendary weapons in effect registry

- Add all special mechanics effects (Perfect Strike, Sunder, etc.)
- Register 29 weapons with BurstDamageEffect
- Export all effect classes from __init__.py
- Add test to verify all legendary weapons have effects

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Refactor LegendEffect.get_legend_damage()

**Files:**
- Modify: `simulator/legend_effect.py`
- Test: `tests/simulator/test_legend_effect.py` (create new file)

**Step 1: Write tests for two-phase system**

Create `tests/simulator/test_legend_effect.py`:

```python
import pytest
from simulator.legend_effect import LegendEffect
from simulator.stats_collector import StatsCollector
from simulator.weapon import Weapon
from simulator.attack_simulator import AttackSimulator
from simulator.config import Config


def test_legend_effect_on_proc_applies_burst_and_persistent():
    """Test that on proc, both burst and persistent effects are applied."""
    cfg = Config()
    weapon = Weapon('Spear', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    legend_effect = LegendEffect(stats, weapon, attack_sim)

    # Spear has legendary: {'proc': 0.05, 'acid': [4, 6], 'pure': [4, 6]}
    legend_dict = {'proc': 0.05, 'acid': [[4, 6]], 'pure': [[4, 6]]}

    # Force a proc by mocking
    import random
    random.seed(1)  # Seed for reproducible proc

    damage_sums, common_damage, imm_factors = legend_effect.get_legend_damage(legend_dict, 1)

    # If procced, should have damage
    # (exact values depend on random, just check structure)
    assert isinstance(damage_sums, dict)
    assert isinstance(common_damage, list)
    assert isinstance(imm_factors, dict)


def test_legend_effect_during_window_applies_only_persistent():
    """Test that during window, only persistent effects apply (not burst damage)."""
    cfg = Config()
    weapon = Weapon('Heavy Flail', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    legend_effect = LegendEffect(stats, weapon, attack_sim)
    legend_effect.legend_attacks_left = 5  # Simulate active window

    # Heavy Flail has persistent common_damage
    legend_dict = {'proc': 0.05, 'physical': [[0, 0, 5]]}

    damage_sums, common_damage, imm_factors = legend_effect.get_legend_damage(legend_dict, 1)

    # During window: no burst damage, but common_damage should be present
    # Note: Heavy Flail has no burst damage anyway
    assert isinstance(common_damage, list)


def test_legend_effect_ab_bonus_property():
    """Test that ab_bonus property returns persistent AB bonus."""
    cfg = Config()
    weapon = Weapon('Darts', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    legend_effect = LegendEffect(stats, weapon, attack_sim)

    # Initially no bonus
    assert legend_effect.ab_bonus == 0

    # After proc (simulated by setting internal state)
    legend_effect._current_ab_bonus = 2
    assert legend_effect.ab_bonus == 2


def test_legend_effect_ac_reduction_property():
    """Test that ac_reduction property returns persistent AC reduction."""
    cfg = Config()
    weapon = Weapon('Light Flail', cfg)
    attack_sim = AttackSimulator(weapon, cfg)
    stats = StatsCollector()

    legend_effect = LegendEffect(stats, weapon, attack_sim)

    # Initially no reduction
    assert legend_effect.ac_reduction == 0

    # After proc (simulated by setting internal state)
    legend_effect._current_ac_reduction = -2
    assert legend_effect.ac_reduction == -2
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/simulator/test_legend_effect.py -v`

Expected: FAIL (current implementation doesn't have properties or two-phase logic)

**Step 3: Refactor LegendEffect class**

Modify `simulator/legend_effect.py`:

```python
from simulator.weapon import Weapon
from simulator.stats_collector import StatsCollector
from simulator.attack_simulator import AttackSimulator
from simulator.legendary_effects import LegendaryEffectRegistry
from simulator.constants import LEGEND_EFFECT_DURATION
from copy import deepcopy
from collections import defaultdict
import random


class LegendEffect:
    _registry = None  # Class-level shared registry

    def __init__(self, stats_obj: StatsCollector, weapon_obj: Weapon, attack_sim: AttackSimulator):
        self.stats = stats_obj
        self.weapon = weapon_obj
        self.attack_sim = attack_sim

        # Initialize shared registry once
        if LegendEffect._registry is None:
            LegendEffect._registry = LegendaryEffectRegistry()

        self.registry = LegendEffect._registry

        self.legend_effect_duration = LEGEND_EFFECT_DURATION  # Use constant from simulator/constants.py
        self.legend_attacks_left = 0  # Track remaining attacks that benefit from legendary property

        # State for persistent effects
        self._current_ab_bonus = 0
        self._current_ac_reduction = 0

    def legend_proc(self, legend_proc_identifier: float):
        roll_threshold = 100 - (legend_proc_identifier * 100)  # Roll above it triggers the property
        legend_roll = random.randint(1, 100)
        if legend_roll > roll_threshold:
            self.stats.legend_procs += 1
            self.legend_attacks_left = self.attack_sim.attacks_per_round * self.legend_effect_duration  # Reset/apply duration (5 rounds)
            return True
        else:
            return False

    @property
    def ab_bonus(self) -> int:
        """Get current AB bonus from legendary effect."""
        return getattr(self, '_current_ab_bonus', 0)

    @property
    def ac_reduction(self) -> int:
        """Get current AC reduction from legendary effect."""
        return getattr(self, '_current_ac_reduction', 0)

    def get_legend_damage(self, legend_dict: dict, crit_multiplier: int):
        """Calculate legendary damage with two-phase effect system.

        Phase 1 - On Proc: Apply burst + persistent effects
        Phase 2 - During Window: Apply only persistent effects

        Returns:
            legend_dict_sums: Dict of burst damage by type
            legend_dmg_common: List of persistent common damage
            legend_imm_factors: Dict of persistent immunity factors
        """
        legend_dict_sums = defaultdict(int)
        legend_dmg_common = []
        legend_imm_factors = {}

        # Reset persistent effects
        self._current_ab_bonus = 0
        self._current_ac_reduction = 0

        if not legend_dict:  # If the dict is empty, return empty results
            return dict(legend_dict_sums), legend_dmg_common, legend_imm_factors

        proc = legend_dict.get('proc')
        custom_effect = self.registry.get_effect(self.weapon.name_purple)

        if not custom_effect:
            # No registered effect - weapon has no legendary property
            return dict(legend_dict_sums), legend_dmg_common, legend_imm_factors

        # Check proc type and phase
        if isinstance(proc, (int, float)):  # Legendary property triggers on-hit, by percentage
            if self.legend_proc(proc):  # Phase 1: Just procced
                burst, persistent = custom_effect.apply(
                    legend_dict, self.stats, crit_multiplier, self.attack_sim)
                # Apply BOTH burst and persistent
                self._apply_effects(burst, persistent, legend_dict_sums,
                                  legend_dmg_common, legend_imm_factors)

            elif self.legend_attacks_left > 0:  # Phase 2: During window
                self.legend_attacks_left -= 1
                burst, persistent = custom_effect.apply(
                    legend_dict, self.stats, crit_multiplier, self.attack_sim)
                # Apply ONLY persistent (ignore burst)
                self._apply_effects({}, persistent, legend_dict_sums,
                                  legend_dmg_common, legend_imm_factors)

        elif isinstance(proc, str) and crit_multiplier > 1:  # Legendary property triggers on crit-hit
            self.stats.legend_procs += 1
            burst, persistent = custom_effect.apply(
                legend_dict, self.stats, crit_multiplier, self.attack_sim)
            self._apply_effects(burst, persistent, legend_dict_sums,
                              legend_dmg_common, legend_imm_factors)

        # Convert back to regular dict before returning
        return dict(legend_dict_sums), legend_dmg_common, legend_imm_factors

    def _apply_effects(self, burst, persistent, legend_dict_sums,
                       legend_dmg_common, legend_imm_factors):
        """Helper to apply burst and persistent effects.

        Args:
            burst: Dict with 'damage_sums' key
            persistent: Dict with 'common_damage', 'immunity_factors', 'ab_bonus', 'ac_reduction' keys
            legend_dict_sums: defaultdict to accumulate damage
            legend_dmg_common: List to extend with common damage
            legend_imm_factors: Dict to update with immunity factors
        """
        # Apply burst damage
        for dmg_type, dmg_value in burst.get('damage_sums', {}).items():
            legend_dict_sums[dmg_type] += dmg_value

        # Apply persistent effects
        if persistent.get('common_damage'):
            legend_dmg_common.extend(persistent['common_damage'])

        legend_imm_factors.update(persistent.get('immunity_factors', {}))

        # Store for property access
        self._current_ab_bonus = persistent.get('ab_bonus', 0)
        self._current_ac_reduction = persistent.get('ac_reduction', 0)
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/simulator/test_legend_effect.py -v`

Expected: All PASS

**Step 5: Run all tests to verify no regressions**

Run: `pytest tests/ -v`

Expected: All tests PASS

**Step 6: Commit**

```bash
git add simulator/legend_effect.py tests/simulator/test_legend_effect.py
git commit -m "refactor: implement two-phase legendary effect system in LegendEffect

- Remove ab_bonus() and ac_reduction() methods, replace with properties
- Remove get_immunity_factors() method (handled by effect classes)
- Remove default fallback behavior (registry-only now)
- Implement two-phase system: burst on proc, persistent during window
- Add _apply_effects() helper method
- Use LEGEND_EFFECT_DURATION constant

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Final Integration Testing

**Files:**
- Test: Run full test suite and benchmarks

**Step 1: Run full test suite**

Run: `pytest tests/ -v`

Expected: All tests PASS (425+ tests)

**Step 2: Run detailed benchmark**

Run: `python scripts/benchmark_detailed.py`

Expected: Completes without errors for all weapons (Spear, Greataxe, Heavy Flail, Scythe, Halberd)

**Step 3: Run simple benchmark**

Run: `python scripts/benchmark_simulation.py`

Expected: Completes successfully with performance metrics

**Step 4: Manual smoke test (optional)**

Run: `python app.py`

Open browser to http://127.0.0.1:8050

Test with Heavy Flail, Darts, Light Flail - should simulate without errors

**Step 5: Final commit**

```bash
git commit --allow-empty -m "chore: legendary effects cleanup complete - all tests pass

- Fixed critical bug in common_damage format handling
- Refactored to registry-only architecture (no backward compatibility)
- Implemented two-phase effect system (burst vs persistent)
- Created 4 new effect classes (BurstDamage, PerfectStrike, Sunder, Inconsequence)
- Updated 2 existing effects (HeavyFlail, CrushingBlow)
- Registered all 36+ legendary weapons
- All 425+ tests pass
- Benchmark runs without errors

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Implementation Complete

**Total Tasks**: 10
**Files Created**: 5 new effect classes, 1 new test file
**Files Modified**: 7 (damage_simulator, legend_effect, base, registry, __init__, 2 existing effects)
**Tests Added**: 10+ new tests
**Breaking Changes**: None (external interface unchanged)

All work completed on branch: `refactor/app-wide-refactoring`

**Next Steps**: Ready for testing and merge to main!
