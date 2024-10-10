import pandas as pd
import plotly.graph_objs as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import json
from dash.exceptions import PreventUpdate
import logging
from decision_tree import *
import openpyxl
import os



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Loading data
excel_file = 'Clusters_Data.xlsx'
xls = pd.ExcelFile(excel_file)
sheet_names = xls.sheet_names

# Create a dictionary to store DataFrames for each organization
dfs = {sheet: pd.read_excel(excel_file, sheet_name=sheet) for sheet in sheet_names}

# Create the Dash app with a theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True,
                assets_folder='assets')
server = app.server

org_order = ["African Overseas Enterprises", "Mr Price Group Ltd", "Rex Trueform Group Ltd", "The Foschini Group Ltd",
             "Truworths International Ltd"]


# Helper function to get unique clusters and years for each organization
def get_clusters_and_years(df):
    clusters = sorted(df['Cluster'].unique())
    years = {cluster: sorted(df[df['Cluster'] == cluster]['Year'].unique()) for cluster in clusters}
    return clusters, years


ROA_card = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H2("Return On Assets", className="card-title"),
                html.H1(id="roa-value", className="card-value")
            ],
            id="ROA_dets"
        ),
        dbc.Tooltip([
            "ROA shows the average return earned by all investors. The industry average ROA is 9.67 %, "
            "a ROA above 9.67 % reflects efficiency in operations."
        ], target="ROA_dets", placement="right", className="tooltip-custom"),

    ],
    className='text-center mx-2 value-cards',
    style={"height": "100px"}
)

NAV_card = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H2("Net Asset Value/Share", className="card-title"),
                html.H1(id="nav-value", className="card-value")
            ],
            id="NAV_det"),
        dbc.Tooltip([
            "The industry average NAV/share is R 3312.96"
        ], target="nav-value", placement="right", className="tooltip-custom"),
    ],
    className='text-center mx-2 value-cards',
    style={"height": "100px"}
)

PE_card = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H2("Price/Earnings Ratio", className="card-title"),
                html.H1(id="pe-value", className="card-value")
            ],
            id="PE_dets"
        ),
        dbc.Tooltip([
            "Price Earnings Ratio compares a company's share price to its Earnings per Share. A high P/E ratio shows "
            "operational efficiency and is an indication of a good investment. The industry average "
            "Price Earnings ratio is R 411.82"
        ], target="PE_dets", placement="right", className="tooltip-custom"),
    ],
    className='text-center mx-2 value-cards',
    style={"height": "100px"}
)
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/home", active="exact", className="nav-link-custom")),
        *[dbc.NavItem(dbc.NavLink(org, href=f"/{org.replace(' ', '-').replace('&', '').lower()}", active="exact",
                                  className="nav-link-custom")) for org in org_order],
        dbc.NavItem(dbc.NavLink("Predictions", href="/predictions", active="exact", className="nav-link-custom")),
    ],
    brand=html.Span("Apparel Retail Industry", className="custom-brand"),
    brand_href="/home",
    color="#09124f",
    dark=True,
    className="custom-navbar"
)

# Define the layout with tabs for each organization
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', className="container mt-4")
])


def format_url_to_org(pathname):
    # Strip leading/trailing slashes
    org = pathname.strip('/')

    # Replace dashes with spaces
    org = org.replace('-', ' ')

    # Handle the replacement of "and" with "&"
    org_parts = org.split(' ')
    for i in range(len(org_parts)):
        if org_parts[i].lower() == 'and':
            org_parts[i] = '&'
    org = ' '.join(org_parts)

    # Title-case the organization name
    org = org.title()

    return org


@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/home' or pathname == '/':
        return render_home_page()
    elif pathname == '/predictions':
        return render_predictions_page()
    else:
        # Extract organization name from pathname
        org = pathname.strip('/').replace('-', ' ').replace('and', '&').title()
        if org in org_order:
            return render_org_page(org)
        else:
            return html.H1("404: Not found", className="text-center")


