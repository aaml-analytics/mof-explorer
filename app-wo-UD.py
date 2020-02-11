import base64
import io
import os
from urllib.parse import quote as urlquote
from flask import Flask, send_from_directory
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objs as go
from textwrap import dedent as d
import plotly.express as px
import json
import textwrap


# CREATE DASH APP
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
server = Flask(__name__)
app = dash.Dash(external_stylesheets=external_stylesheets, server=server)

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
    'width':'50px',
    'color': '#000000',
    'fontColor': '#000000',
}

tab_mini_selected_style={
    'borderTop': '3px solid #5e5e5e',
    'borderBottom': '1px solid #d6d6d6 ',
    'backgroundColor': '#5e5e5e',
    'color': '#ffffff',
    # 'fontColor': '#004a4a',
    'fontWeight': 'bold',
    'padding': '6px',
    'width':'50px'
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


# APP LAYOUT
MOF_tool_about = textwrap.wrap(' These tools aim to provide a reproducible and consistent data visualisation platform '
                               'where experimental and computational researchers can use big data and statistical '
                               'analysis to find the best materials for specific applications',
                               width=50)
twoD_threeD_about = textwrap.wrap(' The 2D Animated MOF Explorer and 3D Animated MOF Explorer provides a 2,3, 4 and'
                                  '5-Dimensional variable environment respectively to explore specific structures '
                                  'against pressure to find the best materials for the users applications', width=50)
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
                                  'analysed against pressure to determine Q1, Q3, IQR, mean, median, maximum and'
                                  ' minimum points for a dataset of the users choice, alongside the distribution of '
                                  'MOFs in said violin plot. In the distribution plot, the number of structures against '
                                  'a variable in the users data frame can be analysed to determine the spread of '
                                  'structures in the users data. The distribution can be further filtered by MOF '
                                  'families (if the user has uploaded this information in its data frame). '
                                  'An animation feature is also available to view these frames in accordance'
                                  ' to pressure.', width=50, )

