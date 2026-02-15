# Third-party imports
import dash
from dash import Input, Output, ALL, MATCH, State, ClientsideFunction

# Local imports
from simulator.config import Config
from weapons_db import WEAPON_PROPERTIES, PURPLE_WEAPONS



def register_ui_callbacks(app, cfg):

    # Clientside callback: Immediately show spinner when reset buttons are clicked
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='show_spinner_on_reset_click'
        ),
        Output('loading-overlay', 'style', allow_duplicate=True),
        Input('reset-button', 'n_clicks'),
        Input('sticky-reset-button', 'n_clicks'),
        prevent_initial_call=True
    )

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


    # RESET CALLBACKS - Split into domain-specific callbacks for maintainability

    # Callback 1: Reset character settings (29 outputs)
    @app.callback(
        [Output('ab-input', 'value', allow_duplicate=True),
         Output('ab-capped-input', 'value', allow_duplicate=True),
         Output('ab-prog-dropdown', 'value', allow_duplicate=True),
         Output('dual-wield-switch', 'value', allow_duplicate=True),
         Output('character-size-dropdown', 'value', allow_duplicate=True),
         Output('two-weapon-fighting-switch', 'value', allow_duplicate=True),
         Output('ambidexterity-switch', 'value', allow_duplicate=True),
         Output('improved-twf-switch', 'value', allow_duplicate=True),
         Output('custom-offhand-weapon-switch', 'value', allow_duplicate=True),
         Output('offhand-weapon-dropdown', 'value', allow_duplicate=True),
         Output('offhand-ab-input', 'value', allow_duplicate=True),
         Output('offhand-keen-switch', 'value', allow_duplicate=True),
         Output('offhand-improved-crit-switch', 'value', allow_duplicate=True),
         Output('offhand-overwhelm-crit-switch', 'value', allow_duplicate=True),
         Output('offhand-dev-crit-switch', 'value', allow_duplicate=True),
         Output('offhand-weaponmaster-threat-switch', 'value', allow_duplicate=True),
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
            return [dash.no_update] * 29
        default_cfg = Config()
        return [
            default_cfg.AB,
            default_cfg.AB_CAPPED,
            default_cfg.AB_PROG,
            default_cfg.DUAL_WIELD,
            default_cfg.CHARACTER_SIZE,
            default_cfg.TWO_WEAPON_FIGHTING,
            default_cfg.AMBIDEXTERITY,
            default_cfg.IMPROVED_TWF,
            default_cfg.CUSTOM_OFFHAND_WEAPON,
            default_cfg.OFFHAND_WEAPON,
            default_cfg.OFFHAND_AB,
            default_cfg.OFFHAND_KEEN,
            default_cfg.OFFHAND_IMPROVED_CRIT,
            default_cfg.OFFHAND_OVERWHELM_CRIT,
            default_cfg.OFFHAND_DEV_CRIT,
            default_cfg.OFFHAND_WEAPONMASTER_THREAT,
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
            True,   # Open the toast
            False,  # Set build-loading False to hide spinner
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


    # Clientside callback: show Results as active tab when simulation done and scroll to top
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='switch_to_results_tab'
        ),
        Output('tabs', 'active_tab'),
        Input('intermediate-value', 'data'),
    )


    # Fully clientside callback for immunity inputs toggle (UI-only)
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='toggle_immunities_inputs'
        ),
        Output({'type': 'immunity-input', 'name': ALL}, 'value'),
        Output({'type': 'immunity-input', 'name': ALL}, 'disabled'),
        Input('target-immunities-switch', 'value'),
        State({'type': 'immunity-input', 'name': ALL}, 'value'),
        State('immunities-store', 'data'),
        State('config-store', 'data'),
    )

    # Fully clientside callback: persist immunity edits while switch is ON
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='sync_immunities_store'
        ),
        Output('immunities-store', 'data'),
        Input({'type': 'immunity-input', 'name': ALL}, 'value'),
        State('target-immunities-switch', 'value'),
        State({'type': 'immunity-input', 'name': ALL}, 'disabled'),
        State('immunities-store', 'data'),
    )


    # Clientside callback: toggle melee/ranged dependent params for instant UI update
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='toggle_melee_params'
        ),
        Output({'type': 'melee-switch', 'name': ALL}, 'value'),
        Output('mighty-input', 'value'),
        Output({'type': 'melee-switch', 'name': ALL}, 'disabled'),
        Output('mighty-input', 'disabled'),
        Input('combat-type-dropdown', 'value'),
        State({'type': 'melee-switch', 'name': ALL}, 'value'),
    )


    # Clientside callback: Dual-wield panel visibility
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='toggle_dual_wield_section'
        ),
        Output('dual-wield-collapse', 'is_open'),
        Input('dual-wield-switch', 'value'),
    )


    # Clientside callback: toggle shape weapon visibility
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='toggle_shape_weapon'
        ),
        Output('shape-weapon-fade', 'is_in'),
        Input('shape-weapon-switch', 'value'),
    )


    # Clientside callback: toggle custom offhand weapon section visibility
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='toggle_custom_offhand_weapon'
        ),
        Output('offhand-customize-collapse', 'is_open'),
        Input('custom-offhand-weapon-switch', 'value'),
    )



    # Clientside callback: toggle additional damage inputs visibility
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='toggle_additional_damage'
        ),
        Output({'type': 'add-dmg-fade', 'name': MATCH}, 'is_in'),
        Input({'type': 'add-dmg-switch', 'name': MATCH}, 'value'),
    )


    # Clientside callback: toggle damage limit visibility
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='toggle_damage_limit'
        ),
        Output('damage-limit-fade', 'is_in'),
        Input('damage-limit-switch', 'value'),
    )

    # Clientside callback: Toggle About modal
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='toggle_about_modal'
        ),
        Output('about-modal', 'is_open'),
        Input('about-link', 'n_clicks'),
        Input('about-close-btn', 'n_clicks'),
        State('about-modal', 'is_open'),
        prevent_initial_call=True
    )

