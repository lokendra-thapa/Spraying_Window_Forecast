
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import fetch
import visualization

app = dash.Dash(__name__)
server = app.server

# App Layout
app.layout = html.Div([
    html.H1("Live Weather Forecast & Spraying Window", style={'textAlign': 'center'}),
    
    # Location Input Form
    html.Div([
        html.Div([
            html.Label("Latitude:", style={'marginRight': '10px', 'fontWeight': 'bold'}),
            dcc.Input(
                id='latitude-input',
                type='number',
                value=None,
                step=0.000001,
                style={'width': '150px', 'marginRight': '20px'}
            ),
            html.Label("Longitude:", style={'marginRight': '10px', 'fontWeight': 'bold'}),
            dcc.Input(
                id='longitude-input',
                type='number',
                value=None,
                step=0.000001,
                style={'width': '150px', 'marginRight': '20px'}
            ),
            html.Button(
                'Update Location',
                id='update-location-button',
                style={
                    'backgroundColor': '#4CAF50',
                    'color': 'white',
                    'padding': '10px 20px',
                    'border': 'none',
                    'borderRadius': '4px',
                    'cursor': 'pointer'
                }
            )
        ], style={
            'display': 'flex',
            'justifyContent': 'center',
            'alignItems': 'center',
            'margin': '20px 0',
            'padding': '15px',
            'backgroundColor': '#f8f9fa',
            'borderRadius': '5px'
        })
    ]),

    dcc.Graph(id='live-graph'),

    html.Div([
        html.Label("Select Day:", style={'fontWeight': 'bold'}),
        dcc.Slider(
            id='day-slider',
            min=0,
            max=4,
            step=1,
            value=0,
            marks={i: f'Day {i+1}' for i in range(5)},
            included=False
        )
    ], style={'margin': '40px'}),

    dcc.Interval(
        id='interval-component',
        interval=15 * 1000,  
        n_intervals=0
    ),
    
    # Store for coordinates
    dcc.Store(id='coordinates-store', data=None, storage_type='local' )
])

# Callback to update coordinates store
@app.callback(
    Output('coordinates-store', 'data'),
    [
        Input('update-location-button', 'n_clicks'),
        Input('latitude-input', 'value'),
        Input('longitude-input', 'value')
    ],
    State('latitude-input', 'value'),
    State('longitude-input', 'value'),
    prevent_initial_call=True
)
def update_or_clear_coordinates(n_clicks, lat_input, lon_input, lat_state, lon_state):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    # If either input is cleared, clear the store
    if lat_input is None or lon_input is None:
        return None

    # If button is clicked and both values are present, update the store
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == 'update-location-button' and lat_state is not None and lon_state is not None:
        return {'lat': lat_state, 'lon': lon_state}

    # Otherwise, do not update
    return dash.no_update

# Auto-advance day slider every 10 seconds
# Reset day slider to 0 when location is updated
@app.callback(
    Output('day-slider', 'value'),
    [Input('interval-component', 'n_intervals'),
     Input('update-location-button', 'n_clicks')],
    prevent_initial_call=True
)
def update_day_slider(n_intervals, n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == 'update-location-button':
        return 0  # Reset to Day 1
    elif trigger_id == 'interval-component':
        return n_intervals % 5  # Auto-advance
    else:
        raise dash.exceptions.PreventUpdate

# Update the graph based on selected day and coordinates
@app.callback(
    Output('live-graph', 'figure'),
    [Input('day-slider', 'value'),
     Input('coordinates-store', 'data')]
)
def update_graph(selected_day, coordinates):
    if not coordinates or coordinates.get('lat') is None or coordinates.get('lon') is None:
        # Return an empty figure or a message
        return {
            "layout": {
                "xaxis": {"visible": False},
                "yaxis": {"visible": False},
                "annotations": [{
                    "text": "Please enter latitude and longitude to view the forecast.",
                    "xref": "paper", "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 20}
                }]
            }
        }
    # Fetch forecast data with the current coordinates
    forecast_data = fetch.fetch_weather_forecast(coordinates['lat'], coordinates['lon'])

    # Get 24 hours per day (assuming hourly data for 7 days)
    day_start = selected_day * 24
    day_end = (selected_day + 1) * 24
    filtered_data = forecast_data[day_start:day_end] if len(forecast_data) >= day_end else []

    if not filtered_data:
        return {
            "layout": {
                "xaxis": {"visible": False},
                "yaxis": {"visible": False},
                "annotations": [{
                    "text": "No forecast data available for this location/day.",
                    "xref": "paper", "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 20}
                }]
            }
        }


    return visualization.create_spraying_window_visualization(filtered_data)

if __name__ == '__main__':
    app.run(debug=True)
