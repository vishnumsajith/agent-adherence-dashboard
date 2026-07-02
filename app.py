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

    login_events = activity[
        activity["Activity Detail"].isin(
            ["SIGN-IN", "AVAILABLE"]
        )
    ]

    first_login = (
        login_events
        .sort_values("Activity Time")
        .groupby(
            ["Agent Name", "Date"]
        )["Activity Time"]
        .first()
        .reset_index()
    )

    roster["Shift Start"] = (
        roster["PST Shift Time"]
        .astype(str)
        .str.split("-")
        .str[0]
    )

    first_login = first_login.merge(
    roster[
        ["Name", "Shift Name", "Shift Start"]
    ],
    left_on="Agent Name",
    right_on="Name",
    how="left"
    )

    def get_late_minutes(row):
        try:
            login_time = row["Activity Time"]

            shift_start = pd.to_datetime(
                row["Shift Start"],
                format="%I:%M%p",
                errors="coerce"
            )

            if pd.isna(shift_start):
                return None

            shift_datetime = pd.Timestamp.combine(
                login_time.date(),
                shift_start.time()
            )

            diff = (
                login_time -
                shift_datetime
            ).total_seconds() / 60

            return max(0, round(diff))

        except:
            return None

    first_login["Late Minutes"] = (
        first_login.apply(
            get_late_minutes,
            axis=1
        )
    )

    st.success(
        "Late Login Report Generated"
    )

    st.subheader(
        "Late Login Dashboard"
    )
 shift_list = sorted(
    first_login["Shift Name"]
    .dropna()
    .unique()
)

selected_shift = st.selectbox(
    "Select Shift",
    ["All"] + list(shift_list)
)

if selected_shift != "All":
    first_login = first_login[
        first_login["Shift Name"] == selected_shift
    ]

first_login["Late Minutes"] = (
    first_login.apply(
        get_late_minutes,
        axis=1
    )
)

st.success(
    "Late Login Report Generated"
)

st.subheader(
    "Late Login Dashboard"
)

st.dataframe(
    first_login[
        [
            "Agent Name",
            "Shift Name",
            "Date",
            "Shift Start",
            "Activity Time",
            "Late Minutes"
        ]
    ],
    use_container_width=True
)

late_count = (
    first_login["Late Minutes"] > 0
).sum()

st.metric(
    "Late Logins",
    late_count
)

st.metric(
    "Agents",
    roster["Name"].nunique()
)
