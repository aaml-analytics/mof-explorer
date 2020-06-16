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
import numpy as np
from natsort import natsorted

pd.options.mode.chained_assignment = None
# CREATE DASH APP
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://codepen.io/chriddyp/pen/bWLwgP.css',
                                      "https://codepen.io/sutharson/pen/zYvEVPW.css"])
server = app.server
# READ FILE
df = pd.read_csv(https://raw.githubusercontent.com/aaml-analytics/mof-explorer/master/sample-data/pb4binned.csv')
df = df.rename(columns={'Pore limiting diameter (A)': 'Pore limiting diameter (Å)',
                        'Large cavity diameter (A)': 'Large cavity diameter (Å)',
                        'Pore Limiting Diameter (A)': 'Pore Limiting Diameter (Å)',
                        'Large Cavity Diameter (A)': 'Large Cavity Diameter (Å)'})
df_obj = df.select_dtypes(exclude=['object'])
df_stat = df.select_dtypes(exclude=['int', 'float'])
df_stat = df_stat.drop(['Refcode'], axis=1)
df_explorer = df.iloc[:, np.r_[0:10]]
df_explorer = df_explorer.sort_values(by=['Year'])
is_2019 = df_explorer['Year'] == 2019
df_explorer_2019 = df_explorer[is_2019]
df_explorer_2019['Year'] = df_explorer_2019['Year'].map({2019: 'All years'})
dff_explorer_2019 = pd.concat([df_explorer_2019, df_explorer], axis=0)
dff_explorer_2019 = dff_explorer_2019.reset_index(drop=True)
df_explorer_y = dff_explorer_2019.drop(['Refcode'], axis=1)
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
                                "produce plots of their preference. All variables in the user's dataset can be sorted,"
                                'filtered and deleted in the interactive data table. The arguments that the data table '
                                'can take are '
                                'specified '
                                'in the manual. After filtering there are options to choose a logarithmic or linear '
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
                                        html.H2([" 2D and 3D Animation Environment"],
                                                style={'fontSize': 18,
                                                       'font-family': 'Raleway', 'font-weight': 'bold'}),
                                        html.Div([' '.join(twoD_threeD_about)], style={'font-family': 'Raleway'}),
                                        html.H2([" MOF Data Filtering Environment"], style={'fontSize': 18,
                                                                                            'font-weight': 'bold',
                                                                                            'font-family': 'Raleway'}),
                                        html.Div([' '.join(MOF_data_filter)], style={'font-family': 'Raleway', }),
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
                                                                       data=df_explorer.to_dict('records'),
                                                                       columns=[{"name": i, "id": i, "deletable": True,
                                                                                 "selectable": True, 'type': 'numeric',
                                                                                 'format': Format(precision=3,
                                                                                                  scheme=Scheme.fixed)}
                                                                                for i in df_explorer.columns],
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
                                                                       },
                                                                       ),
                                                  html.Div(id='data-table-container'), ], style={'padding': 15}),

                                        html.Div([html.Div([
                                            html.Label(["Select X variable:",
                                                        (dcc.Dropdown(id='xaxis', placeholder="Select an option for X",
                                                                      multi=False,
                                                                      options=[{'label': i, 'value': i} for i in
                                                                               df_explorer_color.columns]))
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
                                                                                   df_explorer_color.columns]))
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
                                                                                  df_explorer_color.columns]),
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
                                                                                   df_explorer_color.columns]))
                                                            ], className="six columns",
                                                           style={'fontSize': 14, 'font-family': 'Raleway',
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
                                                        "Select color bar range:",
                                                        dcc.RangeSlider(
                                                            id='colorbar-slider-data-table',
                                                        ),
                                                        html.Div(
                                                            id='slider-output-data-table-container')
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
                                                    'width': '50%',
                                                    'font-family': 'Raleway',
                                                    'padding': 15,
                                                    'display': 'inline-block'
                                                }),
                                                html.Div([
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
                                                ], style={'display': 'inline-block',
                                                          'fontSize': 14,
                                                          'width': '50%',
                                                          'font-family': 'Raleway',
                                                          'padding': 15,
                                                          }
                                                )], style={'display': 'inline-block', 'width': '100%'})

                                        ], style={'display': 'inline-block', 'width': '45%'}),
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
                                                                                                       dff_explorer_2019.columns])],
                                                                                     )],
                                                                                         style={
                                                                                             'padding': 10}),
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
                                                                                                       dff_explorer_2019.columns])],
                                                                                     ), ],
                                                                                         style={
                                                                                             'padding': 10}),
                                                                                 ],
                                                                                     style={
                                                                                         'display': 'inline-block',
                                                                                         'width': '32%',
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
                                                                                                                             dff_explorer_2019.columns])
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
                                                                                                                         placeholder='Select an option for Y',
                                                                                                                         options=[
                                                                                                                             {
                                                                                                                                 'label': i,
                                                                                                                                 'value': i}
                                                                                                                             for
                                                                                                                             i
                                                                                                                             in
                                                                                                                             df_explorer.columns]
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
                                                                                                                         placeholder='Select an option for color',
                                                                                                                         options=[
                                                                                                                             {
                                                                                                                                 'label': i,
                                                                                                                                 'value': i}
                                                                                                                             for
                                                                                                                             i
                                                                                                                             in
                                                                                                                             dff_explorer_2019.columns])
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
                                                                                                             'font-family': 'Raleway',
                                                                                                             'padding': 15,
                                                                                                         }
                                                                                                     )
                                                                                                 ],
                                                                                                 style={
                                                                                                     'display': 'inline-block',
                                                                                                     'width': '32%',
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
                                                                                             dff_explorer_2019.columns])],
                                                                                 )],
                                                                                     style={
                                                                                         'padding': 10}),
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
                                                                                             dff_explorer_2019.columns])],
                                                                                 ), ],
                                                                                     style={
                                                                                         'padding': 10}),
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
                                                                                                      dff_explorer_2019.columns]),
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
                                                                                             placeholder='Select an option for color',
                                                                                             options=[{'label': i,
                                                                                                       'value': i} for i
                                                                                                      in
                                                                                                      dff_explorer_2019.columns])],
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
                                                                                     'font-family': 'Raleway',
                                                                                     'padding': 7,
                                                                                 }
                                                                                 )
                                                                             ],
                                                                                 style={
                                                                                     'display': 'inline-block',
                                                                                     'width': '32%',
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
                                                 style={"width": "65%", "display": "inline-block", }),
                                        html.Div([
                                            html.Div([html.Label(["Select X variable:",
                                                                  dcc.Dropdown(id='xaxis-3D', multi=False,
                                                                               placeholder="Select an option for X",
                                                                               options=[{'label': i, 'value': i}
                                                                                        for i in df_explorer.columns])],
                                                                 )],
                                                     style={'padding': 10}),
                                            html.Div([html.Label(["Select Y variable:",
                                                                  dcc.Dropdown(id='yaxis-3D', multi=False,

                                                                               placeholder='Select an option for Y',
                                                                               options=[{'label': i, 'value': i}
                                                                                        for i in df_explorer.columns])],
                                                                 ), ],
                                                     style={'padding': 10}),
                                            html.Div([html.Label(["Select Z variable:",
                                                                  dcc.Dropdown(id='zaxis-3D', multi=False,
                                                                               options=[{'label': i, 'value': i} for i
                                                                                        in df_explorer.columns],
                                                                               placeholder='Select an option for Z')],
                                                                 ), ],
                                                     style={'padding': 10}),
                                            html.Div([html.Label(
                                                ["Select size variable:",
                                                 dcc.Dropdown(id='saxis-3D', multi=False,
                                                              placeholder='Select an option for size',
                                                              options=[{'label': i, 'value': i} for i in
                                                                       df_explorer.columns]
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
                                                'font-family': 'Raleway',
                                                'padding': 7,
                                            }
                                            ),
                                        ],
                                            style={'fontSize': 14, 'fpmt-family': 'Raleway', 'display': 'inline-block',
                                                   'width': '32%', 'float': 'right',
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
                                                     options=[{'label': i, 'value': i} for i in df_stat.columns])],
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
], style={'backgroundColor': '#f6f6f6', 'font-family': 'Raleway'})


def scaleup(x):
    return round(x * 1.1)


# POPULATE GRAPH 2VAR ENV ANIM
@app.callback(Output('my-2D-graph', 'figure'),
              [
                  Input('xaxis-anim-2D', 'value'),
                  Input('yaxis-anim-2D', 'value')],
              )
def update_figure_2Var(x, y):
    # data = df_explorer.sort_values(by=['Year'])
    data = dff_explorer_2019
    return px.scatter(data, x=x, y=y, title="", animation_frame='Year',
                      animation_group=data.columns[0],
                      hover_name=data.columns[0],
                      hover_data={}, template="none",
                      ).update_xaxes(showgrid=False, title=x.translate(SUP), autorange=True, ticks='outside',
                                     showline=True, showspikes=True, spikethickness=1, spikedash='solid',
                                     mirror=True, tickformat=".1f", title_standoff=10,
                                     ).update_yaxes(spikedash='solid',
                                                    showgrid=False,
                                                    # title_standoff=8,
                                                    title=dict(
                                                        text=y.translate(
                                                            SUP),
                                                        standoff=13),
                                                    autorange=True,
                                                    ticks='outside',
                                                    showspikes=True,
                                                    spikethickness=1,
                                                    showline=True,
                                                    mirror=True,
                                                    tickformat=".1f",
                                                    ).update_layout(
        clickmode='event+select', hovermode='closest', margin={'l': 91}, autosize=True, font=dict(family='Helvetica')
    ).update_traces(marker=dict(opacity=0.7, line=dict(width=0.5, color='DarkSlateGrey'),
                                ))


########################################################################################################################

# POPULATE COLORBAR SLIDER SCATTER 3VAR ENV ANIM
@app.callback([Output('colorbar-slider', 'min'),
               Output('colorbar-slider', 'max'),
               Output('colorbar-slider', 'step'),
               Output('colorbar-slider', 'value')
               ],
              [
                  Input('caxis-anim-3D', 'value')
              ])
def populate_pressure_slider_3Var(color):
    if not color:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    min_v = round(float(df_explorer[color].min()), 1)
    max_v = round(float(df_explorer[color].max()), 1)
    step = 0.1
    value = [round(float(df_explorer[color].min()), 1), round(float(df_explorer[color].max()), 1)]
    return min_v, max_v, step, value


# STATE VALUE COLORBAR SLIDER SCATTER 3VAR ENV ANIM
@app.callback(
    Output('slider-output-container', 'children'),
    [Input('colorbar-slider', 'value')])
def update_output_3Var(value):
    return 'You have selected "{}"'.format(value)


# POPULATE GRAPH 3VAR ENV ANIM
@app.callback(Output('my-3D-graph', 'figure'),
              [Input('xaxis-anim-3D', 'value'),
               Input('yaxis-anim-3D', 'value'),
               Input('caxis-anim-3D', 'value'),
               Input('colorbar-slider', 'value')])
def update_figure_3Var(x, y, color, color_value):
    data = dff_explorer_2019
    if not color_value:
        return dash.no_update
    color_val_float = []
    for i in range(0, len(color_value), 1):
        color_val_float.append(float(color_value[i]))
    color_val = color_val_float
    return px.scatter(data,
                      x=x,
                      y=y,
                      title="",
                      animation_frame='Year',
                      animation_group=data.columns[0],
                      hover_name=data.columns[0],
                      hover_data={},
                      template="none",
                      color=color,
                      category_orders={color: natsorted(data[color].unique())},
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
                                     tickformat=".1f").update_yaxes(spikedash='solid',
                                                                    showgrid=False,
                                                                    title=dict(text=y.translate(SUP)
                                                                               , standoff=12),
                                                                    autorange=True,
                                                                    ticks='outside',
                                                                    showspikes=True,
                                                                    spikethickness=1,
                                                                    showline=True,
                                                                    mirror=True,
                                                                    tickformat=".1f").update_layout(
        clickmode='event+select',
        hovermode='closest',
        margin={'l': 91},
        autosize=True,
        font=dict(family='Helvetica'),
        legend=dict(traceorder='normal'),
        coloraxis_colorbar=dict(title=dict(text=color.translate(SUP), side='right'), ypad=0),
    ).update_traces(marker=dict(size=10,
                                opacity=0.7,
                                showscale=False,
                                line=dict(width=0.7, color='DarkSlateGrey'),
                                colorscale="Viridis"))


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


# POPULATE COLORBAR SLIDER SCATTER 4VAR ENV ANIM
@app.callback([Output('colorbar-slider-4D', 'min'),
               Output('colorbar-slider-4D', 'max'),
               Output('colorbar-slider-4D', 'step'),
               Output('colorbar-slider-4D', 'value')
               ],
              [
                  Input('caxis-anim', 'value')
              ])
def populate_pressure_slider_4Var(color):
    if not color:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    min_v = round(float(df_explorer[color].min()), 1)
    max_v = round(float(df_explorer[color].max()), 1)
    step = 0.1
    value = [round(float(df_explorer[color].min()), 1), round(float(df_explorer[color].max()), 1)]
    return min_v, max_v, step, value


@app.callback(
    Output('slider-output-container-4D', 'children'),
    [Input('colorbar-slider-4D', 'value')])
def update_output_4Var(value):
    return 'You have selected "{}"'.format(value)


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


# POPULATE GRAPH 4VAR ENV ANIM
@app.callback(Output('my-graph', 'figure'),
              [
                  Input('xaxis-anim', 'value'),
                  Input('yaxis-anim', 'value'),
                  Input('caxis-anim', 'value'),
                  Input('saxis-anim', 'value'),
                  Input('colorbar-slider-4D', 'value')],
              )
def update_figure_4Var(x, y, color, size, color_value):
    data = dff_explorer_2019
    if not color_value:
        return dash.no_update
    # size_range = [df[size].min(), df[size].max()]
    color_val_float = []
    for i in range(0, len(color_value), 1):
        color_val_float.append(float(color_value[i]))
    color_val = color_val_float
    return px.scatter(data, x=x, y=y, title="", animation_frame="Year",
                      animation_group=data.columns[0], size=size, color=color,
                      hover_name=data.columns[0],
                      color_continuous_scale='Viridis',
                      hover_data={}, template="none", range_color=color_val,
                      category_orders={color: natsorted(data[color].unique())},
                      ).update_xaxes(showgrid=False, title=x.translate(SUP), autorange=True, ticks='outside',
                                     showline=True, showspikes=True, spikethickness=1, spikedash='solid',
                                     title_standoff=10,
                                     mirror=True, tickformat=".1f").update_yaxes(spikedash='solid',
                                                                                 showgrid=False,
                                                                                 title=dict(text=y.translate(SUP),
                                                                                            standoff=13),
                                                                                 autorange=True, ticks='outside',
                                                                                 showspikes=True, spikethickness=1,
                                                                                 showline=True, mirror=True,
                                                                                 tickformat=".1f").update_layout(
        clickmode='event+select', hovermode='closest', margin={'l': 91}, autosize=True, font=dict(family='Helvetica'),
        coloraxis_colorbar=dict(title=dict(text=color.translate(SUP), side='right', font=dict(size=14)), ypad=0),
        legend=dict(traceorder='normal'),
        # annotations=[
        #     dict(x=1.5, y=-0.15, showarrow=False, align='left',
        #          text='Size range: {}'.format(size_range), xref='paper', yref='paper', font=dict(size=14))
        # ]
    ).update_traces(marker=dict(opacity=0.7, showscale=False, line=dict(width=0.5, color='DarkSlateGrey'),
                                ))


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


# POPULATE COLORBAR SLIDER SCATTER 5VAR (3D) ENV ANIM
@app.callback([Output('colorbar-slider-5D', 'min'),
               Output('colorbar-slider-5D', 'max'),
               Output('colorbar-slider-5D', 'step'),
               Output('colorbar-slider-5D', 'value')
               ],
              [Input('caxis-3D', 'value')
               ])
def populate_pressure_slider_5D(color):
    if not color:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    min_v = round(float(df_explorer[color].min()), 1)
    max_v = round(float(df_explorer[color].max()), 1)
    step = 0.1
    value = [round(float(df_explorer[color].min()), 1), round(float(df_explorer[color].max()), 1)]
    return min_v, max_v, step, value


@app.callback(
    Output('slider-output-container-5D', 'children'),
    [Input('colorbar-slider-5D', 'value')])
def update_output_colorbar_5D(value):
    return 'You have selected "{}"'.format(value)


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
               Input('colorbar-slider-5D', 'value')],
              )
