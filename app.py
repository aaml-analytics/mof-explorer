import base64
import io
from urllib.parse import quote as urlquote
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.exceptions import PreventUpdate
from dash_table.Format import Format, Scheme
import pandas as pd
import plotly.graph_objs as go
from textwrap import dedent as d
import plotly.express as px
import json
import textwrap
import dash_bootstrap_components as dbc
import numpy as np
from natsort import natsorted

pd.options.mode.chained_assignment = None
# CREATE DASH APP
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://codepen.io/chriddyp/pen/bWLwgP.css',
                                      "https://codepen.io/sutharson/pen/zYvEVPW.css",
                                      "https://fonts.googleapis.com/css2?family=Raleway&display=swap"])
server = app.server

# READ FILE
df = pd.read_csv(
    'https://raw.githubusercontent.com/aaml-analytics/mof-explorer/master/sample-data/allmixtures5barbinned_url_V2_vol_uptake_removed.csv')
data_frame = df = pd.read_csv(
    'https://raw.githubusercontent.com/aaml-analytics/mof-explorer/master/sample-data/allmixtures5barbinned_url_V2_vol_uptake_removed.csv')
# df = df.round({'MOF Density (g/cm3)': 3, 'Helium Void Fraction (-)': 3, 'Surface Area (m2/g)': 3,
#                'Free Volume (cm3/g)': 3, 'Pore Limiting Diameter (A)': 3, 'Large Cavity Diameter (A)': 3,
#                'Ratio LCD/PLD (-)': 3}
#               )
df = df.rename(columns={'Pore limiting diameter (A)': 'Pore limiting diameter (Å)',
                        'Largest cavity diameter (A)': 'Largest cavity diameter (Å)',
                        'Pore Limiting Diameter (A)': 'Pore Limiting Diameter (Å)',
                        'Largest Cavity Diameter (A)': 'Largest Cavity Diameter (Å)'})

data_frame = data_frame.rename(columns={'Pore limiting diameter (A)': 'Pore limiting diameter (Å)',
                                        'Largest cavity diameter (A)': 'Largest cavity diameter (Å)',
                                        'Pore limiting diameter (A)': 'Pore limiting diameter (Å)',
                                        'Largest cavity diameter (A)': 'Largest cavity diameter (Å)'})

df_obj = df.select_dtypes(exclude=['object'])
df_stat = df.select_dtypes(exclude=['int', 'float'])
df_stat = df_stat.drop(['NAME'], axis=1)
df_stat2 = df_stat.drop(["URL"], axis=1)
df_explorer = df.iloc[:, np.r_[0:55]]
data_frame_explorer = data_frame.iloc[:, np.r_[0:55]]
data_frame_explorer_url = data_frame.iloc[:, np.r_[0:55, 70]]
data_frame_explorer_all = data_frame_explorer
data_frame_explorer_all = data_frame_explorer_all.reset_index(drop=True)
data_frame_explorer_y = data_frame_explorer_all.drop(['NAME'], axis=1)
data_frame_explorer_color = data_frame_explorer_y.drop(['Porosity'], axis=1)
dff_explorer_all = df_explorer.drop(['NAME'], axis=1)
dff_explorer_all_url = df.iloc[:, np.r_[0:55, 70]]
dff_explorer_all = dff_explorer_all.reset_index(drop=True)
df_explorer_y = dff_explorer_all
df_explorer_color = df_explorer_y.drop(['Porosity'], axis=1)
# PREDEFINED TAB STYLES
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
tabs_styles = {'height': '40px', 'font-family': 'Raleway', 'fontSize': 14}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_mini_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'width': '150px',
    'color': '#000000',
    'fontColor': '#000000',
}

tab_mini_selected_style = {
    'borderTop': '3px solid #333333',
    'borderBottom': '1px solid #d6d6d6 ',
    'backgroundColor': '#333333',
    'color': '#ffffff',
    # 'fontColor': '#004a4a',
    'fontWeight': 'bold',
    'padding': '6px',
    'width': '150px'
}

tab_selected_style = {
    'borderTop': '3px solid #333333',
    'borderBottom': '1px solid #d6d6d6 ',
    'backgroundColor': '#f6f6f6',
    'color': '#333333',
    # 'fontColor': '#004a4a',
    'fontWeight': 'bold',
    'padding': '6px'
}

# SUPERSCRIPT NOTATION
SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")

# APP ABOUT DESCRIPTION
MOF_tool_about = textwrap.wrap(' These tools aim to provide a reproducible and consistent data visualisation platform '
                               'where experimental and computational researchers can use big data and statistical '
                               'analysis to find the best materials for specific applications.',
                               width=50)
twoD_threeD_about = textwrap.wrap(' The 2D Animated MOF Explorer and 3D Animated MOF Explorer provides a 2, 3, 4 and '
                                  '5-Dimensional variable environment to explore specific structures '
                                  'against a discrete data variable (animation frame) of their choice to find the best '
                                  "materials for the user's applications.", width=50)
MOF_data_filter = textwrap.wrap(' Using the sorting and filtering data table, users can filter variables '
                                'from their dataset to '
                                "produce plots of their preference. All variables in the user's data set can be sorted,"
                                ' filtered and deleted in the interactive data table. The arguments that the data table '
                                'can take are '
                                'specified '
                                'in the manual. Users can also use the color bar slider to specify the range of the '
                                'color bar slider. The size reference slider and size min slider can be used to alter'
                                ' marker size in accordance to the selected size variable. '
                                'After filtering there are options to choose a logarithmic or linear '
                                'axis scale, and choose a color scale of choice from the Viridis color palette.'
                                , width=50)
MOF_stat_analysis = textwrap.wrap('All structures or top-performing structures (1%, 5% or 10% of all structures) '
                                  'can be analysed in accordance with a set variable decided by the user e.g. '
                                  'Deliverable Capacity. In the violin plot, geometric properties can then be '
                                  'analysed against a discrete data variable (X-axis) to determine Q1, Q3, IQR, '
                                  'mean, median, maximum and'
                                  ' minimum points for a dataset of the users choice, alongside the distribution of '
                                  'MOFs in said violin plot. In the distribution plot, the number of structures against '
                                  "a variable in the user's data frame can be analysed to determine the spread of"
                                  "structures in the user's data. The distribution can be further filtered by MOF "
                                  'families (if the user has uploaded this information in their data frame). '
                                  'An animation feature is also available to view these frames in accordance'
                                  ' with a discrete data variable of the users choice.', width=50, )
MOF_GH_1 = textwrap.wrap(' The app manual, which explains features of the', width=50)
MOF_GH_1_5 = textwrap.wrap(' tool, can be found', width=50)
MOF_GH_2 = textwrap.wrap(" Since data is already uploaded on this particular app, please ignore the tab "
                         "'Data File Requirements'"
                         " in the manual.", width=50)
