from dash import html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import plotly.express as px
from jbi100_app.config import SEQUENTIAL_COLORS


class ParallelCoordinates(html.Div):
    def __init__(self, name, df):
        self.html_id = name.lower().replace(" ", "-")
        self.df = df

        self.income_group_color_index = {income_group: i for i, income_group in enumerate(sorted(self.df['Income_Group'].unique()))}

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
        fig = go.Figure(data=go.Parcoords(
            line=dict(
                color=[self.income_group_color_index[ig] for ig in df_selected['Income_Group']],  # Map income group to its color index
                colorscale=[(i / (len(SEQUENTIAL_COLORS) - 1), color) for i, color in enumerate(SEQUENTIAL_COLORS)],  # Use the custom color scale
                showscale=False, # Disable default color scale
            ),
            dimensions=[dict(
                range=[self.df['Loan_Type_Count'].min(), self.df['Loan_Type_Count'].max()],
                label=loan_type, values=df_selected[df_selected['Type_of_Loan'] == loan_type]['Loan_Type_Count']
            ) for loan_type in df_selected['Type_of_Loan'].unique()]
        ))

        # Add dummy traces for custom legend entries
        for i, (income_group, color) in enumerate(zip(sorted(selected_income_groups), SEQUENTIAL_COLORS)):
            fig.add_trace(go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=10, color=color),
                legendgroup='Income_Group',
                showlegend=True,
                name=str(income_group)
            ))

        # Update layout to adjust the legend
        fig.update_layout(
            legend=dict(
                title='Income Group',
                traceorder='normal',
                itemsizing='constant'
            )
        )

        # Update layout to remove background and other adjustments
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',  # Transparent background for the entire figure
            plot_bgcolor='rgba(0,0,0,0)',   # Transparent background for the plotting area
            # Other layout adjustments if needed
        )

        fig.update_xaxes(
            tickvals=[],  # Removes all x-axis tick labels
        )

        fig.update_yaxes(
            tickvals=[],  # Removes all y-axis tick labels
        )


        return fig

