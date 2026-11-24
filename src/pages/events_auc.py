import logging
from pathlib import Path

import dash
from dash import Input, Output, callback, dcc, html
from plotly import graph_objects as go

from src.lib.fiber_data_format import FiberAcquisitionMode
from src.lib.recordings import (
    get_recordings_mouse_folder,
)
from src.utils import DATA_ROOT

dash.register_page(__name__, path="/events_auc")

logger = logging.getLogger(__name__)

experiments_root_folder = DATA_ROOT.joinpath("autres_manip")

warning = html.P(
    id="warning",
    style={
        "padding": "2em",
        "color": "red",
    },
)

layout = html.Div(
    [
        html.Div(
            [
                html.P("Experiment root folder:"),
                dcc.Input(
                    id="root_folder",
                    value=str(experiments_root_folder.absolute()),
                ),
                dcc.Dropdown(id="mouse_folder", placeholder="Select a mouse folder"),
                dcc.Dropdown(
                    id="recording_path",
                    placeholder="Select a recording",
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
                dcc.Graph(id="graph"),
            ]
        ),
        warning,
    ],
    style={"padding": "20px"},
)


@callback(
    Output("mouse_folder", "options"),
    Input("root_folder", "value"),
)
def experiment_folders(root_folder):
    if not root_folder:
        return []
    root_folder = Path(root_folder)
    if not root_folder.exists():
        return []
    # Return all mouse folders in root folder
    return [
        {"label": child.name, "value": str(child.absolute())}
        for child in root_folder.iterdir()
        if child.is_dir()
    ]


@callback(
    Output("recording_path", "options"),
    Input("mouse_folder", "value"),
    Input("mode_selection", "value"),
)
def graph_file(mouse_folder, mode):
    if mouse_folder is None:
        return []

    mouse_folder = Path(mouse_folder)

    files = [
        {
            "label": f"{mouse_name}_{recording_number}",
            "value": str(recording_path.absolute()),
        }
        for recording_number, mouse_name, recording_path in get_recordings_mouse_folder(
            mouse_folder, FiberAcquisitionMode(mode)
        )
    ]
    return files


@callback(
    Output("graph", "figure"),
    Output("warning", "children"),
    Input("recording_path", "value"),
    Input("mouse_folder", "value"),
    Input("mode_selection", "value"),
)
def update_boxplot(recording, mouse_folder, mode):
    if not recording or not mouse_folder:
        return go.Figure(), ""

    from src.lib.plots import auc_plot

    # Plot Data
    fig, error_msg = auc_plot(recording, mouse_folder, mode)

    if not fig:
        logger.debug(f"{recording}, {mode}: {error_msg}")
        return go.Figure(), f"Error: {error_msg}"

    return fig, ""


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
