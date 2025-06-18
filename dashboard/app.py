"""
SENTINEL Dashboard Application
Interactive web dashboard for geopolitical trade risk visualization
"""

import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import logging

from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# API base URL
API_BASE_URL = f"http://{settings.API_HOST}:{settings.API_PORT}{settings.API_PREFIX}"

# App layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("SENTINEL", className="text-primary mb-0"),
            html.H4("Fortune 500 Geopolitical Trade Risk Navigator", className="text-muted")
        ], width=8),
        dbc.Col([
            html.Div(id="last-updated", className="text-end")
        ], width=4)
    ], className="mb-4"),
    
    # Navigation tabs
    dbc.Tabs([
        dbc.Tab([
            # Dashboard Overview
            dbc.Row([
                # Key Metrics Cards
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="total-countries", className="card-title"),
                            html.P("Countries Monitored", className="card-text")
                        ])
                    ], className="text-center")
                ], width=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="total-suppliers", className="card-title"),
                            html.P("Active Suppliers", className="card-text")
                        ])
                    ], className="text-center")
                ], width=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="high-risk-countries", className="card-title text-danger"),
                            html.P("High-Risk Countries", className="card-text")
                        ])
                    ], className="text-center")
                ], width=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="active-events", className="card-title text-warning"),
                            html.P("Active Risk Events", className="card-text")
                        ])
                    ], className="text-center")
                ], width=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="avg-risk-score", className="card-title"),
                            html.P("Average Risk Score", className="card-text")
                        ])
                    ], className="text-center")
                ], width=2),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4(id="total-companies", className="card-title"),
                            html.P("Companies Tracked", className="card-text")
                        ])
                    ], className="text-center")
                ], width=2)
            ], className="mb-4"),
            
            # Charts Row
            dbc.Row([
                # Global Risk Heatmap
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Global Risk Heatmap"),
                        dbc.CardBody([
                            dcc.Graph(id="risk-heatmap")
                        ])
                    ])
                ], width=6),
                
                # Risk Distribution
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Risk Score Distribution"),
                        dbc.CardBody([
                            dcc.Graph(id="risk-distribution")
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),
            
            # Second Charts Row
            dbc.Row([
                # Recent Risk Events
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Recent Risk Events"),
                        dbc.CardBody([
                            html.Div(id="recent-events-table")
                        ])
                    ])
                ], width=6),
                
                # Risk Trends
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Risk Trends by Region"),
                        dbc.CardBody([
                            dcc.Graph(id="risk-trends")
                        ])
                    ])
                ], width=6)
            ])
        ], label="Dashboard Overview", tab_id="overview"),
        
        dbc.Tab([
            # Countries Analysis
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Country Risk Analysis"),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id="country-selector",
                                placeholder="Select a country...",
                                clearable=True
                            ),
                            html.Div(id="country-details", className="mt-3")
                        ])
                    ])
                ], width=12)
            ])
        ], label="Countries", tab_id="countries"),
        
        dbc.Tab([
            # Suppliers Analysis
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Supplier Risk Analysis"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dcc.Dropdown(
                                        id="industry-filter",
                                        placeholder="Filter by industry...",
                                        clearable=True
                                    )
                                ], width=4),
                                dbc.Col([
                                    dcc.Dropdown(
                                        id="tier-filter",
                                        placeholder="Filter by tier...",
                                        clearable=True
                                    )
                                ], width=4),
                                dbc.Col([
                                    dcc.Slider(
                                        id="risk-threshold",
                                        min=0,
                                        max=100,
                                        step=5,
                                        value=50,
                                        marks={i: str(i) for i in range(0, 101, 20)},
                                        tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], width=4)
                            ]),
                            dcc.Graph(id="supplier-risk-chart")
                        ])
                    ])
                ], width=12)
            ])
        ], label="Suppliers", tab_id="suppliers"),
        
        dbc.Tab([
            # Trade Routes Analysis
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Trade Route Vulnerability"),
                        dbc.CardBody([
                            dcc.Graph(id="trade-routes-map")
                        ])
                    ])
                ], width=12)
            ])
        ], label="Trade Routes", tab_id="routes"),
        
        dbc.Tab([
            # Companies Analysis
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Company Supply Chain Risk"),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id="company-selector",
                                placeholder="Select a company...",
                                clearable=True
                            ),
                            html.Div(id="company-risk-details", className="mt-3")
                        ])
                    ])
                ], width=12)
            ])
        ], label="Companies", tab_id="companies")
    ], id="main-tabs")
], fluid=True)

