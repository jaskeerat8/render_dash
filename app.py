# Importing Libraries
import radial_bar_chart
import json, ast
import numpy as np
import pandas as pd
import calendar
from datetime import datetime, date, timedelta
import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objects as go
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
from dash.dependencies import Input, Output

# Global Variables
global date_dict

# Reading static Data, later read from AWS after user authentication
df = pd.read_csv("Data/final_30-11-2023_14_11_18.csv")

# Defining Colors and Plotly Graph Options
plot_config = {"modeBarButtonsToRemove": ["zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d", "hoverClosestCartesian", "hoverCompareCartesian"],
               "staticPlot": False, "displaylogo": False}
platform_colors = {"Instagram": "#25D366", "Twitter": "#2D96FF", "Facebook": "#FF5100", "Tiktok": "#f6c604"}
alert_colors = {"High": "#FF5100", "Medium": "#f6c604", "Low": "#25D366"}
content_classification_colors = {"Offensive": "#FFD334", "Sexually Explicit": "#2D96FF", "Sexually Suggestive": "#FF5100", "Other": "#25D366", "Self Harm & Death": "#f77d07"}
classification_bar_colors = {"Mental & Emotional Health": "yellow", "Other Toxic Content": "blue", "Violence & Threats": "red", "Cyberbullying": "green", "Self Harm & Death": "orange", "Sexual & Inappropriate Content": "purple"}
image_location = {"Instagram": "assets/Instagram.png", "Twitter": "assets/twitter.png", "Facebook": "assets/facebook.png", "Tiktok": "assets/tiktok.png"}
platform_icons = {"Instagram": "skill-icons:instagram", "Twitter": "devicon:twitter", "Facebook": "devicon:facebook", "Tiktok": "logos:tiktok-icon"}


# Filter Functions
def child_filter(dataframe, child_value):
    if((child_value is not None) and (child_value != "all")):
        dataframe = dataframe[dataframe["name_childrens"] == child_value]
    return dataframe

def time_filter(dataframe, time_value, date_range_value):
    if(time_value == "all"):
        start_date = datetime.combine(datetime.strptime(date_range_value[0], "%Y-%m-%d"), datetime.min.time())
        end_date = datetime.combine(datetime.strptime(date_range_value[1], "%Y-%m-%d"), datetime.max.time())
        dataframe["createTime_contents"] = pd.to_datetime(dataframe["createTime_contents"], format="%Y-%m-%d %H:%M:%S.%f")
        dataframe = dataframe[(dataframe["createTime_contents"] >= start_date) & (dataframe["createTime_contents"] <= end_date)]
        return dataframe
    else:
        time_value = json.loads(time_value)
        start_date = datetime.now() - timedelta(days=time_value["delta"])
        end_date = datetime.now()
        dataframe["createTime_contents"] = pd.to_datetime(dataframe["createTime_contents"], format="%Y-%m-%d %H:%M:%S.%f")
        dataframe = dataframe[(dataframe["createTime_contents"] >= start_date) & (dataframe["createTime_contents"] <= end_date)]
        return dataframe

def platform_filter(dataframe, platform_value):
    if((platform_value is not None) and (platform_value != "all")):
        dataframe = dataframe[dataframe["platform_contents"] == platform_value]
    return dataframe

def alert_filter(dataframe, alert_value):
    if((alert_value is not None) and (alert_value != "all")):
        dataframe = dataframe[dataframe["alert_contents"] == alert_value]
    return dataframe

def slider_filter(dataframe, slider_value):
    start_date = pd.to_datetime(date_dict[slider_value[0]], format="%Y-%m-%d").date()
    end_date = pd.to_datetime(date_dict[slider_value[1]], format="%Y-%m-%d").date()
    dataframe["commentTime_comments"] = pd.to_datetime(dataframe["commentTime_comments"], format="%Y-%m-%d %H:%M:%S").dt.date
    dataframe = dataframe[(dataframe["commentTime_comments"] >= start_date) & (dataframe["commentTime_comments"] <= end_date)]
    return dataframe


# Function if No Data is available
def no_data_graph():
    message = html.Div(className="no_data_message", id="no_data_message", children=[
        html.Img(src="assets/images/empty_ghost.gif", width="40%"),
        html.P("No Data to Display", style={"fontSize": "24px", "color": "red", "margin": "0px"}),
        html.P("Please make a different Filter Selection", style={"fontSize": "18px", "color": "black", "margin": "0px"})
        ], style={"height": "100%"}
    )
    return message


# SideBar
sidebar = html.Div(className="sidebar", children=[
    html.Div(className="sidebar-header", children=[
        html.Img(src="https://chatstat-dashboard.s3.ap-southeast-2.amazonaws.com/images/chatstatlogo.png"),
        html.H2("chatstat")
    ]),

    html.Hr(style={"height": "8px", "width": "100%", "backgroundColor": "#25d366", "opacity": "1", "borderRadius": "5px", "margin-top": "0px", "margin-left": "0px", "margin-right": "0px"}),

    html.P("Main Menu", style={"color": "white", "margin": 0, "padding": 0, "fontFamily": "Poppins", "fontSize": 12}),
    dbc.Nav(className="sidebar-navlink", children=[
        dbc.NavLink([html.Img(src="https://chatstat-dashboard.s3.ap-southeast-2.amazonaws.com/images/dashboard.png"), html.Span("Dashboard")],
                    href="/dashboard", active="exact"),
        dbc.NavLink([html.Img(src="https://chatstat-dashboard.s3.ap-southeast-2.amazonaws.com/images/analytics.png"), html.Span("Analytics")],
                    href="/analytics", active="exact"),
        dbc.NavLink([html.Img(src="https://chatstat-dashboard.s3.ap-southeast-2.amazonaws.com/images/report.png"), html.Span("Report & Logs")],
                    href="/report", active="exact"),
        ],
        vertical=True, pills=True)
    ]
)


