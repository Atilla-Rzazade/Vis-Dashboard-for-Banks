import plotly.express as px
from dash import html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from jbi100_app.config import COLORS, COLORS_BLIND
import numpy as np

class BubbleChart(html.Div):
    def __init__(self, name, feature_x, feature_y, feature_size, df):
        self.html_id = name.lower().replace(" ", "-")
        self.df = df
        self.feature_x = feature_x
        self.feature_y = feature_y
        self.feature_size = feature_size

        # Define the initial set of occupations to display
        initial_occupations = ['Architect', 'Developer', 'Engineer', 'Musician', 'Scientist', 'Writer']
        
        # Create a color mapping for all possible occupations, not just the initial set
        self.occupation_colors = {occupation: color for occupation, color in zip(df['Occupation'].unique(), COLORS)}

        # Create dropdown options for all occupations present in the dataframe
        options = [{'label': occupation, 'value': occupation} for occupation in df['Occupation'].unique()]

        self.dropdown = dcc.Dropdown(
            id=self.html_id + '-dropdown',
            options=options,
            value=initial_occupations,
            multi=True
        )

        super().__init__(
            className="graph_card",
            children=[
                html.H6(name),
                self.dropdown,
                dcc.Graph(id=self.html_id)
            ],
        )

    def update(self, selected_occupations, selected_data, palette_name):
        fig = go.Figure()

        colors = COLORS if palette_name == 'default' else COLORS_BLIND

        # Create a list to hold the max size value for each occupation
        occupation_sizes = []
        for occupation in selected_occupations:
            occupation_df = self.df[self.df['Occupation'] == occupation]
            max_size = occupation_df[self.feature_size].max()  # Get the max size for current occupation
            occupation_sizes.append((max_size, occupation))

        # Sort the list by size in descending order
        occupation_sizes.sort(key=lambda x: x[0])

        # Now, add the traces based on the sorted occupations
        for _, occupation in occupation_sizes:
            occupation_df = self.df[self.df['Occupation'] == occupation]
            x_values = occupation_df[self.feature_x]
            y_values = occupation_df[self.feature_y]
            size_values = occupation_df[self.feature_size] * 10
            color = colors[self.df['Occupation'].tolist().index(occupation)] if occupation in self.df['Occupation'].tolist() else '#000'
            fig.add_trace(go.Scatter(
                x=x_values,
                y=y_values,
                mode='markers',
                marker=dict(
                    color=color,
                    size=size_values,
                    sizemode='diameter'
                ),
                customdata = np.stack((occupation_df['Occupation'], size_values/10), axis=-1),
                name=occupation,
                hovertemplate='Size: %{customdata[1]:.2f}<extra></extra>'  # Custom hover text

            ))

        fig.update_layout(
            yaxis_zeroline=False,
            xaxis_zeroline=False,
            dragmode='select',
            legend=dict(traceorder='normal')
        )

         # highlight points with selection other graph
        if selected_data is None:
            selected_index = selected_occupations  # show all
        elif selected_data['points']:
            selected_index = [  # show only selected indices
                x['x']
                for x in selected_data['points']
            ]
        
        new_data = [d for d in fig.data if d.customdata[0][0] in selected_index]
        fig.data = new_data
        

        return fig


