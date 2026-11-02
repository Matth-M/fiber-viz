import glob
import os
from pathlib import Path

import dash
import numpy as np
import pandas as pd
from dash import Dash, Input, Output, callback, dcc, html, page_container
from plotly import graph_objects as go
from scipy.ndimage import gaussian_filter1d

dash.register_page(__name__, path="/boxplots")

layout = html.Div(
    [
        html.Div(
            [
                dcc.Dropdown(
                    ["005-008", "008-012", "012-25sec"],
                    placeholder="Select events",
                    id="dropdown_events",
                ),
                dcc.Dropdown(
                    ["1", "2", "3", "4", "5", "6"],
                    placeholder="select a phase",
                    id="dropdown_phases",
                    style={"backgroundColor": "transparent"},
                ),
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
    Output("boxplot_graph", "srcDoc"),
    Input("dropdown_phases", "value"),
    Input("dropdown_events", "value"),
)
def update_boxplot(phase, event):
    folder = Path(
        r"C:\Users\cboulest\Desktop\claire\Claire\portfolio\boxplots_regression"
    )
    if event is None or phase is None:
        return ""
    event = event.replace("-", "_")
    file = folder / f"events_{event}_phase{phase}.html"
    if event == "012-25sec":
        file = folder / f"events_after_012_phase{phase}.html"

    if not file.exists():
        return "<p>No boxplot available.</p>"
    return file.read_text(encoding="utf-8")
