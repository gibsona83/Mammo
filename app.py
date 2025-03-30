# Streamlit Dashboard for Dr. Gor - Ad-Hoc Reporting
# Author: ChatGPT

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# Set up the Streamlit page layout with a modern look
st.set_page_config(page_title='Dr. Gor - Ad-Hoc Reporting', layout='wide', page_icon='📊')

st.markdown("<style>body {background-color: #f4f4f4; font-family: Arial, sans-serif;} .metric {font-size: 1.5em;}</style>", unsafe_allow_html=True)

st.title("🌟 Dr. Gor's Radiology Ad-Hoc Reporting Dashboard")
st.markdown("## Executive Summary and KPI Metrics")

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

# Sidebar filters
st.sidebar.header("Filter Options")
provider_list = qgenda_data['Provider'].unique()
selected_provider = st.sidebar.selectbox("Select Provider", ['All'] + list(provider_list))
date_range = st.sidebar.date_input("Select Date Range", [])

# Calculate half-day mammography shifts
half_day_mammo_shifts = qgenda_data[(qgenda_data['Shift Length'] == 'Half') & (qgenda_data['Shift Type'] == 'Mammo')].shape[0]

# KPI Metrics
total_wRVU = mbms_data['WORK RVU'].sum()
total_procedures = len(mbms_data)
avg_wRVU_per_half_day = total_wRVU / half_day_mammo_shifts

st.markdown("### Key Performance Indicators (KPIs)")
col1, col2, col3 = st.columns(3)
col1.metric("🔍 Total wRVU", f"{total_wRVU:.2f}")
col2.metric("📝 Total Procedures", f"{total_procedures}")
col3.metric("📊 Avg wRVU per Half Day", f"{avg_wRVU_per_half_day:.2f}")

st.markdown("## Detailed Task and Procedure Breakdown")
if selected_provider != 'All':
    filtered_qgenda = qgenda_data[qgenda_data['Provider'] == selected_provider]
else:
    filtered_qgenda = qgenda_data

if date_range:
    filtered_qgenda = filtered_qgenda[filtered_qgenda['Date'].between(date_range[0], date_range[-1])]

st.write("### Provider Tasks from QGenda")
st.dataframe(filtered_qgenda.style.set_precision(2))

st.write("### Studies Read (From MBMS Data)")
filtered_mbms = mbms_data[mbms_data['DR NAME'].isin(filtered_qgenda['Provider'].unique())]
st.dataframe(filtered_mbms.style.set_precision(2))
