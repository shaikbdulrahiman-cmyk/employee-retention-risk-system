
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(
    page_title="Employee Retention Risk System",
    page_icon="📊",
    layout="wide"
)

st.title("Employee Retention Risk Analysis")
st.caption("Employee support prioritization and workforce insights")

DATA_PATH = Path("data/processed/employee_risk_analysis.csv")

if not DATA_PATH.exists():
    st.error("Risk analysis file not found. Run the risk analysis generator first.")
    st.stop()

df = pd.read_csv(DATA_PATH)

# Sidebar filters
st.sidebar.header("Filters")

risk_options = st.sidebar.multiselect(
    "Risk Category",
    ["Low", "Medium", "High"],
    default=["Low", "Medium", "High"]
)

filtered = df[df["risk_category"].isin(risk_options)].copy()

# Metrics
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Employees", f"{len(df):,}")
col2.metric("Employees Displayed", f"{len(filtered):,}")
col3.metric("High Risk", int((df["risk_category"] == "High").sum()))
col4.metric("Medium Risk", int((df["risk_category"] == "Medium").sum()))

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Risk Distribution")
    counts = filtered["risk_category"].value_counts().reindex(
        ["Low", "Medium", "High"], fill_value=0
    )
    st.bar_chart(counts)

with right:
    st.subheader("Engagement Overview")
    engagement = filtered[
        filtered["engagement_score"] >= 1
    ]["engagement_score"]

    if not engagement.empty:
        st.bar_chart(engagement.value_counts().sort_index())
    else:
        st.info("No completed survey scores available.")

st.divider()

st.subheader("Employee Risk Review")

search = st.text_input("Search Employee ID")

if search:
    filtered = filtered[
        filtered["employee_id"].str.contains(
            search, case=False, na=False
        )
    ]

display_columns = [
    "employee_id",
    "role_id",
    "team_id",
    "engagement_score",
    "average_working_hours",
    "risk_score",
    "risk_category",
    "risk_reason",
    "review_recommendation"
]

st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True
)

st.subheader("Employees Prioritized for Human Review")

high_risk = df[df["risk_category"] == "High"]

st.dataframe(
    high_risk[display_columns],
    use_container_width=True,
    hide_index=True
)

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Employee Risk Report",
    data=csv,
    file_name="employee_risk_report.csv",
    mime="text/csv"
)

st.info(
    "This dashboard provides supportive signals for human review. "
    "It must not be used for automated employment decisions."
)
