import plotly.graph_objs as go
from datetime import datetime
import numpy as np

def create_spraying_window_visualization(forecast_data):
    times = [datetime.fromisoformat(f['time']) for f in forecast_data]
    temps = [f['temperature'] for f in forecast_data]
    winds = [f['wind_speed'] for f in forecast_data]
    precp = [f['precipitation'] for f in forecast_data]

    def get_window(t, w, p):
        if 15 <= t <= 25 and w <= 1.5 and p < 0.05:
            return 1, 'green', 'Ideal'
        elif (1.5 < w <= 3.5 and 0.05 <= p < 0.2 and (10 <= t < 15 or 25 < t <= 35)) or ((10 <=t < 15 or 25 < t <= 35) and p < 0.2  and w <= 3.5) or (1.5 < w <= 3.5 and 10 <= t <= 35 and p < 0.2) or (0.05 <= p <0.2 and w <= 3.5 and 10 <= 35):
            return 0.5, 'yellow', 'Moderate'
        return 0, 'red', 'Unsuitable'

    statuses = [get_window(t, w, p) for t, w, p in zip(temps, winds, precp)]
    values = [s[0] for s in statuses]
    labels = [s[2] for s in statuses]

    fig = go.Figure()

    # Make customdata a 2D array matching the shape of z
    customdata_1d = list(zip(temps, winds, precp, labels))
    customdata_2d = np.tile(np.array(customdata_1d), (2, 1, 1))

    fig.add_trace(go.Heatmap(
        x=times, y=[0, 1], z=[values]*2,
        colorscale=[[0, "rgba(255,0,0,0.3)"], [0.5, "rgba(255,255,0,0.3)"], [1, "rgba(0,255,0,0.3)"]],
        zmin=0, zmax=1, showscale=False, opacity=0.9, name='Spraying Window',
        customdata=customdata_2d,
        hovertemplate=(
            '<b>%{x}</b><br><br>' +
            'Temperature: %{customdata[0]:.1f}°C<br>' +
            'Wind: %{customdata[1]:.1f} m/s<br>' +
            'Precipitation: %{customdata[2]:.2f} mm<br>' +
            'Condition: %{customdata[3]}<extra></extra>'
        ),
        ysrc='y5'
    ))

    fig.add_trace(go.Scatter(
        x=times, y=temps, mode='lines+markers', name='Temperature (°C)',
        line=dict(color='red'), yaxis='y2',
        hoverinfo='skip'
    ))

    fig.add_trace(go.Scatter(
        x=times, y=winds, mode='lines', name='Wind Speed (m/s)',
        line=dict(color='blue'), yaxis='y3',
        hoverinfo='skip'
    ))

    fig.add_trace(go.Bar(
        x=times, y=precp, name='Precipitation (mm)',
        marker_color='lightblue', opacity=1, yaxis='y4',
        hoverinfo='skip'
    ))

    fig.update_layout(
        height=700,
        title={'text': 'Integrated Weather Forecast & Spraying Window', 'x': 0.5, 'y': 0.95},
        annotations=[
            dict(text="Spraying Window Conditions", x=0.5, y=0.9, xref="paper", yref="paper", showarrow=False, font=dict(size=15)),
            dict(text="Precipitation (mm)", x=-0.04, y=0.5, xref="paper", yref="paper", textangle=-90, showarrow=False)
        ],
        hovermode='x unified',
        legend=dict(orientation='h', y=1.02, x=1, xanchor='right', bgcolor='rgba(255,255,255,0.8)'),
        yaxis5=dict(domain=[0, 0.85], showgrid=False, showticklabels=False, layer='below traces'),
        yaxis=dict(domain=[0, 0.85], showgrid=False, showticklabels=False),
        yaxis2=dict(overlaying='y', side='right', title='Temperature (°C)', range=[min(temps)-1, max(temps)+1]),
        yaxis3=dict(overlaying='y', side='left', showticklabels=False, range=[0, max(winds)+0.5]),
        yaxis4=dict(overlaying='y', side='left', position=0.0, range=[0, max(max(precp)+0.1, 0.5)], tickformat='.2f'),
        margin=dict(l=200, r=150, t=100)
    )

    # Add dummy traces for legend to indicate condition colors and labels
    for condition, color in zip(["Ideal", "Moderate", "Unsuitable"], ["green", "yellow", "red"]):
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color=color),
            name=condition,
            showlegend=True
        ))

    return fig
