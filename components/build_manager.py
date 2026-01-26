"""Build Manager Component - Manages multiple character configurations (builds)"""

from dash import html
import dash_bootstrap_components as dbc
from typing import Literal


def get_default_build_config():
    """Return a default build configuration dict matching Character Settings + Additional Damage fields."""
    from simulator.config import Config
    default_cfg = Config()

    return {
        # Character Settings
        'AB': default_cfg.AB,
        'AB_CAPPED': default_cfg.AB_CAPPED,
        'AB_PROG': default_cfg.AB_PROG,
        'TOON_SIZE': default_cfg.TOON_SIZE,
        'COMBAT_TYPE': default_cfg.COMBAT_TYPE,
        'MIGHTY': default_cfg.MIGHTY,
        'ENHANCEMENT_SET_BONUS': default_cfg.ENHANCEMENT_SET_BONUS,
        'STR_MOD': default_cfg.STR_MOD,
        'TWO_HANDED': default_cfg.TWO_HANDED,
        'WEAPONMASTER': default_cfg.WEAPONMASTER,
        'KEEN': default_cfg.KEEN,
        'IMPROVED_CRIT': default_cfg.IMPROVED_CRIT,
        'OVERWHELM_CRIT': default_cfg.OVERWHELM_CRIT,
        'DEV_CRIT': default_cfg.DEV_CRIT,
        'SHAPE_WEAPON_OVERRIDE': default_cfg.SHAPE_WEAPON_OVERRIDE,
        'SHAPE_WEAPON': default_cfg.SHAPE_WEAPON,
        # Additional Damage - store the full structure
        'ADDITIONAL_DAMAGE': default_cfg.ADDITIONAL_DAMAGE,
    }


def create_default_builds():
    """Create initial builds array with one default build."""
    return [
        {
            'name': 'Build 1',
            'config': get_default_build_config()
        }
    ]


def build_build_manager():
    """Build the UI component for managing multiple builds."""
    persist_type: Literal["local", "session", "memory"] = "session"

    return html.Div([
        # Build tabs/buttons row
        dbc.Row([
            # Build selector tabs
            dbc.Col([
                html.Div(
                    id='build-tabs-container',
                    children=[
                        dbc.ButtonGroup(
                            id='build-tabs',
                            children=[
                                dbc.Button(
                                    "Build 1",
                                    id={'type': 'build-tab', 'index': 0},
                                    color='primary',
                                    outline=False,
                                    className='build-tab-btn active',
                                    n_clicks=0,
                                )
                            ],
                            className='me-2 flex-wrap',
                        ),
                    ],
                    className='d-flex align-items-center flex-wrap',
                ),
            ], xs=12, md=8, className='mb-2 mb-md-0'),

            # Build management buttons
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button(
                        [html.I(className='fas fa-plus me-1'), "New"],
                        id='add-build-btn',
                        color='success',
                        outline=True,
                        size='sm',
                        title='Add new build with default settings',
                    ),
                    dbc.Button(
                        [html.I(className='fas fa-copy me-1'), "Duplicate"],
                        id='duplicate-build-btn',
                        color='info',
                        outline=True,
                        size='sm',
                        title='Duplicate current build',
                    ),
                    dbc.Button(
                        [html.I(className='fas fa-trash me-1'), "Delete"],
                        id='delete-build-btn',
                        color='danger',
                        outline=True,
                        size='sm',
                        title='Delete current build',
                        disabled=True,  # Disabled when only 1 build
                    ),
                ], className='flex-wrap'),
            ], xs=12, md=4, className='d-flex justify-content-md-end'),
        ], className='mb-3 align-items-center'),

        # Build name editor row
        dbc.Row([
            dbc.Col([
                dbc.InputGroup([
                    dbc.InputGroupText("Build Name:", className='bg-dark'),
                    dbc.Input(
                        id='build-name-input',
                        type='text',
                        value='Build 1',
                        debounce=True,
                        maxLength=30,
                        className='build-name-input',
                    ),
                ], size='sm'),
            ], xs=12, md=6),
        ], className='mb-3'),

        html.Hr()

    ], className='p-3')
