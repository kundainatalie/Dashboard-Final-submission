import os
import json
import plotly.graph_objs as go
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash import dash_table
import pandas as pd


def load_decision_tree_results():
    results = {}
    organizations = ['Truworths International Ltd', 'African Overseas Enterprises', 'Mr Price Group Ltd',
                     'Rex Trueform Group Ltd', 'The Foschini Group Ltd']
    for org in organizations:
        filename = f"{org}_results.json"
        try:
            with open(filename, 'r') as f:
                results[org] = json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filename} not found")
    return results


decision_tree_results = load_decision_tree_results()


def create_decision_tree_controls():
    return html.Div([
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id="org-selector",
                    options=[{"label": org, "value": org} for org in decision_tree_results.keys()],
                    value="African Overseas Enterprises",
                    style={'width': '100%'}
                ),
                width=3
            ),
            dbc.Col(
                html.Div(id="feature-inputs"),
                width=6
            )
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Button("Predict EPS", id="predict-button", color="custom", className="me-2"),
                dbc.Button("Reset", id="reset-button", color="custom")
            ])
        ]),
        html.Div(id="prediction-output", className="mt-3"),
        html.Span(
            "ⓘ",
            id="info-icon",
            style={
                "cursor": "pointer",
                "color": "black",
                "font-weight": "bold",
                "font-size": "1.2em",
                "margin-right": "5px"
            }
        ),
        dbc.Tooltip(
            "Industry Average Earnings per share is R200.42",
            target="info-icon",
            placement="right"),
        html.Div(id="decision-table-container"),
        html.Br(),
        html.P(" LOW : EPS lower than industry average.", style={'font-weight':'bold', 'color':'red'}),
        html.P("HIGH : EPS higher than industry average.", style={'font-weight':'bold', 'color':'green'})
    ])


def create_feature_inputs(selected_org):
    if selected_org not in decision_tree_results:
        return []

    org_data = decision_tree_results[selected_org]
    features = list(org_data['feature_importance'].keys())

    return [
        dbc.Col([
            dbc.Label(feature),
            dbc.Input(
                type="number",
                id={"type": "feature-input", "index": i},
                placeholder=f"Enter {feature}",
                step="any",
            )
        ], width=3, className="mb-3")
        for i, feature in enumerate(features)
    ]


def create_decision_table(tree_structure):
    def traverse_tree(node, path=None):
        if path is None:
            path = []

        if 'class' in node:
            return [(*path, node['class'])]

        feature = node['feature']
        threshold = node['threshold']

        left_path = path + [f"{feature} <= {threshold}"]
        right_path = path + [f"{feature} > {threshold}"]

        return traverse_tree(node['left'], left_path) + traverse_tree(node['right'], right_path)

    rules = traverse_tree(tree_structure)

    # Find the maximum number of conditions
    max_conditions = max(len(rule) - 1 for rule in rules)

    # Create column names dynamically based on the maximum number of conditions
    columns = [f"Condition {i + 1}" for i in range(max_conditions)] + ['Prediction']

    # Pad shorter rules with empty strings
    padded_rules = [rule + ("",) * (max_conditions + 1 - len(rule)) for rule in rules]

    # Create a DataFrame from the padded rules
    df = pd.DataFrame(padded_rules, columns=columns)

    return df


def create_decision_table_component(df):
    return dash_table.DataTable(
        id='decision-table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '5px',
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'Prediction'},
                'backgroundColor': 'rgb(248, 248, 248)',
                'fontWeight': 'bold'
            },
            {
                'if': {'filter_query': '{Condition 1} = ""'},
                'backgroundColor': 'rgb(220, 220, 220)'
            }
        ]
    )


def predict_class(node, feature_values):
    if 'class' in node:
        return node['class']

    feature = node['feature']
    threshold = node['threshold']

    if feature_values[feature] <= threshold:
        return predict_class(node['left'], feature_values)
    else:
        return predict_class(node['right'], feature_values)


__all__ = ['load_decision_tree_results', 'decision_tree_results',
           'create_decision_tree_controls', 'create_decision_table', 'create_decision_table_component',
           'predict_class']