app.layout = html.Div([
    html.Div([
        html.Img(
            src='https://raw.githubusercontent.com/aaml-analytics/mof-explorer/master/UOC.png',
            height='30', width='120', style={'display': 'inline-block', 'padding-left': '1%'}),
        html.H1("Metal-Organic Framework Data Visualisation Tools",
                style={'display': 'inline-block', 'padding-left': '10%','text-align':'center', 'fontSize': 36,
                       'color': 'white', 'font-family': 'Georgia'}),
        html.Img(src='https://raw.githubusercontent.com/aaml-analytics/mof-explorer/master/A2ML-logo.png',
                 height='60', width='130', style={'float': 'right', 'display': 'inline-block', 'padding-right': '2%'}),
        html.H1("...", style={'fontColor': '#3c3c3c', 'fontSize': 6})
    ], style={'backgroundColor': '#004040'}),
    html.Div([html.A('Refresh', href='/')], style={}),
    html.Div([
        html.H2("Upload Data", style={'fontSize': 24, 'font-family': 'Arial', 'color': '#004a4a'}, ),
        html.H3("Upload .txt, .csv or xls files to starting exploring data...", style={'fontSize': 16,
                                                                                       'font-family': 'Arial'}),
        dcc.Upload(
            id='data-table-upload',
            children=html.Div([html.Button('Upload File')],
                              style={'width': '49%', 'height': "60px", 'borderWidth': '1px',
                                     'borderRadius': '5px',
                                     'textAlign': 'center',

                                     }),
            multiple=False
        ), ], style={'display': 'inline-block', 'width': '48%', 'padding-left': '1%', }),
    html.Div([html.Div([html.H2("Explore Data", style={'fontSize': 24,
                                                                              'font-family': 'Arial',
                                                       'color': '#004a4a'})],
                       style={}),
              html.Div([ '', html.A('Download',
                                href='https://github.com/aaml-analytics/mof-explorer/tree/master/sample-data')]),
              html.H3("...AAML's sample file to explore tool functions...", style={'fontSize': 16,
                                                                                                 'font-family': 'Arial', 'display': 'inline-block'}),
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
                                                style={'fontSize': 18, 'font-weight':'bold',
                                                       'font-family': 'Arial'}),
                                        html.Div([' '.join(MOF_stat_analysis)], style={'font-family': 'Arial'}),
                                        # ADD LINK
                                        html.Div([html.Plaintext(
                                            [' Click ', html.A('here',
                                                               href='https://github.com/aaml-analytics/mof-explorer')],
                                                       style={'display': 'inline-block',
                                                              'fontSize': 14, }),
                                        html.Plaintext(
                                            [" to explore AAML's sample data and read more on"
                                             " AAML's MOF Explorer Tool Manual, FAQ's & Troubleshooting"
                                             " on GitHub... ", ]
                                            , style={'display': 'inline-block', 'fontSize': 14}),
                                                  html.Img(
                                                      src='https://raw.githubusercontent.com/aaml-analytics/mof'
                                                          '-explorer/master/github.png',
                                                      height='40', width='40',
                                                      style={'display': 'inline-block', 'float':"right"
                                                            })
                                                  ]
                                                 ,style={'display': 'inline-block'})
                                        ], style={'backgroundColor': '#ffffff'}
                                       )]),
            dcc.Tab(label='MOF Explorer Animation', style=tab_style, selected_style=tab_selected_style,
                    children=[
                        dcc.Tabs(id='sub-tabs1', style=tabs_styles, children=[
                            dcc.Tab(label='2D Animation',style=tab_style, selected_style=tab_selected_style, children=[dcc.Tabs( id='subsub-tabs',style=tabs_styles,
                                    children=[dcc.Tab(label='2', style=tab_mini_style, selected_style=tab_mini_selected_style,children=[
                                    html.Div([html.Div([dcc.Graph(id='my-2D-graph', animate=False)],
                                                                 style={'display': 'inline-block', 'width': '65%',
                                                                        }),
                                                        html.Div([
                                                            html.Div([html.Label(["Select X variable:",
                                                                                  dcc.Dropdown(id='xaxis-anim-2D',
                                                                                               multi=False,
                                                                                               placeholder="Select an option "
                                                                                                           "for X")],
                                                                                 )],
                                                                     style={
                                                                            'padding': 10}),
                                                            html.Div([html.Label(["Select Y variable:",
                                                                                  dcc.Dropdown(id='yaxis-anim-2D',
                                                                                               multi=False,
                                                                                               placeholder='Select an option '
                                                                                                           'for Y')],
                                                                                 ), ],
                                                                     style={ 
                                                                            'padding': 10}),
                                                        ],
                                                            style={'display': 'inline-block', 'width': '30%',
                                                                   'float': 'right', 'fontSize':14,'font-family':'Arial',
                                                                 'backgroundColor': '#ffffff'})
                                                        ], className='container', style={'padding':40,'backgroundColor': '#ffffff'})
                                    ]),
                                        dcc.Tab(label='3', style=tab_mini_style, selected_style=tab_mini_selected_style,children=[
                                        html.Div([html.Div([dcc.Graph(id='my-3D-graph', animate=False)],
                                                                 style={'display': 'inline-block', 'width': '65%',
                                                                        }),
                                                        html.Div([
                                                            html.Div([html.Label(["Select X variable:",
                                                                                  dcc.Dropdown(id='xaxis-anim-3D',
                                                                                               multi=False,
                                                                                               placeholder="Select an option "
                                                                                                           "for X")],
                                                                                 )],
                                                                     style={
                                                                            'padding': 10}),
                                                            html.Div([html.Label(["Select Y variable:",
                                                                                  dcc.Dropdown(id='yaxis-anim-3D',
                                                                                               multi=False,
                                                                                               placeholder='Select an option '
                                                                                                           'for Y')],
                                                                                 ), ],
                                                                     style={ 
                                                                            'padding': 10}),
                                                            html.Div([html.Label(
                                                                ["Select size variable:",
                                                                 dcc.Dropdown(id='saxis-anim-3D', multi=False,
                                                                              placeholder='Select an option for size')],
                                                            )], style={
                                                                       'padding': 10}),
                                                        ],
                                                            style={'display': 'inline-block', 'width': '30%',
                                                                   'float': 'right', 'fontSize':14,'font-family':'Arial',
                                                                 'backgroundColor': '#ffffff'})
                                                        ], className='container', style={'padding':40,'backgroundColor': '#ffffff'})
                                        ]),
                                    dcc.Tab(label='4', style=tab_mini_style, selected_style=tab_mini_selected_style,
                                    children=[html.Div([html.Div([dcc.Graph(id='my-graph', animate=False)],
                                                                 style={'display': 'inline-block', 'width': '65%',
                                                                        }),

                                                        html.Div([
                                                            html.Div([html.Label(["Select X variable:",
                                                                                  dcc.Dropdown(id='xaxis-anim',
                                                                                               multi=False,
                                                                                               placeholder="Select an option "
                                                                                                           "for X")],
                                                                                 )],
                                                                     style={
                                                                            'padding': 10}),
                                                            html.Div([html.Label(["Select Y variable:",
                                                                                  dcc.Dropdown(id='yaxis-anim',
                                                                                               multi=False,
                                                                                               placeholder='Select an option '
                                                                                                           'for Y')],
                                                                                 ), ],
                                                                     style={ 
                                                                            'padding': 10}),
                                                            html.Div([html.Label(
                                                                ["Select size variable:",
                                                                 dcc.Dropdown(id='saxis-anim', multi=False,
                                                                              placeholder='Select an option for size')],
                                                            )], style={
                                                                       'padding': 10}),
                                                            html.Div([html.Label(
                                                                ["Select color variable:",
                                                                 dcc.Dropdown(id="caxis-anim", multi=False,
                                                                              placeholder='Select an option for color')],
                                                            )], style={
                                                                       'padding': 10})
                                                        ],
                                                            style={'display': 'inline-block', 'width': '30%',
                                                                   'float': 'right', 'fontSize':14,'font-family':'Arial',
                                                                 'backgroundColor': '#ffffff'})
                                                        ], className='container', style={'padding':40,'backgroundColor': '#ffffff'})]
                                                        )]
                                                        ),]),
                            dcc.Tab(label='3D Animation', style=tab_style, selected_style=tab_selected_style,
                                    children=[html.Div([
                                        html.Div([dcc.Graph(id="graph"
                                                            )],
                                                 style={"width": "65%", "display": "inline-block", }),
                                        html.Div([
                                            html.Div([html.Label(["Select X variable:",
                                                                  dcc.Dropdown(id='xaxis-3D', multi=False,
                                                                               placeholder="Select an option for X",)],
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

                                                              )],
                                            )], style={'padding': 10}),
                                            html.Div([html.Label(
                                                ["Select color variable:",
                                                 dcc.Dropdown(id="caxis-3D", multi=False,

                                                              placeholder='Select an option for color')],
                                            )], style={'padding': 10})
                                        ],
                                            style={'fontSize':14, 'fpmt-family':'Arial','display': 'inline-block', 'width': '30%', 'float':'right',
                                                   'backgroundColor': '#ffffff'})
                                        ,

                                    ], className='container', style={'backgroundColor': '#ffffff', 'padding':40})])
                        ])
                    ]),
            dcc.Tab(label='MOF Data Filtering', style=tab_style, selected_style=tab_selected_style,
                    children=[html.Div([html.Div([dash_table.DataTable(id='data-table-interact',
                                                                       editable=True,
                                                                       filter_action='native',
                                                                       sort_action='native',
                                                                       sort_mode='multi',
                                                                       # fixed_rows={'headers': True},
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
                                                            (dcc.Dropdown(id='saxis',
                                                                          placeholder="Select an option for size",
                                                                          multi=False))],
                                                           className="six columns",
                                                           style={'fontSize': 14, 'font-family': 'Arial',
                                                                  'width': '20%',
                                                                  'display': 'inline-block', 'padding': 5}
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
                                                                  })
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
                                                                  labelStyle={'display': 'inline-block'}
                                                              )]),
                                                  ], style={'display': 'inline-block', 'width': '33%'}),
                                        html.Div([html.Label(["Select Y axis scale:",
                                                              dcc.RadioItems(
                                                                  id='yaxis-type',
                                                                  options=[{'label': i, 'value': i} for i in
                                                                           ['Linear', 'Log']],
                                                                  value='Linear',
                                                                  labelStyle={'display': 'inline-block'}
                                                              )]),
                                                  ], style={'display': 'inline-block', 'width': '33%'}),
                                        html.Div([html.Label(["Select color scale:",
                                                              dcc.RadioItems(
                                                                  id='colorscale',
                                                                  options=[{'label': i, 'value': i} for i in
                                                                           ['Viridis', 'Plasma']],
                                                              )])
                                                  ], style={'display': 'inline-block', 'width': '33%', 'padding': 5}),

                                        # html.Div([
                                        #     html.Label(["Select Pressure:",
                                        #                 dcc.Slider(id='pressure-slider',
                                        #
                                        #                            ), ])
                                        # ], style={'fontSize': 14, 'font-family': 'Arial', 'height': '20%', 'padding': 15,
                                        #           'width': '90%'})
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
                                            )], style={'padding': 10}),
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
                                                    labelStyle={'display': 'inline-block'}
                                                )]),
                                                      ], style={'padding': 10}),
                                            html.Div([html.Label(["Select variable (Geometrical Property):",
                                                                  dcc.Dropdown(id='yaxis-stat',
                                                                               placeholder="Select an option for Y",
                                                                               multi=False,
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
                                            )], style={'padding': 10}),
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
                                                        labelStyle={'display': 'inline-block'}
                                                    )]),
                                                          ], style={'padding': 10}),
                                                html.Div([html.Label(["Select X variable:",
                                                                      dcc.Dropdown(id='xaxis-dist',
                                                                                   multi=False,
                                                                                   placeholder="Select an option for X"
                                                                                   )]), ],
                                                         style={'padding': 10
                                                                }),
                                                html.Div([html.Label(["Select Grouping:",
                                                                      dcc.RadioItems(
                                                                          id='dist-grouping',
                                                                          options=[{'label': i, 'value': i} for i in
                                                                                   ['None', 'MOF family']],
                                                                          value='None',
                                                                          labelStyle={'display': 'inline-block'})])
                                                          ])
                                            ], style={'fontSize': 14, 'font-family': 'Arial', 'width': '30%',
                                                  'display': 'inline-block',
                                                  'float': 'right' })

                                        ], className='container', style={'backgroundColor': '#ffffff','padding': 40}
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


