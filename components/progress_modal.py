"""Module containing progress-related components and layout elements."""
from dash import html
import dash_bootstrap_components as dbc

def build_progress_elements():
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
