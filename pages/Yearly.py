import base64
import os
from io import BytesIO
#from streamlit_extras.switch_page_button import switch_page
from statistics import mean
from sklearn.metrics import mean_squared_error 
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

overall_accuracy_for_7_days = []
overall_accuracy_for_14_days = []
overall_accuracy_for_21_days = []

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
    selected_page = selected_page or "Yearly"
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
            <a style="color: {'red' if selected_page == 'Yearly' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Yearly' else 'none'}" href="/Yearly" target="_self">Yearly</a>
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
    "/Yearly": "Yearly"
}
selected_page = url_to_page.get(url_path)
custom_top_bar(selected_page)
# -----------------------------------------------

def plot_graph_with_error(actual_dates, actual_revenue, predicted_revenue, title,range1):
    # Calculate day-to-day APE
    daily_ape = calculate_day_to_day_ape(actual_revenue, predicted_revenue)

    # Create figure and primary axis
    fig = go.Figure()
    
    # Plot actual revenue
    fig.add_trace(go.Scatter(x=actual_dates, y=actual_revenue, mode='lines+markers',
                             name='Actual', line=dict(color='blue')))
    #yaxis=dict(title='Revenue (in Lakhs)', range=[100000,2000000])
    # Plot predicted revenue
    fig.add_trace(go.Scatter(x=actual_dates, y=predicted_revenue, mode='lines+markers',
                             name='Predicted', line=dict(color='red')))
    
    # Add secondary axis for the error rate
    fig.add_trace(go.Scatter(x=actual_dates, y=daily_ape, mode='lines+markers',
                             name='Error Rate (%)', yaxis='y2', line=dict(color='green')))
    
    # Layout adjustments
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        #yaxis=dict(title='Revenue'),
        yaxis=dict(title='Revenue (in Lakhs)', range=range1),
        yaxis2=dict(title='Error Rate (%)', overlaying='y', side='right', range=[0, 100]),  # Secondary y-axis for error rate
        legend=dict(x=0.01, y=0.99, bordercolor='Black', borderwidth=1)
    )
    
    # Plot the figure in Streamlit
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
def calculate_day_to_day_ape(actual, predicted):
    actual, predicted = np.array(actual), np.array(predicted)
    return np.abs((actual - predicted) / actual) * 100
# ---------------------------------------------------------------------
def calculate_mape(actual, predicted):
    actual, predicted = np.array(actual), np.array(predicted)
    mask = actual != 0
    mape = (np.abs(actual - predicted) / actual)[mask].mean() * 100
    return mape
