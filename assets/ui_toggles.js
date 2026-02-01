/**
 * Clientside callbacks for UI show/hide toggles
 * These run in the browser for instant UI updates
 */
window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.clientside = window.dash_clientside.clientside || {};

// Simply return the boolean value.
// If Switch is ON (true) -> is_open = true (Expanded)
// If Switch is OFF (false) -> is_open = false (Collapsed)

window.dash_clientside.clientside.toggle_dual_wield_section = function(isEnabled) {
    return isEnabled;
};

// Helper constants
const STYLE_SHOW = {'display': 'flex'};
const STYLE_HIDE = {'display': 'none'};


window.dash_clientside.clientside.toggle_shape_weapon = function(isEnabled) {
    return isEnabled ? STYLE_SHOW : STYLE_HIDE;
};

window.dash_clientside.clientside.toggle_additional_damage = function(isEnabled) {
    return isEnabled ? STYLE_SHOW : STYLE_HIDE;
};

window.dash_clientside.clientside.toggle_damage_limit = function(isEnabled) {
    return isEnabled ? STYLE_SHOW : STYLE_HIDE;
};