MOF_GH = textwrap.wrap(" to explore AAML's repository and deploy your own tool"
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
                       'color': 'white', 'font-family': 'Raleway'}),
        html.H1("...", style={'fontColor': '#3c3c3c', 'fontSize': 6})
    ], style={'backgroundColor': '#333333'}),
    html.Div([
        dcc.Tabs([
            dcc.Tab(label='About', style=tab_style, selected_style=tab_selected_style,
                    children=[html.Div([html.H2(" What are AAML's MOF Data Visualisation tools?",
                                                style={'fontSize': 18, 'font-family': 'Raleway', 'font-weight': 'bold'
                                                       }),
                                        html.Div([' '.join(MOF_tool_about)]
                                                 , style={'font-family': 'Raleway'}),

                                        html.H2([" MOF Data Filtering Environment"], style={'fontSize': 18,
                                                                                            'font-weight': 'bold',
                                                                                            'font-family': 'Raleway'}),
                                        html.Div([' '.join(MOF_data_filter)], style={'font-family': 'Raleway', }),
                                        html.H2([" 2D and 3D Animation Environment"],
                                                style={'fontSize': 18,
                                                       'font-family': 'Raleway', 'font-weight': 'bold'}),
                                        html.Div([' '.join(twoD_threeD_about)], style={'font-family': 'Raleway'}),
                                        html.H2([" MOF Statistical Analysis Environment"],
                                                style={'fontSize': 18, 'font-weight': 'bold',
                                                       'font-family': 'Raleway'}),
                                        html.Div([' '.join(MOF_stat_analysis)], style={'font-family': 'Raleway'}),
                                        html.Div([
                                            html.Div([''.join(MOF_GH_1), ''.join(MOF_GH_1_5)],
                                                     style={'display': 'inline-block',
                                                            'font-family': 'Raleway'}),
                                            html.Plaintext(
                                                [html.A(' here. ',
                                                        href='https://aaml-analytics.github.io/mof-explorer/')],
                                                style={'display': 'inline-block', 'font-family': 'Raleway'}),
                                            html.Div([' '.join(MOF_GH_2)], style={'display': 'inline-block',
                                                                                  'font-family': 'Raleway'})
                                        ]),
                                        # ADD LINK
                                        html.Div([html.Plaintext(
                                            [' Click ', html.A('here ',
                                                               href='https://github.com/aaml-analytics/mof-explorer')],
                                            style={'display': 'inline-block', 'font-family': 'Raleway'}),
                                            html.Div([' '.join(MOF_GH)], style={'display': 'inline-block',
                                                                                'font-family': 'Raleway'}),
                                            html.Img(
                                                src='https://raw.githubusercontent.com/aaml-analytics/mof'
                                                    '-explorer/master/github.png',
                                                height='40', width='40',
                                                style={'display': 'inline-block', 'float': "right"
                                                       })
                                        ]
                                            , style={'display': 'inline-block'}),

                                        ], style={'backgroundColor': '#ffffff'}
                                       )]),
            dcc.Tab(label='MOF Explorer', style=tab_style, selected_style=tab_selected_style,
                    children=[html.Div([html.Div([dash_table.DataTable(id='data-table-interact',
                                                                       data=data_frame_explorer_url.to_dict('records'),
                                                                       columns=[{"name": i, "id": i, "deletable": True,
                                                                                 "selectable": True, 'type': 'numeric',
                                                                                 'format': Format(precision=3,
                                                                                                  scheme=Scheme.fixed
                                                                                                  )
                                                                                 }
                                                                                for i in data_frame_explorer_url.columns
                                                                                ],
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
                                                                           'minWidth': '0px', 'maxWidth': '450px',
                                                                           'whiteSpace': 'normal',
                                                                       },
                                                                       ),
                                                  html.Div(id='data-table-container'), ], style={'padding': 15}),

                                        html.Div([html.Div([
                                            html.Label(["Select X variable:",
                                                        (dcc.Dropdown(id='xaxis', placeholder="Select an option for X",
                                                                      multi=False,
                                                                      options=[{'label': i, 'value': i} for i in
                                                                               data_frame_explorer_color.columns]))
                                                        ], className="six columns",
                                                       style={'fontSize': 14, 'font-family': 'Raleway',
                                                              'width': '20%', 'display': 'inline-block', 'padding': 5,
                                                              })
                                        ]),
                                            html.Div([
                                                html.Label(["Select Y variable:",
                                                            (dcc.Dropdown(id='yaxis',
                                                                          placeholder="Select an option for Y",
                                                                          multi=False,
                                                                          options=[{'label': i, 'value': i} for i in
                                                                                   data_frame_explorer_color.columns]))
                                                            ], className="six columns",
                                                           style={'fontSize': 14, 'font-family': 'Raleway',
                                                                  'width': '20%',
                                                                  'display': 'inline-block', 'padding': 5
                                                                  })
                                            ]),
                                            html.Div([
                                                html.Label(["Select size variable:",
                                                            dcc.Dropdown(id='saxis',
                                                                         placeholder="Select an option for size",
                                                                         multi=False,
                                                                         options=[{'label': i, 'value': i} for i in
                                                                                  data_frame_explorer_color.columns]),
                                                            ],
                                                           className="six columns",
                                                           style={'fontSize': 14, 'font-family': 'Raleway',
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
                                                                          multi=False,
                                                                          options=[{'label': i, 'value': i} for i in
                                                                                   data_frame_explorer_color.columns]))
                                                            ], className="six columns",
                                                           style={'fontSize': 14, 'font-family': 'Raleway',
                                                                  'width': '20%',
                                                                  'padding': 5
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
                                            html.Div([
                                                html.Div([
                                                    html.Label("Input x-axis range:"),
                                                    html.Label([
                                                        html.Div(id='size-output-container-filter-xaxis')]),
                                                    html.Div([dcc.Input(id='xaxis-input-min', type='number'),
                                                              ], style={'display': 'inline-block'}),
                                                    html.Label("Minimum"),
                                                    html.Div([dcc.Input(id='xaxis-input-max', type='number'),
                                                              ], style={'display': 'inline-block'}),
                                                    html.Label("Maximum"),
                                                    html.Button('Submit', id='button-xaxis'),
                                                    html.Div(id='output-container-button-xaxis')
                                                ], style={'width': '28%', 'display': 'inline-block'}),
                                                html.Div([
                                                    html.Label("Input y-axis range:"),
                                                    html.Label([
                                                        html.Div(id='size-output-container-filter-yaxis')]),
                                                    html.Div([dcc.Input(id='yaxis-input-min', type='number'),
                                                              ], style={'display': 'inline-block'}),
                                                    html.Label("Minimum"),
                                                    html.Div([dcc.Input(id='yaxis-input-max', type='number'),
                                                              ], style={'display': 'inline-block'}),
                                                    html.Label("Maximum"),
                                                    html.Button('Submit', id='button-yaxis'),
                                                    html.Div(id='output-container-button-yaxis')
                                                ], style={'width': '28%', 'display': 'inline-block'}),
                                                html.Div([
                                                    html.Label("Input color bar range:"),
                                                    html.Label([
                                                        html.Div(id='size-output-container-filter-color')]),
                                                    html.Div([dcc.Input(id='color-input-min', type='number'),
                                                              ], style={'display': 'inline-block'}),
                                                    html.Label("Minimum"),
                                                    html.Div([dcc.Input(id='color-input-max', type='number'),
                                                              ], style={'display': 'inline-block'}),
                                                    html.Label("Maximum"),
                                                    html.Button('Submit', id='button'),
                                                    html.Div(id='output-container-button')
                                                ], style={'width': '28%', 'display': 'inline-block'}),
                                                # html.Div([
                                                #     html.Div([html.Label("Minimum")], style={}),
                                                #     html.P(),
                                                #     html.Div(["Maximum"], style={}),
                                                # ], style={'width': '15%', 'display': 'inline-block'}),
                                            ], style={})
                                        ],
                                            style={'padding-left': '15%', 'padding-right': '5%'}
                                        ),
                                        html.Div([html.Div([html.Label(["Select X axis scale:",
                                                                        dcc.RadioItems(
                                                                            id='xaxis-type',
                                                                            options=[{'label': i, 'value': i} for i in
                                                                                     ['Linear', 'Log']],
                                                                            value='Linear',
                                                                            labelStyle={'display': 'inline-block', }
                                                                        )]),
                                                            ], style={'padding-left': '45%', }),
                                                  html.Div([html.Label(["Select Y axis scale:",
                                                                        dcc.RadioItems(
                                                                            id='yaxis-type',
                                                                            options=[{'label': i, 'value': i} for i in
                                                                                     ['Linear', 'Log']],
                                                                            value='Linear',
                                                                            labelStyle={'display': 'inline-block',
                                                                                        }
                                                                        )]),
                                                            ], style={'padding-left': '45%', }),
                                                  html.Div([html.Label(["Select color scale:",
                                                                        dcc.RadioItems(
                                                                            id='colorscale',
                                                                            options=[{'label': i, 'value': i} for i in
                                                                                     ['Viridis', 'Plasma']],
                                                                            value='Plasma',
                                                                            labelStyle={'display': 'inline-block',
                                                                                        }
                                                                        )]),
                                                            ], style={'padding-left': '45%', }),
                                                  html.Div([html.Label(["Size range:",
                                                                        html.Div(id='size-output-container-filter')])
                                                            ], style={'padding-left': '45%', }
                                                           ), ], style={'display': 'inline-block', 'width': '35%',
                                                                        }),
                                        html.Div([html.Div(
                                            [
                                                html.Label(
                                                    [
                                                        "Select size variable reference:",
                                                        dcc.Slider(
                                                            id='sizebar-slider-data-table',
                                                            min=1,
                                                            max=15,
                                                            value=7.5,
                                                            step=0.1
                                                        ),
                                                        html.Div(
                                                            id='slider-output-data-table-size-container')
                                                    ]
                                                )
                                            ],
                                            style={
                                                'fontSize': 14,
                                                # 'width': '40%',
                                                'font-family': 'Raleway',
                                                'padding': 15,
                                            }
                                        ),
                                            html.Div(
                                                [
                                                    html.Label([
                                                        "Select minimum size value:",
                                                        dcc.Slider(
                                                            id='sizebar-min-slider-data-table',
                                                            min=1,
                                                            max=15,
                                                            value=7.5,
                                                            step=0.1
                                                        ),
                                                        html.Div(
                                                            id='slider-output-data-table-size-min-container')
                                                    ])
                                                ],
                                                style={
                                                    'fontSize': 14,
                                                    # 'width': '40%',
                                                    'font-family': 'Raleway',
                                                    'padding': 15,
                                                }
                                            ),
                                        ], style={'display': 'inline-block', 'width': '45%'}),
                                        html.Div(
                                            [html.Label("Once you have selected the dropdowns and a plot has appeared,"
                                                        " click a data point to ")], style={'display': 'inline-block',
                                                                                            'padding-left': '14%'}),
                                        html.Div([html.A(children=' access the MOF structure in the CCDC', id='link',
                                                         href='https://www.ccdc.cam.ac.uk/structures/',
                                                         target='_blank'),
                                                  ], style={'padding-left': '0.5%', 'display': 'inline-block'}),
                                        app.css.append_css({
                                            'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
                                        })
                                        ], style={'backgroundColor': '#ffffff'})]
                    ),
            dcc.Tab(label='MOF Explorer Animation', style=tab_style, selected_style=tab_selected_style,
                    children=[
                        dcc.Tabs(id='sub-tabs1', style=tabs_styles, children=[
                            dcc.Tab(label='2D Animation', style=tab_style, selected_style=tab_selected_style,
                                    children=[dcc.Tabs(id='subsub-tabs', style=tabs_styles,
                                                       children=[dcc.Tab(label='2 Variables', style=tab_mini_style,
                                                                         selected_style=tab_mini_selected_style,
                                                                         children=[
                                                                             html.Div([html.Div([dcc.Graph(
                                                                                 id='my-2D-graph', animate=False)],
                                                                                 style={
                                                                                     'display': 'inline-block',
                                                                                     'width': '58%',
                                                                                 }),
                                                                                 html.Div([
                                                                                     html.Div([html.Label(
                                                                                         ["Select X variable:",
                                                                                          dcc.Dropdown(
                                                                                              id='xaxis-anim-2D',
                                                                                              multi=False,
                                                                                              placeholder="Select an option "
                                                                                                          "for X",
                                                                                              options=[{'label': i,
                                                                                                        'value': i} for
                                                                                                       i in
                                                                                                       dff_explorer_all.columns])],
                                                                                     )],
                                                                                         style={}),
                                                                                     html.Div([html.Label(
                                                                                         ["Select Y variable:",
                                                                                          dcc.Dropdown(
                                                                                              id='yaxis-anim-2D',
                                                                                              multi=False,
                                                                                              placeholder='Select an option '
                                                                                                          'for Y',
                                                                                              options=[{'label': i,
                                                                                                        'value': i} for
                                                                                                       i in
                                                                                                       dff_explorer_all.columns])],
                                                                                     ), ],
                                                                                         style={}),
                                                                                     html.Div([
                                                                                         html.Label(
                                                                                             "Input x-axis range:"),
                                                                                         html.Label([
                                                                                             html.Div(
                                                                                                 id='size-container-filter-xaxis-2D')]),
                                                                                         html.Div([dcc.Input(
                                                                                             id='xaxis-input-min-2D',
                                                                                             type='number'),
                                                                                             html.Label(
                                                                                                 "Minimum"),
                                                                                         ], style={
                                                                                             'display': 'table-cell',
                                                                                         }),
                                                                                         html.Div([dcc.Input(
                                                                                             id='xaxis-input-max-2D',
                                                                                             type='number'),
                                                                                             html.Label(
                                                                                                 "Maximum")],
                                                                                             style={
                                                                                                 'display': 'table-cell', }),
                                                                                         html.Button('Submit',
                                                                                                     id='button-xaxis-2D'),
                                                                                         html.Div(
                                                                                             id='output-container-button-xaxis-2D')
                                                                                     ], style={}),
                                                                                     html.Div([
                                                                                         html.Label(
                                                                                             "Input y-axis range:"),
                                                                                         html.Label([
                                                                                             html.Div(
                                                                                                 id='size-container-filter-yaxis-2D')]),
                                                                                         html.Div([dcc.Input(
                                                                                             id='yaxis-input-min-2D',
                                                                                             type='number'),
                                                                                             html.Label(
                                                                                                 "Minimum"),
                                                                                         ], style={
                                                                                             'display': 'table-cell', }),
                                                                                         html.Div([dcc.Input(
                                                                                             id='yaxis-input-max-2D',
                                                                                             type='number'),
                                                                                             html.Label(
                                                                                                 "Maximum")],
                                                                                             style={
                                                                                                 'display': 'table-cell'}),
                                                                                         html.Button('Submit',
                                                                                                     id='button-yaxis-2D'),
                                                                                         html.Div(
                                                                                             id='output-container-button-yaxis-2D')
                                                                                     ], style={}),
                                                                                     html.Div([html.Label(
                                                                                         "Once you have selected the dropdowns and a plot has appeared,"
                                                                                         " click a data point to ")],
                                                                                         style={'padding-left': '2%',
                                                                                                'display': 'inline-block'}),
                                                                                     html.Div([html.A(
                                                                                         children='access the MOF structure in the CCDC',
                                                                                         id='link-2d',
                                                                                         href='https://www.ccdc.cam.ac.uk/structures/',
                                                                                         target='_blank'),
                                                                                     ], style={
                                                                                         'padding-left': '2%',
                                                                                         'display': 'inline-block'}),
                                                                                 ],
                                                                                     style={
                                                                                         'display': 'inline-block',
                                                                                         'width': '34%',
                                                                                         'float': 'right',
                                                                                         'fontSize': 14,
                                                                                         'font-family': 'Raleway',
                                                                                         'backgroundColor': '#ffffff'})
                                                                             ], className='container',
                                                                                 style={'padding': 20,
                                                                                        'backgroundColor': '#ffffff'})
                                                                         ]),
                                                                 dcc.Tab(label='3 Variables', style=tab_mini_style,
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
                                                                                                     'width': '57%',
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
                                                                                                                         placeholder="Select an option for X",
                                                                                                                         options=[
                                                                                                                             {
                                                                                                                                 'label': i,
                                                                                                                                 'value': i}
                                                                                                                             for
                                                                                                                             i
                                                                                                                             in
                                                                                                                             dff_explorer_all.columns])
                                                                                                                 ],
                                                                                                             )
                                                                                                         ],
                                                                                                         style={}
                                                                                                     ),
                                                                                                     html.Div(
                                                                                                         [
                                                                                                             html.Label(
                                                                                                                 [
                                                                                                                     "Select Y variable:",
                                                                                                                     dcc.Dropdown(
                                                                                                                         id='yaxis-anim-3D',
                                                                                                                         multi=False,
                                                                                                                         placeholder='Select an option for Y',
                                                                                                                         options=[
                                                                                                                             {
                                                                                                                                 'label': i,
                                                                                                                                 'value': i}
                                                                                                                             for
                                                                                                                             i
                                                                                                                             in
                                                                                                                             dff_explorer_all.columns]
                                                                                                                     )
                                                                                                                 ],
                                                                                                             ),
                                                                                                         ],
                                                                                                         style={}
                                                                                                     ),
                                                                                                     html.Div(
                                                                                                         [
                                                                                                             html.Label(
                                                                                                                 [
                                                                                                                     "Select color variable:",
                                                                                                                     dcc.Dropdown(
                                                                                                                         id='caxis-anim-3D',
                                                                                                                         multi=False,
                                                                                                                         placeholder='Select an option for color',
                                                                                                                         options=[
                                                                                                                             {
                                                                                                                                 'label': i,
                                                                                                                                 'value': i}
                                                                                                                             for
                                                                                                                             i
                                                                                                                             in
                                                                                                                             dff_explorer_all.columns])
                                                                                                                 ],
                                                                                                             )
                                                                                                         ],
                                                                                                         style={}
                                                                                                     ),
                                                                                                     html.Div([
                                                                                                         html.Label(
                                                                                                             "Input x-axis range:"),
                                                                                                         html.Label([
                                                                                                             html.Div(
                                                                                                                 id='size-container-filter-xaxis-3D')]),
                                                                                                         html.Div(
                                                                                                             [dcc.Input(
                                                                                                                 id='xaxis-input-min-3D',
                                                                                                                 type='number'),
                                                                                                                 html.Label(
                                                                                                                     "Minimum"),
                                                                                                             ], style={
                                                                                                                 'display': 'table-cell',
                                                                                                             }),
                                                                                                         html.Div(
                                                                                                             [dcc.Input(
                                                                                                                 id='xaxis-input-max-3D',
                                                                                                                 type='number'),
                                                                                                                 html.Label(
                                                                                                                     "Maximum")],
                                                                                                             style={
                                                                                                                 'display': 'table-cell', }),
                                                                                                         html.Button(
                                                                                                             'Submit',
                                                                                                             id='button-xaxis-3D'),
                                                                                                         html.Div(
                                                                                                             id='output-container-button-xaxis-3D')
                                                                                                     ], style={}),
                                                                                                     html.Div([
                                                                                                         html.Label(
                                                                                                             "Input y-axis range:"),
                                                                                                         html.Label([
                                                                                                             html.Div(
                                                                                                                 id='size-container-filter-yaxis-3D')]),
                                                                                                         html.Div(
                                                                                                             [dcc.Input(
                                                                                                                 id='yaxis-input-min-3D',
                                                                                                                 type='number'),
                                                                                                                 html.Label(
                                                                                                                     "Minimum"),
                                                                                                             ], style={
                                                                                                                 'display': 'table-cell', }),
                                                                                                         html.Div(
                                                                                                             [dcc.Input(
                                                                                                                 id='yaxis-input-max-3D',
                                                                                                                 type='number'),
                                                                                                                 html.Label(
                                                                                                                     "Maximum")],
                                                                                                             style={
                                                                                                                 'display': 'table-cell'}),
                                                                                                         html.Button(
                                                                                                             'Submit',
                                                                                                             id='button-yaxis-3D'),
                                                                                                         html.Div(
                                                                                                             id='output-container-button-yaxis-3D')
                                                                                                     ], style={}),
                                                                                                     html.Div([
                                                                                                         html.Label(
                                                                                                             "Input color bar range:"),
                                                                                                         html.Label([
                                                                                                             html.Div(
                                                                                                                 id='size-container-filter-color-3D')]),
                                                                                                         html.Div(
                                                                                                             [dcc.Input(
                                                                                                                 id='color-input-min-3D',
                                                                                                                 type='number'),
                                                                                                                 html.Label(
                                                                                                                     "Minimum"),
                                                                                                             ], style={
                                                                                                                 'display': 'table-cell'}),
                                                                                                         html.Div(
                                                                                                             [dcc.Input(
                                                                                                                 id='color-input-max-3D',
                                                                                                                 type='number'),
                                                                                                                 html.Label(
                                                                                                                     "Maximum")],
                                                                                                             style={
                                                                                                                 'display': 'table-cell'}),
                                                                                                         html.Button(
                                                                                                             'Submit',
                                                                                                             id='button-color-3D'),
                                                                                                         html.Div(
                                                                                                             id='output-container-button-color-3D')
                                                                                                     ], style={}),
                                                                                                     html.Div(
                                                                                                         [html.Label(
                                                                                                             "Once you have selected the dropdowns and a plot has appeared,"
                                                                                                             " click a data point to ")],
                                                                                                         style={
                                                                                                             'padding-left': '2%',
                                                                                                             'display': 'inline-block'}),
                                                                                                     html.Div([html.A(
                                                                                                         children=' access the MOF structure in the CCDC',
                                                                                                         id='link-3d',
                                                                                                         href='https://www.ccdc.cam.ac.uk/structures/',
                                                                                                         target='_blank'),
                                                                                                     ], style={
                                                                                                         'padding-left': '2%',
                                                                                                         'display': 'inline-block'}),
                                                                                                 ],
                                                                                                 style={
                                                                                                     'display': 'inline-block',
                                                                                                     'width': '34%',
                                                                                                     'float': 'right',
                                                                                                     'fontSize': 14,
                                                                                                     'font-family': 'Raleway',
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
                                                                 dcc.Tab(label='4 Variables', style=tab_mini_style,
                                                                         selected_style=tab_mini_selected_style,
                                                                         children=[html.Div([html.Div(
                                                                             [dcc.Graph(id='my-graph', animate=False)],
                                                                             style={'display': 'inline-block',
                                                                                    'width': '57%',
                                                                                    }),

                                                                             html.Div([
                                                                                 html.Div([html.Label([
                                                                                     "Select X variable:",
                                                                                     dcc.Dropdown(
                                                                                         id='xaxis-anim',
                                                                                         multi=False,
                                                                                         placeholder="Select an option "
                                                                                                     "for X",
                                                                                         options=[
                                                                                             {'label': i, 'value': i}
                                                                                             for i in
                                                                                             dff_explorer_all.columns])],
                                                                                 )],
                                                                                     style={}),
                                                                                 html.Div([html.Label([
                                                                                     "Select Y variable:",
                                                                                     dcc.Dropdown(
                                                                                         id='yaxis-anim',
                                                                                         multi=False,
                                                                                         placeholder='Select an option '
                                                                                                     'for Y',
                                                                                         options=[
                                                                                             {'label': i, 'value': i}
                                                                                             for i in
                                                                                             dff_explorer_all.columns])],
                                                                                 ), ],
                                                                                     style={}),
                                                                                 html.Div([html.Label(
                                                                                     [
                                                                                         "Select size variable:",
                                                                                         dcc.Dropdown(
                                                                                             id='saxis-anim',
                                                                                             multi=False,
                                                                                             placeholder='Select an option for size',
                                                                                             options=[{'label': i,
                                                                                                       'value': i} for i
                                                                                                      in
                                                                                                      dff_explorer_all.columns]),
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
                                                                                 ], style={}),
                                                                                 html.Div([html.Label(
                                                                                     [
                                                                                         "Select color variable:",
                                                                                         dcc.Dropdown(
                                                                                             id="caxis-anim",
                                                                                             multi=False,
                                                                                             placeholder='Select an option for color',
                                                                                             options=[{'label': i,
                                                                                                       'value': i} for i
                                                                                                      in
                                                                                                      dff_explorer_all.columns])],
                                                                                 )], style={}),
                                                                                 html.Div([
                                                                                     html.Label(
                                                                                         "Input x-axis range:"),
                                                                                     html.Label([
                                                                                         html.Div(
                                                                                             id='size-container-filter-xaxis-4D')]),
                                                                                     html.Div(
                                                                                         [dcc.Input(
                                                                                             id='xaxis-input-min-4D',
                                                                                             type='number'),
                                                                                             html.Label(
                                                                                                 "Minimum"),
                                                                                         ], style={
                                                                                             'display': 'table-cell',
                                                                                         }),
                                                                                     html.Div(
                                                                                         [dcc.Input(
                                                                                             id='xaxis-input-max-4D',
                                                                                             type='number'),
                                                                                             html.Label(
                                                                                                 "Maximum")],
                                                                                         style={
                                                                                             'display': 'table-cell', }),
                                                                                     html.Button(
                                                                                         'Submit',
                                                                                         id='button-xaxis-4D'),
                                                                                     html.Div(
                                                                                         id='output-container-button-xaxis-4D')
                                                                                 ], style={}),
                                                                                 html.Div([
                                                                                     html.Label(
                                                                                         "Input y-axis range:"),
                                                                                     html.Label([
                                                                                         html.Div(
                                                                                             id='size-container-filter-yaxis-4D')]),
                                                                                     html.Div(
                                                                                         [dcc.Input(
                                                                                             id='yaxis-input-min-4D',
                                                                                             type='number'),
                                                                                             html.Label(
                                                                                                 "Minimum"),
                                                                                         ], style={
                                                                                             'display': 'table-cell', }),
                                                                                     html.Div(
                                                                                         [dcc.Input(
                                                                                             id='yaxis-input-max-4D',
                                                                                             type='number'),
                                                                                             html.Label(
                                                                                                 "Maximum")],
                                                                                         style={
                                                                                             'display': 'table-cell'}),
                                                                                     html.Button(
                                                                                         'Submit',
                                                                                         id='button-yaxis-4D'),
                                                                                     html.Div(
                                                                                         id='output-container-button-yaxis-4D')
                                                                                 ], style={}),
                                                                                 html.Div([
                                                                                     html.Label(
                                                                                         "Input color bar range:"),
                                                                                     html.Label([
                                                                                         html.Div(
                                                                                             id='size-container-filter-color-4D')]),
                                                                                     html.Div(
                                                                                         [dcc.Input(
                                                                                             id='color-input-min-4D',
                                                                                             type='number'),
                                                                                             html.Label(
                                                                                                 "Minimum"),
                                                                                         ], style={
                                                                                             'display': 'table-cell', }),
                                                                                     html.Div(
                                                                                         [dcc.Input(
                                                                                             id='color-input-max-4D',
                                                                                             type='number'),
                                                                                             html.Label(
                                                                                                 "Maximum")],
                                                                                         style={
                                                                                             'display': 'table-cell'}),
                                                                                     html.Button(
                                                                                         'Submit',
                                                                                         id='button-color-4D'),
                                                                                     html.Div(
                                                                                         id='output-container-button-color-4D')
                                                                                 ], style={}),
                                                                                 html.Div(
                                                                                     [html.Label(
                                                                                         "Once you have selected the dropdowns and a plot has appeared,"
                                                                                         " click a data point to ")],
                                                                                     style={'padding-left': '2%',
                                                                                            'display': 'inline-block'}),
                                                                                 html.Div([html.A(
                                                                                     children=' access the MOF structure in the CCDC',
                                                                                     id='link-4d',
                                                                                     href='https://www.ccdc.cam.ac.uk/structures/',
                                                                                     target='_blank'),
                                                                                 ], style={
                                                                                     'padding-left': '2%',
                                                                                     'display': 'inline-block'}),
                                                                             ],
                                                                                 style={
                                                                                     'display': 'inline-block',
                                                                                     'width': '34%',
                                                                                     'float': 'right',
                                                                                     'fontSize': 14,
                                                                                     'font-family': 'Raleway',
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
                                                 style={"width": "73%", "display": "inline-block", }),
                                        html.Div([
                                            html.Div([html.Label(["Select X variable:",
                                                                  dcc.Dropdown(id='xaxis-3D', multi=False,
                                                                               placeholder="Select an option for X",
                                                                               options=[{'label': i, 'value': i}
                                                                                        for i in dff_explorer_all.columns])],
                                                                 )],
                                                     style={'padding': 10}),
                                            html.Div([html.Label(["Select Y variable:",
                                                                  dcc.Dropdown(id='yaxis-3D', multi=False,

                                                                               placeholder='Select an option for Y',
                                                                               options=[{'label': i, 'value': i}
                                                                                        for i in dff_explorer_all.columns])],
                                                                 ), ],
                                                     style={'padding': 10}),
                                            html.Div([html.Label(["Select Z variable:",
                                                                  dcc.Dropdown(id='zaxis-3D', multi=False,
                                                                               options=[{'label': i, 'value': i} for i
                                                                                        in dff_explorer_all.columns],
                                                                               placeholder='Select an option for Z')],
                                                                 ), ],
                                                     style={'padding': 10}),
                                            html.Div([html.Label(
                                                ["Select size variable:",
                                                 dcc.Dropdown(id='saxis-3D', multi=False,
                                                              placeholder='Select an option for size',
                                                              options=[{'label': i, 'value': i} for i in
                                                                       dff_explorer_all.columns]
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
                                                              placeholder='Select an option for color',
                                                              options=[{'label': i, 'value': i} for i in
                                                                       df_explorer_color.columns])],
                                            )], style={'padding': 10}),
                                            html.Div([
                                                html.Label(
                                                    "Input color bar range:"),
                                                html.Label([
                                                    html.Div(
                                                        id='size-container-filter-color-5D')]),
                                                html.Div(
                                                    [dcc.Input(
                                                        id='color-input-min-5D',
                                                        type='number'),
                                                        html.Label(
                                                            "Minimum"),
                                                    ], style={
                                                        'display': 'table-cell', }),
                                                html.Div(
                                                    [dcc.Input(
                                                        id='color-input-max-5D',
                                                        type='number'),
                                                        html.Label(
                                                            "Maximum")],
                                                    style={
                                                        'display': 'table-cell'}),
                                                html.Button(
                                                    'Submit',
                                                    id='button-color-5D'),
                                                html.Div(
                                                    id='output-container-button-color-5D')
                                            ], style={}),
                                            html.Div(
                                                [html.Label(
                                                    "Once you have selected the dropdowns and a plot has appeared,"
                                                    " click a data point to ")],
                                                style={'padding-left': '2%',
                                                       'display': 'inline-block'}),
                                            html.Div([html.A(
                                                children=' access the MOF structure in the CCDC',
                                                id='link-5d',
                                                href='https://www.ccdc.cam.ac.uk/structures/',
                                                target='_blank'),
                                            ], style={
                                                'padding-left': '2%',
                                                'display': 'inline-block'}),
                                        ],
                                            style={'fontSize': 14, 'fpmt-family': 'Raleway', 'display': 'inline-block',
                                                   'width': '25%', 'float': 'right',
                                                   'backgroundColor': '#ffffff'})
                                        ,

                                    ], className='container', style={'backgroundColor': '#ffffff', 'padding': 20})])
                        ])
                    ]),
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
                                                [
                                                    'Select variable to determine top performing structures (tool will filter '
                                                    'percentiles according to selected column):',
                                                    dcc.Dropdown(
                                                        id='data-set',
                                                        placeholder="Select an option for dataset",
                                                        multi=False,
                                                        options=[{'label': i, 'value': i} for i in
                                                                 df_explorer_y.columns]
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
                                            html.Div([html.Label(["Select % of structures in dataset to analyse:"
                                                                     , dcc.RadioItems(
                                                    id='percentile-type',
                                                    options=[
                                                        {'label': 'Top 1% of structures',
                                                         'value': 'Top 1% of structures'},
                                                        {'label': 'Top 5% of structures',
                                                         'value': 'Top 5% of structures'},
                                                        {'label': 'Top 10% of structures',
                                                         'value': 'Top 10% of structures'},
                                                        {'label': 'All structures', 'value': 'All structures'}, ],
                                                    value='All structures',

                                                )]),
                                                      ], style={'padding': 10}),
                                            html.Div([html.Label(
                                                ["Select X variable:",
                                                 dcc.Dropdown(
                                                     id='anim-frame-violin',
                                                     multi=False,
                                                     placeholder='Select an option '
                                                                 'for X',
                                                     options=[{'label': i, 'value': i} for i in df_stat2.columns])],
                                            ), ],
                                                style={
                                                    'padding': 10}),
                                            html.Div([html.Label(["Select Y variable (geometrical properties):",
                                                                  dcc.Dropdown(id='yaxis-stat',
                                                                               placeholder="Select an option for Y",
                                                                               multi=False,
                                                                               options=[{'label': i, 'value': i} for i
                                                                                        in df_explorer_y.columns]
                                                                               )])
                                                      ], style={'padding': 10}),
                                            dcc.Markdown(d("""
               **Click Data**

               Click on points in the graph.
           """)),
                                            html.Pre(id='click-data-stat'),

                                        ], style={'fontSize': 14, 'font-family': 'Raleway', 'width': '30%',
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
                                                [
                                                    'Select variable to determine top performing structures (tool will filter '
                                                    'percentiles according to selected column):',
                                                    dcc.Dropdown(
                                                        id='data-set-dist',
                                                        placeholder="Select an option for dataset",
                                                        multi=False,
                                                        options=[{'label': i, 'value': i} for i in
                                                                 df_explorer_y.columns]
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
                                                html.Div([html.Label(["Select % of structures in dataset to analyse:"
                                                                         , dcc.RadioItems(
                                                        id='percentile-type-dist',
                                                        options=[
                                                            {'label': 'Top 1% of structures',
                                                             'value': 'Top 1% of structures'},
                                                            {'label': 'Top 5% of structures',
                                                             'value': 'Top 5% of structures'},
                                                            {'label': 'Top 10% of structures',
                                                             'value': 'Top 10% of structures'},
                                                            {'label': 'All structures', 'value': 'All structures'}, ],
                                                        value='All structures',

                                                    )]),
                                                          ], style={'padding': 10}),
                                                html.Div([html.Label(["Select X variable:",
                                                                      dcc.Dropdown(id='xaxis-dist',
                                                                                   multi=False,
                                                                                   placeholder="Select an option for X",
                                                                                   options=[{'label': i, 'value': i} for
                                                                                            i in df_explorer_y.columns]
                                                                                   )]), ],
                                                         style={'padding': 10
                                                                }),
                                                html.Div([html.Label(["Select Grouping:",
                                                                      dcc.RadioItems(
                                                                          id='dist-grouping',
                                                                          options=[{'label': i, 'value': i} for i in
                                                                                   ['None', 'Porosity']],
                                                                          value='None',
                                                                          labelStyle={'display': 'inline-block'})])
                                                          ])
                                            ], style={'fontSize': 14, 'font-family': 'Raleway', 'width': '30%',
                                                      'display': 'inline-block',
                                                      'float': 'right'})

                                        ], className='container', style={'backgroundColor': '#ffffff', 'padding': 40}
                                        )
                                    ]),
                        ]),

                    ])
        ], style=tabs_styles)
    ], style={'padding': 5})
], style={'backgroundColor': '#ffffff', 'font-family': 'Raleway'})


