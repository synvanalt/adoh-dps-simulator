# Third-party imports
from dash import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px


# Fixed color palette for damage types (keys are normalized to lowercase base token)
DAMAGE_TYPE_PALETTE = {
    'acid':         '#096F06',  # dark green
    'cold':         '#88DDDD',  # icy blue
    'divine':       '#FFD400',  # golden yellow
    'electrical':   '#0559DC',  # electric blue
    'fire':         '#D80406',  # deep red
    'magical':      '#B067DA',  # violet
    'negative':     '#7A797A',  # dark gray
    'physical':     '#D45603',  # rich orange
    'sonic':        '#DC8401',  # amber
    'positive':     '#CFCED1',  # light gray
    'pure':         '#CC159C',  # magenta
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
    fig.update_yaxes(
        ticklabelposition="outside left",
        ticklabelstandoff=10,
        automargin=True,
        **axis_style
    )
    return fig


def register_plots_callbacks(app):

    def is_multi_build_format(results_dict):
        """Check if results are in multi-build format {build_name: {weapon: results}}."""
        if not results_dict:
            return False
        first_value = next(iter(results_dict.values()))
        return isinstance(first_value, dict) and 'summary' not in first_value

    def flatten_results(results_dict):
        """Flatten multi-build results to list of (build_name, weapon, results) tuples."""
        if is_multi_build_format(results_dict):
            flattened = []
            for build_name, weapons_results in results_dict.items():
                for weapon, results in weapons_results.items():
                    flattened.append((build_name, weapon, results))
            return flattened
        else:
            # Legacy format
            return [('Build 1', weapon, results) for weapon, results in results_dict.items()]

    # Callback: populate build dropdown for per-weapon plots
    @app.callback(
        Output('plots-build-dropdown', 'options'),
        Output('plots-build-dropdown', 'value'),
        Input('intermediate-value', 'data'),
        prevent_initial_call=True
    )
    def populate_build_dropdown(results_dict):
        if not results_dict:
            return [], None

        if is_multi_build_format(results_dict):
            builds = list(results_dict.keys())
        else:
            builds = ['Build 1']

        options = [{'label': b, 'value': b} for b in builds]
        return options, builds[0] if builds else None

    # Callback: populate weapon dropdown based on selected build
    @app.callback(
        Output('plots-weapon-dropdown', 'options'),
        Output('plots-weapon-dropdown', 'value'),
        Input('intermediate-value', 'data'),
        Input('plots-build-dropdown', 'value'),
        prevent_initial_call=True
    )
    def populate_weapon_dropdown(results_dict, selected_build):
        if not results_dict:
            return [], None

        if is_multi_build_format(results_dict):
            if selected_build and selected_build in results_dict:
                weapons = list(results_dict[selected_build].keys())
            else:
                # Fall back to first build
                first_build = next(iter(results_dict.keys()))
                weapons = list(results_dict[first_build].keys())
        else:
            weapons = list(results_dict.keys())

        options = [{'label': w, 'value': w} for w in weapons]
        return options, weapons[0] if weapons else None

    # Callback: DPS Comparison bar chart - three horizontal subplots
    @app.callback(
        Output('plots-dps-comparison', 'figure'),
        Input('intermediate-value', 'data'),
        Input('dps-weights-store', 'data'),
        prevent_initial_call=True
    )
    def update_dps_comparison_figure(results_dict, weights_data):
        from plotly.subplots import make_subplots

        if not results_dict:
            fig = go.Figure()
            fig.update_layout(title='No simulation data')
            apply_dark_theme(fig)
            return fig

        # Get weights from store (default 50/50)
        crit_weight = weights_data.get('crit_allowed', 50) if weights_data else 50
        immune_weight = 100 - crit_weight
        weight_fraction = crit_weight / 100

        flattened = flatten_results(results_dict)

        # Create list of (build_name, weapon, avg_dps, dps_crits, dps_no_crits) tuples
        data_list = []
        for build_name, weapon, results in flattened:
            # Calculate weighted average dynamically
            weighted_avg = results['dps_crits'] * weight_fraction + results['dps_no_crits'] * (1 - weight_fraction)
            data_list.append({
                'label': f'{build_name} | {weapon}',
                'build': build_name,
                'weapon': weapon,
                'avg_dps': weighted_avg,
                'dps_crits': results['dps_crits'],
                'dps_no_crits': results['dps_no_crits'],
            })

        # Sort by avg_dps descending (highest first)
        data_list.sort(key=lambda x: x['avg_dps'], reverse=False)

        # Extract sorted data
        labels = [d['label'] for d in data_list]
        avg_dps_values = [d['avg_dps'] for d in data_list]
        dps_crits_values = [d['dps_crits'] for d in data_list]
        dps_no_crits_values = [d['dps_no_crits'] for d in data_list]

        # Assign consistent colors to each build+weapon combination
        # Sort labels alphabetically to create a stable color mapping independent of DPS order
        color_palette = px.colors.qualitative.Plotly + px.colors.qualitative.Set3
        sorted_labels = sorted(labels)
        label_to_color = {label: color_palette[i % len(color_palette)] for i, label in enumerate(sorted_labels)}
        colors = [label_to_color[label] for label in labels]

        # Dynamic subplot title
        avg_dps_title = f'Average DPS ({crit_weight}/{immune_weight} Allowed/Immune)'

        # Create subplots: 3 rows, shared x-axis
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=(avg_dps_title, 'Crit Allowed', 'Crit Immune'),
            row_heights=[0.33, 0.33, 0.33]
        )

        # Add horizontal bars for each subplot
        # Row 1: Average DPS (50/50)
        fig.add_trace(
            go.Bar(
                y=labels,
                x=avg_dps_values,
                orientation='h',
                marker_color=colors,
                showlegend=False,
                hovertemplate='%{y}<br>DPS: %{x:.2f}<extra></extra>',
                text = avg_dps_values,
                texttemplate = '%{text:.2f}',
                textposition = 'outside',
                textfont = dict(color=colors),
                cliponaxis = False,
            ),
            row=1, col=1
        )

        # Row 2: Crit Allowed
        fig.add_trace(
            go.Bar(
                y=labels,
                x=dps_crits_values,
                orientation='h',
                marker_color=colors,
                showlegend=False,
                hovertemplate='%{y}<br>DPS: %{x:.2f}<extra></extra>',
                text=dps_crits_values,
                texttemplate='%{text:.2f}',
                textposition='outside',
                textfont=dict(color=colors),
            ),
            row=2, col=1
        )

        # Row 3: Crit Immune
        fig.add_trace(
            go.Bar(
                y=labels,
                x=dps_no_crits_values,
                orientation='h',
                marker_color=colors,
                showlegend=False,
                hovertemplate='%{y}<br>DPS: %{x:.2f}<extra></extra>',
                text=dps_no_crits_values,
                texttemplate='%{text:.2f}',
                textposition='outside',
                textfont=dict(color=colors),
            ),
            row=3, col=1
        )

        # Update layout
        fig.update_xaxes(title_text='DPS', row=3, col=1)
        fig.update_layout(
            height=max(300, len(labels) * 100),  # Dynamic height based on number of bars
            showlegend=False,
        )

        apply_dark_theme(fig)
        return fig

    # Callback: DPS vs damage and damage breakdown pie
    @app.callback(
        Output('plots-weapon-dps-vs-damage', 'figure'),
        Output('plots-weapon-breakdown', 'figure'),
        Input('plots-weapon-dropdown', 'value'),
        Input('plots-build-dropdown', 'value'),
        State('intermediate-value', 'data'),
        prevent_initial_call=True
    )
    def update_weapon_plots(selected_weapon, selected_build, results_dict):
        empty_fig = go.Figure()
        empty_fig.update_layout(title='No simulation data')
        apply_dark_theme(empty_fig)

        if not results_dict or not selected_weapon:
            return empty_fig, empty_fig

        # Get results based on format
        if is_multi_build_format(results_dict):
            if not selected_build or selected_build not in results_dict:
                return empty_fig, empty_fig
            build_results = results_dict[selected_build]
            if selected_weapon not in build_results:
                return empty_fig, empty_fig
            results = build_results[selected_weapon]
        else:
            if selected_weapon not in results_dict:
                return empty_fig, empty_fig
            results = results_dict[selected_weapon]

        # DPS vs Cumulative Damage: use cumulative damage (x) vs rolling avg DPS (y)
        dps_vals = results.get('dps_rolling_avg') or results.get('dps_per_round') or []
        cum_damage = results.get('cumulative_damage_per_round') or []
        fig1 = go.Figure()
        if dps_vals and cum_damage:
            n = min(len(dps_vals), len(cum_damage))
            # X = cumulative damage, Y = DPS
            fig1.add_trace(go.Scatter(
                x=cum_damage[:n],
                y=dps_vals[:n],
                mode='lines+markers',
                marker=dict(opacity=0.9),
                hovertemplate='DPS: %{y:.2f}<br>Cumulative Damage: %{x}<extra></extra>',
            ))
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
                dmg_color = DAMAGE_TYPE_PALETTE.get(key)
                if not dmg_color:
                    dmg_color = FALLBACK_COLORS[abs(hash(lab)) % len(FALLBACK_COLORS)]
                colors.append(dmg_color)

            fig2 = px.pie(
                names=labels,
                values=values,
                title=f'',
            )
            fig2.update_traces(
                textinfo='percent+label',
                textfont=dict(color='#f8f9fa'),
                marker=dict(colors=colors, line=dict(color='rgba(255,255,255,0.06)', width=1)),
                hovertemplate='Type: %{label}<br>Damage: %{value}<extra></extra>',
            )
        else:
            fig2 = go.Figure()
            fig2.update_layout(title='No damage breakdown available')
        apply_dark_theme(fig2)

        return fig1, fig2
