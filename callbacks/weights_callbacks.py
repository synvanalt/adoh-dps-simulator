# Third-party imports
from dash import Input, Output, State, callback_context, ClientsideFunction
import dash


def register_weights_callbacks(app):

    # Clientside callback: Immediately show spinner when weights apply button is clicked
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='show_spinner_on_weights_apply'
        ),
        Output('loading-overlay', 'style', allow_duplicate=True),
        Input('weights-apply-btn', 'n_clicks'),
        prevent_initial_call=True
    )

    # Callback: Toggle modal and populate input from store
    @app.callback(
        Output('weights-modal', 'is_open'),
        Output('weights-crit-allowed-input', 'value'),
        Input('weights-settings-btn', 'n_clicks'),
        Input('weights-cancel-btn', 'n_clicks'),
        Input('weights-apply-btn', 'n_clicks'),
        State('weights-modal', 'is_open'),
        State('dps-weights-store', 'data'),
        prevent_initial_call=True
    )
    def toggle_weights_modal(open_clicks, cancel_clicks, apply_clicks, is_open, weights_data):
        ctx = callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'weights-settings-btn':
            # Open modal and populate from store
            crit_allowed = weights_data.get('crit_allowed', 50) if weights_data else 50
            return True, crit_allowed
        elif trigger_id in ('weights-cancel-btn', 'weights-apply-btn'):
            # Close modal
            return False, dash.no_update

        return dash.no_update, dash.no_update

    # Callback: Update complement display when crit_allowed changes
    @app.callback(
        Output('weights-crit-immune-display', 'value'),
        Input('weights-crit-allowed-input', 'value'),
        prevent_initial_call=True
    )
    def update_complement(crit_allowed):
        if crit_allowed is None:
            return 50
        # Clamp to 0-100 range
        crit_allowed = max(0, min(100, crit_allowed))
        return 100 - crit_allowed

    # Callback: Apply weights to store
    @app.callback(
        Output('dps-weights-store', 'data'),
        Input('weights-apply-btn', 'n_clicks'),
        State('weights-crit-allowed-input', 'value'),
        prevent_initial_call=True
    )
    def apply_weights(n_clicks, crit_allowed):
        if not n_clicks:
            return dash.no_update

        # Clamp to 0-100 range
        if crit_allowed is None:
            crit_allowed = 50
        crit_allowed = max(0, min(100, crit_allowed))

        return {'crit_allowed': crit_allowed}
