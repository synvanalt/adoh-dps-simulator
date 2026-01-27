# Third-party imports
import dash
import diskcache
from dash import dcc, html, DiskcacheManager
import dash_bootstrap_components as dbc

# Local imports
from simulator.config import Config
from components.navbar import build_navbar
from components.build_manager import build_build_manager, create_default_builds
from components.character_settings import build_character_settings
from components.additional_damage import build_additional_damage_panel
from components.simulation_settings import build_simulation_settings
from components.results_tab import build_results_tab
from components.reference_tab import build_reference_info_tab
from components.plots import build_plots_tab
from components.progress_modal import build_progress_elements
from components.sticky_bar import build_sticky_bottom_bar
import callbacks.ui_callbacks as cb_ui
import callbacks.core_callbacks as cb_core
import callbacks.plots_callbacks as cb_plots
import callbacks.validation_callbacks as cb_validation
import callbacks.build_callbacks as cb_build


# Create a Config instance
cfg = Config()

# Diskcache manager to store job state
cache = diskcache.Cache('./cache')
background_callback_manager = DiskcacheManager(cache)

# CDN links
dbc_css = 'https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css'
fontawesome = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/7.0.1/css/all.min.css'

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    background_callback_manager=background_callback_manager,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css, fontawesome]
)
server = app.server   # for online deployment


# Force mobile viewport scaling and Bootstrap dark mode
app.index_string = """
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
    <head>
        {%metas%}
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>ADOH DPS Simulator</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""


# Update app layout to use modularized components
app.layout = dbc.Container([
    dcc.Store(id='config-store', storage_type='session'),
    dcc.Store(id='intermediate-value'),             # Store for simulation results
    dcc.Store(id='immunities-store', data=cfg.TARGET_IMMUNITIES, storage_type='session'),  # keeps user edits
    dcc.Store(id='is-simulating', data=False),     # Store for tracking simulation state
    dcc.Store(id='sim-progress', data={'current': 0, 'total': 0, 'results': {}}),
    dcc.Interval(id='sim-interval', interval=200, disabled=True),  # ticks while simulating
    # Multi-build support stores
    dcc.Store(id='builds-store', data=create_default_builds(), storage_type='session'),
    dcc.Store(id='active-build-index', data=0, storage_type='session'),
    dcc.Store(id='build-loading', data=False),  # Track if build is currently loading
    dcc.Store(id='config-buffer', data=None),  # Buffer for batch-loading build config


    # Navbar
    html.Div(build_navbar()),

    # Add progress components
    build_progress_elements(),

    # Dark overlay with spinner during simulation
    html.Div(
        id='loading-overlay',
        children=dbc.Spinner(color='light', size='lg', type='border'),
        style={
            'display': 'none',
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'width': '100%',
            'height': '100%',
            'zIndex': 9999,
        }
    ),

    # Overlay with spinner during build switching
    html.Div(
        id='build-loading-overlay',
        children=[
            dbc.Spinner(color='primary', size='lg', type='border'),
            html.Div('Switching build...', className='text-light mt-3', style={'fontSize': '1.2rem'})
        ],
        style={
            'display': 'none',
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'width': '100%',
            'height': '100%',
            'backgroundColor': 'rgba(0, 0, 0, 0.7)',
            'zIndex': 9998,
            'flexDirection': 'column',
            'justifyContent': 'center',
            'alignItems': 'center',
        }
    ),

    # Error modal to catch exceptions in risky simulation part
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Oops, unexpected error..."), close_button=False),
            dbc.ModalBody(id='global-error-body'),
            dbc.ModalFooter(dbc.Button("Close", id='close-global-error', class_name='ms-auto')),
        ],
        id='global-error-modal',
        is_open=False,
        backdrop='static',
        style={"zIndex": 99999},
    ),

    dbc.Container([
        dbc.Tabs(id='tabs', active_tab='configuration', children=[
            # Tab 1: Configuration
            dbc.Tab(label='Configuration', tab_id='configuration', children=[
                dbc.Container([
                    # Configuration Parameters
                    dbc.Row([
                        # Build Manager (multi-build support)
                        build_build_manager(),

                        # Character settings
                        build_character_settings(cfg),

                        # Additional damage
                        build_additional_damage_panel(cfg),
                    ], class_name='build-manager-container mb-4 p-3 border rounded', style={'display': 'flex', 'alignItems': 'flex-start'}),

                    # Simulation settings
                    dbc.Row([
                        build_simulation_settings(cfg)
                    ], class_name='mb-0', style={'display': 'flex', 'alignItems': 'flex-start'})
                ], fluid=True, class_name='border-bottom rounded-bottom border-start border-end p-5 mb-4'),
            ]),

            # Tab 2: Results
            build_results_tab(),

            # Tab 3: Plots
            build_plots_tab(),

            # Tab 4: Reference Information
            build_reference_info_tab(),

        ], style={'padding': '20px 0px 0px 0px'}),
    ], fluid=True, style={
        'maxWidth': '1200px',
        'margin': 'auto',
        'padding': '0px 0px 0px 0px'
    }),

    # Sticky bottom bar (appears in Configuration tab when not scrolled to bottom)
    build_sticky_bottom_bar(),
], fluid=True, style={
    'margin': 'auto',
    'padding': '0px 0px 0px 0px'
})


# Register callbacks
cb_ui.register_ui_callbacks(app, cfg)
cb_core.register_core_callbacks(app, cfg)
cb_plots.register_plots_callbacks(app)
cb_validation.register_validation_callbacks(app, cfg)
cb_build.register_build_callbacks(app, cfg)

if __name__ == '__main__':
    app.run(debug=True)
