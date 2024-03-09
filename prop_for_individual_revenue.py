#7 Days: Revenue = 91
#14 Days: Revenue = 91
#21 Days: Revenue = 91

# 00 - 07 Days: 98% +
# 08 - 14 Days: 94% + 
# 15 - 21 Days: 90% +

from statistics import mean

import holidays
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import pymongo
from prophet import Prophet
from sklearn.metrics import confusion_matrix, recall_score

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
data4 = data[['Business Date','Individual Revenue']]
data4.columns = ['ds','y'] 
data4 = data4.drop_duplicates()  
print(len(data4))
train_data = data4.iloc[:844]
test_data_for_next_7_days = data4.iloc[844:851]
test_data_for_next_14_days = data4.iloc[851:858]
test_data_for_next_21_days = data4.iloc[858:865]

#FOR 1st 7 DAYS(1-7)
def model_IR():
    model = Prophet(changepoint_prior_scale= 0.3,
                            holidays_prior_scale = 0.8,
                            n_changepoints = 500,
                            seasonality_mode = 'multiplicative',
                            weekly_seasonality=True,
                            daily_seasonality = True,
                            yearly_seasonality = True,
                            #interval_width=0.95
         
                            )
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
        if c >90:
                tp_for_7_days+=1
        else:
                fn_for_7_days+=1
        Accuracy_for_7_days.append(c)

    #FOR next 7 DAYS (8-14)
    model1 = Prophet(
                        changepoint_prior_scale= 0.1,
                        holidays_prior_scale = 0.4,
                        #n_changepoints = 120,
                        seasonality_mode = 'additive',
                        weekly_seasonality=True,
                        daily_seasonality = True,
                        yearly_seasonality = True,
                        #interval_width=0.5
                        )
    model1.fit(train_data)
    future_for_14_days = model1.make_future_dataframe(periods=7, freq='D', include_history=False)
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
        if c >= 90:
            tp_for_21_days +=1
        else:
            fn_for_21_days+=1
        Accuracy_for_21_days.append(c)

    sensitivity_values_for_7_days = tp_for_7_days/(tp_for_7_days + fn_for_7_days)
    sensitivity_values_for_14_days = tp_for_14_days/(tp_for_14_days + fn_for_14_days)
    sensitivity_values_for_21_days = tp_for_21_days/(tp_for_21_days + fn_for_21_days)

    absolute_diff1 = np.abs(np.array(Predicted_for_7_days) - np.array(Actual_for_7_days))
    mae1 = np.mean(absolute_diff1)
    absolute_diff2 = np.abs(np.array(Predicted_for_14_days) - np.array(Actual_for_14_days))
    mae2 = np.mean(absolute_diff2)
    absolute_diff3 = np.abs(np.array(Predicted_for_21_days) - np.array(Actual_for_21_days))
    mae3 = np.mean(absolute_diff3)

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

    return Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days,sensitivity_values_for_7_days,sensitivity_values_for_14_days,sensitivity_values_for_21_days,mae1,mae2,mae3,merged_data
arr = model_IR()

print(arr[2])
print(arr[5])
print(arr[8])
































