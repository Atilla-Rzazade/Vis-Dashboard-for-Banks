import plotly.express as px
from dash import html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from jbi100_app.config import COLORS, COLORS_BLIND


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

    def update(self, selected_occupations, selected_data, palette_name):
        # Generate the bar chart based on the occupations currently selected in the dropdown
        fig = go.Figure()

        colors = COLORS if palette_name == 'default' else COLORS_BLIND

        for occupation in selected_occupations:
            occupation_df = self.df[self.df['Occupation'] == occupation]
            x_values = [occupation]
            y_values = occupation_df[self.feature_y].values
            color = colors[self.df['Occupation'].tolist().index(occupation)] if occupation in self.df['Occupation'].tolist() else '#000'
            fig.add_trace(go.Bar(
                x=x_values, 
                y=y_values,
                name=occupation,
                marker=dict(color=color),  # Fallback color if not found
                hovertemplate='Value: %{y}<extra></extra>'  # Custom hover text
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
        

        return fig
