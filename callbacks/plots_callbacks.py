# Third-party imports
from dash import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px


# Fixed color palette for damage types (keys are normalized to lowercase base token)
DAMAGE_TYPE_PALETTE = {
    'physical': '#D45603',  # rich orange
    'fire': '#D80406',  # deep red
    'cold': '#88DDDD',  # icy blue
    'acid': '#096F06',  # dark green
    'electrical': '#0559DC',  # electric blue
    'sonic': '#DC8401',  # amber
    'negative': '#7A797A',  # dark gray
    'positive': '#CFCED1',  # light gray
    'pure': '#CC159C',  # magenta
    'magical': '#B067DA',  # violet
    'divine': '#E1DE02',  # golden yellow
}

FALLBACK_COLORS = px.colors.qualitative.Plotly


# Dark theme helper to match Bootstrap dark mode
def apply_dark_theme(fig):
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f8f9fa'),
        legend=dict(bgcolor='rgba(0,0,0,0)'),
        margin=dict(l=40, r=20, t=40, b=40),
    )
    axis_style = dict(
        gridcolor='rgba(255,255,255,0.06)',
        zerolinecolor='rgba(255,255,255,0.06)',
        tickfont=dict(color='#f8f9fa'),
        title=dict(font=dict(color='#f8f9fa'))
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
    return fig


def register_plots_callbacks(app):

    # Callback: weapon dropdown with available weapons from the simulation results
    @app.callback(
        Output('plots-weapon-dropdown', 'options'),
        Output('plots-weapon-dropdown', 'value'),
        Input('intermediate-value', 'data'),
    )
    def populate_weapon_dropdown(results_dict):
        if not results_dict:
            return [], None
        weapons = list(results_dict.keys())
        options = [{'label': w, 'value': w} for w in weapons]
        # default to first weapon
        return options, weapons[0]

    # Callback: DPS Comparison bar chart
    @app.callback(
        Output('plots-dps-comparison', 'figure'),
        Input('intermediate-value', 'data')
    )
    def update_dps_comparison_figure(results_dict):
        fig = go.Figure()
        if not results_dict:
            fig.update_layout(title='No simulation data')
            apply_dark_theme(fig)
            return fig

        weapons = []
        dps_crits = []
        dps_no_crits = []
        dps_avg = []

        for weapon, results in results_dict.items():
            weapons.append(weapon)
            dps_crits.append(results['dps_crits'])
            dps_no_crits.append(results['dps_no_crits'])
            dps_avg.append(results['avg_dps_both'])

        # Create grouped bar chart
        fig.add_trace(go.Bar(name='Crits Allowed', x=weapons, y=dps_crits))
        fig.add_trace(go.Bar(name='Crits Immune', x=weapons, y=dps_no_crits))
        fig.add_trace(go.Bar(name='Average DPS', x=weapons, y=dps_avg))

        # Update layout for better readability
        fig.update_layout(
            barmode='group',
            xaxis_title='Weapons',
            yaxis_title='DPS',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        apply_dark_theme(fig)
        return fig

    # Callback: DPS vs damage and damage breakdown pie
    @app.callback(
        Output('plots-weapon-dps-vs-damage', 'figure'),
        Output('plots-weapon-breakdown', 'figure'),
        Input('plots-weapon-dropdown', 'value'),
        State('intermediate-value', 'data')
    )
    def update_weapon_plots(selected_weapon, results_dict):
        empty_fig = go.Figure()
        empty_fig.update_layout(title='No simulation data')
        apply_dark_theme(empty_fig)

        if not results_dict or not selected_weapon or selected_weapon not in results_dict:
            return empty_fig, empty_fig

        results = results_dict[selected_weapon]

        # DPS vs Cumulative Damage: use cumulative damage (x) vs rolling avg DPS (y)
        dps_vals = results.get('dps_rolling_avg') or results.get('dps_per_round') or []
        cum_damage = results.get('cumulative_damage_per_round') or []
        fig1 = go.Figure()
        if dps_vals and cum_damage:
            n = min(len(dps_vals), len(cum_damage))
            # X = cumulative damage, Y = DPS
            fig1.add_trace(go.Scatter(x=cum_damage[:n], y=dps_vals[:n], mode='lines+markers', marker=dict(opacity=0.9)))
            fig1.update_layout(title=f'', xaxis_title='Cumulative Damage', yaxis_title='Mean DPS')
        else:
            fig1.update_layout(title='Insufficient data for DPS vs Damage')
        apply_dark_theme(fig1)

        # Damage breakdown pie
        dmg_by_type = results.get('damage_by_type') or {}
        if dmg_by_type:
            labels = [k.split('_')[0].title() for k in dmg_by_type.keys()]
            values = [v for v in dmg_by_type.values()]
            colors = []
            for lab in labels:
                key = lab.lower()
                col = DAMAGE_TYPE_PALETTE.get(key)
                if not col:
                    col = FALLBACK_COLORS[abs(hash(lab)) % len(FALLBACK_COLORS)]
                colors.append(col)

            fig2 = px.pie(names=labels, values=values, title=f'')
            fig2.update_traces(textinfo='percent+label', textfont=dict(color='#f8f9fa'), marker=dict(colors=colors, line=dict(color='rgba(255,255,255,0.06)', width=1)))
        else:
            fig2 = go.Figure()
            fig2.update_layout(title='No damage breakdown available')
        apply_dark_theme(fig2)

        return fig1, fig2
