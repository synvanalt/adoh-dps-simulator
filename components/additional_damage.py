from dash import html
import dash_bootstrap_components as dbc
from typing import Literal


def build_additional_damage_rows(additional_damage_dict):
    persist_type: Literal["local", "session", "memory"] = "session"

    rows = []
    for key, val in additional_damage_dict.items():

        # Combine label into the Switch component so there is no separate html.Label element
        switch = dbc.Switch(
            id={'type': 'add-dmg-switch', 'name': key},
            label=key.replace('_', ' '),
            value=val[0],
            persistence=True,
            persistence_type=persist_type,
        )

        # Extract damage params from dict format, val[1] example: {'fire_fw': [1, 4, 10]}
        dmg_type_key, dmg_nums = next(iter(val[1].items()))

        # Prettifying the damage type names for better readability
        if dmg_type_key == 'fire_fw':
            dmg_type_name = 'Fire'
        elif dmg_type_key in ('sneak', 'death'):
            dmg_type_name = 'Physical'
        else:
            dmg_type_name = dmg_type_key.title() if dmg_type_key else ''

        # Assigning visibility for each damage input based on applicability (dice damage, flat damage, or both)
        if not isinstance(dmg_nums, list) or len(dmg_nums) != 3:
            raise ValueError(f"Invalid damage numbers for {key}: {dmg_nums}. Expected a list of three integers [dice, sides, flat].")

        if dmg_nums[0] == 0:    # Flat damage only
            visibility_dice = {'display': 'none'}
            visibility_sides = {'display': 'none'}
            visibility_plus = {'display': 'none'}
            visibility_flat = {}    # 'width': '25%'

        elif dmg_nums[2] == 0:  # Dice damage only
            visibility_dice = {'marginRight': '0.2em'}
            visibility_sides = {}
            visibility_plus = {'display': 'none'}
            visibility_flat = {'display': 'none'}

        else:                   # Both dice and flat damage
            visibility_dice = {'marginRight': '0.2em'}
            visibility_sides = {}
            visibility_plus = {'marginLeft': '0.2em', 'marginRight': '0.2em'}
            visibility_flat = {}

        widgets = html.Div([
            dbc.Input(
                id={'type': 'add-dmg-input1', 'name': key},
                type='number',
                value=dmg_nums[0],  # num dice
                step=1,
                persistence=True,
                persistence_type=persist_type,
                debounce=True,
                class_name='add-dmg-input',
                style=visibility_dice,
            ),
            html.Span("d", className='text-muted', style=visibility_dice),
            dbc.Input(
                id={'type': 'add-dmg-input2', 'name': key},
                type='number',
                value=dmg_nums[1],  # sides
                step=1,
                persistence=True,
                persistence_type=persist_type,
                debounce=True,
                class_name='add-dmg-input',
                style=visibility_sides,
            ),
            html.Span("+", style=visibility_plus),
            dbc.Input(
                id={'type': 'add-dmg-input3', 'name': key},
                type='number',
                value=dmg_nums[2],  # flat
                step=1,
                persistence=True,
                persistence_type=persist_type,
                debounce=True,
                class_name='add-dmg-input',
                style=visibility_flat,
            ),
            html.Span(f"{dmg_type_name}", className='text-muted', style={'marginLeft': '0.5em'}),
            dbc.Tooltip(
                val[2],     # string, tooltip description
                target={'type': 'add-dmg-switch', 'name': key},  # must match the component's id
                placement='left',  # top, bottom, left, right
                delay={'show': 500},
            ),
        ], id={'type': 'add-dmg-row', 'name': key}, style={'display': 'none'})

        # Combined row: switch on left and widgets on right
        combined = dbc.Row([
            dbc.Col(switch, xs=12, md=6),
            dbc.Col(widgets, xs=12, md=6),
        ], class_name='switcher tight-row')
        rows.append(combined)

    return rows


def build_additional_damage_panel(cfg):
    return dbc.Col([
        html.H5('Additional Damage', className='mb-3 add-dmg-header'),

        dbc.Row([
            dbc.Col(
                build_additional_damage_rows(cfg.ADDITIONAL_DAMAGE),
                xs=12, md=12,
            )
        ], className='border border-dotted rounded p-3 mb-4'),
    ], xs=12, md=6, class_name='col-right')
