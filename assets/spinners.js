/**
 * Clientside callbacks for spinners during long operations
 */
window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.clientside = window.dash_clientside.clientside || {};

// Centralized spinner style to ensure consistency across all triggers
const spinner_style = {
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

window.dash_clientside.clientside.show_spinner_on_button_click = function(add, dup, del) {
    const triggered = window.dash_clientside.callback_context.triggered;
    if (!triggered || triggered.length === 0) return window.dash_clientside.no_update;
    return spinner_style;
};

window.dash_clientside.clientside.show_spinner_on_reset_click = function(reset, sticky) {
    const triggered = window.dash_clientside.callback_context.triggered;
    if (!triggered || triggered.length === 0) return window.dash_clientside.no_update;
    return spinner_style;
};

window.dash_clientside.clientside.show_spinner_on_weights_apply = function(apply) {
    const triggered = window.dash_clientside.callback_context.triggered;
    if (!triggered || triggered.length === 0) return window.dash_clientside.no_update;
    return spinner_style;
};

window.dash_clientside.clientside.show_spinner_on_tab_click = function(n_clicks_list, active_idx, is_loading) {
    const triggered = window.dash_clientside.callback_context.triggered;
    const no_upd = window.dash_clientside.no_update;

    if (!triggered || triggered.length === 0 || is_loading) return no_upd;
    if (!n_clicks_list || !n_clicks_list.some(n => n > 0)) return no_upd;

    const triggered_id = triggered[0].prop_id;
    const match = triggered_id.match(/"index":(\d+)/);

    if (!match) return no_upd;

    const clicked_index = parseInt(match[1]);
    if (clicked_index === active_idx) return no_upd;

    return spinner_style;
};