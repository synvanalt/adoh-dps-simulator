"""
Unit tests for the Weapon class from simulator/weapon.py

This test suite covers:
- Weapon initialization and validation
- Threat range calculations (including Keen and Improved Crit bonuses)
- Critical multiplier calculations (including Weaponmaster bonus)
- Enhancement bonus calculations based on damage type prioritization
- Strength bonus calculations for different combat types
- Aggregation of all damage sources
"""

import pytest
from simulator.weapon import Weapon
from simulator.config import Config
from simulator.damage_roll import DamageRoll


class TestWeaponInitialization:
    """Tests for Weapon class initialization and basic setup."""

    def test_valid_weapon_initialization(self):
        """Test that a valid weapon initializes correctly."""
        cfg = Config()
        weapon = Weapon("Scythe", cfg)

        assert weapon.name_base == "Scythe"
        assert weapon.name_purple == "Scythe"
        assert isinstance(weapon.dmg['physical'], DamageRoll)
        assert weapon.dmg['physical'].dice == 2
        assert weapon.dmg['physical'].sides == 4
        assert weapon.dmg['physical'].flat == 0
        assert weapon.threat_base == 20
        assert weapon.multiplier_base == 4
        assert weapon.size == 'L'

    def test_weapon_with_purple_suffix_initialization(self):
        """Test that weapons with purple suffixes parse correctly."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)

        assert weapon.name_base == "Scimitar"
        assert weapon.threat_base == 18
        assert weapon.multiplier_base == 2

    def test_invalid_weapon_raises_error(self):
        """Test that initializing with an invalid weapon name raises ValueError."""
        cfg = Config()

        with pytest.raises(ValueError, match="not found in WEAPON_PROPERTIES"):
            Weapon("InvalidWeapon", cfg)

    def test_weapon_properties_loaded_correctly(self):
        """Test that weapon properties are loaded from the database correctly."""
        cfg = Config()
        weapon = Weapon("Halberd", cfg)

        assert isinstance(weapon.dmg['physical'], DamageRoll)
        assert weapon.dmg['physical'].dice == 1
        assert weapon.dmg['physical'].sides == 10
        assert weapon.dmg['physical'].flat == 0
        assert weapon.threat_base == 20
        assert weapon.multiplier_base == 3

    def test_different_weapon_damage_types(self):
        """Test that weapons with different damage types are loaded correctly."""
        cfg = Config()

        slashing_weapon = Weapon("Scythe", cfg)
        assert "slashing" in slashing_weapon.dmg_type

        bludgeoning_weapon = Weapon("Warhammer_Mjolnir", cfg)
        assert "bludgeoning" in bludgeoning_weapon.dmg_type

        piercing_weapon = Weapon("Dagger_PK", cfg)
        assert "piercing" in piercing_weapon.dmg_type


class TestCriticalThreat:
    """Tests for critical threat range calculations."""

    def test_base_threat_range_scimitar(self):
        """Test base threat range for Scimitar (18-20)."""
        cfg = Config(KEEN=False, IMPROVED_CRIT=False, WEAPONMASTER=False)
        weapon = Weapon("Scimitar", cfg)

        assert weapon.crit_threat == 18

    def test_base_threat_range_scythe(self):
        """Test base threat range for Scythe (20 only)."""
        cfg = Config(KEEN=False, IMPROVED_CRIT=False, WEAPONMASTER=False)
        weapon = Weapon("Scythe", cfg)

        assert weapon.crit_threat == 20

    def test_keen_doubles_threat_range(self):
        """Test that Keen feat doubles the threat range."""
        cfg = Config(KEEN=True, IMPROVED_CRIT=False, WEAPONMASTER=False)
        weapon = Weapon("Scimitar", cfg)

        # Scimitar: threat_base = 18, base range = 20 - 18 + 1 = 3
        # With Keen: threat_range_min = 18 - 3 = 15
        assert weapon.crit_threat == 15

    def test_improved_crit_doubles_threat_range(self):
        """Test that Improved Critical feat doubles the threat range."""
        cfg = Config(KEEN=False, IMPROVED_CRIT=True, WEAPONMASTER=False)
        weapon = Weapon("Scimitar", cfg)

        # Scimitar: threat_base = 18, base range = 20 - 18 + 1 = 3
        # With Improved Crit: threat_range_min = 18 - 3 = 15
        assert weapon.crit_threat == 15

    def test_keen_and_improved_crit_stack(self):
        """Test that Keen and Improved Critical stack (both double threat range)."""
        cfg = Config(KEEN=True, IMPROVED_CRIT=True, WEAPONMASTER=False)
        weapon = Weapon("Scimitar", cfg)

        # Scimitar: threat_base = 18, base range = 20 - 18 + 1 = 3
        # With Keen: threat_range_min = 18 - 3 = 15
        # With Improved Crit: threat_range_min = 15 - 3 = 12
        assert weapon.crit_threat == 12

    def test_weaponmaster_reduces_threat_range_by_2(self):
        """Test that Weaponmaster reduces threat range minimum by 2."""
        cfg = Config(KEEN=False, IMPROVED_CRIT=False, WEAPONMASTER=True)
        weapon = Weapon("Scimitar", cfg)

        # Scimitar: threat_base = 18
        # With Weaponmaster: threat_range_min = 18 - 2 = 16
        assert weapon.crit_threat == 16

    def test_weaponmaster_with_keen_and_improved_crit(self):
        """Test Weaponmaster stacks with Keen and Improved Critical."""
        cfg = Config(KEEN=True, IMPROVED_CRIT=True, WEAPONMASTER=True)
        weapon = Weapon("Scimitar", cfg)

        # Scimitar: threat_base = 18, base range = 3
        # With Keen: 18 - 3 = 15
        # With Improved Crit: 15 - 3 = 12
        # With Weaponmaster: 12 - 2 = 10
        assert weapon.crit_threat == 10

    def test_threat_range_cannot_go_below_1(self):
        """Test that threat range calculations produce valid values."""
        cfg = Config(KEEN=True, IMPROVED_CRIT=True, WEAPONMASTER=True)
        weapon = Weapon("Scythe", cfg)

        # Even with all bonuses, threat range should be valid
        # Scythe: threat_base = 20, base range = 1
        # With Keen: 20 - 1 = 19
        # With Improved Crit: 19 - 1 = 18
        # With Weaponmaster: 18 - 2 = 16
        assert weapon.crit_threat >= 1 and weapon.crit_threat <= 20


class TestCriticalMultiplier:
    """Tests for critical hit multiplier calculations."""

    def test_base_multiplier_scimitar(self):
        """Test base multiplier for Scimitar."""
        cfg = Config(WEAPONMASTER=False)
        weapon = Weapon("Scimitar", cfg)

        assert weapon.crit_multiplier == 2

    def test_base_multiplier_scythe(self):
        """Test base multiplier for Scythe."""
        cfg = Config(WEAPONMASTER=False)
        weapon = Weapon("Scythe", cfg)

        assert weapon.crit_multiplier == 4

    def test_weaponmaster_adds_1_to_multiplier(self):
        """Test that Weaponmaster adds +1 to critical multiplier."""
        cfg = Config(WEAPONMASTER=True)
        weapon = Weapon("Scimitar", cfg)

        # Scimitar base multiplier = 2, with Weaponmaster = 2 + 1 = 3
        assert weapon.crit_multiplier == 3

    def test_weaponmaster_applies_to_all_weapons(self):
        """Test that Weaponmaster multiplier bonus applies to all weapons."""
        cfg = Config(WEAPONMASTER=True)

        scythe = Weapon("Scythe", cfg)
        assert scythe.crit_multiplier == 5  # 4 + 1

        halberd = Weapon("Halberd", cfg)
        assert halberd.crit_multiplier == 4  # 3 + 1


class TestEnhancementBonus:
    """Tests for enhancement bonus calculations."""

    def test_standard_weapon_enhancement_bonus(self):
        """Test enhancement bonus for standard melee weapons (purple + set bonus)."""
        cfg = Config(ENHANCEMENT_SET_BONUS=3, DAMAGE_VS_RACE=False)
        weapon = Weapon("Scimitar", cfg)

        bonus = weapon.enhancement_bonus()
        assert 'slashing' in bonus
        # Scimitar has 7 enhancement + 3 set bonus = 10
        assert isinstance(bonus['slashing'], DamageRoll)
        assert bonus['slashing'].flat == 10

    def test_scythe_has_fixed_enhancement_bonus(self):
        """Test that Scythe combines its fixed 10 enhancement with set bonus."""
        cfg = Config(ENHANCEMENT_SET_BONUS=3, DAMAGE_VS_RACE=False)
        weapon = Weapon("Scythe", cfg)

        bonus = weapon.enhancement_bonus()
        # Scythe has 10 enhancement + 3 set bonus = 13
        dmg_type = next(iter(bonus.keys()))
        assert isinstance(bonus[dmg_type], DamageRoll)
        assert bonus[dmg_type].flat == 13

    def test_dwarven_waraxe_damage_vs_race_bonus(self):
        """Test that Dwarven Waraxe gets special vs_race enhancement bonus."""
        cfg_no_bonus = Config(ENHANCEMENT_SET_BONUS=3, DAMAGE_VS_RACE=False)
        cfg_with_bonus = Config(ENHANCEMENT_SET_BONUS=3, DAMAGE_VS_RACE=True)

        weapon_no_bonus = Weapon("Dwarven Waraxe", cfg_no_bonus)
        weapon_with_bonus = Weapon("Dwarven Waraxe", cfg_with_bonus)

        bonus_no_race = weapon_no_bonus.enhancement_bonus()
        bonus_with_race = weapon_with_bonus.enhancement_bonus()

        # Without DAMAGE_VS_RACE: 7 + 3 = 10
        assert isinstance(bonus_no_race['slashing'], DamageRoll)
        assert bonus_no_race['slashing'].flat == 10
        # With DAMAGE_VS_RACE and vs_race_dragon: 12 + 3 = 15
        assert isinstance(bonus_with_race['slashing'], DamageRoll)
        assert bonus_with_race['slashing'].flat == 15

    def test_ranged_weapons_have_zero_enhancement_bonus(self):
        """Test that ammo-based ranged weapons get 0 enhancement bonus regardless of set bonus."""
        cfg = Config(ENHANCEMENT_SET_BONUS=3, DAMAGE_VS_RACE=False)

        for weapon_name in ['Heavy Crossbow', 'Light Crossbow', 'Longbow_FireDragon', 'Shortbow_Celes', 'Sling']:
            weapon = Weapon(weapon_name, cfg)
            bonus = weapon.enhancement_bonus()

            # Ranged weapons should have 0 enhancement (ammo-based weapons ignore set bonus)
            assert all(isinstance(v, DamageRoll) and v.flat == 0 for v in bonus.values())

    def test_throwing_weapons_enhancement_bonus(self):
        """Test enhancement bonus for throwing weapons (different from ranged ammo-based)."""
        cfg = Config(ENHANCEMENT_SET_BONUS=3, DAMAGE_VS_RACE=False)
        weapon = Weapon("Darts", cfg)

        bonus = weapon.enhancement_bonus()
        # Darts have 7 enhancement + 3 set bonus = 10
        assert isinstance(bonus['piercing'], DamageRoll)
        assert bonus['piercing'].flat == 10

    def test_damage_type_prioritization(self):
        """Test that enhancement bonus uses correct damage type prioritization."""
        cfg = Config(ENHANCEMENT_SET_BONUS=3, DAMAGE_VS_RACE=False)

        # Test weapon with multiple damage types
        weapon = Weapon("Halberd", cfg)  # slashing & piercing
        bonus = weapon.enhancement_bonus()

        # Should prioritize slashing over piercing
        # Halberd has 7 enhancement + 3 set bonus = 10
        assert 'slashing' in bonus
        assert isinstance(bonus['slashing'], DamageRoll)
        assert bonus['slashing'].flat == 10


class TestStrengthBonus:
    """Tests for strength modifier damage calculations."""

    def test_melee_one_handed_str_bonus(self):
        """Test strength bonus for one-handed melee weapons."""
        cfg = Config(COMBAT_TYPE='melee', STR_MOD=21, TWO_HANDED=False)
        weapon = Weapon("Scimitar", cfg)

        str_bonus = weapon.strength_bonus()
        assert isinstance(str_bonus['physical'], DamageRoll)
        assert str_bonus['physical'].flat == 21

    def test_melee_two_handed_str_bonus_doubles(self):
        """Test that two-handed weapons double strength bonus."""
        cfg = Config(COMBAT_TYPE='melee', STR_MOD=21, TWO_HANDED=True)
        weapon = Weapon("Scythe", cfg)

        str_bonus = weapon.strength_bonus()
        assert isinstance(str_bonus['physical'], DamageRoll)
        assert str_bonus['physical'].flat == 42  # 21 * 2

    def test_ranged_str_bonus_capped_by_mighty(self):
        """Test that ranged weapons cap strength bonus by Mighty property."""
        cfg = Config(COMBAT_TYPE='ranged', STR_MOD=21, MIGHTY=10)
        weapon = Weapon("Longbow_FireDragon", cfg)

        str_bonus = weapon.strength_bonus()
        assert isinstance(str_bonus['physical'], DamageRoll)
        assert str_bonus['physical'].flat == 10  # min(21, 10)

    def test_ranged_str_bonus_uses_lower_value(self):
        """Test that ranged strength bonus uses min(STR_MOD, MIGHTY)."""
        cfg = Config(COMBAT_TYPE='ranged', STR_MOD=5, MIGHTY=10)
        weapon = Weapon("Longbow_FireDragon", cfg)

        str_bonus = weapon.strength_bonus()
        assert isinstance(str_bonus['physical'], DamageRoll)
        assert str_bonus['physical'].flat == 5  # min(5, 10)

    def test_throwing_weapons_get_str_bonus(self):
        """Test that throwing weapons get strength bonus."""
        cfg = Config(COMBAT_TYPE='ranged', STR_MOD=21, MIGHTY=0)
        weapon = Weapon("Darts", cfg)

        str_bonus = weapon.strength_bonus()
        assert isinstance(str_bonus['physical'], DamageRoll)
        assert str_bonus['physical'].flat == 21  # Throwing weapons have "auto-mighty"

    def test_throwing_axes_get_str_bonus(self):
        """Test that Throwing Axes get strength bonus."""
        cfg = Config(COMBAT_TYPE='ranged', STR_MOD=21, MIGHTY=0)
        weapon = Weapon("Throwing Axes", cfg)

        str_bonus = weapon.strength_bonus()
        assert isinstance(str_bonus['physical'], DamageRoll)
        assert str_bonus['physical'].flat == 21

    def test_invalid_combat_type_raises_error(self):
        """Test that invalid combat type raises ValueError."""
        cfg = Config(COMBAT_TYPE='invalid')
        weapon = Weapon("Scimitar", cfg)

        with pytest.raises(ValueError, match="Invalid combat type"):
            weapon.strength_bonus()


class TestAggregateDamageSources:
    """Tests for aggregating all damage sources."""

    def test_aggregate_includes_base_weapon_damage(self):
        """Test that aggregation includes base weapon damage."""
        cfg_default = Config()
        cfg = Config(ADDITIONAL_DAMAGE={k: [False, v[1]] for k, v in cfg_default.ADDITIONAL_DAMAGE.items()})
        weapon = Weapon("Scimitar", cfg)

        dmg_sources = weapon.aggregate_damage_sources()
        assert 'weapon_base_dmg' in dmg_sources
        assert dmg_sources['weapon_base_dmg'] == weapon.dmg

    def test_aggregate_includes_strength_bonus(self):
        """Test that aggregation includes strength bonus."""
        cfg_default = Config()
        cfg = Config(
            COMBAT_TYPE='melee',
            STR_MOD=21,
            TWO_HANDED=False,
            ADDITIONAL_DAMAGE={k: [False, v[1]] for k, v in cfg_default.ADDITIONAL_DAMAGE.items()}
        )
        weapon = Weapon("Scimitar", cfg)

        dmg_sources = weapon.aggregate_damage_sources()
        assert 'str_dmg' in dmg_sources
        assert isinstance(dmg_sources['str_dmg']['physical'], DamageRoll)
        assert dmg_sources['str_dmg']['physical'].flat == 21

    def test_aggregate_includes_additional_damage(self):
        """Test that aggregation includes enabled additional damage sources."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Flame_Weapon'][0] = True
        weapon = Weapon("Scimitar", cfg)

        dmg_sources = weapon.aggregate_damage_sources()
        assert 'additional_dmg' in dmg_sources
        assert len(dmg_sources['additional_dmg']) >= 1

    def test_aggregate_excludes_disabled_additional_damage(self):
        """Test that disabled additional damage sources are excluded."""
        cfg = Config()
        # Ensure all additional damage is disabled
        for key in cfg.ADDITIONAL_DAMAGE:
            cfg.ADDITIONAL_DAMAGE[key][0] = False

        weapon = Weapon("Scimitar", cfg)

        dmg_sources = weapon.aggregate_damage_sources()
        assert 'additional_dmg' in dmg_sources
        assert len(dmg_sources['additional_dmg']) == 0

    def test_aggregate_all_damage_types_present(self):
        """Test that all expected damage sources are present in aggregation."""
        cfg = Config()
        weapon = Weapon("Scimitar", cfg)

        dmg_sources = weapon.aggregate_damage_sources()

        expected_keys = {'weapon_base_dmg', 'weapon_bonus_dmg', 'str_dmg', 'additional_dmg'}
        assert expected_keys.issubset(dmg_sources.keys())

    def test_weapon_bonus_damage_contains_purple_damage(self):
        """Test that weapon bonus damage includes purple properties."""
        cfg_default = Config()
        cfg = Config(ADDITIONAL_DAMAGE={k: [False, v[1]] for k, v in cfg_default.ADDITIONAL_DAMAGE.items()})
        weapon = Weapon("Scythe", cfg)

        dmg_sources = weapon.aggregate_damage_sources()
        weapon_bonus = dmg_sources['weapon_bonus_dmg']

        # Scythe has purple properties with bludgeoning and negative damage
        assert len(weapon_bonus) > 0


