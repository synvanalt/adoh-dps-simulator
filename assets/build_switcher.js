/**
 * Clientside callbacks for fast build switching
 * These run in the browser (no server round-trip!) for instant UX
 */

window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.build_switching = {
    /**
     * Batch-update all inputs from config buffer
     * This is MUCH faster than 22 separate Python callbacks!
     *
     * @param {Object} config - Build configuration object
     * @returns {Array} Array of values for all 22 inputs
     */
    load_from_buffer: function(config) {
        if (!config || !config.config) {
            // Return no_update for all outputs
            // Note: Outputs 16-19 are ALL patterns, so they need arrays of no_update values
            const no_upd = window.dash_clientside.no_update;
            return [
                no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
                no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
                Array(20).fill(no_upd),  // add-dmg-switch (ALL)
                Array(20).fill(no_upd),  // add-dmg-input1 (ALL)
                Array(20).fill(no_upd),  // add-dmg-input2 (ALL)
                Array(20).fill(no_upd),  // add-dmg-input3 (ALL)
                no_upd,  // build-name-input
                no_upd   // build-loading
            ];
        }

        const cfg = config.config;
        const add_dmg = cfg.ADDITIONAL_DAMAGE || {};

        // Fixed order matching config.py ADDITIONAL_DAMAGE definition (20 entries)
        const expected_keys = [
            "Bane_of_Enemies", "Bard_Song", "Blade_Thirst", "Bless_Weapon",
            "Darkfire", "Death_Attack", "Defeaning_Clang", "Divine_Favor",
            "Divine_Might", "Divine_Wrath", "Domain_STR_Evil", "Domain_STR_Good",
            "Enchant_Arrow", "Favored_Enemy", "Flame_Weapon", "Set_Bonus_Damage",
            "Sneak_Attack", "Tenacious_Blow", "Weapon_Spec", "Weapon_Spec_Epic"
        ];

        // Extract additional damage values in fixed order with safe access
        const add_dmg_switches = expected_keys.map(key => {
            try {
                return add_dmg[key] ? add_dmg[key][0] : false;
            } catch(e) {
                return false;
            }
        });
        const add_dmg_input1 = expected_keys.map(key => {
            try {
                if (!add_dmg[key]) return 0;
                const dmg_dict = add_dmg[key][1];
                const dmg_values = Object.values(dmg_dict)[0];
                return dmg_values[0] || 0;
            } catch(e) {
                return 0;
            }
        });
        const add_dmg_input2 = expected_keys.map(key => {
            try {
                if (!add_dmg[key]) return 0;
                const dmg_dict = add_dmg[key][1];
                const dmg_values = Object.values(dmg_dict)[0];
                return dmg_values[1] || 0;
            } catch(e) {
                return 0;
            }
        });
        const add_dmg_input3 = expected_keys.map(key => {
            try {
                if (!add_dmg[key]) return 0;
                const dmg_dict = add_dmg[key][1];
                const dmg_values = Object.values(dmg_dict)[0];
                return dmg_values[2] || 0;
            } catch(e) {
                return 0;
            }
        });

        // Return all 22 values in the correct order
        return [
            cfg.AB,
            cfg.AB_CAPPED,
            cfg.AB_PROG,
            cfg.TOON_SIZE,
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
            add_dmg_switches,
            add_dmg_input1,
            add_dmg_input2,
            add_dmg_input3,
            config.name,
            false  // Clear loading state
        ];
    }
};
