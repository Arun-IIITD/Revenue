import streamlit as st
import pandas as pd
import datetime
import pymongo
from datetime import datetime, timedelta
from datetime import datetime, timedelta

# UPLOAD_FOLDER = os.path.join(os.getcwd(), "Upload")

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
# MongoDB connection setup
connection_uri = "mongodb+srv://annu21312:6dPsrXPfhm19YxXl@hello.hes3iy5.mongodb.net/"
client = pymongo.MongoClient(connection_uri, serverSelectionTimeoutMS=30000)
database_name = "Revenue_Forecasting"
db = client[database_name]
collection = db["Forecastin"]

current_date = datetime.now().strftime("%Y-%m-%d")
previous_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# Dropdown options for the second date
date_options = ["Previous Date", "Last Year Same Date", "Last Year Same Weekday"]
st.markdown("<div class='section-title'>Daily Overview</div>", unsafe_allow_html=True)

date1_default = current_date
date2_default = previous_date
col1, col2 = st.columns(2)
with col1:
    date1 = st.date_input("Select Date:", datetime.strptime(current_date, "%Y-%m-%d"))
with col2:
    date_option = st.selectbox("Relative to:", date_options)

    if date_option == "Previous Date":
        date2 = (datetime.strptime(current_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    elif date_option == "Last Year Same Date":
        date2 = (datetime.strptime(current_date, "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")
    elif date_option == "Last Year Same Weekday":
        date2 = (datetime.strptime(current_date, "%Y-%m-%d") - timedelta(weeks=52)).strftime("%Y-%m-%d")

# with col2:
    date2 =  datetime.strptime(date2, "%Y-%m-%d")
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
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
st.markdown(f"<div class='date-display'> {date1} vs {date2} incl. tentative</div>", unsafe_allow_html=True)


def display_data():
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
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    # MongoDB query to find data for the two selected dates
    query = {"Business Date": {"$in": [date1, date2]}}
    cursor = collection.find(query)
    df = pd.DataFrame(list(cursor))
    
    if not df.empty:
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