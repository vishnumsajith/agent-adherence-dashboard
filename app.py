import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Agent Adherence Dashboard",
    layout="wide"
)

st.title("Agent Adherence Dashboard")

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

    activity["Activity Time"] = pd.to_datetime(
        activity["Activity Time"],
        errors="coerce"
    )

    activity["Date"] = activity["Activity Time"].dt.date

    login_data = activity[
        activity["Activity Detail"].isin(
            ["SIGN-IN", "AVAILABLE"]
        )
    ]

    first_login = (
        login_data
        .sort_values("Activity Time")
        .groupby(
            ["Agent Name", "Date"]
        )["Activity Time"]
        .first()
        .reset_index()
    )

    st.success("Adherence Data Generated")

    st.subheader("First Login Details")

    st.dataframe(
        first_login,
        use_container_width=True
    )

    st.metric(
        "Agents",
        roster["Name"].nunique()
    )

    st.metric(
        "Login Records",
        len(first_login)
    )
