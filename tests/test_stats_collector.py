"""
Unit tests for the StatsCollector class from simulator/stats_collector.py

This test suite covers:
- StatsCollector initialization and default values
- List initialization with zeroes
- Rate and percentage calculations (hit rate, crit rate, legend proc rate)
- Per-attack statistics tracking and calculations
- Edge cases and boundary conditions (zero division handling)
"""

import pytest
from simulator.stats_collector import StatsCollector


class TestStatsCollectorInitialization:
    """Tests for StatsCollector class initialization and setup."""

    def test_valid_initialization(self):
        """Test that StatsCollector initializes with correct default values."""
        collector = StatsCollector()

        assert collector.attempts_made == 0
        assert collector.hits == 0
        assert collector.crit_hits == 0
        assert collector.legend_procs == 0
        assert collector.hit_rate == 0.0
        assert collector.crit_hit_rate == 0.0
        assert collector.legend_proc_rate == 0.0
        assert collector.attempts_made_per_attack == []
        assert collector.hits_per_attack == []
        assert collector.crits_per_attack == []

    def test_all_initial_values_are_zero_or_empty(self):
        """Test that all attributes start with zero or empty list values."""
        collector = StatsCollector()

        assert collector.attempts_made == 0
        assert collector.hits == 0
        assert collector.crit_hits == 0
        assert collector.legend_procs == 0
        assert isinstance(collector.hit_rate, float)
        assert isinstance(collector.crit_hit_rate, float)
        assert isinstance(collector.legend_proc_rate, float)
        assert isinstance(collector.attempts_made_per_attack, list)
        assert isinstance(collector.hits_per_attack, list)
        assert isinstance(collector.crits_per_attack, list)


class TestInitZeroesLists:
    """Tests for the init_zeroes_lists method."""

    def test_init_zeroes_lists_with_single_attack(self):
        """Test that init_zeroes_lists creates lists of correct length with single attack."""
        collector = StatsCollector()
        collector.init_zeroes_lists(1)

        assert len(collector.attempts_made_per_attack) == 1
        assert len(collector.hits_per_attack) == 1
        assert len(collector.crits_per_attack) == 1
        assert collector.attempts_made_per_attack == [0]
        assert collector.hits_per_attack == [0]
        assert collector.crits_per_attack == [0]

    def test_init_zeroes_lists_with_multiple_attacks(self):
        """Test that init_zeroes_lists creates correctly sized lists for multiple attacks."""
        collector = StatsCollector()
        list_length = 5
        collector.init_zeroes_lists(list_length)

        assert len(collector.attempts_made_per_attack) == list_length
        assert len(collector.hits_per_attack) == list_length
        assert len(collector.crits_per_attack) == list_length
        assert all(val == 0 for val in collector.attempts_made_per_attack)
        assert all(val == 0 for val in collector.hits_per_attack)
        assert all(val == 0 for val in collector.crits_per_attack)

    def test_init_zeroes_lists_with_large_length(self):
        """Test that init_zeroes_lists handles large list sizes correctly."""
        collector = StatsCollector()
        list_length = 100
        collector.init_zeroes_lists(list_length)

        assert len(collector.attempts_made_per_attack) == list_length
        assert len(collector.hits_per_attack) == list_length
        assert len(collector.crits_per_attack) == list_length

    def test_init_zeroes_lists_replaces_existing_lists(self):
        """Test that init_zeroes_lists replaces any previously set lists."""
        collector = StatsCollector()
        collector.init_zeroes_lists(3)

        # Manually modify lists
        collector.attempts_made_per_attack = [100, 200, 300]
        collector.hits_per_attack = [50, 75, 90]
        collector.crits_per_attack = [10, 15, 20]

        # Re-initialize with new length
        collector.init_zeroes_lists(2)

        assert len(collector.attempts_made_per_attack) == 2
        assert len(collector.hits_per_attack) == 2
        assert len(collector.crits_per_attack) == 2
        assert collector.attempts_made_per_attack == [0, 0]
        assert collector.hits_per_attack == [0, 0]
        assert collector.crits_per_attack == [0, 0]

    def test_init_zeroes_lists_with_zero_length(self):
        """Test that init_zeroes_lists handles edge case of zero length."""
        collector = StatsCollector()
        collector.init_zeroes_lists(0)

        assert len(collector.attempts_made_per_attack) == 0
        assert len(collector.hits_per_attack) == 0
        assert len(collector.crits_per_attack) == 0