# Header
dashboard_header = dmc.Header(className="header", height="60px", fixed=False, children=[
    dmc.Text("Dashboard", className="header_title"),
    dmc.Group(className="child_control_container", children=[
        dmc.Avatar(id="child_control_avatar", className="child_control_avatar", color="red", size="40px", radius="xl"),
        dmc.Select(id="child_control", className="child_control", value="all",
                   placeholder="Select Member", clearable=False, searchable=False,
                   rightSection=DashIconify(icon="radix-icons:chevron-down", color="black"),
                   style={"width": "calc(100% - 50px)"})
    ], spacing="10px"
    )
])

analytics_header = dmc.Header(className="header", height="60px", fixed=False, children=[
    dmc.Text("Analytics", className="header_title"),
    dmc.Group(className="child_control_container", children=[
        dmc.Avatar(id="child_control_avatar", className="child_control_avatar", color="red", size="40px", radius="xl"),
        dmc.Select(id="child_control", className="child_control", value="all",
                   placeholder="Select Member", clearable=False, searchable=False,
                   rightSection=DashIconify(icon="radix-icons:chevron-down", color="black"),
                   style={"width": "calc(100% - 50px)"})
    ], spacing="10px"
    )
])

# Controls
control = dmc.Group([
    dmc.Group(className="filter_container", children=[
        html.P("FILTERS", className="filter_label", id="filter_label"),
        dmc.SegmentedControl(id="time_control", className="time_control", value="""{"KPI": "A", "delta": 365}""", radius="md", size="xs",
            data=[
                {"label": "Daily", "value": """{"KPI": "D", "delta": 1}"""},
                {"label": "Weekly", "value": """{"KPI": "W", "delta": 7}"""},
                {"label": "Monthly", "value": """{"KPI": "M", "delta": 30}"""},
                {"label": "Quarterly", "value": """{"KPI": "3M", "delta": 90}"""},
                {"label": "Yearly", "value": """{"KPI": "A", "delta": 365}"""},
                {"label": "Custom Range", "value": "all"}
            ]
        ),
        dbc.Popover(id="popover_date_picker", className="popover_date_picker", children=[
            dbc.PopoverHeader("Selected Date Range", className="popover_date_picker_label"),
            dmc.DateRangePicker(id="date_range_picker", className="date_range_picker", clearable=False, inputFormat="MMM DD, YYYY", icon=DashIconify(icon=f"arcticons:calendar-{datetime.now().day}", color="black", width=30),
                                value=[datetime.now().date() - timedelta(days=30), datetime.now().date()])
        ], target="time_control", placement="bottom", trigger="legacy", hide_arrow=True
        ),
        html.Div(className="platform_dropdown_container", children=[
            html.P("Social Platform", className="platform_dropdown_label"),
            dmc.Select(className="platform_dropdown", id="platform_dropdown", clearable=False, searchable=False, value="all",
                data=[{"label": "All Platforms", "value": "all"}] + [{"label": i.title(), "value": i} for i in df["platform_contents"].unique() if ((str(i).lower() != "nan") and (str(i).lower() != "no"))],
                rightSection=DashIconify(icon="radix-icons:chevron-down", color="black")
            )
        ]),
        html.Div(className="alert_dropdown_container", children=[
            html.P("Alert Level", className="alert_dropdown_label"),
            dmc.Select(className="alert_dropdown", id="alert_dropdown", clearable=False, searchable=False, value="all",
                data=[{"label": "All Alerts", "value": "all"}] + [{"label": i.title(), "value": i}
                for i in sorted(df["alert_contents"].unique(), key=lambda x: ["high", "medium", "low"].index(x.lower())
                    if isinstance(x, str) and x.lower() in ["high", "medium", "low"] else float("inf"))
                    if (isinstance(i, str) and str(i).lower() != "nan") and (str(i).lower() != "no")],
                rightSection=DashIconify(icon="radix-icons:chevron-down", color="black")
            )
        ]),
        dmc.ActionIcon(DashIconify(icon="grommet-icons:power-reset", color="white", width=25, flip="horizontal"), id="reset_filter_container", n_clicks=0, variant="transparent")
    ], spacing="10px"
    ),
    dmc.TextInput(className="searchbar", id="searchbar", placeholder=" Search...", radius="5px", size="lg", icon=html.Img(src="assets/images/chatstatlogo_black.png", width="50%"))
], style={"margin": "10px"}, spacing="10px"
)

# KPI Card
kpi_cards = html.Div([
    dmc.Card(id="kpi_alert_count", withBorder=True, radius="5px", style={"width": "auto", "margin": "0px 10px 0px 0px", "box-shadow": ""}),
    dmc.Group(id="kpi_platform_count", className="kpi_platform_count", position="center", spacing="10px")
    ], style={"display": "flex", "flexDirection": "row", "margin": "10px", "padding": "0px"}
)


# Page Charts
dashboard_charts = html.Div(children=[
    dbc.Row([
        dbc.Col(id="content_classification_radial_chart", className="content_classification_radial_chart", style={"margin": "0px 0px 0px 0px", "padding": "0px", "box-shadow": ""}),
        dbc.Col(id="content_classification_horizontal_bar", className="content_classification_horizontal_bar", style={"margin": "0px 5px 0px 0px", "padding": "0px", "box-shadow": ""}),
        dbc.Col(id="content_risk_bar_chart", className="content_risk_bar_chart", style={"margin": "0px 0px 0px 5px", "padding": "0px", "box-shadow": ""})
    ], style={"margin": "10px", "padding": "0px"}
    ),
    dmc.Group([
        html.Div(id="comment_alert_line_chart_container", className="comment_alert_line_chart_container", children=[
            html.Div(id="comment_alert_line_chart"),
            html.Div(dcc.RangeSlider(id="comment_alert_line_chart_slider", updatemode="drag", pushable=1, min=0, max=730, value=[0, 730]), style={"height": "50px"})
            ], style={"width": "calc(65% - 5px)", "background-color": "white", "box-shadow": ""}
        ),
        html.Div(id="comment_classification_pie_chart", className="comment_classification_pie_chart", style={"width": "calc(35% - 5px)", "background-color": "white", "box-shadow": ""})
    ], spacing="10px", style={"margin": "10px", "padding": "0px"}
    ),
], style={"height": "100%", "width": "100%", "margin": "0px", "padding": "0px"})

