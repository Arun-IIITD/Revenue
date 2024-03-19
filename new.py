# 00 - 07 Days: 98% +
# 08 - 14 Days: 94% + 
# 15 - 21 Days: 90% +

#89 - 0.01
#80 - 0.01
#88 - 0.17

import base64
import os
from io import BytesIO
from statistics import mean
import altair as alt
import holidays
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pymongo
import streamlit as st
from prophet import Prophet
from prophet.plot import (add_changepoints_to_plot, plot, plot_components,plot_components_plotly, plot_plotly)
from sklearn.metrics import (confusion_matrix, mean_absolute_error,mean_absolute_percentage_error,mean_squared_error, recall_score)
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
data4 =  data4[['Business Date','Room Revenue','Rooms Sold']]
data5 = data5[['Business Date','Room Revenue','Rooms Sold','Arrival Rooms','Individual Revenue','Individual Confirm']]
data = pd.concat([data4,data5],ignore_index=True)
data = data[['Business Date','Room Revenue']]
data.columns = ['ds','y'] 
data['ds'] = pd.to_datetime(data['ds'])
data = data.drop_duplicates()  
data = data.sort_values(by='ds')
train_data = data.iloc[122:844]
test_data_for_next_7_days = data.iloc[844:851]
test_data_for_next_14_days = data.iloc[851:858]
test_data_for_next_21_days = data.iloc[858:865]
test_data_for_21_days = data.iloc[844:865]
training = []
validation = []
#without tuning
def change(changepoint):
    model = Prophet(changepoint_prior_scale=changepoint)
    model.fit(train_data)
    future = model.make_future_dataframe(periods=21)
    train_forecast = model.predict(train_data[['ds']])
    val_forecast = model.predict(test_data_for_21_days[['ds']])
    train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
    training.append(train_mape)
    val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'])
    validation.append(val_mape)
for i in range(1,101):
    i =i/100
    a = change(i)
minis_for_RR = []
for i,j in zip(training,validation):
    a = (round(i*100) + round( j*100))
    minis_for_RR.append(i)

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
data4 =  data4[['Business Date','Room Revenue','Rooms Sold']]
data5 = data5[['Business Date','Room Revenue','Rooms Sold','Arrival Rooms','Individual Revenue','Individual Confirm']]
data = pd.concat([data4,data5],ignore_index=True)
data = data[['Business Date','Rooms Sold']]
data.columns = ['ds','y'] 
data['ds'] = pd.to_datetime(data['ds'])
data = data.drop_duplicates()  
data = data.sort_values(by='ds')
train_data = data.iloc[122:844]
test_data_for_next_7_days = data.iloc[844:851]
test_data_for_next_14_days = data.iloc[851:858]
test_data_for_next_21_days = data.iloc[858:865]
test_data_for_21_days = data.iloc[844:865]
training = []
validation = []
#without tuning
def change(changepoint):
    model = Prophet(changepoint_prior_scale=changepoint)
    model.fit(train_data)
    future = model.make_future_dataframe(periods=21)
    train_forecast = model.predict(train_data[['ds']])
    val_forecast = model.predict(test_data_for_21_days[['ds']])
    train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
    training.append(train_mape)
    val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'])
    validation.append(val_mape)
for i in range(1,101):
    i =i/100
    a = change(i)
minis_for_RS = []
for i,j in zip(training,validation):
    a = (round(i*100) + round( j*100))
    minis_for_RS.append(i)


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
data4 =  data4[['Business Date','Room Revenue','Rooms Sold']]
data5 = data5[['Business Date','Room Revenue','Rooms Sold','Arrival Rooms','Individual Revenue','Individual Confirm']]
data = pd.concat([data4,data5],ignore_index=True)
data = data[['Business Date','Arrival Rooms']]
data.columns = ['ds','y'] 
data['ds'] = pd.to_datetime(data['ds'])
data = data.drop_duplicates()  
data = data.sort_values(by='ds')
train_data = data.iloc[520:844]
test_data_for_next_7_days = data.iloc[844:851]
test_data_for_next_14_days = data.iloc[851:858]
test_data_for_next_21_days = data.iloc[858:865]
test_data_for_21_days = data.iloc[844:865]
training = []
validation = []
#without tuning
def change(changepoint):
    model = Prophet(changepoint_prior_scale=changepoint)
    model.fit(train_data)
    future = model.make_future_dataframe(periods=21)
    train_forecast = model.predict(train_data[['ds']])
    val_forecast = model.predict(test_data_for_21_days[['ds']])
    train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
    training.append(train_mape)
    val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'])
    validation.append(val_mape)
