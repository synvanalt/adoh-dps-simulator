from dash import html
import dash_bootstrap_components as dbc



# Modularize layout components

def build_results_tab():
    return dbc.Tab(label="Results", tab_id='results', children=[
        dbc.Container([
            html.Div([
                html.H4("Comparative Results", className='mt-4 mb-4'),
                dbc.Button("Resimulate DPS", id='resimulate-button', color='primary'),
            ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-between'}),

            # Main comparative table
            html.Div(id='comparative-table', className='mb-4'),

            # Detailed results per weapon
            html.H4("Detailed Results", className='mt-4 mb-3'),
            html.Div(id='detailed-results')
        ], fluid=True, className='border-bottom rounded-bottom border-start border-end p-4 mb-4'),
    ])