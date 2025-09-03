import requests
import dash
from dash import dcc, html, callback, Input, Output, State, dash_table
import plotly.graph_objs as go
import pandas as pd


def build_dash_app():
    app = dash.Dash(__name__, requests_pathname_prefix="/app/")
    server = app.server

    # Custom CSS for modern styling
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <style>
                body { 
                    font-family: 'Inter', 'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 0;
                    min-height: 100vh;
                    font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
                }
                .main-container {
                    background: white;
                    border-radius: 16px;
                    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                    margin: 20px auto;
                    max-width: 1200px;
                    overflow: hidden;
                }
                .header {
                    background: linear-gradient(135deg, rgba(12, 74, 110, 0.95) 0%, rgba(7, 89, 133, 0.95) 25%, rgba(3, 105, 161, 0.95) 50%, rgba(2, 132, 199, 0.95) 75%, rgba(14, 165, 233, 0.95) 100%);
                    backdrop-filter: blur(20px);
                    -webkit-backdrop-filter: blur(20px);
                    color: white;
                    padding: 20px 20px;
                    text-align: center;
                    position: relative;
                    overflow: hidden;
                    min-height: 100px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    transition: all 0.3s ease;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }
                .header:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }
                .feature-card {
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }
                .feature-card:hover {
                    transform: translateY(-8px) scale(1.02);
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15), 0 10px 20px rgba(0, 0, 0, 0.1);
                }
                .header::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: 
                        radial-gradient(circle at 20% 30%, rgba(34, 197, 94, 0.15) 0%, transparent 40%),
                        radial-gradient(circle at 80% 20%, rgba(16, 185, 129, 0.12) 0%, transparent 45%),
                        radial-gradient(circle at 60% 80%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 10% 70%, rgba(168, 85, 247, 0.08) 0%, transparent 35%);
                    pointer-events: none;
                }
                .header::after {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background-image: 
                        radial-gradient(circle at 1px 1px, rgba(255,255,255,0.1) 1px, transparent 0);
                    background-size: 20px 20px;
                    opacity: 0.3;
                    pointer-events: none;
                }
                .header h1 {
                    margin: 0 0 6px 0;
                    font-size: 1.8rem;
                    font-weight: 800;
                    letter-spacing: -0.01em;
                    background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 50%, #e0f2fe 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.15);
                    position: relative;
                    z-index: 1;
                    line-height: 1.1;
                }
                .header p {
                    margin: 8px 0 0 0;
                    opacity: 0.8;
                    font-size: 1.1rem;
                    font-weight: 400;
                    letter-spacing: 0.01em;
                    position: relative;
                    z-index: 1;
                    max-width: 1200px;
                    margin-left: auto;
                    margin-right: auto;
                }
                .header .subtitle {
                    margin: 4px 0 0 0;
                    opacity: 0.6;
                    font-size: 0.9rem;
                    font-weight: 300;
                    letter-spacing: 0.05em;
                    text-transform: uppercase;
                    position: relative;
                    z-index: 1;
                    max-width: 1100px;
                    margin-left: auto;
                    margin-right: auto;
                }
                .header .features {
                    margin: 8px 0 0 0;
                    opacity: 0.7;
                    font-size: 0.9rem;
                    font-weight: 400;
                    position: relative;
                    z-index: 1;
                    max-width: 1200px;
                    margin-left: auto;
                    margin-right: auto;
                    line-height: 1.4;
                }
                .header-content {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    max-width: 1200px;
                    margin: 0 auto;
                    position: relative;
                    z-index: 1;
                }
                .header-left {
                    text-align: left;
                    flex: 1;
                }
                .header-right {
                    text-align: right;
                    flex: 1;
                }
                h1.header-compact {
                    margin: 0 0 12px 0;
                    font-size: 4rem;
                    font-weight: 900;
                    letter-spacing: -0.02em;
                    font-family: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 30%, #e0f2fe 60%, #bae6fd 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    text-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    line-height: 0.8;
                    animation: shimmer 3s ease-in-out infinite;
                    position: relative;
                }
                @keyframes shimmer {
                    0%, 100% { 
                        background-position: 0% 50%;
                        filter: brightness(1);
                    }
                    50% { 
                        background-position: 100% 50%;
                        filter: brightness(1.1);
                    }
                }
                p.header-compact.tagline {
                    margin: 0;
                    opacity: 0.9;
                    font-size: 1rem;
                    font-weight: 500;
                    letter-spacing: 0.05em;
                    line-height: 1.2;
                    text-transform: uppercase;
                    font-family: 'Inter', 'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    animation: fadeInUp 1s ease-out 0.5s both;
                }
                @keyframes fadeInUp {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 0.9;
                        transform: translateY(0);
                    }
                }
                .header-compact .features {
                    margin: 0;
                    opacity: 0.7;
                    font-size: 0.65rem;
                    font-weight: 400;
                    line-height: 1.2;
                }
                .metric-card {
                    background: white;
                    border-radius: 16px;
                    padding: 24px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    border-left: 4px solid #3b82f6;
                    margin: 8px;
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                }
                .metric-card:hover {
                    transform: translateY(-4px);
                    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                }
                .metric-card::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: linear-gradient(90deg, #3b82f6, #1d4ed8);
                    opacity: 0;
                    transition: opacity 0.3s ease;
                }
                .metric-card:hover::before {
                    opacity: 1;
                }
                .metric-value {
                    font-size: 2.5rem;
                    font-weight: 800;
                    color: #1e3a8a;
                    margin: 0;
                    line-height: 1;
                }
                .metric-label {
                    color: #6b7280;
                    font-size: 0.875rem;
                    margin: 8px 0 0 0;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    font-weight: 500;
                }
                .metric-trend {
                    display: flex;
                    align-items: center;
                    margin-top: 8px;
                    font-size: 0.75rem;
                    font-weight: 600;
                }
                .trend-up {
                    color: #10b981;
                }
                .trend-down {
                    color: #ef4444;
                }
                .trend-neutral {
                    color: #6b7280;
                }
                .progress-bar {
                    width: 100%;
                    height: 6px;
                    background: #e5e7eb;
                    border-radius: 3px;
                    margin-top: 12px;
                    overflow: hidden;
                }
                .progress-fill {
                    height: 100%;
                    background: linear-gradient(90deg, #3b82f6, #1d4ed8);
                    border-radius: 3px;
                    transition: width 0.8s ease;
                }
                .btn-primary {
                    background: linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%);
                    color: white;
                    border: none;
                    padding: 16px 32px;
                    border-radius: 16px;
                    font-weight: 700;
                    font-size: 1.1rem;
                    cursor: pointer;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    box-shadow: 0 12px 30px rgba(16, 185, 129, 0.4), 0 6px 15px rgba(16, 185, 129, 0.2);
                    position: relative;
                    overflow: hidden;
                    text-transform: uppercase;
                    letter-spacing: 0.8px;
                }
                .btn-primary::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                    transition: left 0.5s ease;
                }
                .btn-primary:hover::before {
                    left: 100%;
                }
                .btn-primary:hover {
                    transform: translateY(-3px) scale(1.02);
                    box-shadow: 0 20px 40px rgba(16, 185, 129, 0.5), 0 10px 20px rgba(16, 185, 129, 0.3);
                    background: linear-gradient(135deg, #34d399 0%, #10b981 50%, #059669 100%);
                }
                .btn-primary:active {
                    transform: translateY(-1px);
                    box-shadow: 0 8px 16px -4px rgba(16, 185, 129, 0.4);
                }
                .btn-secondary {
                    background: #f3f4f6;
                    color: #374151;
                    border: 1px solid #d1d5db;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }
                .btn-secondary:hover {
                    background: #e5e7eb;
                }
                .tabs-container {
                    background: #f8fafc;
                    border-radius: 12px;
                    padding: 8px;
                    margin: 20px;
                }
                .tab-content {
                    padding: 24px;
                    background: white;
                    border-radius: 8px;
                    margin-top: 16px;
                }
                .insight-card {
                    background: white;
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 16px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    border-left: 4px solid #3b82f6;
                    transition: all 0.2s ease;
                }
                .insight-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                }
                .insight-card.beneficial {
                    border-left-color: #10b981;
                    background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
                }
                .insight-card.concerning {
                    border-left-color: #ef4444;
                    background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
                }
                .confidence-badge {
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }
                .confidence-high {
                    background: #10b981;
                    color: white;
                }
                .confidence-moderate {
                    background: #f59e0b;
                    color: white;
                }
                .confidence-low {
                    background: #6b7280;
                    color: white;
                }
                .action-plan {
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 16px;
                    margin-top: 12px;
                }
                .summary-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 16px;
                    margin: 5px 20px;
                }
                .loading-spinner {
                    display: inline-block;
                    width: 20px;
                    height: 20px;
                    border: 3px solid #f3f3f3;
                    border-top: 3px solid #3b82f6;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                .fade-in {
                    animation: fadeIn 0.5s ease-in;
                }
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .pulse {
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }
                .success-message {
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                    padding: 12px 20px;
                    border-radius: 8px;
                    margin: 16px 0;
                    animation: slideIn 0.3s ease-out;
                }
                @keyframes slideIn {
                    from { transform: translateX(-100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes float {
                    0%, 100% { transform: translateY(0px) rotate(0deg); }
                    25% { transform: translateY(-10px) rotate(1deg); }
                    50% { transform: translateY(-5px) rotate(0deg); }
                    75% { transform: translateY(-15px) rotate(-1deg); }
                }
                @media (max-width: 768px) {
                    .main-container {
                        margin: 10px;
                        border-radius: 8px;
                    }
                    .header {
                        padding: 32px 16px;
                    }
                    .header h1 {
                        font-size: 2.5rem;
                        letter-spacing: -0.01em;
                    }
                    .header p {
                        font-size: 1.1rem;
                    }
                    .header .subtitle {
                        font-size: 0.9rem;
                    }
                    .btn-primary {
                        padding: 14px 28px;
                        font-size: 1rem;
                    }
                    .summary-grid {
                        grid-template-columns: 1fr;
                        margin: 16px;
                    }
                    .tab-content {
                        padding: 16px;
                    }
                    .metric-card {
                        padding: 20px;
                    }
                    .metric-value {
                        font-size: 2rem;
                    }
                }
                @media (max-width: 480px) {
                    .header h1 {
                        font-size: 2rem;
                    }
                    .header p {
                        font-size: 1rem;
                    }
                    .header .subtitle {
                        font-size: 0.8rem;
                    }
                }
            </style>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''

    app.layout = html.Div([
        html.Div([
            # Header
            html.Div([
                html.Div([
                    html.H1("Metabolic BioTwin", className="header-compact"),
                    html.P("Your Personal Health Intelligence Platform", className="header-compact tagline"),
                ], style={"textAlign":"center", "position":"relative", "zIndex":"1"}),
                dcc.Store(id="session-id", data=None),
            ], className="header"),

            # Summary Metrics
            html.Div(id="summary-metrics", className="summary-grid"),

            # Tabs
            html.Div([
                dcc.Tabs(
                    id="tabs",
                    value="timeline",
                    children=[
                        dcc.Tab(label="Timeline", value="timeline", className="tab"),
                        dcc.Tab(label="Meals", value="meals", className="tab"),
                        dcc.Tab(label="Insights", value="insights", className="tab"),
                    ],
                    className="tabs-container"
                ),
                html.Div(id="tab-content", className="tab-content"),
            ]),
            # Get Started Button Section (integrated with the journey section)
            html.Div([
                html.Button("Get Started", id="btn-demo", className="btn-primary"),
                html.P("Click to explore with sample health data", 
                       style={"margin":"12px 0 0 0", "color":"#6b7280", "fontSize":"0.9rem", "fontFamily":"'Inter', 'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", "fontWeight":"400"}),
                html.Div(id="ingest-status", style={"marginTop":"8px", "color":"#374151", "fontWeight":"500", "fontSize":"0.9rem"})
            ], id="get-started-section", style={"textAlign":"center", "padding":"20px 0", "display":"none"}),

        ], className="main-container"),
        dcc.Download(id="download-meals")
    ])

    @callback(
        Output("get-started-section","style"),
        Input("session-id","data")
    )
    def toggle_get_started_button(sid):
        if sid:
            return {"textAlign":"center", "padding":"20px 0", "display":"none"}
        else:
            return {"textAlign":"center", "padding":"20px 0", "display":"block"}

    @callback(
        Output("session-id","data"), Output("ingest-status","children"),
        Input("btn-demo","n_clicks"), prevent_initial_call=True
    )
    def load_demo(_):
        r = requests.post("http://localhost:8000/api/ingest", data={"use_demo": "true"})
        js = r.json()
        return js["session_id"], f"✅ Loaded demo data: {js['rows_daily']} days, {js['rows_meals']} meals"



    @callback(
        Output("summary-metrics","children"),
        Input("session-id","data")
    )
    def update_summary_metrics(sid):
        if not sid:
            return html.Div([
                html.Div([
                    html.Div([
                        html.H3("", style={"fontSize":"3rem", "margin":"0 0 24px 0"}),
                        html.H4("Your Health Journey Starts Here", style={"margin":"0 0 12px 0", "color":"#1f2937", "fontWeight":"700", "fontSize":"1.5rem", "fontFamily":"'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", "letterSpacing":"-0.01em"}),
                        html.P("Discover how your daily habits, sleep patterns, and nutrition choices impact your metabolic health with AI-powered insights", 
                               style={"margin":"0 0 24px 0", "color":"#4b5563", "fontSize":"1rem", "lineHeight":"1.5", "maxWidth":"800px", "marginLeft":"auto", "marginRight":"auto", "fontFamily":"'Inter', 'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", "fontWeight":"400"}),
                        html.Div([
                            html.Div([
                                html.H5("Metabolic Analysis", style={"margin":"0 0 8px 0", "color":"#1f2937", "fontWeight":"600", "fontSize":"1.1rem", "fontFamily":"'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", "letterSpacing":"-0.01em"}),
                                html.P("Track glucose patterns and metabolic health", style={"margin":"0", "color":"#6b7280", "fontSize":"0.9rem", "fontFamily":"'Inter', 'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"})
                            ], className="feature-card", style={"textAlign":"center", "padding":"24px", "background":"linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)", "borderRadius":"16px", "border":"1px solid #bae6fd", "boxShadow":"0 8px 25px rgba(59, 130, 246, 0.15), 0 4px 12px rgba(59, 130, 246, 0.1)", "cursor":"pointer"}),
                            html.Div([
                                html.H5("Sleep Optimization", style={"margin":"0 0 8px 0", "color":"#1f2937", "fontWeight":"600", "fontSize":"1.1rem", "fontFamily":"'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", "letterSpacing":"-0.01em"}),
                                html.P("Understand sleep quality and recovery patterns", style={"margin":"0", "color":"#6b7280", "fontSize":"0.9rem", "fontFamily":"'Inter', 'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"})
                            ], className="feature-card", style={"textAlign":"center", "padding":"24px", "background":"linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)", "borderRadius":"16px", "border":"1px solid #bbf7d0", "boxShadow":"0 8px 25px rgba(34, 197, 94, 0.15), 0 4px 12px rgba(34, 197, 94, 0.1)", "cursor":"pointer"}),
                            html.Div([
                                html.H5("Nutrition Insights", style={"margin":"0 0 8px 0", "color":"#1f2937", "fontWeight":"600", "fontSize":"1.1rem", "fontFamily":"'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", "letterSpacing":"-0.01em"}),
                                html.P("Analyze meal timing and nutritional impact", style={"margin":"0", "color":"#6b7280", "fontSize":"0.9rem", "fontFamily":"'Inter', 'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"})
                            ], className="feature-card", style={"textAlign":"center", "padding":"24px", "background":"linear-gradient(135deg, #fefce8 0%, #fef3c7 100%)", "borderRadius":"16px", "border":"1px solid #fde68a", "boxShadow":"0 8px 25px rgba(245, 158, 11, 0.15), 0 4px 12px rgba(245, 158, 11, 0.1)", "cursor":"pointer"})
                        ], style={"display":"grid", "gridTemplateColumns":"repeat(auto-fit, minmax(250px, 1fr))", "gap":"24px", "marginTop":"32px", "maxWidth":"900px", "marginLeft":"auto", "marginRight":"auto"})
                    ], style={"textAlign":"center", "padding":"10px 15px", "background":"white", "borderRadius":"16px", "boxShadow":"0 4px 6px -1px rgba(0, 0, 0, 0.1)"})
                ], className="summary-grid")
            ])
        
        try:
            # Get timeline data for summary
            tj = requests.get("http://localhost:8000/api/timeline", params={"session_id": sid}).json()
            
            # Calculate summary stats
            fg_values = [float(x) for x in tj["fg_fast_mgdl"] if x and x != 0]
            sleep_values = [float(x) for x in tj["sleep_hours"] if x and x != 0]
            
            avg_fg = round(sum(fg_values) / len(fg_values), 1) if fg_values else 0
            avg_sleep = round(sum(sleep_values) / len(sleep_values), 1) if sleep_values else 0
            
            # Get insights count
            ij = requests.get("http://localhost:8000/api/insights", params={"session_id": sid}).json()
            insights_count = len(ij.get("cards", []))
            
            # Get meals count
            mj = requests.get("http://localhost:8000/api/meals", params={"session_id": sid}).json()
            meals_count = len(mj.get("meals", []))
            
            # Calculate trends (simple comparison of first vs last 7 days)
            fg_trend = "neutral"
            sleep_trend = "neutral"
            if len(fg_values) >= 14:
                first_week_fg = sum(fg_values[:7]) / 7
                last_week_fg = sum(fg_values[-7:]) / 7
                fg_trend = "down" if last_week_fg < first_week_fg else "up" if last_week_fg > first_week_fg else "neutral"
            
            if len(sleep_values) >= 14:
                first_week_sleep = sum(sleep_values[:7]) / 7
                last_week_sleep = sum(sleep_values[-7:]) / 7
                sleep_trend = "up" if last_week_sleep > first_week_sleep else "down" if last_week_sleep < first_week_sleep else "neutral"
            
            # Calculate progress percentages (relative to ideal targets)
            fg_progress = min(100, max(0, (100 - avg_fg) / 20 * 100))  # Ideal: 80-100 mg/dL
            sleep_progress = min(100, max(0, avg_sleep / 8 * 100))  # Ideal: 7-8 hours
            
            return html.Div([
                html.Div([
                    html.H3(f"{avg_fg}", className="metric-value"),
                    html.P("Avg Fasting Glucose (mg/dL)", className="metric-label"),
                    html.Div([
                        html.Span("📈" if fg_trend == "up" else "📉" if fg_trend == "down" else "➡️"),
                        html.Span(f" {fg_trend.upper()}", className=f"trend-{fg_trend}")
                    ], className="metric-trend"),
                    html.Div([
                        html.Div(style={"width": f"{fg_progress}%", "height": "100%"}, className="progress-fill")
                    ], className="progress-bar")
                ], className="metric-card"),
                html.Div([
                    html.H3(f"{avg_sleep}", className="metric-value"),
                    html.P("Avg Sleep (hours)", className="metric-label"),
                    html.Div([
                        html.Span("📈" if sleep_trend == "up" else "📉" if sleep_trend == "down" else "➡️"),
                        html.Span(f" {sleep_trend.upper()}", className=f"trend-{sleep_trend}")
                    ], className="metric-trend"),
                    html.Div([
                        html.Div(style={"width": f"{sleep_progress}%", "height": "100%"}, className="progress-fill")
                    ], className="progress-bar")
                ], className="metric-card"),
                html.Div([
                    html.H3(f"{meals_count}", className="metric-value"),
                    html.P("Total Meals Tracked", className="metric-label"),
                    html.Div([
                        html.Span("📊"),
                        html.Span(" TRACKING", className="trend-neutral")
                    ], className="metric-trend"),
                    html.Div([
                        html.Div(style={"width": "100%", "height": "100%"}, className="progress-fill")
                    ], className="progress-bar")
                ], className="metric-card"),
                html.Div([
                    html.H3(f"{insights_count}", className="metric-value"),
                    html.P("AI Insights Generated", className="metric-label"),
                    html.Div([
                        html.Span("🤖"),
                        html.Span(" ACTIVE", className="trend-neutral")
                    ], className="metric-trend"),
                    html.Div([
                        html.Div(style={"width": "100%", "height": "100%"}, className="progress-fill")
                    ], className="progress-bar")
                ], className="metric-card"),
            ])
        except:
            return html.Div("Error loading summary metrics.", style={"textAlign":"center","color":"#ef4444","padding":"40px"})

    @callback(Output("tab-content","children"),
              Input("tabs","value"), State("session-id","data"))
    def render_tab(tab, sid):
        if not sid:
            return html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            # Animated background elements
                            html.Div([
                                html.Div("", style={"position":"absolute", "top":"-20%", "left":"-10%", "width":"120px", "height":"120px", "background":"linear-gradient(45deg, rgba(59, 130, 246, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%)", "borderRadius":"50%", "animation":"float 6s ease-in-out infinite"}),
                                html.Div("", style={"position":"absolute", "top":"10%", "right":"-5%", "width":"80px", "height":"80px", "background":"linear-gradient(45deg, rgba(16, 185, 129, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%)", "borderRadius":"50%", "animation":"float 8s ease-in-out infinite reverse"}),
                                html.Div("", style={"position":"absolute", "bottom":"-15%", "left":"20%", "width":"60px", "height":"60px", "background":"linear-gradient(45deg, rgba(99, 102, 241, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%)", "borderRadius":"50%", "animation":"float 7s ease-in-out infinite"}),
                            ], style={"position":"absolute", "top":"0", "left":"0", "right":"0", "bottom":"0", "overflow":"hidden", "pointerEvents":"none"}),
                            
                            # Main content
                            html.Div([
                                # Icon with gradient and glow
                                html.Div([
                                    html.Div("", style={"width":"24px", "height":"24px", "background":"linear-gradient(45deg, #3b82f6 0%, #10b981 100%)", "borderRadius":"50%", "margin":"0 auto 8px auto"}),
                                    html.Div("", style={"width":"16px", "height":"16px", "background":"linear-gradient(45deg, #10b981 0%, #3b82f6 100%)", "borderRadius":"50%", "margin":"0 auto"})
                                ], style={"width":"80px", "height":"80px", "background":"linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%)", "borderRadius":"50%", "margin":"0 auto 24px auto", "display":"flex", "flexDirection":"column", "alignItems":"center", "justifyContent":"center", "boxShadow":"0 0 30px rgba(59, 130, 246, 0.2), inset 0 0 20px rgba(255, 255, 255, 0.1)", "border":"2px solid rgba(59, 130, 246, 0.2)"}),
                                
                                html.H4("Start Your Health Journey", 
                                        style={"margin":"0 0 16px 0", "color":"#1f2937", "fontWeight":"800", "fontSize":"1.6rem", "fontFamily":"'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", "textAlign":"center", "letterSpacing":"-0.03em", "background":"linear-gradient(135deg, #1f2937 0%, #374151 100%)", "WebkitBackgroundClip":"text", "WebkitTextFillColor":"transparent", "backgroundClip":"text"}),
                                html.P("Transform your health data into actionable insights with AI-powered analysis.", 
                                       style={"margin":"0 0 32px 0", "color":"#6b7280", "fontSize":"1.05rem", "fontFamily":"'Inter', 'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", "textAlign":"center", "lineHeight":"1.7", "maxWidth":"480px", "margin":"0 auto 32px auto", "fontWeight":"500"}),

                            ], style={"position":"relative", "zIndex":"2", "padding":"40px 32px", "textAlign":"center"})
                        ], style={"position":"relative", "background":"linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #f1f5f9 100%)", "borderRadius":"28px", "border":"1px solid rgba(59, 130, 246, 0.1)", "boxShadow":"0 20px 40px rgba(0, 0, 0, 0.08), 0 8px 20px rgba(59, 130, 246, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.8)", "overflow":"hidden", "backdropFilter":"blur(10px)"}),
                    ], style={"position":"relative", "marginTop":"20px"})
                ], style={"textAlign":"center"})
            ])
        if tab == "timeline":
            tj = requests.get("http://localhost:8000/api/timeline", params={"session_id": sid}).json()
            # Build simple 7-day moving averages (ignore zeros as missing)
            def moving_avg(values, window=7):
                vals = [None if (v is None or (isinstance(v, (int,float)) and v == 0)) else float(v) for v in values]
                out = []
                for i in range(len(vals)):
                    start = max(0, i - window + 1)
                    window_vals = [v for v in vals[start:i+1] if v is not None]
                    out.append(sum(window_vals)/len(window_vals) if window_vals else None)
                return out
            fg = tj["fg_fast_mgdl"]
            sleep = tj["sleep_hours"]
            fg_ma = moving_avg(fg, 7)
            sleep_ma = moving_avg(sleep, 7)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=tj["dates"], y=fg, name="Fasting Glucose (mg/dL)", mode="lines", line=dict(color="#2563eb", width=1.5)))
            fig.add_trace(go.Scatter(x=tj["dates"], y=fg_ma, name="FG 7-day avg", mode="lines", line=dict(color="#1d4ed8", width=3)))
            fig.add_trace(go.Scatter(x=tj["dates"], y=sleep, name="Sleep (h)", yaxis="y2", mode="lines", line=dict(color="#dc2626", width=1.5)))
            fig.add_trace(go.Scatter(x=tj["dates"], y=sleep_ma, name="Sleep 7-day avg", yaxis="y2", mode="lines", line=dict(color="#b91c1c", width=3)))
            fig.update_layout(
                height=500,
                margin=dict(l=60,r=60,t=40,b=40),
                template="plotly_white",
                hovermode="x unified",
                legend=dict(
                    orientation="h", 
                    yanchor="bottom", 
                    y=1.02, 
                    xanchor="center", 
                    x=0.5,
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="rgba(0,0,0,0.1)",
                    borderwidth=1
                ),
                xaxis=dict(
                    rangeslider=dict(visible=True, thickness=0.1),
                    showgrid=True,
                    gridcolor="rgba(0,0,0,0.05)",
                    title="Date",
                    titlefont=dict(size=14, color="#374151")
                ),
                yaxis=dict(
                    title="Fasting Glucose (mg/dL)",
                    titlefont=dict(size=14, color="#374151"),
                    showgrid=True,
                    gridcolor="rgba(0,0,0,0.05)",
                    zeroline=False
                ),
                yaxis2=dict(
                    title="Sleep (hours)",
                    titlefont=dict(size=14, color="#374151"),
                    overlaying="y", 
                    side="right", 
                    showgrid=False,
                    zeroline=False
                ),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter, sans-serif", size=12),
                title=dict(
                    text="Health Trends Over Time",
                    font=dict(size=18, color="#1f2937"),
                    x=0.5,
                    xanchor="center"
                )
            )
            return html.Div([dcc.Graph(figure=fig)])
        if tab == "meals":
            mj = requests.get("http://localhost:8000/api/meals", params={"session_id": sid}).json()
            if not mj["meals"]:
                return html.Div("No meals found.")
            table = dash_table.DataTable(
                columns=[{"name": k.replace("_", " ").title(), "id": k} for k in mj["meals"][0].keys()],
                data=mj["meals"],
                page_size=10,
                style_table={
                    "overflowX": "auto",
                    "borderRadius": "12px",
                    "boxShadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
                },
                style_header={
                    "backgroundColor": "#f8fafc",
                    "color": "#374151",
                    "fontWeight": "600",
                    "textAlign": "center",
                    "border": "none",
                    "fontSize": "14px"
                },
                style_cell={
                    "textAlign": "center",
                    "padding": "12px",
                    "fontFamily": "Inter, sans-serif",
                    "border": "none",
                    "fontSize": "13px"
                },
                style_data={
                    "backgroundColor": "white",
                    "border": "none"
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "#f9fafb"
                    }
                ],
                filter_action="native",
                sort_action="native",
                export_format="csv",
            )
            controls = html.Div([
                html.Button("Export CSV", id="btn-export-meals")
            ], style={"display":"flex","justifyContent":"flex-end","marginBottom":"8px"})
            return html.Div([controls, table])
        if tab == "insights":
            ij = requests.get("http://localhost:8000/api/insights", params={"session_id": sid}).json()
            cards = []
            for c in ij["cards"]:
                # Determine card class based on effect
                card_class = "insight-card"
                if c["type"] == "causal_uplift":
                    eff = c.get("effect_pct", 0)
                    if eff < -0.05:  # beneficial effect
                        card_class += " beneficial"
                    elif eff > 0.05:  # concerning effect
                        card_class += " concerning"
                
                # Confidence badge
                confidence = c.get("confidence", "low")
                confidence_class = f"confidence-badge confidence-{confidence}"
                confidence_badge = html.Span(confidence.upper(), className=confidence_class)
                
                header = html.Div([
                    html.H4(c["title"], style={"margin": "0", "display": "inline", "fontSize": "1.25rem", "fontWeight": "600"}),
                    confidence_badge
                ], style={"display": "flex", "alignItems": "center", "marginBottom": "16px", "gap": "12px"})
                
                meta = []
                if c.get("driver"): 
                    meta.append(html.Div([
                        html.Strong("🎯 Driver: "), c['driver']
                    ], style={"marginBottom": "8px", "fontSize": "1rem"}))
                if c.get("target"): 
                    meta.append(html.Div([
                        html.Strong("📊 Target: "), c['target']
                    ], style={"marginBottom": "8px", "fontSize": "1rem"}))
                
                if c["type"] == "causal_uplift":
                    eff = round(100*(c.get("effect_pct") or 0),1)
                    effect_color = "#10b981" if eff < 0 else "#ef4444" if eff > 0 else "#6b7280"
                    meta.append(html.Div([
                        html.Strong("📈 Effect: "), 
                        html.Span(f"{eff}%", style={"color": effect_color, "fontWeight": "700", "fontSize": "1.1rem"}),
                        f" (n={c.get('n','-')})"
                    ], style={"marginBottom": "8px", "fontSize": "1rem"}))
                    if c.get("ci"):
                        lo, hi = c["ci"]
                        meta.append(html.Div([
                            html.Strong("📊 Confidence Interval: "), 
                            f"[{round(100*lo,1)}%, {round(100*hi,1)}%]"
                        ], style={"marginBottom": "8px", "fontSize": "0.9rem", "color": "#6b7280"}))
                    if c.get("counterfactual"):
                        cf = c["counterfactual"]
                        if cf.get("delta_pct") is not None:
                            delta = round(100*cf['delta_pct'],1)
                            delta_color = "#10b981" if delta < 0 else "#ef4444"
                            meta.append(html.Div([
                                html.Strong("🚀 Potential Impact: "),
                                html.Span(f"{delta}%", style={"color": delta_color, "fontWeight": "700"}),
                                f" if {cf['scenario']}"
                            ], style={"marginBottom": "8px", "fontSize": "0.9rem"}))
                
                if c["type"] == "correlation":
                    r = c.get('r', 0)
                    r_color = "#10b981" if abs(r) > 0.5 else "#f59e0b" if abs(r) > 0.3 else "#6b7280"
                    meta.append(html.Div([
                        html.Strong("🔗 Correlation: "),
                        html.Span(f"r={r}", style={"color": r_color, "fontWeight": "700"}),
                        f" (p={c.get('p')}, n={c.get('n')})"
                    ], style={"marginBottom": "8px", "fontSize": "1rem"}))
                
                if c["type"] == "anomaly":
                    meta.append(html.Div([
                        html.Strong("⚠️ Pattern: "),
                        f"Baseline {c['baseline']} → Current {c['current']} (run {c['run_days']} days)"
                    ], style={"marginBottom": "8px", "color": "#ef4444", "fontWeight": "600", "fontSize": "1rem"}))
                
                if c.get("note"): 
                    meta.append(html.Div([
                        html.Em(f"💡 {c['note']}")
                    ], style={"marginBottom": "12px", "fontSize": "0.9rem", "color": "#6b7280", "fontStyle": "italic"}))
                
                if c.get("suggested_experiment"):
                    exp = c["suggested_experiment"]
                    meta.append(html.Div([
                        html.Div([
                            html.Strong("🎯 Action Plan: "), 
                            f"{exp['duration_days']} days — {exp['intervention']}"
                        ], style={"marginBottom": "8px", "color": "#1f2937", "fontSize": "1rem", "fontWeight": "600"}),
                        html.Div([
                            html.Strong("📊 Track: "), ", ".join(exp['metrics'])
                        ], style={"marginBottom": "8px", "fontSize": "0.9rem"}),
                        html.Div([
                            html.Strong("✅ Success: "), exp['success']
                        ], style={"fontSize": "0.9rem", "color": "#059669", "fontWeight": "500"})
                    ], className="action-plan"))
                
                cards.append(html.Div([header, *meta], className=card_class))
            return html.Div(cards)

    @callback(
        Output("download-meals","data"),
        Input("btn-export-meals","n_clicks"),
        State("session-id","data"),
        prevent_initial_call=True,
    )
    def export_meals(n_clicks, sid):
        if not n_clicks:
            return dash.no_update
        mj = requests.get("http://localhost:8000/api/meals", params={"session_id": sid}).json()
        df = pd.DataFrame(mj["meals"]) if mj.get("meals") else pd.DataFrame()
        return dcc.send_data_frame(df.to_csv, "meals.csv", index=False)

    return app
