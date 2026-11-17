import logging

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, callback, dcc, html, page_container

logger = logging.getLogger(__file__)

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_ignore=r"quartz\.css",
)

sidebar = html.Div(
    [
        dbc.Switch(id="Manon theme", label="Manon theme", value=False),
        html.Link(id="theme-link", rel="stylesheet", href=""),
        dcc.Link("home page", href="/", className="text-white text-decoration-none"),
        html.Br(),
        html.Br(),
        dcc.Link(
            "signal visualisation",
            href="/basic_signals",
            className="text-white text-decoration-none",
        ),
        html.Br(),
        html.Br(),
        dcc.Link(
            "smoothing & peaks",
            href="/peaks",
            className="text-white text-decoration-none",
        ),
        html.Br(),
        html.Br(),
        dcc.Link(
            "Photo bleaching",
            href="/photobleaching",
            className="text-white text-decoration-none",
        ),
        html.Br(),
        html.Br(),
        dcc.Link(
            "events Area under the curve",
            href="/events_auc",
            className="text-white text-decoration-none",
        ),
        html.Br(),
        html.Br(),
        dcc.Link(
            "boxplots", href="/boxplots", className="text-white text-decoration-none"
        ),
    ],
    # className="bg-primary",
    style={
        "width": "15em",
        "padding": "20px",
        "backgroundColor": "#4C8BCA",  # "#3F9FD4",
        "minHeight": "100vh",
    },
)


app.layout = html.Div(
    [sidebar, html.Div([page_container], style={"flex": "1"})],
    # className="bg-body",
    style={"display": "flex", "minHeight": "100vh"},
)


@callback(Output("theme-link", "href"), Input("Manon theme", "value"))
def change_theme(value):
    if value:
        return dbc.themes.QUARTZ
    return ""


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    setup_logging(args.debug)
    app.run(debug=args.debug)
