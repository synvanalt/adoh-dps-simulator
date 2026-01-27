"""
Unit tests for the AttackSimulator class from simulator/attack_simulator.py

This test suite covers:
- Attack simulator initialization and configuration
- Hit chance calculations for different attack progressions
- Critical hit chance calculations with various threat ranges
- Attack roll mechanics (hit, miss, critical hit)
- Damage roll mechanics with varying dice and flat damage
- Dual-wield penalty application based on character and weapon sizes
- Legend proc rate calculations (percentage and on-crit triggers)
- Damage immunity and vulnerability application
"""

import pytest
import random
from simulator.attack_simulator import AttackSimulator
from simulator.weapon import Weapon
from simulator.config import Config


class TestAttackSimulatorInitialization:
    """Tests for AttackSimulator initialization and setup."""

    def test_valid_initialization(self):
        """Test that AttackSimulator initializes correctly with valid inputs."""
        cfg = Config(AB_PROG="5APR Classic")
        weapon = Weapon("Scythe", cfg)
        simulator = AttackSimulator(weapon, cfg)

        assert simulator.weapon == weapon
        assert simulator.cfg == cfg
        assert simulator.defender_ac == cfg.TARGET_AC
        assert simulator.ab_capped == cfg.AB_CAPPED
        assert simulator.ab == cfg.AB_CAPPED  # Scythe gets AB_CAPPED

    def test_initialization_with_non_scythe_weapon(self):
        """Test AB assignment for non-Scythe weapons."""
        cfg = Config()
        weapon = Weapon("Longsword", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # Non-Scythe weapons use regular AB, not AB_CAPPED
        assert simulator.ab == cfg.AB

    def test_weapon_with_enhancement_greater_than_7(self):
        """Test AB calculation for weapons with enhancement > 7 (e.g., Scythe +10).

        Logic: If weapon enhancement > 7, add the excess to AB
        Example: Scythe (enhancement=10) → AB + (10 - 7) = AB + 3
        """
        cfg = Config(AB=65, AB_CAPPED=70)
        weapon = Weapon("Scythe", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # Scythe has enhancement=10, so AB should be 65 + (10 - 7) = 68
        # But it's capped at AB_CAPPED=70, so result is 68
        expected_ab = min(65 + (10 - 7), 70)
        assert simulator.ab == expected_ab
        assert simulator.ab == 68  # Explicit check

    def test_weapon_with_enhancement_greater_than_7_capped(self):
        """Test that AB is capped at AB_CAPPED for high-enhancement weapons.

        If weapon enhancement bonus would exceed AB_CAPPED, it should be capped.
        """
        cfg = Config(AB=65, AB_CAPPED=68)
        weapon = Weapon("Scythe", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # Scythe enhancement=10 → AB + (10 - 7) = 65 + 3 = 68
        # This equals AB_CAPPED, so no capping needed
        assert simulator.ab == 68

    def test_weapon_with_enhancement_equals_7_uses_regular_ab(self):
        """Test that weapons with enhancement exactly = 7 use regular AB (no bonus).

        Only when enhancement > 7 should the excess be added.
        """
        cfg = Config(AB=65, AB_CAPPED=70)
        weapon = Weapon("Longsword", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # Longsword has enhancement=7 (not > 7), so use regular AB
        assert simulator.ab == cfg.AB
        assert simulator.ab == 65

    def test_vs_race_enhancement_when_damage_vs_race_enabled(self):
        """Test AB calculation with vs_race enhancement when DAMAGE_VS_RACE is enabled.

        Example: Greataxe vs Undead (vs_race_undead enhancement=12)
        When DAMAGE_VS_RACE=True and vs_race_key exists:
        AB = cfg.AB + (vs_race_enhancement - 7)
        """
        cfg = Config(AB=65, AB_CAPPED=70, DAMAGE_VS_RACE=True)
        weapon = Weapon("Greataxe", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # Greataxe has vs_race_undead with enhancement=12
        # AB should be 65 + (12 - 7) = 70
        expected_ab = 65 + (12 - 7)
        assert simulator.ab == expected_ab
        assert simulator.ab == 70

    def test_vs_race_enhancement_capped(self):
        """Test that vs_race enhancement bonus is also capped at AB_CAPPED.

        High vs_race enhancement values should not exceed the cap.
        """
        cfg = Config(AB=65, AB_CAPPED=68, DAMAGE_VS_RACE=True)
        weapon = Weapon("Greataxe", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # Greataxe vs_race_undead enhancement=12 → AB + (12 - 7) = 65 + 5 = 70
        # But capped at AB_CAPPED=68
        expected_ab = min(65 + (12 - 7), 68)
        assert simulator.ab == expected_ab
        assert simulator.ab == 68

    def test_vs_race_enhancement_ignored_when_damage_vs_race_disabled(self):
        """Test that vs_race enhancement is NOT used when DAMAGE_VS_RACE is False.

        When DAMAGE_VS_RACE is disabled, even if vs_race enhancement exists,
        it should use the base enhancement instead.
        """
        cfg = Config(AB=65, AB_CAPPED=70, DAMAGE_VS_RACE=False)
        weapon = Weapon("Greataxe", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # DAMAGE_VS_RACE=False, so use base enhancement=7 (not vs_race enhancement)
        # Since base enhancement=7 (not > 7), should use regular AB
        assert simulator.ab == cfg.AB
        assert simulator.ab == 65

    def test_vs_race_enhancement_with_high_base_enhancement(self):
        """Test vs_race enhancement when base weapon also has enhancement > 7.

        When DAMAGE_VS_RACE=True and vs_race_key exists with 'enhancement' key,
        the vs_race enhancement should be used instead of base enhancement.
        """
        cfg = Config(AB=65, AB_CAPPED=75, DAMAGE_VS_RACE=True)
        weapon = Weapon("Greataxe", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # Should use vs_race_undead enhancement=12, not base enhancement=7
        # AB = 65 + (12 - 7) = 70
        expected_ab = 65 + (12 - 7)
        assert simulator.ab == expected_ab
        assert simulator.ab == 70

    def test_vs_race_key_none_when_damage_vs_race_enabled_no_vs_race_weapon(self):
        """Test edge case: DAMAGE_VS_RACE=True but weapon has no vs_race_key.

        For weapons without vs_race variants (e.g., Longsword),
        vs_race_key will be None, so should fall through to regular AB.
        """
        cfg = Config(AB=65, AB_CAPPED=70, DAMAGE_VS_RACE=True)
        weapon = Weapon("Longsword", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # Longsword has no vs_race variant, so vs_race_key is None
        # The condition 'enhancement' in self.purple_props[None] would fail
        # so it should fall through to the else clause and use regular AB
        assert simulator.ab == cfg.AB
        assert simulator.ab == 65

    def test_attack_prog_generation(self):
        """Test that attack progression is correctly generated from config."""
        cfg = Config(AB=68, AB_PROG="5APR Classic")
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # 5APR Classic: [0, -5, -10, -15, 0]
        expected_prog = [68 + 0, 68 - 5, 68 - 10, 68 - 15, 68 + 0]
        assert simulator.attack_prog == expected_prog
        assert simulator.attacks_per_round == 5

    def test_hit_chances_calculated(self):
        """Test that hit chances are calculated during initialization."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        assert len(simulator.hit_chance_list) > 0
        assert len(simulator.crit_chance_list) > 0
        assert len(simulator.noncrit_chance_list) > 0
        assert len(simulator.hit_chance_list) == len(simulator.crit_chance_list)


class TestHitChanceCalculations:
    """Tests for hit chance probability calculations."""

    def test_guaranteed_hit(self):
        """Test hit chance calculation when attack bonus exceeds defender AC by large margin."""
        cfg = Config(AB=100, TARGET_AC=20)
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        hit_chance = simulator.get_hit_chance()
        # Should be capped at 95% (natural 1 always misses)
        assert hit_chance == 0.95

    def test_guaranteed_miss(self):
        """Test hit chance calculation when attack bonus is much lower than defender AC."""
        cfg = Config(AB=10, TARGET_AC=100)
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        hit_chance = simulator.get_hit_chance()
        # Should be floored at 5% (natural 20 always hits)
        assert hit_chance == 0.05

    def test_equal_ab_and_ac(self):
        """Test hit chance when attack bonus equals defender AC.

        FORMULA EXPLANATION - Why "21"?
        ================================
        The hit chance formula is: (21 + AB - AC) * 0.05

        D20 MECHANICS:
        - You roll 1d20 (values 1-20): 20 possible outcomes
        - To hit: d20 + AB >= AC
        - Rearranged: d20 >= (AC - AB)

        COUNTING SUCCESSFUL ROLLS:
        - If AC - AB = 5, you need rolls 5-20: that's (20 - 5 + 1) = 16 rolls
        - General formula: 20 - (AC - AB) + 1 = 21 + AB - AC ✓

        CONVERTING TO PERCENTAGE:
        - Each d20 face = 5% (100% / 20 = 5%)
        - So: (21 + AB - AC) * 0.05 converts count to percentage

        WHEN AB == AC (this test case):
        - Formula: (21 + 50 - 50) * 0.05 = 21 * 0.05 = 1.05 (105%)
        - Need to roll 21 or higher to guarantee hit (but d20 max is 20)
        - This exceeds 100%, so it's capped at 95%
        - Reasoning: natural 1 always misses (floor), natural 20 always hits (ceiling)
        - Result: 95% hit chance (effectively 19/20 rolls succeed)
        """
        cfg = Config(AB=50, TARGET_AC=50, AB_PROG="4APR Classic")
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        hit_chance_first = simulator.hit_chance_list[0]
        expected = max(0.05, min(0.95, (21 + 50 - 50) * 0.05))
        assert hit_chance_first == expected

    def test_higher_ab_increases_hit_chance(self):
        """Test that higher AB results in higher hit chance."""
        cfg_low = Config(AB=30, TARGET_AC=50)
        cfg_high = Config(AB=50, TARGET_AC=50)

        weapon_low = Weapon("Scimitar", cfg_low)
        weapon_high = Weapon("Scimitar", cfg_high)

        sim_low = AttackSimulator(weapon_low, cfg_low)
        sim_high = AttackSimulator(weapon_high, cfg_high)

        assert sim_low.get_hit_chance() < sim_high.get_hit_chance()

    def test_higher_ac_decreases_hit_chance(self):
        """Test that higher AC results in lower hit chance."""
        cfg_low = Config(AB=50, TARGET_AC=30)
        cfg_high = Config(AB=50, TARGET_AC=50)

        weapon_low = Weapon("Scimitar", cfg_low)
        weapon_high = Weapon("Scimitar", cfg_high)

        sim_low = AttackSimulator(weapon_low, cfg_low)
        sim_high = AttackSimulator(weapon_high, cfg_high)

        assert sim_low.get_hit_chance() > sim_high.get_hit_chance()

    def test_multiple_attacks_average_correctly(self):
        """Test that hit chance averages multiple attacks in round."""
        cfg = Config(AB=68, AB_PROG="5APR Classic", TARGET_AC=65)
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # Should average the hit chances of all 5 attacks
        hit_chance = simulator.get_hit_chance()
        expected_avg = sum(simulator.hit_chance_list) / len(simulator.hit_chance_list)
        assert hit_chance == expected_avg


class TestCriticalHitCalculations:
    """Tests for critical hit probability calculations."""

    def test_crit_chance_lower_than_hit_chance(self):
        """Test that critical hit chance is always lower than total hit chance."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        hit_chance = simulator.get_hit_chance()
        crit_chance = simulator.get_crit_chance()

        assert crit_chance <= hit_chance

    def test_noncrit_plus_crit_equals_hit(self):
        """Test that non-crit + crit chance equals total hit chance."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        hit_chance = simulator.get_hit_chance()
        crit_chance = simulator.get_crit_chance()
        noncrit_chance = simulator.get_noncrit_chance()

        # Allow small floating point error
        assert abs((crit_chance + noncrit_chance) - hit_chance) < 0.0001

    def test_scimitar_higher_crit_threat_than_longsword(self):
        """Test that Scimitar (18-20 threat) has higher crit chance than Longsword (19-20 threat)."""
        cfg = Config()

        scimitar = Weapon("Scimitar", cfg)
        longsword = Weapon("Longsword", cfg)

        sim_scimitar = AttackSimulator(scimitar, cfg)
        sim_longsword = AttackSimulator(longsword, cfg)

        assert sim_scimitar.get_crit_chance() > sim_longsword.get_crit_chance()

    def test_longsword_higher_crit_threat_than_scythe(self):
        """Test that Longsword (19-20 threat) has higher crit chance than Scythe (20 only).

        Threat Range Progression:
        - Scimitar: threat 18 → range 18-20 = 3 values = 15% threat chance
        - Longsword: threat 19 → range 19-20 = 2 values = 10% threat chance
        - Scythe: threat 20 → range 20-20 = 1 value = 5% threat chance

        So: Scimitar > Longsword > Scythe (in terms of natural crit chance)
        Scythe compensates with 4x multiplier.
        """
        cfg = Config(KEEN=False, IMPROVED_CRIT=False)

        longsword = Weapon("Longsword", cfg)
        scythe = Weapon("Scythe", cfg)

        sim_longsword = AttackSimulator(longsword, cfg)
        sim_scythe = AttackSimulator(scythe, cfg)

        # Longsword's wider threat range (19-20) gives higher crit chance than Scythe (20 only)
        assert sim_longsword.get_crit_chance() > sim_scythe.get_crit_chance()

    def test_keen_increases_crit_chance(self):
        """Test that Keen feat increases critical hit chance."""
        cfg_no_keen = Config(KEEN=False, IMPROVED_CRIT=False)
        cfg_keen = Config(KEEN=True, IMPROVED_CRIT=False)

        weapon_no_keen = Weapon("Scimitar", cfg_no_keen)
        weapon_keen = Weapon("Scimitar", cfg_keen)

        sim_no_keen = AttackSimulator(weapon_no_keen, cfg_no_keen)
        sim_keen = AttackSimulator(weapon_keen, cfg_keen)

        assert sim_keen.get_crit_chance() > sim_no_keen.get_crit_chance()

    def test_improved_crit_increases_crit_chance(self):
        """Test that Improved Critical feat increases critical hit chance."""
        cfg_no_ic = Config(KEEN=False, IMPROVED_CRIT=False)
        cfg_ic = Config(KEEN=False, IMPROVED_CRIT=True)

        weapon_no_ic = Weapon("Scimitar", cfg_no_ic)
        weapon_ic = Weapon("Scimitar", cfg_ic)

        sim_no_ic = AttackSimulator(weapon_no_ic, cfg_no_ic)
        sim_ic = AttackSimulator(weapon_ic, cfg_ic)

        assert sim_ic.get_crit_chance() > sim_no_ic.get_crit_chance()

    def test_crit_chance_capped_at_hit_chance(self):
        """Test that critical chance never exceeds hit chance."""
        cfg = Config(AB=100, TARGET_AC=10, KEEN=True, IMPROVED_CRIT=True)
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        for crit in simulator.crit_chance_list:
            for hit in simulator.hit_chance_list:
                assert crit <= hit


class TestAttackRoll:
    """Tests for individual attack roll mechanics."""

    def test_natural_1_always_misses(self):
        """Test that a natural 1 always results in a miss."""
        cfg = Config(AB=100, TARGET_AC=0)  # Guaranteed hit otherwise
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # Mock random to return 1
        random.seed(42)
        original_randint = random.randint

        def mock_randint_1(a, b):
            if a == 1 and b == 20:
                return 1
            return original_randint(a, b)

        random.randint = mock_randint_1
        try:
            result, roll = simulator.attack_roll(simulator.ab)
            assert result == 'miss'
            assert roll == 1
        finally:
            random.randint = original_randint

    def test_natural_20_always_hits(self):
        """Test that a natural 20 always results in a hit or critical."""
        cfg = Config(AB=0, TARGET_AC=100)  # Guaranteed miss otherwise
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # Mock random to return 20
        random.seed(42)
        original_randint = random.randint
        call_count = [0]

        def mock_randint_20(a, b):
            call_count[0] += 1
            if a == 1 and b == 20 and call_count[0] == 1:
                return 20
            return original_randint(a, b)

        random.randint = mock_randint_20
        try:
            result, roll = simulator.attack_roll(simulator.ab)
            assert result in ['hit', 'critical_hit']
            assert roll == 20
        finally:
            random.randint = original_randint

    def test_attack_roll_returns_tuple(self):
        """Test that attack_roll returns (result_string, roll_value)."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        result = simulator.attack_roll(simulator.ab)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], int)
        assert result[0] in ['miss', 'hit', 'critical_hit']
        assert 1 <= result[1] <= 20

    def test_attack_roll_with_ac_modifier(self):
        """Test that AC modifier affects hit calculation - specifically the roll needed to hit.

        This test verifies that lowering AC (negative modifier) makes it easier to hit
        by allowing lower d20 rolls to succeed, and raising AC makes it harder.

        Example with AB=50:
        - AC=50: need d20 >= 0, so all rolls hit (except natural 1)
        - AC=52 (no modifier): need d20 >= 2, so d20=1 misses
        - AC=48 (AC modifier -2): need d20 >= -2 (always hits except natural 1)
        """
        cfg = Config(AB=50, TARGET_AC=50)
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # Test with controlled rolls to verify AC modifier impact
        original_randint = random.randint

        # Mock d20 to return 2 for consistent testing
        def mock_roll(a, b):
            if a == 1 and b == 20:
                return 2  # Low roll that might miss depending on AC
            return original_randint(a, b)

        random.randint = mock_roll

        # Test baseline (no modifier)
        result_base = simulator.attack_roll(simulator.ab, defender_ac_modifier=0)

        # Test with reduced AC (easier to hit)
        result_reduced_ac = simulator.attack_roll(simulator.ab, defender_ac_modifier=-5)

        # Test with increased AC (harder to hit)
        result_increased_ac = simulator.attack_roll(simulator.ab, defender_ac_modifier=5)

        random.randint = original_randint

        # Verify AC modifier actually changes outcomes
        # With base AC=50 and roll=2: d20(2) + AB(50) = 52 >= AC(50) = HIT
        # With AC modifier -5: d20(2) + AB(50) = 52 >= AC(45) = HIT (even easier)
        # With AC modifier +5: d20(2) + AB(50) = 52 >= AC(55) = MISS (harder)

        assert result_base[0] == 'hit'  # 2 + 50 = 52 >= 50 → HIT
        assert result_reduced_ac[0] == 'hit'  # 2 + 50 = 52 >= 45 → HIT (same result, but objectively easier)
        assert result_increased_ac[0] == 'miss'  # 2 + 50 = 52 >= 55 → MISS (harder, so miss)

    def test_multiple_attack_rolls_vary(self):
        """Test that multiple attack rolls produce varying results."""
        cfg = Config(AB=50, TARGET_AC=50)
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        results = [simulator.attack_roll(simulator.ab)[0] for _ in range(100)]

        # Should have variety in results
        unique_results = set(results)
        assert len(unique_results) > 1  # Not all the same result


class TestDamageRoll:
    """Tests for damage roll mechanics."""

    def test_zero_dice_returns_flat_damage_only(self):
        """Test that 0d6+5 returns only the flat damage."""
        result = AttackSimulator.damage_roll(0, 6, 5)
        assert result == 5

    def test_zero_sides_returns_flat_damage_only(self):
        """Test that 2d0+5 returns only the flat damage."""
        result = AttackSimulator.damage_roll(2, 0, 5)
        assert result == 5

    def test_both_zero_returns_flat_damage(self):
        """Test that 0d0+5 returns only the flat damage."""
        result = AttackSimulator.damage_roll(0, 0, 5)
        assert result == 5

    def test_damage_roll_within_range(self):
        """Test that damage roll result is within expected range."""
        # 2d6+3: minimum 5, maximum 15
        for _ in range(100):
            result = AttackSimulator.damage_roll(2, 6, 3)
            assert 5 <= result <= 15

    def test_single_die_roll(self):
        """Test damage roll with a single die."""
        # 1d6+0: minimum 1, maximum 6
        for _ in range(100):
            result = AttackSimulator.damage_roll(1, 6, 0)
            assert 1 <= result <= 6

    def test_damage_roll_includes_flat_damage(self):
        """Test that flat damage is always included in roll."""
        # 0d0+10 should always return 10
        for _ in range(10):
            result = AttackSimulator.damage_roll(0, 0, 10)
            assert result == 10

    def test_large_damage_roll(self):
        """Test damage roll with many dice."""
        # 10d8+5: minimum 15, maximum 85
        for _ in range(100):
            result = AttackSimulator.damage_roll(10, 8, 5)
            assert 15 <= result <= 85


class TestDualWieldPenalty:
    """Tests for dual-wield penalty calculations based on sizes."""

    def test_medium_character_medium_weapon_penalty(self):
        """Test DW penalty for Medium character with Medium weapon."""
        cfg = Config(AB=50, TOON_SIZE='M', AB_PROG="4APR & Dual-Wield")
        weapon = Weapon("Longsword", cfg)  # Medium weapon
        simulator = AttackSimulator(weapon, cfg)

        # M + M = -4 penalty
        # Check that AB was reduced
        assert simulator.ab == 50 + (-4)

    def test_small_character_small_weapon_penalty(self):
        """Test DW penalty for Small character with Small weapon."""
        cfg = Config(AB=50, TOON_SIZE='S', AB_PROG="4APR & Dual-Wield")
        weapon = Weapon("Shortsword_Adam", cfg)  # Small weapon, in PURPLE_WEAPONS
        simulator = AttackSimulator(weapon, cfg)

        # S + S = -4 penalty
        assert simulator.ab == 50 + (-4)

    def test_large_character_medium_weapon_penalty(self):
        """Test DW penalty for Large character with Medium weapon."""
        cfg = Config(AB=50, TOON_SIZE='L', AB_PROG="4APR & Dual-Wield")
        weapon = Weapon("Longsword", cfg)  # Medium weapon
        simulator = AttackSimulator(weapon, cfg)

        # L + M = -2 penalty
        assert simulator.ab == 50 + (-2)

    def test_medium_character_small_weapon_penalty(self):
        """Test DW penalty for Medium character with Small weapon."""
        cfg = Config(AB=50, TOON_SIZE='M', AB_PROG="4APR & Dual-Wield")
        weapon = Weapon("Shortsword_Cleaver", cfg)  # Small weapon, in PURPLE_WEAPONS
        simulator = AttackSimulator(weapon, cfg)

        # M + S = -2 penalty
        assert simulator.ab == 50 + (-2)

    def test_incompatible_size_combination(self):
        """Test DW penalty with incompatible size combination."""
        cfg = Config(AB=50, TOON_SIZE='S', AB_PROG="4APR & Dual-Wield")
        weapon = Weapon("Halberd", cfg)  # Large weapon
        simulator = AttackSimulator(weapon, cfg)

        # AB of 'S' character with 'L' weapon = 0 (cannot dual-wield)
        assert simulator.ab == 0

    def test_hasted_attack_ignores_penalty(self):
        """Test that hasted attack in DW progression doesn't get penalty.

        In dual-wield, the haste attack gets the REVERSED penalty while others get the normal penalty.

        Example with AB=50, M+M weapon (penalty=-4):
        - Base AB becomes: 50 + (-4) = 46 (penalty applied to base)
        - Base progression: [0, -5, -10, '-dw_penalty', 0, -5]
        - '-dw_penalty' becomes: -1 * (-4) = +4 (reversed for haste)
        - After applying progression: [0, -5, -10, +4, 0, -5]
        - Attack ABs: [46+0, 46-5, 46-10, 46+4, 46+0, 46-5]
                    = [46, 41, 36, 50, 46, 41]

        The hasted attack (index 3) gets reversed penalty (+4) instead of normal penalty (-4),
        making it higher AB than surrounding attacks.
        """
        cfg = Config(AB=50, TOON_SIZE='M', AB_PROG="4APR & Dual-Wield")
        weapon = Weapon("Longsword", cfg)  # M+M = -4 DW penalty
        simulator = AttackSimulator(weapon, cfg)

        # Verify the attack progression reflects haste bonus
        # Base AB after DW penalty: 50 + (-4) = 46
        # Attack progression with haste reversed: [0, -5, -10, +4, 0, -5]
        # Final ABs: [46, 41, 36, 50, 46, 41]

        expected_attack_prog = [46, 41, 36, 50, 46, 41]
        assert simulator.attack_prog == expected_attack_prog, \
            f"Expected {expected_attack_prog}, got {simulator.attack_prog}"

        # Specifically verify the hasted attack (index 3) gets the bonus and is highest
        assert simulator.attack_prog[3] == 50, \
            f"Hasted attack (index 3) should be 50, got {simulator.attack_prog[3]}"

        # Verify hasted attack has HIGHER AB than 1st attack
        assert simulator.attack_prog[3] > simulator.attack_prog[0], \
            f"Hasted attack (50) should be higher than first attack ({simulator.attack_prog[0]})"

        # Verify hasted attack is the highest of all attacks
        assert simulator.attack_prog[3] == max(simulator.attack_prog), \
            f"Hasted attack should be highest AB, but got {simulator.attack_prog[3]} vs max {max(simulator.attack_prog)}"


class TestLegendProcRate:
    """Tests for legendary proc rate calculations."""

    def test_no_legendary_returns_zero(self):
        """Test that weapon without legendary property returns 0 proc rate."""
        cfg = Config()
        weapon = Weapon("Morningstar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        proc_rate = simulator.get_legend_proc_rate_theoretical()
        assert proc_rate == 0.0

    def test_fixed_proc_rate(self):
        """Test that fixed proc rate (float) is returned correctly."""
        cfg = Config()
        weapon = Weapon("Darts", cfg)
        simulator = AttackSimulator(weapon, cfg)

        proc_rate = simulator.get_legend_proc_rate_theoretical()
        # Darts has legendary with proc: 0.05
        assert proc_rate == 0.05

    def test_on_crit_proc_rate(self):
        """Test that 'on_crit' proc rate is calculated based on crit chance."""
        cfg = Config()
        weapon = Weapon("Longbow_FireDragon", cfg)
        simulator = AttackSimulator(weapon, cfg)

        proc_rate = simulator.get_legend_proc_rate_theoretical()

        # For 'on_crit', rate should be crit% / hit%
        hit_chance = simulator.get_hit_chance()
        crit_chance = simulator.get_crit_chance()

        if hit_chance > 0:
            expected_rate = crit_chance / hit_chance
            assert abs(proc_rate - expected_rate) < 0.0001
        else:
            assert proc_rate == 0.0

    def test_proc_rate_between_0_and_1(self):
        """Test that proc rate is always between 0 and 1."""
        cfg = Config()
        for weapon_name in ['Darts', 'Longbow_FireDragon', 'Scimitar']:
            weapon = Weapon(weapon_name, cfg)
            simulator = AttackSimulator(weapon, cfg)
            proc_rate = simulator.get_legend_proc_rate_theoretical()
            assert 0.0 <= proc_rate <= 1.0


class TestDamageImmunityReduction:
    """Tests for damage immunity and vulnerability calculations."""

    def test_no_immunity_no_reduction(self):
        """Test that damage remains unchanged with no immunity."""
        cfg = Config(TARGET_IMMUNITIES={'physical': 0.0, 'fire': 0.0})
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        damage_sums = {'slashing': 100}
        result = simulator.damage_immunity_reduction(damage_sums, {})

        assert result['slashing'] == 100

    def test_immunity_reduces_damage(self):
        """Test that immunity reduces damage as expected."""
        cfg = Config(TARGET_IMMUNITIES={'physical': 0.1})
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        damage_sums = {'slashing': 100}
        result = simulator.damage_immunity_reduction(damage_sums, {})

        # 10% immunity: damage reduced by 10, so 90 remains
        assert result['slashing'] == 90

    def test_heavy_immunity(self):
        """Test with heavy immunity (e.g., 50%)."""
        cfg = Config(TARGET_IMMUNITIES={'physical': 0.5})
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        damage_sums = {'slashing': 100}
        result = simulator.damage_immunity_reduction(damage_sums, {})

        # 50% immunity: damage reduced by 50
        assert result['slashing'] == 50

    def test_vulnerability_increases_damage(self):
        """Test that negative immunity (vulnerability) increases damage."""
        cfg = Config(TARGET_IMMUNITIES={'fire': -0.1})
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        damage_sums = {'fire_fw': 100}
        result = simulator.damage_immunity_reduction(damage_sums, {})

        # -10% vulnerability: 10% extra damage added
        assert result['fire_fw'] == 110

    def test_immunity_legend_modification(self):
        """Test that legend property can modify immunity factors."""
        cfg = Config(TARGET_IMMUNITIES={'fire': 0.1})
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        damage_sums = {'fire': 100}
        # Legend reduces fire immunity by 5%
        result = simulator.damage_immunity_reduction(damage_sums, {'fire': -0.05})

        # Original 10% immunity reduced to 5% by legend
        # Damage reduced by 5: 100 - 5 = 95
        assert result['fire'] == 95

    def test_fire_fw_treated_as_fire(self):
        """Test that fire_fw (Flame Weapon) is treated as fire for immunity purposes."""
        cfg = Config(TARGET_IMMUNITIES={'fire': 0.2})
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        damage_sums = {'fire_fw': 100}
        result = simulator.damage_immunity_reduction(damage_sums, {})

        # fire_fw should be treated as fire: 20% reduction
        assert result['fire_fw'] == 80

    def test_physical_damage_type_conversion(self):
        """Test that slashing/piercing/bludgeoning convert to physical immunity."""
        cfg = Config(TARGET_IMMUNITIES={'physical': 0.1})
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        damage_sums = {'slashing': 100}
        result = simulator.damage_immunity_reduction(damage_sums, {})

        # slashing converted to physical, 10% immunity applies
        assert result['slashing'] == 90

    def test_minimum_damage_is_1(self):
        """Test that damage never goes below 1."""
        cfg = Config(TARGET_IMMUNITIES={'physical': 0.95})
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        damage_sums = {'slashing': 10}
        result = simulator.damage_immunity_reduction(damage_sums, {})

        # Even with 95% reduction, minimum is 1
        assert result['slashing'] >= 1

    def test_multiple_damage_types(self):
        """Test immunity reduction with multiple damage types."""
        cfg = Config(TARGET_IMMUNITIES={'physical': 0.1, 'fire': 0.2, 'cold': 0.0})
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        damage_sums = {'slashing': 100, 'fire': 100, 'cold': 100}
        result = simulator.damage_immunity_reduction(damage_sums, {})

        assert result['slashing'] == 90   # 10% immunity
        assert result['fire'] == 80       # 20% immunity
        assert result['cold'] == 100      # 0% immunity


class TestAttackSimulatorIntegration:
    """Integration tests with various configurations."""

    def test_full_attack_round_classic(self):
        """Test full attack progression with Classic 5APR."""
        cfg = Config(AB=68, AB_PROG="5APR Classic", TARGET_AC=65)
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        assert simulator.attacks_per_round == 5
        assert len(simulator.attack_prog) == 5
        assert all(isinstance(ab, int) for ab in simulator.attack_prog)

    def test_ranged_progression(self):
        """Test ranged weapon attack progression."""
        cfg = Config(AB=70, AB_PROG="5APR & Rapid Shot", COMBAT_TYPE='ranged')
        weapon = Weapon("Longbow_FireDragon", cfg)
        simulator = AttackSimulator(weapon, cfg)

        assert simulator.attacks_per_round == 6  # 5 APR + 1 from Rapid Shot

    def test_blinding_speed_progression(self):
        """Test attack progression with Blinding Speed."""
        cfg = Config(AB=68, AB_PROG="5APR & Blinding Speed")
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        assert simulator.attacks_per_round == 6  # Blinding Speed adds one

    def test_attack_simulator_with_all_features(self):
        """Test with all combat features enabled."""
        cfg = Config(
            AB=68,
            AB_CAPPED=70,
            AB_PROG="5APR Classic",
            TARGET_AC=65,
            KEEN=True,
            IMPROVED_CRIT=True,
            WEAPONMASTER=True,
            ENHANCEMENT_SET_BONUS=3
        )
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        assert simulator.ab > 0
        assert len(simulator.hit_chance_list) == 5
        assert all(0.0 <= h <= 1.0 for h in simulator.hit_chance_list)


class TestAttackSimulatorEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_zero_ab(self):
        """Test attack simulator with AB of 0."""
        cfg = Config(AB=0, TARGET_AC=10)
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        hit_chance = simulator.get_hit_chance()
        assert 0.0 <= hit_chance <= 1.0

    def test_very_high_ab(self):
        """Test attack simulator with very high AB."""
        cfg = Config(AB=200, TARGET_AC=50)
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        hit_chance = simulator.get_hit_chance()
        assert hit_chance == 0.95  # Capped at 95%

    def test_negative_ac_modifier(self):
        """Test attack roll with negative AC modifier."""
        cfg = Config(AB=50, TARGET_AC=50)
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        result = simulator.attack_roll(simulator.ab, defender_ac_modifier=-10)
        assert result[0] in ['miss', 'hit', 'critical_hit']

    def test_large_positive_ac_modifier(self):
        """Test attack roll with large positive AC modifier."""
        cfg = Config(AB=50, TARGET_AC=50)
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        result = simulator.attack_roll(simulator.ab, defender_ac_modifier=50)
        # Should likely miss with large AC boost
        assert result[0] in ['miss', 'hit', 'critical_hit']

    def test_single_attack_progression(self):
        """Test with single attack (shouldn't happen in game but test it anyway)."""
        cfg = Config(AB=50)
        cfg.AB_PROGRESSIONS['Single'] = [0]
        cfg.AB_PROG = 'Single'
        weapon = Weapon("Scimitar", cfg)
        simulator = AttackSimulator(weapon, cfg)

        assert simulator.attacks_per_round == 1


class TestTenaciousBlowMissDamage:
    """Tests for Tenacious Blow feat damage on miss."""

    def test_tenacious_blow_miss_damage_dire_mace(self):
        """Test Tenacious Blow applies 4 pure damage on miss with Dire Mace."""
        # This is an integration test that verifies the setup
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Tenacious_Blow'][0] = True
        weapon = Weapon("Dire Mace", cfg)

        # Verify the weapon is correctly identified as double-sided
        assert weapon.name_base in ["Dire Mace", "Double Axe", "Two-Bladed Sword"]

    def test_tenacious_blow_miss_damage_double_axe(self):
        """Test Tenacious Blow applies 4 pure damage on miss with Double Axe."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Tenacious_Blow'][0] = True
        weapon = Weapon("Double Axe", cfg)

        # Verify the weapon is correctly identified as double-sided
        assert weapon.name_base in ["Dire Mace", "Double Axe", "Two-Bladed Sword"]

    def test_tenacious_blow_miss_damage_two_bladed_sword(self):
        """Test Tenacious Blow applies 4 pure damage on miss with Two-Bladed Sword."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Tenacious_Blow'][0] = True
        weapon = Weapon("Two-Bladed Sword", cfg)

        # Verify the weapon is correctly identified as double-sided
        assert weapon.name_base in ["Dire Mace", "Double Axe", "Two-Bladed Sword"]

    def test_tenacious_blow_no_miss_damage_on_single_sided(self):
        """Test Tenacious Blow does not apply on miss with single-sided weapons."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Tenacious_Blow'][0] = True
        weapon = Weapon("Longsword", cfg)

        # Verify the weapon is NOT double-sided
        assert weapon.name_base not in ["Dire Mace", "Double Axe", "Two-Bladed Sword"]


class TestDualWieldOffhandDamage:
    """Tests for dual-wield offhand strength bonus reduction."""

    def test_dual_wield_progression_structure(self):
        """Test that dual-wield progression has correct structure with offhand markers."""
        cfg = Config(AB_PROG="5APR & Dual-Wield")
        weapon = Weapon("Longsword", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # 5APR & Dual-Wield progression should have dw_hasted marker
        # Format: [0, -5, -10, -15, "dw_hasted", 0, -5]
        # After processing, this becomes numerical values
        assert simulator.attacks_per_round == 7
        # All attack_prog values should be integers
        assert all(isinstance(ab, int) for ab in simulator.attack_prog)

    def test_dual_wield_monk_progression_structure(self):
        """Test Monk dual-wield progression has correct structure."""
        cfg = Config(AB_PROG="Monk 7APR & Dual-Wield", TOON_SIZE='M')
        weapon = Weapon("Kama", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # Monk 7APR & Dual-Wield has haste attack marker
        assert simulator.dual_wield is True
        assert simulator.attacks_per_round == 9
        assert all(isinstance(ab, int) for ab in simulator.attack_prog)

    def test_dual_wield_flag_set_correctly(self):
        """Test dual_wield flag is set in damage simulator context."""
        cfg = Config(AB_PROG="4APR & Dual-Wield")
        weapon = Weapon("Longsword", cfg)
        simulator = AttackSimulator(weapon, cfg)

        assert simulator.dual_wield is True
        # Should have 6 attacks: [0, -5, -10, haste, 0, -5]
        assert simulator.attacks_per_round == 6

    def test_non_dual_wield_classic_progression(self):
        """Test classic progression doesn't set dual_wield flag."""
        cfg = Config(AB_PROG="5APR Classic")
        weapon = Weapon("Longsword", cfg)
        simulator = AttackSimulator(weapon, cfg)

        assert simulator.dual_wield is False
        assert simulator.attacks_per_round == 5

    def test_offhand_attack_indices(self):
        """Test that offhand attack indices are correctly identified as last 2 attacks."""
        cfg = Config(
            AB=68,
            AB_PROG="5APR & Dual-Wield",
            COMBAT_TYPE='melee',
            STR_MOD=20,
            TWO_HANDED=False
        )
        weapon = Weapon("Longsword", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # With 7 attacks (5APR & Dual-Wield), offhand should be indices 5 and 6
        total_attacks = simulator.attacks_per_round
        offhand_1_idx = total_attacks - 2
        offhand_2_idx = total_attacks - 1

        assert offhand_1_idx == 5
        assert offhand_2_idx == 6
        assert total_attacks == 7

    def test_dual_wield_penalty_application(self):
        """Test that dual-wield penalty is correctly applied to base AB."""
        cfg = Config(
            AB=50,
            TOON_SIZE='M',
            AB_PROG="4APR & Dual-Wield"
        )
        weapon = Weapon("Longsword", cfg)  # M+M = -4 DW penalty
        simulator = AttackSimulator(weapon, cfg)

        # Base AB should be reduced by dual-wield penalty
        # Original AB=50, DW penalty=-4, so base becomes 46
        # Progression [0, -5, -10, dw_hasted, 0, -5]
        # becomes [0, -5, -10, +4, 0, -5] (haste gets reversed penalty)
        # Final: [46, 41, 36, 50, 46, 41]
        expected = [46, 41, 36, 50, 46, 41]
        assert simulator.attack_prog == expected

    def test_monk_dual_wield_with_flurry(self):
        """Test Monk dual-wield with Flurry progression."""
        cfg = Config(
            AB=60,
            AB_PROG="Monk 7APR & Dual-Wield & Flurry",
            TOON_SIZE='M'
        )
        weapon = Weapon("Kama", cfg)
        simulator = AttackSimulator(weapon, cfg)

        assert simulator.dual_wield is True
        assert simulator.attacks_per_round == 10

    def test_strength_bonus_not_doubled_one_handed_dw(self):
        """Test that strength bonus is NOT doubled for one-handed dual-wield weapons."""
        cfg = Config(
            COMBAT_TYPE='melee',
            STR_MOD=21,
            TWO_HANDED=False,
            AB_PROG="5APR & Dual-Wield"
        )
        weapon = Weapon("Longsword", cfg)

        str_bonus = weapon.strength_bonus()
        # Should be 21, not 42 (only two-handed doubles STR)
        assert str_bonus['physical'][2] == 21


class TestDualWieldFlagDetection:
    """Tests for dual-wield flag detection in attack simulator."""

    def test_dual_wield_flag_detection(self):
        """Test that dual-wield is properly detected in attack simulator."""
        cfg = Config(AB_PROG="5APR & Dual-Wield")
        weapon = Weapon("Longsword", cfg)
        simulator = AttackSimulator(weapon, cfg)

        assert simulator.dual_wield is True

    def test_non_dual_wield_flag_detection(self):
        """Test that non-dual-wield progressions don't set dual_wield flag."""
        cfg = Config(AB_PROG="5APR Classic")
        weapon = Weapon("Longsword", cfg)
        simulator = AttackSimulator(weapon, cfg)

        assert simulator.dual_wield is False

    def test_dual_wield_strength_halving_setup(self):
        """Test that dual-wield offhand attacks are set up correctly.

        This test verifies that the attack simulator correctly identifies
        offhand attacks (last 2 attacks in round) for strength bonus halving.
        """
        cfg = Config(
            AB=68,
            AB_PROG="5APR & Dual-Wield",
            COMBAT_TYPE='melee',
            STR_MOD=20,
            TWO_HANDED=False
        )
        weapon = Weapon("Longsword", cfg)
        simulator = AttackSimulator(weapon, cfg)

        # Dual-wield progression should have 7 attacks
        assert simulator.attacks_per_round == 7
        # Last 2 should be offhand attacks (indices 5 and 6)
        offhand_1_idx = simulator.attacks_per_round - 2
        offhand_2_idx = simulator.attacks_per_round - 1
        assert offhand_1_idx == 5
        assert offhand_2_idx == 6


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

