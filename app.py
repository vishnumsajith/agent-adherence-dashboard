import streamlit as st
import pandas as pd

st.set_page_config(page_title="Agent Adherence Dashboard")

st.title("Agent Adherence Dashboard")

st.write("Upload the roster file and activity report.")

roster_file = st.file_uploader(
    "Upload Roster File",
    type=["xlsx"]
)

activity_file = st.file_uploader(
    "Upload Activity Report",
    type=["xlsx"]
)

if roster_file:
    roster_df = pd.read_excel(roster_file)
    st.subheader("Roster Preview")
    st.dataframe(roster_df.head())

if activity_file:
    activity_df = pd.read_excel(activity_file)
    st.subheader("Activity Report Preview")
    st.dataframe(activity_df.head())

if roster_file and activity_file:
    st.success("Files uploaded successfully.")