def scaleup(x):
    return round(x * 1.1)


# X AXIS RANGE
@app.callback(
    Output('size-container-filter-xaxis-2D', 'children'),
    [Input('xaxis-anim-2D', 'value')]
)
def update_output(size):
    if not size:
        return dash.no_update
    size_range = [round(df_explorer[size].min(), 2), round(df_explorer[size].max(), 2)]
    return '{}'.format(size_range)


# Y AXIS RANGE
@app.callback(
    Output('size-container-filter-yaxis-2D', 'children'),
    [Input('yaxis-anim-2D', 'value')]
)
def update_output(size):
    if not size:
        return dash.no_update
    size_range = [round(df_explorer[size].min(), 2), round(df_explorer[size].max(), 2)]
    return '{}'.format(size_range)


# POPULATE GRAPH 2VAR ENV ANIM
@app.callback(Output('my-2D-graph', 'figure'),
              [
                  Input('xaxis-anim-2D', 'value'),
                  Input('yaxis-anim-2D', 'value'),
                  Input('button-xaxis-2D', 'n_clicks'),
                  Input('button-yaxis-2D', 'n_clicks')

              ],
              [State('xaxis-input-min-2D', 'value'),
               State('xaxis-input-max-2D', 'value'),
               State('yaxis-input-min-2D', 'value'),
               State('yaxis-input-max-2D', 'value')]
              )
