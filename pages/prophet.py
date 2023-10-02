import streamlit as st
import pandas as pd
import numpy as np
from fbprophet import Prophet
import matplotlib.pyplot as plt

# Data extraction
data = pd.read_excel('covid_room_revenue.xlsx')
data = data.dropna(subset=['Date'])

data.rename(columns={'Date': 'ds', 'Revenue': 'y'}, inplace=True)

# Initialize and fit the Prophet model
model = Prophet()
model.fit(data)

# Create a future DataFrame for forecasting (you can specify the number of periods into the future)
future = model.make_future_dataframe(periods=365)  # Example: forecast for the next year

# Generate forecasts
forecast = model.predict(future)

# Streamlit App
st.title('Revenue Forecast App')

# Sidebar controls
st.sidebar.title('Settings')
periods = st.sidebar.number_input('Number of Forecast Periods', min_value=1, max_value=365, value=365)

# Filter the forecast data to display only the selected number of periods
filtered_forecast = forecast.head(len(data) + periods)

# Interactive chart
st.plotly_chart(plt.figure())  # Create an empty chart to be populated later

# Display forecast data
st.subheader('Forecast Data')
st.write(filtered_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])

# Visualize the forecast
st.subheader('Revenue Forecast')
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(filtered_forecast['ds'], filtered_forecast['yhat'], label='Forecast', color='b')
ax.fill_between(filtered_forecast['ds'], filtered_forecast['yhat_lower'], filtered_forecast['yhat_upper'], color='b', alpha=0.3)
ax.plot(data['ds'], data['y'], label='Actual', color='g')
ax.set_xlabel('Date')
ax.set_ylabel('Revenue')
ax.set_title('Revenue Forecast')
plt.xticks(rotation=45)
st.pyplot(fig)
