import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pymongo

# Data extraction
connection_uri = "mongodb+srv://annu21312:6dPsrXPfhm19YxXl@hello.hes3iy5.mongodb.net/"
client = pymongo.MongoClient(connection_uri, serverSelectionTimeoutMS=30000)
database_name = "Revenue_Forecasting"
db = client[database_name]

# Fetch data from MongoDB
collection4 = db["Prophet"]
cursor2 = collection4.find({})
data = pd.DataFrame(list(cursor2))


data.rename(columns={'Date': 'ds', 'Revenue': 'y'}, inplace=True)
#data = data.dropna(subset=['ds'])

# Initialize and fit the Prophet model
model = Prophet()
model.fit(data)

# Create a future DataFrame for forecasting (forecast for the next 7 days)
future = model.make_future_dataframe(periods=7)

# Generate forecasts
forecast = model.predict(future)

# ACTUAL REVENUE FOR 7 DAYS
actual_data = data.tail(7)

# PREDICTIONS FOR 7 DAYS
next_7_days_forecast = forecast.tail(7)


predictions_for_7_days = [int(x) for x in list(next_7_days_forecast['yhat'])]
actual_data_for_7_days = [int(x) for x in list(actual_data['y'])]

print("prediction are",predictions_for_7_days)
print("actual revenue are",actual_data_for_7_days)

# Calculate accuracy as a percentage
accuracy = np.mean([pred / actual * 100 for pred, actual in zip(next_7_days_forecast['yhat'], actual_data['y'])])
print(f"Accuracy is {accuracy:.2f}%")

# Visualize the forecast
fig = model.plot_components(forecast)
plt.title('Revenue Forecast')
plt.xlabel('Date')
plt.ylabel('Revenue')
plt.savefig("revenue_forecasting.png")



# Calculate accuracy metrics
mae = mean_absolute_error(actual_data['y'], next_7_days_forecast['yhat'])
mse = mean_squared_error(actual_data['y'], next_7_days_forecast['yhat'])
rmse = np.sqrt(mse)

'''print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")'''
