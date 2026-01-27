"""
Sticky bottom bar component that appears at the bottom of the screen
when user is in Configuration tab and hasn't scrolled to the bottom.
"""
import dash_bootstrap_components as dbc
from dash import html


def build_sticky_bottom_bar():
    """
    Build a sticky bottom bar with Reset and Simulate buttons.
    Visibility is controlled by JavaScript (sticky_buttons.js)
    """
    return html.Div(
        id='sticky-bottom-bar',
        className='sticky-bottom-bar',
        children=[
            dbc.Button(
                "Reset to Defaults",
                id='sticky-reset-button',
                color='secondary',
                size='md'
            ),
            dbc.Button(
                "Simulate DPS",
                id='sticky-simulate-button',
                color='primary',
                size='md',
                className='ms-2'
            ),
        ],
        style={'display': 'none'}  # Initially hidden, controlled by JS
    )
