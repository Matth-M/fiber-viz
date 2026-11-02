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

boxplots_root_folder = DATA_ROOT.joinpath("boxplots_regression")

dash.register_page(__name__, path="/boxplots")

logger = logging.getLogger(__name__)

layout = html.Div(
    [
        html.Div(
            [
                dcc.Input(
                    id="root_folder",
                    value=str(boxplots_root_folder),
                ),
                dcc.Dropdown(
                    id="file_selection",
                    placeholder="Select file",
                ),
                # dcc.Dropdown(
                #     ["005-008", "008-012", "012-25sec"],
                #     placeholder="Select events",
                #     id="dropdown_events",
                # ),
                # dcc.Dropdown(
                #     ["1", "2", "3", "4", "5", "6"],
                #     placeholder="select a phase",
                #     id="dropdown_phases",
                #     style={"backgroundColor": "transparent"},
                # ),
            ],
            style={"backgroundColor": "transparent"},
        ),
        html.Div(
            [
                html.Iframe(
                    id="boxplot_graph",
                    style={
                        "width": "115%",
                        "height": "468px",
                        "border": "none",
                        "backgroundColor": "transparent",
                    },
                ),
                html.Div(
                    [
                        dcc.Markdown("""
            ###### Events: 
            **005**: start of the experiment, the mouse is in the corridor and door A closed behind it. 
            Fiber photometry begins, and csv starts at this timestamp.  
            **008**: door B opens (the corridor is open), but the mouse is still in it.  
            **012**: The mouse left the corridor, and is in side B. \n
            Once the graph is displayed, each dot represents the amplitude of one csv. the dots are displayed in chronological order from left to right.
    
            """)
                    ]
                ),
            ]
        ),
    ],
    style={"padding": "20px"},
)


@callback(
    Output("file_selection", "options"),
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


@callback(
    Output("boxplot_graph", "srcDoc"),
    Input("file_selection", "value"),
)
def update_boxplot(file_selection):
    if file_selection is None:
        return ""

    file = Path(file_selection)
    if not file.exists():
        return ""

    return file.read_text(encoding="utf-8")
