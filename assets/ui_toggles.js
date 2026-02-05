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

window.dash_clientside.clientside.toggle_additional_damage = function(isEnabled) {
    return isEnabled;
};

window.dash_clientside.clientside.toggle_damage_limit = function(isEnabled) {
    return isEnabled;
};
