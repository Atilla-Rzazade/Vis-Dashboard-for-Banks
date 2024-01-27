from jbi100_app.main import app
from jbi100_app import data
from jbi100_app.views.linegraph import LineGraph
from jbi100_app.views.barchart import BarChart
from jbi100_app.views.bubblechart import BubbleChart
from jbi100_app.views.parallelcoordinates import ParallelCoordinates  # Assuming you have a ParallelCoordinates class

from dash import html
import plotly.express as px
from dash.dependencies import Input, Output

if __name__ == '__main__':
    # Create data
    data = data.get_data()
    top_left_data = data[0]
    top_right_data = data[1]
    print(top_left_data)
    bottom_left_data = data[2]
    bottom_right_data = data[3]

    # Instantiate custom views
    linegraph = LineGraph("Line Graph", 'Month', 'Count', top_right_data)
    parcoords = ParallelCoordinates("Parallel Coordinates", top_left_data)
    barchart = BarChart("Bar Chart", 'Occupation', 'DIO', bottom_left_data)
    bubblechart = BubbleChart("Bubble Chart", 'Num_Bank_Accounts', 'Avg_Credit_Util_Ratio', 'Delays', bottom_right_data)

    app.layout = html.Div(
        id="app-container",
        children=[
            # Top row
            html.Div(
                className="row",
                children=[
                    # Left column
                    html.Div(
                        className="six columns",
                        children=[parcoords]  # Place the line graph here
                    ),
                    # Right column
                    html.Div(
                        className="six columns",
                        children=[linegraph]  # Place the parallel coordinates chart here
                    ),
                ],
            ),
            # Bottom row
            html.Div(
                className="row",
                children=[
                    # Left column
                    html.Div(
                        className="six columns",
                        children=[barchart]  # Place the bar chart here
                    ),
                    # Right column
                    html.Div(
                        className="six columns",
                        children=[bubblechart]  # Place the bubble chart here
                    ),
                ],
            ),
        ],
    )

    @app.callback(
        Output(linegraph.html_id, 'figure'),
        Input(linegraph.html_id + '-dropdown', 'value')
    )
    def update_linegraph(selected_occupations):
        return linegraph.update(selected_occupations)

    @app.callback(
        Output(parcoords.html_id, 'figure'),
        Input(parcoords.html_id + '-dropdown', 'value')
    )
    def update_parcoords(selected_income_groups):
        return parcoords.update(selected_income_groups)

    @app.callback(
        Output(barchart.html_id, 'figure'),
        Input(barchart.html_id + '-dropdown', 'value')
    )
    def update_barchart(selected_occupations):
        return barchart.update(selected_occupations)

    @app.callback(
        Output(bubblechart.html_id, 'figure'),
        Input(bubblechart.html_id + '-dropdown', 'value')
    )
    def update_bubblechart(selected_occupations):
        return bubblechart.update(selected_occupations)

    app.run_server(debug=False, dev_tools_ui=False)
