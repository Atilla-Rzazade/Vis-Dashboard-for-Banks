import plotly.express as px
from dash import html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output

class BarChart(html.Div):
    def __init__(self, name, feature_x, feature_y, df):
        self.html_id = name.lower().replace(" ", "-")
        self.df = df
        self.feature_x = feature_x
        self.feature_y = feature_y

        self.dropdown = dcc.Dropdown(
            id=self.html_id + '-dropdown',
            options=[{'label': i, 'value': i} for i in df['Occupation'].unique()],
            value=df['Occupation'].unique().tolist(),
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

    def update(self, selected_occupations):
        fig = go.Figure()

        for occupation in selected_occupations:
            occupation_df = self.df[self.df['Occupation'] == occupation]
            x_values = [occupation]
            y_values = occupation_df[self.feature_y].values
            fig.add_trace(go.Bar(
                x=x_values, 
                y=y_values,
                name=occupation
            ))

        return fig