class TestCalcRatesPercentages:
    """Tests for the calc_rates_percentages method."""

    def test_basic_rate_calculations(self):
        """Test basic calculations of hit rate, crit rate, and legend proc rate."""
        collector = StatsCollector()
        collector.attempts_made = 100
        collector.hits = 75
        collector.crit_hits = 15
        collector.legend_procs = 5

        collector.calc_rates_percentages()

        assert collector.hit_rate == 75.0
        assert collector.crit_hit_rate == 15.0
        assert collector.legend_proc_rate == round((5 / 75) * 100, 2)  # 6.67

    def test_hit_rate_calculation(self):
        """Test accurate hit rate percentage calculation."""
        collector = StatsCollector()
        collector.attempts_made = 1000
        collector.hits = 650

        collector.calc_rates_percentages()

        assert collector.hit_rate == 65.0

    def test_crit_rate_calculation(self):
        """Test accurate critical hit rate percentage calculation."""
        collector = StatsCollector()
        collector.attempts_made = 1000
        collector.hits = 500
        collector.crit_hits = 50
        collector.legend_procs = 0

        collector.calc_rates_percentages()

        assert collector.crit_hit_rate == 5.0

    def test_legend_proc_rate_calculation(self):
        """Test accurate legend proc rate percentage calculation."""
        collector = StatsCollector()
        collector.attempts_made = 100
        collector.hits = 100
        collector.crit_hits = 0
        collector.legend_procs = 25

        collector.calc_rates_percentages()

        expected_rate = round((25 / 100) * 100, 2)
        assert collector.legend_proc_rate == expected_rate
        assert collector.legend_proc_rate == 25.0

    def test_rates_are_rounded_to_correct_precision(self):
        """Test that rates are rounded to correct decimal places."""
        collector = StatsCollector()
        collector.attempts_made = 3
        collector.hits = 1
        collector.crit_hits = 0
        collector.legend_procs = 0

        collector.calc_rates_percentages()

        # (1/3)*100 = 33.333... rounded to 2 decimals = 33.33
        assert collector.hit_rate == 33.33
        assert isinstance(collector.hit_rate, float)

    def test_per_attack_hit_rate_calculations(self):
        """Test per-attack hit rate calculations for list of attacks."""
        collector = StatsCollector()
        collector.init_zeroes_lists(3)

        # Set up per-attack data
        collector.attempts_made_per_attack = [100, 200, 150]
        collector.hits_per_attack = [75, 160, 120]
        collector.crit_hits = 0
        collector.legend_procs = 0
        collector.attempts_made = 450
        collector.hits = 355

        collector.calc_rates_percentages()

        # Check per-attack hit rates (rounded to 1 decimal)
        assert collector.hits_per_attack[0] == 75.0
        assert collector.hits_per_attack[1] == 80.0
        assert collector.hits_per_attack[2] == 80.0

    def test_per_attack_crit_rate_calculations(self):
        """Test per-attack critical hit rate calculations for list of attacks."""
        collector = StatsCollector()
        collector.init_zeroes_lists(3)

        # Set up per-attack data
        collector.attempts_made_per_attack = [100, 100, 100]
        collector.crits_per_attack = [10, 5, 20]
        collector.crit_hits = 35
        collector.attempts_made = 300
        collector.hits = 100
        collector.legend_procs = 0

        collector.calc_rates_percentages()

        # Check per-attack crit rates (rounded to 1 decimal)
        assert collector.crits_per_attack[0] == 10.0
        assert collector.crits_per_attack[1] == 5.0
        assert collector.crits_per_attack[2] == 20.0

    def test_per_attack_calculations_with_varying_attempts(self):
        """Test per-attack calculations with different attempt counts per attack."""
        collector = StatsCollector()
        collector.init_zeroes_lists(2)

        collector.attempts_made_per_attack = [100, 50]
        collector.hits_per_attack = [50, 40]
        collector.crits_per_attack = [10, 5]
        collector.crit_hits = 15
        collector.attempts_made = 150
        collector.hits = 90
        collector.legend_procs = 2

        collector.calc_rates_percentages()

        assert collector.hits_per_attack[0] == 50.0
        assert collector.hits_per_attack[1] == 80.0
        assert collector.crits_per_attack[0] == 10.0
        assert collector.crits_per_attack[1] == 10.0

    def test_calculation_with_zero_attempts(self):
        """Test calculation behavior when attempts_made is zero (edge case)."""
        collector = StatsCollector()
        collector.attempts_made = 0
        collector.hits = 0
        collector.crit_hits = 0
        collector.legend_procs = 0

        # This should return early without raising an error
        collector.calc_rates_percentages()

    def test_calculation_with_zero_hits_legend_proc(self):
        """Test calculation behavior when hits is zero for legend proc rate."""
        collector = StatsCollector()
        collector.attempts_made = 100
        collector.hits = 0
        collector.crit_hits = 10
        collector.legend_procs = 0

        # This should return early without raising an error
        collector.calc_rates_percentages()

    def test_calculation_preserves_list_length(self):
        """Test that calculation doesn't change per-attack list lengths."""
        collector = StatsCollector()
        collector.init_zeroes_lists(5)

        collector.attempts_made_per_attack = [50] * 5
        collector.hits_per_attack = [25] * 5
        collector.crits_per_attack = [5] * 5
        collector.crit_hits = 25
        collector.attempts_made = 250
        collector.hits = 125
        collector.legend_procs = 0

        collector.calc_rates_percentages()

        assert len(collector.hits_per_attack) == 5
        assert len(collector.crits_per_attack) == 5
        assert len(collector.attempts_made_per_attack) == 5


