"""Callbacks for multi-build management functionality.

Refactored for better UX:
- Auto-save: UI inputs automatically save to builds-store on change (debounced)
- Fast switching: Switching builds only updates active-build-index, then loads new config
- No explicit save-on-switch: eliminates double round-trip delay
"""

import dash
from dash import Input, Output, State, ALL, ctx
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

    # Callback: Add new build (no longer needs to save current state)
    @app.callback(
        Output('builds-store', 'data', allow_duplicate=True),
        Output('active-build-index', 'data', allow_duplicate=True),
        Input('add-build-btn', 'n_clicks'),
        State('builds-store', 'data'),
        prevent_initial_call=True
    )
    def add_new_build(n_clicks, builds):
        if not n_clicks or len(builds) >= 8:
            return dash.no_update, dash.no_update

        # Add new build with defaults (auto-save will have saved current build already)
        new_index = len(builds)
        new_build = {
            'name': f'Build {new_index + 1}',
            'config': get_default_build_config()
        }
        builds.append(new_build)

        return builds, new_index

    # Callback: Duplicate current build (no longer needs to explicitly save current state)
    @app.callback(
        Output('builds-store', 'data', allow_duplicate=True),
        Output('active-build-index', 'data', allow_duplicate=True),
        Input('duplicate-build-btn', 'n_clicks'),
        State('builds-store', 'data'),
        State('active-build-index', 'data'),
        prevent_initial_call=True
    )
    def duplicate_build(n_clicks, builds, active_idx):
        if not n_clicks or len(builds) >= 8:
            return dash.no_update, dash.no_update

        # Duplicate the current build (auto-save will have saved current build already)
        new_index = len(builds)
        current_build = builds[active_idx]
        new_build = {
            'name': f"{current_build['name']} (Copy)",
            'config': copy.deepcopy(current_build['config'])
        }
        builds.append(new_build)

        return builds, new_index

    # Callback: Delete current build
    @app.callback(
        Output('builds-store', 'data', allow_duplicate=True),
        Output('active-build-index', 'data', allow_duplicate=True),
        Input('delete-build-btn', 'n_clicks'),
        State('builds-store', 'data'),
        State('active-build-index', 'data'),
        prevent_initial_call=True
    )
    def delete_build(n_clicks, builds, active_idx):
        if not n_clicks or len(builds) <= 1:
            return dash.no_update, dash.no_update

        # Remove the current build
        builds.pop(active_idx)

        # Adjust active index
        new_active = min(active_idx, len(builds) - 1)

        return builds, new_active

    # Callback: Switch between builds (fast - only updates active index)
    @app.callback(
        Output('active-build-index', 'data', allow_duplicate=True),
        Input({'type': 'build-tab', 'index': ALL}, 'n_clicks'),
        State('active-build-index', 'data'),
        prevent_initial_call=True
    )
    def switch_build(n_clicks_list, active_idx):
        if not ctx.triggered_id or not any(n_clicks_list):
            return dash.no_update

        # Get the clicked build index
        clicked_index = ctx.triggered_id['index']

        # If clicking the same build, no-op
        if clicked_index == active_idx:
            return dash.no_update

        # Just switch the active index (auto-save will have saved current build already)
        return clicked_index

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
        prevent_initial_call=True
    )
    def auto_save_build(ab, ab_capped, ab_prog, toon_size, combat_type, mighty,
                        enhancement, str_mod, two_handed, weaponmaster, keen,
                        improved_crit, overwhelm_crit, dev_crit, shape_override,
                        shape_weapon, add_dmg_states, add_dmg1, add_dmg2, add_dmg3,
                        builds, active_idx):
        """Automatically save current input values to builds-store whenever they change."""
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

    # Callback: Update UI when build changes (load build config into inputs)
    @app.callback(
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
        Input('active-build-index', 'data'),
        State('builds-store', 'data'),
        prevent_initial_call=True
    )
    def load_build_into_ui(active_idx, builds):
        if builds is None or active_idx is None or active_idx >= len(builds):
            return tuple([dash.no_update] * 21)

        build_config = builds[active_idx]['config']
        build_name = builds[active_idx]['name']

        # Extract additional damage values
        add_dmg = build_config.get('ADDITIONAL_DAMAGE', cfg.ADDITIONAL_DAMAGE)
        add_dmg_switches = [val[0] for val in add_dmg.values()]
        add_dmg_input1 = [next(iter(val[1].values()))[0] for val in add_dmg.values()]
        add_dmg_input2 = [next(iter(val[1].values()))[1] for val in add_dmg.values()]
        add_dmg_input3 = [next(iter(val[1].values()))[2] for val in add_dmg.values()]

        return (
            build_config.get('AB', cfg.AB),
            build_config.get('AB_CAPPED', cfg.AB_CAPPED),
            build_config.get('AB_PROG', cfg.AB_PROG),
            build_config.get('TOON_SIZE', cfg.TOON_SIZE),
            build_config.get('COMBAT_TYPE', cfg.COMBAT_TYPE),
            build_config.get('MIGHTY', cfg.MIGHTY),
            build_config.get('ENHANCEMENT_SET_BONUS', cfg.ENHANCEMENT_SET_BONUS),
            build_config.get('STR_MOD', cfg.STR_MOD),
            build_config.get('TWO_HANDED', cfg.TWO_HANDED),
            build_config.get('WEAPONMASTER', cfg.WEAPONMASTER),
            build_config.get('KEEN', cfg.KEEN),
            build_config.get('IMPROVED_CRIT', cfg.IMPROVED_CRIT),
            build_config.get('OVERWHELM_CRIT', cfg.OVERWHELM_CRIT),
            build_config.get('DEV_CRIT', cfg.DEV_CRIT),
            build_config.get('SHAPE_WEAPON_OVERRIDE', cfg.SHAPE_WEAPON_OVERRIDE),
            build_config.get('SHAPE_WEAPON', cfg.SHAPE_WEAPON),
            add_dmg_switches,
            add_dmg_input1,
            add_dmg_input2,
            add_dmg_input3,
            build_name,
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
