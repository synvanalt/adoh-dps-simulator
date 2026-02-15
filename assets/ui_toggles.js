/**
 * Clientside callbacks for UI show/hide toggles
 * These run in the browser for instant UI updates
 */
window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.clientside = window.dash_clientside.clientside || {};

function _get_live_immunity_switch_state() {
    const root = document.getElementById('target-immunities-switch');
    if (!root) return null;

    if (typeof root.checked === 'boolean') {
        return root.checked;
    }

    const checkbox = root.querySelector('input[type="checkbox"]');
    if (checkbox && typeof checkbox.checked === 'boolean') {
        return checkbox.checked;
    }

    return null;
}

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
 * UI-only callback for immunity inputs toggle.
 * Store synchronization is handled by a separate callback to avoid race conditions.
 *
 * @param {boolean} isEnabled - The switch value
 * @param {Array} currentValues - Current immunity input values
 * @param {Object} immunityStore - The immunities-store data (fractions)
 * @param {Object} configStore - The config-store data (contains TARGET_IMMUNITIES as fallback)
 * @returns {Array} [values, disabled] - Arrays for input values and disabled states
 */
window.dash_clientside.clientside.toggle_immunities_inputs = function(isEnabled, currentValues, immunityStore, configStore) {
    const n = currentValues.length;
    const no_upd = window.dash_clientside.no_update;

    // Ignore stale callback executions: if the live switch state has already changed,
    // this invocation is outdated and must not overwrite UI with old values.
    const liveSwitchState = _get_live_immunity_switch_state();
    if (liveSwitchState !== null && liveSwitchState !== isEnabled) {
        return [Array(n).fill(no_upd), Array(n).fill(no_upd)];
    }

    // Immunity names in order (matching Python config)
    const names = ['pure', 'magical', 'positive', 'divine', 'negative', 'sonic', 'acid', 'electrical', 'cold', 'fire', 'physical'];

    if (!isEnabled) {
        // Switch OFF: presentation only (show zeros and disable)
        const zeros = Array(n).fill(0);
        const disabled = Array(n).fill(true);
        return [zeros, disabled];
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
        return [restoredValues, enabled];
    }
};

/**
 * Keep immunities-store synced from live UI edits while switch is ON.
 *
 * @param {Array} currentValues - Current immunity input values in percent
 * @param {boolean} isEnabled - The switch value
 * @param {Array} disabledStates - Current disabled state for immunity inputs
 * @param {Object} currentStore - Existing store data
 * @returns {Object|symbol} - Updated store data or no_update
 */
window.dash_clientside.clientside.sync_immunities_store = function(
    currentValues,
    isEnabled,
    disabledStates,
    currentStore
) {
    if (!isEnabled || !currentValues) {
        return window.dash_clientside.no_update;
    }

    // Ignore persistence while any immunity input is disabled (OFF flow / programmatic updates).
    if (disabledStates && disabledStates.some(Boolean)) {
        return window.dash_clientside.no_update;
    }

    const names = ['pure', 'magical', 'positive', 'divine', 'negative', 'sonic', 'acid', 'electrical', 'cold', 'fire', 'physical'];
    const updatedStore = {};

    for (let i = 0; i < names.length && i < currentValues.length; i++) {
        updatedStore[names[i]] = (currentValues[i] || 0) / 100;
    }

    // Skip update when nothing changed or when a bulk programmatic update happened.
    // User edits change one field at a time; OFF/ON/reset/load typically change many.
    if (currentStore) {
        let changedCount = 0;
        for (let i = 0; i < names.length; i++) {
            if (updatedStore[names[i]] !== currentStore[names[i]]) {
                changedCount += 1;
            }
        }
        if (changedCount === 0 || changedCount > 1) {
            return window.dash_clientside.no_update;
        }
    }

    return updatedStore;
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

