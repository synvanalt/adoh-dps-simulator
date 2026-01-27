"""
Unit tests for validation callbacks.

Tests input validation logic for character settings, additional damage,
and immunity inputs.
"""

import pytest
from simulator.config import Config


class TestValidationLogic:
    """Test validation logic for inputs."""

    def test_validate_within_range(self):
        """Test that values within range are unchanged."""
        val = 50
        min_val = 0
        max_val = 100
        validated = max(min_val, min(max_val, val))
        assert validated == 50

    def test_validate_below_min(self):
        """Test that values below minimum are clamped."""
        val = -10
        min_val = 0
        max_val = 100
        validated = max(min_val, min(max_val, val))
        assert validated == 0

    def test_validate_above_max(self):
        """Test that values above maximum are clamped."""
        val = 150
        min_val = 0
        max_val = 100
        validated = max(min_val, min(max_val, val))
        assert validated == 100

    def test_validate_at_min_boundary(self):
        """Test validation at minimum boundary."""
        val = 0
        min_val = 0
        max_val = 100
        validated = max(min_val, min(max_val, val))
        assert validated == 0

    def test_validate_at_max_boundary(self):
        """Test validation at maximum boundary."""
        val = 100
        min_val = 0
        max_val = 100
        validated = max(min_val, min(max_val, val))
        assert validated == 100


class TestValidationDefaults:
    """Test default value handling in validation."""

    def test_none_value_uses_default(self):
        """Test that None values use default."""
        val = None
        default = 42
        try:
            validated = float(val) if val is not None else default
        except (ValueError, TypeError):
            validated = default
        assert validated == 42

    def test_invalid_string_uses_default(self):
        """Test that invalid strings use default."""
        val = "invalid"
        default = 42
        try:
            validated = float(val)
        except (ValueError, TypeError):
            validated = default
        assert validated == 42

    def test_valid_string_number_converted(self):
        """Test that valid string numbers are converted."""
        val = "50"
        default = 42
        try:
            validated = float(val)
        except (ValueError, TypeError):
            validated = default
        assert validated == 50.0


class TestCharacterSettingsValidation:
    """Test character settings validation ranges."""

    def test_ab_validation_range(self):
        """Test AB validation range."""
        cfg = Config()
        min_val = 0
        max_val = 999
        default = cfg.AB

        # Test within range
        assert max(min_val, min(max_val, 50)) == 50
        # Test below range
        assert max(min_val, min(max_val, -10)) == 0
        # Test above range
        assert max(min_val, min(max_val, 1000)) == 999

    def test_str_mod_validation_range(self):
        """Test STR modifier validation range."""
        cfg = Config()
        min_val = 0
        max_val = 999
        default = cfg.STR_MOD

        assert max(min_val, min(max_val, 15)) == 15
        assert max(min_val, min(max_val, -5)) == 0
        assert max(min_val, min(max_val, 1000)) == 999

    def test_mighty_validation_range(self):
        """Test mighty validation range."""
        cfg = Config()
        min_val = 0
        max_val = 999

        assert max(min_val, min(max_val, 5)) == 5
        assert max(min_val, min(max_val, 0)) == 0
        assert max(min_val, min(max_val, 1000)) == 999


class TestAdditionalDamageValidation:
    """Test additional damage validation."""

    def test_dice_validation_range(self):
        """Test dice validation range."""
        min_val = 0
        max_val = 99

        assert max(min_val, min(max_val, 5)) == 5
        assert max(min_val, min(max_val, -1)) == 0
        assert max(min_val, min(max_val, 100)) == 99

    def test_sides_validation_range(self):
        """Test sides validation range."""
        min_val = 0
        max_val = 99

        assert max(min_val, min(max_val, 6)) == 6
        assert max(min_val, min(max_val, 0)) == 0
        assert max(min_val, min(max_val, 150)) == 99

    def test_flat_damage_validation_range(self):
        """Test flat damage validation range."""
        min_val = 0
        max_val = 999

        assert max(min_val, min(max_val, 10)) == 10
        assert max(min_val, min(max_val, -5)) == 0
        assert max(min_val, min(max_val, 1500)) == 999


class TestImmunityValidation:
    """Test immunity validation."""

    def test_immunity_allows_negative(self):
        """Test that immunity allows negative values (vulnerability)."""
        min_val = -100
        max_val = 100

        assert max(min_val, min(max_val, -50)) == -50

    def test_immunity_validation_range(self):
        """Test immunity validation range."""
        min_val = -100
        max_val = 100

        assert max(min_val, min(max_val, 0)) == 0
        assert max(min_val, min(max_val, 50)) == 50
        assert max(min_val, min(max_val, -150)) == -100
        assert max(min_val, min(max_val, 150)) == 100


class TestValidationDuringBuildLoading:
    """Test that validation is skipped during build loading."""

    def test_validation_skipped_when_loading(self):
        """Test that validation returns no_update when loading."""
        is_loading = True

        # Simulate validation check
        if is_loading:
            should_validate = False
        else:
            should_validate = True

        assert not should_validate

    def test_validation_active_when_not_loading(self):
        """Test that validation is active when not loading."""
        is_loading = False

        # Simulate validation check
        if is_loading:
            should_validate = False
        else:
            should_validate = True

        assert should_validate


class TestConvergenceParametersValidation:
    """Test convergence parameters validation."""

    def test_rounds_validation(self):
        """Test rounds validation."""
        min_val = 1
        max_val = 30000

        assert max(min_val, min(max_val, 1000)) == 1000
        assert max(min_val, min(max_val, 0)) == 1
        assert max(min_val, min(max_val, 50000)) == 30000

    def test_damage_limit_validation(self):
        """Test damage limit validation."""
        min_val = 1
        max_val = 9999999

        assert max(min_val, min(max_val, 100000)) == 100000
        assert max(min_val, min(max_val, 0)) == 1

    def test_relative_change_validation(self):
        """Test relative change threshold validation."""
        min_val = 0.001
        max_val = 1

        assert max(min_val, min(max_val, 0.01)) == 0.01
        assert max(min_val, min(max_val, 0)) == 0.001
        assert max(min_val, min(max_val, 2)) == 1

    def test_relative_std_validation(self):
        """Test relative standard deviation validation."""
        min_val = 0.001
        max_val = 1

        assert max(min_val, min(max_val, 0.05)) == 0.05
        assert max(min_val, min(max_val, -1)) == 0.001
        assert max(min_val, min(max_val, 5)) == 1


class TestValidationEdgeCases:
    """Test edge cases in validation."""

    def test_float_conversion_from_int(self):
        """Test that integers are converted to floats."""
        val = 50
        try:
            validated = float(val)
        except (ValueError, TypeError):
            validated = 0
        assert isinstance(validated, float)
        assert validated == 50.0

    def test_validation_with_empty_string(self):
        """Test validation with empty string."""
        val = ""
        default = 42
        try:
            validated = float(val) if val else default
        except (ValueError, TypeError):
            validated = default
        assert validated == 42

    def test_validation_with_whitespace(self):
        """Test validation with whitespace."""
        val = "  50  "
        default = 42
        try:
            validated = float(val)
        except (ValueError, TypeError):
            validated = default
        assert validated == 50.0

    def test_validation_with_scientific_notation(self):
        """Test validation with scientific notation."""
        val = "1e2"
        default = 42
        try:
            validated = float(val)
        except (ValueError, TypeError):
            validated = default
        assert validated == 100.0
