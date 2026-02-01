# Standard library imports
import traceback
from dataclasses import asdict
from functools import wraps

# Third-party imports
import dash
from dash import html, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
import pandas as pd

# Local imports
from simulator.damage_simulator import DamageSimulator
from simulator.config import Config


def register_core_callbacks(app, cfg):

    spinner_style = {
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center',
        'position': 'fixed',
        'top': 0,
        'left': 0,
        'width': '100%',
        'height': '100%',
        'zIndex': 9999,
    }

    # Callback: decorator to catch exceptions
    def with_error_modal(app_name, outputs, inputs, states=None, **callback_kwargs):
        """
        Wraps a callback so that any exception is caught and shown in a global modal.
        outputs: list of Outputs from your normal callback +
                 2 extra outputs at the end:
                 Output('global-error-body','children') and Output('global-error-modal','is_open')
        """
        states = states or []
        def decorator(func):
            @app_name.callback(outputs, inputs, states, **callback_kwargs)
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    # Fill all normal outputs with dash.no_update
                    n_normal_outputs = len(outputs) - 2
                    error_trace = traceback.format_exc()
                    error_trace = html.Pre(error_trace, style={
                        "whiteSpace": "pre-wrap",
                        "fontFamily": "monospace",
                        "overflowX": "auto",
                        "maxHeight": "300px"
                    })
                    return *[dash.no_update]*n_normal_outputs, error_trace, True
            return wrapper
        return decorator

    @with_error_modal(
        app,
        outputs=[
            Output('is-simulating', 'data'),
            Output('intermediate-value', 'data'),
            Output('config-store', 'data'),
            Output('progress-text', 'children'),
            Output('builds-store', 'data'),  # Save current build before simulation
            Output('global-error-body', 'children'),         # extra: error text
            Output('global-error-modal', 'is_open')          # extra: open modal
        ],
        inputs=[
            Input('simulate-button', 'n_clicks'),
            Input('resimulate-button', 'n_clicks'),
            Input('sticky-simulate-button', 'n_clicks'),
        ],
        states=[
            # Core stores
            State('config-store', 'data'),
            State('builds-store', 'data'),
            State('active-build-index', 'data'),
            # Current build UI state (for save-before-simulate)
            State('ab-input', 'value'),
            State('ab-capped-input', 'value'),
            State('ab-prog-dropdown', 'value'),
            State('dual-wield-switch', 'value'),
            State('character-size-dropdown', 'value'),
            State('two-weapon-fighting-switch', 'value'),
            State('ambidexterity-switch', 'value'),
            State('improved-twf-switch', 'value'),
            State('combat-type-dropdown', 'value'),
            State('mighty-input', 'value'),
            State('enhancement-set-bonus-dropdown', 'value'),
            State('str-mod-input', 'value'),
            State({'type': 'melee-switch', 'name': 'two-handed'}, 'value'),
            State({'type': 'melee-switch', 'name': 'weaponmaster'}, 'value'),
            State('keen-switch', 'value'),
            State('improved-crit-switch', 'value'),
            State('overwhelm-crit-switch', 'value'),
            State('dev-crit-switch', 'value'),
            State('shape-weapon-switch', 'value'),
            State('shape-weapon-dropdown', 'value'),
            State({'type': 'add-dmg-switch', 'name': ALL}, 'value'),
            State({'type': 'add-dmg-input1', 'name': ALL}, 'value'),
            State({'type': 'add-dmg-input2', 'name': ALL}, 'value'),
            State({'type': 'add-dmg-input3', 'name': ALL}, 'value'),
            State('weapon-dropdown', 'value'),
            # Shared simulation settings (not per-build)
            State('target-ac-input', 'value'),
            State('rounds-input', 'value'),
            State('damage-limit-switch', 'value'),
            State('damage-limit-input', 'value'),
            State('dmg-vs-race-switch', 'value'),
            State('relative-change-input', 'value'),
            State('relative-std-input', 'value'),
            State('target-immunities-switch', 'value'),
            State({'type': 'immunity-input', 'name': ALL}, 'value'),
        ],
        background=True,  # runs in a worker thread automatically
        cancel=[Input('cancel-sim-button', 'n_clicks')],   # Cancel operation button
        progress=[
            Output('progress-text', 'children'),
            Output('progress-bar', 'value'),
            Output('progress-bar', 'max')
        ],  # streamed progress
        running=[
            (Output('simulate-button', 'disabled'), True, False),
            (Output('resimulate-button', 'disabled'), True, False),
            (Output('sticky-simulate-button', 'disabled'), True, False),
            (Output('reset-button', 'disabled'), True, False),
            (Output('sticky-reset-button', 'disabled'), True, False),
            (Output('progress-modal', 'is_open'), True, False),
            (Output('loading-overlay', 'style'), spinner_style, {'display': 'none'}),
            (Output('progress-text', 'children'), "Warming up...", "Done!"),
            (Output('progress-bar', 'value'), 0, 100),
        ],  # Disable buttons & clear progress modal when sim starts, re-enable buttons when finishes
        prevent_initial_call=True
    )
    def run_simulation(set_progress, _, __, ___, current_cfg, builds, active_build_idx,
                       ab, ab_capped, ab_prog,
                       dual_wield, character_size, two_weapon_fighting, ambidexterity, improved_twf,
                       combat_type, mighty, enhancement_set_bonus, str_mod, two_handed, weaponmaster,
                       keen, improved_crit, overwhelm_crit, dev_crit, shape_weapon_override, shape_weapon,
                       add_dmg_state, add_dmg1, add_dmg2, add_dmg3, weapons,
                       target_ac, rounds, dmg_limit_flag, dmg_limit, dmg_vs_race,
                       relative_change, relative_std, immunity_flag, immunity_values):
        """Run simulation with save-on-action: saves current build first, then simulates all builds."""
        # Check if any build has weapons configured
        has_any_weapons = any(
            build.get('config', {}).get('WEAPONS', [])
            for build in (builds or [])
        )
        if not ctx.triggered_id or not has_any_weapons:
            return False, dash.no_update, current_cfg, dash.no_update, dash.no_update, dash.no_update, False

        print("Starting simulation...")

        # Initialize config store if needed
        if current_cfg is None:
            current_cfg = asdict(cfg)
            print("current_cfg was None and is initialized")

        # Initialize builds if needed
        if builds is None:
            from components.build_manager import create_default_builds
            builds = create_default_builds()

        # Save current build state before simulation (save-on-action)
        add_dmg_dict = {
            key: [add_dmg_state[idx], {next(iter(val[1].keys())): [add_dmg1[idx], add_dmg2[idx], add_dmg3[idx]]}, val[2]]
            for idx, (key, val) in enumerate(cfg.ADDITIONAL_DAMAGE.items())
        }
        builds[active_build_idx]['config'] = {
            'AB': ab,
            'AB_CAPPED': ab_capped,
            'AB_PROG': ab_prog,
            'DUAL_WIELD': dual_wield,
            'CHARACTER_SIZE': character_size,
            'TWO_WEAPON_FIGHTING': two_weapon_fighting,
            'AMBIDEXTERITY': ambidexterity,
            'IMPROVED_TWF': improved_twf,
            'COMBAT_TYPE': combat_type,
            'MIGHTY': mighty,
            'ENHANCEMENT_SET_BONUS': int(enhancement_set_bonus) if enhancement_set_bonus else 3,
            'STR_MOD': str_mod,
            'TWO_HANDED': two_handed,
            'WEAPONMASTER': weaponmaster,
            'KEEN': keen,
            'IMPROVED_CRIT': improved_crit,
            'OVERWHELM_CRIT': overwhelm_crit,
            'DEV_CRIT': dev_crit,
            'SHAPE_WEAPON_OVERRIDE': shape_weapon_override,
            'SHAPE_WEAPON': shape_weapon,
            'ADDITIONAL_DAMAGE': add_dmg_dict,
            'WEAPONS': weapons if weapons else [],
        }

        # Build shared simulation settings (same for all builds)
        shared_settings = {
            'TARGET_AC': target_ac,
            'ROUNDS': rounds,
            'DAMAGE_LIMIT_FLAG': dmg_limit_flag,
            'DAMAGE_LIMIT': dmg_limit,
            'DAMAGE_VS_RACE': dmg_vs_race,
            'CHANGE_THRESHOLD': relative_change / 100,
            'STD_THRESHOLD': relative_std / 100,
            'TARGET_IMMUNITIES_FLAG': immunity_flag,
            'TARGET_IMMUNITIES': {
                name: val / 100
                for name, val in zip(cfg.TARGET_IMMUNITIES.keys(), immunity_values)
            },
        }

        # Calculate total simulations (sum of weapons per build)
        total_sims = sum(len(build['config'].get('WEAPONS', [])) for build in builds)
        sim_count = 0

        # Results dict: {build_name: {weapon: results}}
        results_dict = {}

        for build in builds:
            build_name = build['name']
            build_config = build['config']
            build_weapons = build_config.get('WEAPONS', [])

            if not build_weapons:
                continue  # Skip builds with no weapons

            # Merge build config with shared settings to create full config
            full_cfg_dict = asdict(cfg)  # Start with defaults
            full_cfg_dict.update(build_config)
            full_cfg_dict.update(shared_settings)
            # Remove WEAPONS key - it's build-specific, not a Config attribute
            full_cfg_dict.pop('WEAPONS', None)

            user_cfg = Config(**full_cfg_dict)
            results_dict[build_name] = {}

            for weapon in build_weapons:  # Per-build weapons
                sim_count += 1
                set_progress((f"{build_name} | {weapon}...  ({sim_count}/{total_sims})", str(sim_count), str(total_sims)))

                simulator = DamageSimulator(weapon, user_cfg)
                results_dict[build_name][weapon] = simulator.simulate_dps()

        # Update current_cfg with last used settings (for compatibility)
        current_cfg.update(shared_settings)

        return False, results_dict, current_cfg, "Done!", builds, dash.no_update, False


    # Callback: update results based on stored simulation results
    @app.callback(
        [Output('comparative-table', 'children'),
         Output('detailed-results', 'children'),
         Output('loading-overlay', 'style', allow_duplicate=True)],
        [Input('intermediate-value', 'data'),
         Input('dps-weights-store', 'data')],
        prevent_initial_call=True
    )
    def update_results(results_dict, weights_data):
        if not results_dict:
            return "Run simulation to see results...", "", {'display': 'none'}

        # Get weights from store (default 50/50)
        crit_weight = weights_data.get('crit_allowed', 50) if weights_data else 50
        immune_weight = 100 - crit_weight
        weight_fraction = crit_weight / 100

        # Dynamic column label
        avg_dps_label = f"Avg DPS ({crit_weight}/{immune_weight})"

        # Check if results are in new multi-build format {build_name: {weapon: results}}
        # or legacy format {weapon: results}
        first_value = next(iter(results_dict.values()))
        is_multi_build = isinstance(first_value, dict) and 'summary' not in first_value

        comparative_rows = []

        if is_multi_build:
            # New multi-build format
            for build_name, weapons_results in results_dict.items():
                for weapon, results in weapons_results.items():
                    # Calculate weighted average dynamically
                    weighted_avg = results["dps_crits"] * weight_fraction + results["dps_no_crits"] * (1 - weight_fraction)
                    # Add to comparative table rows with results reference
                    comparative_rows.append({
                        'Build Name': build_name,
                        'Weapon': weapon,
                        avg_dps_label: weighted_avg,
                        'DPS (Crit Allowed)': results["dps_crits"],
                        'DPS (Crit Immune)': results["dps_no_crits"],
                        'Hit %': results["hit_rate_actual"],
                        'Crit %': results["crit_rate_actual"],
                        'Legend Proc %': results["legend_proc_rate_actual"],
                        '_results': results,  # Keep reference to full results for detailed cards
                    })
        else:
            # Legacy single-build format (for backwards compatibility)
            for weapon, results in results_dict.items():
                # Calculate weighted average dynamically
                weighted_avg = results["dps_crits"] * weight_fraction + results["dps_no_crits"] * (1 - weight_fraction)
                comparative_rows.append({
                    'Build Name': 'Build 1',
                    'Weapon': weapon,
                    avg_dps_label: weighted_avg,
                    'DPS (Crit Allowed)': results["dps_crits"],
                    'DPS (Crit Immune)': results["dps_no_crits"],
                    'Hit %': results["hit_rate_actual"],
                    'Crit %': results["crit_rate_actual"],
                    'Legend Proc %': results["legend_proc_rate_actual"],
                    '_results': results,  # Keep reference to full results for detailed cards
                })

        # Sort by DPS descending (use dynamic column label)
        comparative_rows.sort(key=lambda x: x[avg_dps_label], reverse=True)

        # Build detailed results in sorted order
        detailed_results = []
        for row in comparative_rows:
            build_name = row['Build Name']
            weapon = row['Weapon']
            results = row['_results']
            title = f"{build_name} | {weapon}"
            detailed_weapon_results = build_detailed_results_card(title, results)
            detailed_results.append(detailed_weapon_results)

        # Create comparative DataFrame (remove _results helper field before displaying)
        comparative_df = pd.DataFrame([{k: v for k, v in row.items() if k != '_results'} for row in comparative_rows])

        # Wrap table in a responsive div
        comparative_table = html.Div([
            dbc.Table.from_dataframe(       # type: ignore[attr-defined]
                comparative_df.round(2),
                bordered=True,
                hover=True,
                striped=True,
                class_name='table-responsive mb-4',
            )
        ], style={'overflowX': 'auto'})

        # Hide loading overlay when results update completes
        return comparative_table, html.Div(detailed_results), {'display': 'none'}


    def build_detailed_results_card(title, results):
        """Build a detailed results card for a single weapon/build combination."""
        return dbc.Card([
            dbc.CardHeader(html.H6(title, className='mb-0')),
            dbc.CardBody([
                # Attack Stats, Hit and Crit rates per attack
                dbc.Row([
                    dbc.Col([
                        html.Pre(results["summary"], className='border rounded p-3 bg-dark-subtle', style={'overflowX': 'auto'}),
                    ], class_name='mb-4'),
                ]),
                dbc.Row([
                    # Attack Statistics - full width on mobile, 4 cols on desktop
                    dbc.Col([
                        html.H6('Attack Statistics', className='mb-3'),
                        html.Div([
                            dbc.Table([
                                html.Thead([html.Tr([html.Th('Statistic'), html.Th('Actual'), html.Th('Theoretical')])]),
                                html.Tbody([
                                    html.Tr([html.Td('Hit Rate'),
                                             html.Td(f'{results["hit_rate_actual"]:.1f}%'),
                                             html.Td(f'{results["hit_rate_theoretical"]:.1f}%')]),
                                    html.Tr([html.Td('Crit Rate'),
                                             html.Td(f'{results["crit_rate_actual"]:.1f}%'),
                                             html.Td(f'{results["crit_rate_theoretical"]:.1f}%')]),
                                    html.Tr([html.Td('Legend Proc Rate'),
                                             html.Td(f'{results["legend_proc_rate_actual"]:.1f}%'),
                                             html.Td(f'{results["legend_proc_rate_theoretical"]:.1f}%')]),
                                ])
                            ], bordered=True, hover=True, striped=True, size='sm', class_name='table-responsive')
                        ], style={'overflowX': 'auto'})
                    ], xs=12, md=4, class_name='mb-4'),

                    # Hit Rate per Attack - full width on mobile, 4 cols on desktop
                    dbc.Col([
                        html.H6('Hit Rate per Attack', className='mb-3'),
                        html.Div([
                            dbc.Table([
                                html.Thead([html.Tr([html.Th('Attack #'), html.Th('Actual %'), html.Th('Theoretical %')])]),
                                html.Tbody([
                                    html.Tr([
                                        html.Td(f'Attack {i + 1}'),
                                        html.Td(f'{results["hits_per_attack"][i]:.1f}%'),
                                        html.Td(f'{results["hit_rate_per_attack_theoretical"][i]:.1f}%')
                                    ]) for i in range(len(results["hits_per_attack"]))
                                ])
                            ], bordered=True, hover=True, striped=True, size='sm', class_name='table-responsive')
                        ], style={'overflowX': 'auto'})
                    ], xs=12, md=4, class_name='mb-4'),

                    # Crit Rate per Attack - full width on mobile, 4 cols on desktop
                    dbc.Col([
                        html.H6('Crit Rate per Attack', className='mb-3'),
                        html.Div([
                            dbc.Table([
                                html.Thead([html.Tr([html.Th('Attack #'), html.Th('Actual %'), html.Th('Theoretical %')])]),
                                html.Tbody([
                                    html.Tr([
                                        html.Td(f'Attack {i + 1}'),
                                        html.Td(f'{results["crits_per_attack"][i]:.1f}%'),
                                        html.Td(f'{results["crit_rate_per_attack_theoretical"][i]:.1f}%')
                                    ]) for i in range(len(results["crits_per_attack"]))
                                ])
                            ], bordered=True, hover=True, striped=True, size='sm', class_name='table-responsive')
                        ], style={'overflowX': 'auto'})
                    ], xs=12, md=4, class_name='mb-4')
                ], class_name='gx-4', style={'alignItems': 'flex-start'})  # Add horizontal spacing between columns
            ])
        ], class_name='mb-4')


    # Callback: update config-store when inputs change
    @app.callback(
        Output('config-store', 'data', allow_duplicate=True),
        Input({'type': 'immunity-input', 'name': ALL}, 'value'),
        State('config-store', 'data'),
        State('target-immunities-switch', 'value'),
        prevent_initial_call=True
    )
    def update_store_from_inputs(values, cfg_data, switch_on):
        names = list(cfg.TARGET_IMMUNITIES.keys())
        cfg_data = cfg_data or {}

        # Build a list of current store values for comparison
        stored_values = [round(cfg_data.get("TARGET_IMMUNITIES", {}).get(name, 0) * 100) for name in names]

        # Only update store if user manually changed an input while switch is ON
        if not switch_on or values == stored_values:
            return dash.no_update

        cfg_data["TARGET_IMMUNITIES"] = {
            name: (val or 0) / 100 for name, val in zip(names, values)
        }
        return cfg_data