def render_home_page():
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    [
                        dbc.CardImg(src="/assets/images/aoe-1.png", top=True,
                                    style={"height": "200px", "object-fit": "cover"},
                                    alt="AOE Image"),
                        dbc.CardBody(
                            [
                                html.H4("African & Overseas Enterprises", className="card-title"),
                                html.P([
                                    "African and Overseas Enterprises is a holding company that was founded "
                                    "in 1947 in Cape Town, South Africa. The organisation's primary business "
                                    "focus is in the clothing and fashion accessories retail. The group has "
                                    "controlling interests in Rex Trueform Ltd "
                                    "which has an interest"
                                    " in Retail operations through Queenspark store, Property management, "
                                    "Media and Broadcasting, water infrastructure and group services. ",
                                    html.Span("It is the "
                                              "smallest organisation in the industry with a market cap of R 138.7 "
                                              "million.",
                                              style={"color": "#4B49AC", "font-weight": "bold"}),

                                ],
                                    className="card-text", style={"textAlign":"justify", "textJustify":"inter-word"}),
                                dbc.Button("View Details", id="btn-aoe", color="custom", className="mt-3")
                            ]
                        ),
                    ],
                    style={"height": "100%"}
                )
            ], width=6, className="mb-4"),
            dbc.Col([
                dbc.Card(
                    [
                        dbc.CardImg(src="/assets/images/mrp2.png", top=True,
                                    style={"height": "200px", "object-fit": "cover"},
                                    alt="MRP Image"),
                        dbc.CardBody(
                            [
                                html.H4("Mr Price Group Ltd", className="card-title"),
                                html.P([
                                    "Mr Price Group is a cash-based, omni-channel business that predominantly "
                                    "operates in the fashion retail space. The organisation operates in the "
                                    "apparel, homeware, sportswear and telecoms segments through 2,900 stores. ",
                                    html.Span("Mr "
                                              "Price Group Ltd is the largest organisation in the industry with a market "
                                              "cap of R 60.39 billion.",
                                              style={"color": "#4B49AC", "font-weight": "bold"}),

                                ],  className="card-text", style={"textAlign":"justify", "textJustify":"inter-word"}),
                                html.Br(),
                                html.Br(),
                                html.Br(),
                                dbc.Button("View Details", id="btn-mrp", color="custom", className="mt-3")
                            ]
                        ),
                    ],
                    style={"height": "100%"}
                )
            ], width=6, className="mb-4"),
        ], className="g-4"),
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    [
                        dbc.CardImg(src="/assets/images/rt.png", top=True,
                                    style={"height": "200px", "object-fit": "cover"},
                                    alt="Rex Image"),
                        dbc.CardBody(
                            [
                                html.H4("Rex Trueform Group Ltd", className="card-title"),
                                html.P([
                                    "Rex Trueform Group Ltd was established in 1937 in Cape Town, South Africa. "
                                    "The Group is a subsidiary of African and Overseas Group Ltd. The Group "
                                    "operates in the retail space through Queenspark group of stores, "
                                    "Media and Broadcasting, Water infrastructure and property services. ", html.Span(
                                        "The group has a market cap of R 232.85 million.",
                                        style={"color": "#4B49AC", "font-weight": "bold"}),

                                ],  className="card-text", style={"textAlign":"justify", "textJustify":"inter-word"}),
                                dbc.Button("View Details", id="btn-rex", color="custom", className="mt-3")
                            ]
                        ),
                    ],
                    style={"height": "100%"}
                )
            ], width=6, className="mb-4"),
            dbc.Col([
                dbc.Card(
                    [
                        dbc.CardImg(src="/assets/images/tfg.png", top=True,
                                    style={"height": "200px", "object-fit": "cover"},
                                    alt="TFG Image"),
                        dbc.CardBody(
                            [
                                html.H4("The Foschini Group Ltd", className="card-title"),
                                html.P([
                                    "TFG is one of South Africa's chain-store groups with an internationally "
                                    "diverse portfolio consisting of 34 apparel and lifestyle retail brands "
                                    "inclusive of Foschini, Jet, Sterns, American Swiss and @Home stores. ",
                                    html.Span("The group"
                                              "is the second largest in the industry with a market cap of R 46.13 "
                                              "billion.",
                                              style={"color": "#4B49AC", "font-weight": "bold"}),

                                ],  className="card-text", style={"textAlign":"justify", "textJustify":"inter-word"}),
                                dbc.Button("View Details", id="btn-tfg", color="custom", className="mt-3")
                            ]
                        ),
                    ],
                    style={"height": "100%"}
                )
            ], width=6, className="mb-4"),
        ], className="g-4"),
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    [
                        dbc.CardImg(src="/assets/images/truworths.jpg", top=True,
                                    style={"height": "200px", "object-fit": "cover"},
                                    alt="Truworths Image"),
                        dbc.CardBody(
                            [
                                html.H4("Truworths International Ltd", className="card-title"),
                                html.P([
                                    "Truworths International is an Investment Holding and Management company that "
                                    "is a leading retailer of fashion clothing, footwear and homewear. The "
                                    "organisation was listed on the JSE in 1998. Truworths International brands "
                                    "and stores include Truworths, Truworths Man, Uzzi, Identity and Loads of "
                                    "Living", html.Span(" The group has a market cap of R 37.8 billion.",
                                                        style={"color": "#4B49AC", "font-weight": "bold"}),

                                ],  className="card-text", style={"textAlign":"justify", "textJustify":"inter-word"}),
                                dbc.Button("View Details", id="btn-truworths", color="custom", className="mt-3")
                            ]
                        ),
                    ],
                    style={"height": "100%"}
                )
            ], width=6, className="mb-4"),
        ], className="g-4"),
    ], className="container-fluid px-4 py-4"),


