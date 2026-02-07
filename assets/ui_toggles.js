/**
 * Clientside callbacks for UI show/hide toggles
 * These run in the browser for instant UI updates
 */
window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.clientside = window.dash_clientside.clientside || {};

// Return boolean values for dbc.Fade is_in property
// If Switch is ON (true) -> is_in = true (Fade in)
// If Switch is OFF (false) -> is_in = false (Fade out)

window.dash_clientside.clientside.toggle_dual_wield_section = function(isEnabled) {
    return isEnabled;  // is_open for Collapse (already has animation)
};

window.dash_clientside.clientside.toggle_shape_weapon = function(isEnabled) {
    return isEnabled;
};

window.dash_clientside.clientside.toggle_custom_offhand_weapon = function(isEnabled) {
    return isEnabled;  // is_open for Collapse
};

window.dash_clientside.clientside.toggle_damage_limit = function(isEnabled) {
    return isEnabled;
};

window.dash_clientside.clientside.toggle_additional_damage = function(isEnabled) {
    return isEnabled;
};

/**
 * Fully clientside callback for immunity inputs toggle with store persistence.
 * When switch is OFF: save current values to store, set inputs to 0, disable them.
 * When switch is ON: restore values from store, enable inputs.
 *
 * @param {boolean} isEnabled - The switch value
 * @param {Array} currentValues - Current immunity input values
 * @param {Object} immunityStore - The immunities-store data (fractions)
 * @param {Object} configStore - The config-store data (contains TARGET_IMMUNITIES as fallback)
 * @returns {Array} [values, disabled, updatedStore] - Arrays for input values, disabled states, and updated store
 */
window.dash_clientside.clientside.toggle_immunities_inputs = function(isEnabled, currentValues, immunityStore, configStore) {
    const n = currentValues.length;

    // Immunity names in order (matching Python config)
    const names = ['pure', 'magical', 'positive', 'divine', 'negative', 'sonic', 'acid', 'electrical', 'cold', 'fire', 'physical'];

    if (!isEnabled) {
        // Switch OFF: save current values to store, then show zeros and disable
        const updatedStore = {};
        for (let i = 0; i < n; i++) {
            // Convert percentage to fraction for storage
            updatedStore[names[i]] = (currentValues[i] || 0) / 100;
        }
        const zeros = Array(n).fill(0);
        const disabled = Array(n).fill(true);
        return [zeros, disabled, updatedStore];
    } else {
        // Switch ON: restore values from store or config, enable inputs
        immunityStore = immunityStore || {};

        const restoredValues = [];
        for (let i = 0; i < n; i++) {
            const name = names[i];
            // Priority: immunities-store > config-store > default 0
            if (immunityStore[name] !== undefined) {
                restoredValues.push(Math.round(immunityStore[name] * 100));
            } else if (configStore && configStore.TARGET_IMMUNITIES && configStore.TARGET_IMMUNITIES[name] !== undefined) {
                restoredValues.push(Math.round(configStore.TARGET_IMMUNITIES[name] * 100));
            } else {
                restoredValues.push(0);
            }
        }
        const enabled = Array(n).fill(false);
        // Return no_update for store since we're just reading from it
        return [restoredValues, enabled, window.dash_clientside.no_update];
    }
};

/**
 * Clientside callback for instant combat type toggle UI updates.
 * When ranged: disable melee switches, set to false, set mighty to 20, enable mighty
 * When melee: enable melee switches, set mighty to 0, disable mighty
 *
 * @param {string} combatType - 'melee' or 'ranged'
 * @param {Array} currentMeleeSwitchValues - Current melee switch values (for array length)
 * @returns {Array} [meleeSwitchValues, mightyValue, meleeSwitchDisabled, mightyDisabled]
 */
window.dash_clientside.clientside.toggle_melee_params = function(combatType, currentMeleeSwitchValues) {
    const n = currentMeleeSwitchValues.length;

    if (combatType === 'ranged') {
        return [
            Array(n).fill(false),  // Turn OFF all melee switches
            20,                    // Set mighty to 20
            Array(n).fill(true),   // Disable all melee switches
            false                  // Enable mighty input
        ];
    } else if (combatType === 'melee') {
        return [
            Array(n).fill(window.dash_clientside.no_update),  // Don't update melee switches
            0,                     // Set mighty to 0
            Array(n).fill(false),  // Enable all melee switches
            true                   // Disable mighty input
        ];
    } else {
        return [
            Array(n).fill(window.dash_clientside.no_update),
            window.dash_clientside.no_update,
            Array(n).fill(window.dash_clientside.no_update),
            window.dash_clientside.no_update
        ];
    }
};

window.dash_clientside.clientside.toggle_about_modal = function(link_clicks, close_clicks, is_open) {
    // Toggle the modal state when either button is clicked
    return !is_open;
};

/**
 * Clientside callback to switch to results tab and scroll to top when simulation completes.
 * This ensures users start reading results from the top of the page.
 *
 * @param {Object} results - The simulation results from intermediate-value store
 * @returns {string} - The tab id to activate ('results') or no_update
 */
window.dash_clientside.clientside.switch_to_results_tab = function(results) {
    if (results) {
        // Scroll to top of page after a small delay to ensure tab has switched
        setTimeout(function() {
            window.scrollTo({ top: 0, behavior: 'instant' });
        }, 50);
        return 'results';
    }
    return window.dash_clientside.no_update;
};

