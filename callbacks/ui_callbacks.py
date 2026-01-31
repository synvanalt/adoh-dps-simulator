# Third-party imports
import dash
from dash import Input, Output, ALL, MATCH, State, ctx, ClientsideFunction

# Local imports
from simulator.config import Config
from weapons_db import WEAPON_PROPERTIES, PURPLE_WEAPONS



def register_ui_callbacks(app, cfg):

    # Clientside callback: Immediately show spinner when reset buttons are clicked
    app.clientside_callback(
        ClientsideFunction(
            namespace='build_switching',
            function_name='show_spinner_on_reset_click'
        ),
        Output('loading-overlay', 'style', allow_duplicate=True),
        Input('reset-button', 'n_clicks'),
        Input('sticky-reset-button', 'n_clicks'),
        prevent_initial_call=True
    )

    # Callback: toggle additional damage inputs visibility
    @app.callback(
        Output({'type': 'add-dmg-row', 'name': MATCH}, 'style'),
        Input({'type': 'add-dmg-switch', 'name': MATCH}, 'value'),
    )
    def toggle_additional_damage(show):
        style = {'display': 'flex'} if show else {'display': 'none'}
        return style


    # Callback: update reference information
    # Shows weapons from ALL builds (deduplicated) in the Reference Info tab
    @app.callback(
        [Output('weapon-properties', 'children'),
         Output('purple-weapons', 'children'),
         Output('target-immunities', 'children')],
        [Input('simulate-button', 'n_clicks'),
         Input('resimulate-button', 'n_clicks'),
         Input('sticky-simulate-button', 'n_clicks'),
         Input('weapon-dropdown', 'value'),
         Input('shape-weapon-switch', 'value'),
         Input('shape-weapon-dropdown', 'value'),
         Input({'type': 'immunity-input', 'name': ALL}, 'value'),
         Input('builds-store', 'data')],
        State('build-loading', 'data'),
        prevent_initial_call=True
    )
    def update_reference_info(_, __, ___, current_dropdown_weapons, shape_weapon_override, shape_weapon, immunity_values, builds, is_loading):
        # Skip during build loading to prevent callback cascade
        if is_loading:
            return dash.no_update, dash.no_update, dash.no_update

        # Collect unique weapons from ALL builds + current dropdown (deduplicated, preserving order)
        # This ensures we show:
        # 1. Current dropdown selection (may have unsaved changes)
        # 2. Weapons from other saved builds in builds-store
        all_weapons = []
        seen = set()

        # First, add current dropdown selection (active build's current state)
        if current_dropdown_weapons:
            for w in current_dropdown_weapons:
                if w not in seen:
                    seen.add(w)
                    all_weapons.append(w)

        # Then, add weapons from all saved builds (other builds)
        if builds:
            for build in builds:
                build_weapons = build.get('config', {}).get('WEAPONS', [])
                if build_weapons:
                    for w in build_weapons:
                        if w not in seen:
                            seen.add(w)
                            all_weapons.append(w)

        selected_weapons = all_weapons

        if not selected_weapons:
            return "No weapon selected", str(cfg.TARGET_IMMUNITIES), "No weapon selected"

        # Format weapon properties for all selected weapons
        base_weapon_props = []
        for weapon in selected_weapons:
            base_weapon = weapon.split('_')[0]

            if shape_weapon_override:  # Override the weapon properties with the selected shape weapon
                base_weapon = shape_weapon
                override_msg = f" (overwritten with '{base_weapon}')"
            else:
                override_msg = ""

            props = WEAPON_PROPERTIES.get(base_weapon, "Weapon not found")
            props_name = f"{weapon}{override_msg}:"
            props_dmg = f"{props['dmg'][0]}d{props['dmg'][1]}"
            props_dmg_type = f"{props['dmg'][2].title()}"
            props_crit = f"Crit: {props['threat']}-20/x{props['multiplier']}"
            props_size = f"Size: {props['size']}"
            base_weapon_props.append((props_name, props_dmg, props_dmg_type, props_crit, props_size))

        # Format purple weapon information for all selected weapons
        purple_weapon_props = []
        for weapon in selected_weapons:
            properties = PURPLE_WEAPONS.get(weapon, {})
            props_name = f"{weapon}:"
            props_dmg = []

            # properties now a dict mapping dmg-type -> params
            for key, val in properties.items():
                if key == 'enhancement':
                    props_dmg.append(f"+{val} {key.title()}")

                elif key == 'legendary' and isinstance(val, dict):
                    proc = val.get('proc')
                    proc_str = f"On-Hit {int(proc * 100)}%" if isinstance(proc, (int, float)) else ("On-Crit" if proc == 'on_crit' else str(proc))
                    # handle effect key separately
                    for leg_key, leg_val in val.items():
                        if leg_key == 'proc':
                            continue
                        if leg_key == 'effect':
                            props_dmg.append(f"{proc_str}: {leg_val.replace('_', ' ').title()}")
                            continue
                        # leg_val expected to be [dice, sides] or [dice, sides, flat]
                        dice = leg_val[0]
                        sides = leg_val[1]
                        flat = leg_val[2] if len(leg_val) > 2 else None
                        if dice == 0 and flat:
                            props_dmg.append(f"{proc_str}: {flat} {leg_key.title()}")
                        elif dice > 0 and flat:
                            props_dmg.append(f"{proc_str}: {dice}d{sides}+{flat} {leg_key.title()}")
                        else:
                            props_dmg.append(f"{proc_str}: {dice}d{sides} {leg_key.title()}")

                else:
                    # val can be a list [dice, sides]/[dice, sides, flat] or dict (vs_race mapping)
                    if "vs_race" in key and isinstance(val, dict):
                        # vs_race entry; val is {actual_type: [dice, sides]}
                        for sub_key, sub_val in val.items():
                            if sub_key == 'enhancement':
                                props_dmg.append(f"+{sub_val} {sub_key.title()} (vs. race)")
                            else:
                                dice = sub_val[0]
                                sides = sub_val[1]
                                flat = sub_val[2] if len(sub_val) > 2 else None
                                if dice == 0 and flat:
                                    props_dmg.append(f"{flat} {sub_key.title()} (vs. race)")
                                elif dice > 0 and flat:
                                    props_dmg.append(f"{dice}d{sides}+{flat} {sub_key.title()} (vs. race)")
                                else:
                                    props_dmg.append(f"{dice}d{sides} {sub_key.title()} (vs. race)")
                    else:
                        dice = val[0]
                        sides = val[1]
                        flat = val[2] if len(val) > 2 else None
                        if dice == 0 and flat:
                            props_dmg.append(f"{flat} {key.title()}")
                        elif dice > 0 and flat:
                            props_dmg.append(f"{dice}d{sides}+{flat} {key.title()}")
                        else:
                            props_dmg.append(f"{dice}d{sides} {key.title()}")

            # props_dmg = ", ".join(props_dmg)
            # purple_weapon_props.append((props_name, str(props_dmg)))
            purple_weapon_props.append((props_name, *props_dmg))

        def prettify_text(text):
            """Helper function to align text in columns for better readability
               Works even if rows have different lengths."""
            # Find max number of columns across all rows
            max_cols = max(len(row) for row in text)
            # Compute column widths considering only rows that have that column
            col_widths = []
            for i in range(max_cols):
                max_width = max(len(row[i]) for row in text if i < len(row))
                col_widths.append(max_width)
            # Format each row, padding only existing columns
            formatted_lines = []
            for row in text:
                line = "  ".join(
                    row[i].ljust(col_widths[i]) for i in range(len(row))
                )
                formatted_lines.append(line)
            return "\n".join(formatted_lines)

        # Map immunity inputs back into a dictionary (normalize % -> fraction)
        cfg.TARGET_IMMUNITIES = {
            name: ((val or 0) / 100)        # (None or 0) → 0
            for name, val in zip(cfg.TARGET_IMMUNITIES.keys(), immunity_values)
        }

        imms_data = [f"{k.title()}: {int(v * 100)}%" for k, v in cfg.TARGET_IMMUNITIES.items()]
        imms_data = "\n".join(imms_data)

        return (
            prettify_text(base_weapon_props),
            prettify_text(purple_weapon_props),
            imms_data,
        )


    # =========================================================================
    # RESET CALLBACKS - Split into domain-specific callbacks for maintainability
    # =========================================================================

    # Callback 1: Reset character settings (16 outputs)
    @app.callback(
        [Output('ab-input', 'value', allow_duplicate=True),
         Output('ab-capped-input', 'value', allow_duplicate=True),
         Output('ab-prog-dropdown', 'value', allow_duplicate=True),
         Output('toon-size-dropdown', 'value', allow_duplicate=True),
         Output('combat-type-dropdown', 'value', allow_duplicate=True),
         Output('mighty-input', 'value', allow_duplicate=True),
         Output('enhancement-set-bonus-dropdown', 'value', allow_duplicate=True),
         Output('str-mod-input', 'value', allow_duplicate=True),
         Output({'type': 'melee-switch', 'name': 'two-handed'}, 'value', allow_duplicate=True),
         Output({'type': 'melee-switch', 'name': 'weaponmaster'}, 'value', allow_duplicate=True),
         Output('keen-switch', 'value', allow_duplicate=True),
         Output('improved-crit-switch', 'value', allow_duplicate=True),
         Output('overwhelm-crit-switch', 'value', allow_duplicate=True),
         Output('dev-crit-switch', 'value', allow_duplicate=True),
         Output('shape-weapon-switch', 'value', allow_duplicate=True),
         Output('shape-weapon-dropdown', 'value', allow_duplicate=True),
         Output('weapon-dropdown', 'value', allow_duplicate=True)],
        [Input('reset-button', 'n_clicks'),
         Input('sticky-reset-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def reset_character_settings(n1, n2):
        if not (n1 or n2):
            return [dash.no_update] * 16
        default_cfg = Config()
        return [
            default_cfg.AB,
            default_cfg.AB_CAPPED,
            default_cfg.AB_PROG,
            default_cfg.TOON_SIZE,
            default_cfg.COMBAT_TYPE,
            default_cfg.MIGHTY,
            default_cfg.ENHANCEMENT_SET_BONUS,
            default_cfg.STR_MOD,
            default_cfg.TWO_HANDED,
            default_cfg.WEAPONMASTER,
            default_cfg.KEEN,
            default_cfg.IMPROVED_CRIT,
            default_cfg.OVERWHELM_CRIT,
            default_cfg.DEV_CRIT,
            default_cfg.SHAPE_WEAPON_OVERRIDE,
            default_cfg.SHAPE_WEAPON,
            default_cfg.DEFAULT_WEAPONS,
        ]

    # Callback 2: Reset additional damage (4 ALL pattern outputs)
    @app.callback(
        [Output({'type': 'add-dmg-switch', 'name': ALL}, 'value', allow_duplicate=True),
         Output({'type': 'add-dmg-input1', 'name': ALL}, 'value', allow_duplicate=True),
         Output({'type': 'add-dmg-input2', 'name': ALL}, 'value', allow_duplicate=True),
         Output({'type': 'add-dmg-input3', 'name': ALL}, 'value', allow_duplicate=True)],
        [Input('reset-button', 'n_clicks'),
         Input('sticky-reset-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def reset_additional_damage(n1, n2):
        if not (n1 or n2):
            # Return no_update arrays for ALL pattern outputs
            return [[dash.no_update] * 20] * 4
        default_cfg = Config()
        return [
            [val[0] for val in default_cfg.ADDITIONAL_DAMAGE.values()],
            [next(iter(val[1].values()))[0] for val in default_cfg.ADDITIONAL_DAMAGE.values()],
            [next(iter(val[1].values()))[1] for val in default_cfg.ADDITIONAL_DAMAGE.values()],
            [next(iter(val[1].values()))[2] for val in default_cfg.ADDITIONAL_DAMAGE.values()],
        ]

    # Callback 3: Reset simulation settings (11 outputs)
    @app.callback(
        [Output('target-ac-input', 'value', allow_duplicate=True),
         Output('rounds-input', 'value', allow_duplicate=True),
         Output('damage-limit-switch', 'value', allow_duplicate=True),
         Output('damage-limit-input', 'value', allow_duplicate=True),
         Output('dmg-vs-race-switch', 'value', allow_duplicate=True),
         Output('relative-change-input', 'value', allow_duplicate=True),
         Output('relative-std-input', 'value', allow_duplicate=True),
         Output('target-immunities-switch', 'value', allow_duplicate=True),
         Output({'type': 'immunity-input', 'name': ALL}, 'value', allow_duplicate=True),
         Output('immunities-store', 'data', allow_duplicate=True)],
        [Input('reset-button', 'n_clicks'),
         Input('sticky-reset-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def reset_simulation_settings(n1, n2):
        if not (n1 or n2):
            # Return no_update for all outputs (11th is ALL pattern)
            return [dash.no_update] * 9 + [[dash.no_update] * 11, dash.no_update]
        default_cfg = Config()
        reset_immunities_store = {
            name: (val or 0)
            for name, val in default_cfg.TARGET_IMMUNITIES.items()
        }
        return [
            default_cfg.TARGET_AC,
            default_cfg.ROUNDS,
            default_cfg.DAMAGE_LIMIT_FLAG,
            default_cfg.DAMAGE_LIMIT,
            default_cfg.DAMAGE_VS_RACE,
            default_cfg.CHANGE_THRESHOLD * 100,
            default_cfg.STD_THRESHOLD * 100,
            default_cfg.TARGET_IMMUNITIES_FLAG,
            [val * 100 for val in default_cfg.TARGET_IMMUNITIES.values()],
            reset_immunities_store,
        ]

    # Callback 4: Reset stores and show toast (5 outputs)
    @app.callback(
        [Output('config-store', 'data', allow_duplicate=True),
         Output('builds-store', 'data', allow_duplicate=True),
         Output('active-build-index', 'data', allow_duplicate=True),
         Output('reset-toast', 'is_open', allow_duplicate=True),
         Output('build-loading', 'data', allow_duplicate=True)],
        [Input('reset-button', 'n_clicks'),
         Input('sticky-reset-button', 'n_clicks')],
        prevent_initial_call=True
    )
    def reset_stores_and_toast(n1, n2):
        if not (n1 or n2):
            return [dash.no_update] * 5
        from components.build_manager import create_default_builds
        default_cfg = Config()
        return [
            default_cfg.__dict__,
            create_default_builds(),
            0,
            True,  # Open the toast
            False,  # Set build-loading to False to hide spinner
        ]


    # Callback: close error modal
    @app.callback(
        Output('global-error-modal', 'is_open', allow_duplicate=True),
        Output('loading-overlay', 'style', allow_duplicate=True),
        Input('close-global-error', 'n_clicks'),
        State('global-error-modal', 'is_open'),
        prevent_initial_call=True
    )
    def close_error_modal(n_clicks, is_open):
        if n_clicks:
            return not is_open, {'display': 'none'}
        else:
            return dash.no_update, dash.no_update


    # Callback: show Results as active tab when simulation done
    @app.callback(
        Output('tabs', 'active_tab'),
        [Input('intermediate-value', 'data')]
    )
    def switch_to_results(results):
        if results:
            return 'results'
        return dash.no_update


    # Callback: toggle target immunities inputs
    @app.callback(
        Output({'type': 'immunity-input', 'name': ALL}, 'value'),
        Output('immunities-store', 'data'),
        Input('target-immunities-switch', 'value'),
        State('config-store', 'data'),
        State('immunities-store', 'data'),
        State({'type': 'immunity-input', 'name': ALL}, 'value'),
        prevent_initial_call=True
    )
    def toggle_immunities(apply_immunities, cfg_store, immunities_store, current_input_values):
        names = list(cfg.TARGET_IMMUNITIES.keys())
        n = len(names)

        # Ensure store dict exists
        immunities_store = immunities_store or {}

        if apply_immunities:
            # Prefer the most recent user values saved in immunities-store
            if any(name in immunities_store for name in names):
                return [round(immunities_store.get(name, 0) * 100) for name in names], immunities_store

            # Fallback to config-store values (fractions -> percentages)
            if cfg_store and "TARGET_IMMUNITIES" in cfg_store:
                return [round(cfg_store["TARGET_IMMUNITIES"].get(name, 0) * 100) for name in names], immunities_store

            # Final fallback: zeros
            return [0] * n, immunities_store

        else:
            # Switch off → save current values to immunities-store before setting to 0
            updated_store = {
                name: (val or 0) / 100  # Convert percentages back to fractions
                for name, val in zip(names, current_input_values)
            }
            return [0] * n, updated_store


    # Callback: toggle melee/ranged dependent params OFF and disabled
    @app.callback(
        # Output({'type': 'melee-row', 'name': ALL}, 'style'),
        Output({'type': 'melee-switch', 'name': ALL}, 'value'),
        Output('mighty-input', 'value'),
        Output({'type': 'melee-switch', 'name': ALL}, 'disabled', allow_duplicate=True),
        Output('mighty-input', 'disabled', allow_duplicate=True),
        Input('combat-type-dropdown', 'value'),
        prevent_initial_call='initial_duplicate'
    )
    def toggle_melee_params(combat_type):
        n = len(ctx.outputs_list[0])  # number of matching melee rows
        if combat_type == 'ranged':
            return (
                [False] * n,  # Turn OFF all melee switches
                20,  # Set mighty to 20
                [True] * n,  # Disable all melee switches
                False  # Enable mighty input
            )
        elif combat_type == 'melee':
            return (
                [dash.no_update] * n,  # Don't update the melee switches
                0,  # Set mighty to 0
                [False] * n,  # Enable all melee switches
                True  # Disable mighty input
            )
        else:
            return dash.no_update


    # Callback: toggle shape weapon visibility
    @app.callback(
        Output('shape-weapon-dropdown', 'style'),
        Input('shape-weapon-switch', 'value'),
    )
    def toggle_shape_weapon(show):
        style = {'display': 'flex'} if show else {'display': 'none'}
        return style


    # Callback: toggle damage limit visibility
    @app.callback(
        Output('damage-limit-input', 'style'),
        Input('damage-limit-switch', 'value'),
    )
    def toggle_damage_limit(show):
        style = {'display': 'flex'} if show else {'display': 'none'}
        return style
