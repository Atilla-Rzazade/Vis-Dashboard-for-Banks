import plotly.express as px
from dash import html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from jbi100_app.config import COLORS


class LineGraph(html.Div):
    def __init__(self, name, feature_x, feature_y, df):
        self.html_id = name.lower().replace(" ", "-")
        self.df = df
        self.feature_x = feature_x
        self.feature_y = feature_y

        occupations = ['Architect', 'Developer', 'Engineer', 'Musician', 'Scientist', 'Writer']

        self.occupation_colors = {occupation: color for occupation, color in zip(self.df['Sorted_Occupation'], COLORS)}

        options = [{'label': occupation, 'value': occupation} for occupation in occupations if occupation in self.df['Occupation'].values]
        values = [occupation for occupation in occupations if occupation in self.df['Occupation'].values]

        self.dropdown = dcc.Dropdown(
            id=self.html_id + '-dropdown',
            options=options,
            value=values,
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

    def update(self, selected_occupations):
        fig = go.Figure()

        for occupation in selected_occupations:
            occupation_df = self.df[self.df['Occupation'] == occupation]
            x_values = occupation_df[self.feature_x]
            y_values = occupation_df[self.feature_y]
            fig.add_trace(go.Scatter(
                x=x_values, 
                y=y_values,
                mode='lines',
                name=occupation,
                line=dict(color=self.occupation_colors[occupation])
            ))

        return fig
