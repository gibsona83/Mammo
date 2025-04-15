import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Streamlit page config
st.set_page_config(page_title="CY24 Mammography Dashboard", layout="wide")

# Title
st.title("CY24 Mammography Performance Dashboard")

# Load data
@st.cache_data
def load_data():
    # Assuming the Excel file is in the repo root
    file_path = "CY24 Mammo.xlsx"
    xl = pd.ExcelFile(file_path)
    
    # Load relevant sheets
    by_rad = xl.parse("CY 2024 OVERALL - BY RAD")
    case_mix = xl.parse("CY24 OVERALL CASE MIX")
    by_seat = xl.parse("CY 2024 OVERALL - BY SEAT")
    
    return by_rad, case_mix, by_seat

by_rad, case_mix, by_seat = load_data()

# Sidebar filters
st.sidebar.header("Filters")
selected_rad = st.sidebar.multiselect("Select Radiologist(s)", options=by_rad["RAD"].unique(), default=by_rad["RAD"].unique())
selected_seat = st.sidebar.multiselect("Select Location(s)", options=by_seat["SEAT"].unique(), default=by_seat["SEAT"].unique())

# Filter data
filtered_rad = by_rad[by_rad["RAD"].isin(selected_rad)]
filtered_seat = by_seat[by_seat["SEAT"].isin(selected_seat)]

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["Radiologist Performance", "Location Analysis", "Case Mix"])

with tab1:
    st.header("Radiologist Performance")
    
    # Bar chart for Normalized HD Avg
    fig1 = px.bar(
        filtered_rad,
        x="RAD",
        y="Normalized HD Avg",
        title="Normalized HD Average by Radiologist",
        color="RAD",
        labels={"Normalized HD Avg": "Normalized HD Avg (wRVU)"},
    )
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Display raw data
    st.subheader("Raw Data")
    st.dataframe(filtered_rad[["RAD", "FULL", "AVG FULL", "HALF", "AVG HALF", "Normalized HD Avg"]])

with tab2:
    st.header("Location Analysis")
    
    # Bar chart for Normalized HD Avg by seat
    fig2 = px.bar(
        filtered_seat,
        x="SEAT",
        y="Normalized HD Avg",
        title="Normalized HD Average by Location",
        color="SEAT",
        labels={"Normalized HD Avg": "Normalized HD Avg (wRVU)"},
    )
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)
    
    # Display raw data
    st.subheader("Raw Data")
    st.dataframe(filtered_seat[["SEAT", "FULL", "AVG FULL", "HALF", "AVG HALF", "Normalized HD Avg"]])

with tab3:
    st.header("Case Mix Analysis")
    
    # Filter case mix for selected radiologists
    filtered_case_mix = case_mix[case_mix["RAD"].isin(selected_rad)]
    
    # Pie chart for Procedure vs Read
    fig3 = go.Figure()
    for rad in filtered_case_mix["RAD"]:
        subset = filtered_case_mix[filtered_case_mix["RAD"] == rad]
        fig3.add_trace(
            go.Pie(
                labels=["Procedure", "Read"],
                values=[subset["Procedure"].iloc[0], subset["Read"].iloc[0]],
                name=rad,
                visible=True if rad == filtered_case_mix["RAD"].iloc[0] else False,
            )
        )
    
    # Add dropdown for radiologist selection
    fig3.update_layout(
        updatemenus=[
            dict(
                buttons=[
                    dict(
                        label=rad,
                        method="update",
                        args=[{"visible": [r == rad for r in filtered_case_mix["RAD"]]}],
                    )
                    for rad in filtered_case_mix["RAD"]
                ],
                direction="down",
                showactive=True,
            )
        ],
        title="Procedure vs. Read Case Mix by Radiologist",
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # Display raw data
    st.subheader("Raw Data")
    st.dataframe(filtered_case_mix)

# Instructions for deployment
st.sidebar.markdown("""
### Deployment Instructions
1. Push this file (`app.py`) and `CY24 Mammo.xlsx` to your GitHub repo: `gibsona83/Mammo`.
2. Create a `requirements.txt` with:
```
streamlit
pandas
plotly
openpyxl
```
3. Deploy to Streamlit Community Cloud:
   - Connect your GitHub repo.
   - Select `app.py` as the main file.
   - Ensure the Excel file is in the repo root.
""")