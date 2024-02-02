from jbi100_app.main import app
from jbi100_app import data
from jbi100_app.views.linegraph import LineGraph
from jbi100_app.views.barchart import BarChart
from jbi100_app.views.bubblechart import BubbleChart
from jbi100_app.views.parallelcoordinates import ParallelCoordinates  # Assuming you have a ParallelCoordinates class
from jbi100_app.config import COLORS, COLORS_BLIND, SEQUENTIAL_COLORS

from dash import html, dcc, State
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
        html.Div(
            children=[
                html.Button(
                    'Change Color Palette', 
                    id='change-color-btn', 
                    n_clicks=0,
                    style={
                        'margin-top': '20px',
                        'margin-left': '20px',
                        'background-color': '#ffffff',
                        'border': '1px solid #cccccc',
                        'cursor': 'pointer'
                    }
                )
            ],
            style={'position': 'absolute', 'top': '0', 'left': '0', 'z-index': '1000'}
        ),
        dcc.Store(id='color-palette-store', data={'palette': 'default'}),
        # Add a div with padding-top to push content below the button
        html.Div(
            style={'padding-top': '50px'},  # Adjust this value as necessary
            children=[
                # Top row
                html.Div(
                    className="row",
                    children=[
                        # Left column
                        html.Div(
                            className="six columns",
                            children=[parcoords]
                        ),
                        # Right column
                        html.Div(
                            className="six columns",
                            children=[linegraph]
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
                            children=[barchart]
                        ),
                        # Right column
                        html.Div(
                            className="six columns",
                            children=[bubblechart]
                        ),
                    ],
                ),
            ]
        ),
    ],
)



    @app.callback(
        Output('color-palette-store', 'data'),
        Input('change-color-btn', 'n_clicks'),
        State('color-palette-store', 'data')
    )
    def change_palette(n_clicks, data):
        if n_clicks % 2 == 0:
            # Set to default palette
            data['palette'] = 'default'
        else:
            # Set to color-blind palette
            data['palette'] = 'color_blind'
        return data

    

    @app.callback(
    Output(parcoords.html_id, 'figure'),
     Input(parcoords.html_id + '-dropdown', 'value')
    )
    def update_parcoords(dropdown_value):
        return parcoords.update(dropdown_value)

    @app.callback(
        Output(barchart.html_id, 'figure'),
        [Input(bubblechart.html_id, 'selectedData'),
        Input(barchart.html_id + '-dropdown', 'value'),
        Input('color-palette-store', 'data')]
        )
    def update_barchart(selected_data, dropdown_value, palette_store_data):
        palette_name = palette_store_data['palette']
        return barchart.update(dropdown_value, selected_data, palette_name)


    @app.callback(
        Output(bubblechart.html_id, 'figure'),
        [Input(barchart.html_id, 'selectedData'),
         Input(bubblechart.html_id + '-dropdown', 'value'),
         Input('color-palette-store', 'data')]
    )
    def update_bubblechart(dropdown_value, selected_data, palette_store_data):
        palette_name = palette_store_data['palette']
        return bubblechart.update(selected_data, dropdown_value, palette_name)

    
    @app.callback(
    Output(linegraph.html_id, 'figure'),
    [Input(bubblechart.html_id, 'selectedData'),
     Input(linegraph.html_id + '-dropdown', 'value'),
     Input('color-palette-store', 'data')]
    )
    def update_linegraph(selected_data_bubblechart, dropdown_value, palette_store_data):
        palette_name = palette_store_data['palette']

        if selected_data_bubblechart is None or not selected_data_bubblechart['points']:
            selected_occupations = dropdown_value
        else:
            selected_occupations = [point['customdata'] for point in selected_data_bubblechart['points']]           
    
        return linegraph.update(selected_occupations, palette_name)

    app.run_server(debug=True, dev_tools_ui=True)
