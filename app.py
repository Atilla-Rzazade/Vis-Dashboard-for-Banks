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
    print(top_left_data)
    top_right_data = data[1]
    bottom_left_data = data[2]
    bottom_right_data = data[3]
    income_group_dict = data[4]
    print(income_group_dict)

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
    [Input(barchart.html_id, 'selectedData'),
     Input(parcoords.html_id + '-dropdown', 'value')]
    )
    def update_parcoords(selected_data, dropdown_value):
        ctx = dash.callback_context
        if not ctx.triggered or ctx.triggered[0]['prop_id'].split('.')[0] == barchart.html_id:
            if selected_data is None:
                selected_income_groups = dropdown_value
            else:
                selected_occupations = [point['x'] for point in selected_data['points']]
                selected_income_groups = []
                for occupation in selected_occupations:
                    for income_group, occupations in income_group_dict.items():
                        if occupation in occupations:
                            selected_income_groups.append(int(income_group))
                                
            return parcoords.update(selected_income_groups)
        else:
            return dash.no_update

    @app.callback(
        Output(barchart.html_id, 'figure'),
        [Input(parcoords.html_id, 'restyleData'),
        Input(barchart.html_id + '-dropdown', 'value')]
    )
    def update_barchart(restyle_data, dropdown_value):
        ctx = dash.callback_context
        if not ctx.triggered or ctx.triggered[0]['prop_id'].split('.')[0] == parcoords.html_id:
            if restyle_data is None or len(restyle_data) == 0:
                return barchart.update(dropdown_value)
            selected_occupations = []
            # Iterate over all dimensions representing occupations
            for i in range(9):  # Adjust this range according to the number of dimensions
                dimension_range = restyle_data[0].get(f'dimensions[{i}].constraintrange')
                if dimension_range is not None:
                    # Map this range back to the corresponding income groups
                    selected_income_groups = map_range_to_income_groups(dimension_range)
                    # Determine the selected occupations based on the selected income groups
                    for income_group in selected_income_groups:
                        selected_occupations.extend(income_group_dict[str(income_group)])
            if len(selected_occupations) == 0:
                return barchart.update(dropdown_value)
            return barchart.update(selected_occupations)
        else:
            return dash.no_update


    def map_range_to_income_groups(selected_range):
        min_value, max_value = selected_range[0]
        selected_income_groups = []

        # Iterate over the rows in the data
        for _, row in top_left_data.iterrows():
            # Check if the Loan_Type_Count falls within the selected range
            if min_value <= row['Loan_Type_Count'] <= max_value:
                # If it does, add the corresponding Income_Group to selected_income_groups
                selected_income_groups.append(row['Income_Group'])

        return list(set(selected_income_groups))
    
    @app.callback(
        Output(bubblechart.html_id, 'figure'),
        [Input(linegraph.html_id, 'clickData'),
        Input(bubblechart.html_id + '-dropdown', 'value')]
    )
    def update_bubblechart(selected_data, dropdown_value):
        if selected_data is None:
            selected_occupations = dropdown_value
        else:

            selected_occupations = [point['x'] for point in selected_data['points']]
        return bubblechart.update(selected_occupations)
    

    @app.callback(
    Output(linegraph.html_id, 'figure'),
    [Input(bubblechart.html_id, 'selectedData'),
     Input(linegraph.html_id + '-dropdown', 'value')]
    )
    def update_linegraph(selected_data, dropdown_value):
        if selected_data is None:
            selected_occupations = dropdown_value
        else:
            selected_occupations = [point['customdata'] for point in selected_data['points']]           
        return linegraph.update(selected_occupations)

   


    app.run_server(debug=False, dev_tools_ui=False)
