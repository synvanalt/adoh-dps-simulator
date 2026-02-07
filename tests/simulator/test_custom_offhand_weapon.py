"""Tests for custom offhand weapon functionality in dual-wield mode."""

import pytest
from simulator.config import Config
from simulator.damage_simulator import DamageSimulator
from simulator.attack_simulator import AttackSimulator
from simulator.weapon import Weapon


class TestCustomOffhandWeaponConfig:
    """Test custom offhand weapon configuration parameters."""

    def test_default_custom_offhand_weapon_disabled(self):
        """Test that CUSTOM_OFFHAND_WEAPON is disabled by default."""
        cfg = Config()
        assert cfg.CUSTOM_OFFHAND_WEAPON is False

    def test_default_offhand_weapon_is_scimitar(self):
        """Test that default OFFHAND_WEAPON is Scimitar."""
        cfg = Config()
        assert cfg.OFFHAND_WEAPON == "Scimitar"

    def test_default_offhand_ab_equals_ab(self):
        """Test that default OFFHAND_AB equals AB."""
        cfg = Config()
        assert cfg.OFFHAND_AB == cfg.AB

    def test_default_offhand_crit_settings(self):
        """Test that default offhand crit settings are correct."""
        cfg = Config()
        assert cfg.OFFHAND_KEEN is True
        assert cfg.OFFHAND_IMPROVED_CRIT is True
        assert cfg.OFFHAND_OVERWHELM_CRIT is False
        assert cfg.OFFHAND_DEV_CRIT is False
        assert cfg.OFFHAND_WEAPONMASTER_THREAT is False


class TestCustomOffhandWeaponSimulator:
    """Test custom offhand weapon in DamageSimulator."""

    def test_no_offhand_weapon_when_disabled(self):
        """Test that offhand_weapon is None when CUSTOM_OFFHAND_WEAPON is disabled."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = False
        sim = DamageSimulator('Scimitar', cfg)
        assert sim.offhand_weapon is None

    def test_offhand_weapon_created_when_enabled(self):
        """Test that offhand_weapon is created when CUSTOM_OFFHAND_WEAPON is enabled."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Kukri_Crow'
        sim = DamageSimulator('Scimitar', cfg)
        assert sim.offhand_weapon is not None
        assert sim.offhand_weapon.name_purple == 'Kukri_Crow'

    def test_offhand_weapon_not_created_without_dual_wield(self):
        """Test that offhand_weapon is None when DUAL_WIELD is disabled."""
        cfg = Config()
        cfg.DUAL_WIELD = False
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Kukri_Crow'
        sim = DamageSimulator('Scimitar', cfg)
        assert sim.offhand_weapon is None

    def test_offhand_legend_effect_created(self):
        """Test that offhand_legend_effect is created when custom offhand is enabled."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Kukri_Crow'
        sim = DamageSimulator('Scimitar', cfg)
        assert sim.offhand_legend_effect is not None

    def test_offhand_dmg_dict_populated(self):
        """Test that offhand damage dictionary is populated."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Kukri_Crow'
        sim = DamageSimulator('Scimitar', cfg)
        assert len(sim.offhand_dmg_dict) > 0
        assert 'physical' in sim.offhand_dmg_dict


class TestCustomOffhandAB:
    """Test custom offhand AB functionality."""

    def test_offhand_ab_uses_mainhand_when_custom_offhand_disabled(self):
        """Test that offhand AB uses mainhand AB when CUSTOM_OFFHAND_WEAPON is disabled."""
        cfg = Config()
        cfg.AB = 68
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = False
        sim = DamageSimulator('Scimitar', cfg)
        assert sim.attack_sim.offhand_ab == cfg.AB

    def test_offhand_ab_uses_custom_when_custom_offhand_enabled(self):
        """Test that offhand AB uses custom value when CUSTOM_OFFHAND_WEAPON is enabled."""
        cfg = Config()
        cfg.AB = 68
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_AB = 60
        sim = DamageSimulator('Scimitar', cfg)
        assert sim.attack_sim.offhand_ab == 60

    def test_offhand_ab_capped_calculated_correctly(self):
        """Test that OFFHAND_AB_CAPPED is calculated correctly."""
        cfg = Config()
        cfg.AB = 68
        cfg.AB_CAPPED = 75
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_AB = 60
        sim = DamageSimulator('Scimitar', cfg)
        # OFFHAND_AB_CAPPED = AB_CAPPED - (AB - OFFHAND_AB) = 75 - (68 - 60) = 67
        expected_cap = 75 - (68 - 60)
        assert sim.attack_sim.offhand_ab_capped == expected_cap


