import base64
import io
from urllib.parse import quote as urlquote
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash_table.Format import Format, Scheme
import pandas as pd
import plotly.graph_objs as go
from textwrap import dedent as d
import plotly.express as px
import json
import textwrap
import dash_bootstrap_components as dbc

# CREATE DASH APP
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://codepen.io/chriddyp/pen/bWLwgP.css',
                                      "https://codepen.io/sutharson/pen/dyYzEGZ.css"])
server = app.server

# PREDEFINED TAB STYLES
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
tabs_styles = {'height': '40px', 'font-family': 'Arial', 'fontSize': 14}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_mini_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'width': '50px',
    'color': '#000000',
    'fontColor': '#000000',
}

tab_mini_selected_style = {
    'borderTop': '3px solid #5e5e5e',
    'borderBottom': '1px solid #d6d6d6 ',
    'backgroundColor': '#5e5e5e',
    'color': '#ffffff',
    # 'fontColor': '#004a4a',
    'fontWeight': 'bold',
    'padding': '6px',
    'width': '50px'
}

tab_selected_style = {
    'borderTop': '3px solid #004a4a',
    'borderBottom': '1px solid #d6d6d6 ',
    'backgroundColor': '#f6f6f6',
    'color': '#004a4a',
    # 'fontColor': '#004a4a',
    'fontWeight': 'bold',
    'padding': '6px'
}

# SUPERSCRIPT NOTATION
SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")

# APP ABOUT DESCRIPTION
MOF_tool_about = textwrap.wrap(' These tools aim to provide a reproducible and consistent data visualisation platform '
                               'where experimental and computational researchers can use big data and statistical '
                               'analysis to find the best materials for specific applications',
                               width=50)
twoD_threeD_about = textwrap.wrap(' The 2D Animated MOF Explorer and 3D Animated MOF Explorer provides a 2, 3, 4 and '
                                  '5-Dimensional variable environment to explore specific structures '
                                  'against a discrete data variable (animation frame) of their choice to find the best '
                                  'materials for the users applications', width=50)
MOF_data_filter = textwrap.wrap(' Using the sorting and filtering datatable, users are able to filter variables '
                                'from their dataset to '
                                'produce plots of their preference. All variables in the users dataset can be sorted, '
                                'filtered and deleted in the interactive datatable. The arguments that the datatable '
                                'can take are '
                                'specified '
                                'in the manual. After filtering there are options to choose a logarithmic or linear '
                                'axis scale, and choose a colorscale of choice from the viridis color palette.'
                                , width=50)
MOF_stat_analysis = textwrap.wrap('All structures, or top performing structures (1%, 5% or 10% of all structures) '
                                  'can be analysed in accordance to a set variable decided by the user e.g. '
                                  'Deliverable Capacity. In the violin plot, geometric properties can then be '
                                  'analysed against a discrete data variable (X axis) to determine Q1, Q3, IQR, '
                                  'mean, median, maximum and'
                                  ' minimum points for a dataset of the users choice, alongside the distribution of '
                                  'MOFs in said violin plot. In the distribution plot, the number of structures against '
                                  'a variable in the users data frame can be analysed to determine the spread of '
                                  'structures in the users data. The distribution can be further filtered by MOF '
                                  'families (if the user has uploaded this information in its data frame). '
                                  'An animation feature is also available to view these frames in accordance'
                                  ' to a discrete data variable of the users choice.', width=50, )
MOF_GH = textwrap.wrap(" to explore AAML's sample data and read more on"
                       " AAML's MOF Explorer Tool Manual, FAQ's & Troubleshooting"
                       " on GitHub... ", width=50)