def render_predictions_page():
    return dbc.Card(
        dbc.CardBody([
            html.H2("Decision Table Predicting Earnings per Share"),
            html.Br(),
            create_decision_tree_controls()

        ])

    )


def render_org_page(org):
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div(id='cluster-year-checklist', className='checklist-main'),
                    dcc.Checklist(id='cluster-checklist', className='inline-checklist'),
                ], className='checklist-wrapper')
            ], width=10),
            dbc.Col([
                dbc.Button(
                    "Reset",
                    id="btn-reset",
                    color="#17A2B8 ",
                    className="mt-3"
                ),
            ], width=2, className="d-flex align-items-end")
        ], className="mb-4 align-items-end"),
        dbc.Row([
            dbc.Col(ROA_card, width={"size": 3, "offset": 1}),
            dbc.Col(NAV_card, width=3),
            dbc.Col(PE_card, width=3),
        ], justify="center", className="mb-4"),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div(
                            dcc.Graph(id='bar-chart'),
                            id='bar-chart-div'
                        ),
                        dbc.Tooltip([
                            "Earnings Yield measures the return on the share price.",
                            html.Span("The Earnings Yield Industry Average"
                                      " is 5.952.", style={"color": "#4B49AC", "font-weight": "bold"}),
                            "  An EY higher than 5.952 reflects above average returns on the share price.",
                            html.Br(),
                            html.Br(),
                            "Dividend Yield is  measure of final dividend on the share price.",
                            html.Span(' The benchmark Dividend Yield is 3.178.',
                                      style={"color": "#4B49AC", "font-weight": "bold"}),
                            ' A dividend yield higher than the benchmark '
                            'reflects a good '
                            'investment.'], target="bar-chart-div", placement="right", className="tooltip-custom"),
                    ]), style={"backgroundColor": "#f8f9fa"}
                ), width=6
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div(
                            dcc.Graph(id='donut-chart'),
                            id='donut_div'
                        ),
                        dbc.Tooltip(
                            "Earnings per share shows how much income an organisation makes per share issued. Dividends "
                            "per"
                            " share is the portion of Earnings that the board decides to return to shareholders. The "
                            "earnings that"
                            " are not paid out as dividends are reinvested in the organisation for growth.",
                            target="donut_div", placement="right"),
                    ]), style={"backgroundColor": "#f8f9fa"}
                ), width=6
            ),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div(
                            dcc.Graph(id='area-chart'),
                            id='area_div'
                        ),
                        dbc.Tooltip([
                            "Current and Quick ratio show how liquid an organisation is, that is how quickly the "
                            "organisation"
                            "can convert assets into cash.", html.Span('The benchmark for Current Ratio is 1.95 and '
                                                                       '1.18 for Quick Ratio.',
                                                                       style={"color": "#4B49AC",
                                                                              "font-weight": "bold"})],
                            target="area_div", placement="right"),
                    ]), style={"backgroundColor": "#f8f9fa"}
                ), width=6
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div(
                            dcc.Graph(id='line-chart'),
                            id='line_div'
                        ),
                        dbc.Tooltip(
                            "ROE measures an organisation's financial performance by measuring how efficiently "
                            "shareholders'"
                            "equity was turned into Net Income. A higher ROE shows efficient use equity. The Industry Average ROE "
                            "is 10.94.", target="line_div", placement="right"),
                    ]), style={"backgroundColor": "#f8f9fa"}
                ), width=6
            ),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div(
                            dcc.Graph(id='gauge-chart', config={'displayModeBar': False}),
                            id='gauge_div'
                        ),
                        dbc.Tooltip("ROA measures the net income per asset employed. "
                                    "Industry benchmark ROA is 19.72 %.", target="gauge_div", placement="right")
                    ]), style={"backgroundColor": "#f8f9fa"}
                ), width=6,
                className="d-flex justify-content-center"
            ),

        ], className="mb-4 justify-content-center"),
        html.Div(id='selected-data', style={'display': 'none'}),
    ])