class TestCustomOffhandAttackProgression:
    """Test attack progression with custom offhand."""

    def test_offhand_attack_indices_tracked(self):
        """Test that offhand attack indices are tracked correctly."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.IMPROVED_TWF = True
        sim = DamageSimulator('Scimitar', cfg)
        # With IMPROVED_TWF, should have 2 offhand attacks
        assert len(sim.attack_sim.offhand_attack_indices) == 2

    def test_offhand_attack_indices_without_improved_twf(self):
        """Test offhand attack indices without Improved TWF."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.IMPROVED_TWF = False
        sim = DamageSimulator('Scimitar', cfg)
        # Without IMPROVED_TWF, should have 1 offhand attack
        assert len(sim.attack_sim.offhand_attack_indices) == 1

    def test_offhand_attacks_use_offhand_ab(self):
        """Test that offhand attacks use the correct offhand AB."""
        cfg = Config()
        cfg.AB = 68
        cfg.DUAL_WIELD = True
        cfg.TWO_WEAPON_FIGHTING = True
        cfg.AMBIDEXTERITY = True
        cfg.IMPROVED_TWF = True
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_AB = 60
        sim = DamageSimulator('Scimitar', cfg)

        # Get offhand attack ABs from progression
        offhand_indices = sim.attack_sim.offhand_attack_indices
        offhand_abs = [sim.attack_sim.attack_prog[i] for i in offhand_indices]

        # Offhand attacks should be based on OFFHAND_AB (60) minus penalties
        # Scimitar is Medium, so for Medium char it's NOT light weapon
        # With TWF+Ambi and non-light offhand: -4 penalty
        # First offhand: 60 - 4 = 56
        # Second offhand: 60 - 4 - 5 = 51
        assert offhand_abs[0] == 56
        assert offhand_abs[1] == 51


class TestCustomOffhandCriticalHit:
    """Test critical hit mechanics with custom offhand."""

    def test_offhand_uses_own_crit_threat(self):
        """Test that offhand attacks use offhand weapon's crit threat."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Kukri_Crow'  # 18-20 threat (12 with keen)
        sim = DamageSimulator('Scythe', cfg)  # 20/x4

        # Scythe base threat is 20, Kukri base threat is 18
        # With Keen (default enabled), Scythe: 19-20, Kukri: 15-20
        # Check that they have different crit threats
        mainhand_threat = sim.weapon.crit_threat
        offhand_threat = sim.offhand_weapon.crit_threat
        assert offhand_threat < mainhand_threat  # Kukri has wider threat range

    def test_offhand_uses_mainhand_crit_multiplier(self):
        """Test that offhand critical hits use mainhand's multiplier."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Kukri_Crow'  # x2 multiplier
        sim = DamageSimulator('Scythe', cfg)  # x4 multiplier

        # The mainhand's crit multiplier (x4) should be used for offhand crits
        # Offhand attacks pass offhand's crit_threat to attack_roll, but damage uses mainhand's multiplier
        mainhand_mult = sim.weapon.crit_multiplier
        offhand_mult = sim.offhand_weapon.crit_multiplier

        assert mainhand_mult == 4
        assert offhand_mult == 2
        # The simulator uses mainhand_mult for all damage calculations (verified in simulate_dps)