for i in range(1,101):
    i =i/100
    a = change(i)
minis_for_arrival = []
for i,j in zip(training,validation):
    a = (round(i*100) + round( j*100))
    minis_for_arrival.append(i)




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
data4 =  data4[['Business Date','Room Revenue','Rooms Sold']]
data5 = data5[['Business Date','Room Revenue','Rooms Sold','Arrival Rooms','Individual Revenue','Individual Confirm']]
data = pd.concat([data4,data5],ignore_index=True)
data = data[['Business Date','Individual Confirm']]
data.columns = ['ds','y'] 
data['ds'] = pd.to_datetime(data['ds'])
data = data.drop_duplicates()  
data = data.sort_values(by='ds')
train_data = data.iloc[520:844]
test_data_for_next_7_days = data.iloc[844:851]
test_data_for_next_14_days = data.iloc[851:858]
test_data_for_next_21_days = data.iloc[858:865]
test_data_for_21_days = data.iloc[844:865]
training = []
validation = []
#without tuning
def change(changepoint):
    model = Prophet(changepoint_prior_scale=changepoint)
    model.fit(train_data)
    future = model.make_future_dataframe(periods=21)
    forecast = model.predict(future)
    train_forecast = model.predict(train_data[['ds']])
    val_forecast = model.predict(test_data_for_21_days[['ds']])
    train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
    training.append(train_mape)
    val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'])
    validation.append(val_mape)
for i in range(1,101):
    i =i/100
    a = change(i)
minis_for_IC = []
for i,j in zip(training,validation):
    a = (round(i*100) + round( j*100))
   # print(round(i*100) , round( j*100))
    minis_for_IC.append(i)




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
data4 =  data4[['Business Date','Room Revenue','Rooms Sold']]
data5 = data5[['Business Date','Room Revenue','Rooms Sold','Arrival Rooms','Individual Revenue','Individual Confirm']]
data = pd.concat([data4,data5],ignore_index=True)
data = data[['Business Date','Individual Revenue']]
data.columns = ['ds','y'] 
data['ds'] = pd.to_datetime(data['ds'])
data = data.drop_duplicates()  
data = data.sort_values(by='ds')
train_data = data.iloc[520:844]
test_data_for_next_7_days = data.iloc[844:851]
test_data_for_next_14_days = data.iloc[851:858]
test_data_for_next_21_days = data.iloc[858:865]
test_data_for_21_days = data.iloc[844:865]
training = []
validation = []
#without tuning
def change(changepoint):
    model = Prophet(changepoint_prior_scale=changepoint)
    model.fit(train_data)
    future = model.make_future_dataframe(periods=21)
    forecast = model.predict(future)
    train_forecast = model.predict(train_data[['ds']])
    val_forecast = model.predict(test_data_for_21_days[['ds']])
    train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
    training.append(train_mape)
    val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'])
    validation.append(val_mape)
for i in range(1,101):
    i =i/100
    a = change(i)
minis_for_IR = []
for i,j in zip(training,validation):
    a = (round(i*100) + round( j*100))
    minis_for_IR.append(i)

print("RR")
#print(len(minis_for_RR))
print(minis_for_RR.index(min(minis_for_RR)))
print(min(minis_for_RR))
print("\n")


print("RS")
#print(len(minis_for_RS))
print(minis_for_RS.index(min(minis_for_RS)))
print(min(minis_for_RS))
print("\n")

print("arrival")
#print(len(minis_for_arrival))
print(minis_for_arrival.index(min(minis_for_arrival)))
print(min(minis_for_arrival))
print("\n")

print("IC")
#print(len(minis_for_IC))
print(minis_for_IC.index(min(minis_for_IC)))
print(min(minis_for_IC))
print("\n")

print("IR")
#print(len(minis_for_IR))
print(minis_for_IR.index(min(minis_for_IR)))
print(min(minis_for_IR))


   








