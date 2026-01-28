from dash import dcc, html
import dash_bootstrap_components as dbc
from typing import Literal
from weapons_db import WEAPON_PROPERTIES, PURPLE_WEAPONS


def build_character_settings(cfg):
    persist_type: Literal["local", "session", "memory"] = "session"
    tooltip_delay = 500  # milliseconds

    return dbc.Col([
        html.H5('Character Settings', className='mb-3'),

        # Attack Bonus Settings
        dbc.Row([
            dbc.Col(dbc.Label(
                'Attack Bonus (AB):',
                html_for='ab-input'
            ), xs=6, md=6),
            dbc.Col(dbc.Input(
                id='ab-input',
                type='number',
                value=cfg.AB,
                step=1,
                persistence=True,
                persistence_type=persist_type,
                debounce=True,
            ), xs=6, md=6),
            dbc.Tooltip(
                "Input should reflect your AB with a +7 purple weapon (add set bonus if applicable). "
                "Extra AB for special weapons with higher bonus (e.g., Scythe) are managed by simulator automatically. "
                "AB penalties for extra attacks (e.g., Flurry, Blinding Speed, Rapid Shot) should be included in the input. "
                "Dual-wield penalty should NOT be included, as simulator applies it automatically based on weapon and character size.",
                target='ab-input',  # must match the component's id
                placement='right',  # top, bottom, left, right
                delay={'show': tooltip_delay},
            ),
        ], class_name=''),

        dbc.Row([
            dbc.Col(dbc.Label(
                'AB Capped:',
                html_for='ab-capped-input',
            ), xs=6, md=6),
            dbc.Col(dbc.Input(
                id='ab-capped-input',
                type='number',
                value=cfg.AB_CAPPED,
                step=1,
                persistence=True,
                persistence_type=persist_type,
                debounce=True,
            ), xs=6, md=6),
            dbc.Tooltip(
                "Maximum AB (capped) that can be used for attack rolls. "
                "Important for simulation to apply the correct AB when weapons with higher Enhancement are used (e.g., Scythe), "
                "or when temporary AB bonuses are applied (e.g., Darts +2 AB on-crit).",
                target='ab-capped-input',  # must match the component's id
                placement='right',  # top, bottom, left, right
                delay={'show': tooltip_delay},
            ),
        ], class_name=''),

        dbc.Row([
            dbc.Col(dbc.Label(
                'AB Progression:',
                html_for='ab-prog-dropdown',
            ), xs=6, md=6),
            dbc.Col(dbc.Select(
                id='ab-prog-dropdown',
                options=[{"label": key, "value": key} for key in cfg.AB_PROGRESSIONS.keys()],
                value=cfg.AB_PROG,  # default value
                persistence=True,
                persistence_type=persist_type,
            ), xs=6, md=6),
            dbc.Tooltip(
                "AB progression determines how many attacks per round you get at different AB thresholds.",
                target='ab-prog-dropdown',  # must match the component's id
                placement='right',  # top, bottom, left, right
                delay={'show': tooltip_delay},
            ),
        ], class_name=''),

        dbc.Row([
            dbc.Col(dbc.Label(
                'Character Size:',
                html_for='toon-size-dropdown',
            ), xs=6, md=6),
            dbc.Col(dbc.Select(
                id='toon-size-dropdown',
                options=[
                    {'label': 'Small', 'value': 'S'},
                    {'label': 'Medium', 'value': 'M'},
                    {'label': 'Large', 'value': 'L'}
                ],
                value=cfg.TOON_SIZE,
                persistence=True,
                persistence_type=persist_type,
            ), xs=6, md=6),
            dbc.Tooltip(
                "Used for applying the correct dual-wield penalty.",
                target='toon-size-dropdown',  # must match the component's id
                placement='right',  # top, bottom, left, right
                delay={'show': tooltip_delay},
            ),
        ], class_name=''),

        # Combat Settings
        dbc.Row([
            dbc.Col(dbc.Label(
                'Combat Type:',
                html_for='combat-type-dropdown',
            ), xs=6, md=6),
            dbc.Col(dbc.Select(
                id='combat-type-dropdown',
                options=[
                    {'label': 'Melee', 'value': 'melee'},
                    {'label': 'Ranged', 'value': 'ranged'}
                ],
                value=cfg.COMBAT_TYPE,
                persistence=True,
                persistence_type=persist_type,
            ), xs=6, md=6),
            dbc.Tooltip(
                "Used for applying the correct Strength-based bonus physical damage.",
                target='combat-type-dropdown',  # must match the component's id
                placement='right',  # top, bottom, left, right
                delay={'show': tooltip_delay},
            ),
        ], class_name=''),

        dbc.Row([
            dbc.Col(dbc.Label(
                'Mighty (Ranged):',
                html_for='mighty-input',
            ), xs=6, md=6),
            dbc.Col(dbc.Input(
                id='mighty-input',
                type='number',
                value=cfg.MIGHTY,
                step=1,
                persistence=True,
                persistence_type=persist_type,
                debounce=True,
            ), xs=6, md=6),
            dbc.Tooltip(
                "Used for applying the correct Strength-based bonus physical damage for ammo-based ranged weapons.",
                target='mighty-input',  # must match the component's id
                placement='right',  # top, bottom, left, right
                delay={'show': tooltip_delay},
            ),
        ], class_name=''),

        # Character Stats
        dbc.Row([
            dbc.Col(dbc.Label(
                'Enhancement Set Bonus:',
                html_for='enhancement-set-bonus-dropdown',
            ), xs=6, md=6),
            dbc.Col(dbc.Select(
                id='enhancement-set-bonus-dropdown',
                options=[
                    {'label': '+1', 'value': 1},
                    {'label': '+2', 'value': 2},
                    {'label': '+3', 'value': 3}
                ],
                value=cfg.ENHANCEMENT_SET_BONUS,
                persistence=True,
                persistence_type=persist_type,
            ), xs=6, md=6),
            dbc.Tooltip(
                "Extra physical damage from equipment Set Bonus (ignored if ammo-based ranged weapon with Mighty properties). For example, select +3 for Pure Green Vengeful set.",
                target='enhancement-set-bonus-dropdown',  # must match the component's id
                placement='right',  # top, bottom, left, right
                delay={'show': tooltip_delay},
            ),
        ], class_name=''),

        dbc.Row([
            dbc.Col(dbc.Label(
                'Strength Modifier:',
                html_for='str-mod-input',
            ), xs=6, md=6),
            dbc.Col(dbc.Input(
                id='str-mod-input',
                type='number',
                value=cfg.STR_MOD,
                step=1,
                persistence=True,
                persistence_type=persist_type,
                debounce=True,
            ), xs=6, md=6),
            dbc.Tooltip(
                "Used for applying the correct Strength-based bonus physical damage.",
                target='str-mod-input',  # must match the component's id
                placement='right',  # top, bottom, left, right
                delay={'show': tooltip_delay},
            ),
        ], class_name=''),

        # Two-Handed Weapon: combine switch+label into single Col using label kwarg
        dbc.Row([
            dbc.Col(dbc.Switch(
                id={'type': 'melee-switch', 'name': 'two-handed'},
                label='Two-Handed Weapon',
                label_style={'marginLeft': '0.5em'},
                value=cfg.TWO_HANDED,
                persistence=True,
                persistence_type=persist_type,
            ), xs=12, md=12),
            dbc.Tooltip(
                "Multiplies Strength-based bonus physical damage by 2.",
                target={'type': 'melee-switch', 'name': 'two-handed'},  # must match the component's id
                placement='left',  # top, bottom, left, right
                delay={'show': tooltip_delay},
            ),
        ], class_name='switcher', id={'type': 'melee-row', 'name': 'two-handed'}),

        # Weaponmaster: single Col with label inside switch
        dbc.Row([
            dbc.Col(dbc.Switch(
                id={'type': 'melee-switch', 'name': 'weaponmaster'},
                label='Weaponmaster',
                value=cfg.WEAPONMASTER,
                persistence=True,
                persistence_type=persist_type,
            ), xs=12, md=12),
            dbc.Tooltip(
                "Increases critical hit multiplier and threat range.",
                target={'type': 'melee-switch', 'name': 'weaponmaster'},  # must match the component's id
                placement='left',  # top, bottom, left, right
                delay={'show': tooltip_delay},
            ),
        ], class_name='switcher', id={'type': 'melee-row', 'name': 'weaponmaster'}),

        # Critical Hit Settings: Keen
        dbc.Row([
            dbc.Col(dbc.Switch(
                id='keen-switch',
                label='Keen',
                value=cfg.KEEN,
                persistence=True,
                persistence_type=persist_type,
            ), xs=12, md=12),
            dbc.Tooltip(
                "Increases critical hit threat range.",
                target='keen-switch',  # must match the component's id
                placement='left',  # top, bottom, left, right
                delay={'show': tooltip_delay},
            ),
        ], class_name='switcher'),

        # Critical Hit Settings: Improved Crit
        dbc.Row([
            dbc.Col(dbc.Switch(
                id='improved-crit-switch',
                label='Improved Critical',
                value=cfg.IMPROVED_CRIT,
                persistence=True,
                persistence_type=persist_type,
            ), xs=12, md=12),
            dbc.Tooltip(
                "Increases critical hit threat range.",
                target='improved-crit-switch',  # must match the component's id
                placement='left',  # top, bottom, left, right
                delay={'show': tooltip_delay},
            ),
        ], class_name='switcher'),

        # Critical Hit Settings: Overwhelm Critical
        dbc.Row([
            dbc.Col(dbc.Switch(
                id='overwhelm-crit-switch',
                label='Overwhelming Critical',
                value=cfg.OVERWHELM_CRIT,
                persistence=True,
                persistence_type=persist_type,
            ), xs=12, md=12),
            dbc.Tooltip(
                "On critical hit, adds Physical damage based on weapon critical multiplier: x2 adds 1d6, x3 adds 2d6, x4+ adds 3d6.",
                target='overwhelm-crit-switch',  # must match the component's id
                placement='left',  # top, bottom, left, right
                delay={'show': tooltip_delay},
            ),
        ], class_name='switcher'),

        # Critical Hit Settings: Devastating Critical
        dbc.Row([
            dbc.Col(dbc.Switch(
                id='dev-crit-switch',
                label='Devastating Critical',
                value=cfg.DEV_CRIT,
                persistence=True,
                persistence_type=persist_type,
            ), xs=12, md=12),
            dbc.Tooltip(
                "On critical hit, adds Pure damage based on weapon size: Tiny/Small +10, Medium +20, Large +30.",
                target='dev-crit-switch',  # must match the component's id
                placement='left',  # top, bottom, left, right
                delay={'show': tooltip_delay},
            ),
        ], class_name='switcher'),

        # Shape Weapon Override: switch and dropdown inline on md, stacked on xs
        dbc.Row([
            dbc.Col(dbc.Switch(
                id='shape-weapon-switch',
                label='Shape Weapon Override',
                value=cfg.SHAPE_WEAPON_OVERRIDE,
                persistence=True,
                persistence_type=persist_type,
            ), xs=6, md=6),
            dbc.Col(dbc.Select(
                id='shape-weapon-dropdown',
                options=[{"label": key, "value": key} for key in WEAPON_PROPERTIES.keys()],
                value=cfg.SHAPE_WEAPON,  # default value
                persistence=True,
                persistence_type=persist_type,
                style={'display': 'none'},
            ), xs=6, md=6),
            dbc.Tooltip(
                "Overwrites base weapon properties with the selected weapon, relevant for shapeshifting only.",
                target='shape-weapon-switch',  # must match the component's id
                placement='left',  # top, bottom, left, right
                delay={'show': tooltip_delay},
            ),
        ], class_name='switcher'),

        # Weapon Selection Row (per-build)
        dbc.Row([
            html.H5('Weapon Selection', className='mt-3 mb-3'),
            dbc.Col(dcc.Dropdown(
                id='weapon-dropdown',
                options=[{'label': k, 'value': k} for k in sorted([
                    k for k in PURPLE_WEAPONS.keys()
                    if k.split('_')[0] in WEAPON_PROPERTIES
                ])],
                value=cfg.DEFAULT_WEAPONS,
                multi=True,
                closeOnSelect=False,
                className='dbc',
                # No persistence - builds-store handles it
            ), xs=12, md=12),
        ], className='mt-3 mb-3'),

    ], xs=12, md=6, class_name='col-left')
