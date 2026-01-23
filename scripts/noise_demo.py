#!/usr/bin/env python
"""
noise_demo.py

Run noise (per-iteration variance) DPS tests for weapon configurations and plot per-iteration DPS values.

Usage:
    python scripts\noise_demo.po --runs 100

The script expects a `weapons_config` dictionary (same shape as `ab_sweetspot.py`) and will run
`runs` independent simulations for each configured weapon/iteration, collecting the reported
`dps_crits` value from `DamageSimulator.simulate_dps()` each time.

Outputs:
    - A matplotlib plot showing DPS (Y) vs iteration number (X) for each configured iteration/weapon.
    - Returns a results dict mapping display_name -> list of DPS values.

Note: The file extension is ".po" because the request specified it; the file contains Python code and
can be executed with the python interpreter.
"""

from simulator.damage_simulator import DamageSimulator
from simulator.config import Config
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import time


def noise_demo(weapons_config, runs=100, show_plot=True):
    """
    Run `runs` independent DPS simulations for each entry in `weapons_config` and plot the per-run DPS.

    Parameters:
    - weapons_config: dict like in `ab_sweetspot.py` where each key is an iteration name and the value
                      is a dict of Config parameters. It may optionally include a literal `"weapon"`
                      key to specify the weapon name.
    - runs: int, number of independent simulation runs per iteration
    - show_plot: bool, whether to call plt.show() before returning

    Returns:
    - results: dict mapping display_name -> list of DPS floats (length == runs, or fewer if errors)
    """
    results = {}
    last_cfg = None  # Store last config for later use in plot labels

    print(f"Running noise demo: {len(weapons_config)} iterations, {runs} runs each")
    print("-" * 80)

    for iteration_name, iteration_params in weapons_config.items():
        # Determine weapon name and config params
        if isinstance(iteration_params, dict) and "weapon" in iteration_params:
            weapon_name = iteration_params["weapon"]
            display_name = iteration_name
            config_params = {k: v for k, v in iteration_params.items() if k != "weapon"}
        elif "___" in iteration_name:
            weapon_name, _ = iteration_name.split("___", 1)
            display_name = iteration_name
            config_params = iteration_params if isinstance(iteration_params, dict) else {}
        else:
            weapon_name = iteration_name
            display_name = iteration_name
            config_params = iteration_params if isinstance(iteration_params, dict) else {}

        print(f"\nAnalyzing iteration: {display_name} (weapon: {weapon_name})")
        # Prepare structure to hold both metrics per run
        results[display_name] = {"dps_crits": [], "dps_no_crits": []}

        # Create a fresh config for this iteration
        cfg = Config()
        last_cfg = cfg

        # Pull local copy of params so we don't mutate the original dict
        local_params = dict(config_params) if isinstance(config_params, dict) else {}

        # Handle AB_MODIFIER specially if present
        ab_modifier = 0
        if "AB_MODIFIER" in local_params:
            try:
                ab_modifier = int(local_params.get("AB_MODIFIER", 0))
            except Exception:
                ab_modifier = 0

        # Optionally allow the config to provide a starting AB via AB_BASE
        # If AB_BASE found, apply modifier to it; otherwise leave default cfg.AB
        if "AB_BASE" in local_params:
            try:
                cfg.AB = int(local_params["AB_BASE"]) + ab_modifier
            except Exception:
                pass
        else:
            # If AB explicitly provided, use it
            if "AB" in local_params:
                try:
                    cfg.AB = int(local_params["AB"]) + ab_modifier
                except Exception:
                    pass

        # Apply any custom Config parameters for this iteration
        for param_name, param_value in config_params.items():
            # Skip AB_MODIFIER as it's already been processed
            if param_name == "AB_MODIFIER":
                continue

            if hasattr(cfg, param_name):
                # Special handling for nested dictionaries like ADDITIONAL_DAMAGE
                if param_name == "ADDITIONAL_DAMAGE" and isinstance(param_value, dict):
                    # Create a fresh ADDITIONAL_DAMAGE dict instead of mutating shared default
                    fresh_additional_damage = dict(cfg.ADDITIONAL_DAMAGE)
                    fresh_additional_damage.update(param_value)
                    cfg.ADDITIONAL_DAMAGE = fresh_additional_damage
                    print(f"    Updating {param_name} with: {param_value}")
                else:
                    setattr(cfg, param_name, param_value)
                    print(f"    Setting {param_name} = {param_value}")
            else:
                print(f"    Warning: Config parameter '{param_name}' not found")

        for i in range(runs):
            if (i + 1) % max(1, runs // 5) == 0:
                print(f"  {display_name}: run {i + 1}/{runs}")

            try:
                # Run the simulation
                dps_calc = DamageSimulator(weapon_name, cfg)
                dps_result = dps_calc.simulate_dps()

                # Extract both metrics if present
                if isinstance(dps_result, dict):
                    dps_crits_val = dps_result.get("dps_crits", None)
                    dps_no_crits_val = dps_result.get("dps_no_crits", None)
                else:
                    dps_crits_val = None
                    dps_no_crits_val = None

                # Fallback to 0 if still None
                if dps_crits_val is None:
                    dps_crits_val = 0.0
                if dps_no_crits_val is None:
                    dps_no_crits_val = 0.0

                results[display_name]["dps_crits"].append(float(dps_crits_val))
                results[display_name]["dps_no_crits"].append(float(dps_no_crits_val))

            except Exception as e:
                # On error, append NaN and continue
                import traceback
                print(f"    Error on run {i+1} for {display_name}: {e}")
                traceback.print_exc()
                results[display_name]["dps_crits"].append(float('nan'))
                results[display_name]["dps_no_crits"].append(float('nan'))
                continue

    # Plotting: two subplots side-by-side with shared Y axis
    print("\nGenerating plot...")
    # Restore seaborn's modern visual theme (don't change the color palette)
    # Using 'darkgrid' with 'notebook' context gives the modern seaborn look
    sns.set_theme(style="darkgrid", context="notebook")

    num_series = len(results)
    fig, axs = plt.subplots(1, 2, figsize=(14, 7), sharey=True)

    # Prepare a color palette
    color_palette = sns.color_palette("husl", num_series if num_series > 0 else 1)

    # Compute global y-limits across both metrics for consistent scaling
    all_vals = []
    for series_dict in results.values():
        all_vals.extend([v for v in series_dict.get("dps_crits", []) if not pd.isna(v)])
        all_vals.extend([v for v in series_dict.get("dps_no_crits", []) if not pd.isna(v)])

    if len(all_vals) > 0:
        ymin = min(all_vals)
        ymax = max(all_vals)
    else:
        ymin, ymax = 0.0, 1.0

    # add small padding
    padding = max(0.01, (ymax - ymin) * 0.05)
    ymin_pad = ymin - padding
    ymax_pad = ymax + padding

    # Plot each series on both axes
    for series_idx, (series_name, series_dict) in enumerate(results.items()):
        color = color_palette[series_idx]
        series_name = series_name.replace("___", ": ").replace("_", " ")

        # Crits plot (left)
        crits_list = series_dict.get("dps_crits", [])
        df_crits = pd.DataFrame({"Iteration": list(range(1, len(crits_list) + 1)), "DPS": crits_list})
        if not df_crits.empty:
            sns.scatterplot(data=df_crits, x="Iteration", y="DPS", ax=axs[0], label=f"{series_name}", alpha=0.5, s=40, color=color)
            gp_sorted = df_crits.sort_values("Iteration")
            expanding = gp_sorted["DPS"].expanding(min_periods=1).mean()
            expanding_std = gp_sorted["DPS"].expanding(min_periods=1).std()
            expanding_count = gp_sorted["DPS"].expanding(min_periods=1).count()
            expanding_se = expanding_std / (expanding_count ** 0.5)
            axs[0].plot(gp_sorted["Iteration"], expanding, linewidth=2.2, color=color)
            axs[0].fill_between(gp_sorted["Iteration"], expanding - (expanding_se * 3), expanding + (expanding_se * 3), alpha=0.2, color=color)
            final_iteration = gp_sorted["Iteration"].iloc[-1]
            final_avg = expanding.iloc[-1]
            axs[0].annotate(f"{final_avg:.2f}", xy=(final_iteration, final_avg), xytext=(5, 5), textcoords="offset points", fontsize=9, bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.7))

        # No-crits plot (right)
        nocrits_list = series_dict.get("dps_no_crits", [])
        df_nocrits = pd.DataFrame({"Iteration": list(range(1, len(nocrits_list) + 1)), "DPS": nocrits_list})
        if not df_nocrits.empty:
            sns.scatterplot(data=df_nocrits, x="Iteration", y="DPS", ax=axs[1], label=f"{series_name}", alpha=0.5, s=40, color=color)
            gp_sorted2 = df_nocrits.sort_values("Iteration")
            expanding2 = gp_sorted2["DPS"].expanding(min_periods=1).mean()
            expanding_std2 = gp_sorted2["DPS"].expanding(min_periods=1).std()
            expanding_count2 = gp_sorted2["DPS"].expanding(min_periods=1).count()
            expanding_se2 = expanding_std2 / (expanding_count2 ** 0.5)
            axs[1].plot(gp_sorted2["Iteration"], expanding2, linewidth=2.2, color=color)
            axs[1].fill_between(gp_sorted2["Iteration"], expanding2 - (expanding_se2 * 3), expanding2 + (expanding_se2 * 3), alpha=0.2, color=color)
            final_iteration2 = gp_sorted2["Iteration"].iloc[-1]
            final_avg2 = expanding2.iloc[-1]
            axs[1].annotate(f"{final_avg2:.2f}", xy=(final_iteration2, final_avg2), xytext=(5, 5), textcoords="offset points", fontsize=9, bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.7))

    # Set shared labels and limits
    axs[0].set_title("Crit Allowed")
    axs[1].set_title("Crit Immune")
    axs[0].set_xlabel("DPS Dummy Iterations")
    axs[1].set_xlabel("DPS Dummy Iterations")
    axs[0].set_ylabel("DPS")
    axs[0].set_ylim(ymin_pad, ymax_pad)

    # Overall figure tweaks
    plt.suptitle(f"How Crappy is Your Dummy? ({target_ac} AC)", y=0.98)
    damage_k = int(last_cfg.DAMAGE_LIMIT/1000) if last_cfg else "Unknown"
    fig.text(0.5, 0.01, f"({damage_k}k damage per dummy)", ha='center')

    # Optionally show plot
    plt.tight_layout(rect=(0, 0.03, 1, 0.95))

    if show_plot:
        plt.show()

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run DPS noise demo for configured weapons")
    parser.add_argument("--runs", type=int, default=300, help="Number of runs per iteration")
    args = parser.parse_args()
    target_ac = 70

    # Example weapons_config similar to ab_sweetspot.py
    weapons_config = {
        # "Scythe___5APR_71AB": {
        #     "TARGET_AC": target_ac,
        #     "DAMAGE_LIMIT_FLAG": True,
        #     "AB": 71,
        #     "AB_PROG": "5APR Classic",
        #     "STR_MOD": 17,
        #     "COMBAT_TYPE": "melee",
        #     "TWO_HANDED": False,
        #     "ADDITIONAL_DAMAGE": {
        #         "Flame_Weapon": [False, {'fire_fw': [1, 4, 10]}],
        #         "Bard_Song": [True, {"physical": [0, 0, 5]}],
        #     },
        # },
        # "Heavy Flail___5APR_68AB": {
        #     "TARGET_AC": target_ac,
        #     "DAMAGE_LIMIT_FLAG": True,
        #     "AB": 68,
        #     "AB_PROG": "5APR Classic",
        #     "STR_MOD": 17,
        #     "COMBAT_TYPE": "melee",
        #     "TWO_HANDED": False,
        #     "ADDITIONAL_DAMAGE": {
        #         "Flame_Weapon": [False, {'fire_fw': [1, 4, 10]}],
        #         "Bard_Song": [True, {"physical": [0, 0, 5]}],
        #     },
        # },
        # "Dire Mace___5APR_69AB": {
        #     "TARGET_AC": target_ac,
        #     "DAMAGE_LIMIT_FLAG": True,
        #     "AB": 69,
        #     "AB_PROG": "5APR Classic",
        #     "STR_MOD": 17,
        #     "COMBAT_TYPE": "melee",
        #     "ADDITIONAL_DAMAGE": {
        #         "Flame_Weapon": [False, {'fire_fw': [1, 4, 10]}],
        #         "Bard_Song": [True, {"physical": [0, 0, 5]}],
        #         "Tenacious_Blow": [True, {'physical': [0, 0, 8]}],
        #     },
        # },
        # "Dire Mace___Dual-Wield_63AB(No-Rage)": {
        #     "TARGET_AC": target_ac,
        #     "DAMAGE_LIMIT_FLAG": True,
        #     "AB": 65,
        #     "AB_PROG": "5APR Dual-Wield",
        #     "STR_MOD": 16,
        #     "COMBAT_TYPE": "melee",
        #     "ADDITIONAL_DAMAGE": {
        #         "Flame_Weapon": [False, {'fire_fw': [1, 4, 10]}],
        #         "Bard_Song": [True, {"physical": [0, 0, 5]}],
        #         "Tenacious_Blow": [True, {'physical': [0, 0, 8]}],
        #     },
        # },
        # "Dire Mace___Dual-Wield_65AB(Yes-Rage)": {
        #     "TARGET_AC": target_ac,
        #     "DAMAGE_LIMIT_FLAG": True,
        #     "AB": 67,
        #     "AB_PROG": "5APR Dual-Wield",
        #     "STR_MOD": 16,
        #     "COMBAT_TYPE": "melee",
        #     "ADDITIONAL_DAMAGE": {
        #         "Flame_Weapon": [False, {'fire_fw': [1, 4, 10]}],
        #         "Bard_Song": [True, {"physical": [0, 0, 5]}],
        #         "Tenacious_Blow": [True, {'physical': [0, 0, 8]}],
        #     },
        # },
        "Longbow_FireDragon": {
            "TARGET_AC": target_ac,
            "DAMAGE_LIMIT_FLAG": True,
            "AB": 75,
            "AB_CAPPED": 77,
            "AB_PROG": "5APR & R.Shot & B.Speed",
            "STR_MOD": 7,
            "COMBAT_TYPE": "ranged",
            "MIGHTY": 7,
            "OVERWHELM_CRIT": True,
            "DEV_CRIT": True,
            "ADDITIONAL_DAMAGE": {
                "Flame_Weapon": [True, {'fire_fw': [1, 4, 10]}],
                "Bard_Song": [True, {"physical": [0, 0, 15]}],
            },
        },
        "Longbow_FireCeles": {
            "TARGET_AC": target_ac,
            "DAMAGE_LIMIT_FLAG": True,
            "AB": 75,
            "AB_CAPPED": 77,
            "AB_PROG": "5APR & R.Shot & B.Speed",
            "STR_MOD": 7,
            "COMBAT_TYPE": "ranged",
            "MIGHTY": 7,
            "OVERWHELM_CRIT": True,
            "DEV_CRIT": True,
            "ADDITIONAL_DAMAGE": {
                "Flame_Weapon": [True, {'fire_fw': [1, 4, 10]}],
                "Bard_Song": [True, {"physical": [0, 0, 15]}],
            },
        },
        "Longbow_ElecDragon": {
            "TARGET_AC": target_ac,
            "DAMAGE_LIMIT_FLAG": True,
            "AB": 75,
            "AB_CAPPED": 77,
            "AB_PROG": "5APR & R.Shot & B.Speed",
            "STR_MOD": 7,
            "COMBAT_TYPE": "ranged",
            "MIGHTY": 7,
            "OVERWHELM_CRIT": True,
            "DEV_CRIT": True,
            "ADDITIONAL_DAMAGE": {
                "Flame_Weapon": [True, {'fire_fw': [1, 4, 10]}],
                "Bard_Song": [True, {"physical": [0, 0, 15]}],
            },
        },
        "Longbow_ElecCeles": {
            "TARGET_AC": target_ac,
            "DAMAGE_LIMIT_FLAG": True,
            "AB": 75,
            "AB_CAPPED": 77,
            "AB_PROG": "5APR & R.Shot & B.Speed",
            "STR_MOD": 7,
            "COMBAT_TYPE": "ranged",
            "MIGHTY": 7,
            "OVERWHELM_CRIT": True,
            "DEV_CRIT": True,
            "ADDITIONAL_DAMAGE": {
                "Flame_Weapon": [True, {'fire_fw': [1, 4, 10]}],
                "Bard_Song": [True, {"physical": [0, 0, 15]}],
            },
        },
    }

    start = time.time()
    res = noise_demo(weapons_config, runs=args.runs, show_plot=True)
    elapsed = time.time() - start
    print(f"\nCompleted noise demo in {elapsed:.2f}s")