# POPULATE X AXIS DROPDOWN 2D ENV ANIM
@app.callback(Output('xaxis-anim-2D', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_xaxis_dropdown_anim(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# POPULATE Y AXIS DROPDOWN 2D ENV ANIM
@app.callback(Output('yaxis-anim-2D', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_yaxis_dropdown_anim(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


@app.callback(Output('my-2D-graph', 'figure'),
              [Input('data-table-upload', 'contents'),
               Input('xaxis-anim-2D', 'value'),
               Input('yaxis-anim-2D', 'value')],
              [State('data-table-upload', 'filename')]
              )
def update_figure(contents, x, y, filename):
    df = parse_contents(contents, filename)
    return px.scatter(df, x=df[x], y=df[y], title="", animation_frame="Pressure (bar)",
                      animation_group=df.columns[0], 
                      hover_name=df.columns[0],
                      hover_data={}, template="none",
                      ).update_xaxes(showgrid=False, title=x, autorange=True, ticks='outside',
                                     showline=True, showspikes=True, spikethickness=1, spikedash='solid',
                                     mirror=True).update_yaxes(spikedash='solid',
        showgrid=False, title=y, autorange=True, ticks='outside', showspikes=True, spikethickness=1,
        showline=True, mirror=True).update_layout(
        clickmode='event+select', hovermode='closest', margin={'l': 80}, autosize=True
    ).update_traces(marker=dict(opacity=0.7, line=dict(width=0.5, color='DarkSlateGrey'),
                             ))


# POPULATE X AXIS DROPDOWN 3D ENV ANIM
@app.callback(Output('xaxis-anim-3D', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_xaxis_dropdown_anim(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# POPULATE Y AXIS DROPDOWN 3D ENV ANIM
@app.callback(Output('yaxis-anim-3D', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_yaxis_dropdown_anim(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# POPULATE S AXIS DROPDOWN 3D ENV ANIM
@app.callback(Output('saxis-anim-3D', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_saxis_dropdown_anim(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


@app.callback(Output('my-3D-graph', 'figure'),
              [Input('data-table-upload', 'contents'),
               Input('xaxis-anim-3D', 'value'),
               Input('yaxis-anim-3D', 'value'),
               Input('saxis-anim-3D', 'value')],
              [State('data-table-upload', 'filename')]
              )
def update_figure(contents, x, y, size, filename):
    df = parse_contents(contents, filename)
    return px.scatter(df, x=df[x], y=df[y], title="", animation_frame="Pressure (bar)",
                      animation_group=df.columns[0], size=df[size],
                      hover_name=df.columns[0], 
                      hover_data={}, template="none",
                      ).update_xaxes(showgrid=False, title=x, autorange=True, ticks='outside',
                                     showline=True, showspikes=True, spikethickness=1, spikedash='solid',
                                     mirror=True).update_yaxes(spikedash='solid',
        showgrid=False, title=y, autorange=True, ticks='outside', showspikes=True, spikethickness=1,
        showline=True, mirror=True).update_layout(
        clickmode='event+select', hovermode='closest', margin={'l': 80}, autosize=True
    ).update_traces(marker=dict(opacity=0.7, line=dict(width=0.5, color='DarkSlateGrey'),
                               ))


# POPULATE X AXIS DROPDOWN 4D ENV ANIM
@app.callback(Output('xaxis-anim', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_xaxis_dropdown_anim(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# POPULATE Y AXIS DROPDOWN 4D ENV ANIM
@app.callback(Output('yaxis-anim', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_yaxis_dropdown_anim(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# POPULATE C AXIS DROPDOWN 4D ENV ANIM
@app.callback(Output('caxis-anim', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_caxis_dropdown_anim(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# POPULATE S AXIS DROPDOWN 4D ENV ANIM
@app.callback(Output('saxis-anim', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_saxis_dropdown_anim(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


@app.callback(Output('my-graph', 'figure'),
              [Input('data-table-upload', 'contents'),
               Input('xaxis-anim', 'value'),
               Input('yaxis-anim', 'value'),
               Input('caxis-anim', 'value'),
               Input('saxis-anim', 'value')],
              [State('data-table-upload', 'filename')]
              )
def update_figure(contents, x, y, color, size, filename):
    df = parse_contents(contents, filename)
    return px.scatter(df, x=df[x], y=df[y], title="", animation_frame="Pressure (bar)",
                      animation_group=df.columns[0], size=df[size], color=df[color],
                      hover_name=df.columns[0], color_continuous_scale='Viridis',
                      hover_data={}, template="none",
                      ).update_xaxes(showgrid=False, title=x, autorange=True, ticks='outside',
                                     showline=True, showspikes=True, spikethickness=1, spikedash='solid',
                                     mirror=True).update_yaxes(spikedash='solid',
        showgrid=False, title=y, autorange=True, ticks='outside', showspikes=True, spikethickness=1,
        showline=True, mirror=True).update_layout(
        clickmode='event+select', hovermode='closest', margin={'l': 80}, autosize=True
    ).update_traces(marker=dict(opacity=0.7, showscale=True, line=dict(width=0.5, color='DarkSlateGrey'),
                                colorbar=dict(title=color)))


# POPULATE X AXIS DROPDOWN 3D
@app.callback(Output('xaxis-3D', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_xaxis_dropdown(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# POPULATE Y AXIS DROPDOWN 3D
@app.callback(Output('yaxis-3D', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_yaxis_dropdown(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# POPULATE Z AXIS DROPDOWN 3D
@app.callback(Output('zaxis-3D', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_zaxis_dropdown(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# POPULATE S AXIS DROPDOWN 3D
@app.callback(Output('saxis-3D', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_saxis_dropdown(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# POPULATE C AXIS DROPDOWN 3D
@app.callback(Output('caxis-3D', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_caxis_dropdown(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


@app.callback(Output("graph", "figure"),
              [Input('xaxis-3D', "value"),
               Input('yaxis-3D', 'value'),
               Input('zaxis-3D', 'value'),
               Input('caxis-3D', 'value'),
               Input('saxis-3D', 'value'),
               Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def make_figure(x, y, z, color, size, contents, filename):
    df = parse_contents(contents, filename)
    if x and y and z and color and size is None:
        return dash.no_update
    return px.scatter_3d(df, x=df[x], y=df[y], z=df[z], title="", animation_frame="Pressure (bar)",
                         animation_group=df.columns[0], size=df[size], color=df[color],
                         hover_name=df.columns[0], color_continuous_scale='Viridis',
                         hover_data={}, template="plotly_white",
                         ).update_xaxes(showgrid=False, title=x, autorange=True).update_yaxes(
        showgrid=False, title=y, autorange=True).update_layout(
        clickmode='event+select', hovermode='closest', margin={'l': 50, 'b': 80, 't': 50, 'r': 10}, autosize=True
    ).update_traces(marker=dict(opacity=0.7, showscale=True, line=dict(width=0.5, color='#3d3d3d'),
                                colorbar=dict(title=color)))


# POPULATE X AXIS DROPDOWN SCATTER
@app.callback(Output('xaxis', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_xaxis_dropdown(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# POPULATE Y AXIS DROPDOWN SCATTER
@app.callback(Output('yaxis', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_yaxis_dropdown(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# POPULATE C AXIS DROPDOWN SCATTER
@app.callback(Output('caxis', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_caxis_dropdown(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# POPULATE S AXIS DROPDOWN SCATTER
@app.callback(Output('saxis', 'options'),
              [Input('data-table-upload', 'contents')],
              [State('data-table-upload', 'filename')])
def populate_saxis_dropdown(contents, filename):
    df = parse_contents(contents, filename)
    return [{'label': i, 'value': i} for i in df.columns]


# POPULATE PRESSURE SLIDER SCATTER
# @app.callback([Output('pressure-slider', 'min'),
#                Output('pressure-slider', 'max'),
#                Output('pressure-slider', 'value'),
#                Output('pressure-slider', 'marks')],
#               [Input('data-table-upload', 'contents')],
#               [State('data-table-upload', 'filename')])
# def populate_pressure_slider(contents, filename):
#     df = parse_contents(contents, filename)
#     min = df['Pressure (bar)'].min(),
#     max = df['Pressure (bar)'].max(),
#     value = df['Pressure (bar)'].max(),
#     marks = {str(pressure): str(pressure) for pressure in df['Pressure (bar)'].unique()}
#     return min, max, value, marks


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
    columns = [{"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns]
    return data, columns


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
                                                       colorbar=dict(title=marker_color),
                                                       colorscale="Viridis" if colorscale == 'Viridis' else "Plasma"),
                                           text=dff[df.columns[0]],
                                           hoverinfo=['x', 'y', 'text', 'name'],
                                           # hovertemplate=
                                           # "<b>%{text}</b><br><br>" +
                                           # "%{yaxis_name}: %{y:.0f}<br>" +
                                           # "X Variable: %{x:. }<br>"
                                           # "S Variable : %{marker.size:. }<br>" +
                                           # "C Variable: %{marker.color:.}"
                                           # "<extra></extra>",
                                           )],
                                'layout': go.Layout(
                                    xaxis={'title': xaxis_name, 'autorange': True,
                                           'mirror': True,
                                           'ticks': 'outside',
                                           'showline': True,
                                           'showspikes': True,
                                           'type': 'linear' if xaxis_type == 'Linear' else 'log'
                                           },
                                    yaxis={'title': yaxis_name, 'autorange': True,
                                           'mirror': True,
                                           'ticks': 'outside',
                                           'showline': True,
                                           'showspikes': True,
                                           'type': 'linear' if yaxis_type == 'Linear' else 'log'
                                           },
                                    title="",
                                    template="simple_white",
                                    margin={'l': 50, 'b': 60, 't': 70, 'r': 50},
                                    hovermode='closest',
                                ),

                            },
                            )
                  ], style={'textAlign': 'center', 'padding': 25, 'width': '50%', 'height': '100%',
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


@app.callback(Output('violin-plot', 'figure'),
              [
                  Input('yaxis-stat', 'value'),
                  Input('percentile-type', 'value'),
                  Input('data-set', 'value'),
                  Input('data-table-upload', 'contents')
              ],
              [State('data-table-upload', 'filename')]
              )
def update_graph_stat(yaxis_name, percentile_type, data_set, contents, filename):
    df = parse_contents(contents, filename)
    traces = []
    pressure_set = set(df['Pressure (bar)'])
    pressure_list = sorted(list(pressure_set))
    if data_set is None:
        return dash.no_update
    if percentile_type == 'All structures':
        data = df
    elif percentile_type == 'Top 1% of structures':
        data = df[df[data_set] > df[data_set].quantile(0.99)]
    elif percentile_type == 'Top 5% of structures':
        data = df[df[data_set] > df[data_set].quantile(0.95)]
    elif percentile_type == 'Top 10% of structures':
        data = df[df[data_set] > df[data_set].quantile(0.9)]
    if yaxis_name is None:
        return dash.no_update
    for pressure in pressure_list:
        traces.append(go.Violin(y=data[data['Pressure (bar)'] == pressure][yaxis_name], name=pressure,
                                marker={'size': 4}, box_visible=True, opacity=0.6, meanline_visible=True,
                                points='all', text=data[df.columns[0]],
                                hovertemplate=
                                "<b>%{text}</b><br><br>" +
                                "Variable: %{y:.0f}<br>"
                                "Pressure: %{x:. bar}<br>"
                                ))
    return {'data': traces

        , 'layout': go.Layout(
            title=f"<b> Pressure (bar) against {''.join(str(i) for i in yaxis_name)} "
            ,
            xaxis=dict(rangeslider=dict(visible=True), title='Pressure (bar)'),
            yaxis={'title': yaxis_name},
            font=dict(
                family="Arial",
            ),
            margin={'l': 50, 'b': 5, 't': 50, 'r': 50},
            hovermode='closest',
        )
            }


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


@app.callback(Output("dist-plot", "figure"),
              [Input('xaxis-dist', "value"),
               Input('dist-grouping', 'value'),
               Input('data-set-dist', 'value'),
               Input('percentile-type-dist', 'value'),
               Input('data-table-upload', 'contents'), ],
              [State('data-table-upload', 'filename')])
def make_figure(x, dist_type, data_set, percentile_type, contents, filename):
    df = parse_contents(contents, filename)
    if x is None:
        return dash.no_update
    if data_set is None:
        return dash.no_update
    if percentile_type == 'All structures':
        data = df
    elif percentile_type == 'Top 1% of structures':
        data = df[df[data_set] > df[data_set].quantile(0.99)]
    elif percentile_type == 'Top 5% of structures':
        data = df[df[data_set] > df[data_set].quantile(0.95)]
    elif percentile_type == 'Top 10% of structures':
        data = df[df[data_set] > df[data_set].quantile(0.9)]
    return px.histogram(data, x=data[x], marginal="rug",
                        color="MOF family" if dist_type == 'MOF family' else None,
                        animation_frame="Pressure (bar)",
                        hover_data=df.columns, hover_name=df.columns[0], template="none"
                        ).update_xaxes(showgrid=False, title=x, autorange=True, ticks='outside',
                                       mirror=True, showline=True,
                                       ).update_yaxes(title='', showgrid=False, ticks='outside',
                                                      mirror=True, autorange=True, showline=True).update_layout(
        hovermode='closest', margin={'l': 50, 'b': 80, 't': 50, 'r': 10}, autosize=True
    ).update_traces(marker=dict(opacity=0.7, line=dict(width=0.5, color='DarkSlateGrey'),
                                )).update_layout(
        title=f"<b> Distribution of Structures against {''.join(str(i) for i in x)}", font=dict(
                family="Arial",
            ),)


if __name__ == '__main__':
    app.run_server()
