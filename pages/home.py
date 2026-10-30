import dash
from dash import html, dcc

dash.register_page(__name__, path="/")

layout2 = html.Div([
    html.H1("My Internship Portfolio"),
    html.P("Welcome to my scientific results portfolio.")
], style={'padding': '20px'})

textlayout = html.Div([

    dcc.Markdown("""
#### About this portfolio

This web portal presents the work carried out during my internship and provides an interactive overview of the main methods, analyses, and results obtained throughout the project.

The portfolio includes data visualizations and analyses developed to explore **fiber photometry recordings**, with a particular focus on fluorescence signal variations across different experimental conditions and behavioral events.

#### Explore the project

Use the navigation menu to explore the different parts of the project, including:

- Experimental data and recordings
- Signal processing and ΔF/F analysis
- Detection and analysis of fluorescence transients
- Comparison of social and sugar conditions
- Interactive boxplots and other visualizations

#### About

**Author:** Claire Boulesteix \n 
**Collaborators:** \n
Fabrice de Chaumont, **PhD**  
Manon Moreau, **PhD**  
Benoît Forget, **PhD**   
Thomas Bourgeron, **PhD**   
Xavier Mousset, **PhD**  
Matthieu Matsima
""")

], style={'padding': '20px'})


layout = html.Div([
    layout2,
    textlayout
])