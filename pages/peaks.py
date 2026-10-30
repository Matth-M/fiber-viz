from pathlib import Path

import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import scipy.signal as s
from dash import Input, Output, callback, dcc, html
from scipy.ndimage import gaussian_filter1d

dash.register_page(__name__, path="/peaks")


layout = html.Div(
    [
        html.Div(
            [
                html.H3("Effects of smoothing on peak detection"),
                dcc.Markdown("""Folder and file selection"""),
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
                            id="dropdown_folders2",
                        ),
                        dcc.Dropdown(
                            placeholder="select a mouse file", id="dropdown_files2"
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
    Output("dropdown_files2", "options"),
    Input("dropdown_folders2", "value"),
)
def correct_files(folder_selection):
    if folder_selection is None:
        return []
    if folder_selection == "Souris 83 (HT)":
        folder = Path(
            r"C:\Users\cboulest\Desktop\claire\Claire\detection_transient\autres_manip\Manip_souris83"
        )
        files = list(folder.glob(r"**\Fluorescence.csv"))
        return [
            {"label": str(file).split("\\")[-3], "value": str(file)} for file in files
        ]
    if folder_selection == "Souris 86 (HT)":
        folder = Path(
            r"C:\Users\cboulest\Desktop\claire\Claire\detection_transient\autres_manip\Manip_souris86"
        )
        files = list(folder.glob(r"**\Fluorescence.csv"))
        return [
            {"label": str(file).split("\\")[-3], "value": str(file)} for file in files
        ]
    if folder_selection == "Souris 87 (WT)":
        folder = Path(
            r"C:\Users\cboulest\Desktop\claire\Claire\detection_transient\autres_manip\Manip_souris87"
        )
        files = list(folder.glob("**.csv"))
        return [
            {"label": str(file).split("\\")[-1], "value": str(file)} for file in files
        ]
    if folder_selection == "Souris 88 (WT)":
        folder = Path(
            r"C:\Users\cboulest\Desktop\claire\Claire\detection_transient\autres_manip\Manip_souris88"
        )
        files = list(folder.glob(r"**\Fluorescence.csv"))
        return [
            {"label": str(file).split("\\")[-3], "value": str(file)} for file in files
        ]


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
    Input("dropdown_files2", "value"),
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


# T,_ =s.find_peaks(smoothed, prominence=2.3, rel_height=0.5) #apparently bc two variables and we dont care about _
# peaks_X=X.iloc[T]
# peaks_Y= smoothed[T]

# @callback(
#     Output("signal_graph", 'figure'),


# def upd


# def make_peak_graph(x,signal,peak_indexes,title):

#     x = np.asarray(x)
#     signal = np.asarray(signal)

#     peak_indexes = np.asarray(peak_indexes,dtype=int)

#     fig = go.Figure()
#     # signal
#     fig.add_trace(
#         go.Scatter(
#             x=x,
#             y=signal,
#             mode="lines",
#             name="Smoothed DF/F",
#             line=dict(
#                 color="black",
#                 width=1
#             )
#         )
#     )


#     # detected peaks
#     if len(peak_indexes) > 0:

#         fig.add_trace(
#             go.Scatter(
#                 x=x[peak_indexes],
#                 y=signal[peak_indexes],
#                 mode="markers",
#                 name=f"Peaks: {len(peak_indexes)}",
#                 marker=dict(
#                     color="red",
#                     size=8
#                 )
#             )
#         )


#     # zero line
#     fig.add_hline(
#         y=0,
#         line_dash="dash",
#         line_color="gray"
#     )


#     fig.update_layout(

#         title=(
#             f"{title} — "
#             f"{len(peak_indexes)} peaks detected"
#         ),

#         xaxis_title="Time (s)",

#         yaxis_title="DF/F",

#         height=450,

#         margin=dict(
#             l=60,
#             r=30,
#             t=60,
#             b=50
#         )
#     )


#     return fig


# # LAYOUT


# layout = html.Div([

#     html.H2(
#         "Peak Detection Algorithm Comparison"
#     ),


#     html.H4(
#         "Select recording"
#     ),

#     dcc.Dropdown(
#         id="peak_file_dropdown",

#         options=[
#             # EXAMPLE:
#             #
#             # {
#             #     "label": "Mouse 83 file 1",
#             #     "value": r"C:\path\to\file.csv"
#             # },
#             #
#             # {
#             #     "label": "Mouse 86 file 4",
#             #     "value": r"C:\path\to\file.csv"
#             # },

#         ],

#         placeholder="Select a file",

#         clearable=True
#     ),


#     html.Br(),


#     # ========================================================
#     # GLOBAL SMOOTHING
#     # ========================================================

#     html.H3(
#         "Smoothing"
#     ),

#     html.Label(
#         "Gaussian sigma"
#     ),

#     dcc.Slider(

#         id="sigma_slider",

#         min=0,
#         max=15,
#         step=0.5,

#         value=5,

#         marks={
#             0: "0",
#             2.5: "2.5",
#             5: "5",
#             7.5: "7.5",
#             10: "10",
#             12.5: "12.5",
#             15: "15"
#         },

#         tooltip={
#             "placement": "bottom",
#             "always_visible": True
#         }
#     ),


#     html.Hr(),

#     # FABRICE


#     html.H3(
#         "Fabrice algorithm"
#     ),

#     html.P(
#         "Peak detection using the parameters "
#         "defined internally in FluoProcess."
#     ),

#     dcc.Graph(
#         id="fabrice_graph"
#     ),


#     html.Hr(),


#     # SCIPY FIND_PEAKS


#     html.H3(
#         "Scipy find_peaks"
#     ),


#     html.Label(
#         "Prominence"
#     ),

#     dcc.Slider(

#         id="find_prominence",

#         min=0,
#         max=10,
#         step=0.1,

#         value=2.3,

#         marks={
#             0: "0",
#             2: "2",
#             4: "4",
#             6: "6",
#             8: "8",
#             10: "10"
#         },

#         tooltip={
#             "placement": "bottom",
#             "always_visible": True
#         }
#     ),


#     html.Br(),


#     html.Label(
#         "Minimum distance between peaks"
#     ),

#     dcc.Slider(

#         id="find_distance",

#         min=1,
#         max=200,
#         step=1,

#         value=1,

#         marks={
#             1: "1",
#             25: "25",
#             50: "50",
#             100: "100",
#             150: "150",
#             200: "200"
#         },

#         tooltip={
#             "placement": "bottom",
#             "always_visible": True
#         }
#     ),


#     dcc.Graph(
#         id="find_graph"
#     ),


#     html.Hr(),


#     # ARGRELEXTREMA


#     html.H3("Argrelextrema"),
#     html.Label( "Percentile threshold"),

#     dcc.Slider(id="arg_percentile",min=50,max=99,step=1,value=88,
#         marks={
#             50: "50",
#             60: "60",
#             70: "70",
#             80: "80",
#             88: "88",
#             90: "90",
#             99: "99"
#         },

#         tooltip={
#             "placement": "bottom",
#             "always_visible": True
#         }
#     ),


#     html.Br(),


#     html.Label(
#         "Derivative multiplier"
#     ),

#     dcc.Slider(

#         id="arg_multiplier",

#         min=0.5,
#         max=3,
#         step=0.05,

#         value=1.55,

#         marks={
#             0.5: "0.5",
#             1: "1",
#             1.5: "1.5",
#             2: "2",
#             2.5: "2.5",
#             3: "3"
#         },

#         tooltip={
#             "placement": "bottom",
#             "always_visible": True
#         }
#     ),


#     html.Br(),


#     html.Label(
#         "Extrema order"
#     ),

#     dcc.Slider(

#         id="arg_order",

#         min=1,
#         max=50,
#         step=1,

#         value=1,

#         marks={
#             1: "1",
#             5: "5",
#             10: "10",
#             20: "20",
#             30: "30",
#             40: "40",
#             50: "50"
#         },

#         tooltip={
#             "placement": "bottom",
#             "always_visible": True
#         }
#     ),


#     dcc.Graph(
#         id="arg_graph"
#     )


# ], style={
#     "padding": "20px"
# })


# # ============================================================
# # CALLBACK
# # ============================================================

# @callback(

#     Output(
#         "fabrice_graph",
#         "figure"
#     ),

#     Output(
#         "find_graph",
#         "figure"
#     ),

#     Output(
#         "arg_graph",
#         "figure"
#     ),


#     Input(
#         "peak_file_dropdown",
#         "value"
#     ),

#     Input(
#         "sigma_slider",
#         "value"
#     ),

#     Input(
#         "find_prominence",
#         "value"
#     ),

#     Input(
#         "find_distance",
#         "value"
#     ),

#     Input(
#         "arg_percentile",
#         "value"
#     ),

#     Input(
#         "arg_multiplier",
#         "value"
#     ),

#     Input(
#         "arg_order",
#         "value"
#     )
# )
# def update_peak_comparison(
#     selected_file,
#     sigma,
#     prominence,
#     distance,
#     percentile,
#     multiplier,
#     order
# ):


#     # ========================================================
#     # NOTHING SELECTED
#     # ========================================================

#     if selected_file is None:

#         empty1 = go.Figure()
#         empty2 = go.Figure()
#         empty3 = go.Figure()

#         return (
#             empty1,
#             empty2,
#             empty3
#         )


#     # ========================================================
#     # READ CSV
#     # ========================================================

#     df = pd.read_csv(
#         selected_file,
#         skiprows=2
#     )


#     # Rename columns
#     df = df.rename(
#         columns={
#             "0": "Time in s",
#             "43.41": "CH1-410",
#             "59.61": "CH1-470",
#             "Unnamed: 1": "Events"
#         }
#     )


#     # Remove unnamed columns
#     df = df.loc[
#         :,
#         ~df.columns.str.contains(
#             "^Unnamed"
#         )
#     ]


#     # ========================================================
#     # TIME
#     # ========================================================

#     x = (
#         df["Time in s"]
#         / 1000
#     )


#     # ========================================================
#     # GET DF/F
#     # ========================================================

#     fabrice_process = (
#         FluoProcess
#         .FluoProcess
#         .from_dataframe(
#             df.copy()
#         )
#     )


#     deltaf_f = np.asarray(
#         fabrice_process.data["DF"]
#     )


#     # ========================================================
#     # GLOBAL SMOOTHING
#     # ========================================================

#     smoothed = smooth_signal(
#         deltaf_f,
#         sigma
#     )


#     # ========================================================
#     # FABRICE ALGORITHM
#     # ========================================================

#     fabrice_peaks = fabrice_algorithm(
#         df
#     )


#     fig_fabrice = make_peak_graph(
#         x,
#         smoothed,
#         fabrice_peaks,
#         "Fabrice algorithm"
#     )


#     # ========================================================
#     # FIND_PEAKS
#     # ========================================================

#     find_peaks = find_peaks_algorithm(

#         smoothed,

#         prominence=prominence,

#         distance=distance
#     )


#     fig_find = make_peak_graph(
#         x,
#         smoothed,
#         find_peaks,
#         "Scipy find_peaks"
#     )


#     # ========================================================
#     # ARGRELEXTREMA
#     # ========================================================

#     arg_peaks = argrelextrema_algorithm(

#         x,

#         smoothed,

#         percentile=percentile,

#         derivative_multiplier=multiplier,

#         order=order
#     )


#     fig_arg = make_peak_graph(
#         x,
#         smoothed,
#         arg_peaks,
#         "Argrelextrema"
#     )


#     # ========================================================
#     # RETURN ALL THREE VERTICAL GRAPHS
#     # ========================================================

#     return (
#         fig_fabrice,
#         fig_find,
#         fig_arg
#     )

