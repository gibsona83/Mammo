import streamlit as st
import pandas as pd
import os

# --- App Setup ---
st.set_page_config(page_title="CY24 Mammo SAPI Dashboard", layout="wide")

# --- Branding ---
st.image("milv.png", width=180)
st.markdown("""
### **CY24 Seat-Adjusted Performance Index Dashboard**
Evaluating radiologist productivity relative to seat-specific expectations
""")

st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #003d5c;
    }
    .stDataFrame th {
        background-color: #e6f2f7 !important;
        color: #003d5c;
    }
</style>
""", unsafe_allow_html=True)

# --- Load Cleaned Excel File ---
data_path = "CY24 Mammo Cleaned.xlsx"
if not os.path.exists(data_path):
    st.error("CY24 Mammo Cleaned.xlsx not found. Please place it in the main folder of the GitHub repository.")
    st.stop()

xls = pd.ExcelFile(data_path)
rads_df = pd.read_excel(xls, sheet_name="Radiologist_Overall")
seats_df = pd.read_excel(xls, sheet_name="Seat_Overall")
detail_df = pd.read_excel(xls, sheet_name="Seat_Rad_Breakdown")
sapi_df = pd.read_excel(xls, sheet_name="SAPI_Summary")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")
rad_options = detail_df['RAD'].unique().tolist()
seat_options = detail_df['SEAT'].unique().tolist()
selected_rads = st.sidebar.multiselect("Select Radiologist(s):", rad_options, default=rad_options)
selected_seats = st.sidebar.multiselect("Select Seat(s):", seat_options, default=seat_options)

# --- Filtered Dataset ---
filtered = detail_df[detail_df['RAD'].isin(selected_rads) & detail_df['SEAT'].isin(selected_seats)]

# --- SAPI Leaderboard ---
st.subheader("📋 SAPI Leaderboard")
st.caption("Compares each radiologist’s performance vs. 75th percentile benchmark for the seats they worked.")
st.dataframe(sapi_df.sort_values("SAPI_Weighted", ascending=False).round(2), use_container_width=True)

# --- Seat-Level Details ---
st.subheader("🪑 Seat-Level Performance")
st.caption("Normalized HD Avg vs. seat benchmark, including shift count and weighted SAPI.")
st.dataframe(filtered[['RAD', 'SEAT', 'Norm_HD_Avg', 'Benchmark_75th', 'SAPI_Unweighted', 'Shifts', 'Weighted_SAPI']].round(2), use_container_width=True)

# --- Benchmark Overview ---
st.subheader("📈 Benchmark Reference")
st.caption("125% of seat average = 75th percentile benchmark")
st.dataframe(seats_df[['SEAT', 'Seat_Norm_HD_Avg', 'Benchmark_75th']].round(2), use_container_width=True)

st.markdown("---")
st.markdown("""
💡 **Unweighted SAPI** = average across seats 
📊 **Weighted SAPI** = weighted by # of shifts per seat

🎯 Developed for executive reporting by Medical Imaging of Lehigh Valley.
For questions, contact agibson@milvrad.com
