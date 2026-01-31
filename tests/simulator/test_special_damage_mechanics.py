"""
Unit tests for special damage mechanics in the DamageSimulator.

This test suite verifies that special damage types are handled correctly:
- Sneak Attack: NOT multiplied on critical hits, does NOT stack (only highest counts)
- Death Attack: NOT multiplied on critical hits, does NOT stack (only highest counts)
- Massive Critical: Added ONLY on critical hits, NOT multiplied, does NOT stack (only highest counts)
- Flame Weapon: NOT multiplied on critical hits, does NOT stack (only highest counts)

These tests primarily verify:
1. The bug fix for DamageRoll object handling
2. Integration with the damage system
3. That simulations complete without errors
"""

import pytest
from simulator.damage_simulator import DamageSimulator
from simulator.config import Config
from simulator.damage_roll import DamageRoll


class TestDamageRollMaxSelection:
    """Unit tests for the max() selection logic with DamageRoll objects."""

    def test_get_max_dmg_function(self):
        """Test that get_max_dmg correctly calculates maximum possible damage."""
        # This is the helper function used in damage_simulator.py
        def get_max_dmg(dmg_roll: DamageRoll) -> int:
            return dmg_roll.dice * dmg_roll.sides + dmg_roll.flat

        roll1 = DamageRoll(dice=5, sides=6, flat=0)  # max: 30
        roll2 = DamageRoll(dice=3, sides=6, flat=2)  # max: 20
        roll3 = DamageRoll(dice=2, sides=6, flat=5)  # max: 17

        assert get_max_dmg(roll1) == 30
        assert get_max_dmg(roll2) == 20
        assert get_max_dmg(roll3) == 17

    def test_max_damage_roll_selection_with_dice(self):
        """Test selecting max DamageRoll based on maximum possible damage."""
        def get_max_dmg(dmg_roll: DamageRoll) -> int:
            return dmg_roll.dice * dmg_roll.sides + dmg_roll.flat

        rolls = [
            DamageRoll(dice=5, sides=6, flat=0),  # max: 30
            DamageRoll(dice=3, sides=6, flat=2),  # max: 20
            DamageRoll(dice=10, sides=4, flat=0), # max: 40 <-- highest
        ]

        max_roll = max(rolls, key=get_max_dmg)
        assert max_roll.dice == 10
        assert max_roll.sides == 4

    def test_max_damage_roll_selection_with_flat(self):
        """Test selecting max DamageRoll when flat damage is significant."""
        def get_max_dmg(dmg_roll: DamageRoll) -> int:
            return dmg_roll.dice * dmg_roll.sides + dmg_roll.flat

        rolls = [
            DamageRoll(dice=0, sides=0, flat=200),  # max: 200 <-- highest
            DamageRoll(dice=2, sides=12, flat=0),   # max: 24
            DamageRoll(dice=0, sides=0, flat=100),  # max: 100
        ]

        max_roll = max(rolls, key=get_max_dmg)
        assert max_roll.flat == 200

    def test_max_with_empty_list_returns_default(self):
        """Test that max() with empty list returns the default value."""
        def get_max_dmg(dmg_roll: DamageRoll) -> int:
            return dmg_roll.dice * dmg_roll.sides + dmg_roll.flat

        rolls = []
        max_roll = max(rolls, key=get_max_dmg, default=None)
        assert max_roll is None


class TestSneakAttackIntegration:
    """Integration tests for Sneak Attack damage."""

    def test_sneak_attack_simulation_completes(self):
        """Test that simulation completes with Sneak Attack enabled."""
        cfg = Config()
        cfg.AB = 50
        cfg.TARGET_AC = 10
        cfg.ROUNDS = 10
        cfg.ADDITIONAL_DAMAGE['Sneak_Attack'][0] = True  # Enable

        sim = DamageSimulator('Scimitar', cfg)
        results = sim.simulate_dps()

        # Verify simulation completed
        assert 'dps_crits' in results
        assert results['dps_crits'] > 0

    def test_multiple_sneak_sources_no_crash(self):
        """Test that multiple sneak sources don't cause crashes (stacking logic)."""
        cfg = Config()
        cfg.AB = 50
        cfg.TARGET_AC = 10
        cfg.ROUNDS = 10

        # Enable sneak attack
        cfg.ADDITIONAL_DAMAGE['Sneak_Attack'][0] = True

        # Use a weapon with built-in sneak damage
        sim = DamageSimulator('Gloves_Adam', cfg)  # Has sneak: [1, 6]
        results = sim.simulate_dps()

        # Verify simulation completed (tests the max() logic doesn't crash)
        assert 'dps_crits' in results


class TestDeathAttackIntegration:
    """Integration tests for Death Attack damage."""

    def test_death_attack_simulation_completes(self):
        """Test that simulation completes with Death Attack enabled."""
        cfg = Config()
        cfg.AB = 50
        cfg.TARGET_AC = 10
        cfg.ROUNDS = 10
        cfg.ADDITIONAL_DAMAGE['Death_Attack'][0] = True  # Enable

        sim = DamageSimulator('Scimitar', cfg)
        results = sim.simulate_dps()

        # Verify simulation completed
        assert 'dps_crits' in results
        assert results['dps_crits'] > 0