@app.callback(
    Output('url', 'pathname'),
    [Input('btn-aoe', 'n_clicks'),
     Input('btn-mrp', 'n_clicks'),
     Input('btn-rex', 'n_clicks'),
     Input('btn-tfg', 'n_clicks'),
     Input('btn-truworths', 'n_clicks')],
    [State('url', 'pathname')]
)
def update_active_tab(btn_aoe, btn_mrp, btn_rex, btn_tfg, btn_truworths, current_tab):
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_tab
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'btn-aoe':
            return "African Overseas Enterprises"
        elif button_id == 'btn-mrp':
            return "Mr Price Group Ltd"
        elif button_id == 'btn-rex':
            return "Rex Trueform Group Ltd"
        elif button_id == 'btn-tfg':
            return "The Foschini Group Ltd"
        elif button_id == 'btn-truworths':
            return "Truworths International Ltd"
        else:
            return current_tab


@app.callback(
    Output("decision-table-container", "children"),
    Input("org-selector", "value")
)
def update_decision_table(selected_org):
    if not selected_org:
        return html.Div("Select an organization to view its decision table")

    if selected_org not in decision_tree_results:
        return html.Div(f"No decision logic data found for {selected_org}")

    org_data = decision_tree_results[selected_org]
    tree_structure = org_data['tree_structure']

    df = create_decision_table(tree_structure)
    return create_decision_table_component(df)


@app.callback(
    Output("feature-inputs", "children"),
    Input("org-selector", "value")
)
def update_feature_inputs(selected_org):
    if not selected_org or selected_org not in decision_tree_results:
        return []

    org_data = decision_tree_results[selected_org]
    features = list(org_data['feature_importance'].keys())

    return dbc.Row([
        dbc.Col([
            dbc.Input(
                type="number",
                id={"type": "feature-input", "index": i},
                placeholder=feature,
                step="any",
                style={"width": "150px"}
            )
        ], width="auto", className="mb-2 me-2")  # me-2 adds margin to the right of each column
        for i, feature in enumerate(features)
    ])