analytics_charts = html.Div(children=[
    dmc.LoadingOverlay(
        dcc.Graph(id="content_result_treemap"), loaderProps={"variant": "bars", "color": "orange", "size": "xl"}, style={"width": "100%"}
    ),
    dcc.Graph(id="comment_result_radar", style={"width": "100%"}),
    dcc.Graph(id="content_result_bubble_chart", style={"width": "100%"}),
])


# Designing Main App
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=["https://fonts.googleapis.com/css2?family=Poppins:wght@200;300;400;500;600;700&display=swap", dbc.themes.BOOTSTRAP, dbc.themes.MATERIA, dbc.icons.FONT_AWESOME])
server = app.server
app.css.config.serve_locally = True
app.title = "Parent Dashboard"
app.layout = html.Div(
    children=[
        dcc.Interval(id="time_interval", disabled=True),
        dcc.Location(id="url_path", refresh=False),
        html.Div(children=[], style={"width": "4.5rem", "display": "inline-block"}),
        html.Div(id="page_content", style={"display": "inline-block", "width": "calc(100% - 4.5rem)"})
    ],
)


# Website Page Navigation
@app.callback(Output("page_content", "children"),
              [Input("url_path", "pathname")]
)
def display_page(pathname):
    if pathname == "/dashboard":
        return [sidebar, dashboard_header, control, kpi_cards, dashboard_charts]
    elif pathname == "/analytics":
        return [sidebar, analytics_header, analytics_charts]
    elif pathname == "/report":
        return [sidebar]
    else:
        return [sidebar]


# Child Control Avatar
@app.callback(
    Output("child_control_avatar", "children"),
    Input("child_control", "value")
)
def update_child_control_avatar(child_value):
    avatar_text = "".join([name[0].title() for name in child_value.split(" ")])
    return avatar_text


# Child Control Drop Down
@app.callback(
    Output("child_control", "data"),
    [Input("time_interval", "n_intervals")]
)
def update_child_control(time_interval):
    user_df = df.copy()
    user_list = user_df["name_childrens"].unique()
    data = [{"value": "all", "label": "All Members"}] + [{"value": i, "label": i.split(" ")[0].title()} for i in user_list]
    return data


# Date Picker
@app.callback(
    [Output("popover_date_picker", "style"), Output("popover_date_picker", "offset")],
    [Input("time_control", "value")]
)
def update_popover_date_picker(time_value):
    if(time_value == "all"):
        return {"display": "block"}, "160,10"
    else:
        return {"display": "none"}, ""


# Platform Dropdown
@app.callback(
    Output("platform_dropdown", "icon"),
    Input("platform_dropdown", "value")
)
def update_platform_dropdown(platform_value):
    if(platform_value in ["all", None]):
        return DashIconify(icon="gis:earth-australia-o", color="#23a8fe", width=20)
    else:
        return DashIconify(icon=platform_icons[platform_value.title()], width=20)


# Alert Dropdown
@app.callback(
    Output("alert_dropdown", "icon"),
    Input("alert_dropdown", "value")
)
def update_alert_dropdown(alert_value):
    if(alert_value in ["all", None]):
        return DashIconify(icon="line-md:alert", color="#012749", width=30)
    else:
        return DashIconify(icon="line-md:alert", color=alert_colors[alert_value.title()], width=30)


