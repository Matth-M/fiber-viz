import glob
import os
from pathlib import Path

import dash
import numpy as np
import pandas as pd
from dash import Dash, Input, Output, callback, dcc, html, page_container
from plotly import graph_objects as go
from scipy.ndimage import gaussian_filter1d

dash.register_page(__name__, path="/basic_signals")

# ----------files


layout = html.Div(
    [
        html.Div(
            [
                dcc.Dropdown(
                    [
                        "Souris 83 (HT)",
                        "Souris 86 (HT)",
                        "Souris 87 (WT)",
                        "Souris 88 (WT)",
                    ],
                    placeholder="Select a mouse folder",
                    id="dropdown_folders",
                ),
                dcc.Dropdown(placeholder="select a mouse file", id="dropdown_files"),
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


@callback(Output("dropdown_files", "options"), Input("dropdown_folders", "value"))
def correct_files(folder_selection):
    if folder_selection is None:
        return []
    if folder_selection == "Souris 83 (HT)":
        folder = Path(
            r"C:\Users\cboulest\Desktop\claire\Claire\portfolio\autres_manip\Manip_souris83"
        )
        files = list(folder.glob(r"**\Fluorescence.csv"))
        return [
            {"label": str(file).split("\\")[-3], "value": str(file)} for file in files
        ]
    if folder_selection == "Souris 86 (HT)":
        folder = Path(
            r"C:\Users\cboulest\Desktop\claire\Claire\portfolio\autres_manip\Manip_souris86"
        )
        files = list(folder.glob(r"**\Fluorescence.csv"))
        return [
            {"label": str(file).split("\\")[-3], "value": str(file)} for file in files
        ]
    if folder_selection == "Souris 87 (WT)":
        folder = Path(
            r"C:\Users\cboulest\Desktop\claire\Claire\portfolio\autres_manip\Manip_souris87"
        )
        files = list(folder.glob("**.csv"))
        return [
            {"label": str(file).split("\\")[-1], "value": str(file)} for file in files
        ]
    if folder_selection == "Souris 88 (WT)":
        folder = Path(
            r"C:\Users\cboulest\Desktop\claire\Claire\portfolio\autres_manip\Manip_souris88"
        )
        files = list(folder.glob(r"**\Fluorescence.csv"))
        return [
            {"label": str(file).split("\\")[-2], "value": str(file)} for file in files
        ]


@callback(
    Output("signal_graph", "figure"),
    Input("dropdown_files", "value"),
    # Input('signal_checklist', "value")
)
def display_graph_from_csv(csv):
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


# @callback(
#     Output("signal_graph", 'figure'),


# def updategraph(checklist_option):

#     if checklist_option== 'CH1-410':