def make_figure(x, y, z, color, size, color_value):
    if not color_value:
        return dash.no_update
    if x and y and z and color and size is None:
        return dash.no_update
    color_val_float = []
    for i in range(0, len(color_value), 1):
        color_val_float.append(float(color_value[i]))
    color_val = color_val_float
    data = dff_explorer_2019
    return px.scatter_3d(dff_explorer_2019, x=x, y=y, z=z, title="", animation_frame='Year',
                         animation_group=dff_explorer_2019.columns[0], size=size, color=color,
                         category_orders={color: natsorted(data[color].unique())},
                         hover_name=dff_explorer_2019.columns[0],
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


# STATE VALUE COLORBAR SLIDER SCATTER 3VAR ENV ANIM
@app.callback(
    Output('slider-output-data-table-container', 'children'),
    [Input('colorbar-slider-data-table', 'value')])
def update_output_3Var(value):
    return 'You have selected "{}"'.format(value)


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
               Input('colorbar-slider-data-table', 'value'),
               Input('sizebar-slider-data-table', 'value'),
               Input('sizebar-min-slider-data-table', 'value')
               ])
def update_figure(rows, derived_virtual_data, derived_virtual_selected_rows, xaxis_name, yaxis_name,
                  marker_color, marker_size, xaxis_type, yaxis_type, colorscale, color_value, size_value, size_min):
    df_explorer = pd.DataFrame(rows)
    if derived_virtual_selected_rows is None:
        return []
    dff = df_explorer if derived_virtual_data is None else pd.DataFrame(derived_virtual_data)
    if not color_value:
        return dash.no_update
    if not size_value:
        return dash.no_update
    if not size_min:
        return dash.no_update
    color_val_float = []
    for i in range(0, len(color_value), 1):
        color_val_float.append(float(color_value[i]))
    color_val = color_val_float
    return [
        html.Div([dcc.Graph(id='HTS-graph',
                            figure={'data': [
                                go.Scatter(x=dff[xaxis_name], y=dff[yaxis_name],
                                           mode='markers',
                                           marker_color=dff[marker_color],
                                           marker_size=dff[marker_size],
                                           marker=dict(sizemode='area',
                                                       sizeref=max(dff[marker_size]) / (int(size_value) ** 3.5),
                                                       sizemin=size_min,
                                                       cmin=min(color_val), cmax=max(color_val),
                                                       opacity=0.7, showscale=True,
                                                       line=dict(width=0.7, color='DarkSlateGrey'),
                                                       colorbar=dict(title=dict(text=marker_color.translate(SUP),
                                                                                font=dict(family='Helvetica'),
                                                                                side='right'), ypad=0,
                                                                     ),
                                                       colorscale="Viridis" if colorscale == 'Viridis' else "Plasma"),
                                           text=dff[df_explorer.columns[0]],
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
                            'padding-left': '25%', 'padding-right': '32%'
                            })
        for column in [xaxis_name] if column in dff
        for column in [yaxis_name] if column in dff
        for column in [marker_color] if column in dff
        for column in [marker_size] if column in dff
    ]


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
                                # category_orders={frame_value: natsorted(df[frame_value].unique())},
                                marker={'size': 4}, box_visible=True, opacity=0.9, meanline_visible=True,
                                points='all', text=data[df.columns[0]],
                                hovertemplate=
                                "<b>%{text}</b><br><br>" +
                                "X Variable: %{x:.2f}<br>" +
                                "Y Variable: %{y:.0f}<br>"

                                ))
    return {'data': traces,

            'layout': go.Layout(
                title=f"<b> {''.join(str(i) for i in frame_value.translate(SUP))} against"
                      f" {''.join(str(i) for i in yaxis_name.translate(SUP))} "
                ,
                xaxis=dict(rangeslider=dict(visible=True), mirror=True, ticks='outside',
                           showline=True, title=frame_value.translate(SUP)),
                yaxis={'title': yaxis_name.translate(SUP), 'mirror': True,
                       'ticks': 'outside', 'showline': True, 'tickformat': ".1f",
                       'title_standoff': 15},
                font=dict(
                    family="Helvetica",
                ),
                margin={'l': 74, 'b': 35, 't': 50, 'r': 50},
                hovermode='closest',
                # annotations=[
                #     dict(x=0.5, y=-0.44, showarrow=False, text=frame_value.translate(SUP),
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
    frame_set = set(dff_explorer_2019['Year'])
    frame_list = list(frame_set)
    dfObj = pd.DataFrame()
    flag1 = False
    if percentile_type == 'All structures':
        data = dff_explorer_2019
    for frame_item in frame_list:
        dff = dff_explorer_2019[(dff_explorer_2019['Year'] == frame_item)]
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
        data = dfObj
    return px.histogram(data, x=x, marginal="rug",
                        color="Porosity" if dist_type == 'Porosity' else None,
                        animation_frame="Year",
                        hover_data=data.columns, hover_name=data.columns[0], template="none",
                        category_orders={"Porosity": natsorted(data["Porosity"].unique())}
                        ).update_xaxes(showgrid=False, autorange=True, ticks='outside',
                                       mirror=True, showline=True, tickformat=".1f", title=' ',
                                       ).update_yaxes(showgrid=False, ticks='outside',
                                                      mirror=True, autorange=True, showline=True, tickformat=".1f",
                                                      title=' '
                                                      ).update_layout(
        hovermode='closest', margin={'l': 85, 'b': 80, 't': 50, 'r': 5}, autosize=True, font=dict(family='Helvetica'),
        annotations=[dict(x=0.5, y=-0.17, showarrow=False, text=x.translate(SUP), xref='paper', yref='paper',
                          font=dict(size=14)),
                     dict(x=-0.17, y=0.5, showarrow=False, text="Number of Structures", textangle=-90, xref='paper',
                          yref='paper', font=dict(size=14))]
    ).update_traces(marker=dict(opacity=0.7, line=dict(width=0.5, color='DarkSlateGrey'),
                                )).update_layout(
        title=f"<b> Distribution of Structures against {''.join(str(i) for i in x.translate(SUP))}",
        font=dict(family='Helvetica'),
    )


# RUN APP
if __name__ == '__main__':
    app.run_server()
