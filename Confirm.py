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
data1 =  data4[['Business Date','Room Revenue','Rooms Sold']]
data2 = data5[['Business Date','Room Revenue','Rooms Sold','Arrival Rooms','Individual Revenue','Individual Confirm']]
data = pd.concat([data1,data2],ignore_index=True)
data4 = data[['Business Date','Individual Confirm']]
data4.columns = ['ds','y'] 
data4['ds'] = pd.to_datetime(data4['ds'])
data4 = data4.drop_duplicates()  
data4 = data4.sort_values(by='ds')
data4 = data4.drop_duplicates()  
train_data = data4.iloc[520:775]
test_data = data4.iloc[775:860]


def prophet():
    model = Prophet(
        changepoint_prior_scale=0.01,
        holidays_prior_scale=0.8,
        #n_changepoints=500,
        seasonality_mode='multiplicative',
        weekly_seasonality=True,
        daily_seasonality=True,
        yearly_seasonality=True,
        interval_width=0.95
    )
    model.fit(train_data)

    # Generate a future dataframe for the next 90 days
    future_for_90_days = model.make_future_dataframe(periods=85, freq='D', include_history=False)
    forecast = model.predict(future_for_90_days)


    # Initialize an empty list to store accuracy for each day
    daily_accuracies = []

    # Loop through each day in the forecast
    for i in range(85):
        predicted_value = forecast.iloc[i]['yhat']
        print(round(predicted_value))
        actual_value = test_data.iloc[i]['y']  # Ensure test_data is correctly aligned with forecast dates
        print(actual_value)

        # Calculate the accuracy for the day as 1 - absolute percentage error
        accuracy = 1 - np.abs((actual_value - predicted_value) / actual_value)
        accuracy = max(0, accuracy)  # Ensure accuracy is not negative
        daily_accuracies.append(accuracy)

    # Optionally, create a DataFrame to neatly display the date and its corresponding daily accuracy
    results_df = pd.DataFrame({
        'Date': forecast['ds'].iloc[:85],
        'Actual': test_data['y'].values[:85],  # Assuming test_data is correctly prepared
        'Predicted': forecast['yhat'].iloc[:85],
        'Accuracy': daily_accuracies
    })

    p = results_df['Accuracy'].tolist()
    accu = []
    for i in p:
        i = i*100
        accu.append(round(i))

    # Convert 'ds' to datetime
    data4['ds'] = pd.to_datetime(data4['ds'])

    # Extract year and month
    data4['Year'] = data4['ds'].dt.year
    data4['Month'] = data4['ds'].dt.strftime('%B')  # Month in full name

    # Filter for the year 2023
    data_2023 = data4[data4['Year'] == 2023]

    # Define the month order
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June', 
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    # Make 'Month' a categorical column with a specified order
    data_2023['Month'] = pd.Categorical(data_2023['Month'], categories=month_order, ordered=True)

    # Group by month and sum the revenues for 2023
    merged_data = data_2023.groupby('Month')['y'].sum().reset_index()

    return results_df, merged_data