# Reset Filter Container
@app.callback(
    [Output("time_control", "value"), Output("platform_dropdown", "value"), Output("alert_dropdown", "value")],
    Input("reset_filter_container", "n_clicks"),
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    return """{"KPI": "A", "delta": 365}""", "all", "all"


# KPI Count Card
@app.callback(
    Output("kpi_alert_count", "children"),
    [Input("child_control", "value"), Input("time_control", "value"), Input("date_range_picker", "value")]
)
def update_kpi_count(child_value, time_value, date_range_value):
    alert_count_df = df.copy()
    alert_count_df = alert_count_df[(alert_count_df["alert_contents"].str.lower() != "no") & (alert_count_df["alert_contents"].str.lower() != "") & (alert_count_df["alert_contents"].notna())]

    # Filters
    alert_count_df = child_filter(alert_count_df, child_value)
    if(time_value == "all"):
        alert_count_df = time_filter(alert_count_df, time_value, date_range_value)
        card = dmc.Stack(children=[
                dmc.Text("Number of Alerts", id="kpi_alert_count_label", className="kpi_alert_count_label"),
                dmc.Group(children=[
                    dmc.Text(alert_count_df["id_contents"].nunique(), style={"color": "#052F5F", "fontSize": "40px", "fontFamily": "Poppins", "fontWeight": 600}),
                    dmc.Stack([
                        dmc.Text("Between ", color="dimmed", style={"fontSize": "12px", "fontFamily": "Poppins", "text-align": "right"}),
                        dmc.Text(datetime.strptime(date_range_value[0], "%Y-%m-%d").strftime("%b %d, %Y"), color="dimmed", style={"fontSize": "12px", "fontFamily": "Poppins", "text-align": "right"}),
                        dmc.Text("& " + datetime.strptime(date_range_value[1], "%Y-%m-%d").strftime("%b %d, %Y"), color="dimmed", style={"fontSize": "12px", "fontFamily": "Poppins", "text-align": "right"})
                        ], align="center", justify="center", spacing="0px")
                ], position="center", style={"margin": "0px", "padding": "0px"}),
            ], spacing="0px")
        return card

    else:
        time_value = json.loads(time_value)

        alert_count_df["createTime_contents"] = pd.to_datetime(alert_count_df["createTime_contents"], format="%Y-%m-%d %H:%M:%S.%f")
        alert_count_df.set_index("createTime_contents", inplace=True)
        alert_count_df = alert_count_df.resample(time_value["KPI"])["id_contents"].nunique()
        alert_count_df = alert_count_df.reset_index()
        alert_count_df.columns = ["date", "count"]
        if(len(alert_count_df) == 1):
            alert_count_df["increase"] = alert_count_df["count"].diff().fillna(alert_count_df["count"].iloc[0]).astype(int)
        else:
            alert_count_df["increase"] = alert_count_df["count"].diff().fillna(0).astype(int)
        alert_count_df["date"] = alert_count_df["date"].dt.date
        alert_count_df = alert_count_df.sort_values(by="date", ascending=False)

        if(time_value["KPI"] == "W"):
            today = datetime.today().date() - timedelta(days=365)
            date_comparison = today + timedelta(days=(6 - today.weekday()) % 7)
            metric_text = "vs Last Week"
        elif(time_value["KPI"] == "M"):
            today = datetime.today().date() - timedelta(days=365)
            date_comparison = datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[-1]).date()
            metric_text = "vs Last Month"
        elif(time_value["KPI"] == "3M"):
            today = datetime.today().date() - timedelta(days=365)
            date_comparison = (today + pd.tseries.offsets.QuarterEnd(0)).date()
            metric_text = "vs Last Quarter"
        elif(time_value["KPI"] == "A"):
            today = datetime.today().date() - timedelta(days=365)
            date_comparison = datetime(today.year, 12, 31).date()
            metric_text = "vs Last Year"
        else:
            date_comparison = datetime.today().date() - timedelta(days=365)
            metric_text = "vs Last Day"

        if(date_comparison in alert_count_df["date"].values):
            card = dmc.Stack(children=[
                dmc.Text("Number of Alerts", id="kpi_alert_count_label", className="kpi_alert_count_label"),
                dmc.Group(children=[
                    dmc.Text(alert_count_df["count"].iloc[0], style={"color": "#052F5F", "fontSize": "40px", "fontFamily": "Poppins", "fontWeight": 600}),
                    dmc.Stack([
                        dmc.Text("▲"+str(alert_count_df["increase"].iloc[0]) if alert_count_df["increase"].iloc[0] >= 0 else "▼"+str(alert_count_df["increase"].iloc[0]),
                                 style={"color": "#25D366" if alert_count_df["increase"].iloc[0] >= 0 else "#FF5100", "fontSize": "20px", "fontFamily": "Poppins", "fontWeight": 600}),
                        dmc.Text(metric_text, color="dimmed", style={"fontSize": "12px", "fontFamily": "Poppins", "text-align": "right"})
                        ], align="center", justify="center", spacing="0px")
                ], position="center", style={"margin": "0px", "padding": "0px"}),
            ], spacing="0px")
        else:
            card = dmc.Stack(children=[
                dmc.Text("Number of Alerts", id="kpi_alert_count_label", className="kpi_alert_count_label"),
                dmc.Text("No Data Found", color="black", style={"fontSize": 17, "fontFamily": "Poppins", "fontWeight": "bold", "text-align": "center"})
            ])
        return card


# KPI Platform Card
@app.callback(
    Output("kpi_platform_count", "children"),
    [Input("child_control", "value"), Input("time_control", "value"), Input("date_range_picker", "value"), Input("alert_dropdown", "value")]
)
def update_kpi_platform(child_value, time_value, date_range_value, alert_value):
    kpi_platform_df = df.copy()
    kpi_platform_df = kpi_platform_df[(kpi_platform_df["alert_contents"].str.lower() != "no") & (kpi_platform_df["alert_contents"].str.lower() != "") & (kpi_platform_df["alert_contents"].notna())]
    kpi_platform_df = kpi_platform_df[(kpi_platform_df["result_contents"].str.lower() != "no") & (kpi_platform_df["result_contents"].str.lower() != "") & (kpi_platform_df["result_contents"].notna())]

    # Filters
    kpi_platform_df = child_filter(kpi_platform_df, child_value)
    kpi_platform_df = time_filter(kpi_platform_df, time_value, date_range_value)
    kpi_platform_df = alert_filter(kpi_platform_df, alert_value)

    if(len(kpi_platform_df) == 0):
        card = dmc.Card(children=[
            dmc.Text("No Cards to Display", color="black", style={"fontSize": 17, "fontFamily": "Poppins", "fontWeight": "bold"})
            ], withBorder=True, radius="5px", style={"height": "100%", "width": "100%", "display": "flex", "justify-content": "center", "align-items": "center", "box-shadow": ""}
        )
        return card
    else:
        kpi_platform_df = kpi_platform_df.groupby(by=["platform_contents", "result_contents"], as_index=False)["id_contents"].nunique()
        kpi_platform_df.columns = ["platform", "result", "count"]
        kpi_platform_df.sort_values(by=["platform", "count"], ascending=[True, False], inplace=True)

        kpi_list = []
        number_of_platforms = len(kpi_platform_df["platform"].unique())
        for platform in kpi_platform_df["platform"].unique():
            platform_df = kpi_platform_df[kpi_platform_df["platform"] == platform]
            title = platform.title()+f" - {alert_value} Alerts" if ((alert_value is not None) and (alert_value != "all")) else platform.title()
            kpi_list.append(
                dmc.Card(children=[
                    dmc.Text(title, style={"color": "black", "fontSize": "18px", "fontFamily": "Poppins, verdana", "fontWeight": "bold"}),
                    dmc.Group(children=[
                        dmc.Image(src=f"assets/images/{platform}.png", height="50px", width="50px"),
                        dmc.Stack(children=[
                            html.Div(children=[
                                dmc.Text(row["result"], style={"color": "#979797", "fontSize": "12px", "fontFamily": "Poppins"}),
                                dmc.Space(w="25px"),
                                dmc.Text(row["count"], style={"color": "#052F5F", "fontSize": "12px", "fontFamily": "Poppins", "fontWeight": "bold"})
                            ], style={"display": "flex", "justifyContent": "space-between", "width": "100%"})
                            for index, row in platform_df.iterrows()],
                            align="flex-start", justify="flex-end", spacing="0px"
                        ),
                        dmc.Text(platform_df["count"].sum(), style={"color": "#052F5F", "fontSize": "40px", "fontFamily": "Poppins", "fontWeight": 600})
                    ], position="apart")
                ], withBorder=True, radius="5px", style={"width": f"""calc((100% - {10*(number_of_platforms-1)}px) / {number_of_platforms})""", "box-shadow": ""}
                )
            )
        return kpi_list


