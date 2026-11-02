import glob
import logging
import os
from pathlib import Path

import dash
import numpy as np
import pandas as pd
from dash import Dash, Input, Output, callback, dcc, html, page_container
from plotly import graph_objects as go
from scipy.ndimage import gaussian_filter1d

from src.utils import DATA_ROOT

experiments_root_folder = DATA_ROOT.joinpath("autres_manip")


logger = logging.getLogger(__file__)

dash.register_page(__name__, path="/basic_signals")


layout = html.Div(
    [
        html.Div(
            [
                html.P("Experiment root folder:"),
                dcc.Input(
                    id="root_folder",
                    value=str(experiments_root_folder.absolute()),
                ),
                dcc.Dropdown(
                    id="mouse_folders",
                    placeholder="Select a mouse folder",
                ),
                dcc.Dropdown(
                    id="experiment_file",
                    placeholder="select a mouse file",
                ),
            ],
            style={"color": "black"},
        ),
        html.Div(
            [
                dcc.Graph(id="signal_graph"),
                # dcc.Checklist(options=['CH1-410','CH1-470','CH1-410 isofit','deltaf/f'], id='signal_checklist' ),
            ]
        ),
    ],
    style={"padding": "20px"},
)


@callback(
    Output("mouse_folders", "options"),
    Input("root_folder", "value"),
)
def experiment_folders(root_folder):
    root_folder = Path(root_folder)
    # Return all mouse folders in root folder
    return [
        {"label": child.name, "value": str(child.absolute())}
        for child in root_folder.iterdir()
        if child.is_dir()
    ]


@callback(
    Output("experiment_file", "options"),
    Input("mouse_folders", "value"),
)
def experiment_file(folder_selection):
    if folder_selection is None:
        return []
    mouse_folder = Path(folder_selection)
    files = [
        {
            "label": file.parent.parent.name,
            "value": str(file.absolute()),
        }
        for file in mouse_folder.glob(r"**\Fluorescence.csv")
    ]
    if len(files) == 0:  # no Fluorescence found
        files = [
            {
                "label": f"{file.name}",
                "value": f"{str(file.absolute())}",
            }
            for file in mouse_folder.glob(r"**\*.csv")
        ]

    return files


@callback(
    Output("signal_graph", "figure"),
    Input("experiment_file", "value"),
)
def display_graph_from_csv(csv):
    logger.debug(f"csv path: {csv}")

    if csv is None:
        return go.Figure()

    df = pd.read_csv(csv, skiprows=1)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    del df["Events"]

    X = df.iloc[:, 0]
    Y1 = df.iloc[:, 1]
    Y2 = df.iloc[:, 2]
    coeff_du_fit = np.polyfit(Y1, Y2, 1)
    isofit = np.polyval(coeff_du_fit, Y1)  # pour isofit y1
    deltaf_f = ((Y2 - isofit) / isofit) * 100

    fig = go.Figure()

    # TODO:
    # if checklist_option == []:
    #     return fig
    # if 'CH1-410' in checklist_option:
    fig.add_trace(go.Scatter(x=X, y=Y1, name="CH1-410", line_color="red"))

    # if 'CH1-470' in checklist_option:
    fig.add_trace(go.Scatter(x=X, y=Y2, name="CH1-470", line_color="black"))
    # if 'CH1-410 isofit' in checklist_option:
    fig.add_trace(go.Scatter(x=X, y=isofit, name="CH1-410 isofit", line_color="blue"))
    # if 'deltaf/f' in checklist_option:
    fig.add_trace(go.Scatter(x=X, y=deltaf_f, name="deltaf/f", line_color="lightgreen"))
    fig.add_annotation(
        text="Click on the legend to display or remove signals",
        showarrow=False,
        xref="paper",
        yref="paper",
        x=1,
        y=1,
    )
    fig.update_layout(
        title="Fluorescent signals", xaxis_title="time (ms)", yaxis_title="percentage"
    )
    return fig
