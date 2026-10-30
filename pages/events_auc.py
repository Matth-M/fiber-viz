import dash
from dash import Dash, html, dcc, page_container, callback, Input,Output
from plotly import graph_objects as go
from pathlib import Path
import glob
import os
import pandas as pd
import numpy as np
from scipy.ndimage import gaussian_filter1d
import glob
import os
from pathlib import Path



dash.register_page(__name__, path="/events_auc")


layout=html.Div([
    html.Div([ 

        dcc.Dropdown(options=[{"label": "Souris 83 (HT)", "value": 83},{"label": "Souris 86 (HT)", "value": 86},{"label": "Souris 87 (WT)", "value": 87},{"label": "Souris 88 (WT)", "value": 88},],placeholder="Select a mouse folder", id='dropdown_folders5'),
        dcc.Dropdown(placeholder='select a mouse file', id='dropdown_files5'),
        dcc.Dropdown(options=[{'label':'door -> out', 'value':'008_012'},{'label': 'out -> +25sec', 'value':"012_25"}],placeholder='select an event')
    ],style={'color':'black'}),

    html.Div([
        html.Iframe(id='signal_graph5',
        style={
            "width": "100%",
            "height": "800px",
            "border": "none"})
        
        # dcc.Checklist(options=['CH1-410','CH1-470','CH1-410 isofit','deltaf/f'], id='signal_checklist' ),

    ])

], style={"padding":"20px"})



@callback(
    Output("dropdown_files5", "options"),
    Input("dropdown_folders5", "value")
)

def correct_files(folder_selection):
    if folder_selection is None:
        return []
    if folder_selection:
        folder= Path(r'C:\Users\cboulest\Desktop\claire\Claire\portfolio\graphs')
        files = list(folder.glob(rf"mouse_{folder_selection}*"))
        print(files)
        return [{"label": str(file).split('_')[-2],"value": str(file)}for file in files]   #file.name

@callback(
    Output('signal_graph5', 'srcDoc'),
    Input('dropdown_files5', 'value'))

def update_graph(file):

    if file is None:
        return ""
    file = Path(file)
    if not file.exists():
        return "<p>No graph available.</p>"
    return file.read_text(encoding="utf-8")



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