def update_figure_2Var(x, y, n_clicks_x, n_clicks_y, xaxis_min, xaxis_max, yaxis_min, yaxis_max):
    data = dff_explorer_all_url
    return px.scatter(data, x=x, y=y, title="", animation_frame='Mixture',
                      animation_group=data.columns[0], custom_data=['URL'],
                      hover_name=data.columns[0], template="none",
                      ).update_xaxes(showgrid=False, title=x.translate(SUP), autorange=False,
                                     fixedrange=True,
                                     range=[xaxis_min if xaxis_min is not None and n_clicks_x >= 1 else (min(
                                         data[x]) * 0.1),
                                            xaxis_max if xaxis_max is not None and n_clicks_x >= 1 else (max(
                                                data[x]) * 1.15)],
                                     constrain='domain',
                                     ticks='outside',
                                     showline=True, showspikes=True, spikethickness=1, spikedash='solid',
                                     mirror=True, tickformat=".1f", title_standoff=10,
                                     ).update_yaxes(spikedash='solid',
                                                    showgrid=False,
                                                    # title_standoff=8,
                                                    title=dict(
                                                        text=y.translate(
                                                            SUP),
                                                        standoff=13),
                                                    autorange=False,
                                                    fixedrange=True,
                                                    range=[yaxis_min if yaxis_min is not None and n_clicks_y >= 1 else
                                                           (min(data[y]) * 0.1),
                                                           yaxis_max if yaxis_max is not None and n_clicks_y >= 1 else
                                                           (max(data[y]) * 1.15)],
                                                    constrain='domain',
                                                    ticks='outside',
                                                    showspikes=True,
                                                    spikethickness=1,
                                                    showline=True,
                                                    mirror=True,
                                                    tickformat=".1f",
                                                    ).update_layout(hovermode='closest',
                                                                    margin={'l': 91}, autosize=True,
                                                                    font=dict(family='Helvetica',
                                                                              size=13)
                                                                    ).update_traces(
        marker=dict(opacity=0.7, line=dict(width=0.5, color='DarkSlateGrey'),
                    ))


