# Streamlit Dashboard for Dr. Gor - Provider-Level Reporting
# Author: ChatGPT

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

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

# Inspect columns to find the correct provider field
st.write("MBMS Data Columns:", mbms_data.columns)
st.write("QGenda Data Columns:", qgenda_data.columns)

# Temporary display to help identify the correct provider column
st.write("### Sample MBMS Data")
st.dataframe(mbms_data.head())

st.write("### Sample QGenda Data")
st.dataframe(qgenda_data.head())
