/**
 * Clientside callbacks for fast build switching
 * These run in the browser (no server round-trip!) for instant UX
 */

window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.build_switching = window.dash_clientside.build_switching || {};

// --- HELPERS ---

function _parse_damage_config(additional_dmg_dict, additional_dmg_keys) {
    additional_dmg_dict = additional_dmg_dict || {};
    const result = { switches: [], input1: [], input2: [], input3: [] };

    additional_dmg_keys.forEach(key => {
        let sw_val = false;
        let val1 = 0, val2 = 0, val3 = 0;

        try {
            if (additional_dmg_dict[key]) {
                sw_val = additional_dmg_dict[key][0]; // Switch
                const dmg_dict = additional_dmg_dict[key][1]; // Nested dict
                if (dmg_dict) {
                    const dmg_values = Object.values(dmg_dict)[0];
                    if (Array.isArray(dmg_values)) {
                        val1 = dmg_values[0] || 0;
                        val2 = dmg_values[1] || 0;
                        val3 = dmg_values[2] || 0;
                    }
                }
            }
        } catch (e) { /* ignore errors */ }

        result.switches.push(sw_val);
        result.input1.push(val1);
        result.input2.push(val2);
        result.input3.push(val3);
    });
    return result;
}

function _get_no_update_return(keys_count) {
    const no_upd = window.dash_clientside.no_update;
    // Dynamically size the no_update arrays based on key count
    return [
        no_upd, // active-idx
        no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
        no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
        Array(keys_count).fill(no_upd), // switches
        Array(keys_count).fill(no_upd), // input1
        Array(keys_count).fill(no_upd), // input2
        Array(keys_count).fill(no_upd), // input3
        no_upd, // weapons
        no_upd, // name
        no_upd  // loading
    ];
}

// --- MAIN FUNCTIONS ---

/**
 * Handles tab clicks.
 * @param {Array} additional_dmg_keys - list of additional damage keys passed from Python dcc.Store
 */
window.dash_clientside.build_switching.switch_build = function(n_clicks_list, builds, active_idx, is_loading, additional_dmg_keys) {
    const triggered = window.dash_clientside.callback_context.triggered;

    if (!triggered || triggered.length === 0 || is_loading) {
        return _get_no_update_return(additional_dmg_keys.length);
    }

    const match = triggered[0].prop_id.match(/"index":(\d+)/);
    if (!match) return _get_no_update_return(additional_dmg_keys.length);

    const clicked_index = parseInt(match[1]);

    if (clicked_index === active_idx || !builds || clicked_index >= builds.length) {
        return _get_no_update_return(additional_dmg_keys.length);
    }

    const build = builds[clicked_index];
    const dmg_data = _parse_damage_config(build.config.ADDITIONAL_DAMAGE, additional_dmg_keys);

    return [
        clicked_index,
        build.config.AB,
        build.config.AB_CAPPED,
        build.config.AB_PROG,
        build.config.TOON_SIZE,
        build.config.COMBAT_TYPE,
        build.config.MIGHTY,
        build.config.ENHANCEMENT_SET_BONUS,
        build.config.STR_MOD,
        build.config.TWO_HANDED,
        build.config.WEAPONMASTER,
        build.config.KEEN,
        build.config.IMPROVED_CRIT,
        build.config.OVERWHELM_CRIT,
        build.config.DEV_CRIT,
        build.config.SHAPE_WEAPON_OVERRIDE,
        build.config.SHAPE_WEAPON,
        dmg_data.switches,
        dmg_data.input1,
        dmg_data.input2,
        dmg_data.input3,
        build.config.WEAPONS || [],
        build.name,
        false
    ];
};

/**
 * Handles CRUD updates.
 * @param {Array} additional_dmg_keys - list of additional damage keys passed from Python dcc.Store
 */
window.dash_clientside.build_switching.load_from_buffer = function(config, is_loading, additional_dmg_keys) {
    const no_upd = window.dash_clientside.no_update;

    if (!is_loading || !config || !config.config) {
        // Return structure matches Output count, minus active_index
        return [
            no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
            no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
            Array(additional_dmg_keys.length).fill(no_upd),
            Array(additional_dmg_keys.length).fill(no_upd),
            Array(additional_dmg_keys.length).fill(no_upd),
            Array(additional_dmg_keys.length).fill(no_upd),
            no_upd, no_upd, no_upd
        ];
    }

    const dmg_data = _parse_damage_config(config.config.ADDITIONAL_DAMAGE, additional_dmg_keys);

    return [
        config.config.AB,
        config.config.AB_CAPPED,
        config.config.AB_PROG,
        config.config.TOON_SIZE,
        config.config.COMBAT_TYPE,
        config.config.MIGHTY,
        config.config.ENHANCEMENT_SET_BONUS,
        config.config.STR_MOD,
        config.config.TWO_HANDED,
        config.config.WEAPONMASTER,
        config.config.KEEN,
        config.config.IMPROVED_CRIT,
        config.config.OVERWHELM_CRIT,
        config.config.DEV_CRIT,
        config.config.SHAPE_WEAPON_OVERRIDE,
        config.config.SHAPE_WEAPON,
        dmg_data.switches,
        dmg_data.input1,
        dmg_data.input2,
        dmg_data.input3,
        config.config.WEAPONS || [],
        config.name,
        false
    ];
};