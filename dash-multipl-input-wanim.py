import dash
import dash_core_components as dcc
import dash_html_components as html
import json
from textwrap import dedent as d
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import flask

df = pd.read_csv('/Users/mythilisutharson/documents/cam_work/mof_explorer_flourish/MOF_trans_data.csv')

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)
features = df.columns
server = app.server

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
tabs_styles = {'height': '35px', 'font-family': 'Arial'}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#3d3d3d',
    'color': 'white',
    'padding': '6px'
}
app.layout = html.Div([
    html.H1('',
            style={'textAlign': 'center', 'color': 'DarkSlateGrey', 'fontSize': 20}),
    html.Div([
        dcc.Tabs([
            dcc.Tab(label='MOF explorer', style=tab_style, selected_style=tab_selected_style,
                    children=[
                        html.Div([dcc.Graph(id='HTS-plot', animate=True), html.Div([
                            dcc.Markdown(d("""
                **Click Data**

                Click on points in the graph.
            """)),
                            html.Pre(id='click-data', style=styles['pre']),
                        ], style={'fontSize': 14, 'font-family': 'Arial', 'padding': 50,
                                  'width': '23%', 'float': 'left'})
                                  ], style={'height': '70vh', 'width': '70vw'}, ),
                        html.Div([
                            html.Label(["Select Pressure (bar):",
                                        dcc.Slider(id='pressure-slider',
                                                   min=df['Pressure'].min(),
                                                   max=df['Pressure'].max(),
                                                   value=df['Pressure'].max(),
                                                   marks={str(pressure): str(pressure) for pressure in
                                                          df['Pressure'].unique()},
                                                   step=None,
                                                   # updatemode='drag'
                                                   ), ])
                        ], style={'fontSize': 14, 'font-family': 'Arial'}),
                        html.Div([
                            html.Label(["Select X variable:",
                                        dcc.Dropdown(id='xaxis', options=[{'label': i, 'value': i} for i in features],
                                                     value='Uptake (Grav.)', )])
                        ], style={'width': '18%', 'display': 'inline-block', 'fontSize': 14, 'font-family': 'Arial'}),
                        html.Div([
                            html.Label(["Select Y variable:",
                                        dcc.Dropdown(id='yaxis', options=[{'label': i, 'value': i} for i in features],
                                                     value='Uptake (Vol.)')])
                        ], style={'width': '18%', 'display': 'inline-block', 'fontSize': 14, 'font-family': 'Arial'}),
                        html.Div([
                            html.Label(
                                ["Select S variable:",
                                 dcc.Dropdown(id='marker_size', options=[{'label': i, 'value': i} for i in features],
                                              value='Pore Limiting Diameter')])
                        ], style={'width': '18%', 'display': 'inline-block', 'fontSize': 14, 'font-family': 'Arial'}),
                        html.Div([
                            html.Label(
                                ["Select C variable:",
                                 dcc.Dropdown(id="marker_color", options=[{'label': i, 'value': i} for i in features],
                                              value='Void Fraction')])
                        ], style={'width': '18%', 'display': 'inline-block', 'fontSize': 14, 'font-family': 'Arial'}),

                    ]),
            dcc.Tab(label='Statistical Analysis', style=tab_style, selected_style=tab_selected_style,
                    children=[html.Div([
                        html.Div([dcc.Graph(id='violin-plot'), html.Div([
                            dcc.Markdown(d("""
               **Click Data**

               Click on points in the graph.
           """)),
                            html.Pre(id='click-data-stat', style=styles['pre']),

                        ], style={'fontSize': 14, 'font-family': 'Arial', 'width': '35%', 'padding': 20,
                                  'float': 'right'})
                                  ], style={'height': '70vh', 'width': '80vw'}),
                        html.Div([
                            html.Label(["Select Y variable (Geometrical Property):",
                                        dcc.Dropdown(id='yaxis-stat',
                                                     options=[{'label': i, 'value': i} for i in features],
                                                     value='Void Fraction')])
                        ], style={'display': 'inline-block', 'fontSize': 14, 'font-family': 'Arial', 'width': '35%',
                                  'padding': 20
                                  }),
                    ], className='container')
                    ])

        ], style=tabs_styles),

    ]),

], style={})  # style for outter div