@app.callback(
    [Output("prediction-output", "children"),
     Output({"type": "feature-input", "index": ALL}, "value")],
    [Input("predict-button", "n_clicks"),
     Input("reset-button", "n_clicks")],
    [State({"type": "feature-input", "index": ALL}, "value"),
     State("org-selector", "value")]
)
def update_prediction(predict_clicks, reset_clicks, feature_values, selected_org):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "reset-button":
        return "", [""] * len(feature_values)

    if not selected_org or selected_org not in decision_tree_results:
        return f"No data found for {selected_org}", [dash.no_update] * len(feature_values)

    org_data = decision_tree_results[selected_org]
    features = list(org_data['feature_importance'].keys())

    if len(feature_values) != len(features) or any(v is None or v == '' for v in feature_values):
        return html.Div([
            html.Span("Please enter values for all features.",
                      style={'color': 'red', 'font-weight': 'bold'})
        ]), [dash.no_update] * len(feature_values)

    try:
        feature_values = [float(v) for v in feature_values]
    except ValueError:
        return html.Div([
            html.Span("Please enter valid numeric values for all features.",
                      style={'color': 'red', 'font-weight': 'bold'})
        ]), [dash.no_update] * len(feature_values)

    tree = org_data['tree_structure']
    prediction = predict_class(tree, dict(zip(features, feature_values)))

    return html.Div([
        html.Span(f"The predicted EPS value for {selected_org} is {prediction}ER than the Industry Average EPS",
                  style={'color': 'teal', 'font-weight': 'bold'})
    ]), [dash.no_update] * len(feature_values)


# Add this function to create the reset button
def create_reset_button():
    return html.Button("Reset", id="reset-button", className="btn btn-secondary mt-3 ml-2")

@app.callback(
    [Output('cluster-year-checklist', 'children'),
     Output('cluster-checklist', 'value')],
    [Input('url', 'pathname'),
     Input('btn-reset', 'n_clicks')],
    [State('cluster-checklist', 'value')]
)
def update_cluster_year_checklist(pathname, n_clicks, current_clusters):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    logger.info(f"Pathname: {pathname}")

    if pathname in ['/home', '/', '/predictions'] or pathname is None:
        logger.info("PreventUpdate raised due to pathname")
        raise PreventUpdate

    try:
        selected_org = format_url_to_org(pathname)

        if selected_org not in dfs:
            logger.warning(f"Organization not found: {selected_org}")
            logger.info("Available organizations: %s", list(dfs.keys()))
            return html.Div(f"Organization not found: {selected_org}", className="text-danger"), []

        df = dfs[selected_org]
        clusters, years = get_clusters_and_years(df)

        checklist = html.Div([
            dbc.Label("Select Clusters:", className="label-style"),
            dcc.Checklist(
                id='cluster-checklist',
                options=[{'label': f'Cluster {i}', 'value': i} for i in clusters],
                value=[0] if triggered_id != 'btn-reset' else [],
                className="inline-checklist mb-2"
            ),
            html.Div(id='year-checklists', className="mt-2")
        ])

        if triggered_id == 'btn-reset':
            return checklist, []
        else:
            return checklist, current_clusters or [0]
    except Exception as e:
        logger.error(f"Error in update_cluster_year_checklist: {str(e)}")
        raise PreventUpdate


