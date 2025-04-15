import streamlit as st
import pandas as pd
import os

# --- App Title & Description ---
st.set_page_config(page_title="CY24 Mammo SAPI Dashboard", layout="wide")
st.title("📊 CY24 Seat-Adjusted Performance Index Dashboard")

st.markdown("""
This dashboard evaluates radiologist performance using the **Seat-Adjusted Performance Index (SAPI)**:

- **Unweighted SAPI**: Average % above/below benchmark per seat (equal weight)
- **Weighted SAPI**: Average weighted by number of shifts per seat (total contribution)

Benchmarks are based on 125% of seat averages to reflect the 75th percentile.
""")

# --- Load Data from File ---
data_path = os.path.join("data", "CY24 Mammo.xlsx")
if not os.path.exists(data_path):
    st.error("CY24 Mammo.xlsx not found. Please place it in the 'data' folder of the GitHub repository.")
    st.stop()

xls = pd.ExcelFile(data_path)
hd_df = pd.read_excel(xls, sheet_name='HD Conversions')
data_df = pd.read_excel(xls, sheet_name='Data')

# --- Extract Benchmark Table ---
seat_section = hd_df.iloc[1:7, [4, 5]]
seat_section.columns = ['SEAT', 'Seat_Norm_HD_Avg']
seat_section = seat_section.dropna().copy()
seat_section['Benchmark'] = seat_section['Seat_Norm_HD_Avg'] * 1.25

# --- Extract Radiologist Normalized HD Averages ---
rad_section = hd_df.iloc[1:12, [0, 1]]
rad_section.columns = ['RAD', 'Norm_HD_Avg']
rad_section = rad_section.dropna().copy()

# --- Extract Per-Seat Radiologist Performance ---
seat_rads = []
seat_names = seat_section['SEAT'].tolist()
for seat in seat_names:
    seat_data = hd_df[hd_df.iloc[:, 0] == seat].iloc[:, :2]
    if not seat_data.empty:
        for i in range(1, 10):
            rad = hd_df.iloc[hd_df[hd_df.columns[0]] == seat].index[0] + i
            val = hd_df.iloc[rad, 0:2].tolist()
            if pd.notna(val[0]) and pd.notna(val[1]):
                seat_rads.append([val[0], seat, val[1]])
            else:
                break
seat_rad_df = pd.DataFrame(seat_rads, columns=['RAD', 'SEAT', 'Norm_HD_Avg'])

# --- Merge with Benchmarks ---
seat_rad_df = seat_rad_df.merge(seat_section, on='SEAT', how='left')
seat_rad_df['SAPI_Unweighted'] = seat_rad_df['Norm_HD_Avg'] / seat_rad_df['Benchmark'] * 100

# --- Shift Counts for Weighted SAPI ---
shifts = data_df.groupby(['Finalizing Provider', 'Location']).size().reset_index(name='Shifts')
shifts.columns = ['RAD', 'SEAT', 'Shifts']
seat_rad_df = seat_rad_df.merge(shifts, on=['RAD', 'SEAT'], how='left')
seat_rad_df['Shifts'] = seat_rad_df['Shifts'].fillna(1)

# --- Weighted SAPI Calculation ---
weighted = seat_rad_df.copy()
weighted['Weighted_SAPI'] = weighted['SAPI_Unweighted'] * weighted['Shifts']
weighted_summary = weighted.groupby('RAD').agg({
    'Weighted_SAPI': 'sum',
    'Shifts': 'sum'
}).reset_index()
weighted_summary['SAPI_Weighted'] = weighted_summary['Weighted_SAPI'] / weighted_summary['Shifts']

# --- Combine Unweighted SAPI ---
unweighted_summary = seat_rad_df.groupby('RAD')['SAPI_Unweighted'].mean().reset_index()
combined = weighted_summary.merge(unweighted_summary, on='RAD')

# --- Display Dashboard ---
st.subheader("📋 SAPI Leaderboard")
st.dataframe(combined.sort_values('SAPI_Weighted', ascending=False).round(2), use_container_width=True)

st.subheader("🪑 Seat-Level Breakdown")
st.dataframe(seat_rad_df[['RAD', 'SEAT', 'Norm_HD_Avg', 'Benchmark', 'SAPI_Unweighted', 'Shifts']].round(2), use_container_width=True)

st.subheader("📈 Benchmark Reference Table")
st.dataframe(seat_section.round(2), use_container_width=True)

st.markdown("---")
st.markdown("Developed for executive reporting. For questions, contact [@gibsona83](https://github.com/gibsona83/Mammo)")
