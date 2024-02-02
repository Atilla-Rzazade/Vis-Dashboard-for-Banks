import plotly.express as px
from dash import html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from jbi100_app.config import COLORS


class BarChart(html.Div):
    def __init__(self, name, feature_x, feature_y, df):
        self.html_id = name.lower().replace(" ", "-")
        self.df = df
        self.feature_x = feature_x
        self.feature_y = feature_y

        # Define the initial set of occupations to display
        initial_occupations = ['Architect', 'Developer', 'Engineer', 'Musician', 'Scientist', 'Writer']
        
        # Create a color mapping for all possible occupations, not just the initial set
        self.occupation_colors = {occupation: color for occupation, color in zip(df['Occupation'].unique(), COLORS)}

        # Create dropdown options for all occupations present in the dataframe
        options = [{'label': occupation, 'value': occupation} for occupation in df['Occupation'].unique()]

        # The initial value of the dropdown is set to the predefined list of occupations
        self.dropdown = dcc.Dropdown(
            id=self.html_id + '-dropdown',
            options=options,
            value=initial_occupations,  # Default value includes only the initial occupations
            multi=True
        )

        super().__init__(
            className="graph_card",
            children=[
                html.H6(name),
                self.dropdown,
                dcc.Graph(id=self.html_id, config={'modeBarButtonsToAdd':['select2d', 'lasso2d']})
            ],
        )

    def update(self, selected_occupations, selected_data):
        # Generate the bar chart based on the occupations currently selected in the dropdown
        fig = go.Figure()

        for occupation in selected_occupations:
            occupation_df = self.df[self.df['Occupation'] == occupation]
            x_values = [occupation]
            y_values = occupation_df[self.feature_y].values
            fig.add_trace(go.Bar(
                x=x_values, 
                y=y_values,
                name=occupation,
                marker=dict(color=self.occupation_colors.get(occupation, '#000'))  # Fallback color if not found
            ))

        fig.update_layout(
            yaxis_zeroline=False,
            xaxis_zeroline=False,
            dragmode='select',
        )


        # highlight points with selection other graph
        if selected_data is None:
            selected_index = selected_occupations  # show all
        elif selected_data['points']:
            selected_index = [  # show only selected indices
                x['customdata']
                for x in selected_data['points']
                
            ]

        
        new_data = [d for d in fig.data if d.name in selected_index]
        fig.data = new_data
        

        print(fig.data)

        return fig