@app.callback(Output('HTS-plot', 'figure'),
              [
                  Input('xaxis', 'value'),
                  Input('yaxis', 'value'),
                  Input('marker_size', 'value'),
                  Input('marker_color', 'value'),
                  Input('pressure-slider', 'value'),
              ])
def update_graph(xaxis_name, yaxis_name, size_name, color_name, pressure_value):
    dff = df[df['Pressure'] == pressure_value]
    # pressure_value2 = list(set(pressure_value))
    # file = open("debug.text", "w+")
    # file.write("%f" % pressure_value2)
    # file.write("%f" % (len(yaxis_name)))
    # file.write("\n")
    # for i in range(0, len(pressure_value), 1):
    #     file.write("%f" %(pressure_value[i]))
    #     file.write("\n")
    # file.write("%s" %pressure_value)
    # file.write("\n")
    # file.write("%s" %yaxis_name)
    # pressure_set2 = set(pressure_value)
    # pressures2 = sorted(list(pressure_set2))
    # pressure_str = [str(i) for i in pressures2]
    # for i in range(0, len(pressure_str), 1):
    #     pressure_str2 = int(pressure_str[i])
    #     pressure_str[i] = pressure_str2
    return {'data': [go.Scatter(x=dff[xaxis_name],
                                y=dff[yaxis_name], mode='markers',
                                marker_color=dff[color_name], marker_size=dff[size_name],
                                marker=dict(sizemode='area', sizeref=max(dff[size_name]) / (25 ** 2),
                                            sizemin=4,
                                            opacity=0.7, showscale=True,
                                            line=dict(width=0.5, color='DarkSlateGrey'),
                                            colorbar=dict(title=color_name),
                                            colorscale='Viridis', ),
                                text=dff['DDEC code'],
                                hovertemplate=
                                "<b>%{text}</b><br><br>" +
                                "Volumetric Uptake: %{y:.0f cm/(STP)cm}<br>" +
                                "Gravimetric Uptake: %{x:.0 mol/kg}<br>" +
                                "Largest Cavity Diameter : %{marker.size:,}" +
                                "<extra></extra>", )]

        , 'layout': go.Layout(
            title=f"<b>MOF explorer tool</b> " ,
            xaxis={'title': xaxis_name},
            yaxis={'title': yaxis_name},

            margin={'l': 50, 'b': 80, 't': 50, 'r': 10},
            hovermode='closest',
            clickmode='event+select'  # double click to discharge
        )

            }


# so pressure_set is pressure_value
# pressure_set = set(df['Pressure'])
# pressure_list = list(pressure_set)
# pressures = sorted(pressure_list)
# pressure_str = [str(i) for i in pressures]
# string = ' bar'
# pressures_bar = [s + string for s in pressure_str]


@app.callback(
    Output('click-data', 'children'),
    [Input('HTS-plot', 'clickData'),
     ])
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)


pressure_set = set(df['Pressure'])
pressure_list = list(pressure_set)
pressures = pressure_list.sort()


@app.callback(Output('violin-plot', 'figure'),
              [
                  Input('yaxis-stat', 'value'),
              ])
def update_graph_stat(yaxis_name):
    traces = []
    for pressure in pressure_list:
        traces.append(go.Violin(y=df[df['Pressure'] == pressure][yaxis_name], name=pressure,
                                marker={'size': 4}, box_visible=True, opacity=0.6, meanline_visible=True,
                                ))

    return {'data': traces

        , 'layout': go.Layout(
            title=f"<b>Violin plot for {''.join(str(i) for i in yaxis_name)} against Pressure</b>",
            xaxis=dict(rangeslider=dict(visible=True)),
            yaxis={'title': yaxis_name},

            margin={'l': 50, 'b': 0, 't': 50, 'r': 10},
            hovermode='closest',
            clickmode='event+select',  # double click to discharge
        ),
            }


# {'title': 'Pressure (bar)'},


@app.callback(
    Output('click-data-stat', 'children'),
    [Input('violin-plot', 'clickData'),
     ])
def display_click_data_stat(clickData):
    return json.dumps(clickData, indent=2)


app.run_server(debug=True, port=6060)
