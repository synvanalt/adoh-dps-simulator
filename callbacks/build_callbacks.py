"""Callbacks for multi-build management functionality.

Refactored for better UX:
- Auto-save: UI inputs automatically save to builds-store on change (debounced)
- Fast switching: Switching builds only updates active-build-index, then loads new config
- No explicit save-on-switch: eliminates double round-trip delay
"""

import dash
from dash import Input, Output, State, ALL, ctx, clientside_callback, ClientsideFunction
import dash_bootstrap_components as dbc
import copy

from components.build_manager import get_default_build_config


def register_build_callbacks(app, cfg):
    """Register all callbacks related to build management."""

    # Helper: create a build tab button
    def create_build_tab_button(name, index, is_active):
        return dbc.Button(
            name,
            id={'type': 'build-tab', 'index': index},
            color='primary' if is_active else 'secondary',
            outline=not is_active,
            className=f'build-tab-btn {"active" if is_active else ""}',
            n_clicks=0,
        )

    # Clientside callback: Immediately show spinner when build management buttons are clicked
    # This runs BEFORE Python callbacks, eliminating the perceived delay
    app.clientside_callback(
        ClientsideFunction(
            namespace='build_switching',
            function_name='show_spinner_on_button_click'
        ),
        Output('build-loading-overlay', 'style', allow_duplicate=True),
        Input('add-build-btn', 'n_clicks'),
        Input('duplicate-build-btn', 'n_clicks'),
        Input('delete-build-btn', 'n_clicks'),
        prevent_initial_call=True
    )

    # Callback: Add new build (no longer needs to save current state)
    @app.callback(
        Output('builds-store', 'data', allow_duplicate=True),
        Output('active-build-index', 'data', allow_duplicate=True),
        Output('build-loading', 'data', allow_duplicate=True),
        Input('add-build-btn', 'n_clicks'),
        State('builds-store', 'data'),
        prevent_initial_call=True
    )
    def add_new_build(n_clicks, builds):
        if not n_clicks or len(builds) >= 8:
            return dash.no_update, dash.no_update, dash.no_update

        # Add new build with defaults (auto-save will have saved current build already)
        new_index = len(builds)
        new_build = {
            'name': f'Build {new_index + 1}',
            'config': get_default_build_config()
        }
        builds.append(new_build)

        return builds, new_index, True  # Set loading state

    # Callback: Duplicate current build (no longer needs to explicitly save current state)
    @app.callback(
        Output('builds-store', 'data', allow_duplicate=True),
        Output('active-build-index', 'data', allow_duplicate=True),
        Output('build-loading', 'data', allow_duplicate=True),
        Input('duplicate-build-btn', 'n_clicks'),
        State('builds-store', 'data'),
        State('active-build-index', 'data'),
        prevent_initial_call=True
    )
    def duplicate_build(n_clicks, builds, active_idx):
        if not n_clicks or len(builds) >= 8:
            return dash.no_update, dash.no_update, dash.no_update

        # Duplicate the current build (auto-save will have saved current build already)
        new_index = len(builds)
        current_build = builds[active_idx]
        new_build = {
            'name': f"{current_build['name']} (Copy)",
            'config': copy.deepcopy(current_build['config'])
        }
        builds.append(new_build)

        return builds, new_index, True  # Set loading state

    # Callback: Delete current build
    @app.callback(
        Output('builds-store', 'data', allow_duplicate=True),
        Output('active-build-index', 'data', allow_duplicate=True),
        Output('build-loading', 'data', allow_duplicate=True),
        Input('delete-build-btn', 'n_clicks'),
        State('builds-store', 'data'),
        State('active-build-index', 'data'),
        prevent_initial_call=True
    )
    def delete_build(n_clicks, builds, active_idx):
        if not n_clicks or len(builds) <= 1:
            return dash.no_update, dash.no_update, dash.no_update

        # Remove the current build
        builds.pop(active_idx)

        # Adjust active index
        new_active = min(active_idx, len(builds) - 1)

        return builds, new_active, True

    # Callback: Switch between builds (fast - only updates active index and sets loading state)
    @app.callback(
        Output('active-build-index', 'data', allow_duplicate=True),
        Output('build-loading', 'data', allow_duplicate=True),
        Input({'type': 'build-tab', 'index': ALL}, 'n_clicks'),
        State('active-build-index', 'data'),
        State('build-loading', 'data'),
        prevent_initial_call=True
    )
    def switch_build(n_clicks_list, active_idx, is_loading):
        if not ctx.triggered_id or not any(n_clicks_list):
            return dash.no_update, dash.no_update

        # Prevent switching while already loading
        if is_loading:
            return dash.no_update, dash.no_update

        # Get the clicked build index
        clicked_index = ctx.triggered_id['index']

        # If clicking the same build, no-op
        if clicked_index == active_idx:
            return dash.no_update, dash.no_update

        # Switch the active index and set loading state
        return clicked_index, True

    # Callback: Update build name
    @app.callback(
        Output('builds-store', 'data', allow_duplicate=True),
        Input('build-name-input', 'value'),
        State('builds-store', 'data'),
        State('active-build-index', 'data'),
        prevent_initial_call=True
    )
    def update_build_name(name, builds, active_idx):
        if not name or not builds:
            return dash.no_update

        builds[active_idx]['name'] = name
        return builds

    # Callback: Auto-save - monitors all inputs and automatically saves to builds-store
    @app.callback(
        Output('builds-store', 'data', allow_duplicate=True),
        Input('ab-input', 'value'),
        Input('ab-capped-input', 'value'),
        Input('ab-prog-dropdown', 'value'),
        Input('toon-size-dropdown', 'value'),
        Input('combat-type-dropdown', 'value'),
        Input('mighty-input', 'value'),
        Input('enhancement-set-bonus-dropdown', 'value'),
        Input('str-mod-input', 'value'),
        Input({'type': 'melee-switch', 'name': 'two-handed'}, 'value'),
        Input({'type': 'melee-switch', 'name': 'weaponmaster'}, 'value'),
        Input('keen-switch', 'value'),
        Input('improved-crit-switch', 'value'),
        Input('overwhelm-crit-switch', 'value'),
        Input('dev-crit-switch', 'value'),
        Input('shape-weapon-switch', 'value'),
        Input('shape-weapon-dropdown', 'value'),
        Input({'type': 'add-dmg-switch', 'name': ALL}, 'value'),
        Input({'type': 'add-dmg-input1', 'name': ALL}, 'value'),
        Input({'type': 'add-dmg-input2', 'name': ALL}, 'value'),
        Input({'type': 'add-dmg-input3', 'name': ALL}, 'value'),
        State('builds-store', 'data'),
        State('active-build-index', 'data'),
        State('build-loading', 'data'),  # Prevent save during load
        prevent_initial_call=True
    )
    def auto_save_build(ab, ab_capped, ab_prog, toon_size, combat_type, mighty,
                        enhancement, str_mod, two_handed, weaponmaster, keen,
                        improved_crit, overwhelm_crit, dev_crit, shape_override,
                        shape_weapon, add_dmg_states, add_dmg1, add_dmg2, add_dmg3,
                        builds, active_idx, is_loading):
        """Automatically save current input values to builds-store whenever they change."""
        # Don't save if build is currently loading (prevents race condition)
        if is_loading:
            return dash.no_update

        if not builds or active_idx is None or active_idx >= len(builds):
            return dash.no_update

        # Save current state to builds-store
        builds = save_current_build_state(
            builds, active_idx, ab, ab_capped, ab_prog, toon_size, combat_type,
            mighty, enhancement, str_mod, two_handed, weaponmaster, keen,
            improved_crit, overwhelm_crit, dev_crit, shape_override, shape_weapon,
            add_dmg_states, add_dmg1, add_dmg2, add_dmg3, cfg
        )

        return builds

    # Step 1: Load build config into buffer (Python, fast - just data transfer)
    @app.callback(
        Output('config-buffer', 'data', allow_duplicate=True),
        Input('active-build-index', 'data'),
        State('builds-store', 'data'),
        prevent_initial_call=True
    )
    def load_build_to_buffer(active_idx, builds):
        """Load build config to buffer. Clientside callback will update inputs from buffer."""
        if builds is None or active_idx is None or active_idx >= len(builds):
            return dash.no_update

        # Just return the build data - clientside will handle the rest
        return builds[active_idx]

    # Step 2: Update UI from buffer (Clientside, INSTANT - no server round-trip!)
    app.clientside_callback(
        ClientsideFunction(
            namespace='build_switching',
            function_name='load_from_buffer'
        ),
        Output('ab-input', 'value', allow_duplicate=True),
        Output('ab-capped-input', 'value', allow_duplicate=True),
        Output('ab-prog-dropdown', 'value', allow_duplicate=True),
        Output('toon-size-dropdown', 'value', allow_duplicate=True),
        Output('combat-type-dropdown', 'value', allow_duplicate=True),
        Output('mighty-input', 'value', allow_duplicate=True),
        Output('enhancement-set-bonus-dropdown', 'value', allow_duplicate=True),
        Output('str-mod-input', 'value', allow_duplicate=True),
        Output({'type': 'melee-switch', 'name': 'two-handed'}, 'value', allow_duplicate=True),
        Output({'type': 'melee-switch', 'name': 'weaponmaster'}, 'value', allow_duplicate=True),
        Output('keen-switch', 'value', allow_duplicate=True),
        Output('improved-crit-switch', 'value', allow_duplicate=True),
        Output('overwhelm-crit-switch', 'value', allow_duplicate=True),
        Output('dev-crit-switch', 'value', allow_duplicate=True),
        Output('shape-weapon-switch', 'value', allow_duplicate=True),
        Output('shape-weapon-dropdown', 'value', allow_duplicate=True),
        Output({'type': 'add-dmg-switch', 'name': ALL}, 'value', allow_duplicate=True),
        Output({'type': 'add-dmg-input1', 'name': ALL}, 'value', allow_duplicate=True),
        Output({'type': 'add-dmg-input2', 'name': ALL}, 'value', allow_duplicate=True),
        Output({'type': 'add-dmg-input3', 'name': ALL}, 'value', allow_duplicate=True),
        Output('build-name-input', 'value', allow_duplicate=True),
        Output('build-loading', 'data', allow_duplicate=True),
        Input('config-buffer', 'data'),
        prevent_initial_call=True
    )

    # Callback: Update build tabs UI based on builds-store
    @app.callback(
        Output('build-tabs', 'children'),
        Output('delete-build-btn', 'disabled'),
        Output('add-build-btn', 'disabled'),
        Output('duplicate-build-btn', 'disabled'),
        Input('builds-store', 'data'),
        Input('active-build-index', 'data'),
    )
    def update_build_tabs_ui(builds, active_idx):
        if not builds:
            builds = [{'name': 'Build 1', 'config': get_default_build_config()}]
            active_idx = 0

        tabs = []
        for i, build in enumerate(builds):
            is_active = (i == active_idx)
            tabs.append(create_build_tab_button(build['name'], i, is_active))

        # Disable delete if only 1 build, disable add/duplicate if 8 builds
        delete_disabled = len(builds) <= 1
        add_disabled = len(builds) >= 8
        duplicate_disabled = len(builds) >= 8

        return tabs, delete_disabled, add_disabled, duplicate_disabled

    # Callback: Control loading overlay visibility
    @app.callback(
        Output('build-loading-overlay', 'style'),
        Input('build-loading', 'data'),
    )
    def toggle_build_loading_overlay(is_loading):
        """Show/hide loading overlay during build switching."""
        if is_loading:
            return {
                'display': 'flex',
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
        else:
            return {'display': 'none'}


def save_current_build_state(builds, active_idx, ab, ab_capped, ab_prog, toon_size,
                              combat_type, mighty, enhancement, str_mod, two_handed,
                              weaponmaster, keen, improved_crit, overwhelm_crit,
                              dev_crit, shape_override, shape_weapon,
                              add_dmg_states, add_dmg1, add_dmg2, add_dmg3, cfg):
    """Save the current UI values into the builds array at active_idx."""
    if not builds or active_idx is None or active_idx >= len(builds):
        return builds

    # Rebuild ADDITIONAL_DAMAGE dict from individual inputs
    add_dmg_dict = {}
    for idx, (key, val) in enumerate(cfg.ADDITIONAL_DAMAGE.items()):
        dmg_type_key = next(iter(val[1].keys()))
        add_dmg_dict[key] = [
            add_dmg_states[idx] if idx < len(add_dmg_states) else val[0],
            {dmg_type_key: [
                add_dmg1[idx] if idx < len(add_dmg1) else val[1][dmg_type_key][0],
                add_dmg2[idx] if idx < len(add_dmg2) else val[1][dmg_type_key][1],
                add_dmg3[idx] if idx < len(add_dmg3) else val[1][dmg_type_key][2],
            ]},
            val[2]  # Keep the description
        ]

    builds[active_idx]['config'] = {
        'AB': ab,
        'AB_CAPPED': ab_capped,
        'AB_PROG': ab_prog,
        'TOON_SIZE': toon_size,
        'COMBAT_TYPE': combat_type,
        'MIGHTY': mighty,
        'ENHANCEMENT_SET_BONUS': int(enhancement) if enhancement else 3,
        'STR_MOD': str_mod,
        'TWO_HANDED': two_handed,
        'WEAPONMASTER': weaponmaster,
        'KEEN': keen,
        'IMPROVED_CRIT': improved_crit,
        'OVERWHELM_CRIT': overwhelm_crit,
        'DEV_CRIT': dev_crit,
        'SHAPE_WEAPON_OVERRIDE': shape_override,
        'SHAPE_WEAPON': shape_weapon,
        'ADDITIONAL_DAMAGE': add_dmg_dict,
    }

    return builds
