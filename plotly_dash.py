import plotly.express as px
from dash import Dash, dcc, html

import pandas as pd
from dash import Dash, dcc, html, Input, Output
import pandas as pd

from dash import Dash, dcc, html, Input, Output, dash_table

import plotly.express as px

import pandas as pd
import plotly.graph_objects as go

 

results = pd.read_csv('data_generation/results.csv').iloc[:, -4:]
release_decisions = pd.read_csv('data_generation/release_decisions.csv').iloc[:,1:]
fig = px.parallel_coordinates(results)

fig_decisions = px.line(release_decisions)

app = Dash()

 

app.layout = html.Div([

    dcc.Graph(

        id='parallel_coordinates',

        figure=fig

    ),

 

    dash_table.DataTable(

        id='datatable',

        columns=[{"name": i, "id": i, "deletable": True, "selectable": True} for i in results.columns],

        data=results.to_dict('records'),

        editable=True,

        filter_action="native",

        sort_action="native",

        sort_mode="multi",

        column_selectable="single",

        row_selectable="multi",

        row_deletable=True,

        selected_columns=[],

        selected_rows=[],

        page_action="native",

        page_current=0,

        page_size=10,

    ),
        dcc.Graph(

        id='time_series_decisions',

        figure=fig_decisions

    ),

])

 

# Handle row selections:

 
 

@app.callback(
    Output('parallel_coordinates', 'figure'),
    [Input('datatable', 'selected_rows')]
)


def update_graph(selected_rows):
    if sum(results.index.isin(selected_rows).astype(int)) == 0:
        res = results 
    else:
        res = results[results.index.isin(selected_rows)]
    fig = px.parallel_coordinates(
        res
    )
    return fig

@app.callback(
    Output('time_series_decisions', 'figure'),
    [Input('datatable', 'selected_rows')]
)


def update_graph_release(selected_rows):
    if sum(results.index.isin(selected_rows).astype(int)) == 0:
        res = release_decisions 
    else:
        res = release_decisions.iloc[:, selected_rows]
    fig_decisions = px.line(res)
    return fig_decisions



if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)