# Content Classification Radial Chart
@app.callback(
    Output("content_classification_radial_chart", "children"),
    [Input("child_control", "value"), Input("time_control", "value"), Input("date_range_picker", "value"), Input("platform_dropdown", "value"), Input("alert_dropdown", "value")]
)
def update_radial_chart(child_value, time_value, date_range_value, platform_value, alert_value):
    result_contents_df = df.copy()
    result_contents_df = result_contents_df[(result_contents_df["result_contents"].str.lower() != "no") & (result_contents_df["result_contents"].str.lower() != "") & (result_contents_df["result_contents"].notna())]
    result_contents_df = result_contents_df[(result_contents_df["alert_contents"].str.lower() != "no") & (result_contents_df["alert_contents"].str.lower() != "") & (result_contents_df["alert_contents"].notna())]

    # Filters
    result_contents_df = child_filter(result_contents_df, child_value)
    result_contents_df = time_filter(result_contents_df, time_value, date_range_value)
    result_contents_df = platform_filter(result_contents_df, platform_value)
    result_contents_df = alert_filter(result_contents_df, alert_value)

    if(len(result_contents_df) == 0):
        return no_data_graph()
    else:
        result_contents_df = result_contents_df.groupby(by=["result_contents"], as_index=False)["id_contents"].nunique()
        result_contents_df.columns = ["classification", "count"]
        result_contents_df["radial"] = (result_contents_df["count"] / result_contents_df["count"].max()) * 270
        result_contents_df.sort_values(by=["radial"], ascending=True, inplace=True)

        if(((platform_value is not None) and (platform_value != "all")) and ((alert_value is not None) and (alert_value != "all"))):
            title = f"Comment Classification - {platform_value} & {alert_value} Alerts"
        elif((platform_value is not None) and (platform_value != "all")):
            title = f"Content Classification - {platform_value}"
        elif((alert_value is not None) and (alert_value != "all")):
            title = f"Content Classification - {alert_value} Alerts"
        else:
            title = "Content Classification"
        return [
            html.P(title, style={"color": "#052F5F", "fontWeight": "bold", "fontSize": 17, "margin": "10px 25px 0px 25px"}),
            html.Img(src=radial_bar_chart.radial_chart(result_contents_df, platform_value, alert_value), width="100%")
        ]


# Content Classification Horizontal Bar
@app.callback(
    Output("content_classification_horizontal_bar", "children"),
    [Input("child_control", "value"), Input("time_control", "value"), Input("date_range_picker", "value")]
)
def update_horizontal_bar(child_value, time_value, date_range_value):
    content_bar_df = df.copy()
    content_bar_df = content_bar_df[(content_bar_df["result_contents"].str.lower() != "no") & (content_bar_df["result_contents"].str.lower() != "") & (content_bar_df["result_contents"].notna())]
    content_bar_df = content_bar_df[(content_bar_df["alert_contents"].str.lower() != "no") & (content_bar_df["alert_contents"].str.lower() != "") & (content_bar_df["alert_contents"].notna())]

    # Filters
    content_bar_df = child_filter(content_bar_df, child_value)
    content_bar_df = time_filter(content_bar_df, time_value, date_range_value)

    if(len(content_bar_df) == 0):
        return no_data_graph()
    else:
        content_bar_df = content_bar_df.groupby(by=["result_contents"], as_index=False)["id_contents"].nunique()
        content_bar_df.columns = ["classification", "count"]
        content_bar_df["percentage_of_total"] = (content_bar_df["count"] / content_bar_df["count"].sum()) * 100
        bar_sections = []
        bar_legend = []
        for index, row in content_bar_df.iterrows():
            bar_sections.append({"value": row["percentage_of_total"], "color": classification_bar_colors[row["classification"]], "label": str(int(row["percentage_of_total"]))+"%"})
            bar_legend.append([
                dmc.Col(dmc.Badge(row["classification"], variant="dot", color=classification_bar_colors[row["classification"]], size="xl", radius="xl", style={"border": "white", "fontSize": 14, "text-align": "left"}), span=6),
                dmc.Col(html.Header(row["count"], style={"color": "#081A51", "fontFamily": "Poppins", "fontWeight": "bold", "fontSize": 14, "text-align": "right", "margin": "auto"}), span=3),
                dmc.Col(dmc.Avatar(str(int(row["percentage_of_total"]))+"%", size="md", radius="xl", color="#2D96FF"), span=2, offset=1)
                ]
            )
        return [
            html.Header("Risk Categories Classification", style={"color": "#052F5F", "fontWeight": "bold", "fontSize": 17, "margin": "10px 25px 0px 25px"}),
            dmc.Space(h="lg"),
            dmc.Progress(sections=bar_sections, radius="xl", size=25, animate=False, striped=False, style={"width": "90%", "margin": "auto"}),
            dmc.Space(h="lg"),
            dmc.Grid(children=sum(bar_legend, []), gutter="xs", justify="center", align="center", style={"margin": "20px"})
            ]


