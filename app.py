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

# Improved name normalization function
def normalize_name(name):
    # Remove titles like 'Md', 'Do', ',', '.' and extra spaces
    name = re.sub(r'(Md|Do|,|\.)', '', name).strip()
    # Remove multiple spaces
    name = re.sub(r'\s+', ' ', name)
    return name

mbms_data['Normalized Name'] = mbms_data['DR NAME'].apply(normalize_name)
qgenda_data['Normalized Name'] = qgenda_data['Provider'].apply(normalize_name)

# Adjust shift counts: Split full days into two half days
qgenda_data['Adjusted Shifts'] = np.where(qgenda_data['Shift Length'] == 'Full', 2 * qgenda_data['Corrected Shifts'], qgenda_data['Corrected Shifts'])

# Calculate total wRVU and wRVUs per half day per provider
provider_summary = mbms_data.groupby('Normalized Name').agg(
    total_wRVU=('WORK RVU', 'sum'),
    total_procedures=('CODE', 'count')
).reset_index()

# Calculate half-day mammography shifts per provider
half_day_shifts = qgenda_data[qgenda_data['Shift Type'] == 'Mammo'].groupby('Normalized Name').agg(
    half_day_count=('Adjusted Shifts', 'sum')
).reset_index()

# Merge shift data into the provider summary
provider_summary = pd.merge(provider_summary, half_day_shifts, on='Normalized Name', how='left')

# Fill NaN values for half_day_count with 0
provider_summary['half_day_count'].fillna(0, inplace=True)

# Avoid division by zero for wRVUs per half day calculation
provider_summary['wRVUs_per_half_day'] = np.where(
    provider_summary['half_day_count'] > 0,
    provider_summary['total_wRVU'] / provider_summary['half_day_count'],
    np.nan
)

# Display provider-level metrics
st.markdown("### Provider-Level Summary")
st.dataframe(provider_summary)

st.markdown("### Bar Chart: Total wRVU per Provider")
fig = px.bar(provider_summary, x='Normalized Name', y='total_wRVU', title='Total wRVU per Provider')
st.plotly_chart(fig)

st.markdown("### Bar Chart: wRVUs per Half Day per Provider")
fig2 = px.bar(provider_summary, x='Normalized Name', y='wRVUs_per_half_day', title='wRVUs per Half Day per Provider')
st.plotly_chart(fig2)
