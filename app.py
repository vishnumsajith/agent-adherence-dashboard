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

    # ------------------------
    # LOAD FILES
    # ------------------------

    roster = pd.read_excel(roster_file)
    activity = pd.read_excel(activity_file)

    roster.columns = roster.columns.str.strip()
    activity.columns = activity.columns.str.strip()

    # ------------------------
    # TROUBLESHOOTING
    # ------------------------

    st.subheader("Roster Columns")
    st.write(roster.columns.tolist())

    st.subheader("Activity Columns")
    st.write(activity.columns.tolist())

    # ------------------------
    # PREPARE ACTIVITY DATA
    # ------------------------

    activity["Activity Time"] = pd.to_datetime(
        activity["Activity Time"],
        errors="coerce"
    )

    activity["Date"] = activity["Activity Time"].dt.date

    # ------------------------
    # LOGIN EVENTS
    # ------------------------

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

    # ------------------------
    # SHIFT START
    # ------------------------

    roster["Shift Start"] = (
        roster["PST Shift Time"]
        .astype(str)
        .str.split("-")
        .str[0]
        .str.strip()
    )

    # ------------------------
    # MERGE ROSTER
    # ------------------------

    first_login = first_login.merge(
        roster[
            [
                "Name",
                "Shift Time",
                "Shift Start"
            ]
        ],
        left_on="Agent Name",
        right_on="Name",
        how="left"
    )

    # ------------------------
    # UNMATCHED AGENTS
    # ------------------------

    unmatched_agents = (
        first_login[
            first_login["Name"].isna()
        ]["Agent Name"]
        .drop_duplicates()
        .tolist()
    )

    # Keep only roster agents
    first_login = first_login[
        first_login["Name"].notna()
    ].copy()

    # ------------------------
    # LATE LOGIN
    # ------------------------

    def get_late_minutes(row):

        try:

            login_time = row["Activity Time"]

            shift_start = pd.to_datetime(
                row["Shift Start"],
                format="%I:%M%p",
                errors="coerce"
            )

            if pd.isna(shift_start):
                return 0

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
            return 0

    first_login["Late Minutes"] = (
        first_login.apply(
            get_late_minutes,
            axis=1
        )
    )

    # ------------------------
    # SHIFT FILTER
    # ------------------------

    shift_list = sorted(
        first_login["Shift Time"]
        .dropna()
        .unique()
    )

    selected_shift = st.selectbox(
        "Select Shift",
        ["All"] + list(shift_list)
    )

    if selected_shift != "All":

        first_login = first_login[
            first_login["Shift Time"] == selected_shift
        ]

    # ------------------------
    # METRICS
    # ------------------------

    late_count = (
        first_login["Late Minutes"] > 0
    ).sum()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Late Logins",
            int(late_count)
        )

    with col2:
        st.metric(
            "Agents",
            roster["Name"].nunique()
        )

    # ------------------------
    # UNMATCHED AGENTS DISPLAY
    # ------------------------

    st.subheader("Unmatched Agents")

    if len(unmatched_agents) > 0:

        st.warning(
            f"{len(unmatched_agents)} unmatched agents found."
        )

        st.write(unmatched_agents)

    else:

        st.success(
            "All agents matched with roster."
        )

    # ------------------------
    # LOGIN ADHERENCE TABLE
    # ------------------------

    st.subheader("Login Adherence")

    st.dataframe(
        first_login[
            [
                "Agent Name",
                "Shift Time",
                "Date",
                "Shift Start",
                "Activity Time",
                "Late Minutes"
            ]
        ],
        use_container_width=True
    )
