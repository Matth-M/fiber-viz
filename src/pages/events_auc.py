import logging
from pathlib import Path

import dash
from dash import Input, Output, callback, dcc, html
from plotly import graph_objects as go

from src.lib.fiber_data_format import FiberAcquisitionMode, parse_recording
from src.lib.FiberLogReader import FiberLogReader
from src.lib.processing import area_under_curve
from src.lib.recordings import (
    find_log_from_mouse_folder,
    get_fullname_component_from_fullpath,
    get_recordings_mouse_folder,
    parse_name_number_from_full,
)
from src.utils import DATA_ROOT

dash.register_page(__name__, path="/events_auc")

logger = logging.getLogger(__name__)

experiments_root_folder = DATA_ROOT.joinpath("autres_manip")

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
    ],
    style={"padding": "20px"},
)


@callback(
    Output("mouse_folder", "options"),
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
    Input("recording_path", "value"),
    Input("mouse_folder", "value"),
    Input("mode_selection", "value"),
)
def update_boxplot(recording, mouse_folder, mode):
    if not recording or not mouse_folder:
        return go.Figure()

    # Get log from glob mouse folder
    mouse_folder = Path(mouse_folder)
    log = find_log_from_mouse_folder(mouse_folder)
    log_reader = FiberLogReader(log)

    mode = FiberAcquisitionMode(mode)

    # Get recording as DataFrame
    recording_path = Path(recording)
    fullname = get_fullname_component_from_fullpath(recording_path, mode)
    name_number = parse_name_number_from_full(fullname)
    if name_number:
        _, recording_number = name_number
    else:
        return go.Figure()
    recording_path = Path(recording_path)
    mode = FiberAcquisitionMode(mode)
    df = parse_recording(recording_path, mode)
    df, auc_between, auc_after = area_under_curve(df, log_reader, recording_number)

    # Plot Data
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=df["delta_f"]))

    return fig


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