# APP LAYOUT
app.layout = html.Div([
    html.Div([
        html.Img(
            src='https://raw.githubusercontent.com/aaml-analytics/mof-explorer/master/UOC.png',
            height='30', width='140', style={'display': 'inline-block', 'padding-left': '1%'}),
        html.Img(src='https://raw.githubusercontent.com/aaml-analytics/mof-explorer/master/A2ML-logo.png',
                 height='60', width='160', style={'float': 'right', 'display': 'inline-block', 'padding-right': '2%'}),
        html.H1("Metal-Organic Framework Data Visualisation Tools",
                style={'display': 'inline-block', 'padding-left': '10%', 'text-align': 'center', 'fontSize': 36,
                       'color': 'white', 'font-family': 'Georgia'}),
        html.H1("...", style={'fontColor': '#3c3c3c', 'fontSize': 6})
    ], style={'backgroundColor': '#004040'}),
    html.Div([html.A('Refresh', href='/')], style={}),
    html.Div([
        html.H2("Upload Data", style={'fontSize': 24, 'font-family': 'Arial', 'color': '#004a4a'}, ),
        html.H3("Upload .txt, .csv or .xls files to starting exploring data...", style={'fontSize': 16,
                                                                                        'font-family': 'Arial'}),
        dcc.Store(id='csv-data', storage_type='session', data=None),
        html.Div([dcc.Upload(
            id='data-table-upload',
            children=html.Div([html.Button('Upload File')],
                              style={'width': '49%', 'height': "60px", 'borderWidth': '1px',
                                     'borderRadius': '5px',
                                     'textAlign': 'center',

                                     }),
            multiple=False
        ),
            html.Div(id='output-data-upload'),
            dbc.Modal(
                [
                    dbc.ModalHeader(
                        "Upload Error!"),
                    dbc.ModalBody(
                        "Please upload a .txt, .csv or .xls file."),
                    dbc.ModalFooter(
                        dbc.Button("Close",
                                   id="close-upload",
                                   className="ml-auto")
                    ),
                ],
                id="modal-upload",
                is_open=False,
                centered=True,
                size="xl"
            )
        ]), ], style={'display': 'inline-block', 'width': '48%', 'padding-left': '1%', }),
    html.Div([html.Div([html.H2("Explore Data", style={'fontSize': 24,
                                                       'font-family': 'Arial',
                                                       'color': '#004a4a'})],
                       style={}),
              html.Div(['', html.A('Download',
                                   href='https://github.com/aaml-analytics/mof-explorer/tree/master/sample-data')]),
              html.H3("...AAML's sample file to explore tool functions...", style={'fontSize': 16,
                                                                                   'font-family': 'Arial',
                                                                                   'display': 'inline-block'}),
              html.U(id='file-list')], style={'display': 'inline-block', 'width': '44%', 'font-family': 'Arial'}),
    html.Div([
        dcc.Tabs([
            dcc.Tab(label='About', style=tab_style, selected_style=tab_selected_style,
                    children=[html.Div([html.H2(" What are AAML's MOF Data Visualisation tools?",
                                                style={'fontSize': 18, 'font-family': 'Arial', 'font-weight': 'bold'
                                                       }),
                                        html.Div([' '.join(MOF_tool_about)]
                                                 , style={'font-family': 'Arial'}),
                                        html.H2([" 2D and 3D Animation Environment"],
                                                style={'fontSize': 18,
                                                       'font-family': 'Arial', 'font-weight': 'bold'}),
                                        html.Div([' '.join(twoD_threeD_about)], style={'font-family': 'Arial'}),
                                        html.H2([" MOF Data Filtering Environment"], style={'fontSize': 18,
                                                                                            'font-weight': 'bold',
                                                                                            'font-family': 'Arial'}),
                                        html.Div([' '.join(MOF_data_filter)], style={'font-family': 'Arial', }),
                                        html.H2([" MOF Statistical Analysis Environment"],
                                                style={'fontSize': 18, 'font-weight': 'bold',
                                                       'font-family': 'Arial'}),
                                        html.Div([' '.join(MOF_stat_analysis)], style={'font-family': 'Arial'}),
                                        # ADD LINK
                                        html.Div([html.Plaintext(
                                            [' Click ', html.A('here ',
                                                               href='https://github.com/aaml-analytics/mof-explorer')],
                                            style={'display': 'inline-block',
                                                   'fontSize': 14, 'font-family': 'Arial'}),
                                            html.Div([' '.join(MOF_GH)], style={'display': 'inline-block',
                                                                                'fontSize': 14,
                                                                                'font-family': 'Arial'}),
                                            html.Img(
                                                src='https://raw.githubusercontent.com/aaml-analytics/mof'
                                                    '-explorer/master/github.png',
                                                height='40', width='40',
                                                style={'display': 'inline-block', 'float': "right"
                                                       })
                                        ]
                                            , style={'display': 'inline-block'})
                                        ], style={'backgroundColor': '#ffffff'}
                                       )]),
            dcc.Tab(label='MOF Explorer Animation', style=tab_style, selected_style=tab_selected_style,
                    children=[
                        dcc.Tabs(id='sub-tabs1', style=tabs_styles, children=[
                            dcc.Tab(label='2D Animation', style=tab_style, selected_style=tab_selected_style,
                                    children=[dcc.Tabs(id='subsub-tabs', style=tabs_styles,
                                                       children=[dcc.Tab(label='2', style=tab_mini_style,
                                                                         selected_style=tab_mini_selected_style,
                                                                         children=[
                                                                             html.Div([html.Div([dcc.Graph(
                                                                                 id='my-2D-graph', animate=False)],
                                                                                 style={
                                                                                     'display': 'inline-block',
                                                                                     'width': '56%',
                                                                                 }),
                                                                                 html.Div([
                                                                                     html.Div([html.Label(
                                                                                         ["Select X variable:",
                                                                                          dcc.Dropdown(
                                                                                              id='xaxis-anim-2D',
                                                                                              multi=False,
                                                                                              placeholder="Select an option "
                                                                                                          "for X")],
                                                                                     )],
                                                                                         style={
                                                                                             'padding': 10}),
                                                                                     html.Div([html.Label(
                                                                                         ["Select Y variable:",
                                                                                          dcc.Dropdown(
                                                                                              id='yaxis-anim-2D',
                                                                                              multi=False,
                                                                                              placeholder='Select an option '
                                                                                                          'for Y')],
                                                                                     ), ],
                                                                                         style={
                                                                                             'padding': 10}),
                                                                                     html.Div([html.Label(
                                                                                         ["Select Animation Frame:",
                                                                                          dcc.Dropdown(
                                                                                              id='anim-frame-2D',
                                                                                              multi=False,
                                                                                              placeholder='Select an option '
                                                                                                          'for Animation Frame')],
                                                                                     ), ],
                                                                                         style={
                                                                                             'padding': 10}),
                                                                                 ],
                                                                                     style={
                                                                                         'display': 'inline-block',
                                                                                         'width': '32%',
                                                                                         'float': 'right',
                                                                                         'fontSize': 14,
                                                                                         'font-family': 'Arial',
                                                                                         'backgroundColor': '#ffffff'})
                                                                             ], className='container',
                                                                                 style={'padding': 20,
                                                                                        'backgroundColor': '#ffffff'})
                                                                         ]),
                                                                 dcc.Tab(label='3', style=tab_mini_style,
                                                                         selected_style=tab_mini_selected_style,
                                                                         children=[
                                                                             html.Div(
                                                                                 [
                                                                                     html.Div(
                                                                                         [
                                                                                             html.Div(
                                                                                                 [
                                                                                                     dcc.Graph(
                                                                                                         id='my-3D-graph',
                                                                                                         animate=False)
                                                                                                 ],
                                                                                                 style={
                                                                                                     'display': 'inline-block',
                                                                                                     'width': '56%',
                                                                                                 }
                                                                                             ),
                                                                                             html.Div(
                                                                                                 [
                                                                                                     html.Div(
                                                                                                         [
                                                                                                             html.Label(
                                                                                                                 [
                                                                                                                     "Select X variable:",
                                                                                                                     dcc.Dropdown(
                                                                                                                         id='xaxis-anim-3D',
                                                                                                                         multi=False,
                                                                                                                         placeholder="Select an option for X")
                                                                                                                 ],
                                                                                                             )
                                                                                                         ],
                                                                                                         style={
                                                                                                             'padding': 10
                                                                                                         }
                                                                                                     ),
                                                                                                     html.Div(
                                                                                                         [
                                                                                                             html.Label(
                                                                                                                 [
                                                                                                                     "Select Y variable:",
                                                                                                                     dcc.Dropdown(
                                                                                                                         id='yaxis-anim-3D',
                                                                                                                         multi=False,
                                                                                                                         placeholder='Select an option for Y'
                                                                                                                     )
                                                                                                                 ],
                                                                                                             ),
                                                                                                         ],
                                                                                                         style={
                                                                                                             'padding': 10}
                                                                                                     ),
                                                                                                     html.Div(
                                                                                                         [
                                                                                                             html.Label(
                                                                                                                 [
                                                                                                                     "Select color variable:",
                                                                                                                     dcc.Dropdown(
                                                                                                                         id='caxis-anim-3D',
                                                                                                                         multi=False,
                                                                                                                         placeholder='Select an option for color')
                                                                                                                 ],
                                                                                                             )
                                                                                                         ],
                                                                                                         style={
                                                                                                             'padding': 10}
                                                                                                     ),
                                                                                                     html.Div(
                                                                                                         [
                                                                                                             html.Label(
                                                                                                                 [
                                                                                                                     "Select color bar range:",
                                                                                                                     dcc.RangeSlider(
                                                                                                                         id='colorbar-slider',
                                                                                                                     ),
                                                                                                                     html.Div(
                                                                                                                         id='slider-output-container')
                                                                                                                 ]
                                                                                                             )
                                                                                                         ],
                                                                                                         style={
                                                                                                             'fontSize': 14,
                                                                                                             'font-family': 'Arial',
                                                                                                             'padding': 15,
                                                                                                         }
                                                                                                     ),
                                                                                                     html.Div(
                                                                                                         [html.Label(
                                                                                                             [
                                                                                                                 "Select Animation Frame:",
                                                                                                                 dcc.Dropdown(
                                                                                                                     id='anim-frame-3Var',
                                                                                                                     multi=False,
                                                                                                                     placeholder='Select an option '
                                                                                                                                 'for Animation Frame')],
                                                                                                         ), ],
                                                                                                         style={
                                                                                                             'padding': 10})
                                                                                                 ],
                                                                                                 style={
                                                                                                     'display': 'inline-block',
                                                                                                     'width': '32%',
                                                                                                     'float': 'right',
                                                                                                     'fontSize': 14,
                                                                                                     'font-family': 'Arial',
                                                                                                     'backgroundColor': '#ffffff'}
                                                                                             )
                                                                                         ],
                                                                                         className='container',
                                                                                         style={
                                                                                             'padding': 20,
                                                                                             'backgroundColor': '#ffffff'
                                                                                         }
                                                                                     )
                                                                                 ]
                                                                             )
                                                                         ]),
                                                                 dcc.Tab(label='4', style=tab_mini_style,
                                                                         selected_style=tab_mini_selected_style,
                                                                         children=[html.Div([html.Div(
                                                                             [dcc.Graph(id='my-graph', animate=False)],
                                                                             style={'display': 'inline-block',
                                                                                    'width': '56%',
                                                                                    }),

                                                                             html.Div([
                                                                                 html.Div([html.Label([
                                                                                     "Select X variable:",
                                                                                     dcc.Dropdown(
                                                                                         id='xaxis-anim',
                                                                                         multi=False,
                                                                                         placeholder="Select an option "
                                                                                                     "for X")],
                                                                                 )],
                                                                                     style={
                                                                                         'padding': 10}),
                                                                                 html.Div([html.Label([
                                                                                     "Select Y variable:",
                                                                                     dcc.Dropdown(
                                                                                         id='yaxis-anim',
                                                                                         multi=False,
                                                                                         placeholder='Select an option '
                                                                                                     'for Y')],
                                                                                 ), ],
                                                                                     style={
                                                                                         'padding': 10}),
                                                                                 html.Div([html.Label(
                                                                                     [
                                                                                         "Select size variable:",
                                                                                         dcc.Dropdown(
                                                                                             id='saxis-anim',
                                                                                             multi=False,
                                                                                             placeholder='Select an option for size'),
                                                                                         html.Div(
                                                                                             id='size-container-4D')
                                                                                     ],
                                                                                 ),
                                                                                     dbc.Modal(
                                                                                         [
                                                                                             dbc.ModalHeader(
                                                                                                 "Selection Error!"),
                                                                                             dbc.ModalBody(
                                                                                                 "Please select a size variable that contains numerical values."),
                                                                                             dbc.ModalFooter(
                                                                                                 dbc.Button("Close",
                                                                                                            id="close",
                                                                                                            className="ml-auto")
                                                                                             ),
                                                                                         ],
                                                                                         id="modal-4Var",
                                                                                         is_open=False,
                                                                                         centered=True,
                                                                                         size="xl"
                                                                                     )
                                                                                 ], style={
                                                                                     'padding': 10}),
                                                                                 html.Div([html.Label(
                                                                                     [
                                                                                         "Select color variable:",
                                                                                         dcc.Dropdown(
                                                                                             id="caxis-anim",
                                                                                             multi=False,
                                                                                             placeholder='Select an option for color')],
                                                                                 )], style={
                                                                                     'padding': 10}),
                                                                                 html.Div([html.Label(
                                                                                     [
                                                                                         "Select color bar range:",
                                                                                         dcc.RangeSlider(
                                                                                             id='colorbar-slider-4D',
                                                                                         ),
                                                                                         html.Div(
                                                                                             id='slider-output-container-4D')
                                                                                     ]
                                                                                 )], style={
                                                                                     'fontSize': 14,
                                                                                     'font-family': 'Arial',
                                                                                     'padding': 7,
                                                                                 }
                                                                                 ),
                                                                                 html.Div(
                                                                                     [html.Label(
                                                                                         [
                                                                                             "Select Animation Frame:",
                                                                                             dcc.Dropdown(
                                                                                                 id='anim-frame-4Var',
                                                                                                 multi=False,
                                                                                                 placeholder='Select an option '
                                                                                                             'for Animation Frame')],
                                                                                     ), ],
                                                                                     style={
                                                                                         'padding': 10})
                                                                             ],
                                                                                 style={
                                                                                     'display': 'inline-block',
                                                                                     'width': '32%',
                                                                                     'float': 'right',
                                                                                     'fontSize': 14,
                                                                                     'font-family': 'Arial',
                                                                                     'backgroundColor': '#ffffff'})
                                                                         ], className='container',
                                                                             style={'padding': 20,
                                                                                    'backgroundColor': '#ffffff'})]
                                                                         )]
                                                       ), ]),
                            dcc.Tab(label='3D Animation', style=tab_style, selected_style=tab_selected_style,
                                    children=[html.Div([
                                        html.Div([dcc.Graph(id="graph"
                                                            )],
                                                 style={"width": "65%", "display": "inline-block", }),
                                        html.Div([
                                            html.Div([html.Label(["Select X variable:",
                                                                  dcc.Dropdown(id='xaxis-3D', multi=False,
                                                                               placeholder="Select an option for X", )],
                                                                 )],
                                                     style={'padding': 10}),
                                            html.Div([html.Label(["Select Y variable:",
                                                                  dcc.Dropdown(id='yaxis-3D', multi=False,

                                                                               placeholder='Select an option for Y')],
                                                                 ), ],
                                                     style={'padding': 10}),
                                            html.Div([html.Label(["Select Z variable:",
                                                                  dcc.Dropdown(id='zaxis-3D', multi=False,

                                                                               placeholder='Select an option for Z')],
                                                                 ), ],
                                                     style={'padding': 10}),
                                            html.Div([html.Label(
                                                ["Select size variable:",
                                                 dcc.Dropdown(id='saxis-3D', multi=False,
                                                              placeholder='Select an option for size',

                                                              ),
                                                 html.Div(
                                                     id='size-slider-container-5D')
                                                 ],
                                            ), dbc.Modal(
                                                [
                                                    dbc.ModalHeader(
                                                        "Selection Error!"),
                                                    dbc.ModalBody(
                                                        "Please select a size variable that contains numerical values."),
                                                    dbc.ModalFooter(
                                                        dbc.Button("Close",
                                                                   id="close-5D",
                                                                   className="ml-auto")
                                                    ),
                                                ],
                                                id="modal-5Var",
                                                is_open=False,
                                                centered=True,
                                                size="xl"
                                            )], style={'padding': 10}),
                                            html.Div([html.Label(
                                                ["Select color variable:",
                                                 dcc.Dropdown(id="caxis-3D", multi=False,

                                                              placeholder='Select an option for color')],
                                            )], style={'padding': 10}),
                                            html.Div([html.Label(
                                                [
                                                    "Select color bar range:",
                                                    dcc.RangeSlider(
                                                        id='colorbar-slider-5D',
                                                    ),
                                                    html.Div(id='slider-output-container-5D')
                                                ]
                                            )], style={
                                                'fontSize': 14,
                                                'font-family': 'Arial',
                                                'padding': 7,
                                            }
                                            ),
                                            html.Div(
                                                [html.Label(
                                                    [
                                                        "Select Animation Frame:",
                                                        dcc.Dropdown(
                                                            id='anim-frame-5D',
                                                            multi=False,
                                                            placeholder='Select an option '
                                                                        'for Animation Frame')],
                                                ), ],
                                                style={
                                                    'padding': 10})
                                        ],
                                            style={'fontSize': 14, 'fpmt-family': 'Arial', 'display': 'inline-block',
                                                   'width': '32%', 'float': 'right',
                                                   'backgroundColor': '#ffffff'})
                                        ,

                                    ], className='container', style={'backgroundColor': '#ffffff', 'padding': 20})])
                        ])
                    ]),
            dcc.Tab(label='MOF Data Filtering', style=tab_style, selected_style=tab_selected_style,
                    children=[html.Div([html.Div([dash_table.DataTable(id='data-table-interact',
                                                                       editable=True,
                                                                       filter_action='native',
                                                                       sort_action='native',
                                                                       sort_mode='multi',
                                                                       selected_columns=[],
                                                                       selected_rows=[],
                                                                       page_action='native',
                                                                       column_selectable='single',
                                                                       page_current=0,
                                                                       page_size=20,
                                                                       style_data={'height': 'auto'},
                                                                       style_table={'overflowX': 'scroll',
                                                                                    'maxHeight': '300px',
                                                                                    'overflowY': 'scroll'},
                                                                       style_cell={
                                                                           'minWidth': '0px', 'maxWidth': '220px',
                                                                           'whiteSpace': 'normal',
                                                                       }
                                                                       ),
                                                  html.Div(id='data-table-container'), ], style={'padding': 15}),

                                        html.Div([html.Div([
                                            html.Label(["Select X variable:",
                                                        (dcc.Dropdown(id='xaxis', placeholder="Select an option for X",
                                                                      multi=False))
                                                        ], className="six columns",
                                                       style={'fontSize': 14, 'font-family': 'Arial',
                                                              'width': '20%', 'display': 'inline-block', 'padding': 5
                                                              })
                                        ]),
                                            html.Div([
                                                html.Label(["Select Y variable:",
                                                            (dcc.Dropdown(id='yaxis',
                                                                          placeholder="Select an option for Y",
                                                                          multi=False))
                                                            ], className="six columns",
                                                           style={'fontSize': 14, 'font-family': 'Arial',
                                                                  'width': '20%',
                                                                  'display': 'inline-block', 'padding': 5
                                                                  })
                                            ]),
                                            html.Div([
                                                html.Label(["Select size variable:",
                                                            dcc.Dropdown(id='saxis',
                                                                         placeholder="Select an option for size",
                                                                         multi=False),
                                                            ],
                                                           className="six columns",
                                                           style={'fontSize': 14, 'font-family': 'Arial',
                                                                  'width': '20%',
                                                                  'display': 'inline-block', 'padding': 5}
                                                           ),
                                                dbc.Modal(
                                                    [
                                                        dbc.ModalHeader(
                                                            "Selection Error!"),
                                                        dbc.ModalBody(
                                                            "Please select a size variable that contains numerical values."),
                                                        dbc.ModalFooter(
                                                            dbc.Button("Close",
                                                                       id="close-data",
                                                                       className="ml-auto")
                                                        ),
                                                    ],
                                                    id="modal-data",
                                                    is_open=False,
                                                    centered=True,
                                                    size="xl"
                                                )

                                            ]),
                                            html.Div([
                                                html.Label(["Select color variable:",
                                                            (dcc.Dropdown(id='caxis',
                                                                          placeholder="Select an option for color",
                                                                          multi=False))
                                                            ], className="six columns",
                                                           style={'fontSize': 14, 'font-family': 'Arial',
                                                                  'width': '20%',
                                                                  'display': 'inline-block', 'padding': 5
                                                                  }),
                                                dbc.Modal(
                                                    [
                                                        dbc.ModalHeader(
                                                            "Selection Error!"),
                                                        dbc.ModalBody(
                                                            "Please select a color variable that contains numerical values."),
                                                        dbc.ModalFooter(
                                                            dbc.Button("Close",
                                                                       id="close-datac",
                                                                       className="ml-auto")
                                                        ),
                                                    ],
                                                    id="modal-datac",
                                                    is_open=False,
                                                    centered=True,
                                                    size="xl"
                                                )
                                            ]),
                                        ],
                                            style={'padding-left': '15%', 'padding-right': '5%'}
                                        ),
                                        html.Div([html.Label(["Select X axis scale:",
                                                              dcc.RadioItems(
                                                                  id='xaxis-type',
                                                                  options=[{'label': i, 'value': i} for i in
                                                                           ['Linear', 'Log']],
                                                                  value='Linear',
                                                                  labelStyle={'display': 'inline-block', }
                                                              )]),
                                                  ], style={'display': 'inline-block', 'width': '24%'}),
                                        html.Div([html.Label(["Select Y axis scale:",
                                                              dcc.RadioItems(
                                                                  id='yaxis-type',
                                                                  options=[{'label': i, 'value': i} for i in
                                                                           ['Linear', 'Log']],
                                                                  value='Linear',
                                                                  labelStyle={'display': 'inline-block'}
                                                              )]),
                                                  ], style={'display': 'inline-block', 'width': '24%'}),
                                        html.Div([html.Label(["Select color scale:",
                                                              dcc.RadioItems(
                                                                  id='colorscale',
                                                                  options=[{'label': i, 'value': i} for i in
                                                                           ['Viridis', 'Plasma']],
                                                                  value='Plasma'
                                                              )]),
                                                  ], style={'display': 'inline-block', 'width': '24%', }),
                                        html.Div([html.Label(["Size range:"
                                                                 , html.Div(id='size-output-container-filter')])
                                                  ], style={'display': 'inline-block', 'width': '24%', }
                                                 ),
                                        app.css.append_css({
                                            'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
                                        })
                                        ], style={'backgroundColor': '#ffffff'})]
                    ),
            dcc.Tab(label='Statistical Analysis of Top Structures', style=tab_style,
                    selected_style=tab_selected_style,
                    children=[

                        dcc.Tabs(id="subtabs2", style=tabs_styles, children=[
                            dcc.Tab(label='Violin Plot', style=tab_style,
                                    selected_style=tab_selected_style,
                                    children=[html.Div([html.Div([dcc.Graph(id='violin-plot')
                                                                  ],
                                                                 style={'width': '65%', 'display': 'inline-block', })
                                                           , html.Div([
                                            html.Div([html.Label(
                                                ['Select variable to determine top performing structures (will filter '
                                                 'percentiles according to selected column):',
                                                 dcc.Dropdown(
                                                     id='data-set',
                                                     placeholder="Select an option for dataset",
                                                     multi=False,
                                                 )]
                                            ),
                                                dbc.Modal(
                                                    [
                                                        dbc.ModalHeader(
                                                            "Selection Error!"),
                                                        dbc.ModalBody(
                                                            "Please select a variable that contains numerical values."),
                                                        dbc.ModalFooter(
                                                            dbc.Button("Close",
                                                                       id="close-violin",
                                                                       className="ml-auto")
                                                        ),
                                                    ],
                                                    id="modal-violin",
                                                    is_open=False,
                                                    centered=True,
                                                    size="xl"
                                                )
                                            ], style={'padding': 10}),
                                            html.Div([html.Label(["Select % of structures in dataset to analyse per "
                                                                  "pressure:"
                                                                     , dcc.RadioItems(
                                                    id='percentile-type',
                                                    options=[{'label': 'All structures', 'value': 'All structures'},
                                                             {'label': 'Top 1% of structures',
                                                              'value': 'Top 1% of structures'},
                                                             {'label': 'Top 5% of structures',
                                                              'value': 'Top 5% of structures'},
                                                             {'label': 'Top 10% of structures',
                                                              'value': 'Top 10% of structures'}],
                                                    value='All structures',

                                                )]),
                                                      ], style={'padding': 10}),
                                            html.Div([html.Label(
                                                ["Select X variable:",
                                                 dcc.Dropdown(
                                                     id='anim-frame-violin',
                                                     multi=False,
                                                     placeholder='Select an option '
                                                                 'for X')],
                                            ), ],
                                                style={
                                                    'padding': 10}),
                                            html.Div([html.Label(["Select Y variable (Geometrical Property):",
                                                                  dcc.Dropdown(id='yaxis-stat',
                                                                               placeholder="Select an option for Y",
                                                                               multi=False,
                                                                               )])
                                                      ], style={'padding': 10}),
                                            html.Div([html.Label(["Take absolute values of data:",
                                                                  dcc.RadioItems(id='abs-value',
                                                                                 options=[
                                                                                     {'label': 'Yes', 'value': 'Yes'},
                                                                                     {'label': 'No', 'value': 'No'}],
                                                                                 value='Yes'

                                                                                 )])
                                                      ], style={'padding': 10}),
                                            dcc.Markdown(d("""
               **Click Data**

               Click on points in the graph.
           """)),
                                            html.Pre(id='click-data-stat'),

                                        ], style={'fontSize': 14, 'font-family': 'Arial', 'width': '30%',
                                                  'display': 'inline-block',
                                                  'float': 'right'})
                                                           ,

                                                        ], className='container', style={'padding': 40,
                                                                                         'backgroundColor': '#ffffff'})]),
                            dcc.Tab(label='Distribution Plot', style=tab_style,
                                    selected_style=tab_selected_style,
                                    children=[
                                        html.Div([
                                            html.Div([dcc.Graph(id='dist-plot', animate=False)],
                                                     style={'width': '65%', 'display': 'inline-block',
                                                            }),
                                            html.Div([html.Div([html.Label(
                                                ['Select variable to determine top performing structures (will filter '
                                                 'percentiles according to selected column):',
                                                 dcc.Dropdown(
                                                     id='data-set-dist',
                                                     placeholder="Select an option for dataset",
                                                     multi=False,
                                                 )]
                                            ),
                                                dbc.Modal(
                                                    [
                                                        dbc.ModalHeader(
                                                            "Selection Error!"),
                                                        dbc.ModalBody(
                                                            "Please select a variable that contains numerical values."),
                                                        dbc.ModalFooter(
                                                            dbc.Button("Close",
                                                                       id="close-dist",
                                                                       className="ml-auto")
                                                        ),
                                                    ],
                                                    id="modal-dist",
                                                    is_open=False,
                                                    centered=True,
                                                    size="xl"
                                                )
                                            ], style={'padding': 10}),
                                                html.Div([html.Label(["Select % of structures in dataset to analyse per"
                                                                      " pressure:"
                                                                         , dcc.RadioItems(
                                                        id='percentile-type-dist',
                                                        options=[{'label': 'All structures', 'value': 'All structures'},
                                                                 {'label': 'Top 1% of structures',
                                                                  'value': 'Top 1% of structures'},
                                                                 {'label': 'Top 5% of structures',
                                                                  'value': 'Top 5% of structures'},
                                                                 {'label': 'Top 10% of structures',
                                                                  'value': 'Top 10% of structures'}],
                                                        value='All structures',

                                                    )]),
                                                          ], style={'padding': 10}),
                                                html.Div([html.Label(["Select X variable:",
                                                                      dcc.Dropdown(id='xaxis-dist',
                                                                                   multi=False,
                                                                                   placeholder="Select an option for X"
                                                                                   )]), ],
                                                         style={'padding': 10
                                                                }),
                                                html.Div([html.Label(["Take absolute values of data:",
                                                                      dcc.RadioItems(id='abs-value-dist',
                                                                                     options=[{'label': 'Yes',
                                                                                               'value': 'Yes'},
                                                                                              {'label': 'No',
                                                                                               'value': 'No'}],
                                                                                     value='Yes'

                                                                                     )])
                                                          ], style={'padding': 10}),
                                                html.Div([html.Label(["Select Grouping:",
                                                                      dcc.RadioItems(
                                                                          id='dist-grouping',
                                                                          options=[{'label': i, 'value': i} for i in
                                                                                   ['None', 'Family']],
                                                                          value='None',
                                                                          labelStyle={'display': 'inline-block'})])
                                                          ]),
                                                html.Div([html.Label(
                                                    ["Select Animation Frame:",
                                                     dcc.Dropdown(
                                                         id='anim-frame-dist',
                                                         multi=False,
                                                         placeholder='Select an option '
                                                                     'for Animation Frame')],
                                                ), ],
                                                    style={
                                                        'padding': 10})
                                            ], style={'fontSize': 14, 'font-family': 'Arial', 'width': '30%',
                                                      'display': 'inline-block',
                                                      'float': 'right'})

                                        ], className='container', style={'backgroundColor': '#ffffff', 'padding': 40}
                                        )
                                    ]),
                        ]),

                    ])
        ], style=tabs_styles)
    ], style={'padding': 15})
], style={'backgroundColor': '#f6f6f6'})