# Callback to update dashboard summary
@app.callback(
    [Output("total-countries", "children"),
     Output("total-suppliers", "children"),
     Output("high-risk-countries", "children"),
     Output("active-events", "children"),
     Output("avg-risk-score", "children"),
     Output("total-companies", "children"),
     Output("last-updated", "children")],
    [Input("main-tabs", "active_tab")]
)
def update_dashboard_summary(active_tab):
    """Update dashboard summary metrics"""
    try:
        # Fetch dashboard summary from API
        response = requests.get(f"{API_BASE_URL}/dashboard-summary")
        if response.status_code == 200:
            data = response.json()
            summary = data["summary"]
            risk_metrics = data["risk_metrics"]
            
            return (
                f"{summary['total_countries']:,}",
                f"{summary['total_suppliers']:,}",
                f"{summary['high_risk_countries']:,}",
                f"{summary['active_risk_events']:,}",
                f"{risk_metrics['average_country_risk']:.1f}",
                f"{summary['total_companies']:,}",
                f"Last Updated: {datetime.now().strftime('%H:%M:%S')}"
            )
        else:
            return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "Error"
    except Exception as e:
        logger.error(f"Error updating dashboard summary: {e}")
        return "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "Error"

# Callback to update risk heatmap
@app.callback(
    Output("risk-heatmap", "figure"),
    [Input("main-tabs", "active_tab")]
)
def update_risk_heatmap(active_tab):
    """Update global risk heatmap"""
    try:
        # Fetch countries data
        response = requests.get(f"{API_BASE_URL}/countries")
        if response.status_code == 200:
            data = response.json()
            countries = data["countries"]
            
            # Create heatmap data
            df = pd.DataFrame(countries)
            
            # Create choropleth map
            fig = px.choropleth(
                df,
                locations="country_code",
                color="risk_score",
                hover_name="country_name",
                color_continuous_scale="RdYlGn_r",
                range_color=[0, 100],
                title="Global Risk Heatmap"
            )
            
            fig.update_layout(
                height=500,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            return fig
        else:
            return go.Figure().add_annotation(text="No data available", showarrow=False)
    except Exception as e:
        logger.error(f"Error updating risk heatmap: {e}")
        return go.Figure().add_annotation(text="Error loading data", showarrow=False)

# Callback to update risk distribution
@app.callback(
    Output("risk-distribution", "figure"),
    [Input("main-tabs", "active_tab")]
)
def update_risk_distribution(active_tab):
    """Update risk score distribution chart"""
    try:
        # Fetch countries data
        response = requests.get(f"{API_BASE_URL}/countries")
        if response.status_code == 200:
            data = response.json()
            countries = data["countries"]
            
            # Create distribution data
            risk_scores = [c["risk_score"] for c in countries]
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=risk_scores,
                nbinsx=20,
                name="Risk Score Distribution",
                marker_color="lightblue"
            ))
            
            fig.update_layout(
                title="Risk Score Distribution",
                xaxis_title="Risk Score",
                yaxis_title="Number of Countries",
                height=400,
                showlegend=False
            )
            
            return fig
        else:
            return go.Figure().add_annotation(text="No data available", showarrow=False)
    except Exception as e:
        logger.error(f"Error updating risk distribution: {e}")
        return go.Figure().add_annotation(text="Error loading data", showarrow=False)

