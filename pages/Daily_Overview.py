import streamlit as st
import pymongo
import pandas as pd
import plotly.graph_objects as go
import os 
# warnings.filterwarnings('ignore')

st.set_page_config(page_title="Daily Overview", page_icon=":barchart:", layout="wide")
def display_data():

    # MongoDB connection setup
    connection_uri = "mongodb+srv://annu21312:6dPsrXPfhm19YxXl@hello.hes3iy5.mongodb.net/"
    client = pymongo.MongoClient(connection_uri)
    database_name = "Revenue_Forecasting"

    db = client[database_name]
    collection = db["Forecasting"]

    # Title and section selection
    st.title("Hotel Revenue Dashboard")
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
display_data()