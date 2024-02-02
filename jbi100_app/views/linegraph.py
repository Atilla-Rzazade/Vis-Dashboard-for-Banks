import plotly.express as px
from dash import html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from jbi100_app.config import COLORS, COLORS_BLIND


class LineGraph(html.Div):
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

    def update(self, selected_occupations, palette_name):
        fig = go.Figure()

        colors = COLORS if palette_name == 'default' else COLORS_BLIND


        for occupation in selected_occupations:
            occupation_df = self.df[self.df['Occupation'] == occupation]
            x_values = occupation_df[self.feature_x]
            y_values = occupation_df[self.feature_y]
            color = colors[self.df['Occupation'].tolist().index(occupation)] if occupation in self.df['Occupation'].tolist() else '#000'
            fig.add_trace(go.Scatter(
                x=x_values, 
                y=y_values,
                mode='lines',
                name=occupation,
                line=dict(color=color)
            ))

        return fig