@app.callback(
    Output('year-checklists', 'children'),
    [Input('cluster-checklist', 'value'),
     Input('url', 'pathname'),
     Input('btn-reset', 'n_clicks')]
)
def update_year_checklists(selected_clusters, pathname, n_clicks):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'btn-reset' or not selected_clusters or pathname in ['/home', '/about', '/']:
        return []

    # Convert pathname to the format used in dfs keys
    selected_org = pathname.strip('/').replace('-', ' ').replace('and', '&').title()

    if selected_org not in dfs:
        print(f"Organization not found: {selected_org}")
        print("Available organizations:", list(dfs.keys()))
        return html.Div(f"Organization not found: {selected_org}", className="text-danger")

    df = dfs[selected_org]
    clusters, years = get_clusters_and_years(df)

    year_checklists = []
    for cluster in selected_clusters:
        cluster_years = years[cluster]
        year_checklists.append(html.Div([
            dbc.Label(f"Years for Cluster {cluster}:", className="label-style"),
            dcc.Checklist(
                id={'type': 'year-checklist', 'cluster': cluster},
                options=[{'label': str(year), 'value': year} for year in cluster_years],
                value=[],
                className="inline-checklist mb-2"
            )
        ]))

    return year_checklists


@app.callback(
    Output('selected-data', 'children'),
    [Input('url', 'pathname'),
     Input('cluster-checklist', 'value'),
     Input({'type': 'year-checklist', 'cluster': ALL}, 'value'),
     Input('btn-reset', 'n_clicks')]
)
def store_selected_data(selected_org, selected_clusters, selected_years, n_clicks):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'btn-reset' or selected_org in ['home', 'predictions', '/']:
        return json.dumps({'org': selected_org, 'clusters': [], 'years': {}})

    # Handle the case where selected_years is None
    if selected_years is None:
        selected_years = []

    # Create the selected_years_dict only if we have both clusters and years
    if selected_clusters and selected_years:
        selected_years_dict = {cluster: years for cluster, years in zip(selected_clusters, selected_years) if years}
    else:
        selected_years_dict = {}

    data = {'org': selected_org, 'clusters': selected_clusters, 'years': selected_years_dict}
    return json.dumps(data)


def format_url_to_org(pathname):
    # Strip leading/trailing slashes
    org = pathname.strip('/')

    # Replace dashes with spaces
    org = org.replace('-', ' ')

    # Handle the replacement of "and" with "&"
    org_parts = org.split(' ')
    for i in range(len(org_parts)):
        if org_parts[i].lower() == 'and':
            org_parts[i] = '&'
    org = ' '.join(org_parts)

    # Title-case the organization name
    org = org.title()

    return org


