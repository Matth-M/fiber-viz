import glob
import os
from pathlib import Path

import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import scipy.signal as s
from dash import Input, Output, callback, dcc, html
from scipy.ndimage import gaussian_filter1d

from src.utils import DATA_ROOT

dash.register_page(__name__, path="/photobleaching")

graphs_root_folder = DATA_ROOT.joinpath("linear_regressions_graphs")

layout = html.Div(
    [
        html.H3("Photobleaching over time"),
        html.H6("Definition"),
        dcc.Markdown(
            "Photobleaching is a phenomenon in which the fluorescence of a fluorophore (a fluorescent molecule or dye) is permanently reduced or eliminated upon prolonged exposure to light. This process occurs due to the photochemical destruction or alteration of the fluorophore molecules, rendering them non-fluorescent. - *Photonics.com*"
        ),
        html.H6("Materials & methods"),
        dcc.Markdown(
            "Neuronal activation causes an influx of calcium into the cell, Ca²⁺ then binds to calmodulin, causing a conformational change in calmodulin M13, which induces an increase in GFP fluorescence. - *Manon Moreau, PhD*"
        ),
        dcc.Markdown("Vizualize it below!"),
        html.Div(
            [
                dcc.Input(
                    id="root_folder",
                    value=str(graphs_root_folder),
                ),
                dcc.Dropdown(
                    id="graph_file",
                    placeholder="Select a graph",
                ),
            ],
            style={"color": "black"},
        ),
        html.Div(
            [
                html.Iframe(
                    id="photobleaching_graph",
                    # style={
                    #     "width": "100%",
                    #     "height": "800px",
                    #     "border": "none"}),])
                    style={
                        "width": "100%",
                        "height": "480px",
                        "border": "none",
                        # "transform": "scale()",
                        "transformOrigin": "top left",
                    },
                ),
            ]
        ),
        dcc.Markdown(
            """**Traces depicting photobleaching across successive recordings.** The x-axis represents individual csv recordings from a single mouse, arranged in chronological order and therefore reflects the progression of mouse recordings over time. For each csv file, the mean signal amplitude was calculated independently for CH410 and CH470 and plotted on the y-axis. Both channels show an overall decrease in mean signal amplitude throughout the experiment, as indicated by the negative slopes of their linear regressions (cf.legend). The similar negative trends observed in both channels are consistent with progressive photobleaching over the course of the experiment."""
        ),
    ],
    style={"padding": "20px"},
)

@callback(
    Output("photobleaching_graph", "srcDoc"),
    Input("graph_file", "value"),
)
def update_boxplot(file_selection):
    if file_selection is None:
        return ""

    file = Path(file_selection)
    if not file.exists():
        return ""

    return file.read_text(encoding="utf-8")

@callback(
    Output("graph_file", "options"),
    Input("root_folder", "value"),
)
def graph_file(root_folder):
    if root_folder is None:
        return []
    root = Path(root_folder)
    if not root.exists():
        logger.debug(f"{root} not found")
        return []

    return [
        {"label": child.name, "value": child.absolute().__str__()}
        for child in root.iterdir()
    ]
