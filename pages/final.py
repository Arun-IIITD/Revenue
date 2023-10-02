import streamlit as st
import pymongo
import pandas as pd
import plotly.graph_objects as go

# MongoDB connection setup
connection_uri = "mongodb://localhost:27017/"
client = pymongo.MongoClient(connection_uri)
database_name = "revenue_database"
db = client[database_name]
collection = db["revenue_table1"]

# Title and section selection
st.title("Hotel Revenue Dashboard")
section = st.sidebar.selectbox("Select a Section:", ["Daily Overview", "Performance", "Future Months and Pickup"])

# Define CSS for styling
css = """
.card {
    background-color: #fff;
    padding: 20px;
    margin: 10px;
    border-radius: 10px;
    box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.1);
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

    # User input for two specific dates
    date1 = st.date_input("Select the First Date:")
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

            # Calculate the difference between the two dates
            occupancy_diff = date2_data["Occupancy %"].iloc[0] - date1_data["Occupancy %"].iloc[0]
            arr_diff = date2_data["ARR"].iloc[0] - date1_data["ARR"].iloc[0]
            ooo_rooms_diff = date2_data["OOO Rooms"].iloc[0] - date1_data["OOO Rooms"].iloc[0]
           
            
            # Function to display values for a given field
            def display_field(field_name, date1_data, date2_data):
                # Calculate the difference between the two dates
                field_diff = date2_data[field_name].iloc[0] - date1_data[field_name].iloc[0]
                
                # Choose a color based on the field_diff (you can customize this logic)
                color = "red" if isinstance(field_diff, (int, float)) and field_diff < 0 else "green"
                
                # Display the values in a modern design button
                st.markdown(
                    
                    # f"<div class='box-frame'>"
                    # f"<div>"
                    # f"<h3 style='font-size: 24px; font-family: Roboto;'>{field_name}</h3>"
                    # f"<div class='text-size'>"
                    # # f"{date1_data[field_name].iloc[0]} <span class='red-text' style='color: {color};'>{field_diff:.2f}</span> {date2_data[field_name].iloc[0]}"
                    # f"<span style='font-size: 28px;color: {color};'>{date1_data[field_name].iloc[0]}&emsp;</span> {field_diff:.2f} &emsp;{date2_data[field_name].iloc[0]}"

                    # f"</div>"
                    # f"</div>"
                    # f"</div>",
                    f"<div class='card'>"
                    f"<h3>{field_name}</h3>"
                    f"<p>Date 1: {date1_data[field_name].iloc[0]}</p>"
                    f"<p>Date 2: {date2_data[field_name].iloc[0]}</p>"
                    f"<p>Difference: <span style='color: {color};'>{field_diff:.2f}</span></p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            # Display values for each field
            fields = ["Occupancy %", "ARR", "Arrival Rooms", "OOO Rooms", "Pax", "Room Revenue", "Rooms for Sale", "Departure Rooms", "House Use", "Total Room Inventory"]
         
            # Display values for each field
            for field in fields:
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
def show():
    st.title("Daily Overview")
# Close MongoDB connection
client.close()
