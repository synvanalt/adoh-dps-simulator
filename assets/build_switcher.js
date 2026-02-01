/**
 * Clientside callbacks for fast build switching
 * These run in the browser (no server round-trip!) for instant UX
 */

window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.clientside = window.dash_clientside.clientside || {};

// --- HELPERS ---

function _parse_damage_config(dmg_source, keys) {
    const len = keys.length;

    // 1. Pre-allocate memory since we know the exact size
    const switches = new Array(len);
    const input1 = new Array(len);
    const input2 = new Array(len);
    const input3 = new Array(len);

    // Safety check for source
    const source = dmg_source || {};

    for (let i = 0; i < len; i++) {
        const key = keys[i];
        const entry = source[key];

        // Default values
        let sw_val = false;
        let v1 = 0, v2 = 0, v3 = 0;

        // 2. Explicit checks are faster than try/catch
        if (entry) {
            sw_val = entry[0];
            const inner_dict = entry[1];

            // 3. Fast extraction of values without creating arrays (Object.values)
            if (inner_dict) {
                // This loop runs exactly once and breaks, avoiding array allocation
                for (const k in inner_dict) {
                    const vals = inner_dict[k];
                    if (vals) { // Simple check if array exists
                        v1 = vals[0] || 0;
                        v2 = vals[1] || 0;
                        v3 = vals[2] || 0;
                    }
                    break;
                }
            }
        }

        // Direct assignment is faster than push
        switches[i] = sw_val;
        input1[i] = v1;
        input2[i] = v2;
        input3[i] = v3;
    }

    return { switches, input1, input2, input3 };
}

function _get_no_update_return(keys_count) {
    const no_upd = window.dash_clientside.no_update;
    // Note: Array(n).fill(x) is extremely fast in modern JS
    return [
        no_upd, // active-idx
        no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
        no_upd, no_upd, // two-handed, weaponmaster
        no_upd, no_upd, no_upd, no_upd, // dual-wield settings (4 new fields)
        no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, // keen through shape_weapon
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

window.dash_clientside.clientside.switch_build = function(n_clicks_list, builds, active_idx, is_loading, additional_dmg_keys) {
    const triggered = window.dash_clientside.callback_context.triggered;

    // Fail-fast checks
    if (!triggered || !triggered.length || is_loading) {
        return _get_no_update_return(additional_dmg_keys.length);
    }

    // Parse index
    const prop_id = triggered[0].prop_id;
    // Optimization: Check for specific string pattern before Regex to save CPU on non-matches
    if (prop_id.indexOf('index') === -1) {
         return _get_no_update_return(additional_dmg_keys.length);
    }

    const match = prop_id.match(/"index":(\d+)/);
    if (!match) return _get_no_update_return(additional_dmg_keys.length);

    const clicked_index = parseInt(match[1], 10); // Always specify radix 10

    if (clicked_index === active_idx || !builds || clicked_index >= builds.length) {
        return _get_no_update_return(additional_dmg_keys.length);
    }

    const build = builds[clicked_index];
    const cfg = build.config; // Short alias for readability

    // Parse specific damage data
    const dmg_data = _parse_damage_config(cfg.ADDITIONAL_DAMAGE, additional_dmg_keys);

    return [
        clicked_index,
        cfg.AB,
        cfg.AB_CAPPED,
        cfg.AB_PROG,
        cfg.DUAL_WIELD,
        cfg.CHARACTER_SIZE,
        cfg.TWO_WEAPON_FIGHTING,
        cfg.AMBIDEXTERITY,
        cfg.IMPROVED_TWF,
        cfg.COMBAT_TYPE,
        cfg.MIGHTY,
        cfg.ENHANCEMENT_SET_BONUS,
        cfg.STR_MOD,
        cfg.TWO_HANDED,
        cfg.WEAPONMASTER,
        cfg.KEEN,
        cfg.IMPROVED_CRIT,
        cfg.OVERWHELM_CRIT,
        cfg.DEV_CRIT,
        cfg.SHAPE_WEAPON_OVERRIDE,
        cfg.SHAPE_WEAPON,
        dmg_data.switches,
        dmg_data.input1,
        dmg_data.input2,
        dmg_data.input3,
        cfg.WEAPONS || [],
        build.name,
        false
    ];
};

window.dash_clientside.clientside.load_from_buffer = function(config, is_loading, additional_dmg_keys) {
    const no_upd = window.dash_clientside.no_update;

    if (!is_loading || !config || !config.config) {
        // Return structure matches Output count, minus active_index
        const len = additional_dmg_keys.length;
        return [
            no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
            no_upd, no_upd, // two-handed, weaponmaster
            no_upd, no_upd, no_upd, no_upd, // dual-wield settings (4 new fields)
            no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, // keen through shape_weapon
            Array(len).fill(no_upd),
            Array(len).fill(no_upd),
            Array(len).fill(no_upd),
            Array(len).fill(no_upd),
            no_upd, no_upd, no_upd
        ];
    }

    const cfg = config.config;
    const dmg_data = _parse_damage_config(cfg.ADDITIONAL_DAMAGE, additional_dmg_keys);

    return [
        cfg.AB,
        cfg.AB_CAPPED,
        cfg.AB_PROG,
        cfg.DUAL_WIELD,
        cfg.CHARACTER_SIZE,
        cfg.TWO_WEAPON_FIGHTING,
        cfg.AMBIDEXTERITY,
        cfg.IMPROVED_TWF,
        cfg.COMBAT_TYPE,
        cfg.MIGHTY,
        cfg.ENHANCEMENT_SET_BONUS,
        cfg.STR_MOD,
        cfg.TWO_HANDED,
        cfg.WEAPONMASTER,
        cfg.KEEN,
        cfg.IMPROVED_CRIT,
        cfg.OVERWHELM_CRIT,
        cfg.DEV_CRIT,
        cfg.SHAPE_WEAPON_OVERRIDE,
        cfg.SHAPE_WEAPON,
        dmg_data.switches,
        dmg_data.input1,
        dmg_data.input2,
        dmg_data.input3,
        cfg.WEAPONS || [],
        config.name,
        false
    ];
};