# Content Risk Bar Chart
@app.callback(
    Output("content_risk_bar_chart", "children"),
    [Input("child_control", "value"), Input("time_control", "value"), Input("date_range_picker", "value"), Input("platform_dropdown", "value")]
)
def update_bar_chart(child_value, time_value, date_range_value, platform_value):
    risk_content_df = df.copy()
    risk_content_df = risk_content_df[(risk_content_df["alert_contents"].str.lower() != "no") & (risk_content_df["alert_contents"].str.lower() != "") & (risk_content_df["alert_contents"].notna())]

    # Filters
    risk_content_df = child_filter(risk_content_df, child_value)
    risk_content_df = time_filter(risk_content_df, time_value, date_range_value)
    risk_content_df = platform_filter(risk_content_df, platform_value)

    if(len(risk_content_df) == 0):
        return no_data_graph()
    else:
        risk_content_df["createTime_contents"] = pd.to_datetime(risk_content_df["createTime_contents"], format="%Y-%m-%d %H:%M:%S.%f")
        risk_content_df = risk_content_df.groupby(by=["alert_contents", "platform_contents"], as_index=False)["id_contents"].nunique()
        risk_content_df.columns = ["alert", "platform", "count"]
        categories = ["High", "Medium", "Low"]

        # Handling Missing Values
        for platform in risk_content_df["platform"].unique():
            for cat in categories:
                if(cat not in risk_content_df["platform"].unique()):
                    new_row = {"alert": cat, "platform": platform.title(), "count": 0}
                    risk_content_df = pd.concat([risk_content_df, pd.DataFrame(new_row, index=[len(risk_content_df)])])

        risk_content_df["alert"] = pd.Categorical(risk_content_df["alert"], categories=categories, ordered=True)
        risk_content_df = risk_content_df.sort_values(by="alert")

        if((platform_value is None) or (platform_value == "all")):
            content_risk = px.bar(risk_content_df, x="alert", y="count", color="platform", text_auto=True, color_discrete_map=platform_colors, pattern_shape_sequence=None)
            content_risk.update_layout(title="<b>Alerts on User Content</b>", title_font_color="#052F5F", title_font=dict(size=17, family="Poppins"))
        else:
            content_risk = px.bar(risk_content_df, x="alert", y="count", color="alert", text_auto=True, color_discrete_map=alert_colors, pattern_shape_sequence=None)
            content_risk.update_layout(title=f"<b>Alerts on User Content - {platform_value}</b>", title_font_color="#052F5F", title_font=dict(size=17, family="Poppins"))

        content_risk.update_layout(margin=dict(l=25, r=25, b=0))
        content_risk.update_layout(legend=dict(font=dict(family="Poppins"), traceorder="grouped", orientation="h", x=1, y=1, xanchor="right", yanchor="bottom", title_text="", bgcolor="rgba(0,0,0,0)"))
        content_risk.update_traces(width=0.4, marker_line=dict(color="black", width=1.5), textangle=0)
        content_risk.update_traces(textfont=dict(color="#052F5F", size=16, family="Poppins"))
        content_risk.update_layout(xaxis_title="", yaxis_title="", legend_title_text="", plot_bgcolor="rgba(0, 0, 0, 0)")
        content_risk.update_layout(yaxis_showgrid=True, yaxis=dict(tickfont=dict(size=12, family="Poppins", color="#8E8E8E"), griddash="dash", gridwidth=1, gridcolor="#DADADA"))
        content_risk.update_layout(xaxis_showgrid=False, xaxis=dict(tickfont=dict(size=18, family="Poppins", color="#052F5F")))
        content_risk.update_xaxes(fixedrange=True)
        content_risk.update_yaxes(fixedrange=True)
        return dcc.Graph(figure=content_risk, responsive=True, config=plot_config, style={"height": "100%", "width": "100%"})