@app.callback(
    Output('link-2d', 'href'),
    [Input('my-2D-graph', 'clickData')])
def display_hover_data(clickData):
    if clickData:
        target = clickData['points'][0]['customdata']
        return target
    else:
        raise PreventUpdate


########################################################################################################################


# X AXIS RANGE
@app.callback(
    Output('size-container-filter-xaxis-3D', 'children'),
    [Input('xaxis-anim-3D', 'value')]
)
def update_output(size):
    if not size:
        return dash.no_update
    size_range = [round(df_explorer[size].min(), 2), round(df_explorer[size].max(), 2)]
    return '{}'.format(size_range)


# Y AXIS RANGE
@app.callback(
    Output('size-container-filter-yaxis-3D', 'children'),
    [Input('yaxis-anim-3D', 'value')]
)
def update_output(size):
    if not size:
        return dash.no_update
    size_range = [round(df_explorer[size].min(), 2), round(df_explorer[size].max(), 2)]
    return '{}'.format(size_range)


# C AXIS RANGE
@app.callback(
    Output('size-container-filter-color-3D', 'children'),
    [Input('caxis-anim-3D', 'value')]
)
def update_output(size):
    if not size:
        return dash.no_update
    size_range = [round(df_explorer[size].min(), 2), round(df_explorer[size].max(), 2)]
    return '{}'.format(size_range)