# DOWNLOAD UPLOADED FILE
def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)


# READ FILE
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), delimiter=r'\s+'
                             )
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return df


# SIZE MODAL CALLBACK UPLOAD FILE
@app.callback(
    [Output('modal-upload', 'is_open'),
     Output('output-data-upload', 'children')],
    [
        Input('data-table-upload', 'contents'),
        Input('close-upload', 'n_clicks')],
    [State('data-table-upload', 'filename')])
def update_output(contents, modal_close, filename):
    ctx = dash.callback_context
    user_clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    df = parse_contents(contents, filename)
    if not user_clicked or user_clicked == 'close':
        return dash.no_update, False

    if contents is None:
        return [], False

    if not filename.endswith(('.xls', '.csv', '.txt')):
        return [], True
    return df


@app.callback(Output('csv-data', 'data'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def parse_uploaded_file(contents, filename):
    if not filename:
        return dash.no_update
    df = parse_contents(contents, filename)
    return df.to_json(date_format='iso', orient='split')


# POPULATE AXIS DROPDOWN 2VAR ENV ANIM
@app.callback([Output('xaxis-anim-2D', 'options'),
               Output('yaxis-anim-2D', 'options'), ],
              [Input('csv-data', 'data')])
def populate_dropdown_2var_anim(data):
    if not data:
        return dash.no_update, dash.no_update
    df = pd.read_json(data, orient='split')
    options = [{'label': i, 'value': i} for i in df.columns]
    return options, options


@app.callback(Output('anim-frame-2D', 'options'),
              [Input('csv-data', 'data')])
def populate_animation_frame_2D(data):
    if not data:
        return dash.no_update
    df = pd.read_json(data, orient='split')
    dff = df.select_dtypes(exclude=['float', 'object'])
    options = [{'label': i, 'value': i} for i in dff.columns]
    return options


# POPULATE GRAPH 2VAR ENV ANIM
@app.callback(Output('my-2D-graph', 'figure'),
              [
                  Input('xaxis-anim-2D', 'value'),
                  Input('yaxis-anim-2D', 'value'),
                  Input('anim-frame-2D', 'value')],
              [State('csv-data', 'data')]
              )
def update_figure_2Var(x, y, frame, data):
    if not data:
        return dash.no_update
    df = pd.read_json(data, orient='split')
    return px.scatter(df, x=df[x], y=df[y], title="", animation_frame=df[frame],
                      animation_group=df.columns[0],
                      hover_name=df.columns[0],
                      hover_data={}, template="none",
                      ).update_xaxes(showgrid=False, title=x.translate(SUP), autorange=True, ticks='outside',
                                     showline=True, showspikes=True, spikethickness=1, spikedash='solid',
                                     mirror=True, tickformat=".1f", title_standoff=10).update_yaxes(spikedash='solid',
                                                                                                    showgrid=False,
                                                                                                    title_standoff=10,
                                                                                                    title=dict(
                                                                                                        text=y.translate(
                                                                                                            SUP),
                                                                                                        standoff=5),
                                                                                                    autorange=True,
                                                                                                    ticks='outside',
                                                                                                    showspikes=True,
                                                                                                    spikethickness=1,
                                                                                                    showline=True,
                                                                                                    mirror=True,
                                                                                                    tickformat=".1f"
                                                                                                    ).update_layout(
        clickmode='event+select', hovermode='closest', margin={'l': 80}, autosize=True, font=dict(family='Helvetica')
    ).update_traces(marker=dict(opacity=0.7, line=dict(width=0.5, color='DarkSlateGrey'),
                                ))


# POPULATE AXIS DROPDOWN 3VAR ENV ANIM
@app.callback([Output('xaxis-anim-3D', 'options'),
               Output('yaxis-anim-3D', 'options'),
               Output('caxis-anim-3D', 'options')],
              [Input('csv-data', 'data')])
def populate_dropdown_3var_anim(data):
    if not data:
        return dash.no_update, dash.no_update, dash.no_update
    df = pd.read_json(data, orient='split')
    options = [{'label': i, 'value': i} for i in df.columns]
    return options, options, options


# POPULATE COLORBAR SLIDER SCATTER 3VAR ENV ANIM
@app.callback([Output('colorbar-slider', 'min'),
               Output('colorbar-slider', 'max'),
               Output('colorbar-slider', 'step'),
               Output('colorbar-slider', 'value')
               ],
              [Input('csv-data', 'data'),
               Input('caxis-anim-3D', 'value')
               ],
              [State('csv-data', 'data')])
def populate_pressure_slider_3Var(_, color, data):
    if not data or not color:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    df = pd.read_json(data, orient='split')
    min_v = round(float(df[color].min()), 1)
    max_v = round(float(df[color].max()), 1)
    step = 0.1
    value = [round(float(df[color].min()), 1), round(float(df[color].max()), 1)]
    return min_v, max_v, step, value


# STATE VALUE COLORBAR SLIDER SCATTER 3VAR ENV ANIM
@app.callback(
    Output('slider-output-container', 'children'),
    [Input('colorbar-slider', 'value')])
def update_output_3Var(value):
    return 'You have selected "{}"'.format(value)


# POPULATE 3VAR ENV ANIM FRAME
@app.callback(
    Output('anim-frame-3Var', 'options'),
    [Input('csv-data', 'data')]
)
def populate_animation_frame_3var(data):
    if not data:
        return dash.no_update
    df = pd.read_json(data, orient='split')
    dff = df.select_dtypes(exclude=['float', 'object'])
    options = [{'label': i, 'value': i} for i in dff.columns]
    return options


# POPULATE GRAPH 3VAR ENV ANIM
@app.callback(Output('my-3D-graph', 'figure'),
              [Input('xaxis-anim-3D', 'value'),
               Input('yaxis-anim-3D', 'value'),
               Input('caxis-anim-3D', 'value'),
               Input('colorbar-slider', 'value'),
               Input('anim-frame-3Var', 'value')],
              [State('csv-data', 'data')])
def update_figure_3Var(x, y, color, color_value, frame, data):
    if not data or not color_value:
        return dash.no_update
    df = pd.read_json(data, orient='split')
    color_val_float = []
    for i in range(0, len(color_value), 1):
        color_val_float.append(float(color_value[i]))
    color_val = color_val_float
    return px.scatter(df,
                      x=df[x],
                      y=df[y],
                      title="",
                      animation_frame=df[frame],
                      animation_group=df.columns[0],
                      hover_name=df.columns[0],
                      hover_data={},
                      template="none",
                      color=df[color],
                      color_continuous_scale='Viridis',
                      range_color=color_val
                      ).update_xaxes(showgrid=False, title_standoff=10,
                                     title=x.translate(SUP),
                                     autorange=True,
                                     ticks='outside',
                                     showline=True,
                                     showspikes=True,
                                     spikethickness=1,
                                     spikedash='solid',
                                     mirror=True,
                                     tickformat=".1f").update_yaxes(spikedash='solid', title_standoff=10,
                                                                    showgrid=False,
                                                                    title=dict(text=y.translate(SUP)
                                                                               , standoff=5),
                                                                    autorange=True,
                                                                    ticks='outside',
                                                                    showspikes=True,
                                                                    spikethickness=1,
                                                                    showline=True,
                                                                    mirror=True,
                                                                    tickformat=".1f").update_layout(
        clickmode='event+select',
        hovermode='closest',
        margin={'l': 80},
        autosize=True,
        font=dict(family='Helvetica', ),
        coloraxis_colorbar=dict(title=dict(text=color.translate(SUP), side='right'), ypad=0),
    ).update_traces(marker=dict(size=10,
                                opacity=0.7,
                                showscale=False,
                                line=dict(width=0.7, color='DarkSlateGrey'),
                                colorscale="Viridis"))


# POPULATE AXIS DROPDOWN 4VAR ENV ANIM
@app.callback([Output('xaxis-anim', 'options'),
               Output('yaxis-anim', 'options'),
               Output('caxis-anim', 'options'),
               Output('saxis-anim', 'options')
               ],
              [Input('csv-data', 'data')])
def populate_dropdown_4var_anim(data):
    if not data:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    df = pd.read_json(data, orient='split')
    options = [{'label': i, 'value': i} for i in df.columns]
    return options, options, options, options


# SIZE MODAL CALLBACK 4VAR ENV ANIM
@app.callback(
    Output('modal-4Var', 'is_open'),
    [Input('saxis-anim', 'value'),
     Input('data-table-upload', 'contents'),
     Input('close', 'n_clicks')],
    [State('data-table-upload', 'filename')])
def update_output_4Var(size_value, contents, modal_close, filename):
    ctx = dash.callback_context
    user_clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    df = parse_contents(contents, filename)
    size_list = df[size_value].to_list()
    if not user_clicked or user_clicked == 'close':
        return dash.no_update, False

    if contents is None:
        return [], False

    if filename is None:
        return [], False

    if size_value is None:
        return [], False

    for item in size_list:
        if any(c.isalpha() for c in item):
            return [], True


# POPULATE COLORBAR SLIDER SCATTER 4VAR ENV ANIM
@app.callback([Output('colorbar-slider-4D', 'min'),
               Output('colorbar-slider-4D', 'max'),
               Output('colorbar-slider-4D', 'step'),
               Output('colorbar-slider-4D', 'value')
               ],
              [Input('csv-data', 'data'),
               Input('caxis-anim', 'value')
               ],
              [State('csv-data', 'data')])
def populate_pressure_slider_4Var(_, color, data):
    if not data or not color:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    df = pd.read_json(data, orient='split')
    min_v = round(float(df[color].min()), 1)
    max_v = round(float(df[color].max()), 1)
    step = 0.1
    value = [round(float(df[color].min()), 1), round(float(df[color].max()), 1)]
    return min_v, max_v, step, value


@app.callback(
    Output('slider-output-container-4D', 'children'),
    [Input('colorbar-slider-4D', 'value')])
def update_output_4Var(value):
    return 'You have selected "{}"'.format(value)


# SIZE RANGE
@app.callback(
    Output('size-container-4D', 'children'),
    [Input('saxis-anim', 'value'),
     Input('csv-data', 'data')],
    [State('csv-data', 'data')]
)
def update_output_size_range_4Var(size, __, data):
    if not data or not size:
        return dash.no_update
    df = pd.read_json(data, orient='split')
    size_range = [round(df[size].min(), 2), round(df[size].max(), 2)]
    return 'Size range: {}'.format(size_range)


# POPULATE GRAPH 4VAR ENV ANIM FRAME
@app.callback(
    Output('anim-frame-4Var', 'options'),
    [Input('csv-data', 'data')]
)
def populate_animation_frame_4var(data):
    if not data:
        return dash.no_update
    df = pd.read_json(data, orient='split')
    dff = df.select_dtypes(exclude=['float', 'object'])
    options = [{'label': i, 'value': i} for i in dff.columns]
    return options


# POPULATE GRAPH 4VAR ENV ANIM
@app.callback(Output('my-graph', 'figure'),
              [
                  Input('xaxis-anim', 'value'),
                  Input('yaxis-anim', 'value'),
                  Input('caxis-anim', 'value'),
                  Input('saxis-anim', 'value'),
                  Input('colorbar-slider-4D', 'value'),
                  Input('anim-frame-4Var', 'value')],
              [State('csv-data', 'data')]
              )
def update_figure_4Var(x, y, color, size, color_value, frame, data):
    if not data or not color_value:
        return dash.no_update
    df = pd.read_json(data, orient='split')
    # size_range = [df[size].min(), df[size].max()]
    color_val_float = []
    for i in range(0, len(color_value), 1):
        color_val_float.append(float(color_value[i]))
    color_val = color_val_float
    return px.scatter(df, x=df[x], y=df[y], title="", animation_frame=frame,
                      animation_group=df.columns[0], size=df[size], color=df[color],
                      hover_name=df.columns[0],
                      color_continuous_scale='Viridis',
                      hover_data={}, template="none", range_color=color_val
                      ).update_xaxes(showgrid=False, title=x.translate(SUP), autorange=True, ticks='outside',
                                     showline=True, showspikes=True, spikethickness=1, spikedash='solid',
                                     title_standoff=10,
                                     mirror=True, tickformat=".1f").update_yaxes(spikedash='solid',
                                                                                 showgrid=False, title_standoff=10,
                                                                                 title=dict(text=y.translate(SUP),
                                                                                            standoff=5),
                                                                                 autorange=True, ticks='outside',
                                                                                 showspikes=True, spikethickness=1,
                                                                                 showline=True, mirror=True,
                                                                                 tickformat=".1f").update_layout(
        clickmode='event+select', hovermode='closest', margin={'l': 80}, autosize=True, font=dict(family='Helvetica'),
        coloraxis_colorbar=dict(title=dict(text=color.translate(SUP), side='right', font=dict(size=14)), ypad=0),
        # annotations=[
        #     dict(x=1.5, y=-0.15, showarrow=False, align='left',
        #          text='Size range: {}'.format(size_range), xref='paper', yref='paper', font=dict(size=14))
        # ]
    ).update_traces(marker=dict(opacity=0.7, showscale=False, line=dict(width=0.5, color='DarkSlateGrey'),
                                ))


# POPULATE AXIS DROPDOWN 5VAR (3D) ENV ANIM
@app.callback([Output('xaxis-3D', 'options'),
               Output('yaxis-3D', 'options'),
               Output('zaxis-3D', 'options'),
               Output('saxis-3D', 'options'),
               Output('caxis-3D', 'options')
               ],
              [Input('csv-data', 'data')], )
def populate_dropdown_5D_anim(data):
    if not data:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    df = pd.read_json(data, orient='split')
    options = [{'label': i, 'value': i} for i in df.columns]
    return options, options, options, options, options


# SIZE MODAL CALLBACK 5VAR (3D) ENV ANIM
@app.callback(
    Output('modal-5Var', 'is_open'),
    [Input('saxis-3D', 'value'),
     Input('data-table-upload', 'contents'),
     Input('close-5D', 'n_clicks')],
    [State('data-table-upload', 'filename')])
def update_output_modal5(size_value, contents, modal_close, filename):
    ctx = dash.callback_context
    user_clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    df = parse_contents(contents, filename)
    size_list = df[size_value].to_list()
    if not user_clicked or user_clicked == 'close':
        return dash.no_update, False

    if contents is None:
        return [], False

    if filename is None:
        return [], False

    if size_value is None:
        return [], False

    for item in size_list:
        if any(c.isalpha() for c in item):
            return [], True


# POPULATE COLORBAR SLIDER SCATTER 5VAR (3D) ENV ANIM
@app.callback([Output('colorbar-slider-5D', 'min'),
               Output('colorbar-slider-5D', 'max'),
               Output('colorbar-slider-5D', 'step'),
               Output('colorbar-slider-5D', 'value')
               ],
              [Input('csv-data', 'data'),
               Input('caxis-3D', 'value')
               ],
              [State('csv-data', 'data')])
def populate_pressure_slider_5D(_, color, data):
    if not data or not color:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    df = pd.read_json(data, orient='split')
    min_v = round(float(df[color].min()), 1)
    max_v = round(float(df[color].max()), 1)
    step = 0.1
    value = [round(float(df[color].min()), 1), round(float(df[color].max()), 1)]
    return min_v, max_v, step, value


@app.callback(
    Output('slider-output-container-5D', 'children'),
    [Input('colorbar-slider-5D', 'value')])
def update_output_colorbar_5D(value):
    return 'You have selected "{}"'.format(value)


# SIZE RANGE
@app.callback(
    Output('size-slider-container-5D', 'children'),
    [Input('saxis-3D', 'value'),
     Input('csv-data', 'data')],
    [State('csv-data', 'data')]
)
def update_output_size_range_5D(size, __, data):
    if not data or not size:
        return dash.no_update
    df = pd.read_json(data, orient='split')
    size_range = [round(df[size].min(), 2), round(df[size].max(), 2)]
    return 'Size range: {}'.format(size_range)


@app.callback(
    Output('anim-frame-5D', 'options'),
    [Input('csv-data', 'data')]
)
def populate_animation_frame_5D(data):
    if not data:
        return dash.no_update
    df = pd.read_json(data, orient='split')
    dff = df.select_dtypes(exclude=['float', 'object'])
    options = [{'label': i, 'value': i} for i in dff.columns]
    return options


# POPULATE GRAPH 5VAR (3D) ENV ANIM
@app.callback(Output("graph", "figure"),
              [Input('xaxis-3D', "value"),
               Input('yaxis-3D', 'value'),
               Input('zaxis-3D', 'value'),
               Input('caxis-3D', 'value'),
               Input('saxis-3D', 'value'),
               Input('colorbar-slider-5D', 'value'),
               Input('anim-frame-5D', 'value')],
              [State('csv-data', 'data')]
              )
def make_figure(x, y, z, color, size, color_value, frame, data):
    if not data or not color_value:
        return dash.no_update
    if x and y and z and color and size is None:
        return dash.no_update
    df = pd.read_json(data, orient='split')
    color_val_float = []
    for i in range(0, len(color_value), 1):
        color_val_float.append(float(color_value[i]))
    color_val = color_val_float
    return px.scatter_3d(df, x=df[x], y=df[y], z=df[z], title="", animation_frame=frame,
                         animation_group=df.columns[0], size=df[size], color=df[color],
                         hover_name=df.columns[0],
                         color_continuous_scale='Viridis',
                         hover_data={}, template="none", range_color=color_val
                         ).update_xaxes(showgrid=False, title=x.translate(SUP), autorange=True, tickformat=".1f"
                                        ).update_yaxes(
        showgrid=False, title=y.translate(SUP), autorange=True, tickformat=".1f").update_layout(
        coloraxis_colorbar=dict(title=dict(text=color.translate(SUP), side='right', font=dict(size=14)), ypad=0),
        font=dict(family='Helvetica'),
        clickmode='event+select', hovermode='closest', margin={'l': 50, 'b': 80, 't': 50, 'r': 10}, autosize=True,
    ).update_traces(
        marker=dict(opacity=0.7, showscale=False, line=dict(width=0.5, color='#3d3d3d'),
                    ))


# POPULATE AXIS DROPDOWN SCATTER DATA TABLE FIGURE
@app.callback([Output('xaxis', 'options'),
               Output('yaxis', 'options'),
               Output('caxis', 'options'),
               Output('saxis', 'options')
               ],
              [Input('csv-data', 'data')], )
def populate_scatter_dropdown(data):
    if not data:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    df = pd.read_json(data, orient='split')
    options = [{'label': i, 'value': i} for i in df.columns]
    return options, options, options, options


# SIZE MODAL CALLBACK SCATTER DATA TABLE
@app.callback(
    Output('modal-data', 'is_open'),
    [Input('saxis', 'value'),
     Input('data-table-upload', 'contents'),
     Input('close-data', 'n_clicks')],
    [State('data-table-upload', 'filename')])
def update_output(size_value, contents, modal_close, filename):
    ctx = dash.callback_context
    user_clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    df = parse_contents(contents, filename)
    size_list = df[size_value].to_list()
    if not user_clicked or user_clicked == 'close':
        return dash.no_update, False

    if contents is None:
        return [], False

    if filename is None:
        return [], False

    if size_value is None:
        return [], False

    for item in size_list:
        if any(c.isalpha() for c in item):
            return [], True


# COLOR MODAL CALLBACK SCATTER DATA TABLE
@app.callback(
    Output('modal-datac', 'is_open'),
    [Input('caxis', 'value'),
     Input('data-table-upload', 'contents'),
     Input('close-datac', 'n_clicks')],
    [State('data-table-upload', 'filename')])
def update_output(color_value, contents, modal_close, filename):
    ctx = dash.callback_context
    user_clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    df = parse_contents(contents, filename)
    color_list = df[color_value].to_list()
    if not user_clicked or user_clicked == 'close':
        return dash.no_update, False

    if contents is None:
        return [], False

    if filename is None:
        return [], False

    if color_value is None:
        return [], False

    for item in color_list:
        if any(c.isalpha() for c in item):
            return [], True


# POPULATE DATA TABLE SCATTER
@app.callback([Output('data-table-interact', 'data'),
               Output('data-table-interact', 'columns')],
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def update_output(contents, filename):
    if contents is None:
        return [{}], []
    df = parse_contents(contents, filename)
    data = df.to_dict('records')
    columns = [{"name": i, "id": i, "deletable": True, "selectable": True, 'type': 'numeric',
                'format': Format(precision=3, scheme=Scheme.fixed)} for i in df.columns]
    return data, columns


# SIZE RANGE
@app.callback(
    Output('size-output-container-filter', 'children'),
    [Input('saxis', 'value'),
     Input('csv-data', 'data')],
    [State('csv-data', 'data')]
)
def update_output(size, __, data):
    if not data or not size:
        return dash.no_update
    df = pd.read_json(data, orient='split')
    size_range = [round(df[size].min(), 2), round(df[size].max(), 2)]
    return '{}'.format(size_range)


# INTERACT FIGURE WITH POPULATED FIELDS SCATTER
@app.callback(Output('data-table-container', 'children'),
              [Input('data-table-interact', 'data'),
               Input('data-table-interact', 'derived_virtual_data'),
               Input('data-table-interact', 'derived_virtual_selected_rows'),
               Input('xaxis', 'value'),
               Input('yaxis', 'value'),
               Input('caxis', 'value'),
               Input('saxis', 'value'),
               Input('xaxis-type', 'value'),
               Input('yaxis-type', 'value'),
               Input('colorscale', 'value')
               ])
def update_figure(rows, derived_virtual_data, derived_virtual_selected_rows, xaxis_name, yaxis_name,
                  marker_color, marker_size, xaxis_type, yaxis_type, colorscale):
    df = pd.DataFrame(rows)
    if derived_virtual_selected_rows is None:
        return []
    dff = df if derived_virtual_data is None else pd.DataFrame(derived_virtual_data)
    print(dff[marker_color])
    return [
        html.Div([dcc.Graph(id='HTS-graph',
                            figure={'data': [
                                go.Scatter(x=dff[xaxis_name], y=dff[yaxis_name],
                                           mode='markers',
                                           marker_color=dff[marker_color],
                                           marker_size=dff[marker_size],
                                           marker=dict(sizemode='area', sizeref=max(dff[marker_size]) / (15 ** 2),
                                                       sizemin=4,
                                                       opacity=0.7, showscale=True,
                                                       line=dict(width=0.7, color='DarkSlateGrey'),
                                                       colorbar=dict(title=dict(text=marker_color.translate(SUP),
                                                                                font=dict(family='Helvetica'),
                                                                                side='right'), ypad=0),
                                                       colorscale="Viridis" if colorscale == 'Viridis' else "Plasma"),
                                           text=dff[df.columns[0]],
                                           hoverinfo=['x', 'y', 'text', 'name'],
                                           )],
                                'layout': go.Layout(
                                    font={'family': 'Helvetica', 'size': 14},
                                    xaxis={'title': xaxis_name.translate(SUP), 'autorange': True,
                                           'mirror': True,
                                           'ticks': 'outside',
                                           'showline': True,
                                           'showspikes': True,
                                           'type': 'linear' if xaxis_type == 'Linear' else 'log',
                                           'tickformat': ".1f"
                                           },
                                    yaxis={'title': yaxis_name.translate(SUP), 'autorange': True,
                                           'mirror': True,
                                           'ticks': 'outside',
                                           'showline': True,
                                           'showspikes': True,
                                           'type': 'linear' if yaxis_type == 'Linear' else 'log',
                                           'tickformat': ".1f"
                                           },
                                    title="",
                                    template="simple_white",
                                    margin={'l': 50, 'b': 60, 't': 70, 'r': 50},
                                    hovermode='closest',
                                    width=550,
                                ),
                            },
                            )
                  ], style={'textAlign': 'center', 'padding': 25,
                            'horizontal-align': 'middle',
                            'padding-left': '25%', 'padding-right': '25%'
                            })
        for column in [xaxis_name] if column in dff
        for column in [yaxis_name] if column in dff
        for column in [marker_color] if column in dff
        for column in [marker_size] if column in dff
    ]


# POPULATE DROPDOWN DATASET VIOLIN
@app.callback(Output('data-set', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_df_dropdown(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# POPULATE DROPDOWN Y AXIS VIOLIN
@app.callback(Output('yaxis-stat', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_yaxis_stat(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# VIRIDIS AND PLASMA COLOR PALETTE
colors = ('rgb(240, 249, 33)', 'rgb(253, 202, 38)', 'rgb(251, 159, 58)', 'rgb(237, 121, 83)', 'rgb(216, 87, 107)',
          'rgb(189, 55, 134)', 'rgb(156, 23, 158)', 'rgb(114, 1, 168)', 'rgb(70, 3, 159)', 'rgb(13, 8, 135)',

          )
colors2 = ('rgb(68, 1, 84)', 'rgb(72, 40, 120)', 'rgb(62, 73, 137)', 'rgb(49, 104, 142)', 'rgb(38, 130, 142)',
           'rgb(31, 158, 137)', 'rgb(53, 183, 121)', 'rgb(110, 206, 88)', 'rgb(181, 222, 43)', 'rgb(253, 231, 37)')


# SIZE MODAL CALLBACK VIOLIN PLOT
@app.callback(
    Output('modal-violin', 'is_open'),
    [Input('data-set', 'value'),
     Input('data-table-upload', 'contents'),
     Input('close-violin', 'n_clicks')],
    [State('data-table-upload', 'filename')])
def update_output(size_value, contents, modal_close, filename):
    ctx = dash.callback_context
    user_clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    df = parse_contents(contents, filename)
    size_list = df[size_value].to_list()
    if not user_clicked or user_clicked == 'close':
        return dash.no_update, False

    if contents is None:
        return [], False

    if filename is None:
        return [], False

    if size_value is None:
        return [], False

    for item in size_list:
        if any(c.isalpha() for c in item):
            return [], True


# POPULATE VIOLIN PLOT X AXIS GROUPING
@app.callback(Output('anim-frame-violin', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_animation_frame_dist(contents, filename):
    df = parse_contents(contents, filename)
    dff = df.select_dtypes(exclude=['float'])
    return [{'label': i, 'value': i} for i in dff.columns]


# POPULATE VIOLIN PLOT CHANGED
@app.callback(Output('violin-plot', 'figure'),
              [
                  Input('yaxis-stat', 'value'),
                  Input('percentile-type', 'value'),
                  Input('abs-value', 'value'),
                  Input('anim-frame-violin', 'value'),
                  Input('data-set', 'value'),
                  Input('data-table-upload', 'contents')
              ],
              [State('data-table-upload', 'filename')]
              )
def update_graph_stat(yaxis_name, percentile_type, abs_value, frame_value, data_set, contents, filename):
    df = parse_contents(contents, filename)
    print()
    traces = []
    frame_set = set(df[frame_value])
    frame_list = sorted(list(frame_set))
    if data_set is None:
        return dash.no_update
    dfObj = pd.DataFrame()
    flag1 = False
    if percentile_type == 'All structures':
        data = df
    for frame in frame_list:
        dff = df[(df[frame_value] == frame)]
        if percentile_type == 'Top 1% of structures' and abs_value == 'Yes':
            data = dff[abs(dff[(data_set)]) > abs(dff[data_set]).quantile(0.99)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
        elif percentile_type == 'Top 1% of structures' and abs_value == 'No':
            data = dff[dff[(data_set)] > dff[data_set].quantile(0.99)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
        elif percentile_type == 'Top 5% of structures' and abs_value == 'Yes':
            data = dff[abs(dff[data_set]) > abs(dff[data_set]).quantile(0.95)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
        elif percentile_type == 'Top 5% of structures' and abs_value == 'No':
            data = dff[dff[data_set] > dff[data_set].quantile(0.95)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
        elif percentile_type == 'Top 10% of structures' and abs_value == 'Yes':
            data = dff[abs(dff[data_set]) > abs(dff[data_set]).quantile(0.9)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
        elif percentile_type == 'Top 10% of structures' and abs_value == 'No':
            data = dff[dff[data_set] > dff[data_set].quantile(0.9)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
    if yaxis_name is None:
        return dash.no_update
    if flag1 == True:
        data = dfObj
    for frame, color in zip(frame_list, colors):
        traces.append(go.Violin(y=data[data[frame_value] == frame][yaxis_name], name=frame,
                                line_color=color,
                                marker={'size': 4}, box_visible=True, opacity=0.9, meanline_visible=True,
                                points='all', text=data[df.columns[0]],
                                hovertemplate=
                                "<b>%{text}</b><br><br>" +
                                "Variable: %{y:.0f}<br>"
                                "Pressure: %{x:. bar}<br>"
                                ))
    return {'data': traces,

            'layout': go.Layout(
                title=f"<b> {''.join(str(i) for i in frame_value.translate(SUP))} against"
                      f" {''.join(str(i) for i in yaxis_name.translate(SUP))} "
                ,
                xaxis=dict(rangeslider=dict(visible=True), mirror=True, ticks='outside',
                           showline=True),
                yaxis={'title': yaxis_name.translate(SUP), 'mirror': True,
                       'ticks': 'outside', 'showline': True, 'tickformat': ".1f"},
                font=dict(
                    family="Helvetica",
                ),
                margin={'l': 60, 'b': 0, 't': 50, 'r': 50},
                hovermode='closest',
                annotations=[
                    dict(x=0.5, y=-0.135, showarrow=False, text=frame_value.translate(SUP),
                         xref='paper', yref='paper',
                         font=dict(size=14))
                ]
            )
            }


# CLICK DATA VIOLIN PLOT
@app.callback(
    Output('click-data-stat', 'children'),
    [Input('violin-plot', 'clickData'),
     ])
def display_click_data_stat(clickData):
    return json.dumps(clickData, indent=2)


# POPULATE DROPDOWN DATASET DIST PLOT
@app.callback(Output('data-set-dist', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_df_dropdown_dist(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# POPULATE X AXIS DROPDOWN DIST PLOT
@app.callback(Output('xaxis-dist', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_xaxis_dropdown_dist(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# SIZE MODAL CALLBACK 4VAR ENV ANIM
@app.callback(
    Output('modal-dist', 'is_open'),
    [Input('data-set-dist', 'value'),
     Input('data-table-upload', 'contents'),
     Input('close-dist', 'n_clicks')],
    [State('data-table-upload', 'filename')])
def update_output(size_value, contents, modal_close, filename):
    ctx = dash.callback_context
    user_clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    df = parse_contents(contents, filename)
    size_list = df[size_value].to_list()
    if not user_clicked or user_clicked == 'close':
        return dash.no_update, False

    if contents is None:
        return [], False

    if filename is None:
        return [], False

    if size_value is None:
        return [], False

    for item in size_list:
        if any(c.isalpha() for c in item):
            return [], True


# POPULATE DROPDOWN FOR DIST ANIMATION FRAME
@app.callback(Output('anim-frame-dist', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_animation_frame_dist(contents, filename):
    df = parse_contents(contents, filename)
    dff = df.select_dtypes(exclude=['float', 'object'])
    return [{'label': i, 'value': i} for i in dff.columns]


# POPULATE DIST PLOT
@app.callback(Output("dist-plot", "figure"),
              [Input('xaxis-dist', "value"),
               Input('dist-grouping', 'value'),
               Input('data-set-dist', 'value'),
               Input('percentile-type-dist', 'value'),
               Input('abs-value-dist', 'value'),
               Input('anim-frame-dist', 'value'),
               Input('data-table-upload', 'contents'), ],
              [State('data-table-upload', 'filename')])
def make_figure(x, dist_type, data_set, percentile_type, abs_value, frame, contents, filename):
    df = parse_contents(contents, filename)
    if x is None:
        return dash.no_update
    if data_set is None:
        return dash.no_update
    pressure_set = set(df['Pressure'])
    pressure_list = sorted(list(pressure_set))
    dfObj = pd.DataFrame()
    flag1 = False
    if percentile_type == 'All structures':
        data = df
    for pressure in pressure_list:
        dff = df[(df['Pressure'] == pressure)]
        if percentile_type == 'Top 1% of structures' and abs_value == 'Yes':
            data = dff[abs(dff[data_set]) > abs(dff[data_set]).quantile(0.99)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
        elif percentile_type == 'Top 1% of structures' and abs_value == 'No':
            data = dff[dff[data_set] > dff[data_set].quantile(0.99)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
        elif percentile_type == 'Top 5% of structures' and abs_value == 'Yes':
            data = dff[abs(dff[data_set]) > abs(dff[data_set]).quantile(0.95)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
        elif percentile_type == 'Top 5% of structures' and abs_value == 'No':
            data = dff[dff[data_set] > dff[data_set].quantile(0.95)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
        elif percentile_type == 'Top 10% of structures' and abs_value == 'Yes':
            data = dff[abs(dff[data_set]) > abs(dff[data_set]).quantile(0.9)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
        elif percentile_type == 'Top 10% of structures' and abs_value == 'No':
            data = dff[dff[data_set] > dff[data_set].quantile(0.9)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
    if flag1 == True:
        data = dfObj
    return px.histogram(data, x=data[x], marginal="rug",
                        color="Family" if dist_type == 'Family' else None,
                        animation_frame=frame,
                        hover_data=df.columns, hover_name=df.columns[0], template="none"
                        ).update_xaxes(showgrid=False, autorange=True, ticks='outside',
                                       mirror=True, showline=True, tickformat=".1f", title=' '
                                       ).update_yaxes(showgrid=False, ticks='outside',
                                                      mirror=True, autorange=True, showline=True, tickformat=".1f",
                                                      title=' '
                                                      ).update_layout(
        hovermode='closest', margin={'l': 60, 'b': 80, 't': 50, 'r': 10}, autosize=True, font=dict(family='Helvetica'),
        annotations=[dict(x=0.5, y=-0.17, showarrow=False, text=x.translate(SUP), xref='paper', yref='paper',
                          font=dict(size=14)),
                     dict(x=-0.13, y=0.5, showarrow=False, text="Number of Structures", textangle=-90, xref='paper',
                          yref='paper', font=dict(size=14))]
    ).update_traces(marker=dict(opacity=0.7, line=dict(width=0.5, color='DarkSlateGrey'),
                                )).update_layout(
        title=f"<b> Distribution of Structures against {''.join(str(i) for i in x.translate(SUP))}", font=dict(
            family="Arial",
        ), )


# RUN APP
if __name__ == '__main__':
    app.run_server()
