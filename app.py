import json
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

# Load data
with open("./data/staff.json") as f:
    staff_data = json.load(f)
with open("./output/assignments.json") as f:
    assignments_data = json.load(f)

# Map ID to names
staff_map = {s["id"]: s["name"] for s in staff_data}

# Shift definitions (fixed codes)
shift_times = {
    "M": (7, 15),  # Morning
    "E": (15, 23),  # Evening
    "N": (23, 7),  # Night (to next day)
}
shift_labels = {"M": "Morning", "E": "Evening", "N": "Night"}

calendar_data = []
for assignment in assignments_data:
    sid_str = assignment["shift_id"]
    date_str = sid_str[:8]
    shift_code = sid_str[-1].upper()

    # Safety fix: handle if shift_type in file is 'night', 'evening', etc.
    if shift_code not in shift_labels:
        if "night" in assignment.get("shift_type", "").lower():
            shift_code = "N"
        elif "evening" in assignment.get("shift_type", "").lower():
            shift_code = "E"
        elif "morning" in assignment.get("shift_type", "").lower():
            shift_code = "M"

    shift_label = shift_labels.get(shift_code, "Unknown")
    s_h, e_h = shift_times.get(shift_code, (0, 8))

    base_date = datetime.strptime(date_str, "%Y%m%d")
    start_dt = base_date + timedelta(hours=s_h)
    end_dt = (
        base_date + timedelta(days=1) + timedelta(hours=e_h)
        if e_h <= s_h
        else base_date + timedelta(hours=e_h)
    )

    for staff_id in assignment["staff_ids"]:
        calendar_data.append(
            {
                "Staff": staff_map.get(staff_id, staff_id),
                "Start": start_dt,
                "End": end_dt,
                "Shift Type": shift_label,
            }
        )

calendar_df = pd.DataFrame(calendar_data)

# Table data for assignments
tables = []
for ass in assignments_data:
    names = [staff_map.get(x, x) for x in ass["staff_ids"]]
    tables.append({"Shift ID": ass["shift_id"], "Staff Assigned": ", ".join(names)})
table_df = pd.DataFrame(tables)

# Create Gantt chart figure
gantt_fig = px.timeline(
    calendar_df,
    x_start="Start",
    x_end="End",
    y="Staff",
    color="Shift Type",
    text="Shift Type",
    hover_data=["Start", "End"],
)

# Style updates for bigger blocks & readability
gantt_fig.update_traces(
    marker_line_width=1,
    marker_line_color="black",
    textposition="inside",
    insidetextanchor="start",
    textfont={"size": 14, "color": "white"},
    selector={"type": "bar"},
)

gantt_fig.update_yaxes(
    autorange="reversed", title="Staff Member", tickfont={"size": 14}
)

# Default zoom range: 3 weeks from earliest start
start_view = calendar_df["Start"].min()
end_view = start_view + pd.Timedelta(days=21)

gantt_fig.update_layout(
    height=600,
    width=4000,  # wide for horizontal scroll
    margin={"l": 200, "r": 30, "t": 50, "b": 50},
    bargap=0.5,
    barmode="stack",
    legend_title="Shift Type",
    plot_bgcolor="white",
    xaxis={
        "title": "Date & Time",
        "side": "top",
        "tickformat": "%b %d %H:%M",
        "tickangle": 0,
        "tickmode": "linear",
        "dtick": 3600000 * 4,  # 4 hours
        "ticklabelmode": "period",
        "type": "date",
        "range": [start_view, end_view],
        "fixedrange": False,
        "showgrid": True,
    },
)

# Streamlit UI
st.title("Shift Schedule")

st.markdown(
    """
    <style>
    /* Container with horizontal scroll */
    .scroll-container {
        overflow-x: auto;
        overflow-y: hidden;
        max-height: 650px;
        border: 1px solid #ddd;
        padding: 10px;
        white-space: nowrap;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Chart inside scrollable container
st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
st.plotly_chart(gantt_fig, use_container_width=False)
st.markdown("</div>", unsafe_allow_html=True)
