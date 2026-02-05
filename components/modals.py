"""Module containing progress-related components and layout elements."""
from dash import html
import dash_bootstrap_components as dbc

def build_progress_modal():
    """Create all progress-related components."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Running..."), close_button=False),
            dbc.ModalBody([
                dbc.Label(
                    "Warming up...",
                    id='progress-text',
                    class_name='mb-3'
                ),
                dbc.Progress(id='progress-bar', value='0', style={'height': '20px'}, class_name='mb-3'),
            ]),
            dbc.ModalFooter(dbc.Button("Cancel", id='cancel-sim-button', class_name='ms-auto')),
        ],
        id='progress-modal',
        is_open=False,
        backdrop='static',
        keyboard=False,
        style={"zIndex": 9999}
    )

def build_weights_modal():
    """Create DPS Weights Settings Modal."""
    # DPS Weights Settings Modal
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Average DPS Weights")),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Crit Allowed Weight (%)", className='mb-2'),
                    dbc.Input(id='weights-crit-allowed-input', type='number', min=0, max=100, value=50),
                ], width=6),
                dbc.Col([
                    dbc.Label("Crit Immune Weight (%)", className='mb-2'),
                    dbc.Input(id='weights-crit-immune-display', type='number', value=50, disabled=True),
                ], width=6),
            ]),
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id='weights-cancel-btn', color='secondary', className='me-2'),
            dbc.Button("Apply", id='weights-apply-btn', color='primary'),
        ]),
    ], id='weights-modal', is_open=False)


def build_sim_error_modal():
    """Create  Error Modal."""
    # Error modal to catch exceptions in risky simulation part
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Oops, unexpected error..."), close_button=False),
            dbc.ModalBody(id='global-error-body'),
            dbc.ModalFooter(dbc.Button("Close", id='close-global-error', class_name='ms-auto')),
        ],
        id='global-error-modal',
        is_open=False,
        backdrop='static',
        style={"zIndex": 99999},
    )


def build_about_modal():
    """Create About Modal with app overview, features, and user guide."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("About ADOH DPS Simulator")),
            dbc.ModalBody([
                # Overview Section
                html.H5("Overview", className="mb-3"),
                html.P([
                    "ADOH DPS Simulator is a web-based damage-per-second simulator designed for ",
                    html.A("A Dawn of Heroes", href="https://www.adawnofheroes.org/", target="_blank"),
                    ", a popular NWN:EE action-RPG server. ",
                    "This tool helps players analyze and optimize their character builds by simulating "
                    "realistic combat scenarios and providing detailed damage breakdowns."
                ], className="mb-4"),

                # Features Section
                html.H5("Features", className="mb-3"),
                html.Ul([
                    html.Li([html.Strong("Realistic D20 Simulation: "), "Accurate modeling of attack rolls, hit calculations, and damage aggregation"]),
                    html.Li([html.Strong("Character Customization: "), "Support for dual-wielding, feats, buffs, and legendary weapon effects"]),
                    html.Li([html.Strong("Multi-Build Comparison: "), "Compare multiple character configurations side-by-side"]),
                    html.Li([html.Strong("Data Visualizations: "), "Damage distribution plots and convergence tracking graphs"]),
                ], className="mb-4"),

                # Quick Start Guide Section
                html.H5("Quick Start Guide", className="mb-3"),
                html.Ol([
                    html.Li([
                        html.Strong("Configure Your Build: "),
                        "Set your character stats, select weapons, and adjust target immunities"
                    ]),
                    html.Li([
                        html.Strong("Run Simulation: "),
                        "The simulator will perform multiple attack rounds until results converge"
                    ]),
                    html.Li([
                        html.Strong("Analyze Results: "),
                        "View your DPS breakdown, compare builds, and explore damage distributions"
                    ]),
                ], className="mb-3"),
            ]),
            dbc.ModalFooter(
                dbc.Button("Close", id="about-close-btn", className="ms-auto")
            ),
        ],
        id="about-modal",
        size="lg",
        is_open=False,
    )
