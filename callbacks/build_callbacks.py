"""Callbacks for multi-build management functionality.

Save-on-Action approach:
- Saves happen ONLY on major actions: switch build, CRUD, run simulation
- No auto-save on every input change (eliminates race conditions)
- Predictable timing: save current → then perform action
"""

import dash
from dash import Input, Output, State, ALL, ctx, ClientsideFunction
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

    # =========================================================================
    # BUILD SWITCHING - Save current build, then load new build
    # =========================================================================

    # Clientside callback: Immediately show spinner when build tab is clicked
    app.clientside_callback(
        ClientsideFunction(
            namespace='build_switching',
            function_name='show_spinner_on_tab_click'
        ),
        Output('loading-overlay', 'style', allow_duplicate=True),
        Input({'type': 'build-tab', 'index': ALL}, 'n_clicks'),
        State('active-build-index', 'data'),
        State('build-loading', 'data'),
        prevent_initial_call=True
    )

    # Python callback: Save current build, switch to new build, and load config directly
    # (Merged switch + load into one callback for faster switching - eliminates 1 round-trip)
    @app.callback(
        Output('builds-store', 'data', allow_duplicate=True),
        Output('active-build-index', 'data', allow_duplicate=True),
        Output('build-loading', 'data', allow_duplicate=True),
        Output('config-buffer', 'data', allow_duplicate=True),
        Input({'type': 'build-tab', 'index': ALL}, 'n_clicks'),
        # Current UI state to save
        State('ab-input', 'value'),
        State('ab-capped-input', 'value'),
        State('ab-prog-dropdown', 'value'),
        State('toon-size-dropdown', 'value'),
        State('combat-type-dropdown', 'value'),
        State('mighty-input', 'value'),
        State('enhancement-set-bonus-dropdown', 'value'),
        State('str-mod-input', 'value'),
        State({'type': 'melee-switch', 'name': 'two-handed'}, 'value'),
        State({'type': 'melee-switch', 'name': 'weaponmaster'}, 'value'),
        State('keen-switch', 'value'),
        State('improved-crit-switch', 'value'),
        State('overwhelm-crit-switch', 'value'),
        State('dev-crit-switch', 'value'),
        State('shape-weapon-switch', 'value'),
        State('shape-weapon-dropdown', 'value'),
        State({'type': 'add-dmg-switch', 'name': ALL}, 'value'),
        State({'type': 'add-dmg-input1', 'name': ALL}, 'value'),
        State({'type': 'add-dmg-input2', 'name': ALL}, 'value'),
        State({'type': 'add-dmg-input3', 'name': ALL}, 'value'),
        State('weapon-dropdown', 'value'),
        # Build state
        State('builds-store', 'data'),
        State('active-build-index', 'data'),
        State('build-loading', 'data'),
        prevent_initial_call=True
    )
    def switch_build(n_clicks_list, ab, ab_capped, ab_prog, toon_size, combat_type,
                     mighty, enhancement, str_mod, two_handed, weaponmaster, keen,
                     improved_crit, overwhelm_crit, dev_crit, shape_override, shape_weapon,
                     add_dmg_states, add_dmg1, add_dmg2, add_dmg3, weapons,
                     builds, active_idx, is_loading):
        """Save current build state, then switch to the clicked build and load its config."""
        no_update = dash.no_update
        if not ctx.triggered_id or not any(n_clicks_list):
            return no_update, no_update, no_update, no_update

        # Prevent switching while already loading
        if is_loading:
            return no_update, no_update, no_update, no_update

        # Get the clicked build index
        clicked_index = ctx.triggered_id['index']

        # If clicking the same build, no-op
        if clicked_index == active_idx:
            return no_update, no_update, no_update, no_update

        # Save current build state before switching
        builds = save_current_build_state(
            builds, active_idx, ab, ab_capped, ab_prog, toon_size, combat_type,
            mighty, enhancement, str_mod, two_handed, weaponmaster, keen,
            improved_crit, overwhelm_crit, dev_crit, shape_override, shape_weapon,
            add_dmg_states, add_dmg1, add_dmg2, add_dmg3, weapons, cfg
        )

        # Return new build config directly to buffer (skips load_build_to_buffer round-trip)
        return builds, clicked_index, True, builds[clicked_index]

    # =========================================================================
    # CRUD OPERATIONS - Save current build first, then perform operation
    # =========================================================================

    # Clientside callback: Immediately show spinner when CRUD buttons are clicked
    app.clientside_callback(
        ClientsideFunction(
            namespace='build_switching',
            function_name='show_spinner_on_button_click'
        ),
        Output('loading-overlay', 'style', allow_duplicate=True),
        Input('add-build-btn', 'n_clicks'),
        Input('duplicate-build-btn', 'n_clicks'),
        Input('delete-build-btn', 'n_clicks'),
        prevent_initial_call=True
    )

    # Callback: Add new build (saves current build first, loads new build config directly)
    @app.callback(
        Output('builds-store', 'data', allow_duplicate=True),
        Output('active-build-index', 'data', allow_duplicate=True),
        Output('build-loading', 'data', allow_duplicate=True),
        Output('config-buffer', 'data', allow_duplicate=True),
        Input('add-build-btn', 'n_clicks'),
        # Current UI state to save
        State('ab-input', 'value'),
        State('ab-capped-input', 'value'),
        State('ab-prog-dropdown', 'value'),
        State('toon-size-dropdown', 'value'),
        State('combat-type-dropdown', 'value'),
        State('mighty-input', 'value'),
        State('enhancement-set-bonus-dropdown', 'value'),
        State('str-mod-input', 'value'),
        State({'type': 'melee-switch', 'name': 'two-handed'}, 'value'),
        State({'type': 'melee-switch', 'name': 'weaponmaster'}, 'value'),
        State('keen-switch', 'value'),
        State('improved-crit-switch', 'value'),
        State('overwhelm-crit-switch', 'value'),
        State('dev-crit-switch', 'value'),
        State('shape-weapon-switch', 'value'),
        State('shape-weapon-dropdown', 'value'),
        State({'type': 'add-dmg-switch', 'name': ALL}, 'value'),
        State({'type': 'add-dmg-input1', 'name': ALL}, 'value'),
        State({'type': 'add-dmg-input2', 'name': ALL}, 'value'),
        State({'type': 'add-dmg-input3', 'name': ALL}, 'value'),
        State('weapon-dropdown', 'value'),
        # Build state
        State('builds-store', 'data'),
        State('active-build-index', 'data'),
        prevent_initial_call=True
    )
    def add_new_build(n_clicks, ab, ab_capped, ab_prog, toon_size, combat_type,
                      mighty, enhancement, str_mod, two_handed, weaponmaster, keen,
                      improved_crit, overwhelm_crit, dev_crit, shape_override, shape_weapon,
                      add_dmg_states, add_dmg1, add_dmg2, add_dmg3, weapons,
                      builds, active_idx):
        no_update = dash.no_update
        if not n_clicks or len(builds) >= 8:
            return no_update, no_update, no_update, no_update

        # Save current build state first
        builds = save_current_build_state(
            builds, active_idx, ab, ab_capped, ab_prog, toon_size, combat_type,
            mighty, enhancement, str_mod, two_handed, weaponmaster, keen,
            improved_crit, overwhelm_crit, dev_crit, shape_override, shape_weapon,
            add_dmg_states, add_dmg1, add_dmg2, add_dmg3, weapons, cfg
        )

        # Add new build with defaults
        new_index = len(builds)
        new_build = {
            'name': f'Build {new_index + 1}',
            'config': get_default_build_config()
        }
        builds.append(new_build)

        # Return new build config directly to buffer
        return builds, new_index, True, new_build

    # Callback: Duplicate current build (saves current build first, loads new build config directly)
    @app.callback(
        Output('builds-store', 'data', allow_duplicate=True),
        Output('active-build-index', 'data', allow_duplicate=True),
        Output('build-loading', 'data', allow_duplicate=True),
        Output('config-buffer', 'data', allow_duplicate=True),
        Input('duplicate-build-btn', 'n_clicks'),
        # Current UI state to save
        State('ab-input', 'value'),
        State('ab-capped-input', 'value'),
        State('ab-prog-dropdown', 'value'),
        State('toon-size-dropdown', 'value'),
        State('combat-type-dropdown', 'value'),
        State('mighty-input', 'value'),
        State('enhancement-set-bonus-dropdown', 'value'),
        State('str-mod-input', 'value'),
        State({'type': 'melee-switch', 'name': 'two-handed'}, 'value'),
        State({'type': 'melee-switch', 'name': 'weaponmaster'}, 'value'),
        State('keen-switch', 'value'),
        State('improved-crit-switch', 'value'),
        State('overwhelm-crit-switch', 'value'),
        State('dev-crit-switch', 'value'),
        State('shape-weapon-switch', 'value'),
        State('shape-weapon-dropdown', 'value'),
        State({'type': 'add-dmg-switch', 'name': ALL}, 'value'),
        State({'type': 'add-dmg-input1', 'name': ALL}, 'value'),
        State({'type': 'add-dmg-input2', 'name': ALL}, 'value'),
        State({'type': 'add-dmg-input3', 'name': ALL}, 'value'),
        State('weapon-dropdown', 'value'),
        # Build state
        State('builds-store', 'data'),
        State('active-build-index', 'data'),
        prevent_initial_call=True
    )
    def duplicate_build(n_clicks, ab, ab_capped, ab_prog, toon_size, combat_type,
                        mighty, enhancement, str_mod, two_handed, weaponmaster, keen,
                        improved_crit, overwhelm_crit, dev_crit, shape_override, shape_weapon,
                        add_dmg_states, add_dmg1, add_dmg2, add_dmg3, weapons,
                        builds, active_idx):
        no_update = dash.no_update
        if not n_clicks or len(builds) >= 8:
            return no_update, no_update, no_update, no_update

        # Save current build state first (so duplicate gets latest changes)
        builds = save_current_build_state(
            builds, active_idx, ab, ab_capped, ab_prog, toon_size, combat_type,
            mighty, enhancement, str_mod, two_handed, weaponmaster, keen,
            improved_crit, overwhelm_crit, dev_crit, shape_override, shape_weapon,
            add_dmg_states, add_dmg1, add_dmg2, add_dmg3, weapons, cfg
        )

        # Duplicate the current build (now has latest state)
        new_index = len(builds)
        current_build = builds[active_idx]
        new_build = {
            'name': f"{current_build['name']} (Copy)",
            'config': copy.deepcopy(current_build['config'])
        }
        builds.append(new_build)

        # Return duplicated build config directly to buffer
        return builds, new_index, True, new_build

    # Callback: Delete current build (no need to save the one being deleted, loads remaining build config directly)
    @app.callback(
        Output('builds-store', 'data', allow_duplicate=True),
        Output('active-build-index', 'data', allow_duplicate=True),
        Output('build-loading', 'data', allow_duplicate=True),
        Output('config-buffer', 'data', allow_duplicate=True),
        Input('delete-build-btn', 'n_clicks'),
        State('builds-store', 'data'),
        State('active-build-index', 'data'),
        prevent_initial_call=True
    )
    def delete_build(n_clicks, builds, active_idx):
        no_update = dash.no_update
        if not n_clicks or len(builds) <= 1:
            return no_update, no_update, no_update, no_update

        # Remove the current build (no need to save it first)
        builds.pop(active_idx)

        # Adjust active index
        new_active = min(active_idx, len(builds) - 1)

        # Return the build at new active index directly to buffer
        return builds, new_active, True, builds[new_active]

    # =========================================================================
    # BUILD NAME UPDATE - Minor, acceptable to update on change
    # =========================================================================

    @app.callback(
        Output('builds-store', 'data', allow_duplicate=True),
        Input('build-name-input', 'value'),
        State('builds-store', 'data'),
        State('active-build-index', 'data'),
        State('build-loading', 'data'),
        prevent_initial_call=True
    )
    def update_build_name(name, builds, active_idx, is_loading):
        # Don't update during loading (prevents overwriting with stale name)
        if is_loading or not name or not builds:
            return dash.no_update

        builds[active_idx]['name'] = name
        return builds

    # =========================================================================
    # BUILD LOADING - Clientside update from config-buffer
    # =========================================================================

    # Note: load_build_to_buffer callback was removed - all operations (switch, add, duplicate, delete)
    # now output config-buffer directly, eliminating one Python round-trip for faster switching.

    # Clientside: Update UI from buffer (instant, no server round-trip)
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
        Output('weapon-dropdown', 'value', allow_duplicate=True),
        Output('build-name-input', 'value', allow_duplicate=True),
        Output('build-loading', 'data', allow_duplicate=True),
        Input('config-buffer', 'data'),
        State('build-loading', 'data'),
        prevent_initial_call=True
    )

    # =========================================================================
    # UI UPDATES
    # =========================================================================

    # Update build tabs UI based on builds-store
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

    # Control loading overlay visibility
    @app.callback(
        Output('loading-overlay', 'style', allow_duplicate=True),
        Input('build-loading', 'data'),
        prevent_initial_call=True
    )
    def toggle_build_loading_overlay(is_loading):
        """Hide loading overlay when build operation completes."""
        if not is_loading:
            return {'display': 'none'}
        return dash.no_update


def save_current_build_state(builds, active_idx, ab, ab_capped, ab_prog, toon_size,
                              combat_type, mighty, enhancement, str_mod, two_handed,
                              weaponmaster, keen, improved_crit, overwhelm_crit,
                              dev_crit, shape_override, shape_weapon,
                              add_dmg_states, add_dmg1, add_dmg2, add_dmg3, weapons, cfg):
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
        'WEAPONS': weapons if weapons else [],
    }

    return builds
