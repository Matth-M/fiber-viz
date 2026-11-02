from pathlib import Path

import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import scipy.signal as s
from dash import Input, Output, callback, dcc, html
from scipy.ndimage import gaussian_filter1d

dash.register_page(__name__, path="/peaks")

from src.utils import ROOT_EXPERIMENT_FOLDER_DEFAULT

layout = html.Div(
    [
        html.Div(
            [
                html.H3("Effects of smoothing on peak detection"),
                html.Div(
                    [
                        html.P("Experiment root folder:"),
                        dcc.Input(
                            id="root_folder",
                            value=str(ROOT_EXPERIMENT_FOLDER_DEFAULT.absolute()),
                        ),
                        dcc.Dropdown(
                            id="dropdown_folders",
                            placeholder="Select a mouse folder",
                        ),
                        dcc.Dropdown(
                            id="dropdown_files",
                            placeholder="select a mouse file",
                        ),
                    ],
                    style={"color": "black"},
                ),
            ]
        ),
        html.Div(
            [
                dcc.Graph(id="smoothing_graph"),
                dcc.Slider(0, 30, 1, value=5, id="smoothing_slider"),
            ],
        ),
        html.Div(
            [
                dcc.Markdown("""Distance"""),
                dcc.Markdown("""Prominence"""),
                dcc.Markdown("""Width"""),
            ],
            style={"display": "flex", "flexDirection": "row", "gap": " 185px"},
        ),
        html.Div(
            [
                dcc.Input(
                    type="number",
                    id="distance",
                    value=10,
                    placeholder="distance",
                    min=10,
                    step=1,
                ),
                dcc.Input(
                    type="number",
                    id="prominence",
                    value=0,
                    placeholder="prominence",
                    min=0,
                    step=0.1,
                ),
                dcc.Input(
                    type="number",
                    id="width",
                    value=1,
                    placeholder="peak width",
                    min=0,
                    step=0.1,
                ),
            ],
            style={"display": "flex", "flexDirection": "row", "gap": "10px"},
        ),
        html.Div(
            [
                dcc.Markdown("""*Please input values manually*  
        Parameters:  
        1)**distance** between peaks (try starting at 50)  
        2)**prominence** (how much a peak stands out)  
        3)**width of peaks** (how wide a peak should be)""")
            ]
        ),
        html.Div(
            [
                # peakutils
                dcc.Graph(id="smoothing_graph2"),
                dcc.Slider(0, 30, 1, value=5, id="smoothing_slider2"),
                html.Div(
                    [
                        dcc.Input(
                            type="number",
                            id="threshold",
                            placeholder="threshold",
                            step=0.01,
                        ),
                        dcc.Input(
                            type="number",
                            id="min_dist",
                            placeholder="min distance",
                            min=0,
                        ),
                    ],
                    style={"display": "flex", "flexDirection": "row", "gap": "10px"},
                ),
            ]
        ),
        html.Div(
            [
                dcc.Graph(id="smoothing_graph3"),
                dcc.Slider(0, 30, 1, value=5, id="smoothing_slider3"),
            ]
        ),
    ],
    style={"padding": "20px"},
)

# __________________callbacks / methods________________________


@callback(
    Output("dropdown_folders", "options"),
    Input("root_folder", "value"),
)
def experiment_folders(folder_selection):
    root_folder = Path(folder_selection)
    if not root_folder.exists():
        return []
    # Return all mouse folders in root folder
    return [
        {"label": child.name, "value": str(child.absolute())}
        for child in root_folder.iterdir()
        if child.is_dir()
    ]


@callback(
    Output("dropdown_files", "options"),
    Input("dropdown_folders", "value"),
)
def experiment_files(folder_selection):
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

def make_smoothing_graph(
    X,
    deltaf_f,
    sigma,
    find_peaks=False,
    rel_height=None,
    distance=None,
    prominence=None,
    width=None,
    peakutils=False,
    thres=None,
    min_dist=None,
):

    smoothed = gaussian_filter1d(deltaf_f, sigma=sigma)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=X,
            y=deltaf_f,
            name="deltaf/f",
            line_color="lightgreen",
            mode="lines",
            line=dict(width=3),
        )
    )
    fig.add_trace(
        go.Scatter(x=X, y=smoothed, name="smoothed deltaf/f", line_color="black")
    )

    # Only add peaks when requested
    if find_peaks:
        T, _ = s.find_peaks(
            smoothed, distance=distance, prominence=prominence, width=width
        )
        peaks_X = X.iloc[T]
        peaks_Y = smoothed[T]
        numberofpeaks = len(T)
        fig.add_trace(
            go.Scatter(
                x=peaks_X,
                y=peaks_Y,
                mode="markers",
                name=f"Peaks : {numberofpeaks}",
                marker=dict(size=4, color="red"),
            )
        )
        fig.update_layout(
            title=f"Find_peaks algorithm",
            xaxis_title="time (ms)",
            yaxis_title="percentage",
        )

    if peakutils:
        import peakutils

        T = peakutils.indexes(smoothed, thres=0.3, min_dist=20, thres_abs=False)
        peaks_X = X.iloc[T]
        peaks_Y = smoothed[T]
        numberofpeaks = len(T)
        fig.add_trace(
            go.Scatter(
                x=peaks_X,
                y=peaks_Y,
                mode="markers",
                name=f"Peaks : {numberofpeaks}",
                marker=dict(size=4, color="red"),
            )
        )
        fig.update_layout(
            title=f"PeakUtils algorithm",
            xaxis_title="time (ms)",
            yaxis_title="percentage",
        )
    return fig


@callback(
    Output("smoothing_graph", "figure"),
    Output("smoothing_graph2", "figure"),
    Output("smoothing_graph3", "figure"),
    Input("dropdown_files", "value"),
    Input("smoothing_slider", "value"),  # value1
    Input("smoothing_slider2", "value"),  # value2
    Input("smoothing_slider3", "value"),  # value3
    Input("distance", "value"),
    Input("prominence", "value"),
    Input("width", "value"),
    Input("threshold", "value"),
    Input("min_dist", "value"),
)
def display_graph_from_csv(
    csv, value1, value2, value3, distance, prominence, width, min_dist, thres
):
    if csv is None:
        return go.Figure(), go.Figure(), go.Figure()
    df = pd.read_csv(csv, skiprows=1)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    if "Events" in df.columns:
        del df["Events"]

    X = df.iloc[:, 0]
    Y1 = df.iloc[:, 1]
    Y2 = df.iloc[:, 2]
    coeff_du_fit = np.polyfit(Y1, Y2, 1)
    isofit = np.polyval(coeff_du_fit, Y1)
    deltaf_f = ((Y2 - isofit) / isofit) * 100

    fig1 = make_smoothing_graph(
        X,
        deltaf_f,
        value1,
        find_peaks=True,
        distance=distance,
        prominence=prominence,
        width=width,
    )

    fig2 = make_smoothing_graph(
        X, deltaf_f, value2, peakutils=True, min_dist=min_dist, thres=thres
    )

    fig3 = make_smoothing_graph(X, deltaf_f, value3)

    return fig1, fig2, fig3
