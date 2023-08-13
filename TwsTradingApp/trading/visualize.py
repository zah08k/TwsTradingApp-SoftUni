import plotly.offline as pyo
import plotly.graph_objs as go


def plot_pnl(cumulative_sum):
    data = [go.Scatter(x=list(range(len(cumulative_sum))), y=cumulative_sum, mode='lines+markers', name='Cumulative PnL')]
    layout = go.Layout()
    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(
        autosize=False,
        width=500,
        height=300,
        margin=dict(
            l=10,  # left margin
            r=10,  # right margin
            b=10,  # bottom margin
            t=20,  # top margin
            pad=10  # padding
        )
    )
    graphJSON = pyo.plot(fig, auto_open=False, output_type='div')
    return graphJSON

