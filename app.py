import streamlit as st
import pandas as pd
import os
from pathlib import Path

# Inject custom CSS for color scheme alignment
st.markdown("""
<style>
    body {
        background-color: #1C2526;
        color: #FFFFFF;
    }
    .stApp {
        background-color: #1C2526;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF;
        font-family: 'Arial', sans-serif;
    }
    .stMarkdown p {
        color: #D3D3D3;
    }
    .stDataFrame div {
        background-color: #2B4A5D;
        color: #FFFFFF;
        border: 1px solid #FFFFFF;
    }
    .stDataFrame div:hover {
        background-color: #3A5F73;
    }
    /* Style for the divider */
    hr {
        border-top: 1px solid #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

# Cache data loading to prevent repeated file reads
@st.cache_data
def load_data(file_path):
    try:
        xls = pd.ExcelFile(file_path)
        return pd.read_excel(xls, sheet_name='HD Conversions'), pd.read_excel(xls, sheet_name='Data')
    except FileNotFoundError:
        st.error("CY24 Mammo.xlsx not found in the main repository folder.")
        st.stop()

# Cache data processing to avoid redundant computations
@st.cache_data
def process_data(hd_df, data_df):
    # Extract Benchmark Table
    seat_section = hd_df.iloc[1:7, [4, 5]].dropna().copy()
    seat_section.columns = ['SEAT', 'Seat_Norm_HD_Avg']
    seat_section['Benchmark'] = seat_section['Seat_Norm_HD_Avg'] * 1.25

    # Extract Radiologist Normalized HD Averages
    rad_section = hd_df.iloc[1:12, [0, 1]].dropna().copy()
    rad_section.columns = ['RAD', 'Norm_HD_Avg']

    # Extract Per-Seat Radiologist Performance (optimized loop)
    seat_rads = []
    seat_names = seat_section['SEAT'].to_numpy()  # Use numpy for faster iteration
    for seat in seat_names:
        seat_idx = hd_df[hd_df.iloc[:, 0] == seat].index
        if not seat_idx.empty:
            start_idx = seat_idx[0]
            for i in range(1, 10):
                row = hd_df.iloc[start_idx + i, 0:2]
                if row.notna().all():
                    seat_rads.append([row[0], seat, row[1]])
                else:
                    break
    seat_rad_df = pd.DataFrame(seat_rads, columns=['RAD', 'SEAT', 'Norm_HD_Avg'])

    # Merge with Benchmarks
    seat_rad_df = seat_rad_df.merge(seat_section, on='SEAT', how='left')
    seat_rad_df['SAPI_Unweighted'] = seat_rad_df['Norm_HD_Avg'] / seat_rad_df['Benchmark'] * 100

    # Shift Counts for Weighted SAPI
    shifts = data_df.groupby(['Finalizing Provider', 'Location']).size().reset_index(name='Shifts')
    shifts.columns = ['RAD', 'SEAT', 'Shifts']
    seat_rad_df = seat_rad_df.merge(shifts, on=['RAD', 'SEAT'], how='left').fillna({'Shifts': 1})

    # Weighted SAPI Calculation
    weighted = seat_rad_df.copy()
    weighted['Weighted_SAPI'] = weighted['SAPI_Unweighted'] * weighted['Shifts']
    weighted_summary = weighted.groupby('RAD').agg({
        'Weighted_SAPI': 'sum',
        'Shifts': 'sum'
    }).reset_index()
    weighted_summary['SAPI_Weighted'] = weighted_summary['Weighted_SAPI'] / weighted_summary['Shifts']

    # Combine Unweighted SAPI
    unweighted_summary = seat_rad_df.groupby('RAD')['SAPI_Unweighted'].mean().reset_index()
    combined = weighted_summary.merge(unweighted_summary, on='RAD')

    return seat_section, seat_rad_df, combined

# --- App Setup ---
st.set_page_config(page_title="CY24 Mammo SAPI Dashboard", layout="wide")

# Display the logo
st.image("milv.png", use_column_width=False, width=500)

st.title("📊 CY24 Seat-Adjusted Performance Index Dashboard")

st.markdown("""
This dashboard evaluates radiologist performance using the **Seat-Adjusted Performance Index (SAPI)**:
- **Unweighted SAPI**: Average % above/below benchmark per seat (equal weight)
- **Weighted SAPI**: Average weighted by number of shifts per seat (total contribution)
Benchmarks are based on 125% of seat averages to reflect the 75th percentile.
""")

# --- Load and Process Data ---
data_path = Path("CY24 Mammo.xlsx")  # In main directory
hd_df, data_df = load_data(data_path)
seat_section, seat_rad_df, combined = process_data(hd_df, data_df)

# --- Display Dashboard ---
st.subheader("📋 SAPI Leaderboard")
st.dataframe(
    combined.sort_values('SAPI_Weighted', ascending=False).round(2),
    use_container_width=True,
    height=300
)

st.subheader("🪑 Seat-Level Breakdown")
st.dataframe(
    seat_rad_df[['RAD', 'SEAT', 'Norm_HD_Avg', 'Benchmark', 'SAPI_Unweighted', 'Shifts']].round(2),
    use_container_width=True,
    height=400
)

st.subheader("📈 Benchmark Reference Table")
st.dataframe(
    seat_section.round(2),
    use_container_width=True,
    height=200
)

st.markdown("---")
st.markdown("Developed for executive reporting. For questions, contact agibson@milvrad.com")