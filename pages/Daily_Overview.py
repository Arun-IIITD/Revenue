import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from statsmodels.tsa.arima.model import ARIMA
import plotly.express as px
import pymongo
import sys
import openpyxl
import os
import zipfile
from datetime import datetime, timedelta
import io
from CAL import perform
from prophet import Prophet
from prophet.plot import add_changepoints_to_plot
import altair as alt  
from sklearn.metrics import mean_absolute_error, mean_squared_error

UPLOAD_FOLDER = os.path.join(os.getcwd(), "Upload")

df2 = pd.read_csv('weather.csv')
st.set_page_config(page_title="Daily Overview", page_icon=":overview", layout="wide")

# Define a custom CSS style for the fixed header
header_style = """
position: fixed;
top: 0;
left: 0;
width: 100%;
background-color: #1E90FF;
color: white;
padding: 10px;
text-align: center;
"""

# # Create the fixed header using the custom CSS style
# st.markdown(f'<div style="{header_style}">Hotel Revenue Forecasting</div>', unsafe_allow_html=True)

# MongoDB connection setup
connection_uri = "mongodb+srv://annu21312:6dPsrXPfhm19YxXl@hello.hes3iy5.mongodb.net/"
client = pymongo.MongoClient(connection_uri, serverSelectionTimeoutMS=30000)
database_name = "Revenue_Forecasting"
db = client[database_name]
collection = db["Forecastin"]

# Get current date and previous date
current_date = datetime.now().strftime("%Y-%m-%d")
previous_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# Dropdown options for the second date
date_options = ["Previous Date", "Last Year Same Date", "Last Year Same Weekday"]
st.markdown("<div class='section-title'>Daily Overview</div>", unsafe_allow_html=True)

# Sidebar to select dates
date_option = st.selectbox("Select Date Option for the Second Date:", date_options)
date1_default = current_date
date2_default = previous_date
if date_option == "Previous Date":
    date2 = (datetime.strptime(current_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
elif date_option == "Last Year Same Date":
    date2 = (datetime.strptime(current_date, "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")
elif date_option == "Last Year Same Weekday":
    date2 = (datetime.strptime(current_date, "%Y-%m-%d") - timedelta(weeks=52)).strftime("%Y-%m-%d")
# else:
#     date2 = st.date_input("Select Custom Date:", datetime.strptime(previous_date, "%Y-%m-%d"))

col1, col2 = st.columns((2))
with col1:
    # date1 = st.date_input("Select Start Date:", datetime.strptime(current_date, "%Y-%m-%d"))
    date1 = st.date_input("Select Date:", datetime.strptime(current_date, "%Y-%m-%d"))
with col2:
    # date2 = st.date_input("Select End Date:", datetime.strptime(date2, "%Y-%m-%d"))
    date2 = st.date_input("Select comparision Date:", datetime.strptime(date2, "%Y-%m-%d"))
# Convert selected dates to ISO format for MongoDB query
date1 = date1.strftime("%Y-%m-%d")
date2 = date2.strftime("%Y-%m-%d")
css = """
    body {
        background-color: #f8f9fa !important;
    }

    .container {
        margin: 20px;
    }

    .header {
        background-color: #1E90FF;
        color: white;
        padding: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }

    .date-display {
        font-size: 18px;
        margin-bottom: 20px;
    }

    .card {
        flex-basis: 30%;
        padding: 20px;
        margin: 10px 0;
        border-radius: 10px;
        box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }

    .card:hover {
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    }

    .card-values {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .card-values div {
        text-align: center;
        flex-basis: 33%;
    }

    .card-values div.left {
        text-align: left;
    }

    .card-values div.right {
        text-align: right;
    }
"""

# Apply CSS to the HTML elements
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# # Display the header
# st.markdown("<div class='header'>Hotel Revenue Forecasting</div>", unsafe_allow_html=True)

# Display the selected dates in one line
st.markdown(f"<div class='date-display'>Selected Date Range: {date1} to {date2}</div>", unsafe_allow_html=True)



# # Convert selected dates to ISO format for MongoDB query
# date1 = date1.strftime("%Y-%m-%d")
# date2 = date2.strftime("%Y-%m-%d")
def display_data():
    # CSS for styling
    css = """
    body {
        background-color: #ffffff;
        color: #000000;
    }
    .card-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
    }

    .card {
        flex-basis: 30%; /* Set card width to 30% for three cards in a row */
        # background-color: #fff;
        padding: 20px;
        margin: 10px 0;
        border-radius: 10px;
        box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.1);
        # transition: transform 0.2s, box-shadow 0.2s;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;

        color: {card_text_color};
    }
    .card:hover {
        # transform: scale(1.02); /* Add zoom effect on hover */
        # transform: scale(1.03);
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    }

    .section-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
        color: {card_text_color};
    }
    """

    # Apply CSS to the HTML elements
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    # st.markdown("<div class='section-title'>Daily Overview</div>", unsafe_allow_html=True)
    # MongoDB query to find data for the two selected dates
    query = {"Business Date": {"$in": [date1, date2]}}
    cursor = collection.find(query)
    
    # Convert MongoDB cursor to DataFrame
    df = pd.DataFrame(list(cursor))
    
    if not df.empty:
        # Extract data for the two selected dates
        date1_data = df[df["Business Date"] == date1]
        date2_data = df[df["Business Date"] == date2]
        # Check if data exists for both selected dates
        if not date1_data.empty and not date2_data.empty:

            def display_field(field_name, date1_data, date2_data):
                field_diff = date2_data[field_name].iloc[0] - date1_data[field_name].iloc[0]
                color = "red" if isinstance(field_diff, (int, float)) and field_diff < 0 else "green"
                
                st.markdown(
                    f"<div class='card'>"
                    f"<p>{field_name}</p>"

                    f"<div class='card-values'>"
                    f"<div class='card-values' style='display: flex; justify-content: space-between; align-items: center;'>"
                    f"<div style='text-align: left; flex-basis: 33%; color: {color};'>{date1_data[field_name].iloc[0]}</div>"
                    f"<div style='text-align: center; flex-basis: 33%; font-weight: bold;'>{field_diff:.2f}</div>"
                    f"<div style='text-align: right; flex-basis: 33%;'>{date2_data[field_name].iloc[0]}</div>"
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            # Display values for each field
            fields = ["Occupancy %", "ARR", "Arrival Rooms", "OOO Rooms", "Pax", "Room Revenue", "Rooms for Sale", "Departure Rooms", "House Use", "Total Room Inventory"]
            col1, col2, col3 = st.columns(3)

            # # Display values for each field
            for i, field in enumerate(fields):
                if i % 3 == 0:
                    card_column = col1
                elif i % 3 == 1:
                    card_column = col2
                else:
                    card_column = col3
                with card_column:
                    display_field(field, date1_data, date2_data)

        else:
            st.warning("Data not available for one or both of the selected dates.")

display_data()