class TestRealWorldScenarios:
    """Tests simulating real-world combat scenarios."""

    def test_typical_combat_statistics(self):
        """Test a typical combat scenario with realistic numbers."""
        collector = StatsCollector()
        collector.attempts_made = 1000
        collector.hits = 625
        collector.crit_hits = 50
        collector.legend_procs = 10

        collector.calc_rates_percentages()

        assert collector.hit_rate == 62.5
        assert collector.crit_hit_rate == 5.0
        assert collector.legend_proc_rate == round((10 / 625) * 100, 2)

    def test_dual_attack_scenario(self):
        """Test combat with two attack sequences (main hand and off-hand)."""
        collector = StatsCollector()
        collector.init_zeroes_lists(2)

        # Main hand attack statistics
        collector.attempts_made_per_attack[0] = 100
        collector.hits_per_attack[0] = 80
        collector.crits_per_attack[0] = 8

        # Off-hand attack statistics (lower hit rate due to penalties)
        collector.attempts_made_per_attack[1] = 100
        collector.hits_per_attack[1] = 60
        collector.crits_per_attack[1] = 5

        collector.attempts_made = 200
        collector.hits = 140
        collector.crit_hits = 13
        collector.legend_procs = 2

        collector.calc_rates_percentages()

        assert collector.hit_rate == 70.0
        assert collector.crit_hit_rate == 6.5
        assert collector.hits_per_attack[0] == 80.0
        assert collector.hits_per_attack[1] == 60.0

    def test_high_accuracy_build(self):
        """Test statistics for a high-accuracy character build."""
        collector = StatsCollector()
        collector.attempts_made = 500
        collector.hits = 475
        collector.crit_hits = 35
        collector.legend_procs = 8

        collector.calc_rates_percentages()

        assert collector.hit_rate == 95.0
        assert collector.crit_hit_rate == 7.0
        assert collector.legend_proc_rate == round((8 / 475) * 100, 2)

    def test_low_accuracy_build(self):
        """Test statistics for a lower-accuracy character build."""
        collector = StatsCollector()
        collector.attempts_made = 500
        collector.hits = 250
        collector.crit_hits = 10
        collector.legend_procs = 1

        collector.calc_rates_percentages()

        assert collector.hit_rate == 50.0
        assert collector.crit_hit_rate == 2.0
        assert collector.legend_proc_rate == round((1 / 250) * 100, 2)


class TestStateModificationAndRecalculation:
    """Tests for modifying state and recalculating statistics."""

    def test_recalculation_after_state_change(self):
        """Test that recalculating with new values updates all rates correctly."""
        collector = StatsCollector()
        collector.attempts_made = 100
        collector.hits = 50
        collector.crit_hits = 5
        collector.legend_procs = 1

        collector.calc_rates_percentages()
        first_hit_rate = collector.hit_rate

        # Modify state
        collector.attempts_made = 200
        collector.hits = 180
        collector.crit_hits = 20
        collector.legend_procs = 5

        collector.calc_rates_percentages()

        assert collector.hit_rate == 90.0
        assert collector.hit_rate != first_hit_rate

    def test_per_attack_data_accumulation(self):
        """Test accumulating per-attack data over multiple calls."""
        collector = StatsCollector()
        collector.init_zeroes_lists(2)

        # Simulate first round of data collection
        collector.attempts_made_per_attack[0] += 50
        collector.attempts_made_per_attack[1] += 40
        collector.hits_per_attack[0] += 40
        collector.hits_per_attack[1] += 30

        assert collector.hits_per_attack[0] == 40
        assert collector.hits_per_attack[1] == 30

    def test_multiple_sequential_calculations(self):
        """Test that multiple sequential calculations work correctly."""
        collector = StatsCollector()

        # First calculation
        collector.attempts_made = 100
        collector.hits = 75
        collector.crit_hits = 10
        collector.legend_procs = 0
        collector.calc_rates_percentages()

        assert collector.hit_rate == 75.0

        # Second calculation with new data
        collector.attempts_made = 200
        collector.hits = 140
        collector.crit_hits = 15
        collector.legend_procs = 2
        collector.calc_rates_percentages()

        assert collector.hit_rate == 70.0
        assert collector.legend_proc_rate == round((2 / 140) * 100, 2)

