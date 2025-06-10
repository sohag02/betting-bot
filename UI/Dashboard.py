import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import streamlit as st
import pandas as pd
import plotly.express as px
from src.analytics.summary import calculate_bet_metrics

st.set_page_config(page_title="Dashboard", layout="wide")
st.title("Dashboard")
if st.button("🔄 Reload"):
    st.rerun()


st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stAppDeployButton {display:none;}
        .stAppHeader {display:none;}
        .stMainBlockContainer {padding-top: 0;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)


def sidebar_btn(section: str, label: str):
    st.html(
        f"""
        <a href="#{section}" style="
            display: block;
            padding: 10px 16px;
            margin-bottom: 8px;
            background-color: #f0f0f0;
            color: #333;
            text-decoration: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            transition: background-color 0.2s ease;
            "
            onmouseover="this.style.backgroundColor='#e0e0e0';"
            onmouseout="this.style.backgroundColor='#f0f0f0';"
        >
            {label}
        </a>
    """
    )


with st.sidebar:
    sidebar_btn("kpis", "KPIs")
    sidebar_btn("charts", "Charts")
    sidebar_btn("daily-report", "Daily Report")


@st.cache_data(ttl=10)  # cache for 10 seconds
def load_data():
    return pd.read_csv("data/betting_log.csv", parse_dates=["timestamp"])

df = load_data()


def capital_growth_chart(df: pd.DataFrame):
    for i, _ in df.iterrows():
        df.at[i, "round_id"] = i + 1

    data = pd.DataFrame({
        'x': df["round_id"],
        'y': df["balance"]
    })

    data = data.set_index('x')

    return st.line_chart(data)


def win_loss_pie_chart(df: pd.DataFrame):
    win_count = (df["outcome"] == "W").sum()
    loss_count = (df["outcome"] == "L").sum()
    fig = px.pie(
        names=["Wins", "Losses"],
        values=[win_count, loss_count],
        color_discrete_sequence=["green", "red"],
        labels=["Wins", "Losses"]
    )
    return st.plotly_chart(fig)


def bet_size_histogram(df: pd.DataFrame):
    fig = px.histogram(df["bet_amount"], nbins=20)
    return st.plotly_chart(fig)


def profit_per_hour_heatmap(df: pd.DataFrame):
    df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
    df["profit"] = df["balance"].diff().fillna(0)
    profit_per_hour = df.groupby("hour")["profit"].sum().reset_index()

    colors = [
        "#ff0000",  # red
        "#ff4000",  # reddish-orange
        "#ff8000",  # orange
        "#ffbf00",  # orange-yellow
        "#ffff00",  # yellow
        "#bfff00",  # yellow-green
        "#80ff00",  # lime-green
        "#40ff00",  # bright green
        "#00ff00",  # green
    ]

    # Reshape to 2D for heatmap: 1 row, 24 columns (hours)
    heatmap_data = profit_per_hour.set_index("hour").T
    fig = px.imshow(
        heatmap_data,
        color_continuous_scale=["red", "orange", "yellow", "green"],
        aspect="auto",
        labels=dict(x="Hour of Day", y="", color="Profit")
    )
    # Hide y-axis label since it's just one row
    fig.update_yaxes(showticklabels=False)

    return st.plotly_chart(fig)


metrics = calculate_bet_metrics("data/betting_log.csv")

st.markdown("## **KPIs**")
items = [
    ("Total Rounds", metrics["Total Rounds"]),
    ("Wins", metrics["Wins"]),
    ("Losses", metrics["Losses"]),
    ("Final Wallet Balance", f"₹ {metrics['Final Wallet Balance']}"),
    ("Maximum Losing Streak", metrics["Maximum Losing Streak"]),
    ("Max Bet Placed", f"₹ {metrics['Max Bet Placed']}"),
    ("Total Profit", f"₹ {metrics["Total Profit"]}"),
    ("Profit Percentage", f"{metrics['Profit Percentage']:.2f}%")
]

cols_per_row = 3

for i in range(0, len(items), cols_per_row):
    cols = st.columns(cols_per_row)
    for j in range(cols_per_row):
        if i + j < len(items):
            label, value = items[i + j]
            cols[j].metric(label, value)


st.subheader("Charts")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Capital Growth Chart")
    capital_growth_chart(df)

with col2:
    st.markdown("### Win/Loss Ratio")
    win_loss_pie_chart(df)

col3, col4 = st.columns(2)

with col3:
    st.markdown("### Bet Size Distribution")
    bet_size_histogram(df)

with col4:
    st.markdown("### Profit per Hour")
    profit_per_hour_heatmap(df)

try:
    st.markdown("## Daily Report")
    daily_report = pd.read_csv("data/daily_report.csv")

    st.dataframe(daily_report)
except:
    st.write("No Daily Report Available")
    pass
