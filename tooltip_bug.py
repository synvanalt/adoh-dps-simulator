import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Force mobile viewport scaling and Bootstrap dark mode
# app.index_string = """
# <!DOCTYPE html>
# <html lang="en" data-bs-theme="dark">
#     <head>
#         {%metas%}
#         <meta name="viewport" content="width=device-width, initial-scale=1">
#         <title>ADOH DPS Simulator</title>
#         {%favicon%}
#         {%css%}
#     </head>
#     <body>
#         {%app_entry%}
#         <footer>
#             {%config%}
#             {%scripts%}
#             {%renderer%}
#         </footer>
#     </body>
# </html>
# """

app.layout = html.Div([
    html.Div(
        style={
            'backdrop-filter': 'blur(8px) saturate(120%)',
            'padding': '50px',
            'border': '1px solid #ccc'
        },
        children=[
            dbc.Button("Hover me", id="btn-hover", size="sm"),
            dbc.Tooltip(
                "Tooltip text very long text very long text very long text very long text very long text"
                " very long text very long text very long text very long text very long text"
                " very long text very long text very long text very long text very long text",
                target="btn-hover",
                placement="top",
                fade=False,
                delay={'show': 200, 'hide': 0}
            )
        ]
    )
])

if __name__ == '__main__':
    app.run(debug=True)