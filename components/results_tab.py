from dash import html
import dash_bootstrap_components as dbc



# Modularize layout components

def build_results_tab():
    return dbc.Tab(label="Results", tab_id='results', children=[
        dbc.Container([
            html.Div([
                html.H4("Comparative Results", className='mt-4 mb-4'),
                html.Div([
                    dbc.Button("Simulate DPS", id='resimulate-button', color='primary', className='me-3'),
                    dbc.Button(
                        html.I(className='fas fa-cog'),
                        id='weights-settings-btn',
                        color='secondary',
                        outline=True,
                        title="Configure average DPS weight (Crit Allowed vs. Crit Immune)",
                    ),
                ], style={'display': 'flex', 'alignItems': 'center'}, className='mb-4'),
            ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-between', 'flexWrap': 'wrap'}),

            # Main comparative table
            html.Div(id='comparative-table', className='mb-4'),

            # Detailed results per weapon
            html.H4("Detailed Results", className='mt-4 mb-3'),
            html.Div(id='detailed-results')
        ], fluid=True, className='border-bottom rounded-bottom border-start border-end p-4 mb-4'),
    ])