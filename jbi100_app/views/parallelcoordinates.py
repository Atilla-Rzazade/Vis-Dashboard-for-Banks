from dash import html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import plotly.express as px


class ParallelCoordinates(html.Div):
    def __init__(self, name, df):
        self.html_id = name.lower().replace(" ", "-")
        self.df = df

        self.dropdown = dcc.Dropdown(
            id=self.html_id + '-dropdown',
            options=[{'label': i, 'value': i} for i in df['Income_Group'].unique()],
            value=df['Income_Group'].unique().tolist(),
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

    def update(self, selected_income_groups):
        df_selected = self.df[self.df['Income_Group'].isin(selected_income_groups)]
        fig = go.Figure(data=
            go.Parcoords(
                line = dict(color = df_selected['Income_Group'],  # Use the numerical income groups here
                        colorscale = px.colors.qualitative.Plotly,  # Define the colorscale
                        showscale = True),
                dimensions = [dict(range = [self.df['Loan_Type_Count'].min(), self.df['Loan_Type_Count'].max()],
                                label = loan_type, values = df_selected[df_selected['Type_of_Loan'] == loan_type]['Loan_Type_Count']) 
                            for loan_type in df_selected['Type_of_Loan'].unique()]
            )
        )
        return fig
