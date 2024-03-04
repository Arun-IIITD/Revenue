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
    #---------------------------------------------------------------------------
   #YEARLY, MONTH, DAILY AND WEEKLY VIEW
    st.subheader("VIEW")
    data4 = data4.drop_duplicates() 
    data4['Business Date'] = pd.to_datetime(data4['Business Date'])
    data4['Month_Year'] = data4['Business Date'].dt.to_period('M')
    data4_monthly = data4.groupby('Month_Year').sum()  
    data4_monthly.index = data4_monthly.index.to_timestamp()
    data4_monthly['Month_Year'] = data4_monthly.index.strftime('%B_%Y')
    data4['Business Date'] = pd.to_datetime(data4['Business Date'])
    data4['Business Date'] = data4['Business Date'].dt.date
    data4['Business Date'] = pd.to_datetime(data4['Business Date'])
    data4['Year'] = data4['Business Date'].dt.to_period('Y')
    data4_yearly = data4.groupby('Year').sum()
    data4_yearly['Year'] = data4_yearly.index.astype(str)
    data4['Week'] = data4['Business Date'].dt.to_period('W')
    data4_weekly = data4.groupby('Week').sum()
    data4_weekly.index = data4_weekly.index.to_timestamp()
    data4_weekly['Week'] = data4_weekly.index.strftime('%U_%Y')
    
    data5 = data5.drop_duplicates() 
    data5['Business Date'] = pd.to_datetime(data5['Business Date'])
    data5['Month_Year'] = data5['Business Date'].dt.to_period('M')
    data5_monthly = data5.groupby('Month_Year').sum()  
    data5_monthly.index = data5_monthly.index.to_timestamp()
    data5_monthly['Month_Year'] = data5_monthly.index.strftime('%B_%Y')
    data5['Business Date'] = pd.to_datetime(data5['Business Date'])
    data5['Business Date'] = data5['Business Date'].dt.date
    data5['Business Date'] = pd.to_datetime(data5['Business Date'])
    data5['Year'] = data5['Business Date'].dt.to_period('Y')
    data5_yearly = data5.groupby('Year').sum()
    data5_yearly['Year'] = data5_yearly.index.astype(str)
    data5['Week'] = data5['Business Date'].dt.to_period('W')
    data5_weekly = data5.groupby('Week').sum()
    data5_weekly.index = data5_weekly.index.to_timestamp()
    data5_weekly['Week'] = data5_weekly.index.strftime('%U_%Y')

    view_option = st.selectbox("Select View", ['Yearly', 'Monthly','Weekly','Daily'])

    if view_option == 'Daily':
        st.write("Daily View")
        st.write("Data from Sep2021 - Dec2021 is zero due to covid.")
        st.dataframe(data4[['Business Date', 'Room Revenue','Rooms Sold']])  
        st.dataframe(data5[['Business Date','Arrival Rooms','Individual Confirm','Individual Revenue']])  

    elif view_option == 'Monthly':
        st.write("Monthly View")
        st.write("Data from Sep2021 - Dec2021 is zero due to covid.")
        st.dataframe(data4_monthly.reset_index(drop=True)[['Month_Year', 'Room Revenue','Rooms Sold']])  
        st.dataframe(data5_monthly.reset_index(drop=True)[['Month_Year','Arrival Rooms','Individual Confirm','Individual Revenue']])  

    elif view_option == 'Weekly':
        st.write("Weekly View")
        st.write("Data from Sep2021 - Dec2021 is zero due to covid.")
        st.dataframe(data4_weekly.reset_index(drop=True)[['Week', 'Room Revenue', 'Rooms Sold']]) 
        st.dataframe(data5_weekly.reset_index(drop=True)[['Week', 'Arrival Rooms', 'Individual Confirm', 'Individual Revenue']])
       
    elif view_option == 'Yearly':
        st.write("Yearly View")
        st.write("Data from Sep2021 - Dec2021 is zero due to covid.")
        st.dataframe(data4_yearly.reset_index(drop=True)[['Year', 'Room Revenue','Rooms Sold']])  
        st.dataframe(data5_yearly.reset_index(drop=True)[['Year', 'Arrival Rooms', 'Individual Confirm', 'Individual Revenue']])

if __name__ == '__main__':
    main()