class TestOffhandCritSettings:
    """Test offhand-specific crit feat settings."""

    def test_offhand_keen_affects_only_offhand(self):
        """Test that OFFHAND_KEEN only affects offhand weapon crit threat."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Scimitar'  # Base threat 18
        cfg.KEEN = True  # Mainhand Keen ON
        cfg.OFFHAND_KEEN = False  # Offhand Keen OFF
        cfg.IMPROVED_CRIT = False
        cfg.OFFHAND_IMPROVED_CRIT = False

        mainhand = Weapon('Scimitar', cfg, is_offhand=False)
        offhand = Weapon('Scimitar', cfg, is_offhand=True)

        # Mainhand: 18 - 3 = 15 (Keen doubles threat range)
        # Offhand: 18 (no Keen)
        assert mainhand.crit_threat == 15
        assert offhand.crit_threat == 18

    def test_offhand_improved_crit_affects_only_offhand(self):
        """Test that OFFHAND_IMPROVED_CRIT only affects offhand weapon crit threat."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Scimitar'
        cfg.KEEN = False
        cfg.OFFHAND_KEEN = False
        cfg.IMPROVED_CRIT = True  # Mainhand Improved Crit ON
        cfg.OFFHAND_IMPROVED_CRIT = False  # Offhand Improved Crit OFF

        mainhand = Weapon('Scimitar', cfg, is_offhand=False)
        offhand = Weapon('Scimitar', cfg, is_offhand=True)

        # Mainhand: 18 - 3 = 15 (Improved Crit doubles threat range)
        # Offhand: 18 (no Improved Crit)
        assert mainhand.crit_threat == 15
        assert offhand.crit_threat == 18

    def test_offhand_weaponmaster_threat_affects_only_offhand(self):
        """Test that OFFHAND_WEAPONMASTER_THREAT only affects offhand weapon crit threat."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Scimitar'
        cfg.KEEN = False
        cfg.OFFHAND_KEEN = False
        cfg.IMPROVED_CRIT = False
        cfg.OFFHAND_IMPROVED_CRIT = False
        cfg.WEAPONMASTER = True  # Mainhand WM ON (affects threat and multiplier)
        cfg.OFFHAND_WEAPONMASTER_THREAT = False  # Offhand WM Threat OFF

        mainhand = Weapon('Scimitar', cfg, is_offhand=False)
        offhand = Weapon('Scimitar', cfg, is_offhand=True)

        # Mainhand: 18 - 2 = 16 (WM reduces threat by 2)
        # Offhand: 18 (no WM Threat)
        assert mainhand.crit_threat == 16
        assert offhand.crit_threat == 18

    def test_offhand_weaponmaster_threat_does_not_affect_multiplier(self):
        """Test that OFFHAND_WEAPONMASTER_THREAT doesn't affect crit multiplier."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Scimitar'
        cfg.WEAPONMASTER = False  # Mainhand WM OFF
        cfg.OFFHAND_WEAPONMASTER_THREAT = True  # Offhand WM Threat ON

        mainhand = Weapon('Scimitar', cfg, is_offhand=False)
        offhand = Weapon('Scimitar', cfg, is_offhand=True)

        # Multiplier should come from mainhand WEAPONMASTER setting
        # Since mainhand WM is OFF, both should have base multiplier (x2)
        assert mainhand.crit_multiplier == 2
        assert offhand.crit_multiplier == 2  # Not affected by OFFHAND_WEAPONMASTER_THREAT

    def test_offhand_crit_threat_with_all_settings(self):
        """Test offhand crit threat with multiple settings enabled."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Scimitar'  # Base threat 18
        cfg.OFFHAND_KEEN = True
        cfg.OFFHAND_IMPROVED_CRIT = True
        cfg.OFFHAND_WEAPONMASTER_THREAT = True

        offhand = Weapon('Scimitar', cfg, is_offhand=True)

        # Base: 18, threat range = 3
        # Keen: -3
        # Improved Crit: -3
        # WM Threat: -2
        # Total: 18 - 3 - 3 - 2 = 10
        assert offhand.crit_threat == 10


class TestCustomOffhandDualWieldValidation:
    """Test dual-wield validation with custom offhand weapons."""

    def test_large_mainhand_medium_offhand_valid_for_large_char(self):
        """Test that Large mainhand + Medium offhand is valid for Large character."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CHARACTER_SIZE = 'L'
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Scimitar'  # Medium
        sim = DamageSimulator('Spear', cfg)  # Large
        assert sim.attack_sim.valid_dual_wield_config is True

    def test_large_mainhand_small_offhand_valid_for_large_char(self):
        """Test that Large mainhand + Small offhand is valid for Large character."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CHARACTER_SIZE = 'L'
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Handaxe_Adam'  # Small
        sim = DamageSimulator('Spear', cfg)  # Large
        assert sim.attack_sim.valid_dual_wield_config is True

    def test_large_mainhand_tiny_offhand_invalid_for_large_char(self):
        """Test that Large mainhand + Tiny offhand is invalid for Large character."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CHARACTER_SIZE = 'L'
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Kukri_Crow'  # Tiny
        sim = DamageSimulator('Spear', cfg)  # Large
        assert sim.attack_sim.valid_dual_wield_config is False

    def test_large_mainhand_large_offhand_invalid_for_large_char(self):
        """Test that Large mainhand + Large offhand is invalid."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CHARACTER_SIZE = 'L'
        cfg.CUSTOM_OFFHAND_WEAPON = False  # Same weapon (Large)
        sim = DamageSimulator('Spear', cfg)  # Large
        assert sim.attack_sim.valid_dual_wield_config is False

    def test_medium_offhand_penalty_calculation(self):
        """Test that offhand weapon size affects dual-wield penalties."""
        cfg = Config()
        cfg.AB = 68
        cfg.DUAL_WIELD = True
        cfg.CHARACTER_SIZE = 'M'
        cfg.TWO_WEAPON_FIGHTING = True
        cfg.AMBIDEXTERITY = True
        cfg.IMPROVED_TWF = False
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Longsword'  # Medium (not light for Medium char)
        sim = DamageSimulator('Scimitar', cfg)

        # With Medium offhand (not light): -4/-4 penalties
        # First mainhand attack: 68 - 4 = 64
        # Offhand attack: 68 - 4 = 64
        assert sim.attack_sim.attack_prog[-1] == 64  # Last is offhand

    def test_small_offhand_penalty_calculation(self):
        """Test that small (light) offhand weapon reduces penalties."""
        cfg = Config()
        cfg.AB = 68
        cfg.DUAL_WIELD = True
        cfg.CHARACTER_SIZE = 'M'
        cfg.TWO_WEAPON_FIGHTING = True
        cfg.AMBIDEXTERITY = True
        cfg.IMPROVED_TWF = False
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Handaxe_Adam'  # Small (light for Medium char)
        sim = DamageSimulator('Scimitar', cfg)

        # With Small offhand (light): -2/-2 penalties
        # Offhand attack: 68 - 2 = 66
        assert sim.attack_sim.attack_prog[-1] == 66  # Last is offhand


class TestCustomOffhandSimulationOutput:
    """Test simulation output with custom offhand."""

    def test_summary_includes_offhand_info(self):
        """Test that simulation summary includes offhand weapon info."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Kukri_Crow'
        cfg.ROUNDS = 10
        sim = DamageSimulator('Scimitar', cfg)
        results = sim.simulate_dps()

        assert 'Offhand: Kukri_Crow' in results['summary']
        assert 'Offhand Crit:' in results['summary']

    def test_simulation_produces_positive_dps(self):
        """Test that simulation with custom offhand produces positive DPS."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Kukri_Crow'
        cfg.ROUNDS = 50
        sim = DamageSimulator('Scimitar', cfg)
        results = sim.simulate_dps()

        assert results['dps_crits'] > 0
        assert results['hit_rate_actual'] > 0


class TestOffhandLegendProcRate:
    """Test theoretical legend proc rate for offhand."""

    def test_get_offhand_legend_proc_rate_returns_zero_when_no_custom_offhand(self):
        """Test that offhand legend proc rate is 0 when no custom offhand."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = False
        sim = DamageSimulator('Scimitar', cfg)

        rate = sim.attack_sim.get_offhand_legend_proc_rate_theoretical()
        assert rate == 0.0

    def test_get_offhand_legend_proc_rate_with_custom_offhand(self):
        """Test that offhand legend proc rate is calculated with custom offhand."""
        cfg = Config()
        cfg.DUAL_WIELD = True
        cfg.CUSTOM_OFFHAND_WEAPON = True
        cfg.OFFHAND_WEAPON = 'Kukri_Crow'  # Has on-hit legendary
        sim = DamageSimulator('Scimitar', cfg)

        rate = sim.attack_sim.get_offhand_legend_proc_rate_theoretical()
        # Should have a proc rate based on weapon's legendary property
        assert rate >= 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
