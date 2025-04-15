import streamlit as st
import pandas as pd
import os

# --- Page Config ---
st.set_page_config(page_title="CY24 Mammo SAPI Dashboard", layout="wide")

# --- Branding: MILV Logo ---
st.image("milv.png", width=200)

# --- Header ---
st.markdown("""
# **CY24 Seat-Adjusted Performance Index Dashboard**
_Evaluating radiologist productivity relative to seat-specific expectations._
""")

# --- Custom Style ---
st.markdown("""
<style>
    h1, h2, h3 {
        color: #003d5c;
    }
    .stDataFrame th {
        background-color: #e6f2f7 !important;
        color: #003d5c;
    }
</style>
""", unsafe_allow_html=True)

# --- Load Excel File ---
file_path = "CY24 Mammo Cleaned.xlsx"
if not os.path.exists(file_path):
    st.error("CY24 Mammo Cleaned.xlsx not found. Please upload to the main GitHub folder.")
    st.stop()

xls = pd.ExcelFile(file_path)
rads_df = pd.read_excel(xls, sheet_name="Radiologist_Overall")
seats_df = pd.read_excel(xls, sheet_name="Seat_Overall")
detail_df = pd.read_excel(xls, sheet_name="Seat_Rad_Breakdown")
sapi_df = pd.read_excel(xls, sheet_name="SAPI_Summary")

# --- Normalize Strings for Clean Merging ---
for df in [detail_df, sapi_df, seats_df]:
    df['RAD'] = df['RAD'].astype(str).str.strip().str.upper()
    if 'SEAT' in df.columns:
        df['SEAT'] = df['SEAT'].astype(str).str.strip().str.upper()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Dashboard")

rad_options = sorted(detail_df['RAD'].unique())
seat_options = sorted(detail_df['SEAT'].unique())

selected_rads = st.sidebar.multiselect("Select Radiologist(s):", rad_options, default=rad_options)
selected_seats = st.sidebar.multiselect("Select Seat(s):", seat_options, default=seat_options)

# --- Filter Data ---
filtered = detail_df[
    detail_df['RAD'].isin(selected_rads) &
    detail_df['SEAT'].isin(selected_seats)
].copy()

# --- Fill NAs to prevent blank display ---
filtered['Benchmark_75th'] = filtered['Benchmark_75th'].fillna(0)
filtered['SAPI_Unweighted'] = filtered['SAPI_Unweighted'].fillna(0)
filtered['Weighted_SAPI'] = filtered['Weighted_SAPI'].fillna(0)
sapi_df['SAPI_Weighted'] = sapi_df['SAPI_Weighted'].fillna(0)
sapi_df['SAPI_Unweighted'] = sapi_df['SAPI_Unweighted'].fillna(0)

# --- 📋 SAPI Leaderboard ---
st.subheader("📋 SAPI Leaderboard")
st.caption("Comparison of radiologist performance vs. 75th percentile seat benchmarks.")
leaderboard = sapi_df[sapi_df['RAD'].isin(selected_rads)].sort_values('SAPI_Weighted', ascending=False).round(2)
st.dataframe(leaderboard, use_container_width=True)

# --- 🪑 Seat-Level Detail ---
st.subheader("🪑 Seat-Level Performance")
st.caption("Per-seat normalized averages, benchmarks, and calculated SAPI values.")
st.dataframe(
    filtered[['RAD', 'SEAT', 'Norm_HD_Avg', 'Benchmark_75th', 'SAPI_Unweighted', 'Shifts', 'Weighted_SAPI']].round(2),
    use_container_width=True
)

# --- 📈 Benchmark Table ---
st.subheader("📈 Seat Benchmark Reference")
st.caption("Benchmarks set at 125% of seat averages (75th percentile proxy).")
st.dataframe(
    seats_df[['SEAT', 'Seat_Norm_HD_Avg', 'Benchmark_75th']].round(2).sort_values(by='SEAT'),
    use_container_width=True
)

# --- Footer ---
st.markdown("---")
st.markdown("""
**SAPI Definitions**  
📊 **Unweighted SAPI** = average % above/below benchmark across seats  
📈 **Weighted SAPI** = weighted by number of shifts at each seat  

📘 _Dashboard developed for executive review by_ **Medical Imaging of Lehigh Valley, P.C.**  
Questions? Contact [@gibsona83](https://github.com/gibsona83/Mammo)
""")
