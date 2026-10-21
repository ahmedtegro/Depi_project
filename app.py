"""
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

df = pd.read_csv(r'C:\Users\Lenovo\OneDrive\Desktop\retail-sales-intelligence\sales_data.csv')
df['Date'] = pd.to_datetime(df['Date'])
df['Revenue'] = df['Units Sold'] * df['Price'] * (1 - df['Discount'] / 100)
df['YearMonth'] = df['Date'].dt.to_period('M').astype(str)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Retail Sales Intelligence Dashboard"

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Retail Sales Intelligence Dashboard", className="text-center text-primary my-4"), width=12)
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Region:"),
            dcc.Dropdown(
                id='region-dropdown',
                options=[{'label': 'All Regions', 'value': 'All'}] + [{'label': r, 'value': r} for r in sorted(df['Region'].unique())],
                value='All',
                clearable=False
            )
        ], width=3),
        dbc.Col([
            html.Label("Category:"),
            dcc.Dropdown(
                id='category-dropdown',
                options=[{'label': 'All Categories', 'value': 'All'}] + [{'label': c, 'value': c} for c in sorted(df['Category'].unique())],
                value='All',
                clearable=False
            )
        ], width=3),
        dbc.Col([
            html.Label("Store:"),
            dcc.Dropdown(
                id='store-dropdown',
                options=[{'label': 'All Stores', 'value': 'All'}] + [{'label': s, 'value': s} for s in sorted(df['Store ID'].unique())],
                value='All',
                clearable=False
            )
        ], width=3),
        dbc.Col([
            html.Label("Date range:"),
            dcc.DatePickerRange(
                id='date-range',
                min_date_allowed=df['Date'].min().date(),
                max_date_allowed=df['Date'].max().date(),
                start_date=df['Date'].min().date(),
                end_date=df['Date'].max().date()
            )
        ], width=3),
    ], className="mb-4 bg-light p-3 rounded shadow-sm"),

    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody([html.H5("Total Revenue", className="card-title text-muted"), html.H3(id='kpi-revenue', className="text-success")])], className="shadow-sm"), width=3),
        dbc.Col(dbc.Card([dbc.CardBody([html.H5("Total Units Sold", className="card-title text-muted"), html.H3(id='kpi-sold', className="text-primary")])], className="shadow-sm"), width=3),
        dbc.Col(dbc.Card([dbc.CardBody([html.H5("Avg Inventory Level", className="card-title text-muted"), html.H3(id='kpi-inventory', className="text-info")])], className="shadow-sm"), width=3),
        dbc.Col(dbc.Card([dbc.CardBody([html.H5("Avg Demand", className="card-title text-muted"), html.H3(id='kpi-demand', className="text-warning")])], className="shadow-sm"), width=3),
    ], className="mb-4 text-center"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='revenue-trend-chart'), width=8),
        dbc.Col(dcc.Graph(id='category-revenue-chart'), width=4),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='top-products-chart'), width=6),
        dbc.Col(dcc.Graph(id='bottom-products-chart'), width=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='season-chart'), width=6),
        dbc.Col(dcc.Graph(id='weather-impact-chart'), width=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='promotion-impact-chart'), width=6),
        dbc.Col(dcc.Graph(id='epidemic-impact-chart'), width=6),
    ], className="mb-4"),

], fluid=True)


@app.callback(
    [
        Output('kpi-revenue', 'children'),
        Output('kpi-sold', 'children'),
        Output('kpi-inventory', 'children'),
        Output('kpi-demand', 'children'),
        Output('revenue-trend-chart', 'figure'),
        Output('category-revenue-chart', 'figure'),
        Output('top-products-chart', 'figure'),
        Output('bottom-products-chart', 'figure'),
        Output('season-chart', 'figure'),
        Output('weather-impact-chart', 'figure'),
        Output('promotion-impact-chart', 'figure'),
        Output('epidemic-impact-chart', 'figure')
    ],
    [
        Input('region-dropdown', 'value'),
        Input('category-dropdown', 'value'),
        Input('store-dropdown', 'value'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date')
    ]
)
def update_dashboard(selected_region, selected_category, selected_store, start_date, end_date):
    filtered_df = df.copy()
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['Region'] == selected_region]
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    if selected_store != 'All':
        filtered_df = filtered_df[filtered_df['Store ID'] == selected_store]
    if start_date is not None:
        filtered_df = filtered_df[filtered_df['Date'] >= pd.to_datetime(start_date)]
    if end_date is not None:
        filtered_df = filtered_df[filtered_df['Date'] <= pd.to_datetime(end_date)]

    total_revenue = f"${filtered_df['Revenue'].sum():,.2f}"
    total_sold = f"{filtered_df['Units Sold'].sum():,}"
    avg_inventory = f"{filtered_df['Inventory Level'].mean():,.1f}"
    avg_demand = f"{filtered_df['Demand'].mean():,.1f}"

    trend_df = filtered_df.groupby('YearMonth')['Revenue'].sum().reset_index()
    fig_trend = px.line(
        trend_df, x='YearMonth', y='Revenue',
        title="Monthly Revenue Trend",
        markers=True, template="plotly_white"
    )
    fig_trend.update_layout(xaxis_title="Month", yaxis_title="Revenue ($)")

    cat_df = filtered_df.groupby('Category')['Revenue'].sum().reset_index()
    fig_cat = px.bar(
        cat_df, x='Category', y='Revenue', color='Category',
        title="Revenue by Category", template="plotly_white"
    )

    product_df = filtered_df.groupby('Product ID')['Revenue'].sum().reset_index()
    top_df = product_df.nlargest(5, 'Revenue')
    bottom_df = product_df.nsmallest(5, 'Revenue')
    fig_top = px.bar(
        top_df, x='Product ID', y='Revenue',
        title="Top 5 Products by Revenue", template="plotly_white"
    )
    fig_bottom = px.bar(
        bottom_df, x='Product ID', y='Revenue',
        title="Bottom 5 Products by Revenue", template="plotly_white"
    )

    season_df = filtered_df.groupby('Seasonality')['Units Sold'].mean().reset_index()
    fig_season = px.bar(
        season_df, x='Seasonality', y='Units Sold', color='Seasonality',
        category_orders={'Seasonality': ['Spring', 'Summer', 'Autumn', 'Winter']},
        title="Avg Units Sold by Season", template="plotly_white"
    )

    weather_df = filtered_df.groupby('Weather Condition')['Units Sold'].mean().reset_index()
    fig_weather = px.bar(
        weather_df, x='Weather Condition', y='Units Sold', color='Weather Condition',
        title="Avg Units Sold by Weather Condition", template="plotly_white"
    )

    promo_df = filtered_df.groupby('Promotion')[['Units Sold', 'Demand']].mean().reset_index()
    promo_df['Promotion'] = promo_df['Promotion'].map({0: 'No Promotion', 1: 'Active Promotion'})
    fig_promo = px.bar(
        promo_df, x='Promotion', y=['Units Sold', 'Demand'], barmode='group',
        title="Impact of Promotions on Sales vs. Demand", template="plotly_white"
    )
    fig_promo.update_layout(yaxis_title="Average Units")

    epidemic_df = filtered_df.groupby('Epidemic')[['Units Sold', 'Demand']].mean().reset_index()
    epidemic_df['Epidemic'] = epidemic_df['Epidemic'].map({0: 'Normal period', 1: 'Epidemic period'})
    fig_epidemic = px.bar(
        epidemic_df, x='Epidemic', y=['Units Sold', 'Demand'], barmode='group',
        title="Impact of Epidemic Periods on Sales vs. Demand", template="plotly_white"
    )
    fig_epidemic.update_layout(yaxis_title="Average Units")

    return (total_revenue, total_sold, avg_inventory, avg_demand,
            fig_trend, fig_cat, fig_top, fig_bottom,
            fig_season, fig_weather, fig_promo, fig_epidemic)


if __name__ == '__main__':
    app.run(debug=True, port=8050)
"""
import os
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Automatically find the directory where app.py is located and join it with the CSV filename
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'sales_data.csv')