class TestWeaponWithDifferentConfigs:
    """Integration tests with various configuration combinations."""

    def test_weapon_melee_full_buffs(self):
        """Test weapon with all melee buffs enabled."""
        cfg = Config(
            COMBAT_TYPE='melee',
            STR_MOD=21,
            TWO_HANDED=True,
            ENHANCEMENT_SET_BONUS=3,
            WEAPONMASTER=True,
            KEEN=True,
            IMPROVED_CRIT=True,
            DAMAGE_VS_RACE=True
        )
        weapon = Weapon("Scythe", cfg)

        assert weapon.crit_multiplier == 5  # 4 + 1 from Weaponmaster
        assert weapon.crit_threat == 16  # 20 - 1 (base range) - 1 (Keen) - 1 (Improved) - 2 (WM)

        str_bonus = weapon.strength_bonus()
        assert isinstance(str_bonus['physical'], DamageRoll)
        assert str_bonus['physical'].flat == 42  # 21 * 2

    def test_weapon_ranged_configuration(self):
        """Test weapon with ranged configuration."""
        cfg = Config(
            COMBAT_TYPE='ranged',
            STR_MOD=21,
            MIGHTY=10,
            ENHANCEMENT_SET_BONUS=3,
            KEEN=False,
            IMPROVED_CRIT=False
        )
        weapon = Weapon("Longbow_FireDragon", cfg)

        str_bonus = weapon.strength_bonus()
        assert isinstance(str_bonus['physical'], DamageRoll)
        assert str_bonus['physical'].flat == 10  # Capped by Mighty

    def test_weapon_shape_override(self):
        """Test weapon with shape override configuration."""
        cfg = Config(SHAPE_WEAPON_OVERRIDE=True, SHAPE_WEAPON="Scythe")
        weapon = Weapon("Scimitar", cfg)

        # Should use Scythe properties instead of Scimitar
        assert isinstance(weapon.dmg['physical'], DamageRoll)
        assert weapon.dmg['physical'].dice == 2
        assert weapon.dmg['physical'].sides == 4
        assert weapon.dmg['physical'].flat == 0

    def test_multiple_additional_damage_enabled(self):
        """Test aggregation with multiple additional damage sources enabled."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Flame_Weapon'][0] = True
        cfg.ADDITIONAL_DAMAGE['Divine_Favor'][0] = True
        cfg.ADDITIONAL_DAMAGE['Sneak_Attack'][0] = True

        weapon = Weapon("Scimitar", cfg)
        dmg_sources = weapon.aggregate_damage_sources()

        assert len(dmg_sources['additional_dmg']) >= 3


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_zero_strength_modifier(self):
        """Test weapon with zero strength modifier."""
        cfg = Config(COMBAT_TYPE='melee', STR_MOD=0, TWO_HANDED=False)
        weapon = Weapon("Scimitar", cfg)

        str_bonus = weapon.strength_bonus()
        assert isinstance(str_bonus['physical'], DamageRoll)
        assert str_bonus['physical'].flat == 0

    def test_negative_strength_modifier(self):
        """Test weapon with negative strength modifier."""
        cfg = Config(COMBAT_TYPE='melee', STR_MOD=-2, TWO_HANDED=False)
        weapon = Weapon("Scimitar", cfg)

        str_bonus = weapon.strength_bonus()
        assert isinstance(str_bonus['physical'], DamageRoll)
        assert str_bonus['physical'].flat == -2

    def test_all_features_disabled(self):
        """Test weapon with all features disabled."""
        cfg = Config(
            KEEN=False,
            IMPROVED_CRIT=False,
            WEAPONMASTER=False,
            DAMAGE_VS_RACE=False,
            STR_MOD=0
        )
        weapon = Weapon("Scimitar", cfg)

        assert weapon.crit_threat == 18
        assert weapon.crit_multiplier == 2
        str_bonus = weapon.strength_bonus()
        assert isinstance(str_bonus['physical'], DamageRoll)
        assert str_bonus['physical'].flat == 0

    def test_empty_additional_damage(self):
        """Test aggregation when no additional damage is configured."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE = {}
        weapon = Weapon("Scimitar", cfg)

        dmg_sources = weapon.aggregate_damage_sources()
        assert 'additional_dmg' in dmg_sources


