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

dash.register_page(__name__, path="/events_auc")

logger = logging.getLogger(__name__)

graphs_root_folder = DATA_ROOT.joinpath("graphs")

layout = html.Div(
    [
        html.Div(
            [
                html.P("Experiment root folder:"),
                dcc.Input(
                    id="root_folder",
                    value=str(graphs_root_folder),
                ),
                dcc.Dropdown(
                    id="graph_file_selection",
                    placeholder="Select a graph file",
                ),
                dcc.Dropdown(
                    options=[
                        {"label": "door -> out", "value": "008_012"},
                        {"label": "out -> +25sec", "value": "012_25"},
                    ],
                    placeholder="select an event",
                ),
            ],
            style={"color": "black"},
        ),
        html.Div(
            [
                html.Iframe(
                    id="graph",
                    style={"width": "100%", "height": "800px", "border": "none"},
                )
                # dcc.Checklist(options=['CH1-410','CH1-470','CH1-410 isofit','deltaf/f'], id='signal_checklist' ),
            ]
        ),
    ],
    style={"padding": "20px"},
)


@callback(
    Output("graph", "srcDoc"),
    Input("graph_file_selection", "value"),
)
def update_boxplot(file_selection):
    if file_selection is None:
        return ""

    file = Path(file_selection)
    if not file.exists():
        return ""

    return file.read_text(encoding="utf-8")


@callback(
    Output("graph_file_selection", "options"),
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


# @callback(
#     Output('signal_graph', 'figure'),
#     Input('dropdown_files','value'),
#     # Input('signal_checklist', "value")

# )

# def display_graph_from_csv(csv):
#     if csv is None:
#         return go.Figure()

#     df = pd.read_csv(csv, skiprows=1)
#     df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
#     del df['Events']

#     X=df.iloc[:,0]
#     Y1=df.iloc[:,1]
#     Y2=df.iloc[:,2]
#     coeff_du_fit=np.polyfit(Y1,Y2,1)
#     isofit = np.polyval(coeff_du_fit, Y1) #pour isofit y1
#     deltaf_f= ((Y2 - isofit)/isofit)*100

#     fig=go.Figure()

#     # if checklist_option == []:
#     #     return fig
#     # if 'CH1-410' in checklist_option:
#     fig.add_trace(go.Scatter(x=X, y=Y1, name="CH1-410", line_color='red'))

#     # if 'CH1-470' in checklist_option:
#     fig.add_trace(go.Scatter(x=X, y=Y2, name='CH1-470', line_color='black'))
#     # if 'CH1-410 isofit' in checklist_option:
#     fig.add_trace(go.Scatter(x=X, y=isofit, name='CH1-410 isofit', line_color='blue'))
#     # if 'deltaf/f' in checklist_option:
#     fig.add_trace(go.Scatter(x=X, y=deltaf_f, name='deltaf/f', line_color='springgreen'))
#     fig.add_annotation(text='Click on the legend to display or remove signals', showarrow=False, xref='paper', yref='paper',x=1, y=1)
#     fig.update_layout(title='Fluorescent signals', xaxis_title='time (ms)', yaxis_title='percentage')
#     return fig
