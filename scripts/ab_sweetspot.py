from simulator.damage_simulator import DamageSimulator
from simulator.config import Config
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def ab_sweetspot(weapons_config, ab_values):
    """
    Analyze DPS across different AB values for each weapon with custom Config parameters.

    Parameters:
    - weapons_config: Dictionary where keys are iteration names and values are dicts of Config parameters
      The weapon can be specified in two ways:

      Option 1: Include 'weapon' key in the config dictionary
      {
          "iteration_1": {
              "weapon": "Kama",
              "AB_PROG": "Monk Kama & Dual-Wield & Flurry",
          },
          "iteration_2": {
              "weapon": "Gloves_Adam",
              "AB_PROG": "Monk APR & Flurry",
          },
      }

      Option 2: Use triple underscore to append iteration ID to weapon name
      {
          "Kama___rapid": {
              "AB_PROG": "Monk Kama & Dual-Wield & Flurry",
          },
          "Kama___slow": {
              "AB_PROG": "Monk APR & Flurry",
          },
      }

      Special parameters:
      - AB_MODIFIER: (int) Adjustment applied to each AB value (e.g., -2 to reduce by 2)
        Example: "AB_MODIFIER": -2

    - ab_values: List of AB values to test

    Creates one plot with all iterations showing DPS vs AB values.
    """
    results = {}

    print(f"Running AB sweetspot analysis for {len(weapons_config)} iterations with AB values: {ab_values}")
    print("-" * 80)

    # Run simulations for each iteration and AB value combination
    for iteration_name, iteration_params in weapons_config.items():
        # Determine weapon name - either from 'weapon' key or by parsing triple underscore
        if "weapon" in iteration_params:
            weapon_name = iteration_params["weapon"]
            display_name = iteration_name
            # Create a copy without the 'weapon' key for processing other params
            config_params = {k: v for k, v in iteration_params.items() if k != "weapon"}
        elif "___" in iteration_name:
            # Parse weapon___iteration format
            weapon_name, iteration_id = iteration_name.split("___", 1)
            display_name = iteration_name
            config_params = iteration_params
        else:
            # If no weapon specified and no triple underscore, use iteration_name as weapon
            weapon_name = iteration_name
            display_name = iteration_name
            config_params = iteration_params

        print(f"\nAnalyzing iteration: {display_name} (weapon: {weapon_name})")
        results[display_name] = {"ab_values": [], "dps_values": []}

        for ab_value in ab_values:
            print(f"  Testing AB value: {ab_value}")
            try:
                # Create a fresh config instance for each AB value to ensure proper isolation
                cfg = Config()

                # Extract AB_MODIFIER if present (will be removed from config_params before setting)
                ab_modifier = 0
                if "AB_MODIFIER" in config_params:
                    ab_modifier = config_params["AB_MODIFIER"]
                    print(f"    AB_MODIFIER found: {ab_modifier}")

                # Set the AB value with modifier applied
                cfg.AB = ab_value + ab_modifier
                print(f"    Effective AB: {ab_value} + {ab_modifier} = {cfg.AB}")

                # Apply any custom Config parameters for this iteration
                for param_name, param_value in config_params.items():
                    # Skip AB_MODIFIER as it's already been processed
                    if param_name == "AB_MODIFIER":
                        continue

                    if hasattr(cfg, param_name):
                        # Special handling for nested dictionaries like ADDITIONAL_DAMAGE
                        if param_name == "ADDITIONAL_DAMAGE" and isinstance(param_value, dict):
                            # Merge with existing ADDITIONAL_DAMAGE instead of replacing
                            cfg.ADDITIONAL_DAMAGE.update(param_value)
                            print(f"    Updating {param_name} with: {param_value}")
                        else:
                            setattr(cfg, param_name, param_value)
                            print(f"    Setting {param_name} = {param_value}")
                    else:
                        print(f"    Warning: Config parameter '{param_name}' not found")

                # Run DamageSimulator with the current AB value
                dps_calculator = DamageSimulator(weapon_name, cfg)
                dps_result = dps_calculator.simulate_dps()

                # Extract the DPS (crit allowed)
                dps = dps_result.get('dps_crits', 0)

                results[display_name]["ab_values"].append(ab_value)
                results[display_name]["dps_values"].append(dps)

                print(f"    DPS at AB {ab_value} (effective AB: {cfg.AB}): {dps:.2f}\n---\n")
            except Exception as e:
                print(f"    Error testing iteration {display_name} (weapon: {weapon_name}) with AB {ab_value}: {e}")
                continue

    print("\n" + "-" * 80)
    print("Generating combined plot...")

    # Create a single plot with all weapons
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot all weapons on the same chart with different colors
    for weapon, data in results.items():
        df = pd.DataFrame({
            "AB Value": data["ab_values"],
            "DPS": data["dps_values"]
        })
        sns.lineplot(data=df, x="AB Value", y="DPS", ax=ax, marker='o', linewidth=2.5, markersize=8, label=weapon)

    ax.set_title("DPS vs AB", fontsize=14, fontweight='bold')
    ax.set_xlabel("AB", fontsize=12)
    ax.set_ylabel("Average DPS (Crit Allowed)", fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11, loc='best')

    # Format X-axis to show integers only
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

    plt.tight_layout()
    plt.show()

    return results


if __name__ == "__main__":
    # Define weapons with custom Config parameters for each iteration
    weapons_config = {
        "Scimitar___5APR_69AB": {
            # "DAMAGE_LIMIT_FLAG": True,
            "AB_PROG": "5APR Classic",
            "STR_MOD": 17,
            "COMBAT_TYPE": "melee",
            "ADDITIONAL_DAMAGE": {
                "Flame_Weapon": [False, {'fire_fw': [1, 4, 10]}],
                "Bard_Song": [True, {"physical": [0, 0, 5]}],
            },
        },
        "Scimitar___Dual-Wield_65AB": {
            # "DAMAGE_LIMIT_FLAG": True,
            "AB_PROG": "5APR Dual-Wield",
            "STR_MOD": 17,
            "COMBAT_TYPE": "melee",
            "ADDITIONAL_DAMAGE": {
                "Flame_Weapon": [False, {'fire_fw': [1, 4, 10]}],
                "Bard_Song": [True, {"physical": [0, 0, 5]}],
            },
        },
        # "Gloves_Shandy": {
        #     "AB_PROG": "Monk APR & Flurry",
        #     "STR_MOD": 6,
        #     "COMBAT_TYPE": "melee",
        #     "ADDITIONAL_DAMAGE": {
        #         "Death_Attack": [True, {'death': [15, 6, 0]}]
        #     },
        # },
    }

    # weapons_config = {
    #     "Longbow_5APR_Rapid": {
    #         "weapon": "Longbow",
    #         "AB_PROG": "5APR & Rapid Shot",
    #         "STR_MOD": 6,
    #         "COMBAT_TYPE": "ranged",
    #         "MIGHTY": True,
    #     },
    #     "Longbow_5APR_Rapid_BlindSpeed": {
    #         "weapon": "Longbow",
    #         "AB_PROG": "5APR & R.Shot & B.Speed",
    #         "STR_MOD": 6,
    #         "COMBAT_TYPE": "ranged",
    #         "MIGHTY": True,
    #         "AB_MODIFIER": -2,  # Reduce AB by 2 due to Blinding Speed penalty
    #     },
    # }

    ab_range = list(range(45, 70))  # AB values from 54 to 73
    sim_results = ab_sweetspot(weapons_config, ab_range)

