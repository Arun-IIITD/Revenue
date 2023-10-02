import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px

# MongoDB connection setup
connection_uri = "mongodb+srv://annu21312:6dPsrXPfhm19YxXl@hello.hes3iy5.mongodb.net/"
client = pymongo.MongoClient(connection_uri, serverSelectionTimeoutMS=30000)
database_name = "Revenue_Forecasting"
db = client[database_name]
collection = db["Forecasting"]

# Title and section selection
st.title("Hotel Revenue Dashboard")
# section = st.sidebar.selectbox("Select a Section:", ["Daily Overview", "Performance", "Future Months and Pickup"])

# if section == "Daily Overview":
st.header("Daily Overview")

# User input for date comparison
start_date = st.date_input("Select the Start Date:")
end_date = st.date_input("Select the End Date:")

if start_date <= end_date:
    # Convert start and end dates to ISO format for MongoDB query
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    
    # MongoDB query to filter data for the selected date range
    query = {"Business Date": {"$gte": start_date, "$lte": end_date}}
    cursor = collection.find(query)
    
    # Convert MongoDB cursor to DataFrame
    df = pd.DataFrame(list(cursor))
    
    if not df.empty:
        # Calculate the average percentages for Occupancy, ARR, and OOO Rooms
        avg_occupancy = df['Occupancy %'].mean()
        avg_arr = df['ARR'].mean()
        avg_ooo_rooms = df['OOO Rooms'].mean()
        
        # Create a DataFrame for the bar chart
        avg_data = pd.DataFrame({
            "Metric": ["Occupancy %", "ARR", "OOO Rooms"],
            "Average Percentage": [avg_occupancy, avg_arr, avg_ooo_rooms]
        })
        
        # Display the comparison in a bar chart
        fig = px.bar(
            avg_data,
            x="Metric",
            y="Average Percentage",
            labels={"x": "Metric", "y": "Average Percentage"},
            title=f"Averages from {start_date} to {end_date}",
        )
        st.plotly_chart(fig)
        
        st.write(f"Average Occupancy: {avg_occupancy:.2f}%")
        st.write(f"Average ARR: ${avg_arr:.2f}")
        st.write(f"Average OOO Rooms: {avg_ooo_rooms:.2f}%")

        st.write("Daily Overview Data:")
        st.write(df[["Business Date", "Occupancy %", "ARR", "OOO Rooms"]])

    else:
        st.warning("No data available for the selected date range.")
else:
    st.error("End date must be greater than or equal to the start date.")

# elif section == "Performance":
#     st.header("Performance")
    
#     # Add performance-related content here
    
# elif section == "Future Months and Pickup":
#     st.header("Future Months and Pickup")
    
#     # Add future months and pickup related content here

# Close MongoDB connection
client.close()