df = pd.read_csv(file_path)
df['Date'] = pd.to_datetime(df['Date'])
df['Revenue'] = df['Units Sold'] * df['Price'] * (1 - df['Discount'] / 100)
df['YearMonth'] = df['Date'].dt.to_period('M').astype(str)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Retail Sales Intelligence Dashboard"

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Retail Sales Intelligence Dashboard", className="text-center text-primary my-4"), width=12)
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Region:"),
            dcc.Dropdown(
                id='region-dropdown',
                options=[{'label': 'All Regions', 'value': 'All'}] + [{'label': r, 'value': r} for r in sorted(df['Region'].unique())],
                value='All',
                clearable=False
            )
        ], width=3),
        dbc.Col([
            html.Label("Category:"),
            dcc.Dropdown(
                id='category-dropdown',
                options=[{'label': 'All Categories', 'value': 'All'}] + [{'label': c, 'value': c} for c in sorted(df['Category'].unique())],
                value='All',
                clearable=False
            )
        ], width=3),
        dbc.Col([
            html.Label("Store:"),
            dcc.Dropdown(
                id='store-dropdown',
                options=[{'label': 'All Stores', 'value': 'All'}] + [{'label': s, 'value': s} for s in sorted(df['Store ID'].unique())],
                value='All',
                clearable=False
            )
        ], width=3),
        dbc.Col([
            html.Label("Date range:"),
            dcc.DatePickerRange(
                id='date-range',
                min_date_allowed=df['Date'].min().date(),
                max_date_allowed=df['Date'].max().date(),
                start_date=df['Date'].min().date(),
                end_date=df['Date'].max().date()
            )
        ], width=3),
    ], className="mb-4 bg-light p-3 rounded shadow-sm"),

    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody([html.H5("Total Revenue", className="card-title text-muted"), html.H3(id='kpi-revenue', className="text-success")])], className="shadow-sm"), width=3),
        dbc.Col(dbc.Card([dbc.CardBody([html.H5("Total Units Sold", className="card-title text-muted"), html.H3(id='kpi-sold', className="text-primary")])], className="shadow-sm"), width=3),
        dbc.Col(dbc.Card([dbc.CardBody([html.H5("Avg Inventory Level", className="card-title text-muted"), html.H3(id='kpi-inventory', className="text-info")])], className="shadow-sm"), width=3),
        dbc.Col(dbc.Card([dbc.CardBody([html.H5("Avg Demand", className="card-title text-muted"), html.H3(id='kpi-demand', className="text-warning")])], className="shadow-sm"), width=3),
    ], className="mb-4 text-center"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='revenue-trend-chart'), width=8),
        dbc.Col(dcc.Graph(id='category-revenue-chart'), width=4),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='top-products-chart'), width=6),
        dbc.Col(dcc.Graph(id='bottom-products-chart'), width=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='season-chart'), width=6),
        dbc.Col(dcc.Graph(id='weather-impact-chart'), width=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='promotion-impact-chart'), width=6),
        dbc.Col(dcc.Graph(id='epidemic-impact-chart'), width=6),
    ], className="mb-4"),

], fluid=True)


