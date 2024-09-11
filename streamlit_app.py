import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Set page config and style
st.set_page_config(page_title="Ticketing Tool", page_icon="🎫", layout="wide")
st.markdown("""
    <style>
    .stApp {
        background-color: black;
        color: red;
    }
    .stButton>button {
        color: red;
        background-color: #333333;
        border: 1px solid red;
    }
    .stSelectbox>div>div {
        background-color: #333333;
        color: red;
    }
    .stTextInput>div>div>input {
        background-color: #333333;
        color: red;
    }
    </style>
    """, unsafe_allow_html=True)

# Show app title and description
st.title("🎫Ticket Analyzer")
st.write(
    """
    This app demonstrates the ticketing workflow for executive offices.\n 
    Create tickets, edit existing ones, and view key statistics with ease.
    """
)

# Define tracks
TRACKS = ["TIBCO", "KAFKA", "MQ", "SOLACE", "ABINITIO", "DATASTAGE"]
TRACK_COLORS = {
    "TIBCO": "#FF4136",
    "KAFKA": "#FF851B",
    "MQ": "#FFDC00",
    "SOLACE": "#2ECC40",
    "ABINITIO": "#0074D9",
    "DATASTAGE": "#B10DC9"
}

# Create a random Pandas dataframe with existing tickets
if "df" not in st.session_state:
    np.random.seed(42)
    issue_descriptions = [
        "Network connectivity issues in the office",
        "Software application crashing on startup",
        "Printer not responding to print commands",
        "Email server downtime",
        "Data backup failure",
        "Login authentication problems",
        "Website performance degradation",
        "Security vulnerability identified",
        "Hardware malfunction in the server room",
        "Employee unable to access shared files",
        "Database connection failure",
        "Mobile application not syncing data",
        "VoIP phone system issues",
        "VPN connection problems for remote employees",
        "System updates causing compatibility issues",
        "File server running out of storage space",
        "Intrusion detection system alerts",
        "Inventory management system errors",
        "Customer data not loading in CRM",
        "Collaboration tool not sending notifications",
    ]

    data = {
        "ID": [f"INC-{i}" for i in range(1100, 1000, -1)],
        "Issue": np.random.choice(issue_descriptions, size=100),
        "Status": np.random.choice(["Open", "In Progress", "Closed"], size=100),
        "Priority": np.random.choice(["High", "Medium", "Low"], size=100),
        "Date Submitted": [
            datetime.date(2024, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
            for _ in range(100)
        ],
        "Track": np.random.choice(TRACKS, size=100),
    }
    df = pd.DataFrame(data)
    st.session_state.df = df

# Show a section to add a new ticket
st.header("Add a New Ticket")

with st.form("add_ticket_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        issue = st.text_area("Describe the issue")
    with col2:
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    with col3:
        track = st.selectbox("Track", TRACKS)
    submitted = st.form_submit_button("SUBMIT")

if submitted:
    recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    df_new = pd.DataFrame(
        [
            {
                "ID": f"TICKET-{recent_ticket_number+1}",
                "Issue": issue,
                "Status": "Open",
                "Priority": priority,
                "Date Submitted": today,
                "Track": track,
            }
        ]
    )

    st.success("Ticket submitted! Below are the ticket details:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

# Show section to view and edit existing tickets in a table
st.header("Existing tickets")
st.write(f"Number of tickets: `{len(st.session_state.df)}`")

st.info(
    "You can edit the tickets by double clicking on a cell. Note how the plots below "
    "update automatically! \n You can also sort the table by clicking on the column headers.",
    icon="✍️",
)

# Show the tickets dataframe with `st.data_editor`
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Status",
            help="Ticket status",
            options=["Open", "In Progress", "Closed"],
            required=True,
        ),
        "Priority": st.column_config.SelectboxColumn(
            "Priority",
            help="Priority",
            options=["High", "Medium", "Low"],
            required=True,
        ),
        "Track": st.column_config.SelectboxColumn(
            "Track",
            help="Software stack",
            options=TRACKS,
            required=True,
        ),
    },
    disabled=["ID", "Date Submitted"],
    column_order=["ID", "Issue", "Status", "Priority", "Date Submitted", "Track"],
)

# Show statistics with filter
st.header("Statistics")

# Filter by Track
selected_tracks = st.multiselect("Filter by Track", TRACKS, default=TRACKS)
filtered_df = edited_df[edited_df['Track'].isin(selected_tracks)]

# Show metrics
col1, col2, col3 = st.columns(3)
num_open_tickets = len(filtered_df[filtered_df.Status == "Open"])
col1.metric(label="Number of open tickets", value=num_open_tickets)
col2.metric(label="First response time (hours)", value=5.2)
col3.metric(label="Average resolution time (hours)", value=16)

# Show Altair charts
st.write("##### Ticket status per month")
status_plot = (
    alt.Chart(filtered_df)
    .mark_bar()
    .encode(
        x="month(Date Submitted):O",
        y="count():Q",
        xOffset="Status:N",
        color=alt.Color("Status:N", scale=alt.Scale(scheme='redyellowgreen')),
    )
    .properties(height=300)
    .configure_axis(labelColor='red', titleColor='red')
    .configure_legend(orient="bottom", titleColor='red', labelColor='red')
)
st.altair_chart(status_plot, use_container_width=True)

st.write("##### Current ticket priorities")
priority_plot = (
    alt.Chart(filtered_df)
    .mark_arc()
    .encode(
        theta="count():Q",
        color=alt.Color("Priority:N", scale=alt.Scale(scheme='redyellowgreen')),
    )
    .properties(height=300)
    .configure_axis(labelColor='red', titleColor='red')
    .configure_legend(orient="bottom", titleColor='red', labelColor='red')
)
st.altair_chart(priority_plot, use_container_width=True)

st.write("##### Tickets by Track")
track_plot = (
    alt.Chart(filtered_df)
    .mark_bar()
    .encode(
        x="count():Q",
        y="Track:N",
        color=alt.Color("Track:N", scale=alt.Scale(domain=TRACKS, range=list(TRACK_COLORS.values()))),
    )
    .properties(height=300)
    .configure_axis(labelColor='red', titleColor='red')
    .configure_legend(orient="bottom", titleColor='red', labelColor='red')
)
st.altair_chart(track_plot, use_container_width=True)

# Highlight all tracks when showing complete data
if set(selected_tracks) == set(TRACKS):
    st.write("##### All Tracks:")
    st.write(", ".join(TRACKS))