class TestWeaponDamageTypes:
    """Tests for weapons with different damage type combinations."""

    def test_single_damage_type(self):
        """Test weapon with single damage type."""
        cfg = Config(ENHANCEMENT_SET_BONUS=3)
        weapon = Weapon("Dagger_PK", cfg)

        bonus = weapon.enhancement_bonus()
        assert 'piercing' in bonus

    def test_dual_damage_type(self):
        """Test weapon with dual damage types."""
        cfg = Config(ENHANCEMENT_SET_BONUS=3)
        weapon = Weapon("Halberd", cfg)

        # Halberd has 'slashing & piercing'
        bonus = weapon.enhancement_bonus()
        # Should pick the prioritized type (slashing comes before piercing)
        assert 'slashing' in bonus

    def test_all_monk_weapons_load(self):
        """Test that all monk weapons load correctly."""
        cfg = Config()

        monk_weapons = ['Gloves_Shandy', 'Kama', 'Quarterstaff_IcyFire', 'Shuriken']
        for weapon_name in monk_weapons:
            weapon = Weapon(weapon_name, cfg)
            assert weapon.name_base in ['Gloves', 'Kama', 'Quarterstaff', 'Shuriken']

    def test_all_medium_weapons_load(self):
        """Test that various medium weapons load correctly."""
        cfg = Config()

        medium_weapons = ['Scimitar', 'Longsword', 'Katana_Kin', 'Rapier_Stinger']
        for weapon_name in medium_weapons:
            weapon = Weapon(weapon_name, cfg)
            assert weapon.name_base in ['Scimitar', 'Longsword', 'Katana', 'Rapier']