# POPULATE GRAPH 3VAR ENV ANIM
@app.callback(Output('my-3D-graph', 'figure'),
              [Input('xaxis-anim-3D', 'value'),
               Input('yaxis-anim-3D', 'value'),
               Input('caxis-anim-3D', 'value'),
               Input('button-xaxis-3D', 'n_clicks'),
               Input('button-yaxis-3D', 'n_clicks'),
               Input('button-color-3D', 'n_clicks')],
              [State('xaxis-input-min-3D', 'value'),
               State('xaxis-input-max-3D', 'value'),
               State('yaxis-input-min-3D', 'value'),
               State('yaxis-input-max-3D', 'value'),
               State('color-input-min-3D', 'value'),
               State('color-input-max-3D', 'value')
               ])
def update_figure_3Var(x, y, color, n_clicks_x, n_clicks_y, n_clicks, xaxis_min, xaxis_max, yaxis_min, yaxis_max,
                       color_min, color_max):
    data = dff_explorer_all_url
    return px.scatter(data,
                      x=x,
                      y=y,
                      title="",
                      animation_frame='Mixture',
                      animation_group=data.columns[0],
                      hover_name=data.columns[0],
                      hover_data={},
                      custom_data=['URL'],
                      template="none",
                      color=color,
                      category_orders={color: natsorted(data[color].unique())},
                      color_continuous_scale='Viridis',
                      range_color=[color_min if color_min is not None and n_clicks >= 1 else
                                   min(data[color]),
                                   color_max if color_max is not None and n_clicks >= 1 else
                                   max(data[color])]
                      ).update_xaxes(showgrid=False, title_standoff=10,
                                     title=x.translate(SUP),
                                     ticks='outside',
                                     showline=True,
                                     showspikes=True,
                                     spikethickness=1,
                                     spikedash='solid',
                                     mirror=True,
                                     tickformat=".1f",
                                     autorange=False,
                                     fixedrange=True,
                                     range=[xaxis_min if xaxis_min is not None and n_clicks_x >= 1 else
                                            (min(data[x]) * 0.1),
                                            xaxis_max if xaxis_max is not None and n_clicks_x >= 1 else
                                            (max(data[x]) * 1.15)],
                                     constrain='domain',
                                     ).update_yaxes(spikedash='solid',
                                                    showgrid=False,
                                                    title=dict(text=y.translate(SUP)
                                                               , standoff=12),
                                                    ticks='outside',
                                                    showspikes=True,
                                                    spikethickness=1,
                                                    showline=True,
                                                    mirror=True,
                                                    tickformat=".1f",
                                                    autorange=False,
                                                    fixedrange=True,
                                                    range=[yaxis_min if yaxis_min is not None and n_clicks_y >= 1 else
                                                           (min(data[y]) * 0.1),
                                                           yaxis_max if yaxis_max is not None and n_clicks_y >= 1 else
                                                           (max(data[y]) * 1.15)],
                                                    constrain='domain',
                                                    ).update_layout(
        hovermode='closest',
        margin={'l': 91},
        autosize=True,
        font=dict(family='Helvetica', size=13),
        legend=dict(traceorder='normal'),
        coloraxis_colorbar=dict(title=dict(text=color.translate(SUP), side='right'), ypad=0),
    ).update_traces(marker=dict(size=10,
                                opacity=0.7,
                                showscale=False,
                                line=dict(width=0.7, color='DarkSlateGrey'),
                                colorscale="Viridis"))


@app.callback(
    Output('link-3d', 'href'),
    [Input('my-3D-graph', 'clickData')])
def display_hover_data(clickData):
    if clickData:
        target = clickData['points'][0]['customdata']
        return target
    else:
        raise PreventUpdate


# SIZE MODAL CALLBACK 4VAR ENV ANIM
@app.callback(
    Output('modal-4Var', 'is_open'),
    [Input('saxis-anim', 'value'),
     Input('close', 'n_clicks')])
def update_output_4Var(size_value, modal_close):
    ctx = dash.callback_context
    user_clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    size_list = df_explorer[size_value].to_list()
    if not user_clicked or user_clicked == 'close':
        return dash.no_update, False

    if size_value is None:
        return [], False

    for item in size_list:
        if any(c.isalpha() for c in item):
            return [], True


# SIZE RANGE
@app.callback(
    Output('size-container-4D', 'children'),
    [Input('saxis-anim', 'value')],
)
def update_output_size_range_4Var(size):
    if not size:
        return dash.no_update
    size_range = [round(df_explorer[size].min(), 2), round(df_explorer[size].max(), 2)]
    return 'Size range: {}'.format(size_range)


# X AXIS RANGE
@app.callback(
    Output('size-container-filter-xaxis-4D', 'children'),
    [Input('xaxis-anim', 'value')]
)
def update_output(size):
    if not size:
        return dash.no_update
    size_range = [round(df_explorer[size].min(), 2), round(df_explorer[size].max(), 2)]
    return '{}'.format(size_range)


# Y AXIS RANGE
@app.callback(
    Output('size-container-filter-yaxis-4D', 'children'),
    [Input('yaxis-anim', 'value')]
)
def update_output(size):
    if not size:
        return dash.no_update
    size_range = [round(df_explorer[size].min(), 2), round(df_explorer[size].max(), 2)]
    return '{}'.format(size_range)


# C AXIS RANGE
@app.callback(
    Output('size-container-filter-color-4D', 'children'),
    [Input('caxis-anim', 'value')]
)
def update_output(size):
    if not size:
        return dash.no_update
    size_range = [round(df_explorer[size].min(), 2), round(df_explorer[size].max(), 2)]
    return '{}'.format(size_range)


# POPULATE GRAPH 4VAR ENV ANIM
@app.callback(Output('my-graph', 'figure'),
              [
                  Input('xaxis-anim', 'value'),
                  Input('yaxis-anim', 'value'),
                  Input('caxis-anim', 'value'),
                  Input('saxis-anim', 'value'),
                  Input('button-xaxis-4D', 'n_clicks'),
                  Input('button-yaxis-4D', 'n_clicks'),
                  Input('button-color-4D', 'n_clicks')],
              [State('xaxis-input-min-4D', 'value'),
               State('xaxis-input-max-4D', 'value'),
               State('yaxis-input-min-4D', 'value'),
               State('yaxis-input-max-4D', 'value'),
               State('color-input-min-4D', 'value'),
               State('color-input-max-4D', 'value')
               ]
              )
def update_figure_4Var(x, y, color, size, n_clicks_x, n_clicks_y, n_clicks, xaxis_min, xaxis_max, yaxis_min, yaxis_max,
                       color_min, color_max):
    data = dff_explorer_all_url
    # size_range = [df[size].min(), df[size].max()]
    return px.scatter(data, x=x, y=y, title="", animation_frame="Mixture", custom_data=["URL"],
                      animation_group=data.columns[0], size=size, color=color,
                      hover_name=data.columns[0],
                      color_continuous_scale='Viridis',
                      hover_data={}, template="none",
                      range_color=[color_min if color_min is not None and n_clicks >= 1 else
                                   min(data[color]),
                                   color_max if color_max is not None and n_clicks >= 1 else
                                   max(data[color])],
                      category_orders={color: natsorted(data[color].unique())},
                      ).update_xaxes(showgrid=False, title=x.translate(SUP), ticks='outside',
                                     showline=True, showspikes=True, spikethickness=1, spikedash='solid',
                                     title_standoff=10,
                                     autorange=False,
                                     fixedrange=True,
                                     range=[xaxis_min if xaxis_min is not None and n_clicks_x >= 1 else
                                            (min(data[x]) * 0.1),
                                            xaxis_max if xaxis_max is not None and n_clicks_x >= 1 else
                                            (max(data[x]) * 1.15)],
                                     constrain='domain',
                                     mirror=True, tickformat=".1f").update_yaxes(spikedash='solid',
                                                                                 showgrid=False,
                                                                                 title=dict(text=y.translate(SUP),
                                                                                            standoff=13),
                                                                                 ticks='outside',
                                                                                 showspikes=True, spikethickness=1,
                                                                                 showline=True, mirror=True,
                                                                                 autorange=False,
                                                                                 fixedrange=True,
                                                                                 range=[
                                                                                     yaxis_min if yaxis_min is not None and n_clicks_y >= 1 else
                                                                                     (min(data[y]) * 0.1),
                                                                                     yaxis_max if yaxis_max is not None and n_clicks_y >= 1 else
                                                                                     (max(data[y]) * 1.15)],
                                                                                 constrain='domain',
                                                                                 tickformat=".1f").update_layout(
        hovermode='closest', margin={'l': 91}, autosize=True, font=dict(family='Helvetica',
                                                                        size=13),
        coloraxis_colorbar=dict(title=dict(text=color.translate(SUP), side='right', font=dict(size=14)), ypad=0),
        legend=dict(traceorder='normal'),
        # annotations=[
        #     dict(x=1.5, y=-0.15, showarrow=False, align='left',
        #          text='Size range: {}'.format(size_range), xref='paper', yref='paper', font=dict(size=14))
        # ]
    ).update_traces(marker=dict(opacity=0.7, showscale=False, line=dict(width=0.5, color='DarkSlateGrey'),
                                ))


@app.callback(
    Output('link-4d', 'href'),
    [Input('my-graph', 'clickData')])
def display_hover_data(clickData):
    if clickData:
        target = clickData['points'][0]['customdata']
        return target
    else:
        raise PreventUpdate


# SIZE MODAL CALLBACK 5VAR (3D) ENV ANIM
@app.callback(
    Output('modal-5Var', 'is_open'),
    [Input('saxis-3D', 'value'),
     Input('close-5D', 'n_clicks')], )
