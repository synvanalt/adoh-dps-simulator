from dash import dcc, html
import dash_bootstrap_components as dbc
from weapons_db import WEAPON_PROPERTIES, PURPLE_WEAPONS
from typing import Literal


persist_type: Literal["local", "session", "memory"] = "session"
tooltip_delay = 500  # milliseconds


def build_immunity_inputs(immunities_dict):
    rows = []
    for name, val in immunities_dict.items():
        imm_label = dbc.Label(
            name.title() + ":"
        )

        imm_input = dbc.Input(
            id={'type': 'immunity-input', 'name': name},
            type='number',
            value=val * 100,  # default as percentage
            step=1,
            persistence=True,
            persistence_type=persist_type,
            debounce=True,
            style={'height': '1.6em'},
        )

        # Combined row: label on left and widgets on right
        combined = dbc.Row([
            dbc.Col(imm_label, xs=4, md=4),
            dbc.Col(imm_input, xs=3, md=3),
            dbc.Col(html.Span("%"), xs=1, md=1),
        ], class_name='immunity-row')
        rows.append(combined)

    return rows


def build_simulation_settings(cfg):
    # Create a list of valid weapons that exist in both dictionaries
    valid_weapons = sorted([k for k in PURPLE_WEAPONS.keys()
                     if k.split('_')[0] in WEAPON_PROPERTIES])

    simulation_settings = dbc.Col([
        dbc.Row([
            dbc.Col(html.H4('Simulation Settings', className='mt-4 mb-4'), xs=12, md=12),
        ]),

        # Weapon Selection
        dbc.Row([
            dbc.Col(dbc.Label(
                'Select Weapons:',
                html_for='weapon-dropdown',
            ), xs=12, md=2),
            dbc.Col(dcc.Dropdown(
                id='weapon-dropdown',
                options=[{'label': k, 'value': k} for k in valid_weapons],
                value=cfg.DEFAULT_WEAPONS,
                multi=True,
                closeOnSelect=False,
                persistence=True,
                persistence_type='session',
                className='dbc',
            ), xs=12, md=10),
        ], className=''),

        # Simulation Settings - Cont.
        dbc.Row([
            dbc.Col([

                # Target Settings
                dbc.Row([
                    dbc.Col(dbc.Label(
                        'Target AC:',
                        html_for='target-ac-input',
                    ), xs=6, md=6),
                    dbc.Col(dbc.Input(
                        id='target-ac-input',
                        type='number',
                        value=cfg.TARGET_AC,
                        step=1,
                        persistence=True,
                        persistence_type=persist_type,
                        debounce=True,
                    ), xs=6, md=6),
                    dbc.Tooltip(
                        "Target Armor Class (AC) to hit against.",
                        target='target-ac-input',  # must match the component's id
                        placement='right',  # top, bottom, left, right
                        delay={'show': tooltip_delay},
                    ),
                ], class_name='mt-4'),

                # Number of rounds
                dbc.Row([
                    dbc.Col(dbc.Label(
                        'Max Number of Rounds:',
                        html_for='rounds-input',
                    ), xs=6, md=6),
                    dbc.Col(dbc.Input(
                        id='rounds-input',
                        type='number',
                        value=cfg.ROUNDS,
                        step=1,
                        persistence=True,
                        persistence_type=persist_type,
                        debounce=True,
                    ), xs=6, md=6),
                    dbc.Tooltip(
                        "Simulation will stop when either the max number of rounds or the convergence criteria are met.",
                        target='rounds-input',  # must match the component's id
                        placement='right',  # top, bottom, left, right
                        delay={'show': tooltip_delay},
                    ),
                ], class_name=''),

                # Damage limit (stop calculation on reach)
                dbc.Row([
                    dbc.Col(dbc.Switch(
                        id='damage-limit-switch',
                        label="Damage Limit",
                        value=cfg.DAMAGE_LIMIT_FLAG,
                        persistence=True,
                        persistence_type=persist_type,
                    ), xs=6, md=6),
                    dbc.Col(dbc.Input(
                        id='damage-limit-input',
                        type='number',
                        value=cfg.DAMAGE_LIMIT,  # default value
                        step=1,
                        persistence=True,
                        persistence_type=persist_type,
                        debounce=True,
                        style={'display': 'none'},
                    ), xs=6, md=6),
                    dbc.Tooltip(
                        "Simulation will stop when the set damage limit is reached, regardless of convergence.",
                        target='damage-limit-switch',  # must match the component's id
                        placement='left',  # top, bottom, left, right
                        delay={'show': tooltip_delay},
                    ),
                ], class_name='switcher'),

                # Damage limit (stop calculation on reach)
                dbc.Row([
                    dbc.Col(dbc.Switch(
                        id='dmg-vs-race-switch',
                        label="Damage vs. Race",
                        value=cfg.DAMAGE_VS_RACE,
                        persistence=True,
                        persistence_type=persist_type,
                    ), xs=6, md=6),
                    dbc.Tooltip(
                        "Simulation will include specific damage vs. race properties, if applicable.",
                        target='dmg-vs-race-switch',  # must match the component's id
                        placement='left',  # top, bottom, left, right
                        delay={'show': tooltip_delay},
                    ),
                ], class_name='switcher'),

                # Relative Change Convergence
                dbc.Row([
                    dbc.Col(dbc.Label(
                        'Relative Change Convergence:',
                        html_for='relative-change-input',
                    ), xs=6, md=6),
                    dbc.Col(dbc.Input(
                        id='relative-change-input',
                        type='number',
                        value=cfg.CHANGE_THRESHOLD * 100,   # convert to percentage
                        persistence=True,
                        persistence_type=persist_type,
                        debounce=True,
                    ), xs=5, md=5),
                    dbc.Col(html.Span("%"), xs=1, md=1),
                    dbc.Tooltip(
                        "Simulation will stop when both convergence criteria are met. "
                        "Relative Change checks the mean DPS fluctuation within a 15 rounds window. "
                        "Lower values require smaller changes for convergence to be detected.",
                        target='relative-change-input',  # must match the component's id
                        placement='right',  # top, bottom, left, right
                        delay={'show': tooltip_delay},
                    ),
                ], class_name=''),

                # Relative STD Convergence
                dbc.Row([
                    dbc.Col(dbc.Label(
                        'Relative STD Convergence:',
                        html_for='relative-std-input',
                    ), xs=6, md=6),
                    dbc.Col(dbc.Input(
                        id='relative-std-input',
                        type='number',
                        value=cfg.STD_THRESHOLD * 100,  # convert to percentage
                        persistence=True,
                        persistence_type=persist_type,
                        debounce=True,
                    ), xs=5, md=5),
                    dbc.Col(html.Span("%"), xs=1, md=1),
                    dbc.Tooltip(
                        "Simulation will stop when both convergence criteria are met. "
                        "Relative STD checks the mean standard deviation relative to the mean within a 15 rounds window. "
                        "Lower values demand more stability before the simulation is considered converged.",
                        target='relative-std-input',  # must match the component's id
                        placement='right',  # top, bottom, left, right
                        delay={'show': tooltip_delay},
                    ),
                ], class_name=''),

            ], xs=12, md=6, class_name='col-left'),

            # Target Immunities
            dbc.Col([
                dbc.Row([
                    dbc.Col(dbc.Switch(
                        id='target-immunities-switch',
                        label='Apply Target Immunities',
                        value=cfg.TARGET_IMMUNITIES_FLAG,
                        persistence=True,
                        persistence_type=persist_type,
                    ), xs=12, md=12)
                ], class_name='switcher mb-2 mt-4'),

                dbc.Row([
                    dbc.Col(
                        build_immunity_inputs(cfg.TARGET_IMMUNITIES),
                        xs=12, md=12,
                    )
                ], id={'type': 'immunities', 'name': 'container'}, className='border rounded p-3 mb-4')
            ], xs=12, md=6, class_name='col-right'),

        ], className='', style={'display': 'flex', 'alignItems': 'flex-start'}),

        # Simulate Button
        dbc.Row([
            dbc.Col([
                dbc.Button("Reset to Defaults", id='reset-button', color='secondary'),
                dbc.Button("Simulate DPS", id='simulate-button', color='primary', className='ms-3'),
            ], width={"size": 12, "offset": 0}, className='mt-3', style={'display': 'flex', 'justifyContent': 'flex-end'}),
        ]),

        # Toast for reset notification
        dbc.Toast(
            "Values have been reset to defaults!",
            id='reset-toast',
            header="Reset Successful",
            icon='success',
            duration=3000,
            is_open=False,
            dismissable=True,
            style={'position': 'fixed', 'top': 10, 'right': 10},
        ),
    ], xs=12, md=12)

    return simulation_settings