@app.callback(
    [Output('bar-chart', 'figure'),
     Output('donut-chart', 'figure'),
     Output('area-chart', 'figure'),
     Output('line-chart', 'figure'),
     Output('roa-value', 'children'),
     Output('nav-value', 'children'),
     Output('pe-value', 'children'),
     Output('gauge-chart', 'figure')],
    [Input('selected-data', 'children')]
)
def update_graphs(json_data):
    data = json.loads(json_data)
    selected_org = data['org']

    print(f"Received selected_org from URL: {selected_org}")

    if selected_org in ['home', 'predictions', '/']:
        # Return empty figures for the 'home' and 'about' tabs
        empty_fig = go.Figure()
        return empty_fig, empty_fig, empty_fig, empty_fig, "", "", "", empty_fig

    # Convert URL format to organization name
    selected_org = format_url_to_org(selected_org)
    print(f"Formatted selected_org: {selected_org}")

    selected_clusters = data['clusters']
    selected_years = [year for years in data['years'].values() for year in years]

    print(f"Available organizations in dfs: {list(dfs.keys())}")

    if selected_org in dfs:
        df = dfs[selected_org]
    else:
        print(f"No data found for organization: {selected_org}")
        empty_fig = go.Figure()
        return empty_fig, empty_fig, empty_fig, empty_fig, "", "", "", empty_fig

    if selected_clusters:
        df = df[df['Cluster'].isin(selected_clusters)]

    if selected_years:
        df = df[df['Year'].isin(selected_years)]

    # Define a common color scheme
    colors = ['#09124f', '#98BDFF', '#574476', '#17A2B8', '#2576A7', '#488A99', '#00CCCC', '#FF97FF', '#FECB52']

    # Update ROA Card
    roa_value = df['InflationAdjustedReturn OnAssets'].mean()
    roa_card_content = f"{roa_value:.2f}%"

    # Update NAV Card
    nav_value = df['NAVShare'].mean()
    nav_card_content = f" R {nav_value:.2f}"

    # Update PE Card
    pe_value = df['PriceEarnings'].mean()
    pe_card_content = f"{pe_value:.2f}"

    # Bar Chart
    bar_fig = go.Figure()
    bar_fig.add_trace(
        go.Bar(x=df['Year'], y=df['EarningsYield'], name='Earnings Yield', marker_color=colors[0], width=0.4))
    bar_fig.add_trace(
        go.Bar(x=df['Year'], y=df['DividendYield'], name='Dividend Yield', marker_color=colors[1], width=0.4))
    bar_fig.update_layout(
        title={
            'text': f'{selected_org}<br>Earnings Yield and Dividend Yield',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        barmode='group',
        xaxis_title='Year',
        yaxis_title='Yield',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly_white',
        bargap=0.15
    )

    # Donut Chart
    earnings_per_share = df['ES'].sum()
    dividend_per_share = df['DividendShare'].sum()
    donut_fig = go.Figure(data=[go.Pie(
        labels=['Earnings per share', 'Dividend per share'],
        values=[earnings_per_share, dividend_per_share],
        hole=.3,
        marker_colors=[colors[0], colors[3]]
    )])
    donut_fig.update_layout(
        title={
            'text': f'{selected_org}<br>Dividend Payout Ratio',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },

        annotations=[dict(text=' ', x=0.5, y=0.5, font_size=20, showarrow=False)],
        template='plotly_white'
    )

    # Area Chart
    area_fig = go.Figure()
    area_fig.add_trace(go.Scatter(
        x=df['Year'], y=df['QuickRatio'],
        mode='lines',
        line=dict(width=0.5, color=colors[5]),
        stackgroup='one',
        name='Quick Ratio'
    ))
    area_fig.add_trace(go.Scatter(
        x=df['Year'], y=df['CurrentRatio'],
        mode='lines',
        line=dict(width=0.5, color=colors[3]),
        stackgroup='one',
        name='Current Ratio'
    ))
    area_fig.update_layout(
        title={
            'text': f'{selected_org}<br>Liquidity Overview',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },

        xaxis_title='Year',
        yaxis_title='Ratio',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly_white'
    )

    # Line Chart
    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(
        x=df['Year'],
        y=df['InflationAdjustedROE'],
        name='Return On Equity',
        mode='lines+markers',
        line=dict(color=colors[0], width=2),
        marker=dict(size=8)
    ))
    line_fig.update_layout(
        title={
            'text': f'{selected_org}<br>Return on Equity',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Year',
        yaxis_title='ROE',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly_white',
        hovermode="x unified"
    )

    # Gauge Chart
    debt_equity = df['DebtEquity'].mean()
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=debt_equity,
        title={
            'text': f'{selected_org}<br>Debt Equity Ratio',
            'font': {'size': 18}  # Adjust size as needed
        },
        domain={'y': [0, 1], 'x': [0, 1]},
        gauge={
            'axis': {'range': [0, df['DebtEquity'].max()]},
            'bar': {'color': colors[3]},
            'steps': [
                {'range': [0, df['DebtEquity'].mean()], 'color': "lightblue"},
                {'range': [df['DebtEquity'].mean(), df['DebtEquity'].max()], 'color': colors[5]}
            ],
            'threshold': {
                'line': {'color': colors[0], 'width': 4},
                'thickness': 0.75,
                'value': df['DebtEquity'].mean() + df['DebtEquity'].std()
            }
        }
    ))

    gauge_fig.update_layout(
        template='plotly_white',
        height=450,
        margin=dict(t=50, b=50, l=50, r=50)
    )

    return bar_fig, donut_fig, area_fig, line_fig, roa_card_content, nav_card_content, pe_card_content, gauge_fig


# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run_server(debug=False, host='0.0.0.0', port=port)