def update_output_modal5(size_value, modal_close):
    ctx = dash.callback_context
    user_clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    size_list = df_explorer[size_value].to_list()
    if not user_clicked or user_clicked == 'close':
        return dash.no_update, False

    if size_value is None:
        return [], False

    for item in size_list:
        if any(c.isalpha() for c in item):
            return [], True


# SIZE RANGE
@app.callback(
    Output('size-slider-container-5D', 'children'),
    [Input('saxis-3D', 'value')],
)
def update_output_size_range_5D(size):
    if not size:
        return dash.no_update
    size_range = [round(df_explorer[size].min(), 2), round(df_explorer[size].max(), 2)]
    return 'Size range: {}'.format(size_range)


# POPULATE GRAPH 5VAR (3D) ENV ANIM
@app.callback(Output("graph", "figure"),
              [Input('xaxis-3D', "value"),
               Input('yaxis-3D', 'value'),
               Input('zaxis-3D', 'value'),
               Input('caxis-3D', 'value'),
               Input('saxis-3D', 'value'),
               Input('button-color-5D', 'n_clicks')],
              [
                  State('color-input-min-5D', 'value'),
                  State('color-input-max-5D', 'value')
              ]
              )
def make_figure(x, y, z, color, size, n_clicks, color_min, color_max):
    if x and y and z and color and size is None:
        return dash.no_update
    data = dff_explorer_all_url
    return px.scatter_3d(dff_explorer_all_url, x=x, y=y, z=z, title="", animation_frame='Mixture',
                         animation_group=dff_explorer_all.columns[0], size=size, color=color,
                         category_orders={color: natsorted(data[color].unique())},
                         hover_name=dff_explorer_all.columns[0], custom_data=['URL'],
                         color_continuous_scale='Viridis',
                         hover_data={}, template="none",
                         range_color=[color_min if color_min is not None and n_clicks >= 1 else
                                      min(data[color]),
                                      color_max if color_max is not None and n_clicks >= 1 else
                                      max(data[color])],
                         ).update_xaxes(showgrid=False, title=x.translate(SUP), autorange=True, tickformat=".1f",
                                        ).update_yaxes(
        showgrid=False, title=y.translate(SUP), autorange=True, tickformat=".1f").update_layout(
        coloraxis_colorbar=dict(title=dict(text=color.translate(SUP), side='right', font=dict(size=14)), ypad=0),
        font=dict(family='Helvetica', size=13),
        hovermode='closest', margin={'l': 50, 'b': 80, 't': 50, 'r': 10}, autosize=True,
    ).update_traces(
        marker=dict(opacity=0.7, showscale=False, line=dict(width=0.5, color='#3d3d3d'),
                    ))


@app.callback(
    Output('link-5d', 'href'),
    [Input('graph', 'clickData')])
def display_hover_data(clickData):
    if clickData:
        target = clickData['points'][0]['customdata']
        return target
    else:
        raise PreventUpdate


# SIZE MODAL CALLBACK SCATTER DATA TABLE
@app.callback(
    Output('modal-data', 'is_open'),
    [Input('saxis', 'value'),
     Input('close-data', 'n_clicks')])
def update_output(size_value, modal_close):
    ctx = dash.callback_context
    user_clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    size_list = df_explorer[size_value].to_list()
    if not user_clicked or user_clicked == 'close':
        return dash.no_update, False

    if size_value is None:
        return [], False

    for item in size_list:
        if any(c.isalpha() for c in item):
            return [], True


# COLOR MODAL CALLBACK SCATTER DATA TABLE
@app.callback(
    Output('modal-datac', 'is_open'),
    [Input('caxis', 'value'),
     Input('close-datac', 'n_clicks')], )
def update_output(color_value, modal_close):
    ctx = dash.callback_context
    user_clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    color_list = df_explorer[color_value].to_list()
    if not user_clicked or user_clicked == 'close':
        return dash.no_update, False

    if color_value is None:
        return [], False

    for item in color_list:
        if any(c.isalpha() for c in item):
            return [], True


# X AXIS RANGE
@app.callback(
    Output('size-output-container-filter-xaxis', 'children'),
    [Input('xaxis', 'value')]
)
def update_output(size):
    if not size:
        return dash.no_update
    size_range = [round(df_explorer[size].min(), 2), round(df_explorer[size].max(), 2)]
    return '{}'.format(size_range)


@app.callback(
    Output('size-output-container-filter-yaxis', 'children'),
    [Input('yaxis', 'value')]
)
def update_output(size):
    if not size:
        return dash.no_update
    size_range = [round(df_explorer[size].min(), 2), round(df_explorer[size].max(), 2)]
    return '{}'.format(size_range)


@app.callback(
    Output('size-output-container-filter-color', 'children'),
    [Input('caxis', 'value')]
)
def update_output(size):
    if not size:
        return dash.no_update
    size_range = [round(df_explorer[size].min(), 2), round(df_explorer[size].max(), 2)]
    return '{}'.format(size_range)


# SIZE RANGE
@app.callback(
    Output('size-output-container-filter', 'children'),
    [Input('saxis', 'value')]
)
def update_output(size):
    if not size:
        return dash.no_update
    size_range = [round(df_explorer[size].min(), 2), round(df_explorer[size].max(), 2)]
    return '{}'.format(size_range)


# POPULATE COLORBAR SLIDER SCATTER 3VAR ENV ANIM
@app.callback([Output('colorbar-slider-data-table', 'min'),
               Output('colorbar-slider-data-table', 'max'),
               Output('colorbar-slider-data-table', 'step'),
               Output('colorbar-slider-data-table', 'value')
               ],
              [
                  Input('caxis', 'value')
              ])
def populate_pressure_slider_3Var(color):
    if not color:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    min_v = round(float(df_explorer[color].min()), 1)
    max_v = round(float(df_explorer[color].max()), 1)
    step = 0.1
    value = [round(float(df_explorer[color].min()), 1), round(float(df_explorer[color].max()), 1)]
    return min_v, max_v, step, value


@app.callback(
    Output('slider-output-data-table-size-container', 'children'),
    [Input('sizebar-slider-data-table', 'value')])
def update_output_3Var(value):
    return 'You have selected "{}"'.format(value)


@app.callback(
    Output('slider-output-data-table-size-min-container', 'children'),
    [Input('sizebar-min-slider-data-table', 'value')])
def update_output_3Var(value):
    return 'You have selected "{}"'.format(value)


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
               Input('colorscale', 'value'),
               Input('sizebar-slider-data-table', 'value'),
               Input('sizebar-min-slider-data-table', 'value'),
               Input('button', 'n_clicks'),
               Input('button-xaxis', 'n_clicks'),
               Input('button-yaxis', 'n_clicks')
               ],
              [State('color-input-min', 'value'),
               State('color-input-max', 'value'),
               State('xaxis-input-min', 'value'),
               State('xaxis-input-max', 'value'),
               State('yaxis-input-min', 'value'),
               State('yaxis-input-max', 'value')])