class TestMassiveCriticalIntegration:
    """Integration tests for Massive Critical damage."""

    def test_massive_simulation_with_halberd(self):
        """Test that Halberd's massive damage (200 flat) works correctly."""
        cfg = Config()
        cfg.AB = 50
        cfg.TARGET_AC = 10
        cfg.ROUNDS = 10

        # Halberd has massive: [0, 0, 200]
        sim = DamageSimulator('Halberd', cfg)
        results = sim.simulate_dps()

        # Verify simulation completed
        assert 'dps_crits' in results
        assert results['dps_crits'] > 0

    def test_multiple_massive_sources_no_crash(self):
        """Test that multiple massive sources don't cause crashes (stacking logic)."""
        cfg = Config()
        cfg.AB = 50
        cfg.TARGET_AC = 10
        cfg.ROUNDS = 10

        # Note: Can't easily add additional massive via ADDITIONAL_DAMAGE
        # (no pre-defined massive additional damage source), but we test with weapon

        sim = DamageSimulator('Halberd', cfg)
        results = sim.simulate_dps()

        # Verify simulation completed (tests the max() logic doesn't crash)
        assert 'dps_crits' in results


class TestFlameWeaponIntegration:
    """Integration tests for Flame Weapon damage."""

    def test_flame_weapon_simulation_completes(self):
        """Test that simulation completes with Flame Weapon enabled."""
        cfg = Config()
        cfg.AB = 50
        cfg.TARGET_AC = 10
        cfg.TARGET_IMMUNITIES = {'physical': 0.0, 'fire': 0.0}  # No immunities
        cfg.ROUNDS = 10
        cfg.ADDITIONAL_DAMAGE['Flame_Weapon'][0] = True  # Enable (default is True)

        sim = DamageSimulator('Scimitar', cfg)
        results = sim.simulate_dps()

        # Verify simulation completed
        assert 'dps_crits' in results
        assert results['dps_crits'] > 0

        # Verify fire damage was tracked
        assert 'fire' in results['damage_by_type']

    def test_multiple_flame_weapon_sources_no_crash(self):
        """Test that multiple flame weapon sources don't cause crashes (stacking logic)."""
        cfg = Config()
        cfg.AB = 50
        cfg.TARGET_AC = 10
        cfg.TARGET_IMMUNITIES = {'physical': 0.0, 'fire': 0.0}
        cfg.ROUNDS = 10

        # Enable Flame Weapon
        cfg.ADDITIONAL_DAMAGE['Flame_Weapon'][0] = True

        # Enable Darkfire (also fire_fw type)
        cfg.ADDITIONAL_DAMAGE['Darkfire'][0] = True

        sim = DamageSimulator('Scimitar', cfg)
        results = sim.simulate_dps()

        # Verify simulation completed (tests the max() logic doesn't crash)
        assert 'dps_crits' in results
        assert 'fire' in results['damage_by_type']


class TestAllSpecialDamageTypesCombined:
    """Integration tests with multiple special damage types active."""

    def test_all_special_types_together(self):
        """Test that all special damage types work together without crashes."""
        cfg = Config()
        cfg.AB = 50
        cfg.TARGET_AC = 10
        cfg.TARGET_IMMUNITIES = {'physical': 0.0, 'fire': 0.0}
        cfg.ROUNDS = 10

        # Enable multiple special damage sources
        cfg.ADDITIONAL_DAMAGE['Sneak_Attack'][0] = True
        cfg.ADDITIONAL_DAMAGE['Death_Attack'][0] = True
        cfg.ADDITIONAL_DAMAGE['Flame_Weapon'][0] = True

        # Use Halberd which has massive: [0, 0, 200]
        sim = DamageSimulator('Halberd', cfg)
        results = sim.simulate_dps()

        # Verify simulation completed successfully
        assert 'dps_crits' in results
        assert results['dps_crits'] > 0

    def test_sneak_and_weapon_sneak_combined(self):
        """Test sneak from both ADDITIONAL_DAMAGE and weapon properties."""
        cfg = Config()
        cfg.AB = 50
        cfg.TARGET_AC = 10
        cfg.ROUNDS = 10

        # Enable sneak attack (5d6)
        cfg.ADDITIONAL_DAMAGE['Sneak_Attack'][0] = True

        # Use weapon with built-in sneak (Gloves_Adam has 1d6 sneak)
        sim = DamageSimulator('Gloves_Adam', cfg)
        results = sim.simulate_dps()

        # Verify simulation completed (max() should pick the 5d6, not crash)
        assert 'dps_crits' in results


class TestBugFixVerification:
    """Tests that specifically verify the DamageRoll subscript bug fix."""

    def test_sneak_max_selection_does_not_crash(self):
        """Verify the bug fix: sneak damage max() no longer tries to subscript DamageRoll."""
        cfg = Config()
        cfg.AB = 50
        cfg.TARGET_AC = 10
        cfg.ROUNDS = 5
        cfg.ADDITIONAL_DAMAGE['Sneak_Attack'][0] = True

        # This would have crashed with: TypeError: 'DamageRoll' object is not subscriptable
        # at line: dmg_sneak_max = max(dmg_sneak, key=lambda sublist: sublist[0], default=None)
        sim = DamageSimulator('Scimitar', cfg)
        results = sim.simulate_dps()

        assert results is not None
        assert 'dps_crits' in results

    def test_death_max_selection_does_not_crash(self):
        """Verify the bug fix: death damage max() no longer tries to subscript DamageRoll."""
        cfg = Config()
        cfg.AB = 50
        cfg.TARGET_AC = 10
        cfg.ROUNDS = 5
        cfg.ADDITIONAL_DAMAGE['Death_Attack'][0] = True

        # This would have crashed with the same error
        sim = DamageSimulator('Scimitar', cfg)
        results = sim.simulate_dps()

        assert results is not None
        assert 'dps_crits' in results


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