# Comment Alert Line Chart
@app.callback(
    Output("comment_alert_line_chart", "children"),
    [Input("child_control", "value"), Input("alert_dropdown", "value"), Input("comment_alert_line_chart_slider", "value")]
)
def update_line_chart(child_value, alert_value, slider_value):
    alert_comment_df = df.copy()
    alert_comment_df = alert_comment_df[(alert_comment_df["alert_comments"].str.lower() != "no") & (alert_comment_df["alert_comments"].str.lower() != "") & (alert_comment_df["alert_comments"].notna())]

    # Filters
    alert_comment_df = child_filter(alert_comment_df, child_value)
    alert_comment_df = alert_filter(alert_comment_df, alert_value)
    alert_comment_df = slider_filter(alert_comment_df, slider_value)

    if(len(alert_comment_df) == 0):
        return no_data_graph()
    else:
        alert_comment_df["commentTime_comments"] = pd.to_datetime(alert_comment_df["commentTime_comments"], format="%Y-%m-%d").dt.strftime("%b %Y")
        alert_comment_df = alert_comment_df.groupby(by=["commentTime_comments", "platform_comments"], as_index=False)["id_contents"].nunique()
        alert_comment_df.columns = ["commentTime", "platform", "count"]
        alert_comment_df["commentTime"] = pd.to_datetime(alert_comment_df["commentTime"], format="%b %Y")
        alert_comment_df.sort_values(by="commentTime", inplace=True)

        comment_alert = px.line(alert_comment_df, x="commentTime", y="count", color="platform", color_discrete_map=platform_colors, symbol_sequence=[])
        comment_alert.update_layout(margin=dict(l=25, r=25, b=0), height=400)
        comment_alert.update_layout(legend=dict(font=dict(family="Poppins"), traceorder="grouped", orientation="h", x=1, y=1, xanchor="right", yanchor="bottom", title_text=""))
        comment_alert.update_layout(xaxis_title="", yaxis_title="", legend_title_text="", plot_bgcolor="rgba(0, 0, 0, 0)")
        comment_alert.update_layout(yaxis_showgrid=True, yaxis=dict(tickfont=dict(size=12, family="Poppins", color="#8E8E8E"), griddash="dash", gridwidth=1, gridcolor="#DADADA"))
        comment_alert.update_layout(xaxis_showgrid=False, xaxis=dict(tickfont=dict(size=9, family="Poppins", color="#052F5F"), tickangle=0))
        comment_alert.update_traces(mode="lines+markers", line=dict(width=2), marker=dict(sizemode="diameter", size=8, color="white", line=dict(width=2)))
        comment_alert.update_xaxes(fixedrange=True)
        comment_alert.update_yaxes(fixedrange=True)
        comment_alert.add_vline(x=alert_comment_df[alert_comment_df["count"] == alert_comment_df["count"].max()]["commentTime"].iloc[0], line_width=2, line_dash="dashdot", line_color="#017EFA")

        if((alert_value is not None) and (alert_value != "all")):
            comment_alert.update_layout(title=f"<b>Alerts on Comments Received - {alert_value} Alerts</b>", title_font_color="#052F5F", title_font=dict(size=17, family="Poppins"))
        else:
            comment_alert.update_layout(title="<b>Alerts on Comments Received</b>", title_font_color="#052F5F", title_font=dict(size=17, family="Poppins"))
        return dcc.Graph(figure=comment_alert, config=plot_config)


# Comment Alert Line Chart Slider
@app.callback(
    [Output("comment_alert_line_chart_slider", "marks"), Output("comment_alert_line_chart_slider", "max"),
     Output("comment_alert_line_chart_slider", "min"), Output("comment_alert_line_chart_slider", "value")],
    [Input("child_control", "value")]
)
def update_line_chart_slider(child_value):
    slider_df = df.copy()
    slider_df = slider_df[(slider_df["alert_comments"].str.lower() != "no") & (slider_df["alert_comments"].str.lower() != "") & (slider_df["alert_comments"].notna())]

    # Filters
    slider_df = child_filter(slider_df, child_value)

    slider_df["commentTime_comments"] = pd.to_datetime(slider_df["commentTime_comments"], format="%Y-%m-%d %H:%M:%S").dt.date
    slider_df = slider_df[slider_df["commentTime_comments"] >= date.today()-timedelta(days=365*2)]

    try:
        min_date = slider_df["commentTime_comments"].min()
        max_date = slider_df["commentTime_comments"].max()
        date_range = range((max_date - min_date).days + 1)
    except:
        min_date = datetime.now() - timedelta(days=365)
        max_date = datetime.now()
        date_range = range((max_date - min_date).days + 1)

    maximum_mark = max(date_range)
    minimum_mark = min(date_range)
    date_list = [min_date + timedelta(days=i) for i in date_range]

    global date_dict
    date_dict = {i: d.strftime("%Y-%m-%d") for i, d in enumerate(date_list)}
    marks = {i: {"label": d.strftime("%b %Y"), "style": {"fontFamily": "Poppins", "fontWeight": "bold", "fontSize": 10}} for i, d in enumerate(date_list) if ((d.month in [1, 4, 7, 10]) and (d.day == 1))}
    return marks, maximum_mark, minimum_mark, [minimum_mark, maximum_mark]


# Comment Classification Pie Chart
@app.callback(
    Output("comment_classification_pie_chart", "children"),
    [Input("child_control", "value"), Input("time_control", "value"), Input("date_range_picker", "value"), Input("platform_dropdown", "value"), Input("alert_dropdown", "value")]
)
def update_pie_chart(child_value, time_value, date_range_value, platform_value, alert_value):
    result_comment_df = df.copy()
    result_comment_df = result_comment_df[(result_comment_df["result_comments"].str.lower() != "no") & (result_comment_df["result_comments"].str.lower() != "") & (result_comment_df["result_comments"].notna())]
    result_comment_df = result_comment_df[(result_comment_df["alert_comments"].str.lower() != "no") & (result_comment_df["alert_comments"].str.lower() != "") & (result_comment_df["alert_comments"].notna())]

    # Filters
    result_comment_df = child_filter(result_comment_df, child_value)
    result_comment_df = time_filter(result_comment_df, time_value, date_range_value)
    result_comment_df = platform_filter(result_comment_df, platform_value)
    result_comment_df = alert_filter(result_comment_df, alert_value)

    if(len(result_comment_df) == 0):
        return no_data_graph()
    else:
        result_comment_df["createTime_contents"] = pd.to_datetime(result_comment_df["createTime_contents"], format="%Y-%m-%d %H:%M:%S.%f")
        result_comment_df = result_comment_df.groupby(by=["result_comments"], as_index=False)["id_comments"].nunique()
        result_comment_df.columns = ["classification", "count"]
        result_comment_df.sort_values(by=["count"], ascending=True, inplace=True)

        comment_classification = px.pie(result_comment_df, values="count", names="classification", color="classification", color_discrete_map=content_classification_colors)
        comment_classification.update_layout(margin=dict(l=25, r=25), plot_bgcolor="white", paper_bgcolor="white")
        comment_classification.update_layout(annotations=[dict(text="<b>"+str(result_comment_df["count"].sum())+"</b>", x=0.5, y=0.55, font=dict(family="Poppins", size=28, color="#052F5F"), showarrow=False),
                                                          dict(text="Total Comments", x=0.5, y=0.45, font=dict(family="Poppins", size=18, color="#052F5F"), showarrow=False)]
                                             )
        comment_classification.update_layout(legend={"orientation": "h", "x": 0.5, "y": -0.1, "xanchor": "center", "font": {"family": "Poppins", "color": "#2a3f5f", "size": 12}})
        comment_classification.update_traces(textinfo="percent", texttemplate="<b>%{percent}</b>", textposition="outside")
        comment_classification.update_traces(outsidetextfont=dict(family="Poppins", size=14, color="black"), insidetextorientation="horizontal")
        comment_classification.update_traces(hole=0.65, marker=dict(line=dict(color="white", width=2.5)))

        if(((platform_value is not None) and (platform_value != "all")) and ((alert_value is not None) and (alert_value != "all"))):
            comment_classification.update_layout(title={"text": f"<b>Comment Classification - {platform_value} &<br>{alert_value} Alerts</b>"}, title_font_color="#052F5F", title_font=dict(family="Poppins", size=17))
        elif((platform_value is not None) and (platform_value != "all")):
            comment_classification.update_layout(title={"text": f"<b>Comment Classification - {platform_value}</b>"}, title_font_color="#052F5F", title_font=dict(family="Poppins", size=17))
        elif((alert_value is not None) and (alert_value != "all")):
            comment_classification.update_layout(title={"text": f"<b>Comment Classification - {alert_value} Alerts</b>"}, title_font_color="#052F5F", title_font=dict(family="Poppins", size=17))
        else:
            comment_classification.update_layout(title={"text": "<b>Comment Classification</b>"}, title_font_color="#052F5F", title_font=dict(family="Poppins", size=17))
        return dcc.Graph(figure=comment_classification, config=plot_config)


