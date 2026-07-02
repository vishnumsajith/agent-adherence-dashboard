import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Agent Adherence Dashboard",
    layout="wide"
)

st.title("Agent Adherence Dashboard")

st.write(
    "Upload Roster and Activity Report"
)

roster_file = st.file_uploader(
    "Upload Roster File",
    type=["xlsx"]
)

activity_file = st.file_uploader(
    "Upload Activity Report",
    type=["xlsx"]
)

if roster_file and activity_file:

    roster = pd.read_excel(roster_file)

    activity = pd.read_excel(activity_file)

    st.success("Files Uploaded Successfully")

    st.subheader("Roster Preview")

    st.dataframe(roster.head())

    st.subheader("Activity Preview")

    st.dataframe(activity.head())

    st.metric(
        "Total Agents",
        roster["Name"].nunique()
    )

    st.metric(
        "Total Records",
        len(activity)
    )