def update_figure(rows, derived_virtual_data, derived_virtual_selected_rows, xaxis_name, yaxis_name,
                  marker_color, marker_size, xaxis_type, yaxis_type, colorscale, size_value, size_min,
                  n_clicks, n_clicks_x, n_clicks_y, color_min, color_max, xaxis_min, xaxis_max, yaxis_min, yaxis_max):
    data_frame_explorer_url = pd.DataFrame(rows)
    if derived_virtual_selected_rows is None:
        return []
    dff = data_frame_explorer_url if derived_virtual_data is None else pd.DataFrame(derived_virtual_data)
    if not size_value:
        return dash.no_update
    if not size_min:
        return dash.no_update
    color_val_float = []
    return [
            html.Div([dcc.Graph(id='HTS-graph',
                                figure={'data': [
                                    go.Scatter(x=dff[xaxis_name], y=dff[yaxis_name],
                                               meta=dff["NAME"],
                                               mode='markers', customdata=dff["URL"],
                                               marker_color=dff[marker_color],
                                               marker_size=dff[marker_size],
                                               hovertemplate="<b>%{meta}</b><br><br>"
                                                             "<extra></extra>",
                                               marker=dict(sizemode='area',
                                                           sizeref=max(dff[marker_size]) / (int(size_value) ** 3.5),
                                                           sizemin=size_min,
                                                           cmin=color_min if color_min is not None and n_clicks >= 1 else min(
                                                               dff[marker_color]),
                                                           cmax=color_max if color_max is not None and n_clicks >= 1 else max(
                                                               dff[marker_color]),
                                                           opacity=0.7, showscale=True,
                                                           line=dict(width=0.7, color='DarkSlateGrey'),
                                                           colorbar=dict(title=dict(text=marker_color.translate(SUP),
                                                                                    font=dict(family='Helvetica'),
                                                                                    side='right'), ypad=0,
                                                                         ),
                                                           colorscale="Viridis" if colorscale == 'Viridis' else "Plasma"),
                                               text=dff[data_frame_explorer_url.columns[0]],
                                               )],
                                    'layout': go.Layout(
                                        font={'family': 'Helvetica', 'size': 14},
                                        xaxis={'title': xaxis_name.translate(SUP), 'autorange': False,
                                               'fixedrange': True,
                                               'mirror': True,
                                               'ticks': 'outside',
                                               'showline': True,
                                               'showspikes': True,
                                               'type': 'linear' if xaxis_type == 'Linear' else 'log',
                                               'tickformat': ".1f",
                                               'range': [
                                                   xaxis_min if xaxis_min is not None and n_clicks_x >= 1 else (min(
                                                       dff[xaxis_name]) * 0.1),
                                                   xaxis_max if xaxis_max is not None and n_clicks_x >= 1 else (max(
                                                       dff[xaxis_name]) * 1.15)
                                                   ],
                                               'constrain': 'domain'
                                               },
                                        yaxis={'title': yaxis_name.translate(SUP),
                                               'autorange': False,
                                               'fixedrange': True,
                                               'mirror': True,
                                               'ticks': 'outside',
                                               'showline': True,
                                               'showspikes': True,
                                               'type': 'linear' if yaxis_type == 'Linear' else 'log',
                                               'tickformat': ".1f",
                                               'range': [
                                                   yaxis_min if yaxis_min is not None and n_clicks_y >= 1 else (min(
                                                       dff[yaxis_name]) * 0.1),
                                                   yaxis_max if yaxis_max is not None and n_clicks_y >= 1 else (max(
                                                       dff[yaxis_name]) * 1.15)
                                                   ],
                                               'constrain': 'domain'
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
                                'padding-left': '25%', 'padding-right': '32%'
                                })
            for column in [xaxis_name] if column in dff
            for column in [yaxis_name] if column in dff
            for column in [marker_color] if column in dff
            for column in [marker_size] if column in dff
        ]


@app.callback(
    Output('link', 'href'),
    [Input('HTS-graph', 'clickData')])
def display_hover_data(clickData):
    if clickData:
        target = clickData['points'][0]['customdata']
        return target
    else:
        raise PreventUpdate


# VIRIDIS AND PLASMA COLOR PALETTE
# PLASMA
colors = ('rgb(240, 249, 33)', 'rgb(249, 221, 37)', 'rgb(254, 176, 49)', 'rgb(249, 152, 61)',
          'rgb(241, 131, 76)', 'rgb(231, 110, 90)', 'rgb(219, 93, 104)', 'rgb(204, 74, 119)', 'rgb(189, 55, 134)',
          'rgb(172, 36, 148)', 'rgb(150, 35, 161)', 'rgb(128, 35, 167)', 'rgb(104, 33, 168)', 'rgb(77, 30, 162)',
          'rgb(49, 27, 152)', 'rgb(13, 22, 135)',

          )
colors2 = ('rgb(68, 1, 84)', 'rgb(72, 40, 120)', 'rgb(62, 73, 137)', 'rgb(49, 104, 142)', 'rgb(38, 130, 142)',
           'rgb(31, 158, 137)', 'rgb(53, 183, 121)', 'rgb(110, 206, 88)', 'rgb(181, 222, 43)', 'rgb(253, 231, 37)')


# SIZE MODAL CALLBACK VIOLIN PLOT
@app.callback(
    Output('modal-violin', 'is_open'),
    [Input('data-set', 'value'),
     Input('close-violin', 'n_clicks')])
def update_output(size_value, modal_close):
    ctx = dash.callback_context
    user_clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    size_list = df_explorer[size_value].to_list()
    if not user_clicked or user_clicked == 'close':
        return dash.no_update, False

    if size_value is None:
        return [], False

    for item in size_list:
        if any(c.isalpha() for c in item):
            return [], True


# POPULATE VIOLIN PLOT CHANGED
@app.callback(Output('violin-plot', 'figure'),
              [
                  Input('yaxis-stat', 'value'),
                  Input('percentile-type', 'value'),
                  Input('anim-frame-violin', 'value'),
                  Input('data-set', 'value'),
              ],
              )
def update_graph_stat(yaxis_name, percentile_type, frame_value, data_set):
    traces = []
    frame_set = set(df[frame_value])
    frame_list = sorted(list(frame_set))
    frame_list = natsorted(frame_list)
    if data_set is None:
        return dash.no_update
    dfObj = pd.DataFrame()
    flag1 = False
    if percentile_type == 'All structures':
        data = df
    for frame in frame_list:
        dff = df[(df[frame_value] == frame)]
        if percentile_type == 'Top 1% of structures':
            data = dff[abs(dff[(data_set)]) > abs(dff[data_set]).quantile(0.99)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
        elif percentile_type == 'Top 5% of structures':
            data = dff[abs(dff[data_set]) > abs(dff[data_set]).quantile(0.95)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
        elif percentile_type == 'Top 10% of structures':
            data = dff[abs(dff[data_set]) > abs(dff[data_set]).quantile(0.9)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
    if yaxis_name is None:
        return dash.no_update
    if flag1 == True:
        data = dfObj
    for frame, color in zip(frame_list, colors):
        data = data.sort_values(by=[frame_value])
        traces.append(go.Violin(y=data[data[frame_value] == frame][yaxis_name], name=frame,
                                line_color=color,
                                meta=[frame],
                                # category_orders={frame_value: natsorted(df[frame_value].unique())},
                                marker={'size': 4}, box_visible=True, opacity=0.9, meanline_visible=True,
                                points='all', text=data[data[frame_value] == frame][data.columns[0]],
                                hovertemplate=
                                "<b>%{text}</b><br><br>" +
                                "X Variable: %{meta[0]}<br>" +
                                "Y Variable: %{y:.3f}<br>"

                                ))
    return {'data': traces,

            'layout': go.Layout(
                title=f"<b> {''.join(str(i) for i in frame_value.translate(SUP))} <br> against "
                      f" {''.join(str(i) for i in yaxis_name.translate(SUP))} <br>"
                      f""
                ,
                xaxis=dict(rangeslider=dict(visible=True), mirror=True, ticks='outside',
                           showline=True, title_standoff=15,
                           title=frame_value.translate(SUP)
                           ),
                yaxis={'title': yaxis_name.translate(SUP), 'mirror': True,
                       'ticks': 'outside', 'showline': True, 'tickformat': ".1f",
                       'title_standoff': 15},
                font=dict(
                    family="Helvetica", size=13
                ),
                margin={'l': 74, 'b': 40, 't': 60, 'r': 50},
                hovermode='closest',
                # annotations=[
                #     dict(x=0.5, y=-0.45, showarrow=False, text=frame_value.translate(SUP),
                #          xref='paper', yref='paper',
                #          font=dict(size=14))
                # ]
            )
            }


# CLICK DATA VIOLIN PLOT
@app.callback(
    Output('click-data-stat', 'children'),
    [Input('violin-plot', 'clickData'),
     ])
def display_click_data_stat(clickData):
    return json.dumps(clickData, indent=2)


# SIZE MODAL CALLBACK 4VAR ENV ANIM
@app.callback(
    Output('modal-dist', 'is_open'),
    [Input('data-set-dist', 'value'),
     Input('close-dist', 'n_clicks')])
def update_output(size_value, modal_close):
    ctx = dash.callback_context
    user_clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    size_list = df_explorer_y[size_value].to_list()
    if not user_clicked or user_clicked == 'close':
        return dash.no_update, False

    if size_value is None:
        return [], False

    for item in size_list:
        if any(c.isalpha() for c in item):
            return [], True


# POPULATE DIST PLOT
@app.callback(Output("dist-plot", "figure"),
              [Input('xaxis-dist', "value"),
               Input('dist-grouping', 'value'),
               Input('data-set-dist', 'value'),
               Input('percentile-type-dist', 'value')])
def make_figure(x, dist_type, data_set, percentile_type):
    if x is None:
        return dash.no_update
    if data_set is None:
        return dash.no_update
    frame_set = set(dff_explorer_all['Mixture'])
    frame_list = list(frame_set)
    dfObj = pd.DataFrame()
    flag1 = False
    if percentile_type == 'All structures':
        data = dff_explorer_all
    for frame_item in frame_list:
        dff = dff_explorer_all[(dff_explorer_all['Mixture'] == frame_item)]
        if percentile_type == 'Top 1% of structures':
            data = dff[abs(dff[data_set]) > abs(dff[data_set]).quantile(0.99)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
        elif percentile_type == 'Top 5% of structures':
            data = dff[abs(dff[data_set]) > abs(dff[data_set]).quantile(0.95)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
        elif percentile_type == 'Top 10% of structures':
            data = dff[abs(dff[data_set]) > abs(dff[data_set]).quantile(0.9)]
            dfObj = pd.concat([dfObj, data], ignore_index=True)
            flag1 = True
    if flag1 == True:
        dfObj = dfObj.sort_values(by=["Mixture"])
        data = dfObj
    return px.histogram(data, x=x, marginal="rug",
                        color="Porosity" if dist_type == 'Porosity' else None,
                        animation_frame="Mixture",
                        hover_data=data.columns, hover_name=data.columns[0], template="none",
                        # category_orders={"Porosity": natsorted(data["Porosity"].unique())}
                        ).update_xaxes(showgrid=False, autorange=True, ticks='outside',
                                       mirror=True, showline=True, tickformat=".1f", title=' ',
                                       ).update_yaxes(showgrid=False, ticks='outside',
                                                      mirror=True, autorange=True, showline=True, tickformat=".1f",
                                                      title=' '
                                                      ).update_layout(
        hovermode='closest', margin={'l': 85, 'b': 80, 't': 60, 'r': 5}, autosize=True, font=dict(family='Helvetica'),
        annotations=[dict(x=0.5, y=-0.20, showarrow=False, text=x.translate(SUP), xref='paper', yref='paper',
                          font=dict(size=14)),
                     dict(x=-0.17, y=0.5, showarrow=False, text="Number of Structures", textangle=-90, xref='paper',
                          yref='paper', font=dict(size=14))]
    ).update_traces(marker=dict(opacity=0.7, line=dict(width=0.5, color='DarkSlateGrey'),
                                )).update_layout(
        title=f"<b> Distribution of {''.join(str(i) for i in x.translate(SUP))}",
        font=dict(family='Helvetica', size=13),
    )


# RUN APP
if __name__ == '__main__':
    app.run_server()
