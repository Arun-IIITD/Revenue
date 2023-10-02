import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from statsmodels.tsa.arima.model import ARIMA
import plotly.express as px
import pymongo
import sys
# from pages import Daily_Overview
df2 = pd.read_csv('weather.csv')
connection_uri = "mongodb+srv://annu21312:6dPsrXPfhm19YxXl@hello.hes3iy5.mongodb.net/"
client = pymongo.MongoClient(connection_uri)
database_name = "Revenue_Forecasting"

db = client[database_name]
collection = db["Forecasting"]
st.set_page_config(page_title="Revenue Forecasting", page_icon=":barchart:", layout="wide")

st.title("Hotel Revenue Forecasting")
st.write("Select a date range to check room revenue:")

col1, col2=st.columns((2))
with col1:
    start_date = st.date_input("Select a start date:")        
with col2:
    end_date = st.date_input("Select an end date:")


if start_date <= end_date:
    # Convert start and end dates to ISO format for MongoDB query
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    # MongoDB query to filter data
    query = {"Business Date": {"$gte": start_date, "$lte": end_date}}
    
    # Fetch data from MongoDB
    cursor = collection.find(query)
    
    # Convert MongoDB cursor to DataFrame
    df = pd.DataFrame(list(cursor))
    
    if not df.empty:
            # Display the filtered data
        st.write("Filtered Data:")
        st.write(df)

        # Display 'Room Revenue' for the selected date range
        total_room_revenue = df['Room Revenue'].sum()
        st.write(f"Total Room Revenue for the selected date range: ${total_room_revenue:.2f}")

        # Interactive chart using Plotly with hover info and different colors
        fig = px.line(df, x='Business Date', y='Room Revenue', title='Room Revenue Over Time',
                      labels={'Business Date': 'Date', 'Room Revenue': 'Revenue'},
                      hover_data={'Room Revenue': ':,.2f'},  # Format hover value with comma separator
                      line_shape='linear',
                      color_discrete_sequence=['#0074D9'])  # Use a distinct color (blue)

        fig.update_traces(mode="lines+markers", hovertemplate="Date: %{x}<br>Revenue: $%{y:,.2f}<extra></extra>")
        fig.update_xaxes(type='date', showgrid=True, gridwidth=1, gridcolor='lightgray')  # Add gridlines
        fig.update_yaxes(title_text='Revenue', showgrid=True, gridwidth=1, gridcolor='lightgray')  # Add gridlines
        st.plotly_chart(fig)
    else:
        st.warning("No data available for the selected date range.")
else:
    st.error("End date must be greater than or equal to the start date.")





def display_data():

    # MongoDB connection setup
    connection_uri = "mongodb+srv://annu21312:6dPsrXPfhm19YxXl@hello.hes3iy5.mongodb.net/"
    client = pymongo.MongoClient(connection_uri)
    database_name = "Revenue_Forecasting"
    db = client[database_name]
    collection = db["Forecasting"]

    

    # Title and section selection
    # st.title("Hotel Revenue Dashboard")
    section = st.sidebar.selectbox("Select a Section:", ["Daily Overview", "Performance", "Future Months and Pickup"])

    # Define CSS for styling
    css = """
    .card-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
    }

    .card {
        flex-basis: 30%; /* Set card width to 30% for three cards in a row */
        background-color: #fff;
        padding: 20px;
        margin: 10px 0;
        border-radius: 10px;
        box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;

    }
    .card:hover {
        # transform: scale(1.02); /* Add zoom effect on hover */
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    }

    .section-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    """

    # Apply CSS to the HTML elements
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

    if section == "Daily Overview":
        # st.header("Daily Overview")
        st.markdown("<div class='section-title'>Daily Overview</div>", unsafe_allow_html=True)
        col1, col2=st.columns((2))
        with col1:

        # User input for two specific dates
            date1 = st.date_input("Select the First Date:")
        with col2:
            date2 = st.date_input("Select the Second Date:")
        
        # Convert selected dates to ISO format for MongoDB query
        date1 = date1.strftime("%Y-%m-%d")
        date2 = date2.strftime("%Y-%m-%d")
        
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

                # Function to display values for a given field
                def display_field(field_name, date1_data, date2_data):
                    # Calculate the difference between the two dates
                    field_diff = date2_data[field_name].iloc[0] - date1_data[field_name].iloc[0]
                    
                    # Choose a color based on the field_diff (you can customize this logic)
                    color = "red" if isinstance(field_diff, (int, float)) and field_diff < 0 else "green"
                    
                    # Display the values in a modern design button
                    st.markdown(
                        f"<div class='card'>"
                        # f"<h5>{field_name}</h5>"
                        f"<p>{field_name}</p>"

                        f"<div class='card-values'>"
                        # f"<span style='font-size: 28px;text-align: left'>{date1_data[field_name].iloc[0]}&emsp;</span> <span class='red-text' style='color: {color};text-align: center'>{field_diff:.2f}</span> &emsp;<span style='text-align: right;'>{date2_data[field_name].iloc[0]}</span>"
                        
                        f"<div class='card-values' style='display: flex; justify-content: space-between; align-items: center;'>"
                        # f"<div style='text-align: left; flex-basis: 33%;font-size: 28px;color: {color};'>{date1_data[field_name].iloc[0]}</div>"
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
                # for field in fields:
                #     display_field(field, date1_data, date2_data)
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
            
        else:
            st.warning("No data available for the selected dates.")
            
    elif section == "Performance":
        st.header("Performance")
        
        # Add performance-related content here
        
    elif section == "Future Months and Pickup":
        st.header("Future Months and Pickup")
        
        # Add future months and pickup related content here

    # Close MongoDB connection
    client.close()
Daily_Overview, Performance, Future_Months_and_Pickup=st.tabs(["Daily Overview", "Performance", "Future Months and Pickup"])
with Daily_Overview:
    display_data()

# tabs = ["Daily Overview", "Performance", "Future Months and Pickup"]
# selected_tab = st.sidebar.radio("Select a Section:", tabs)

# # Conditional content based on the selected tab
# if selected_tab == "Daily Overview":
#     st.header("Comparison")
#     # Call the function from "first.py" to display data under "Daily Overview" tab
#     first.display_data()

# # Close MongoDB connection
# client.close()

