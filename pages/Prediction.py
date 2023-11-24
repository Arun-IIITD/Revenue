import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import plotly.express as px
import pymongo
import os
from CAL import perform
from prophet import Prophet
from prophet.plot import add_changepoints_to_plot
import altair as alt  
from sklearn.metrics import mean_absolute_error, mean_squared_error
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Revenue Forecasting", page_icon=":overview", layout="wide", initial_sidebar_state="collapsed")

def set_custom_styles():
    """
    Custom styles to hide Streamlit default elements and adjust margins.
    """

    custom_styles="""
    <style>
    MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility:hidden;}
    body {
        margin: 0;
        padding: 0;
        font-family: "Helvetica", sans-serif;
    }
    [data-testid="collapsedControl"] {
        display: none
    }     
    .main {
        # margin-left: -80px;
        padding: 20px;
        # margin-top:  -110px; 
        margin-left: -3rem;
        margin-top: -7rem;
        margin-right: -103rem;
    }
    .section-title {
        font-weight: bold;
        font-size: 24px;
    }
    .big-text {
        font-size: 20px;
    }

    .small-text {
        font-size: 14px;
    }

    </style>
    """
    st.markdown(custom_styles, unsafe_allow_html=True)
def custom_top_bar(selected_page=None):
    """
    Custom HTML for a fixed top bar.
    """
    selected_page = selected_page or "Prediction"
    # current_file = __file__.split("/")[-1]
    current_file = os.path.basename(__file__)
    custom_top_bar = f"""
    <style>
        #top-bar {{
            padding: 10px;
            # border-bottom: 1px solid #555;
            border-bottom: 1px solid #ccc;
            # color: black;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        #top-bar h3 {{
            padding: 10px;
            font-weight: bold;
            font-size: 24px;
        }}
        #nav-links {{
            display: flex;
            align-items: center;
        }}
        #nav-links a {{            
            text-decoration: none;
            margin-right: 20px;
            font-size: 16px;
            # font-family: "Source Sans Pro", sans-serif;
            # font-weight: 400;
            # transition: color 0.3s ease-in-out;
        }}
        #nav-links a:hover {{
            # color: #00bcd4;
            color: rgb(255, 75, 75);
        }}
    </style>
    <div id="top-bar">
        <h3 style="font-weight: bold; color: grey;">Revenue Forecasting</h3>
        <div id="nav-links">
            <a style="color: {'red' if selected_page == 'Home' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Home' else 'none'}" href="/Home" target="_self">Home</a>
            <a style="color: {'red' if selected_page == 'Daily_Overview' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Daily_Overview' else 'none'}" href="/Daily_Overview" target="_self">Daily Overview</a>
            <a style="color: {'red' if selected_page == 'Revenue_Analysis' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Revenue_Analysis' else 'none'}" href="/Revenue_Analysis" target="_self">Revenue Analysis</a>
            <a style="color: {'red' if selected_page == 'Report' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Report' else 'none'}" href="/Report" target="_self">Report</a>
            <a style="color: {'red' if selected_page == 'Prediction' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Prediction' else 'none'}" href="/Prediction" target="_self">Prediction</a>
            <a style="color: {'red' if selected_page == 'Upload' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Upload' else 'none'}" href="/Upload" target="_self">Manage Collections</a>
        </div>
    </div>
    """
    st.markdown(custom_top_bar, unsafe_allow_html=True)

# custom_top_bar()
set_custom_styles()

url_path = st.experimental_get_query_params().get("pages", [""])[0]
url_to_page = {
    "/Home": "Home",
    "/Daily_Overview": "Daily_Overview",
    "/Revenue_Analysis": "Revenue_Analysis",
    "/Report": "Report",
    "/Prediction": "Prediction",
    "/upload": "Upload",
}
selected_page = url_to_page.get(url_path)
custom_top_bar(selected_page)
# -----------------------------------------------

connection_uri = "mongodb+srv://annu21312:6dPsrXPfhm19YxXl@hello.hes3iy5.mongodb.net/"
client = pymongo.MongoClient(connection_uri, serverSelectionTimeoutMS=30000)
database_name = "Revenue_Forecasting"
db = client[database_name]

# Fetch data from MongoDB
collection4 = db["Prophet"]
cursor2 = collection4.find({})
data = pd.DataFrame(list(cursor2))

data.rename(columns={'Date': 'ds', 'Revenue': 'y'}, inplace=True)

# Initialize and fit the Prophet model
model = Prophet()
model.fit(data)

