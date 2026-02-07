from simulator.weapon import Weapon
from simulator.attack_simulator import AttackSimulator
from simulator.stats_collector import StatsCollector
from simulator.legend_effect import LegendEffect
from simulator.config import Config
from simulator.damage_roll import DamageRoll
from simulator.constants import PHYSICAL_DAMAGE_TYPES, DOUBLE_SIDED_WEAPONS
from copy import deepcopy
from collections import deque, defaultdict
import statistics
import math


class DamageSimulator:
    def __init__(self, weapon_chosen, config: Config, progress_callback=None):
        """Initialize DamageSimulator (legacy constructor).

        Note: For better testability, consider using SimulatorFactory.create_damage_simulator()
        which supports dependency injection.

        Args:
            weapon_chosen: Name of weapon to simulate
            config: Configuration instance
            progress_callback: Optional callback for progress updates
        """
        self.cfg = config
        self.stats = StatsCollector()   # Create object for collecting statistics
        self.weapon = Weapon(weapon_chosen, config=self.cfg)  # Pass Config instance to Weapon

        # Create offhand weapon if custom offhand is enabled
        self.offhand_weapon = None
        if self.cfg.DUAL_WIELD and self.cfg.CUSTOM_OFFHAND_WEAPON:
            self.offhand_weapon = Weapon(self.cfg.OFFHAND_WEAPON, config=self.cfg)

        self.attack_sim = AttackSimulator(
            weapon_obj=self.weapon,
            config=self.cfg,
            offhand_weapon_obj=self.offhand_weapon
        )
        self.legend_effect = LegendEffect(stats_obj=self.stats, weapon_obj=self.weapon, attack_sim=self.attack_sim)

        # Create separate legend effect for offhand if custom offhand is enabled
        self.offhand_legend_effect = None
        if self.offhand_weapon:
            self.offhand_legend_effect = LegendEffect(
                stats_obj=self.stats,
                weapon_obj=self.offhand_weapon,
                attack_sim=self.attack_sim
            )

        self.progress_callback = progress_callback

        self.dmg_type_names = []    # List of dmg type names, e.g., ['physical', 'acid']
        self.dmg_dict = {}    # Keys are dmg type names, Values are lists of DamageRoll objects
        self.dmg_dict_legend = {}  # Keys are dmg type names or 'proc'/'effect', Values are lists of DamageRoll or metadata
        self.collect_damage_sources_for_weapon(self.weapon, self.dmg_dict, self.dmg_dict_legend)

        # Collect offhand damage sources if custom offhand is enabled
        self.offhand_dmg_dict = {}
        self.offhand_dmg_dict_legend = {}
        if self.offhand_weapon:
            self.collect_damage_sources_for_weapon(self.offhand_weapon, self.offhand_dmg_dict, self.offhand_dmg_dict_legend)

        # Pre-compute damage structures to avoid deep copies in hot loop
        self.dmg_dict_base = deepcopy(self.dmg_dict)  # One-time deep copy
        self.offhand_dmg_dict_base = deepcopy(self.offhand_dmg_dict) if self.offhand_dmg_dict else {}

        # Convergence params, z-score lookup (normal distribution)
        z_values = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
        self.confidence = 0.99
        self.z = z_values.get(self.confidence, 2.576)
        self.window_size = 15

        # Convergence tracking - crit allowed
        self.total_dmg = 0
        self.dps_window = deque(maxlen=self.window_size)
        self.dps_rolling_avg = []
        self.dps_per_round = []
        self.cumulative_damage_per_round = []

        # Convergence tracking - crit immune
        self.total_dmg_crit_imm = 0
        self.dps_crit_imm_window = deque(maxlen=self.window_size)
        self.dps_crit_imm_rolling_avg = []
        self.dps_crit_imm_per_round = []
        self.cumulative_damage_by_type = {}

    def collect_damage_sources_for_weapon(self, weapon: Weapon, dmg_dict: dict, dmg_dict_legend: dict):
        """Collect damage information from a weapon's sources and organize into dictionaries.

        Args:
            weapon: The weapon to collect damage sources from
            dmg_dict: Dictionary to populate with damage types and DamageRoll objects
            dmg_dict_legend: Dictionary to populate with legendary damage data
        """
        damage_sources = weapon.aggregate_damage_sources()

        for src_name, dmg_source in damage_sources.items():
            if isinstance(dmg_source, dict):
                for key, val in dmg_source.items():
                    # Handling purple legendary damage specially
                    if key == 'legendary' and isinstance(val, dict):
                        for leg_key, leg_val in val.items():
                            if leg_key in ('proc', 'effect'):
                                dmg_dict_legend[leg_key] = leg_val
                                continue
                            if isinstance(leg_val, DamageRoll):
                                dmg_entry = leg_val
                            elif isinstance(leg_val, list):
                                dmg_entry = DamageRoll.from_list(leg_val)
                            else:
                                continue
                            dmg_dict_legend.setdefault(leg_key, []).append(dmg_entry)
                    else:
                        if isinstance(val, DamageRoll):
                            dmg_entry = val
                        elif isinstance(val, list):
                            dmg_entry = DamageRoll.from_list(val)
                        else:
                            continue

                        if key in PHYSICAL_DAMAGE_TYPES:
                            dmg_dict.setdefault('physical', []).append(dmg_entry)
                        else:
                            dmg_dict.setdefault(key, []).append(dmg_entry)

            elif isinstance(dmg_source, list):
                for item in dmg_source:
                    if isinstance(item, dict):
                        dmg_type_key, dmg_nums = next(iter(item.items()))
                        if isinstance(dmg_nums, DamageRoll):
                            dmg_entry = dmg_nums
                        elif isinstance(dmg_nums, list):
                            dmg_entry = DamageRoll.from_list(dmg_nums)
                        else:
                            continue
                        dmg_dict.setdefault(dmg_type_key, []).append(dmg_entry)

            else:
                print(f"Warning: Unrecognized damage source format for '{src_name}' on weapon '{weapon.name_purple}'.\n"
                      f"Damage source details: {dmg_source}.\n"
                      f"Skipping this source.")
                continue


    def _setup_dual_wield_tracking(self) -> dict:
        """Set up tracking indices for dual-wield strength bonus halving.

        Returns:
            Dictionary with:
            - is_dual_wield: bool
            - offhand_attack_indices: list of int (from attack_sim)
            - str_idx: int or None (index of STR damage in mainhand physical damage list)
            - offhand_str_idx: int or None (index of STR damage in offhand physical damage list)
        """
        if self.attack_sim.dual_wield:
            # Use offhand_attack_indices from attack_sim
            offhand_attack_indices = self.attack_sim.offhand_attack_indices

            str_dmg_roll = self.weapon.strength_bonus()['physical']  # Already a DamageRoll

            # Find the index for mainhand STR damage
            str_idx = None
            for idx, dmg_roll in enumerate(self.dmg_dict['physical']):
                if dmg_roll.dice == 0 and dmg_roll.sides == 0 and dmg_roll.flat == str_dmg_roll.flat:
                    str_idx = idx
                    break

            if str_idx is None:
                print(f"Warning: Could not find strength damage index in dual-wield setup")

            # Find the index for offhand STR damage if custom offhand is enabled
            offhand_str_idx = None
            if self.offhand_weapon and self.offhand_dmg_dict.get('physical'):
                offhand_str_dmg_roll = self.offhand_weapon.strength_bonus()['physical']
                for idx, dmg_roll in enumerate(self.offhand_dmg_dict['physical']):
                    if dmg_roll.dice == 0 and dmg_roll.sides == 0 and dmg_roll.flat == offhand_str_dmg_roll.flat:
                        offhand_str_idx = idx
                        break

            return {
                'is_dual_wield': True,
                'offhand_attack_indices': offhand_attack_indices,
                'str_idx': str_idx,
                'offhand_str_idx': offhand_str_idx,
            }
        else:
            return {
                'is_dual_wield': False,
                'offhand_attack_indices': [],
                'str_idx': None,
                'offhand_str_idx': None,
            }


    def _calculate_final_statistics(self, round_num: int) -> dict:
        """Calculate final DPS statistics after simulation completes.

        Args:
            round_num: Number of rounds simulated

        Returns:
            Dictionary with all calculated statistics
        """
        # Invalid DW config, no results to show - set all to zeroes
        if not self.attack_sim.valid_dual_wield_config:
            return {
                'dps_mean': 0,
                'dps_stdev': 0,
                'dps_error': 0,
                'dps_crit_imm_mean': 0,
                'dps_crit_imm_stdev': 0,
                'dps_crit_imm_error': 0,
                'dps_both': 0,
                'dpr': 0,
                'dpr_crit_imm': 0,
                'dph': 0,
                'dph_crit_imm': 0,
            }

        # DPS values (crit allowed)
        dps_mean = statistics.mean(self.dps_per_round)
        dps_stdev = statistics.stdev(self.dps_per_round) if round_num > 1 else 0
        dps_error = self.z * (dps_stdev / math.sqrt(round_num))

        # DPS values (crit immune)
        dps_crit_imm_mean = statistics.mean(self.dps_crit_imm_per_round)
        dps_crit_imm_stdev = statistics.stdev(self.dps_crit_imm_per_round) if round_num > 1 else 0
        dps_crit_imm_error = self.z * (dps_crit_imm_stdev / math.sqrt(round_num))

        # Averaging crit-allowed and crit-immune
        dps_both = (dps_mean + dps_crit_imm_mean) / 2

        # Damage per round and per hit
        dpr = self.total_dmg / round_num
        dpr_crit_imm = self.total_dmg_crit_imm / round_num
        dph = self.total_dmg / self.stats.hits
        dph_crit_imm = self.total_dmg_crit_imm / self.stats.hits

        return {
            'dps_mean': dps_mean,
            'dps_stdev': dps_stdev,
            'dps_error': dps_error,
            'dps_crit_imm_mean': dps_crit_imm_mean,
            'dps_crit_imm_stdev': dps_crit_imm_stdev,
            'dps_crit_imm_error': dps_crit_imm_error,
            'dps_both': dps_both,
            'dpr': dpr,
            'dpr_crit_imm': dpr_crit_imm,
            'dph': dph,
            'dph_crit_imm': dph_crit_imm,
        }

    def convergence(self, round_num) -> bool:
        dps_window_mean = statistics.mean(self.dps_window)
        dps_window_stdev = statistics.stdev(self.dps_window)

        # STD check with 'dynamic_window' values
        relative_std = dps_window_stdev / dps_window_mean

        # Relative change check with 'dynamic_window' values
        relative_change = (max(self.dps_window) - min(self.dps_window)) / dps_window_mean

        # Convergence check
        if relative_std < self.cfg.STD_THRESHOLD and relative_change < self.cfg.CHANGE_THRESHOLD:
            print(f"Converged after {round_num} rounds ({self.confidence * 100}% CI).")
            return True

        else:
            return False

    def simulate_dps(self):
        self.stats.init_zeroes_lists(self.attack_sim.attacks_per_round)
        total_rounds = self.cfg.ROUNDS
        round_num = 0
        legend_imm_factors = None
        offhand_legend_imm_factors = None

        # Set up dual-wield tracking indices
        dw_tracking = self._setup_dual_wield_tracking()
        offhand_attack_indices = dw_tracking['offhand_attack_indices']
        str_idx = dw_tracking['str_idx']
        offhand_str_idx = dw_tracking['offhand_str_idx']

        # Check if we have a custom offhand weapon
        has_custom_offhand = self.offhand_weapon is not None

        for round_num in range(1, total_rounds + 1):
            total_round_dmg = 0
            total_round_dmg_crit_imm = 0

            if not self.attack_sim.valid_dual_wield_config:  # Cannot Dual-Wield with this character size and weapon size combination
                break


            for attack_idx, attack_ab in enumerate(self.attack_sim.attack_prog):
                self.stats.attempts_made += 1
                self.stats.attempts_made_per_attack[attack_idx] += 1

                # Determine if this is an offhand attack
                is_offhand_attack = attack_idx in offhand_attack_indices

                # Get appropriate legend effect bonuses based on attack type
                if is_offhand_attack and has_custom_offhand:
                    legend_ab_bonus = self.offhand_legend_effect.ab_bonus
                    legend_ac_reduction = self.offhand_legend_effect.ac_reduction
                else:
                    legend_ab_bonus = self.legend_effect.ab_bonus
                    legend_ac_reduction = self.legend_effect.ac_reduction

                # Apply AB cap based on mainhand or offhand
                if is_offhand_attack:
                    ab_cap = self.attack_sim.offhand_ab_capped
                else:
                    ab_cap = self.attack_sim.ab_capped

                current_ab = min(attack_ab + legend_ab_bonus, ab_cap)

                # Determine crit_threat for this attack
                if is_offhand_attack and has_custom_offhand:
                    crit_threat = self.offhand_weapon.crit_threat
                else:
                    crit_threat = None  # Use mainhand default

                outcome, roll = self.attack_sim.attack_roll(current_ab, defender_ac_modifier=legend_ac_reduction, crit_threat=crit_threat)

                if outcome == 'miss':  # Attack missed the opponent, no damage is added
                    # Check for Tenacious Blow (only for mainhand with double-sided weapons)
                    active_weapon = self.offhand_weapon if (is_offhand_attack and has_custom_offhand) else self.weapon
                    if ("Tenacious_Blow" in self.cfg.ADDITIONAL_DAMAGE
                            and self.cfg.ADDITIONAL_DAMAGE["Tenacious_Blow"][0] is True
                            and active_weapon.name_base in DOUBLE_SIDED_WEAPONS):
                        dmg_dict = {'pure': [DamageRoll(dice=0, sides=0, flat=4)]}
                        if legend_imm_factors is None:
                            legend_imm_factors = {}
                        dmg_sums = self.get_damage_results(dmg_dict, legend_imm_factors)
                        dmg_sums_crit_imm = dmg_sums
                        legend_dmg_sums = {}  # No legend damage on miss, even with Tenacious Blow
                    else:
                        continue

                else:  # Attack hits, critical hit logic is managed within this part:
                    self.stats.hits += 1
                    self.stats.hits_per_attack[attack_idx] += 1

                    # On Critical Hit damage is NOT multiplied(!), it is rolled multiple times!
                    # For offhand attacks: use mainhand's crit_multiplier (game mechanic)
                    crit_multiplier = 1 if outcome == 'hit' else self.weapon.crit_multiplier

                    # Get appropriate damage source and legend dict
                    if is_offhand_attack and has_custom_offhand:
                        # Use offhand weapon damage sources
                        legend_dmg_sums, legend_dmg_common, offhand_legend_imm_factors = (
                            self.offhand_legend_effect.get_legend_damage(self.offhand_dmg_dict_legend, crit_multiplier)
                        )
                        active_imm_factors = offhand_legend_imm_factors if offhand_legend_imm_factors else {}

                        # Use offhand damage dict
                        dmg_dict = {k: list(v) for k, v in self.offhand_dmg_dict_base.items()}

                        # Halve STR damage for offhand
                        if offhand_str_idx is not None and 'physical' in dmg_dict:
                            str_roll = dmg_dict['physical'][offhand_str_idx]
                            dmg_dict['physical'][offhand_str_idx] = DamageRoll(
                                dice=str_roll.dice,
                                sides=str_roll.sides,
                                flat=math.floor(str_roll.flat / 2)
                            )
                    else:
                        # Use mainhand weapon damage sources
                        legend_dmg_sums, legend_dmg_common, legend_imm_factors = (
                            self.legend_effect.get_legend_damage(self.dmg_dict_legend, crit_multiplier)
                        )
                        active_imm_factors = legend_imm_factors if legend_imm_factors else {}

                        # Use mainhand damage dict
                        dmg_dict = {k: list(v) for k, v in self.dmg_dict_base.items()}

                        # Halve STR damage for offhand attacks (when using same weapon)
                        if self.attack_sim.dual_wield and is_offhand_attack and str_idx is not None:
                            str_roll = dmg_dict['physical'][str_idx]
                            dmg_dict['physical'][str_idx] = DamageRoll(
                                dice=str_roll.dice,
                                sides=str_roll.sides,
                                flat=math.floor(str_roll.flat / 2)
                            )

                    def get_max_dmg(dmg_roll: DamageRoll) -> int:
                        """Calculate maximum possible damage from a DamageRoll."""
                        return dmg_roll.dice * dmg_roll.sides + dmg_roll.flat

                    dmg_sneak = dmg_dict.pop('sneak', [])                                      # Remove the 'Sneak Attack' dmg from crit multiplication
                    dmg_sneak_max = max(dmg_sneak, key=get_max_dmg, default=None)              # Find the highest 'sneak' dmg, can't stack Sneak Attacks

                    dmg_death = dmg_dict.pop('death', [])                                      # Remove the 'Death Attack' dmg from crit multiplication
                    dmg_death_max = max(dmg_death, key=get_max_dmg, default=None)              # Find the highest 'death' dmg, can't stack Death Attacks

                    dmg_massive = dmg_dict.pop('massive', [])                          # Remove the 'Massive Critical' dmg from crit multiplication
                    dmg_massive_max = max(dmg_massive, key=get_max_dmg, default=None)  # Find the highest 'massive' dmg, can't stack Massive Criticals

                    dmg_flameweap = dmg_dict.pop('fire_fw', [])                            # Remove the 'Flame Weapon' dmg from crit multiplication
                    dmg_flameweap_max = max(dmg_flameweap, key=get_max_dmg, default=None)  # Find the highest 'fire_fw' dmg, can't stack multiple on-hits

                    if legend_dmg_common:   # Checking if dict is NOT empty, then adding the legend common damage to ordinary damage dictionary
                        # legend_dmg_common format: Dict[str, List[DamageRoll]]
                        for dmg_type, dmg_rolls in legend_dmg_common.items():
                            dmg_dict.setdefault(dmg_type, []).extend(dmg_rolls)

                    # Use shallow copy
                    dmg_dict_crit_imm = {k: list(v) for k, v in dmg_dict.items()}

                    # Get active weapon for size-based calculations
                    active_weapon = self.offhand_weapon if (is_offhand_attack and has_custom_offhand) else self.weapon

                    if crit_multiplier > 1:     # Store an additional dictionary for damage without crit multiplication
                        self.stats.crit_hits += 1
                        self.stats.crits_per_attack[attack_idx] += 1
                        dmg_dict = {k: [i for i in v for _ in range(crit_multiplier)]
                                    for k, v in dmg_dict.items()}  # Copy dice information X times (X = crit multiplier)
                        if dmg_massive_max is not None:
                            dmg_dict['physical'].append(dmg_massive_max)  # Add 'Massive' again after dmg rolls have been multiplied

                        # Overwhelm Critical: Add bonus damage based on crit multiplier
                        if self.cfg.OVERWHELM_CRIT:
                            if crit_multiplier == 2:
                                overwhelm_dmg = DamageRoll(dice=1, sides=6)  # 1d6
                            elif crit_multiplier == 3:
                                overwhelm_dmg = DamageRoll(dice=2, sides=6)  # 2d6
                            else:  # crit_multiplier >= 4
                                overwhelm_dmg = DamageRoll(dice=3, sides=6)  # 3d6
                            dmg_dict.setdefault('physical', []).append(overwhelm_dmg)

                        # Devastating Critical: Add bonus pure damage based on weapon size
                        if self.cfg.DEV_CRIT:
                            if active_weapon.size in ['T', 'S']:  # Tiny or Small
                                dev_dmg = DamageRoll(dice=0, sides=0, flat=10)  # +10 pure damage
                            elif active_weapon.size == 'M':  # Medium
                                dev_dmg = DamageRoll(dice=0, sides=0, flat=20)  # +20 pure damage
                            else:  # Large or larger
                                dev_dmg = DamageRoll(dice=0, sides=0, flat=30)  # +30 pure damage
                            dmg_dict.setdefault('pure', []).append(dev_dmg)

                    if dmg_sneak_max is not None:   # Add 'Sneak Attack' again after crit dmg rolls have been multiplied
                        dmg_dict.setdefault('physical', []).append(dmg_sneak_max)
                        dmg_dict_crit_imm.setdefault('physical', []).append(dmg_sneak_max)

                    if dmg_death_max is not None:   # Add 'Death Attack' again after crit dmg rolls have been multiplied
                        dmg_dict.setdefault('physical', []).append(dmg_death_max)
                        dmg_dict_crit_imm.setdefault('physical', []).append(dmg_death_max)

                    if dmg_flameweap_max is not None:   # Add 'Flame Weapon' again after crit dmg rolls have been multiplied
                        dmg_dict.setdefault('fire', []).append(dmg_flameweap_max)
                        dmg_dict_crit_imm.setdefault('fire', []).append(dmg_flameweap_max)

                    dmg_sums = self.get_damage_results(dmg_dict, active_imm_factors)
                    dmg_sums_crit_imm = dmg_sums if crit_multiplier == 1 else self.get_damage_results(dmg_dict_crit_imm, active_imm_factors)

                attack_dmg = sum(dmg_sums.values()) + sum(legend_dmg_sums.values())
                attack_dmg_crit_imm = sum(dmg_sums_crit_imm.values()) + sum(legend_dmg_sums.values())

                # Update cumulative damage by type for plotting/analysis
                for k, v in dmg_sums.items():
                    self.cumulative_damage_by_type[k] = self.cumulative_damage_by_type.get(k, 0) + v
                for k, v in legend_dmg_sums.items():
                    self.cumulative_damage_by_type[k] = self.cumulative_damage_by_type.get(k, 0) + v

                total_round_dmg += attack_dmg
                total_round_dmg_crit_imm += attack_dmg_crit_imm

            self.total_dmg += total_round_dmg
            self.total_dmg_crit_imm += total_round_dmg_crit_imm

            # Track cumulative total damage per round for plotting
            self.cumulative_damage_per_round.append(self.total_dmg)

            # Current average DPS - crit allowed
            rolling_dpr = self.total_dmg / round_num
            rolling_dps = rolling_dpr / 6
            current_dps = total_round_dmg / 6
            self.dps_window.append(rolling_dps)
            self.dps_rolling_avg.append(rolling_dps)
            self.dps_per_round.append(current_dps)

            # Current average DPS - crit immune
            rolling_dpr_crit_imm = self.total_dmg_crit_imm / round_num
            rolling_dps_crit_imm = rolling_dpr_crit_imm / 6
            current_dps_crit_imm = total_round_dmg_crit_imm / 6
            self.dps_crit_imm_window.append(rolling_dps_crit_imm)
            self.dps_crit_imm_rolling_avg.append(rolling_dps_crit_imm)
            self.dps_crit_imm_per_round.append(current_dps_crit_imm)

            # Stop if damage limit is reached
            if self.cfg.DAMAGE_LIMIT_FLAG and self.total_dmg >= self.cfg.DAMAGE_LIMIT:
                print(f"\nDamage limit of {self.cfg.DAMAGE_LIMIT} reached at round {round_num}, stopping simulation.")
                break

            # Check for convergence
            if len(self.dps_window) >= self.window_size:
                if self.convergence(round_num):
                    break

        # Calculate final statistics
        stats = self._calculate_final_statistics(round_num)
        dps_mean = stats['dps_mean']
        dps_stdev = stats['dps_stdev']
        dps_error = stats['dps_error']
        dps_crit_imm_mean = stats['dps_crit_imm_mean']
        dps_crit_imm_stdev = stats['dps_crit_imm_stdev']
        dps_crit_imm_error = stats['dps_crit_imm_error']
        dps_both = stats['dps_both']
        dpr = stats['dpr']
        dpr_crit_imm = stats['dpr_crit_imm']
        dph = stats['dph']
        dph_crit_imm = stats['dph_crit_imm']

        warning_dupe = f">>> WARNING: Duplicate weapon damage bonus detected! Using higher damage values where applicable. <<<\n\n" if self.weapon.weapon_damage_stack_warning else ""
        error_invalid_dw = f">>> ERROR: Character size '{self.cfg.CHARACTER_SIZE}' cannot dual-wield '{self.weapon.name_base}'. Simulation skipped. <<<\n\n" if not self.attack_sim.valid_dual_wield_config else ""

        # Build offhand info for summary if custom offhand is enabled
        offhand_info = ""
        if self.offhand_weapon:
            # Offhand uses its own crit_threat but mainhand's crit_multiplier
            offhand_info = f" | Offhand: {self.offhand_weapon.name_purple} | Offhand Crit: {self.offhand_weapon.crit_threat}-20/x{self.weapon.crit_multiplier}"

        summary = (
            f"{warning_dupe}{error_invalid_dw}"
            f"AB: {self.attack_sim.attack_prog} | Weapon: {self.weapon.name_purple} | Crit: {self.weapon.crit_threat}-20/x{self.weapon.crit_multiplier}{offhand_info} | "
            f"Target AC: {self.cfg.TARGET_AC} | Rounds averaged: {round_num}\n"
            f"DPS (Crit allowed | immune): {dps_mean:.2f} ± {dps_error:.2f} | {dps_crit_imm_mean:.2f} ± {dps_crit_imm_error:.2f}\n"
            f"TOTAL damage inflicted (Crit allowed | immune): {self.total_dmg} | {self.total_dmg_crit_imm}\n"
            f"AVERAGE damage inflicted per HIT (Crit allowed | immune): {dph:.2f} | {dph_crit_imm:.2f}\n"
            f"AVERAGE damage inflicted per ROUND (Crit allowed | immune): {dpr:.2f} | {dpr_crit_imm:.2f}\n"
        )
        print(summary)

        self.stats.calc_rates_percentages()
        legend_proc_theoretical = self.attack_sim.get_legend_proc_rate_theoretical()

        return {
            "avg_dps_both": round(dps_both, 2),
            "dps_crits": round(dps_mean, 2),
            "dps_no_crits": round(dps_crit_imm_mean, 2),
            "dps_per_round": self.dps_per_round,
            "dps_rolling_avg": self.dps_rolling_avg,
            "cumulative_damage_per_round": self.cumulative_damage_per_round,
            "damage_by_type": self.cumulative_damage_by_type,
            "attack_prog": self.attack_sim.attack_prog,
            "hit_rate_actual": self.stats.hit_rate,
            "crit_rate_actual": self.stats.crit_hit_rate,
            "legend_proc_rate_actual": self.stats.legend_proc_rate,
            "hits_per_attack": self.stats.hits_per_attack,
            "crits_per_attack": self.stats.crits_per_attack,
            "hit_rate_theoretical": self.attack_sim.get_hit_chance() * 100,
            "crit_rate_theoretical": self.attack_sim.get_crit_chance() * 100,
            "legend_proc_rate_theoretical": legend_proc_theoretical * 100,
            "hit_rate_per_attack_theoretical": [x * 100 for x in self.attack_sim.hit_chance_list],
            "crit_rate_per_attack_theoretical": [x * 100 for x in self.attack_sim.crit_chance_list],
            "summary": summary,
        }

    def get_damage_results(self, damage_dict: dict, imm_factors: dict):
        """Calculate damage results from a dictionary of DamageRoll objects or legacy lists.

        Args:
            damage_dict: Dictionary with damage type keys and lists of DamageRoll objects or lists
            imm_factors: Dictionary of immunity/vulnerability factors

        Returns:
            Dictionary of damage sums by type after applying immunities
        """
        damage_sums = defaultdict(int)
        for dmg_key, dmg_list in damage_dict.items():
            for dmg_entry in dmg_list:
                # Handle both DamageRoll objects and legacy list format
                if isinstance(dmg_entry, DamageRoll):
                    dice = dmg_entry.dice
                    sides = dmg_entry.sides
                    flat = dmg_entry.flat
                elif isinstance(dmg_entry, list):
                    # Legacy list format [dice, sides] or [dice, sides, flat]
                    dice = dmg_entry[0]
                    sides = dmg_entry[1]
                    flat = dmg_entry[2] if len(dmg_entry) > 2 else 0
                else:
                    raise TypeError(f"Expected DamageRoll or list, got {type(dmg_entry)}")

                dmg_roll_results = self.attack_sim.damage_roll(dice, sides, flat)
                damage_sums[dmg_key] += dmg_roll_results

        # Convert back to regular dict before applying immunities
        damage_sums_dict = dict(damage_sums)

        # Finally, apply target immunities and vulnerabilities
        damage_sums_dict = self.attack_sim.damage_immunity_reduction(damage_sums_dict, imm_factors)

        return damage_sums_dict