@app.callback(
    [
        Output('kpi-revenue', 'children'),
        Output('kpi-sold', 'children'),
        Output('kpi-inventory', 'children'),
        Output('kpi-demand', 'children'),
        Output('revenue-trend-chart', 'figure'),
        Output('category-revenue-chart', 'figure'),
        Output('top-products-chart', 'figure'),
        Output('bottom-products-chart', 'figure'),
        Output('season-chart', 'figure'),
        Output('weather-impact-chart', 'figure'),
        Output('promotion-impact-chart', 'figure'),
        Output('epidemic-impact-chart', 'figure')
    ],
    [
        Input('region-dropdown', 'value'),
        Input('category-dropdown', 'value'),
        Input('store-dropdown', 'value'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date')
    ]
)
def update_dashboard(selected_region, selected_category, selected_store, start_date, end_date):
    filtered_df = df.copy()
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['Region'] == selected_region]
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    if selected_store != 'All':
        filtered_df = filtered_df[filtered_df['Store ID'] == selected_store]
    if start_date is not None:
        filtered_df = filtered_df[filtered_df['Date'] >= pd.to_datetime(start_date)]
    if end_date is not None:
        filtered_df = filtered_df[filtered_df['Date'] <= pd.to_datetime(end_date)]

    total_revenue = f"${filtered_df['Revenue'].sum():,.2f}"
    total_sold = f"{filtered_df['Units Sold'].sum():,}"
    avg_inventory = f"{filtered_df['Inventory Level'].mean():,.1f}"
    avg_demand = f"{filtered_df['Demand'].mean():,.1f}"

    trend_df = filtered_df.groupby('YearMonth')['Revenue'].sum().reset_index()
    fig_trend = px.line(
        trend_df, x='YearMonth', y='Revenue',
        title="Monthly Revenue Trend",
        markers=True, template="plotly_white"
    )
    fig_trend.update_layout(xaxis_title="Month", yaxis_title="Revenue ($)")

    cat_df = filtered_df.groupby('Category')['Revenue'].sum().reset_index()
    fig_cat = px.bar(
        cat_df, x='Category', y='Revenue', color='Category',
        title="Revenue by Category", template="plotly_white"
    )

    product_df = filtered_df.groupby('Product ID')['Revenue'].sum().reset_index()
    top_df = product_df.nlargest(5, 'Revenue')
    bottom_df = product_df.nsmallest(5, 'Revenue')
    fig_top = px.bar(
        top_df, x='Product ID', y='Revenue',
        title="Top 5 Products by Revenue", template="plotly_white"
    )
    fig_bottom = px.bar(
        bottom_df, x='Product ID', y='Revenue',
        title="Bottom 5 Products by Revenue", template="plotly_white"
    )

    season_df = filtered_df.groupby('Seasonality')['Units Sold'].mean().reset_index()
    fig_season = px.bar(
        season_df, x='Seasonality', y='Units Sold', color='Seasonality',
        category_orders={'Seasonality': ['Spring', 'Summer', 'Autumn', 'Winter']},
        title="Avg Units Sold by Season", template="plotly_white"
    )

    weather_df = filtered_df.groupby('Weather Condition')['Units Sold'].mean().reset_index()
    fig_weather = px.bar(
        weather_df, x='Weather Condition', y='Units Sold', color='Weather Condition',
        title="Avg Units Sold by Weather Condition", template="plotly_white"
    )

    promo_df = filtered_df.groupby('Promotion')[['Units Sold', 'Demand']].mean().reset_index()
    promo_df['Promotion'] = promo_df['Promotion'].map({0: 'No Promotion', 1: 'Active Promotion'})
    fig_promo = px.bar(
        promo_df, x='Promotion', y=['Units Sold', 'Demand'], barmode='group',
        title="Impact of Promotions on Sales vs. Demand", template="plotly_white"
    )
    fig_promo.update_layout(yaxis_title="Average Units")

    epidemic_df = filtered_df.groupby('Epidemic')[['Units Sold', 'Demand']].mean().reset_index()
    epidemic_df['Epidemic'] = epidemic_df['Epidemic'].map({0: 'Normal period', 1: 'Epidemic period'})
    fig_epidemic = px.bar(
        epidemic_df, x='Epidemic', y=['Units Sold', 'Demand'], barmode='group',
        title="Impact of Epidemic Periods on Sales vs. Demand", template="plotly_white"
    )
    fig_epidemic.update_layout(yaxis_title="Average Units")

    return (total_revenue, total_sold, avg_inventory, avg_demand,
            fig_trend, fig_cat, fig_top, fig_bottom,
            fig_season, fig_weather, fig_promo, fig_epidemic)


if __name__ == '__main__':
    app.run(debug=True, port=8050)