# Callback to update recent events table
@app.callback(
    Output("recent-events-table", "children"),
    [Input("main-tabs", "active_tab")]
)
def update_recent_events(active_tab):
    """Update recent risk events table"""
    try:
        # Fetch recent risk events
        response = requests.get(f"{API_BASE_URL}/risk-events?limit=10")
        if response.status_code == 200:
            data = response.json()
            events = data["alerts"]
            
            if not events:
                return html.P("No recent events", className="text-muted")
            
            # Create table rows
            table_rows = []
            for event in events[:5]:  # Show top 5 events
                severity_color = "danger" if event["severity"] >= 70 else "warning" if event["severity"] >= 40 else "success"
                
                row = dbc.Row([
                    dbc.Col(event["title"], width=6),
                    dbc.Col(event["event_type"], width=2),
                    dbc.Col([
                        dbc.Badge(f"{event['severity']:.0f}", color=severity_color)
                    ], width=2),
                    dbc.Col(event["country"] or "N/A", width=2)
                ], className="mb-2")
                table_rows.append(row)
            
            return table_rows
        else:
            return html.P("No events available", className="text-muted")
    except Exception as e:
        logger.error(f"Error updating recent events: {e}")
        return html.P("Error loading events", className="text-danger")

# Callback to update risk trends
@app.callback(
    Output("risk-trends", "figure"),
    [Input("main-tabs", "active_tab")]
)
def update_risk_trends(active_tab):
    """Update risk trends by region"""
    try:
        # Fetch regions summary
        response = requests.get(f"{API_BASE_URL}/countries/regions/summary")
        if response.status_code == 200:
            data = response.json()
            regions = data["regions"]
            
            # Create bar chart
            fig = go.Figure()
            
            region_names = [r["region"] for r in regions]
            avg_risks = [r["average_risk_score"] for r in regions]
            
            fig.add_trace(go.Bar(
                x=region_names,
                y=avg_risks,
                marker_color="lightcoral",
                name="Average Risk Score"
            ))
            
            fig.update_layout(
                title="Average Risk Score by Region",
                xaxis_title="Region",
                yaxis_title="Average Risk Score",
                height=400,
                showlegend=False
            )
            
            return fig
        else:
            return go.Figure().add_annotation(text="No data available", showarrow=False)
    except Exception as e:
        logger.error(f"Error updating risk trends: {e}")
        return go.Figure().add_annotation(text="Error loading data", showarrow=False)

# Callback to populate country selector
@app.callback(
    Output("country-selector", "options"),
    [Input("main-tabs", "active_tab")]
)
def populate_country_selector(active_tab):
    """Populate country dropdown"""
    try:
        response = requests.get(f"{API_BASE_URL}/countries?limit=1000")
        if response.status_code == 200:
            data = response.json()
            countries = data["countries"]
            
            options = [
                {"label": f"{c['country_name']} ({c['country_code']})", "value": c["id"]}
                for c in countries
            ]
            
            return options
        else:
            return []
    except Exception as e:
        logger.error(f"Error populating country selector: {e}")
        return []

# Callback to update country details
@app.callback(
    Output("country-details", "children"),
    [Input("country-selector", "value")]
)
def update_country_details(country_id):
    """Update country details when selected"""
    if not country_id:
        return html.P("Select a country to view details", className="text-muted")
    
    try:
        response = requests.get(f"{API_BASE_URL}/countries/{country_id}")
        if response.status_code == 200:
            country = response.json()
            
            return dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Country Information"),
                        dbc.CardBody([
                            html.H5(country["country_name"]),
                            html.P(f"Region: {country['region']}"),
                            html.P(f"GDP: ${country['gdp_usd']:,}"),
                            html.P(f"Population: {country['population']:,}"),
                            html.P(f"Risk Score: {country['risk_score']:.1f}")
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Risk Metrics"),
                        dbc.CardBody([
                            html.P(f"Political Stability: {country['political_stability_index']:.1f}"),
                            html.P(f"Economic Freedom: {country['economic_freedom_index']:.1f}"),
                            html.P(f"Corruption Index: {country['corruption_perception_index']:.1f}"),
                            html.P(f"Suppliers: {country['statistics']['supplier_count']:,}"),
                            html.P(f"Active Events: {country['statistics']['active_risk_events']:,}")
                        ])
                    ])
                ], width=6)
            ])
        else:
            return html.P("Error loading country details", className="text-danger")
    except Exception as e:
        logger.error(f"Error updating country details: {e}")
        return html.P("Error loading country details", className="text-danger")

if __name__ == "__main__":
    app.run_server(
        host=settings.DASHBOARD_HOST,
        port=settings.DASHBOARD_PORT,
        debug=settings.DEBUG
    ) 