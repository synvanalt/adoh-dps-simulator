import dash_bootstrap_components as dbc
from dash import html


def build_navbar():
    # Define the logo and brand text as a single layout
    brand_content = html.Span([
        html.Img(src="/assets/logo.png", height="30px", className="me-2"),
        "My App Name"
    ], style={"display": "flex", "alignItems": "center"})

    navbar = dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand([
                    html.Img(src="/assets/logo.png", height="30px", className="me-2"),
                    html.Span("ADOH DPS Simulator", style={"color": "#C7E2F0"}),
                    ],
                    className="ms-2"
                ),
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("About", id="about-link", n_clicks=0, style={"cursor": "pointer"})),
                    ],
                    className="ms-auto",
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        color="primary",
        dark=True,
    )
    return navbar