class TestTenaciousBlow:
    """Tests for Tenacious Blow feat handling."""

    def test_tenacious_blow_enabled_on_dire_mace(self):
        """Test Tenacious Blow is active on Dire Mace when enabled."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Tenacious_Blow'][0] = True
        weapon = Weapon("Dire Mace", cfg)

        dmg_sources = weapon.aggregate_damage_sources()
        additional_dmg = dmg_sources['additional_dmg']

        # Should have Tenacious Blow damage [0, 0, 8] in additional damages
        assert {'physical': [0, 0, 8]} in additional_dmg

    def test_tenacious_blow_enabled_on_double_axe(self):
        """Test Tenacious Blow is active on Double Axe when enabled."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Tenacious_Blow'][0] = True
        weapon = Weapon("Double Axe", cfg)

        dmg_sources = weapon.aggregate_damage_sources()
        additional_dmg = dmg_sources['additional_dmg']

        # Should have Tenacious Blow damage [0, 0, 8] in additional damages
        assert {'physical': [0, 0, 8]} in additional_dmg

    def test_tenacious_blow_enabled_on_two_bladed_sword(self):
        """Test Tenacious Blow is active on Two-Bladed Sword when enabled."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Tenacious_Blow'][0] = True
        weapon = Weapon("Two-Bladed Sword", cfg)

        dmg_sources = weapon.aggregate_damage_sources()
        additional_dmg = dmg_sources['additional_dmg']

        # Should have Tenacious Blow damage [0, 0, 8] in additional damages
        assert {'physical': [0, 0, 8]} in additional_dmg

    def test_tenacious_blow_disabled_on_non_double_sided_weapon(self):
        """Test Tenacious Blow is disabled on non-double-sided weapons."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Tenacious_Blow'][0] = True  # Enable it globally
        weapon = Weapon("Scimitar", cfg)  # Non-double-sided weapon

        dmg_sources = weapon.aggregate_damage_sources()
        additional_dmg = dmg_sources['additional_dmg']

        # Tenacious Blow should be filtered out for non-double-sided weapons
        assert all('Tenacious_Blow' not in str(dmg) for dmg in additional_dmg)

    def test_tenacious_blow_disabled_on_longsword(self):
        """Test Tenacious Blow is disabled on Longsword (single-sided)."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Tenacious_Blow'][0] = True  # Enable it globally
        weapon = Weapon("Longsword", cfg)  # Non-double-sided weapon

        dmg_sources = weapon.aggregate_damage_sources()
        additional_dmg = dmg_sources['additional_dmg']

        # Tenacious Blow should be filtered out for Longsword
        assert all('Tenacious_Blow' not in str(dmg) for dmg in additional_dmg)

    def test_tenacious_blow_on_dagger(self):
        """Test Tenacious Blow is disabled on Dagger (single-sided)."""
        cfg = Config()
        cfg.ADDITIONAL_DAMAGE['Tenacious_Blow'][0] = True  # Enable it globally
        weapon = Weapon("Dagger_PK", cfg)  # Non-double-sided weapon

        dmg_sources = weapon.aggregate_damage_sources()
        additional_dmg = dmg_sources['additional_dmg']

        # Tenacious Blow should be filtered out for Dagger
        assert all('Tenacious_Blow' not in str(dmg) for dmg in additional_dmg)


class TestStrengthBonusConfiguration:
    """Tests for strength bonus configuration in weapon context."""

    def test_strength_bonus_included_in_damage_dict(self):
        """Test that strength bonus is included in damage aggregation."""
        cfg = Config(
            COMBAT_TYPE='melee',
            STR_MOD=21,
            TWO_HANDED=False
        )
        weapon = Weapon("Longsword", cfg)

        dmg_sources = weapon.aggregate_damage_sources()
        assert 'str_dmg' in dmg_sources
        assert isinstance(dmg_sources['str_dmg']['physical'], DamageRoll)
        assert dmg_sources['str_dmg']['physical'].flat == 21

    def test_strength_bonus_doubled_two_handed(self):
        """Test that strength bonus is doubled for two-handed weapons."""
        cfg = Config(
            COMBAT_TYPE='melee',
            STR_MOD=21,
            TWO_HANDED=True
        )
        weapon = Weapon("Longsword", cfg)

        str_bonus = weapon.strength_bonus()
        assert isinstance(str_bonus['physical'], DamageRoll)
        assert str_bonus['physical'].flat == 42  # 21 * 2



if __name__ == '__main__':
    pytest.main([__file__, '-v'])
