import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

import plotly.graph_objects as go
import pandas as pd


# Read dataframe from pickle file
df = pd.read_pickle("dataframe.pkl")


app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.ParallelCoordinates(
            id="parallel_coordinates",
            dimensions=[{"label": i, "values": df[i]} for i in df.columns],
        ),
        dcc.Graph(id="line_chart_1"),
        dcc.Graph(id="line_chart_2"),
        dcc.Graph(id="line_chart_3"),
    ]
)


@app.callback(
    [
        Output("line_chart_1", "figure"),
        Output("line_chart_2", "figure"),
        Output("line_chart_3", "figure"),
    ],
    [Input("parallel_coordinates", "restyleData")],
)
def update_line_chart(restyleData):
    # Here assume that your df has columns like 'variable1', 'variable2','variable3'
    # Put conditions here based on restyleData to filter your dataframe
    # Here I just return the whole dataframe
    df_filtered = df

    return [
        {
            "data": [
                go.Scatter(
                    x=df_filtered.index,
                    y=df_filtered["variable1"],
                    mode="lines+markers",
                )
            ]
        },
        {
            "data": [
                go.Scatter(
                    x=df_filtered.index,
                    y=df_filtered["variable2"],
                    mode="lines+markers",
                )
            ]
        },
        {
            "data": [
                go.Scatter(
                    x=df_filtered.index,
                    y=df_filtered["variable3"],
                    mode="lines+markers",
                )
            ]
        },
    ]


@app.callback(
    [
        Output("line_chart_1", "figure"),
        Output("line_chart_2", "figure"),
        Output("line_chart_3", "figure"),
    ],
    [Input("parallel_coordinates", "clickData")],
)
def update_line_chart(clickData):
    df_filtered = df

    return [
        {
            "data": [
                go.Scatter(
                    x=df_filtered.index,
                    y=df_filtered["variable1"],
                    mode="lines+markers",
                )
            ]
        },
        {
            "data": [
                go.Scatter(
                    x=df_filtered.index,
                    y=df_filtered["variable2"],
                    mode="lines+markers",
                )
            ]
        },
        {
            "data": [
                go.Scatter(
                    x=df_filtered.index,
                    y=df_filtered["variable3"],
                    mode="lines+markers",
                )
            ]
        },
    ]


if __name__ == "__main__":
    app.run_server(debug=True)
