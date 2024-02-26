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
}
selected_page = url_to_page.get(url_path)
custom_top_bar(selected_page)
# -----------------------------------------------
#FOR MONTH WISE OF EVERY FEATURE 
def plot_graph_revenue(dates, current_revenue, last_year_revenue):
    fig = go.Figure()

    # Plot this year revenue with markers only
    fig.add_trace(go.Scatter(x=dates, y=current_revenue, mode='markers', name='Current Year Revenue', marker=dict(color='blue'), textposition='bottom center'))
    
    # Plot last year revenue with markers only
    fig.add_trace(go.Scatter(x=dates, y=last_year_revenue, mode='markers', name='Last Year Revenue', marker=dict(color='red'), textposition='bottom center'))
     # Update layout for better interactivity and visual appearance
    fig.update_layout(
        xaxis=dict(title='Date'),
        yaxis=dict(title='Revenue (in Lakhs)',range=[0,2000000]),
        hovermode='x',
        showlegend=True,  # Adjust based on your preference
        legend_title='Legend',
        font=dict(family='Arial', size=14),
        height=530,  # Adjust the height of the plot
        width=530,   # Adjust the width of the plot
        margin=dict(l=20, r=20, t=40, b=20),
    )
    # Show the plot
    st.plotly_chart(fig)

def plot_graph_individual_revenue(dates, current_revenue):
    fig = go.Figure()

    # Plot this year revenue with markers only
    fig.add_trace(go.Scatter(x=dates, y=current_revenue, mode='markers', name='Current Year Revenue', marker=dict(color='blue'), textposition='bottom center'))
    
    # Plot last year revenue with markers only
    #fig.add_trace(go.Scatter(x=dates, y=last_year_revenue, mode='markers', name='Last Year Revenue', marker=dict(color='red'), textposition='bottom center'))
     # Update layout for better interactivity and visual appearance
    fig.update_layout(
        xaxis=dict(title='Date'),
        yaxis=dict(title='Revenue (in Lakhs)',range=[0,2000000]),
        hovermode='x',
        showlegend=True,  # Adjust based on your preference
        legend_title='Legend',
        font=dict(family='Arial', size=14),
        height=530,  # Adjust the height of the plot
        width=530,   # Adjust the width of the plot
        margin=dict(l=20, r=20, t=40, b=20),
    )
    # Show the plot
    st.plotly_chart(fig)


def plot_graph_room(dates, current_room_sold, last_year_room_sold):
    fig = go.Figure()

    # Plot this year revenue with markers only
    fig.add_trace(go.Scatter(x=dates, y=current_room_sold, mode='markers', name='Current Year Room Sold', marker=dict(color='blue'), textposition='bottom center'))
    
    # Plot last year revenue with markers only
    fig.add_trace(go.Scatter(x=dates, y=last_year_room_sold, mode='markers', name='Last Year Room Sold', marker=dict(color='red'), textposition='bottom center'))
     # Update layout for better interactivity and visual appearance
    fig.update_layout(
        xaxis=dict(title='Date'),
        
        yaxis=dict(title='Room Sold', range=[0,150]),
        hovermode='x',
        showlegend=True,  # Adjust based on your preference
        legend_title='Legend',
        font=dict(family='Arial', size=14),
        height=530,  # Adjust the height of the plot
        width=530,   # Adjust the width of the plot
        margin=dict(l=20, r=20, t=40, b=20),
    )
    # Show the plot
    st.plotly_chart(fig)


def plot_graph_arrival_room(dates, current_arrival_rooms):
    fig = go.Figure()

    # Plot current year arrival rooms with markers only
    fig.add_trace(go.Scatter(x=dates, y=current_arrival_rooms, mode='markers', name='Current Year Arrival Room ', marker=dict(color='blue'), textposition='bottom center'))
    
    # Update layout for better interactivity and visual appearance
    fig.update_layout(
        xaxis=dict(title='Date'),
        yaxis=dict(title='Arrival rooms', range=[0, 200]),
        hovermode='x',
        showlegend=True,
        legend_title='Legend',
        font=dict(family='Arial', size=14),
        height=530,
        width=530,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Show the plot
    st.plotly_chart(fig)


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

    #MONTH WISE ROOM REVENUE AND ROOM SOLD
    st.subheader("Graphs for different attributes month wise")
  
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
    #SELCT MONTH AND YEAR
    selected_month = st.selectbox('Select Month', range(1, 13), format_func=lambda x: calendar.month_name[x])
    years = list(range(2021, 2025))
    current_year = st.selectbox('Select current year:', years)
    previous_year = st.selectbox('Select previous year:', years)

    #FOR ROOM REVENUE AND ROOM SOLD
    current_year_data4 = data4[(data4['Business Date'].dt.month == selected_month) & (data4['Business Date'].dt.year == current_year)]
    previous_year_data4 = data4[(data4['Business Date'].dt.month == selected_month) & (data4['Business Date'].dt.year == previous_year)]
    current_year_revenue = current_year_data4['Room Revenue']
    previous_year_revenue = previous_year_data4['Room Revenue']
    current_room_sold = current_year_data4['Rooms Sold']
    previous_year_room_sold = previous_year_data4['Rooms Sold']
    dates = current_year_data4['Business Date']

    #FOR PLOTTING GRAPH
    st.subheader("Room Revenue Comparison")
    col1,col2 = st.columns(2)
    with col1:
        plot_graph_revenue(dates, current_year_revenue,previous_year_revenue)
   
    st.subheader("Room Sold Comparison")
    col3,col4 = st.columns(2)
    with col3:
        plot_graph_room(dates, current_room_sold, previous_year_room_sold)

    #FOR ARRIVAL ROOMS
    #selected_month1 = st.selectbox('Select Month', range(9, 13), format_func=lambda x: calendar.month_name[x])
    data5['Business Date'] = pd.to_datetime(data5['Business Date'])
    #selected_year1 = 2023
    current_year_data5 = data5[(data5['Business Date'].dt.month == selected_month) & (data5['Business Date'].dt.year == current_year)]
    current_year_Arrival_rooms = current_year_data5['Arrival Rooms']
    current_year_Individual_Confirm = current_year_data5['Individual Confirm']
    current_year_Individual_Revenue = current_year_data5['Individual Revenue']


    st.subheader("Arrival Room  Comparison")
    col5,col6 = st.columns(2)
    with col5:
        plot_graph_arrival_room(dates, current_year_Arrival_rooms)

    st.subheader("Individual Confirm  Comparison")
    col5,col6 = st.columns(2)
    with col5:
        plot_graph_arrival_room(dates, current_year_Individual_Confirm)

    st.subheader("Individual Revenue  Comparison")
    col5,col6 = st.columns(2)
    with col5:
        plot_graph_individual_revenue(dates, current_year_Individual_Revenue)

    
   
    #---------------------------------------------------------------------------
   #YEARLY, MONTH, DAILY AND WEEKLY VIEW
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
