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
