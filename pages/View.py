import base64
import os
from io import BytesIO
#from streamlit_extras.switch_page_button import switch_page
from statistics import mean
import streamlit as st
import pandas as pd
import plotly.express as px
import calendar
import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pymongo
import streamlit as st
from prophet import Prophet
from prophet.plot import add_changepoints_to_plot
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA

st.set_page_config(page_title="Revenue Forecasting", page_icon=":overview", layout="wide", initial_sidebar_state="collapsed")

def set_custom_styles():
    """
    Custom styles to hide Streamlit general elements and adjust margins.
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
    selected_page = selected_page or "market"
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
            <a style="color: {'red' if selected_page == 'market' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'market' else 'none'}" href="/market" target="_self">market</a>
            <a style="color: {'red' if selected_page == 'View' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'View' else 'none'}" href="/View" target="_self">View</a>
             <a style="color: {'red' if selected_page == 'Trend' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Trend' else 'none'}" href="/trend" target="_self">Trend</a>
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
    "/market": "market",
    "/View": "View",
      "/Trend": "Trend",
}
selected_page = url_to_page.get(url_path)
custom_top_bar(selected_page)
# -----------------------------------------------
#FOR MONTHLY VIEW AND DAILY VIEW

def main():
    st.markdown(
        """
        <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .input-section {
            margin-bottom: 20px;
        }
        .button-section {
            text-align: center;
        }
        .download-section {
            margin-top: 20px;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

#FOR FETCHING DATA ACCURACY
    connection_uri = "mongodb+srv://annu21312:6dPsrXPfhm19YxXl@hello.hes3iy5.mongodb.net/"
    client = pymongo.MongoClient(connection_uri, serverSelectionTimeoutMS=30000)
    database_name = "Revenue_Forecasting"
    db = client[database_name] 
    collection4 = db["Accuracy"]
    cursor4 = collection4.find({})
    data4 = pd.DataFrame(list(cursor4))
    data4 = data4.drop_duplicates() 
    collection5 = db["Revenue"]
    cursor5 = collection5.find({})
    data5 = pd.DataFrame(list(cursor5))
    data5 = data5.drop_duplicates() 
    #--------------------------------------
    
    data1 =  data4[['Business Date','Room Revenue','Rooms Sold']]
    data2 = data5[['Business Date','Room Revenue','Rooms Sold','Arrival Rooms','Individual Revenue','Individual Confirm']]
    data = pd.concat([data1,data2],ignore_index=True)
    print(len(data))
    print(data)
    #---------------------------------------------------------------------------
    st.subheader("Select Date Range for Analysis")
    date_range = st.date_input("Select Date Range", [])
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = None, None  

    if start_date and end_date:
        data['Business Date'] = pd.to_datetime(data['Business Date'])
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filter data based on selected date range
        filtered_data = data[(data['Business Date'] >= start_date) & (data['Business Date'] <= end_date)]

        # Show filtered data or perform further analysis
        st.write("Filtered Data", filtered_data)  # Placeholder for actual data handling
    else:
        st.write("Please select a start and end date to filter the data.")
   



    #YEARLY, MONTH, DAILY AND WEEKLY VIEW
    st.subheader("VIEW")
    view_option = st.selectbox("Select View", ['Yearly', 'Monthly','Weekly','Daily'])
    data['Business Date'] = pd.to_datetime(data['Business Date'])
    # data = pd.DataFrame({
    # 'Business Date': pd.date_range(start='2022-01-01', end='2024-01-18',freq='D'),
    # 'Room Revenue': np.random.randint(100000, 2000000, size=100000)})

    if view_option == 'Daily':
        daily_data = data.groupby(data['Business Date'].dt.date).agg({'Room Revenue': 'sum', 'Rooms Sold': 'sum','Arrival Rooms':'sum','Individual Revenue':'sum','Individual Confirm':'sum'}).reset_index()
        fig = px.line(daily_data, x='Business Date', y=['Room Revenue'], title='Daily View')
        fig1 = px.line(daily_data, x='Business Date', y=['Rooms Sold'], title='Daily View')
        fig2 = px.line(daily_data, x='Business Date', y=['Arrival Rooms'], title='Daily View')
        fig3 = px.line(daily_data, x='Business Date', y=['Individual Confirm'], title='Daily View')
        fig4 = px.line(daily_data, x='Business Date', y=['Individual Revenue'], title='Daily View')
        st.plotly_chart(fig)
        st.plotly_chart(fig1)
        st.plotly_chart(fig2)
        st.plotly_chart(fig3)
        st.plotly_chart(fig4)

    elif view_option == 'Monthly':
        data['Month-Year'] = data['Business Date'].dt.strftime('%Y-%m')
        daily_data = data.groupby('Month-Year').agg({'Room Revenue': 'sum', 'Rooms Sold': 'sum','Arrival Rooms':'sum','Individual Revenue':'sum','Individual Confirm':'sum'}).reset_index()
        #daily_data = data.groupby(data['Business Date'].dt.to_period('M')).agg({'Room Revenue': 'sum', 'Rooms Sold': 'sum'}).reset_index()
        daily_data.rename(columns={'Business Date': 'Month'}, inplace=True)
        #fig = px.line(daily_data, x='J', y=['Room Revenue'], title='Monthly View')
    elif view_option == 'Weekly':
        daily_data = data.groupby(data['Business Date'].dt.to_period('W')).agg({'Room Revenue': 'sum', 'Rooms Sold': 'sum','Arrival Rooms':'sum','Individual Revenue':'sum','Individual Confirm':'sum'}).reset_index()
        daily_data.rename(columns={'Business Date': 'Week'}, inplace=True)
        #fig = px.line(daily_data, x='Week', y=['Room Revenue'], title='Daily View')
    elif view_option == 'Yearly':
        daily_data = data.groupby(data['Business Date'].dt.year).agg({'Room Revenue': 'sum', 'Rooms Sold': 'sum','Arrival Rooms':'sum','Individual Revenue':'sum','Individual Confirm':'sum'}).reset_index()
        daily_data.rename(columns={'Business Date': 'Year'}, inplace=True)
        fig = px.bar(daily_data, x='Year', y=['Room Revenue'], title='Yearly View')
        fig1 = px.bar(daily_data, x='Year', y=['Rooms Sold'], title='Yearly View')
        fig2 = px.bar(daily_data, x='Year', y=['Arrival Rooms'], title='Yearly View')
        fig3 = px.bar(daily_data, x='Year', y=['Individual Confirm'], title='Yearly View')
        fig4 = px.bar(daily_data, x='Year', y=['Individual Revenue'], title='Yearly View')  
        st.plotly_chart(fig)
        st.plotly_chart(fig1)
        st.plotly_chart(fig2)
        st.plotly_chart(fig3)
        st.plotly_chart(fig4)


    st.dataframe(daily_data)
  






if __name__ == '__main__':
    main()
