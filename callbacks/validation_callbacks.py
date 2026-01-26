# Third-party imports
import dash
from dash import Input, Output, State, MATCH, ctx


def register_validation_callbacks(app, cfg):

    # VALIDATIONS SCOPE - CHARACTER SETTINGS
    validations_inputs = {
        'ab-input':                         {'min': 0, 'max': 999, 'default': cfg.AB},
        'ab-capped-input':                  {'min': 0, 'max': 999, 'default': cfg.AB_CAPPED},
        'mighty-input':                     {'min': 0, 'max': 999, 'default': cfg.MIGHTY},
        'str-mod-input':                    {'min': 0, 'max': 999, 'default': cfg.STR_MOD},
        'target-ac-input':                  {'min': 0, 'max': 999, 'default': cfg.TARGET_AC},
        'rounds-input':                     {'min': 1, 'max': 30000, 'default': cfg.ROUNDS},
        'damage-limit-input':               {'min': 1, 'max': 9999999, 'default': cfg.DAMAGE_LIMIT},
        'relative-change-input':            {'min': 0.001, 'max': 1, 'default': cfg.CHANGE_THRESHOLD},
        'relative-std-input':               {'min': 0.001, 'max': 1, 'default': cfg.STD_THRESHOLD},
    }

    # VALIDATIONS SCOPE - ADDITIONAL DAMAGE
    validations_add_dmg = {}
    for k, v in cfg.ADDITIONAL_DAMAGE.items():
        dmg_nums = next(iter(v[1].values()))  # Extract damage params from dict format, val[1] example: {'fire_fw': [1, 4, 10]}
        validations_add_dmg[k] = {
            'dice':     {'min': 0, 'max': 99, 'default': dmg_nums[0]},
            'sides':    {'min': 0, 'max': 99, 'default': dmg_nums[1]},
            'flat':     {'min': 0, 'max': 999, 'default': dmg_nums[2]}
        }

    # VALIDATIONS SCOPE - IMMUNITIES DAMAGE
    validations_immunities = {}
    for k, v in cfg.TARGET_IMMUNITIES.items():
        validations_immunities[k] = {'min': -100, 'max': 100, 'default': v}


    # Validation callback for separate widget inputs
    @app.callback(
        [Output('ab-input', 'value', allow_duplicate=True),
         Output('ab-capped-input', 'value', allow_duplicate=True),
         Output('mighty-input', 'value', allow_duplicate=True),
         Output('str-mod-input', 'value', allow_duplicate=True),
         Output('target-ac-input', 'value', allow_duplicate=True),
         Output('rounds-input', 'value', allow_duplicate=True),
         Output('damage-limit-input', 'value', allow_duplicate=True),
         Output('relative-change-input', 'value', allow_duplicate=True),
         Output('relative-std-input', 'value', allow_duplicate=True)],
        [Input('ab-input', 'value'),
         Input('ab-capped-input', 'value'),
         Input('mighty-input', 'value'),
         Input('str-mod-input', 'value'),
         Input('target-ac-input', 'value'),
         Input('rounds-input', 'value'),
         Input('damage-limit-input', 'value'),
         Input('relative-change-input', 'value'),
         Input('relative-std-input', 'value')],
        [State('build-loading', 'data')],
        prevent_initial_call=True,
    )
    def validate_inputs(*args):
        # Skip validation during build loading to prevent callback cascade
        is_loading = args[-1]
        if is_loading:
            return [dash.no_update] * 9

        inputs_dict = ctx.inputs                        # Dictionary of all inputs
        widget_id = ctx.triggered_id                    # ID of the widget changed
        val = inputs_dict[f'{widget_id}.value']         # Get the value of input changed
        limits = validations_inputs[widget_id]   # Get the limits of the value changed
        try:
            val = float(val) if val is not None else limits['default']
            val = max(limits['min'], min(limits['max'], val))
        except (ValueError, TypeError):
            val = limits['default']

        validated_dict = inputs_dict.copy()         # Copy inputs dictionary
        validated_dict[f'{widget_id}.value'] = val  # Insert validated value into the dict
        validated = list(validated_dict.values())   # Get all the values into a list
        return validated


    # Validation callback for additional damage inputs
    @app.callback(
        [Output({'type': 'add-dmg-input1', 'name': MATCH}, 'value', allow_duplicate=True),
         Output({'type': 'add-dmg-input2', 'name': MATCH}, 'value', allow_duplicate=True),
         Output({'type': 'add-dmg-input3', 'name': MATCH}, 'value', allow_duplicate=True)],
        [Input({'type': 'add-dmg-switch', 'name': MATCH}, 'id'),
         Input({'type': 'add-dmg-input1', 'name': MATCH}, 'value'),
         Input({'type': 'add-dmg-input2', 'name': MATCH}, 'value'),
         Input({'type': 'add-dmg-input3', 'name': MATCH}, 'value')],
        [State('build-loading', 'data')],
        prevent_initial_call=True,
    )
    def validate_additional_damage_inputs(widget_id, dice, sides, flat, is_loading):
        # Skip validation during build loading to prevent callback cascade
        if is_loading:
            return [dash.no_update] * 3

        inputs = [dice, sides, flat]
        validated = []
        add_dmg_name = widget_id['name']
        for val, (key, limits) in zip(inputs, validations_add_dmg[add_dmg_name].items()):
            try:
                val = float(val) if val is not None else limits['default']
                val = max(limits['min'], min(limits['max'], val))
            except (ValueError, TypeError):
                val = limits['default']
            validated.append(val)

        return validated


    # Validation callback for immunity inputs
    @app.callback(
        Output({'type': 'immunity-input', 'name': MATCH}, 'value', allow_duplicate=True),
        Input({'type': 'immunity-input', 'name': MATCH}, 'value'),
        prevent_initial_call=True,
    )
    def validate_immunity_input(val):
        widget_id = ctx.triggered_id['name']            # ID 'name' of the widget changed (e.g., 'magical')
        limits = validations_immunities[widget_id]      # Get the limits of the value changed
        try:
            val = float(val) if val is not None else limits['default']
            val = max(limits['min'], min(limits['max'], val))
        except (ValueError, TypeError):
            val = limits['default']

        return val
