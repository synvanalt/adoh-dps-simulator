from dash import dcc, html
import dash_bootstrap_components as dbc


def build_plots_tab():
    """Build the 'Plots' tab layout.

    Section #1 - DPS Comparison (bar chart):
      - A bar chart comparing DPS metrics (Crits Allowed, Crits Immune, Average) for each weapon.

    Section #2 - Per-weapon plots:
      - Dropdown to pick one of the weapons that were simulated.
      - Mean DPS vs Damage inflicted (line / scatter) for the selected weapon.
      - Damage breakdown pie chart for the selected weapon.
    """

    return dbc.Tab(label='Plots', tab_id='plots', children=[
        dbc.Container([
            html.H4('DPS Comparison', className='mt-3 mb-3'),
            html.P('Compare DPS metrics across weapons with crits allowed, crits immune, and average of both.'),
            dcc.Graph(
                id='plots-dps-comparison',
                config={
                    'displayModeBar': 'hover',
                    'modeBarButtonsToRemove': ['toImage', 'select2d', 'lasso2d'],
                    'displaylogo': False,
                    'scrollZoom': False,
                    'toImageButtonOptions': {'format': 'png', 'filename': 'dps_comparison'},
                }
            ),

            html.Hr(),

            html.H4('Selective Plots', className='mt-4 mb-3'),
            dbc.Row([
                dbc.Col(dbc.Label(
                    'Select Build:',
                    html_for='plots-build-dropdown',
                ), xs=12, md=2),
                dbc.Col([
                    dbc.Select(id='plots-build-dropdown',)
                ], xs=12, md=3),
            ]),

            dbc.Row([
                dbc.Col(dbc.Label(
                    'Select Weapon:',
                    html_for='plots-weapon-dropdown',
                ), xs=12, md=2),
                dbc.Col([
                    dbc.Select(id='plots-weapon-dropdown', )
                ], xs=12, md=3),
                dbc.Col([], xs=12, md=2)
            ]),

            dbc.Row([
                dbc.Col([
                    html.H6('Mean DPS over Damage Inflicted'),
                    dcc.Graph(
                        id='plots-weapon-dps-vs-damage',
                        config={
                            'displayModeBar': 'hover',
                            'modeBarButtonsToRemove': ['toImage', 'select2d', 'lasso2d'],
                            'displaylogo': False,
                            'scrollZoom': False,
                            'toImageButtonOptions': {'format': 'png', 'filename': 'dps_vs_damage'},
                        }
                    )
                 ], xs=12, md=6),

                dbc.Col([
                    html.H6('Damage Breakdown'),
                    dcc.Graph(
                        id='plots-weapon-breakdown',
                        config={
                            'displayModeBar': False,
                            'modeBarButtonsToRemove': ['toImage', 'select2d', 'lasso2d'],
                            'displaylogo': False,
                            'scrollZoom': False,
                            'toImageButtonOptions': {'format': 'png', 'filename': 'damage_breakdown'},
                        }
                    )
                 ], xs=12, md=6),
             ], class_name='mt-3')

         ], fluid=True, class_name='border-bottom rounded-bottom border-start border-end p-4 mb-4')
     ])
