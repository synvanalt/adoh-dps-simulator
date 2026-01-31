import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# ---------------------------
# Mock helpers (stand-ins for your app)
# ---------------------------

def flatten_results(results_dict):
    """
    Converts:
    {
        build: {
            weapon: {
                avg_dps_both, dps_crits, dps_no_crits
            }
        }
    }
    → list of (build, weapon, results)
    """
    flattened = []
    for build, weapons in results_dict.items():
        for weapon, results in weapons.items():
            flattened.append((build, weapon, results))
    return flattened


def apply_dark_theme(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111",
        plot_bgcolor="#111",
        font=dict(size=13)
    )


# ---------------------------
# Your function (with mocked data)
# ---------------------------

def update_dps_comparison_figure(results_dict):
    if not results_dict:
        fig = go.Figure()
        fig.update_layout(title='No simulation data')
        apply_dark_theme(fig)
        return fig

    flattened = flatten_results(results_dict)

    data_list = []
    for build_name, weapon, results in flattened:
        data_list.append({
            'label': f'{build_name} - {weapon}',
            'avg_dps': results['avg_dps_both'],
            'dps_crits': results['dps_crits'],
            'dps_no_crits': results['dps_no_crits'],
        })

    # Sort lowest → highest so bars stack nicely
    data_list.sort(key=lambda x: x['avg_dps'])

    labels = [d['label'] for d in data_list]
    avg_dps_values = [d['avg_dps'] for d in data_list]
    dps_crits_values = [d['dps_crits'] for d in data_list]
    dps_no_crits_values = [d['dps_no_crits'] for d in data_list]

    color_palette = px.colors.qualitative.Plotly
    colors = [color_palette[i % len(color_palette)] for i in range(len(labels))]

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('Average DPS (50/50 Allowed/Immune)', 'Crit Allowed', 'Crit Immune')
    )

    fig.add_trace(
        go.Bar(
            y=labels,
            x=avg_dps_values,
            orientation='h',
            marker_color=colors,
            hovertemplate='%{y}<br>DPS: %{x:.2f}<extra></extra>',
            text = avg_dps_values,
            texttemplate = '%{text:.2f}',
            textposition = 'outside',
            textfont=dict(color=colors),
            cliponaxis = False,
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            y=labels,
            x=dps_crits_values,
            orientation='h',
            marker_color=colors,
            hovertemplate = '%{y}<br>DPS: %{x:.2f}<extra></extra>',
            text = dps_crits_values,
            texttemplate = '%{text:.2f}',
            textposition = 'outside',
            textfont=dict(color=colors),
            cliponaxis = False,
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Bar(
            y=labels,
            x=dps_no_crits_values,
            orientation='h',
            marker_color=colors,
            hovertemplate='%{y}<br>DPS: %{x:.2f}<extra></extra>',
            text=dps_no_crits_values,
            texttemplate='%{text:.2f}',
            textposition='outside',
            textfont=dict(color=colors),
            cliponaxis=False,
        ),
        row=3, col=1
    )

    # ---------------------------
    # Y-axis label alignment tweaks (THE POINT OF THE DEMO)
    # ---------------------------

    fig.update_yaxes(
        # ticklabelposition="outside left",
        ticklabelstandoff=10,
        # automargin=True
    )

    fig.update_layout(
        height=600,
        margin=dict(l=260),  # makes labels feel properly left-aligned
        showlegend=False
    )

    fig.update_xaxes(title_text='DPS', row=3, col=1, rangemode='tozero')

    apply_dark_theme(fig)
    return fig


# ---------------------------
# Mocked input data
# ---------------------------

mock_results = {
    "Woo Wildrock": {
        "Dire Mace": {
            "avg_dps_both": 82.4,
            "dps_crits": 96.2,
            "dps_no_crits": 68.7
        }
    },
    "Woo Warborn": {
        "Dire Mace": {
            "avg_dps_both": 74.1,
            "dps_crits": 88.9,
            "dps_no_crits": 59.3
        }
    },
    "Woo Wildflower": {
        "Dire Mace": {
            "avg_dps_both": 65.8,
            "dps_crits": 79.5,
            "dps_no_crits": 52.2
        }
    },
    "Woo Warmace": {
        "Dire Mace": {
            "avg_dps_both": 91.6,
            "dps_crits": 108.3,
            "dps_no_crits": 74.9
        }
    }
}


# ---------------------------
# Run it
# ---------------------------

fig = update_dps_comparison_figure(mock_results)
fig.show()
