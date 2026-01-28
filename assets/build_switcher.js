/**
 * Clientside callbacks for fast build switching
 * These run in the browser (no server round-trip!) for instant UX
 */

window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.build_switching = {
    /**
     * Full clientside build switching - no Python round-trips!
     * Handles tab clicks and directly updates all inputs from builds-store.
     *
     * @param {Array} n_clicks_list - Array of n_clicks from all build tabs
     * @param {Array} builds - Full builds array from builds-store
     * @param {number} active_idx - Current active build index
     * @param {boolean} is_loading - Whether a build operation is in progress
     * @returns {Array} [new_active_idx, ...all 23 input values..., build_name, build_loading]
     */
    switch_build: function(n_clicks_list, builds, active_idx, is_loading) {
        const no_upd = window.dash_clientside.no_update;

        // Get triggered context
        const triggered = window.dash_clientside.callback_context.triggered;
        if (!triggered || triggered.length === 0 || is_loading) {
            return [
                no_upd,  // active-build-index
                no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
                no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
                Array(20).fill(no_upd),  // add-dmg-switch (ALL)
                Array(20).fill(no_upd),  // add-dmg-input1 (ALL)
                Array(20).fill(no_upd),  // add-dmg-input2 (ALL)
                Array(20).fill(no_upd),  // add-dmg-input3 (ALL)
                no_upd,  // weapon-dropdown
                no_upd,  // build-name-input
                no_upd   // build-loading
            ];
        }

        // Parse triggered ID to get clicked index
        const triggered_id = triggered[0].prop_id;
        const match = triggered_id.match(/"index":(\d+)/);
        if (!match) {
            return [
                no_upd,
                no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
                no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
                Array(20).fill(no_upd),
                Array(20).fill(no_upd),
                Array(20).fill(no_upd),
                Array(20).fill(no_upd),
                no_upd, no_upd, no_upd
            ];
        }

        const clicked_index = parseInt(match[1]);

        // If clicking the same build, no-op
        if (clicked_index === active_idx) {
            return [
                no_upd,
                no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
                no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
                Array(20).fill(no_upd),
                Array(20).fill(no_upd),
                Array(20).fill(no_upd),
                Array(20).fill(no_upd),
                no_upd, no_upd, no_upd
            ];
        }

        // Validate builds and index
        if (!builds || clicked_index >= builds.length) {
            return [
                no_upd,
                no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
                no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
                Array(20).fill(no_upd),
                Array(20).fill(no_upd),
                Array(20).fill(no_upd),
                Array(20).fill(no_upd),
                no_upd, no_upd, no_upd
            ];
        }

        // Load build config directly - no Python round-trip!
        const build = builds[clicked_index];
        const cfg = build.config;
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

        // Return: [new_active_idx, all 22 inputs, build-name, build-loading=false]
        return [
            clicked_index,  // new active-build-index
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
            cfg.WEAPONS || [],
            build.name,
            false  // Clear build-loading state
        ];
    },

    /**
     * Batch-update all inputs from config buffer
     * This is MUCH faster than 22 separate Python callbacks!
     * Used for CRUD operations (add/duplicate/delete) that still need Python.
     *
     * @param {Object} config - Build configuration object
     * @param {boolean} is_loading - Whether a build operation is in progress
     * @returns {Array} Array of values for all 22 inputs
     */
    load_from_buffer: function(config, is_loading) {
        const no_upd = window.dash_clientside.no_update;

        // Only process if we're in a loading state (CRUD operation)
        // This prevents overwriting user inputs when config-buffer changes unexpectedly
        if (!is_loading || !config || !config.config) {
            return [
                no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
                no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd, no_upd,
                Array(20).fill(no_upd),  // add-dmg-switch (ALL)
                Array(20).fill(no_upd),  // add-dmg-input1 (ALL)
                Array(20).fill(no_upd),  // add-dmg-input2 (ALL)
                Array(20).fill(no_upd),  // add-dmg-input3 (ALL)
                no_upd,  // weapon-dropdown
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

        // Return all 23 values in the correct order
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
            cfg.WEAPONS || [],  // weapon-dropdown with fallback
            config.name,
            false  // Clear loading state
        ];
    },

    /**
     * Immediately show loading spinner when build management buttons are clicked
     * This runs BEFORE the Python callback, eliminating perceived delay
     *
     * @param {number} add_clicks - Add button clicks
     * @param {number} dup_clicks - Duplicate button clicks
     * @param {number} del_clicks - Delete button clicks
     * @returns {Object} Style object for loading overlay
     */
    show_spinner_on_button_click: function(add_clicks, dup_clicks, del_clicks) {
        // Check if any button was clicked (triggered this callback)
        const triggered = window.dash_clientside.callback_context.triggered;
        if (!triggered || triggered.length === 0) {
            return window.dash_clientside.no_update;
        }

        // Show spinner immediately
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
        };
    },

    /**
     * Immediately show loading spinner when reset buttons are clicked
     * This runs BEFORE the Python callbacks, eliminating perceived delay
     *
     * @param {number} reset_clicks - Reset button clicks
     * @param {number} sticky_reset_clicks - Sticky reset button clicks
     * @returns {Object} Style object for loading overlay
     */
    show_spinner_on_reset_click: function(reset_clicks, sticky_reset_clicks) {
        // Check if any button was clicked
        const triggered = window.dash_clientside.callback_context.triggered;
        if (!triggered || triggered.length === 0) {
            return window.dash_clientside.no_update;
        }

        // Show spinner immediately
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
        };
    },

    /**
     * Immediately show loading spinner when build tab is clicked
     * This runs BEFORE the Python callback, eliminating perceived delay
     *
     * @param {Array} n_clicks_list - Array of n_clicks from all build tabs
     * @param {number} active_idx - Current active build index
     * @param {boolean} is_loading - Whether a build operation is in progress
     * @returns {Object} Style object for loading overlay
     */
    show_spinner_on_tab_click: function(n_clicks_list, active_idx, is_loading) {
        const no_upd = window.dash_clientside.no_update;

        // Check if triggered and not already loading
        const triggered = window.dash_clientside.callback_context.triggered;
        if (!triggered || triggered.length === 0 || is_loading) {
            return no_upd;
        }

        // Check if any tab was actually clicked
        if (!n_clicks_list || !n_clicks_list.some(n => n > 0)) {
            return no_upd;
        }

        // Parse triggered ID to get clicked index
        const triggered_id = triggered[0].prop_id;
        const match = triggered_id.match(/"index":(\d+)/);
        if (!match) {
            return no_upd;
        }

        const clicked_index = parseInt(match[1]);

        // If clicking the same build, no spinner needed
        if (clicked_index === active_idx) {
            return no_upd;
        }

        // Show spinner immediately for build switch
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
        };
    }
};
