import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import plotly.express as px
import pymongo
import os
from CAL import perform
from prophet import Prophet
from prophet.plot import add_changepoints_to_plot
import altair as alt  
from sklearn.metrics import mean_absolute_error, mean_squared_error
from streamlit_extras.switch_page_button import switch_page
from statistics import mean
from io import BytesIO
import plotly.graph_objects as go
import base64


st.set_page_config(page_title="Revenue Forecasting", page_icon=":overview", layout="wide", initial_sidebar_state="collapsed")


def set_custom_styles():
    """
    Custom styles to hide Streamlit default elements and adjust margins.
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
}
selected_page = url_to_page.get(url_path)
custom_top_bar(selected_page)
# -----------------------------------------------

Actual_for_ALL_days = []
Predicted_for_ALL_days = []

connection_uri = "mongodb+srv://annu21312:6dPsrXPfhm19YxXl@hello.hes3iy5.mongodb.net/"
client = pymongo.MongoClient(connection_uri, serverSelectionTimeoutMS=30000)
database_name = "Revenue_Forecasting"
db = client[database_name] 
collection5 = db["accuracy_revenue"]
cursor5 = collection5.find({})
data5 = pd.DataFrame(list(cursor5))
train_data = data5.iloc[:760]
test_data_for_next_7_days = data5.iloc[760:767]
test_data_for_next_14_days = data5.iloc[767:774]
test_data_for_next_21_days = data5.iloc[774:781]


#FOR 1st 7 DAYS(1-7)
model = Prophet(
                        changepoint_prior_scale= 0.3,
                        #holidays_prior_scale = 0.8,
                        n_changepoints = 500,
                        seasonality_mode = 'multiplicative',
                        weekly_seasonality=True,
                        daily_seasonality = True,
                        yearly_seasonality = True,
                        interval_width=0.8)
model.fit(train_data)
future_for_7_days = model.make_future_dataframe(periods=7, freq='D', include_history=False)
forecast = model.predict(future_for_7_days)
next_7_days = forecast.tail(7)
Actual_for_7_days =  []
Predicted_for_7_days = []
Accuracy_for_7_days = []
for i,j in zip(list(test_data_for_next_7_days['y'].tail(7)),list(next_7_days['yhat'])):
    i= int(i)
    j = int(j)
    Actual_for_7_days.append(i)
    Predicted_for_7_days.append(j)

tp_for_7_days = 0
fn_for_7_days = 0
for i,j in zip(Actual_for_7_days,Predicted_for_7_days):
    c = abs(i-j)
    c = c*100/i
    c  = 100-c
    c= int(c)
    if c > 90:
            tp_for_7_days+=1
    else:
            fn_for_7_days+=1
    Accuracy_for_7_days.append(c)

#FOR next 7 DAYS (8-14)
model1 = Prophet(
                      changepoint_prior_scale= 0.9,
                      holidays_prior_scale = 0.4,
                      n_changepoints = 400,
                      seasonality_mode = 'additive',
                      weekly_seasonality=True,
                      daily_seasonality = True,
                      yearly_seasonality = True,
                      interval_width=0.5)
model1.fit(train_data)
future_for_14_days = model1.make_future_dataframe(periods=14, freq='D', include_history=False)
forecast1 = model1.predict(future_for_14_days)
next_14_days = forecast1.tail(7)
Actual_for_14_days =  []
Predicted_for_14_days = []
Accuracy_for_14_days = []
for i,j in zip(list(test_data_for_next_14_days['y'].tail(7)),list(next_14_days['yhat'])):
   
    i= int(i)
    j = int(j)
    Actual_for_14_days.append(i)
    Predicted_for_14_days.append(j)
tp_for_14_days = 0
fn_for_14_days = 0
for i,j in zip(Actual_for_14_days,Predicted_for_14_days):
    c = abs(i-j)
    c = c*100/i
    c  = 100-c
    c= int(c)
    if c >90:
        tp_for_14_days += 1
    else:
        fn_for_14_days+=1
    Accuracy_for_14_days.append(c)

# For the next 7 days(15-21 days)
model2 = Prophet(
                      changepoint_prior_scale= 0.1,
                      holidays_prior_scale = 0.4,
                      n_changepoints = 200,
                      seasonality_mode = 'multiplicative',
                      weekly_seasonality=True,
                      daily_seasonality = True,
                      yearly_seasonality = True,
                      interval_width=0.9)
model2.fit(train_data)
future_for_21_days = model2.make_future_dataframe(periods=21, freq='D', include_history=False)
forecast2 = model2.predict(future_for_21_days)
next_21_days = forecast2.tail(7)
Actual_for_21_days =  []
Predicted_for_21_days = []
Accuracy_for_21_days = []
for i,j in zip(list(test_data_for_next_21_days['y'].tail(7)),list(next_21_days['yhat'])):
    i= int(i)
    j = int(j)
    Actual_for_21_days.append(i)
    Predicted_for_21_days.append(j)
tp_for_21_days = 0
fn_for_21_days = 0
for i,j in zip(Actual_for_21_days,Predicted_for_21_days):
    c = abs(i-j)
    c = c*100/i
    c  = 100-c
    c= int(c)
    if c >90:
        tp_for_21_days +=1
    else:
        fn_for_21_days+=1
    Accuracy_for_21_days.append(c)

# Convert to datetime and extract year and month
data5['ds'] = pd.to_datetime(data5['ds'])
data5['Year'] = data5['ds'].dt.year
data5['Month'] = data5['ds'].dt.strftime('%B')  # Month in full name

# Set a custom order for months
month_order = [
    'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'
]

data5['Month'] = pd.Categorical(data5['Month'], categories=month_order, ordered=True)

# Separate data for each year
data_2022 = data5[data5['Year'] == 2022]
data_2023 = data5[data5['Year'] == 2023]

# Group by month and sum the revenues for each year
monthly_total_revenue_2022 = data_2022.groupby('Month')['y'].sum().reset_index()
monthly_total_revenue_2023 = data_2023.groupby('Month')['y'].sum().reset_index()

# Merge the data for 2022 and 2023
merged_data = pd.merge(monthly_total_revenue_2022, monthly_total_revenue_2023, on='Month', suffixes=('_2022', '_2023'))

sensitivity_values_for_7_days = tp_for_7_days/(tp_for_7_days + fn_for_7_days)
sensitivity_values_for_14_days = tp_for_14_days/(tp_for_14_days + fn_for_14_days)
sensitivity_values_for_21_days = tp_for_21_days/(tp_for_21_days + fn_for_21_days)

absolute_diff1 = np.abs(np.array(Predicted_for_7_days) - np.array(Actual_for_7_days))
mae1 = np.mean(absolute_diff1)
absolute_diff2 = np.abs(np.array(Predicted_for_14_days) - np.array(Actual_for_14_days))
mae2 = np.mean(absolute_diff2)
absolute_diff3 = np.abs(np.array(Predicted_for_21_days) - np.array(Actual_for_21_days))
mae3 = np.mean(absolute_diff3)

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

def plot_month_data():
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
    x=merged_data['Month'],
    y=merged_data['y_2023'],
    name='2023',
    marker_color='orange'
    ))
    
    # Update layout for better interactivity
    fig.update_layout(
    barmode='group',  # Display bars in groups
    title='Total Revenue for Each Month (2022-2023)',
    xaxis=dict(title='Month'),
    yaxis=dict(title='Total Revenue in Crore'),
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

collection6 = db["accuracy_room_sold"]
cursor6 = collection6.find({})
data6 = pd.DataFrame(list(cursor6))
data6  = data6[['Date', 'Rooms Sold']]
data6.columns = ['ds','y']
train_data_room_sales = data6.iloc[:237]
test_data_for_next_7_days_room_sales = data6.iloc[237:244]
test_data_for_next_14_days_room_sales = data6.iloc[245:252]
test_data_for_next_21_days_room_sales = data6.iloc[253:260]
data6['ds'] = pd.to_datetime(data6['ds'])

# Room sold for first 7 days(0-7)
model = Prophet(
                        changepoint_prior_scale= 0.9,
                        #holidays_prior_scale = 0.4,
                        #n_changepoints = 200,
                        #seasonality_mode = 'multiplicative',
                        weekly_seasonality=True,
                        daily_seasonality = True,
                        yearly_seasonality = False,
                )
model.fit(train_data_room_sales)
future_for_7_days_room_sales = model.make_future_dataframe(periods=7, freq='D', include_history=False)
forecast = model.predict(future_for_7_days_room_sales)
next_7_days_room_sales = forecast.tail(7)
Actual_for_7_days_room_sales =  []
Predicted_for_7_days_room_sales = []
Accuracy_for_7_days_room_sales = []
for i,j in zip(list(test_data_for_next_7_days_room_sales['y'].tail(10)),list(next_7_days_room_sales['yhat'])):
    i= int(i)
    j = int(j)
    Actual_for_7_days_room_sales.append(i)
    Predicted_for_7_days_room_sales.append(j)

for i,j in zip(Actual_for_7_days_room_sales,Predicted_for_7_days_room_sales):
    c = abs(i-j)
    c = (c*100)/i
    c  = 100-c
    c= int(c)
    Accuracy_for_7_days_room_sales.append(c)

# Convert to datetime and extract year and month
data6['ds'] = pd.to_datetime(data6['ds'])
data6['Year'] = data6['ds'].dt.year
data6['Month'] = data6['ds'].dt.strftime('%B')  # Month in full name

# Set a custom order for months
month_order = [
    'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'
]

data6['Month'] = pd.Categorical(data6['Month'], categories=month_order, ordered=True)

# Separate data for each year
data_2022 = data6[data6['Year'] == 2022]
data_2023 = data6[data6['Year'] == 2023]

# Group by month and sum the revenues for each year
monthly_total_room_sales_2022 = data_2022.groupby('Month')['y'].sum().reset_index()
monthly_total_room_sales_2023 = data_2023.groupby('Month')['y'].sum().reset_index()

# Merge the data for 2022 and 2023
merged_data_room_sales = pd.merge(monthly_total_room_sales_2022, monthly_total_room_sales_2023, on='Month', suffixes=('_2022', '_2023'))
    
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
    st.subheader("Predicted vs Actual Revenue")
    col1, col2 = st.columns(2)
    
    # Plot for 0-7 Days
    with col1:
        df_7_days = pd.DataFrame({'Date': test_data_for_next_7_days['ds'], 'Actual': Actual_for_7_days, 'Predicted': Predicted_for_7_days})
        # fig_7_days = px.line(df_7_days, x='Date', y=['Actual', 'Predicted'], title='Predicted vs Actual Revenue for 0-7 Days')
        plot_revenue(df_7_days['Date'], df_7_days['Actual'], df_7_days['Date'], df_7_days['Predicted'], 'For 0-07 Days')
        # st.plotly_chart(fig_7_days)
        st.write(f"Accuracy: {round(mean(Accuracy_for_7_days))}%")
        st.write(f"Sensitivity: {round(sensitivity_values_for_7_days,3)}")
        st.write(f"MAE: {round(mae1)}")

        df_7_days_room_sales = pd.DataFrame({'Date': test_data_for_next_7_days_room_sales['ds'], 'Actual': Actual_for_7_days_room_sales, 'Predicted': Predicted_for_7_days_room_sales})
        plot_revenue(df_7_days_room_sales['Date'], df_7_days_room_sales['Actual'], df_7_days_room_sales['Date'], df_7_days_room_sales['Predicted'], 'For 0-07 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_7_days_room_sales))}%")
        
        
        st.markdown("---")
        # #Conversion of dfs into excel files
        # revenue_df_7_days = pd.DataFrame({
        #     'Date': test_data_for_next_7_days['ds'].tail(7),
        #     'Actual_Revenue': Actual_for_7_days,
        #     'Predicted_Revenue': Predicted_for_7_days,
        #     'Accuracy_of_revenue': Accuracy_for_7_days,
        #})
    # Plot for 8-14 Days
    with col2:
        df_14_days = pd.DataFrame({'Date': next_14_days['ds'].tail(7), 'Actual': Actual_for_14_days, 'Predicted': Predicted_for_14_days})
        # fig_14_days = px.line(df_14_days, x='Date', y=['Actual', 'Predicted'], title='Predicted vs Actual Revenue for 8-14 Days')
        # st.plotly_chart(fig_14_days)
        plot_revenue(df_14_days['Date'], df_14_days['Actual'], df_14_days['Date'], df_14_days['Predicted'], 'For 8-14 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_14_days))}%")
        st.write(f"Sensitivity: {round(sensitivity_values_for_14_days,3)}")
        st.write(f"MAE: {round(mae2)}")
        st.markdown("---")
        # revenue_df_14_days = pd.DataFrame({
        #     'Date': next_14_days['ds'].tail(7),
        #     'Actual_Revenue': Actual_for_14_days,
        #     'Predicted_Revenue': Predicted_for_14_days,
        #     'Accuracy_of_revenue': Accuracy_for_14_days,
        # })
    # Plot for 15-21 Days
    with col1:
        df_21_days = pd.DataFrame({'Date': next_21_days['ds'].tail(7), 'Actual': Actual_for_21_days, 'Predicted': Predicted_for_21_days})
        # fig_21_days = px.line(df_21_days, x='Date', y=['Actual', 'Predicted'], title='Predicted vs Actual Revenue for 15-21 Days')
        # st.plotly_chart(fig_21_days)
        plot_revenue(df_21_days['Date'], df_21_days['Actual'], df_21_days['Date'], df_21_days['Predicted'], 'For 15-21 Days')

        st.write(f"Accuracy: {round(mean(Accuracy_for_21_days))}%")
        st.write(f"Sensitivity: {round(sensitivity_values_for_21_days,3)}")
        st.write(f"MAE: {round(mae3)}")
        st.markdown("---")
        # revenue_df_21_days = pd.DataFrame({
        #     'Date': next_21_days['ds'].tail(7),
        #     'Actual_Revenue': Actual_for_21_days,
        #     'Predicted_Revenue': Predicted_for_21_days,
        #     'Accuracy_of_revenue': Accuracy_for_21_days,
        # })

    #for MONTHLY
    with col1:
        plot_month_data()

    with col1:
        df_7_days_room_sales = pd.DataFrame({'Date': test_data_for_next_7_days_room_sales['ds'], 'Actual': Actual_for_7_days_room_sales, 'Predicted': Predicted_for_7_days_room_sales})
        plot_revenue(df_7_days_room_sales['Date'], df_7_days_room_sales['Actual'], df_7_days_room_sales['Date'], df_7_days_room_sales['Predicted'], 'For 0-07 Days')
        st.write(f"Accuracy: {round(mean(Accuracy_for_7_days_room_sales))}%")
    

    
    # st.subheader('Download Excel Files')

#     # Download links for Excel files
#     with BytesIO() as buffer:
#         with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
#             revenue_df_7_days.to_excel(writer, sheet_name='revenue_data_7_days', index=False)
#             revenue_df_14_days.to_excel(writer, sheet_name='revenue_data_14_days', index=False)
#             revenue_df_21_days.to_excel(writer, sheet_name='revenue_data_21_days', index=False)
#         buffer.seek(0)

#         st.markdown(get_excel_download_link(buffer, 'revenue_data_7_days.xlsx', 'Download revenue_data_07_days.xlsx'), unsafe_allow_html=True)
#         st.markdown(get_excel_download_link(buffer, 'revenue_data_14_days.xlsx', 'Download revenue_data_14_days.xlsx'), unsafe_allow_html=True)
#         st.markdown(get_excel_download_link(buffer, 'revenue_data_21_days.xlsx', 'Download revenue_data_21_days.xlsx'), unsafe_allow_html=True)

# # Function to generate a download link for the Excel file
# def get_excel_download_link(buffer, file_name, link_text):
#     buffer = buffer.read()
#     b64 = base64.b64encode(buffer).decode()
#     href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">{link_text}</a>'
#     return href

# ----------------------------------------------- 






# #ROOM SOLD FOR next 7 days(8-14)
# model1 = Prophet(changepoint_prior_scale=0.9,
#                 holidays_prior_scale = 0.4,
#                 #n_changepoints = 200,
#                 seasonality_mode = 'multiplicative',
#                 weekly_seasonality=True,
#                 daily_seasonality = True,
#                 yearly_seasonality = False,
#                 interval_width=0.95
#                      )
# model1.fit(train_data)
# future_for_14_days = model1.make_future_dataframe(periods=14, freq='D', include_history=False)
# forecast1 = model1.predict(future_for_14_days)
# next_14_days = forecast1.tail(7)
# Actual_for_14_days =  []
# Predicted_for_14_days = []
# Accuracy_for_14_days = []
# for i,j in zip(list(test_data_for_next_14_days['y'].tail(7)),list(next_14_days['yhat'])):
   
#     i= int(i)
#     j = int(j)
#     Actual_for_14_days.append(i)
#     Predicted_for_14_days.append(j)

# for i,j in zip(Actual_for_14_days,Predicted_for_14_days):
#     c = abs(i-j)
#     c = c*100/i
#     c  = 100-c
#     c= int(c)
#     Accuracy_for_14_days.append(c)

#ROOM SOLD FOR FOR 21 DAYS(15-21 days)
# model2 = Prophet(
#                         changepoint_prior_scale=0.3,  # Tweak this parameter based on your data
#                         yearly_seasonality=False,       # Add yearly seasonality
#                         weekly_seasonality=True, )
# model2.fit(train_data)
# future_for_21_days = model2.make_future_dataframe(periods=21, freq='D', include_history=False)
# forecast2 = model2.predict(future_for_21_days)
# next_21_days = forecast2.tail(7)
# Actual_for_21_days =  []
# Predicted_for_21_days = []
# Accuracy_for_21_days = []
# for i,j in zip(list(test_data_for_next_21_days['y'].tail(7)),list(next_21_days['yhat'])):
#     i= int(i)
#     j = int(j)
#     Actual_for_21_days.append(i)
#     Predicted_for_21_days.append(j)

# for i,j in zip(Actual_for_21_days,Predicted_for_21_days):
#     c = abs(i-j)
#     c = c*100/i
#     c  = 100-c
#     c= int(c)
#     Accuracy_for_21_days.append(c)
st.write("room_sales")


if __name__ == '__main__':
    main()