# Content Result Treemap
@app.callback(
    Output("content_result_treemap", "figure"),
    [Input("time_interval", "n_intervals")]
)
def update_content_treemap(time_interval):
    content_json_df = df.copy()

    content_json_df = content_json_df[(content_json_df["result_json_contents"].str.lower() != "no") & (content_json_df["result_json_contents"].str.lower() != "") & (content_json_df["result_json_contents"].notna())]
    treemap_data = {"category": [], "subcategory": [], "value": []}

    for index, row in content_json_df.iterrows():
        result_json_contents = ast.literal_eval(row["result_json_contents"])
        for category, subcategory_values in result_json_contents.items():
            for subcategory, value in subcategory_values.items():
                treemap_data["category"].append(category)
                treemap_data["subcategory"].append(subcategory)
                treemap_data["value"].append(value)

    content_json_df = pd.DataFrame(treemap_data)
    content_json_df = content_json_df[content_json_df["value"] != 0]
    content_json_df = content_json_df.groupby(by=["category", "subcategory"], as_index=False)["value"].count()
    content_json_df.sort_values(by=["category", "value"], ascending=[True, False], inplace=True)

    content_treemap = px.treemap(content_json_df, path=[px.Constant("Content"), "category", "subcategory"], values="value", color="category", color_discrete_map={})
    content_treemap.update_layout(margin=dict(t=20, l=0, r=0, b=0))
    content_treemap.update_layout(uniformtext=dict(minsize=10, mode="hide"))
    content_treemap.update_traces(marker=dict(cornerradius=10), root_color="white")
    return content_treemap


# Comment Result Radar
@app.callback(
    Output("comment_result_radar", "figure"),
    [Input("time_interval", "n_intervals")]
)
def update_radar_chart(time_interval):
    comment_json_df = df.copy()
    comment_json_df = comment_json_df[(comment_json_df["result_json_comments"].str.lower() != "no") & (comment_json_df["result_json_comments"].str.lower() != "") & (comment_json_df["result_json_comments"].notna())]
    comment_json_df = pd.DataFrame(list(comment_json_df["result_json_comments"].apply(ast.literal_eval)))
    comment_json_df = comment_json_df.to_dict(orient="list")
    comment_json_df = {key: np.mean([x for x in values if not np.isnan(x)])*100 for key, values in comment_json_df.items()}

    values = comment_json_df.values()
    categories = comment_json_df.keys()
    text = [str(round(value, 2))+"%" for value in values]

    fig = px.line_polar(r=values, theta=categories, line_close=True, markers=True, text=text)
    fig.update_layout(template=None, polar=dict(bgcolor="rgba(255, 255, 255, 0.2)"))
    fig.update_traces(fill="toself", textposition="top center")
    return fig


# Content Result Bubble Chart
@app.callback(
    Output("content_result_bubble_chart", "figure"),
    [Input("time_interval", "n_intervals")]
)
def update_bubble_chart(time_interval):
    content_df = df.copy()

    content_df = content_df[(content_df["result_json_contents"].str.lower() != "no") & (content_df["result_json_contents"].str.lower() != "") & (content_df["result_json_contents"].notna())]
    content_df = content_df[["result_json_contents", "createTime_contents"]]
    content_df = content_df.drop_duplicates()

    content_result_df = pd.DataFrame(columns=["category", "subcategory", "value", "date"])
    for index, row in content_df.iterrows():
        json_data = json.loads(row["result_json_contents"].replace("'", '"'))
        for category, subcategories in json_data.items():
            for subcategory, value in subcategories.items():
                content_result_df.loc[len(content_result_df.index)] = [category, subcategory, value, str(row["createTime_contents"])]

    fig = go.Figure(data=go.Scatter(x=[1, 2, 3, 4], y=[10, 11, 12, 13], mode="lines"))
    return fig


# Running Main App
if __name__ == "__main__":
    app.run_server(debug=False)