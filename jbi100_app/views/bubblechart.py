import plotly.express as px
from dash import html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output

class BubbleChart(html.Div):
    def __init__(self, name, feature_x, feature_y, feature_size, df):
        self.html_id = name.lower().replace(" ", "-")
        self.df = df
        self.feature_x = feature_x
        self.feature_y = feature_y
        self.feature_size = feature_size

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
                dcc.Graph(id=self.html_id)
            ],
        )

    def update(self, selected_occupations, selected_data):
        fig = go.Figure()

        for occupation in selected_occupations:
            occupation_df = self.df[self.df['Occupation'] == occupation]
            x_values = occupation_df[self.feature_x]
            y_values = occupation_df[self.feature_y]
            size_values = occupation_df[self.feature_size] * 10
            fig.add_trace(go.Scatter(
                x=x_values, 
                y=y_values,
                mode='markers',
                marker=dict(
                    size=size_values,
                    sizemode='diameter'
                ),
                customdata=occupation_df['Occupation'],
                name=occupation
            ))
        
        fig.update_layout(
            yaxis_zeroline=False,
            xaxis_zeroline=False,
            dragmode='select'
        )


        # highlight points with selection other graph
        if selected_data is None:
            selected_index = selected_occupations  # show all
        elif selected_data['points']:
            selected_index = [  # show only selected indices
                x['x']
                for x in selected_data['points']
            ]

        # print(selected_index)
        
        new_data = [d for d in fig.data if d.customdata[0] in selected_index]
        fig.data = new_data
        

        print(fig.data)
        print(fig)

        return fig

