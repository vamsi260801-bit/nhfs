import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="NFHS Dashboard", layout="wide")

st.title("📊 National Family Health Survey (NFHS) Dashboard")

# -------------------------------
# LOAD DATA
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("All India National Family Health Survey5.xlsx")
    return df

df = load_data()

# -------------------------------
# SIDEBAR FILTERS
# -------------------------------
st.sidebar.header("Filters")

states = sorted(df["India/States/UTs"].dropna().unique())
surveys = sorted(df["Survey"].dropna().unique())
areas = sorted(df["Area"].dropna().unique())

selected_state = st.sidebar.selectbox("Select State / India", states)
selected_survey = st.sidebar.multiselect("Select Survey", surveys, default=surveys)
selected_area = st.sidebar.selectbox("Select Area", areas)

# Filter data
filtered_df = df[
    (df["India/States/UTs"] == selected_state) &
    (df["Survey"].isin(selected_survey)) &
    (df["Area"] == selected_area)
]

# -------------------------------
# INDICATOR SELECTION
# -------------------------------
indicator_columns = df.columns[3:]  # Skip first 3 identifier columns

selected_indicator = st.selectbox("Select Indicator", indicator_columns)

# -------------------------------
# KPI DISPLAY
# -------------------------------
st.subheader("Key Value")

latest_data = filtered_df.sort_values("Survey").tail(1)

if not latest_data.empty:
    latest_value = latest_data[selected_indicator].values[0]
    latest_survey = latest_data["Survey"].values[0]
    st.metric(label=f"{selected_indicator} ({latest_survey})",
              value=round(latest_value, 2))
else:
    st.warning("No data available for selected filters.")

# -------------------------------
# TREND CHART
# -------------------------------
st.subheader("Trend Over Survey Years")

if not filtered_df.empty:
    fig = px.line(
        filtered_df,
        x="Survey",
        y=selected_indicator,
        markers=True,
        title=f"{selected_indicator} Trend"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data to display.")

# -------------------------------
# STATE COMPARISON (ALL STATES)
# -------------------------------
st.subheader("State Comparison")

comparison_survey = st.selectbox(
    "Select Survey for Comparison",
    surveys,
    key="comparison_survey"
)

comparison_df = df[
    (df["Survey"] == comparison_survey) &
    (df["Area"] == selected_area)
]

comparison_df = comparison_df[[
    "India/States/UTs",
    selected_indicator
]].dropna()

fig2 = px.bar(
    comparison_df.sort_values(selected_indicator, ascending=False),
    x="India/States/UTs",
    y=selected_indicator,
    title=f"{selected_indicator} - {comparison_survey}",
)

fig2.update_layout(xaxis_tickangle=90)

st.plotly_chart(fig2, use_container_width=True)

# -------------------------------
# RAW DATA TABLE
# -------------------------------
with st.expander("View Raw Data"):
    st.dataframe(filtered_df)
