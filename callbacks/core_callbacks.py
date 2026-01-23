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
            Output('is-calculating', 'data'),
            Output('intermediate-value', 'data'),
            Output('config-store', 'data'),
            Output('progress-text', 'children'),
            Output('global-error-body', 'children'),         # extra: error text
            Output('global-error-modal', 'is_open')          # extra: open modal
        ],
        inputs=[
            # Input('loading-overlay', 'style'),
            Input('simulate-button', 'n_clicks'),
            Input('resimulate-button', 'n_clicks'),
        ],
        states=[
            State('config-store', 'data'),
            State('ab-input', 'value'),
            State('ab-capped-input', 'value'),
            State('ab-prog-dropdown', 'value'),
            State('toon-size-dropdown', 'value'),
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
            State('target-ac-input', 'value'),
            State('rounds-input', 'value'),
            State('damage-limit-switch', 'value'),
            State('damage-limit-input', 'value'),
            State('dmg-vs-race-switch', 'value'),
            State('relative-change-input', 'value'),
            State('relative-std-input', 'value'),
            State('target-immunities-switch', 'value'),
            State({'type': 'immunity-input', 'name': ALL}, 'value')
        ],
        background=True,  # runs in a worker thread automatically
        cancel=[Input('cancel-calc-button', 'n_clicks')],   # Cancel operation button
        progress=[
            Output('progress-text', 'children'),
            Output('progress-bar', 'value'),
            Output('progress-bar', 'max')
        ],  # streamed progress
        running=[
            (Output('simulate-button', 'disabled'), True, False),
            (Output('resimulate-button', 'disabled'), True, False),
            (Output('reset-button', 'disabled'), True, False),
            (Output('progress-modal', 'is_open'), True, False),
            (Output('loading-overlay', 'style'), spinner_style, {'display': 'none'}),
            (Output('progress-text', 'children'), "Warming up...", "Done!"),
            (Output('progress-bar', 'value'), 0, 100),
        ],  # Disable buttons & clear progress modal when calc starts, re-enable buttons when finishes
        prevent_initial_call=True
    )
    def run_calculation(set_progress, _, __, current_cfg, ab, ab_capped, ab_prog, toon_size, combat_type, mighty, enhancement_set_bonus,
                        str_mod, two_handed, weaponmaster, keen, improved_crit, overwhelm_crit, dev_crit, shape_weapon_override, shape_weapon,
                        add_dmg_state, add_dmg1, add_dmg2, add_dmg3,
                        weapons, target_ac, rounds, dmg_limit_flag, dmg_limit, dmg_vs_race,
                        relative_change, relative_std, immunity_flag, immunity_values):

        if not ctx.triggered_id or not weapons:
        # if spinner['display'] == 'none' or not weapons:
            return False, dash.no_update, current_cfg, dash.no_update, dash.no_update, False

        # if ctx.triggered_id == 'simulate-button' or ctx.triggered_id == 'resimulate-button':
        # if spinner['display'] == 'flex':
        print("Starting simulation...")
        # Start calculation
        if current_cfg is None:
            # fallback
            current_cfg = asdict(cfg)
            print("current_cfg was None and is initialized")

        # build config dict instead of mutating globals
        current_cfg['AB'] = ab
        current_cfg['AB_CAPPED'] = ab_capped
        current_cfg['AB_PROG'] = ab_prog
        current_cfg['TOON_SIZE'] = toon_size
        current_cfg['COMBAT_TYPE'] = combat_type
        current_cfg['MIGHTY'] = mighty
        current_cfg['ENHANCEMENT_SET_BONUS'] = int(enhancement_set_bonus)
        current_cfg['STR_MOD'] = str_mod
        current_cfg['TWO_HANDED'] = two_handed
        current_cfg['WEAPONMASTER'] = weaponmaster
        current_cfg['KEEN'] = keen
        current_cfg['IMPROVED_CRIT'] = improved_crit
        current_cfg['OVERWHELM_CRIT'] = overwhelm_crit
        current_cfg['DEV_CRIT'] = dev_crit
        current_cfg['SHAPE_WEAPON_OVERRIDE'] = shape_weapon_override
        current_cfg['SHAPE_WEAPON'] = shape_weapon
        current_cfg['TARGET_AC'] = target_ac
        current_cfg['ROUNDS'] = rounds
        current_cfg['DAMAGE_LIMIT_FLAG'] = dmg_limit_flag
        current_cfg['DAMAGE_LIMIT'] = dmg_limit
        current_cfg['DAMAGE_VS_RACE'] = dmg_vs_race
        current_cfg['CHANGE_THRESHOLD'] = relative_change / 100     # convert to fraction
        current_cfg['STD_THRESHOLD'] = relative_std / 100           # convert to fraction
        current_cfg['TARGET_IMMUNITIES_FLAG'] = immunity_flag

        # Map immunity inputs back into a dictionary (normalize % -> fraction)
        current_cfg['TARGET_IMMUNITIES'] = {
            name: val / 100
            for name, val in zip(cfg.TARGET_IMMUNITIES.keys(), immunity_values)
        }

        # Update additional damage sources
        current_cfg['ADDITIONAL_DAMAGE'] = {
            key: [add_dmg_state[idx], {next(iter(val[1].keys())): [add_dmg1[idx], add_dmg2[idx], add_dmg3[idx]]}]
            for idx, (key, val) in enumerate(cfg.ADDITIONAL_DAMAGE.items())
        }

        # Calculate DPS for all selected weapons
        total = len(weapons)
        user_cfg = Config(**current_cfg)    # convert dict back to Config object
        results_dict = {}
        for i, weapon in enumerate(weapons, start=1):
            # Send progress update to browser
            set_progress((f"Simulating {weapon}...  ({i}/{total})", str(i), str(total)))

            # Run the heavy calculation:
            calculator = DamageSimulator(weapon, user_cfg)
            results_dict[weapon] = calculator.simulate_dps()


        return False, results_dict, current_cfg, "Done!", dash.no_update, False


    # Callback: update results based on stored calculation results
    @app.callback(
        [Output('comparative-table', 'children'),
         Output('detailed-results', 'children')],
        [Input('intermediate-value', 'data')]
    )
    def update_results(results_dict):
        if not results_dict:
            return "Run simulation to see results...", ""

        detailed_results = []
        for weapon, results in results_dict.items():
            detailed_weapon_results = dbc.Card([
                dbc.CardHeader(html.H5(weapon, className='mb-0')),
                dbc.CardBody([
                    # Attack Stats, Hit and Crit rates per attack
                    dbc.Row([
                        dbc.Col([
                            html.H6('Summary', className='mb-3'),
                            html.Pre(results["summary"], className='border rounded p-3 bg-dark-subtle', style={'overflow-x': 'auto'}),
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
                            ], style={'overflow-x': 'auto'})
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
                            ], style={'overflow-x': 'auto'})
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
                            ], style={'overflow-x': 'auto'})
                        ], xs=12, md=4, class_name='mb-4')
                    ], class_name='gx-4', style={'alignItems': 'flex-start'})  # Add horizontal spacing between columns
                ])
            ], class_name='mb-4')
            detailed_results.append(detailed_weapon_results)

        # Create comparative table - made responsive
        comparative_df = pd.DataFrame({
            weapon: {
                'Weapon': weapon,
                'Avg DPS (50/50)': results["avg_dps_both"],
                'DPS (Crit Allowed)': results["dps_crits"],
                'DPS (Crit Immune)': results["dps_no_crits"],
                'Hit %': results["hit_rate_actual"],
                'Crit %': results["crit_rate_actual"],
                'Legend Proc %': results["legend_proc_rate_actual"],
            }
            for weapon, results in results_dict.items()
        }).transpose()

        comparative_df = comparative_df.reset_index(drop=True).sort_values('Avg DPS (50/50)', ascending=False)

        # Wrap table in a responsive div
        comparative_table = html.Div([
            dbc.Table.from_dataframe(       # type: ignore[attr-defined]
                comparative_df.round(2),
                bordered=True,
                hover=True,
                striped=True,
                class_name='table-responsive mb-4',
            )
        ], style={'overflow-x': 'auto'})

        return comparative_table, html.Div(detailed_results)


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