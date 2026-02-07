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
 * Clientside callback for instant immunity inputs UI update when toggling OFF.
 * When switch is OFF: immediately set all inputs to 0 and disable them.
 * When switch is ON: return no_update to let the server callback handle restoration.
 *
 * @param {boolean} isEnabled - The switch value
 * @param {Array} currentValues - Current immunity input values (needed for output length)
 * @returns {Array} [values, disabled] - Arrays for input values and disabled states
 */
window.dash_clientside.clientside.toggle_immunities_inputs = function(isEnabled, currentValues) {
    const n = currentValues.length;

    if (!isEnabled) {
        // Switch OFF: immediately show zeros and disable inputs
        const zeros = Array(n).fill(0);
        const disabled = Array(n).fill(true);
        return [zeros, disabled];
    } else {
        // Switch ON: let server callback handle value restoration
        return [Array(n).fill(window.dash_clientside.no_update), Array(n).fill(window.dash_clientside.no_update)];
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

