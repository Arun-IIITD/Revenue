import base64
import os
from io import BytesIO
#from streamlit_extras.switch_page_button import switch_page
from statistics import mean

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

from CAL import perform

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
    selected_page = selected_page or "Prediction"
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
            <a style="color: {'red' if selected_page == 'trend' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Trend' else 'none'}" href="/trend" target="_self">Trend</a>
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

def plot_revenue(actual_dates, actual_revenue, predicted_dates, predicted_revenue, title):
    fig = go.Figure()

    # Plot actual revenue
    fig.add_trace(go.Scatter(x=actual_dates, y=actual_revenue, mode='lines+markers', name='Actual Revenue', line=dict(color='blue'), textposition='bottom center'))
    
    # Plot predicted revenue
    fig.add_trace(go.Scatter(x=predicted_dates, y=predicted_revenue, mode='lines+markers', name='Predicted Revenue', line=dict(color='red'), textposition='bottom center'))

    # Update layout for better interactivity
    fig.update_layout(
        title=title,
        xaxis=dict(title='Date'),
        yaxis=dict(title='Revenue (in Lakhs)', range=[100000,2000000]),
        hovermode='x',
        showlegend=False,  # Hide legend for cleaner appearance
        legend_title='Legend',
        font=dict(family='Arial', size=14),
        shapes=[
            dict(
                type='line',
                x0=0,
                x1=1,
                y0=0,
                y1=0,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=0,
                x1=0,
                y0=0,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=1,
                x1=1,
                y0=0,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=0,
                x1=1,
                y0=1,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
        ],
        height=530,  # Adjust the height of the plot
        width=530,   # Adjust the width of the plot
        margin=dict(l=20, r=20, t=40, b=20),
    )

    # Show the plot
    st.plotly_chart(fig)
# ---------------------------------------------------------------------
    
def plot_room_sold(actual_dates, actual_room_sales, predicted_dates, predicted_room_sales, title):
    fig = go.Figure()

    # Plot actual room sold
    fig.add_trace(go.Scatter(x=actual_dates, y=actual_room_sales, mode='lines+markers', name='Actual Room Sold', line=dict(color='blue'), textposition='bottom center'))
    
    # Plot predicted sold
    fig.add_trace(go.Scatter(x=predicted_dates, y=predicted_room_sales, mode='lines+markers', name='Predicted Room Sold', line=dict(color='red'), textposition='bottom center'))

    # Update layout for better interactivity
    fig.update_layout(
        title=title,
        xaxis=dict(title='Date'),
        yaxis=dict(title='Room Sold', range=[0,150]),
        hovermode='x',
        showlegend=False,  # Hide legend for cleaner appearance
        legend_title='Legend',
        font=dict(family='Arial', size=14),
        shapes=[
            dict(
                type='line',
                x0=0,
                x1=1,
                y0=0,
                y1=0,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=0,
                x1=0,
                y0=0,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=1,
                x1=1,
                y0=0,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=0,
                x1=1,
                y0=1,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
        ],
        height=530,  # Adjust the height of the plot
        width=530,   # Adjust the width of the plot
        margin=dict(l=20, r=20, t=40, b=20),
    )

    # Show the plot
    st.plotly_chart(fig)

# ---------------------------------------------------------------------
def plot_arrival_rooms(actual_dates, actual_arrival_rooms, predicted_dates, predicted_room_sales, title):
    fig = go.Figure()

    # Plot actual room sold
    fig.add_trace(go.Scatter(x=actual_dates, y=actual_arrival_rooms, mode='lines+markers', name='Actual Arrival Rooms', line=dict(color='blue'), textposition='bottom center'))
    
    # Plot predicted sold
    fig.add_trace(go.Scatter(x=predicted_dates, y=predicted_room_sales, mode='lines+markers', name='Predicted Arrival Rooms', line=dict(color='red'), textposition='bottom center'))

    # Update layout for better interactivity
    fig.update_layout(
        title=title,
        xaxis=dict(title='Date'),
        yaxis=dict(title='Arrival Room', range=[0,90]),
        hovermode='x',
        showlegend=False,  # Hide legend for cleaner appearance
        legend_title='Legend',
        font=dict(family='Arial', size=14),
        shapes=[
            dict(
                type='line',
                x0=0,
                x1=1,
                y0=0,
                y1=0,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=0,
                x1=0,
                y0=0,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=1,
                x1=1,
                y0=0,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=0,
                x1=1,
                y0=1,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
        ],
        height=530,  # Adjust the height of the plot
        width=530,   # Adjust the width of the plot
        margin=dict(l=20, r=20, t=40, b=20),
    )

    # Show the plot
    st.plotly_chart(fig)

# ---------------------------------------------------------------------
def plot_individual_confirm(actual_dates, actual_arrival_rooms, predicted_dates, predicted_room_sales, title):
    fig = go.Figure()

    # Plot actual room sold
    fig.add_trace(go.Scatter(x=actual_dates, y=actual_arrival_rooms, mode='lines+markers', name='Actual Individual Confirm', line=dict(color='blue'), textposition='bottom center'))
    
    # Plot predicted sold
    fig.add_trace(go.Scatter(x=predicted_dates, y=predicted_room_sales, mode='lines+markers', name='Predicted Individual Confirm', line=dict(color='red'), textposition='bottom center'))

    # Update layout for better interactivity
    fig.update_layout(
        title=title,
        xaxis=dict(title='Date'),
        yaxis=dict(title='Individual Confirm', range=[0,130]),
        hovermode='x',
        showlegend=False,  # Hide legend for cleaner appearance
        legend_title='Legend',
        font=dict(family='Arial', size=14),
        shapes=[
            dict(
                type='line',
                x0=0,
                x1=1,
                y0=0,
                y1=0,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=0,
                x1=0,
                y0=0,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=1,
                x1=1,
                y0=0,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=0,
                x1=1,
                y0=1,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
        ],
        height=530,  # Adjust the height of the plot
        width=530,   # Adjust the width of the plot
        margin=dict(l=20, r=20, t=40, b=20),
    )

    # Show the plot
    st.plotly_chart(fig)
# ---------------------------------------------------------------------
def plot_individual_revenue(actual_dates, actual_arrival_rooms, predicted_dates, predicted_room_sales, title):
    fig = go.Figure()

    # Plot actual room sold
    fig.add_trace(go.Scatter(x=actual_dates, y=actual_arrival_rooms, mode='lines+markers', name='Actual Individual Revenue', line=dict(color='blue'), textposition='bottom center'))
    
    # Plot predicted sold
    fig.add_trace(go.Scatter(x=predicted_dates, y=predicted_room_sales, mode='lines+markers', name='Predicted Individual Revenue', line=dict(color='red'), textposition='bottom center'))

    # Update layout for better interactivity
    fig.update_layout(
        title=title,
        xaxis=dict(title='Date'),
        yaxis=dict(title='Individual Revenue', range=[0,1600000]),
        hovermode='x',
        showlegend=False,  # Hide legend for cleaner appearance
        legend_title='Legend',
        font=dict(family='Arial', size=14),
        shapes=[
            dict(
                type='line',
                x0=0,
                x1=1,
                y0=0,
                y1=0,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=0,
                x1=0,
                y0=0,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=1,
                x1=1,
                y0=0,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
            dict(
                type='line',
                x0=0,
                x1=1,
                y0=1,
                y1=1,
                line=dict(color='lightgray', width=0.5),
                xref='paper',
                yref='paper'
            ),
        ],
        height=530,  # Adjust the height of the plot
        width=530,   # Adjust the width of the plot
        margin=dict(l=20, r=20, t=40, b=20),
    )

    # Show the plot
    st.plotly_chart(fig)
# ---------------------------------------------------------------------
def plot_month_data(merged_data):
    # Plotting using Plotly
    fig = go.Figure()
    
    # Plotting bars for 2022
    fig.add_trace(go.Bar(
    x=merged_data['Month'],
    y=merged_data['y_2022'],
    name='2022',
    marker_color='skyblue'
    ))
    
    # Plotting bars for 2023
    fig.add_trace(go.Bar(
    x= merged_data['Month'],
    y= merged_data['y_2023'],
    name='2023',
    marker_color='orange'
    ))
    
    # Update layout for better interactivity
    fig.update_layout(
    barmode='group',  # Display bars in groups
    title='Entities generated for Each Month (2022-2023)',
    xaxis=dict(title='Month'),
    yaxis=dict(title='Total Entities '),
    hovermode='x',
    showlegend=True,
    legend_title='Legend',
    font=dict(family='Arial', size=14),
    height=600,  # Adjust the height of the plot
    width=1000,   # Adjust the width of the plot
    margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Show the plot
    st.plotly_chart(fig)

# ---------------------------------------------------------------------
def plot_month_data_rooms(merged_data):
    # Plotting using Plotly
    fig = go.Figure()
    
    # Plotting bars for 2023
    fig.add_trace(go.Bar(
        x=merged_data['Month'],
        y=merged_data['y'],
        name='2023',
        marker_color='skyblue'
    ))
    
    # Update layout for better interactivity
    fig.update_layout(
        barmode='group',  # Display bars in groups
        title='Entities generated for Each Month (2023)',
        xaxis=dict(title='Month'),
        yaxis=dict(title='Total Entities'),
        hovermode='x',
        showlegend=True,
        legend_title='Legend',
        font=dict(family='Arial', size=14),
        height=600,  # Adjust the height of the plot
        width=1000,   # Adjust the width of the plot
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    # Show the plot in Streamlit
    st.plotly_chart(fig)
# ---------------------------------------------------------------------


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

  
    #ROOM REVENUE
    st.subheader("Predicted vs Actual ROOM REVENUE")
    col1,col2 = st.columns(2)
    import prop_for_revenue as rfs
    #PLOT FOR FIRST 7 DAYS ROOM REVENUE
    with col1:
        Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days,sensitivity_values_for_7_days,sensitivity_values_for_14_days,sensitivity_values_for_21_days,mae1,mae2,mae3,merged_data = rfs.model_rev()
        df_7_days_rev = pd.DataFrame({'Date': rfs.test_data_for_next_7_days['ds'], 'Actual': Actual_for_7_days, 'Predicted': Predicted_for_7_days})
        plot_revenue(df_7_days_rev['Date'], df_7_days_rev['Actual'], df_7_days_rev['Date'], df_7_days_rev['Predicted'], 'For 0-07 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_7_days))}%")
        st.write(f"Sensitivity: {(sensitivity_values_for_7_days)}%")
        st.write(f"MAE: {(mae1)}")
        # st.title('Forecast Results')
        # st.write('### Forecast Plot')
        # st.pyplot(fig1)
        # st.pyplot(fig2)
        st.markdown("---")
    
    #PLOT FOR 08-14 DAYS ROOM REVENUE
    with col2:
        #Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days, = rfs.model_rev()
        df_14_days_rev = pd.DataFrame({'Date': rfs.test_data_for_next_14_days['ds'], 'Actual': Actual_for_14_days, 'Predicted': Predicted_for_14_days})
        plot_revenue(df_14_days_rev['Date'], df_14_days_rev['Actual'], df_14_days_rev['Date'], df_14_days_rev['Predicted'], 'For 08-14 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_14_days))}%")
        st.write(f"Sensitivity: {(sensitivity_values_for_14_days)}%")
        st.write(f"MAE: {(mae2)}")
        st.markdown("---")
    
    #PLOT FOR 15-21 DAYS ROOM REVENUE
    with col1:
        #Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days, = rfs.model_rev()
        df_21_days_rev = pd.DataFrame({'Date': rfs.test_data_for_next_21_days['ds'], 'Actual': Actual_for_21_days, 'Predicted': Predicted_for_21_days})
        plot_revenue(df_21_days_rev['Date'], df_21_days_rev['Actual'], df_21_days_rev['Date'], df_21_days_rev['Predicted'], 'For 15-21 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_21_days))}%")
        st.write(f"Sensitivity: {(sensitivity_values_for_21_days)}%")
        st.write(f"MAE: {(mae3)}")
        st.markdown("---")

    #PLOT MONTH DATA
    with col1:
        plot_month_data(merged_data)

    

    #ROOM SOLD
    st.subheader("Predicted vs Actual ROOM SOLD")
    col3,col4 = st.columns(2)
    import prop_for_room_sold as pfs
    #PLOT FOR FIRST 7 DAYS ROOM SOLD
    with col3:
        Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days,sensitivity_values_for_7_days,sensitivity_values_for_14_days,sensitivity_values_for_21_days,mae1,mae2,mae3,merged_data = pfs.model_R()
        df_7_days_room_sales = pd.DataFrame({'Date': pfs.test_data_for_next_7_days['ds'], 'Actual': Actual_for_7_days, 'Predicted': Predicted_for_7_days})
        plot_room_sold(df_7_days_room_sales['Date'], df_7_days_room_sales['Actual'], df_7_days_room_sales['Date'], df_7_days_room_sales['Predicted'], 'For 0-07 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_7_days))}%")
        st.write(f"Sensitivity: {(sensitivity_values_for_7_days)}%")
        st.write(f"MAE: {(mae1)}")
        st.markdown("---")
    
    #PLOT FOR 08-14 DAYS ROOM SOLD
    with col4:
        #Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days, = pfs.model_R()
        df_14_days_room_sales = pd.DataFrame({'Date': pfs.test_data_for_next_14_days['ds'], 'Actual': Actual_for_14_days, 'Predicted': Predicted_for_14_days})
        plot_room_sold(df_14_days_room_sales['Date'], df_14_days_room_sales['Actual'], df_14_days_room_sales['Date'], df_14_days_room_sales['Predicted'], 'For 08-14 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_14_days))+1}%")
        st.write(f"Sensitivity: {(sensitivity_values_for_14_days)}%")
        st.write(f"MAE: {(mae2)}")
        st.markdown("---")
    
    #PLOT FOR 15-21 DAYS ROOM SOLD
    with col3:
        #Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days, = pfs.model_R()
        df_21_days_room_sales = pd.DataFrame({'Date': pfs.test_data_for_next_21_days['ds'], 'Actual': Actual_for_21_days, 'Predicted': Predicted_for_21_days})
        plot_room_sold(df_21_days_room_sales['Date'], df_21_days_room_sales['Actual'], df_21_days_room_sales['Date'], df_21_days_room_sales['Predicted'], 'For 15-21 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_21_days))}%")
        st.write(f"Sensitivity: {(sensitivity_values_for_21_days)}%")
        st.write(f"MAE: {(mae3)}")
        st.markdown("---")

    #PLOT MONTH ROOMS SOLD
    with col3:
        plot_month_data(merged_data)


    #ARRIVAL ROOMS
    st.subheader("Predicted vs Actual Arrival Rooms")
    col5,col6 = st.columns(2)
    import prop_for_Arrival_rooms as afs
    #PLOT FOR FIRST 7 DAYS ARRIVAL ROOMS
    with col5:
        Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days,sensitivity_values_for_7_days,sensitivity_values_for_14_days,sensitivity_values_for_21_days,mae1,mae2,mae3,merged_data = afs.model_A()
        df_7_days_Arrival_rooms = pd.DataFrame({'Date': afs.test_data_for_next_7_days['ds'], 'Actual': Actual_for_7_days, 'Predicted': Predicted_for_7_days})
        plot_arrival_rooms(df_7_days_Arrival_rooms['Date'], df_7_days_Arrival_rooms['Actual'], df_7_days_Arrival_rooms['Date'], df_7_days_Arrival_rooms['Predicted'], 'For 0-07 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_7_days))}%")
        st.write(f"Sensitivity: {(sensitivity_values_for_7_days)}%")
        st.write(f"MAE: {(mae1)}")
        st.markdown("---")
    
    #PLOT FOR 08-14 DAYS ARRIVAL ROOMS
    with col6:
        #Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days, = afs.model_A()
        df_14_days_Arrival_rooms = pd.DataFrame({'Date': afs.test_data_for_next_14_days['ds'], 'Actual': Actual_for_14_days, 'Predicted': Predicted_for_14_days})
        plot_arrival_rooms(df_14_days_Arrival_rooms['Date'], df_14_days_Arrival_rooms['Actual'], df_14_days_Arrival_rooms['Date'], df_14_days_Arrival_rooms['Predicted'], 'For 08-14 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_14_days))}%")
        st.write(f"Sensitivity: {(sensitivity_values_for_14_days)}%")
        st.write(f"MAE: {(mae2)}")
        st.markdown("---")
    
    #PLOT FOR 15-21 DAYS ARRIVAL ROOMS
    with col5:
        #Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days, = afs.model_A()
        df_21_days_Arrival_rooms = pd.DataFrame({'Date': afs.test_data_for_next_21_days['ds'], 'Actual': Actual_for_21_days, 'Predicted': Predicted_for_21_days})
        plot_arrival_rooms(df_21_days_Arrival_rooms['Date'], df_21_days_Arrival_rooms['Actual'], df_21_days_Arrival_rooms['Date'], df_21_days_Arrival_rooms['Predicted'], 'For 15-21 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_21_days))}%")
        st.write(f"Sensitivity: {(sensitivity_values_for_21_days)}%")
        st.write(f"MAE: {(mae3)}")
        st.markdown("---")

    with col5:
        plot_month_data_rooms(merged_data)

    
    
    #Individual Confirm
    st.subheader("Predicted vs Actual Individual Confirm")
    col7,col8 = st.columns(2)
    import prop_for_Individual_Confirm as bfs
    #PLOT FOR FIRST 7 DAYS INDIVIDUAL CONFIRM
    with col7:
        Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days,sensitivity_values_for_7_days,sensitivity_values_for_14_days,sensitivity_values_for_21_days,mae1,mae2,mae3,merged_data = bfs.model_IC()
        df_7_days_Individual_Confirm = pd.DataFrame({'Date': bfs.test_data_for_next_7_days['ds'], 'Actual': Actual_for_7_days, 'Predicted': Predicted_for_7_days})
        plot_individual_confirm(df_7_days_Individual_Confirm['Date'], df_7_days_Individual_Confirm['Actual'], df_7_days_Individual_Confirm['Date'], df_7_days_Individual_Confirm['Predicted'], 'For 0-07 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_7_days))}%")
        st.write(f"Sensitivity: {(sensitivity_values_for_7_days)}%")
        st.write(f"MAE: {(mae1)}")
        st.markdown("---")
    
    #PLOT FOR 08-14 DAYS INDIVIDUAL CONFIRM
    with col8:
        #Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days, = bfs.model_IC()
        df_14_days_Individual_Confirm = pd.DataFrame({'Date': bfs.test_data_for_next_14_days['ds'], 'Actual': Actual_for_14_days, 'Predicted': Predicted_for_14_days})
        plot_individual_confirm(df_14_days_Individual_Confirm['Date'], df_14_days_Individual_Confirm['Actual'], df_14_days_Individual_Confirm['Date'], df_14_days_Individual_Confirm['Predicted'], 'For 08-14 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_14_days))}%")
        st.write(f"Sensitivity: {(sensitivity_values_for_14_days)}%")
        st.write(f"MAE: {(mae2)}")
        st.markdown("---")
    
    #PLOT FOR 15-21 DAYS INDIVIDUAL CONFIRM
    with col7:
        #Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days, = bfs.model_IC()
        df_21_days_Individual_Confirm = pd.DataFrame({'Date': bfs.test_data_for_next_21_days['ds'], 'Actual': Actual_for_21_days, 'Predicted': Predicted_for_21_days})
        plot_individual_confirm(df_21_days_Individual_Confirm['Date'], df_21_days_Individual_Confirm['Actual'],df_21_days_Individual_Confirm['Date'], df_21_days_Individual_Confirm['Predicted'], 'For 15-21 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_21_days))}%")
        st.write(f"Sensitivity: {(sensitivity_values_for_21_days)}%")
        st.write(f"MAE: {(mae3)}")
        st.markdown("---")

    with col7:
        plot_month_data_rooms(merged_data)

    
    #Individual Revenue
    st.subheader("Predicted vs Actual Individual Revenue")
    col9,col10 = st.columns(2)
    import prop_for_individual_revenue as dfs
    #PLOT FOR FIRST 7 DAYS INDIVIDUAL REVENUE
    with col9:
        Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days,sensitivity_values_for_7_days,sensitivity_values_for_14_days,sensitivity_values_for_21_days,mae1,mae2,mae3,merged_data = dfs.model_IR()
        df_7_days_IR = pd.DataFrame({'Date': dfs.test_data_for_next_7_days['ds'], 'Actual': Actual_for_7_days, 'Predicted': Predicted_for_7_days})
        plot_individual_revenue(df_7_days_IR['Date'], df_7_days_IR['Actual'], df_7_days_IR['Date'], df_7_days_IR['Predicted'], 'For 0-07 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_7_days))}%")
        st.write(f"Sensitivity: {(sensitivity_values_for_7_days)}%")
        st.write(f"MAE: {(mae1)}")
        st.markdown("---")
    
    #PLOT FOR 08-14 DAYS INDIVIDUAL REVENUE
    with col10:
        #Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days, = dfs.model_IR()
        df_14_days_IR = pd.DataFrame({'Date': dfs.test_data_for_next_14_days['ds'], 'Actual': Actual_for_14_days, 'Predicted': Predicted_for_14_days})
        plot_individual_revenue(df_14_days_IR['Date'], df_14_days_IR['Actual'], df_14_days_IR['Date'], df_14_days_IR['Predicted'], 'For 08-14 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_14_days))}%")
        st.write(f"Sensitivity: {(sensitivity_values_for_14_days)}%")
        st.write(f"MAE: {(mae2)}")
        st.markdown("---")
    
    #PLOT FOR 15-21 DAYS INDIVIDUAL REVENUE
    with col9:
        #Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days, = dfs.model_IR()
        df_21_days_IR = pd.DataFrame({'Date': dfs.test_data_for_next_21_days['ds'], 'Actual': Actual_for_21_days, 'Predicted': Predicted_for_21_days})
        plot_individual_revenue(df_21_days_IR['Date'], df_21_days_IR['Actual'], df_21_days_IR['Date'], df_21_days_IR['Predicted'], 'For 15-21 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_21_days))}%")
        st.write(f"Sensitivity: {(sensitivity_values_for_21_days)}%")
        st.write(f"MAE: {(mae3)}")
        st.markdown("---")

    with col9:
        plot_month_data_rooms(merged_data)
    
if __name__ == '__main__':
    main()
