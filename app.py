# Streamlit Dashboard for Dr. Gor - Provider-Level Reporting
# Author: ChatGPT

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import re

# Set up the Streamlit page layout with a modern look
st.set_page_config(page_title='Dr. Gor - Provider-Level Reporting', layout='wide', page_icon='📊')

st.markdown("<style>body {background-color: #f4f4f4; font-family: Arial, sans-serif;} .metric {font-size: 1.5em;}</style>", unsafe_allow_html=True)

st.title("🌟 Dr. Gor's Radiology Provider-Level Reporting Dashboard")
st.markdown("## Provider-Level Metrics: Total wRVU and wRVUs per Half Day")

# Placeholder for loading data
@st.cache_data
def load_data():
    # Load pre-existing data from GitHub repository
    qgenda_data = pd.read_excel("https://raw.githubusercontent.com/gibsona83/mammo/main/Cleaned_QGenda_Full_2024_Data.xlsx", sheet_name="Combined")
    mbms_data = pd.read_csv("https://raw.githubusercontent.com/gibsona83/mammo/main/Cleaned_MBMS_Site_Encounter_Data_2024.csv")
    # Convert the Date column to datetime format
    qgenda_data['Date'] = pd.to_datetime(qgenda_data['Date'], errors='coerce')
    return qgenda_data, mbms_data

# Load data
qgenda_data, mbms_data = load_data()

# Hardcoded half-day counts based on provided image
def get_hardcoded_half_day_count(provider_name):
    half_day_counts = {
        "Jajoo, Anurita": 64,
        "Johnson, Meredith": 86,
        "Ksepka, Martha": 176,
        "Lyall, Ashima": 60,
        "Mambalam, Pramod": 175,
        "Roman, Nancy": 188,
        "Shelat, Nirav": 261,
        "Trevisan, Susan": 206,
        "Verma, Rahul": 223
    }
    return half_day_counts.get(provider_name, 0)

# Calculate total wRVU and wRVUs per half day per provider
provider_summary = mbms_data.groupby('DR NAME').agg(
    total_wRVU=('WORK RVU', 'sum'),
    total_procedures=('CODE', 'count')
).reset_index()

# Apply hardcoded half-day counts
provider_summary['half_day_count'] = provider_summary['DR NAME'].apply(get_hardcoded_half_day_count)

# Calculate wRVUs per half day
provider_summary['wRVUs_per_half_day'] = np.where(
    provider_summary['half_day_count'] > 0,
    provider_summary['total_wRVU'] / provider_summary['half_day_count'],
    np.nan
)

# Display provider-level metrics
st.markdown("### Provider-Level Summary")
st.dataframe(provider_summary)

st.markdown("### Bar Chart: Total wRVU per Provider")
fig = px.bar(provider_summary, x='DR NAME', y='total_wRVU', title='Total wRVU per Provider')
st.plotly_chart(fig)

st.markdown("### Bar Chart: wRVUs per Half Day per Provider")
fig2 = px.bar(provider_summary, x='DR NAME', y='wRVUs_per_half_day', title='wRVUs per Half Day per Provider')
st.plotly_chart(fig2)