#---------------------------------------------------------------------
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
def evaluation_metrics(actual,predicted):
    tp_for_10_days = 0
    tn_for_10_days = 0
    fp_for_10_days = 0
    fn_for_10_days = 0
    for i,j in zip(actual,predicted):
        c = i-j
        c = abs(i-j)
        c = c*100/i
        c  = 100-c
        c= int(c)
        if i <j:
            if c>80 and c<100:
                tp_for_10_days +=1
            elif c<80:
                fp_for_10_days+=1
        elif  i>j:
            if  c>80 and c<100:
                tn_for_10_days +=1
            elif c<80:
                fn_for_10_days+=1

    sensitivity = tp_for_10_days / (tp_for_10_days + fn_for_10_days) if (tp_for_10_days + fn_for_10_days) >0 else 0
    specificity = tn_for_10_days / (tn_for_10_days + fp_for_10_days) if (tn_for_10_days + fp_for_10_days) > 0 else 0
    precision = tp_for_10_days / (tp_for_10_days + fp_for_10_days) if (tp_for_10_days + fp_for_10_days) > 0 else 0
    
    return sensitivity,specificity,precision





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
    import revenue as rev
    with col1:
        result, merged_data = rev.prophet()
        for i in range(0,9):
            x = i*10
            y = x+10
            result1 = result.iloc[x:y]
            plot_graph_with_error(result1['Date'],result1['Actual'],result1['Predicted'],"Room Revenue Prediction",(100000,2000000))
            st.write(f"Accuracy :{round(mean(result1['Accuracy'])*100)}%")
            st.write(f"MAE:{round(mean_absolute_error(result1['Actual'],result1['Predicted']))}")
            st.write(f"MAPE:{round(calculate_mape(result1['Actual'],result1['Predicted']))}%")
            st.write(f"MSE:{round(mean_squared_error(result1['Actual'],result1['Predicted']))}%")
            st.write(f"Sensitivity: {evaluation_metrics(result1['Actual'],result1['Predicted'])[0]}")
            st.write(f"Specificity: {evaluation_metrics(result1['Actual'],result1['Predicted'])[1]}")
            st.write(f"Precision: {evaluation_metrics(result1['Actual'],result1['Predicted'])[2]}")
    with col1:
        plot_month_data(merged_data)

    #ROOMS SOLD
    st.subheader("Predicted vs Actual ROOMS SOLD")
    col3,col4 = st.columns(2)
    import room_sold as rooom
    with col3:
        result, merged_data = rooom.prophet()
        for i in range(0,9):
            x = i*10
            y = x+10
            result1 = result.iloc[x:y]
            plot_graph_with_error(result1['Date'],result1['Actual'],result1['Predicted'],"Room Sold Prediction",(0,150))
            st.write(f"Accuracy :{round(mean(result1['Accuracy'])*100)}%")
            st.write(f"MAE:{round(mean_absolute_error(result1['Actual'],result1['Predicted']))}")
            st.write(f"MAPE:{round(calculate_mape(result1['Actual'],result1['Predicted']))}%")
            st.write(f"MSE:{round(mean_squared_error(result1['Actual'],result1['Predicted']))}%")
            st.write(f"Sensitivity: {evaluation_metrics(result1['Actual'],result1['Predicted'])[0]}")
            st.write(f"Specificity: {evaluation_metrics(result1['Actual'],result1['Predicted'])[1]}")
            st.write(f"Precision: {evaluation_metrics(result1['Actual'],result1['Predicted'])[2]}")

    with col3:
        plot_month_data(merged_data)
    

    #ARRIVAL ROOMS 
    st.subheader("Predicted vs Actual Arrival ROOMS")
    col5,col6 = st.columns(2)
    import Arrival as ars # type: ignore
    with col5:
        result, merged_data = ars.prophet()
        for i in range(0,8):
            x = i*10
            y = x+10
            result1 = result.iloc[x:y]
            plot_graph_with_error(result1['Date'],result1['Actual'],result1['Predicted'],"Arrival Rooms Prediction",(0,100))
            st.write(f"Accuracy :{round(mean(result1['Accuracy'])*100)}%")
            st.write(f"MAE:{round(mean_absolute_error(result1['Actual'],result1['Predicted']))}")
            st.write(f"MAPE:{round(calculate_mape(result1['Actual'],result1['Predicted']))}%")
            st.write(f"MSE:{round(mean_squared_error(result1['Actual'],result1['Predicted']))}%")
            st.write(f"Sensitivity: {evaluation_metrics(result1['Actual'],result1['Predicted'])[0]}")
            st.write(f"Specificity: {evaluation_metrics(result1['Actual'],result1['Predicted'])[1]}")
            st.write(f"Precision: {evaluation_metrics(result1['Actual'],result1['Predicted'])[2]}")
    
    with col5:
        plot_month_data_rooms(merged_data)

    #INDIVIDUAL CONFIRM
    st.subheader("Predicted vs Actual Individual Confirm")
    col7,col8 = st.columns(2)
    import Confirm as brs # type: ignore
    with col7:
        result,merged_data = brs.prophet()
        for i in range(0,8):
            x = i*10
            y = x+10
            result1 = result.iloc[x:y]
            plot_graph_with_error(result1['Date'],result1['Actual'],result1['Predicted'],"Individual Confirm Prediction",(0,140))
            st.write(f"Accuracy :{round(mean(result1['Accuracy'])*100)}%")
            st.write(f"MAE:{round(mean_absolute_error(result1['Actual'],result1['Predicted']))}")
            st.write(f"MAPE:{round(calculate_mape(result1['Actual'],result1['Predicted']))}%")
            st.write(f"MSE:{round(mean_squared_error(result1['Actual'],result1['Predicted']))}%")
            st.write(f"Sensitivity: {evaluation_metrics(result1['Actual'],result1['Predicted'])[0]}")
            st.write(f"Specificity: {evaluation_metrics(result1['Actual'],result1['Predicted'])[1]}")
            st.write(f"Precision: {evaluation_metrics(result1['Actual'],result1['Predicted'])[2]}")
    with col7:
        plot_month_data_rooms(merged_data)

    #INDIVIDUAL REVENUE
    st.subheader("Predicted vs Actual Individual Revenue")
    col9,col10 = st.columns(2)
    import Individual_R as ISS # type: ignore
    with col9:
        result, merged_data = ISS.prophet()
        for i in range(0,8):
            x = i*10
            y = x+10
            result1 = result.iloc[x:y]
            plot_graph_with_error(result1['Date'],result1['Actual'],result1['Predicted'],"Individual Revenue Prediction",(0,1700000))
            st.write(f"Accuracy :{round(mean(result1['Accuracy'])*100)}%")
            st.write(f"MAE:{round(mean_absolute_error(result1['Actual'],result1['Predicted']))}")
            st.write(f"MAPE:{round(calculate_mape(result1['Actual'],result1['Predicted']))}%")
            st.write(f"MSE:{round(mean_squared_error(result1['Actual'],result1['Predicted']))}%")
            st.write(f"Sensitivity: {evaluation_metrics(result1['Actual'],result1['Predicted'])[0]}")
            st.write(f"Specificity: {evaluation_metrics(result1['Actual'],result1['Predicted'])[1]}")
            st.write(f"Precision: {evaluation_metrics(result1['Actual'],result1['Predicted'])[2]}")
    with col9:
        plot_month_data_rooms(merged_data)

if __name__ == '__main__':
    main()




