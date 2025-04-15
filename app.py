import streamlit as st
import pandas as pd
import os

# --- Page Config ---
st.set_page_config(page_title="CY24 Mammo SAPI Dashboard", layout="wide")

# --- MILV Branding ---
st.image("milv.png", width=200)

st.markdown("""
# **CY24 Seat-Adjusted Performance Index Dashboard**
_Evaluating radiologist productivity relative to seat-specific expectations._
""")

# --- Style ---
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
file_path = "CY24Mammo.xlsx"
if not os.path.exists(file_path):
    st.error("CY24Mammo.xlsx not found. Please upload it to the root of your GitHub repo.")
    st.stop()

try:
    xls = pd.ExcelFile(file_path)
except ValueError:
    st.error("CY24Mammo.xlsx is not a valid Excel file. Please re-upload a correct .xlsx file.")
    st.stop()

# Load sheets
rad_overall = pd.read_excel(xls, sheet_name="Radiologist_Overall")
seat_overall = pd.read_excel(xls, sheet_name="Seat_Overall")
seat_rad_df = pd.read_excel(xls, sheet_name="Seat_Rad_Breakdown")
sapi_df = pd.read_excel(xls, sheet_name="SAPI_Summary")

# --- Normalize Strings (strip + upper for safe merging/filtering) ---
for df in [seat_rad_df, sapi_df, seat_overall]:
    if 'RAD' in df.columns:
        df['RAD'] = df['RAD'].astype(str).str.upper().str.strip()
    if 'SEAT' in df.columns:
        df['SEAT'] = df['SEAT'].astype(str).str.upper().str.strip()

# Also normalize for filters
seat_rad_df['SEAT'] = seat_rad_df['SEAT'].str.upper().str.strip()
seat_rad_df['RAD'] = seat_rad_df['RAD'].str.upper().str.strip()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Dashboard")

all_rads = sorted(seat_rad_df['RAD'].unique())
all_seats = sorted(seat_rad_df['SEAT'].unique())

selected_rads = st.sidebar.multiselect("Radiologist(s):", all_rads, default=all_rads)
selected_seats = st.sidebar.multiselect("Seat(s):", all_seats, default=all_seats)

# --- Filtered Dataset ---
filtered = seat_rad_df[
    seat_rad_df['RAD'].isin(selected_rads) &
    seat_rad_df['SEAT'].isin(selected_seats)
].copy()

# Fill NAs
for col in ['Benchmark_75th', 'SAPI_Unweighted', 'Weighted_SAPI']:
    if col in filtered.columns:
        filtered[col] = filtered[col].fillna(0)
for col in ['SAPI_Weighted', 'SAPI_Unweighted']:
    if col in sapi_df.columns:
        sapi_df[col] = sapi_df[col].fillna(0)

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
    seat_overall[['SEAT', 'Seat_Norm_HD_Avg', 'Benchmark_75th']].sort_values('SEAT').round(2),
    use_container_width=True
)

# --- Footer ---
st.markdown("---")
st.markdown("""
**SAPI Definitions**  
📊 **Unweighted SAPI** = average % above/below benchmark across seats  
📈 **Weighted SAPI** = weighted by number of shifts per seat  

📘 _Dashboard developed for executive review by_ **Medical Imaging of Lehigh Valley, P.C.**  
Questions? Contact [@gibsona83](https://github.com/gibsona83/Mammo)
""")