# Create a future DataFrame for forecasting (forecast for the next 7 days)
future = model.make_future_dataframe(periods=7)

# Generate forecasts
forecast = model.predict(future)

# ACTUAL REVENUE FOR 7 DAYS
actual_data = data.tail(7)

# PREDICTIONS FOR 7 DAYS
next_7_days_forecast = forecast.tail(7)

predictions_for_7_days = [int(x) for x in list(next_7_days_forecast['yhat'])]
actual_data_for_7_days = [int(x) for x in list(actual_data['y'])]

# Calculate accuracy as a percentage
accuracy = np.mean([pred / actual * 100 for pred, actual in zip(next_7_days_forecast['yhat'], actual_data['y'])])
# Calculate accuracy metrics
mae = mean_absolute_error(actual_data['y'], next_7_days_forecast['yhat'])
mse = mean_squared_error(actual_data['y'], next_7_days_forecast['yhat'])
rmse = np.sqrt(mse)
st.markdown("\n")
st.markdown("\n")
st.markdown("<div class='section-title' style='font-weight: bold; font-size: 24px;'>Forecasting for next week</div>", unsafe_allow_html=True)

# Data Presentation
col1, col2=st.columns(2)
with col1:
    st.markdown('Prediction')
    st.dataframe(pd.DataFrame({'Date': next_7_days_forecast['ds'], 'Predicted Revenue': predictions_for_7_days}))
with col2:
    st.markdown('Actual Revenue')
    st.dataframe(pd.DataFrame({'Date': actual_data['ds'], 'Actual Revenue': actual_data_for_7_days}))

# CSS for styling
st.markdown(
    """
    <style>
    /* Adjust text size */
    .big-text {
        font-size: 20px;
    }
    
    .small-text {
        font-size: 14px; /* Adjust the font size as needed */
    }

    /* Style the table */
    table.dataframe {
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# st.subheader(f'Accuracy: {accuracy:.2f}%')
st.markdown(f'Accuracy: {accuracy:.2f}%')
# st.markdown("<div class='section-title'>Revenue Forecast Plot</div>", unsafe_allow_html=True)
# st.header('Revenue Forecast Plot (Altair Chart):')
forecast_chart = alt.Chart(forecast).mark_line().encode(
    x=alt.X('ds:T', title='Date', axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
    y=alt.Y('yhat:Q', title='Revenue Prediction', axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
    color=alt.value('blue'),  # Line color
    strokeWidth=alt.value(2),  # Line width
).properties(
    width=700,  # Chart width
    height=400,  # Chart height
    title='Revenue Forecast',  # Chart title
).configure_title(
    fontSize=16,  # Title font size
    anchor='start'  # Title alignment
).configure_axis(
    labelFontSize=12,  # Axis label font size
    titleFontSize=14  # Axis title font size
)
st.markdown(
    """
    <style>
    .altair-chart {
        width: 100%;
        height: 400px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.altair_chart(forecast_chart, use_container_width=True)
# st.altair_chart(forecast_chart, use_container_width=True, key='forecast_chart')

# -------------------------------

col3, col4=st.columns(2)
with col3:
    st.markdown("<div class='section-title'>Revenue Components</div>", unsafe_allow_html=True)
    # Altair Chart for components that closely resembles the Matplotlib plot
    components_chart = alt.Chart(forecast).mark_area().encode(
        x='ds:T',
        y='trend:Q',
        y2='yhat_upper:Q',
        opacity=alt.value(0.5)
    ).interactive()

    st.altair_chart(components_chart, use_container_width=True)
    # st.altair_chart(components_chart, use_container_width=True, key='components_chart')

# ------------------------------
with col4:
    trend_chart = alt.Chart(forecast).mark_line().encode(
        x=alt.X('ds:T', title='Date', axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
        y=alt.Y('trend:Q', title='Trend', axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
        color=alt.value('blue'),  # Line color
        strokeWidth=alt.value(2),  # Line width
    ).properties(
        width=700,  # Chart width
        height=400,  # Chart height
        title='Trend Component',  # Chart title
    ).configure_title(
        fontSize=16,  # Title font size
        anchor='start'  # Title alignment
    ).configure_axis(
        labelFontSize=12,  # Axis label font size
        titleFontSize=14  # Axis title font size
    )
    st.altair_chart(trend_chart, use_container_width=True)
    # st.altair_chart(trend_chart, use_container_width=True, key='trend_chart')

# with col1:
