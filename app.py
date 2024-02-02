from jbi100_app.main import app
from jbi100_app import data
from jbi100_app.views.linegraph import LineGraph
from jbi100_app.views.barchart import BarChart
from jbi100_app.views.bubblechart import BubbleChart
from jbi100_app.views.parallelcoordinates import ParallelCoordinates  # Assuming you have a ParallelCoordinates class

from dash import html
import dash
import plotly.express as px
from dash.dependencies import Input, Output

if __name__ == '__main__':
    # Create data
    data = data.get_data()
    top_left_data = data[0]
    top_right_data = data[1]
    bottom_left_data = data[2]
    bottom_right_data = data[3]
    income_group_dict = data[4]

    if len(top_left_data) == 0 or len(top_right_data) == 0 or len(bottom_left_data) == 0 or len(bottom_right_data) == 0:
        raise ValueError('No data to display')

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
    Output(parcoords.html_id, 'figure'),
     Input(parcoords.html_id + '-dropdown', 'value')
    )
    def update_parcoords(dropdown_value):
        return parcoords.update(dropdown_value)

    @app.callback(
    Output(barchart.html_id, 'figure'),
    [Input(bubblechart.html_id, 'selectedData'),
     Input(barchart.html_id + '-dropdown', 'value')]
    )
    def update_barchart(dropdown_value, selected_data):
        return barchart.update(selected_data, dropdown_value)

    @app.callback(
        Output(bubblechart.html_id, 'figure'),
        [Input(barchart.html_id, 'selectedData'),
         Input(bubblechart.html_id + '-dropdown', 'value')]
    )
    def update_bubblechart(dropdown_value, selected_data):
        return bubblechart.update(selected_data, dropdown_value)

    
    @app.callback(
    Output(linegraph.html_id, 'figure'),
    [Input(bubblechart.html_id, 'selectedData'),
     Input(linegraph.html_id + '-dropdown', 'value')]
    )
    def update_linegraph(selected_data_bubblechart, dropdown_value):
        if selected_data_bubblechart is None or not selected_data_bubblechart['points']:
            selected_occupations = dropdown_value
        else:
            selected_occupations = [point['customdata'] for point in selected_data_bubblechart['points']]           
    
        return linegraph.update(selected_occupations)

   


    app.run_server(debug=False, dev_tools_ui=False)
