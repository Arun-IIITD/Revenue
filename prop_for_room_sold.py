import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
from statistics import mean
import pymongo
import numpy as np

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
data4 = data[['Business Date','Rooms Sold']]
data4.columns = ['ds','y'] 
data4 = data4.drop_duplicates()  
print(len(data4))
train_data = data4.iloc[:844]
test_data_for_next_7_days = data4.iloc[844:851]
test_data_for_next_14_days = data4.iloc[851:858]
test_data_for_next_21_days = data4.iloc[858:865]

def model_R():
    # Room sold for first 7 days(0-7)
    model = Prophet(
                            changepoint_prior_scale= 0.01,
                            holidays_prior_scale = 0.4,
                            n_changepoints = 200,
                            seasonality_mode = 'multiplicative',
                            weekly_seasonality=True,
                            daily_seasonality = True,
                            yearly_seasonality = False,
                    )
    model.fit(train_data)
    future_for_7_days = model.make_future_dataframe(periods=7, freq='D', include_history=False)
    forecast = model.predict(future_for_7_days)
    next_7_days = forecast.tail(7)
    Actual_for_7_days =  []
    Predicted_for_7_days = []
    Accuracy_for_7_days = []
    for i,j in zip(list(test_data_for_next_7_days['y'].tail(10)),list(next_7_days['yhat'])):
        i= int(i)
        j = int(j)
        Actual_for_7_days.append(i)
        Predicted_for_7_days.append(j)

   
    tp_for_7_days = 0
    fn_for_7_days = 0
    fp_for_7_days = 0
    tn_for_7_days = 0
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




    #ROOM SOLD FOR next 7 days(8-14)
    model1 = Prophet(changepoint_prior_scale=0.01,
                    holidays_prior_scale = 0.4,
                    #n_changepoints = 200,
                    seasonality_mode = 'multiplicative',
                    weekly_seasonality=True,
                    daily_seasonality = True,
                    yearly_seasonality = False,
                    interval_width=0.95
                        )
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


    #ROOM SOLD FOR FOR 21 DAYS(15-21 days)
    model2 = Prophet(
                            changepoint_prior_scale=0.1,  # Tweak this parameter based on your data
                            yearly_seasonality=False,       # Add yearly seasonality
                            weekly_seasonality=True, )
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

    # Convert to datetime and extract year and month
    data4['ds'] = pd.to_datetime(data4['ds'])
    data4['Year'] = data4['ds'].dt.year
    data4['Month'] = data4['ds'].dt.strftime('%B')  # Month in full name

    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'
    ]

    data4['Month'] = pd.Categorical(data4['Month'], categories=month_order, ordered=True)

    # Separate data for each year
    data_2022 = data4[data4['Year'] == 2022]
    data_2023 = data4[data4['Year'] == 2023]

    # Group by month and sum the revenues for each year
    monthly_total_revenue_2022 = data_2022.groupby('Month')['y'].sum().reset_index()
    monthly_total_revenue_2023 = data_2023.groupby('Month')['y'].sum().reset_index()

    # Merge the data for 2022 and 2023
    merged_data = pd.merge(monthly_total_revenue_2022, monthly_total_revenue_2023, on='Month', suffixes=('_2022', '_2023'))


    return Actual_for_7_days,Predicted_for_7_days,Accuracy_for_7_days,Actual_for_14_days,Predicted_for_14_days,Accuracy_for_14_days,Actual_for_21_days,Predicted_for_21_days,Accuracy_for_21_days,sensitivity_values_for_7_days,sensitivity_values_for_14_days,sensitivity_values_for_21_days,mae1,mae2,mae3,merged_data

arr = model_R()

print(arr[2])
print(arr[5])
print(arr[8])



















