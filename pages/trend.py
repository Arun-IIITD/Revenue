# 00 - 07 Days: 98% +
# 08 - 14 Days: 94% + 
# 15 - 21 Days: 90% +

#89 - 0.01
#80 - 0.01
#88 - 0.17


#FIRST WE RUN the  prophet model without tuning
#IST GRAPH
# model = Prophet()
# model = model.fit(train_data)
# future = model.make_future_dataframe(periods=21)
# forecast = model.predict(future)
# fig1  = model.plot(forecast)   #1st graph
# train_forecast = model.predict(train_data[['ds']])
# val_forecast = model.predict(test_data_for_21_days[['ds']])
# train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
# val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'])
# print(f'Training MAPE: {train_mape}')
# print(f'Validation MAPE: {val_mape}')

# # 2ND GRAPH WITH CHANGEPOINT
# model1 = Prophet()
# model1 = model1.fit(train_data)
# future1 = model1.make_future_dataframe(periods=21)
# forecast1 = model1.predict(future1)
# fig2 = model1.plot(forecast1)  #2nd graph with changepoints
# a = add_changepoints_to_plot(fig2.gca(), model1, forecast1)
# plt.savefig("Model with change point")

# #NO OF CHANGEPOINTS AND CHANGEPOINTS #3RD GRAPH WITH CHANGEPOINTS WITH SOME TUNING by default c =25
# m3_changepoints = (pd.date_range('2022-01-23', '2022-12-01', periods=15).date.tolist() + 
# pd.date_range('2023-01-01', '2023-12-01', periods=10).date.tolist())
# m3 = Prophet(changepoints=m3_changepoints, changepoint_prior_scale=0.96)
# m3 = m3.fit(train_data)
# future3 = m3.make_future_dataframe(periods=21)
# forecast3 = m3.predict(future3)
# fig3  = m3.plot(forecast3) #3rd graph without  changepoint
# train_forecast = m3.predict(train_data[['ds']])
# val_forecast = m3.predict(test_data_for_21_days[['ds']])
# train_mape = mean_absolute_percentage_error(train_data['y'], train_forecast['yhat'])
# val_mape = mean_absolute_percentage_error(test_data_for_21_days['y'], val_forecast['yhat'])
# print(f'Training MAPE: {train_mape}')
# print(f'Validation MAPE: {val_mape}')
# fig = m3.plot(forecast3)
# a = add_changepoints_to_plot(fig.gca(), m3, forecast3)
# plt.savefig("Model with change point2") #4th graph after tuning with changepoints
# plt.show()



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
from statistics import mean
from prophet.plot import plot_plotly, plot_components_plotly
from prophet.plot import plot, plot_components
import holidays
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import pymongo
from prophet import Prophet
from sklearn.metrics import confusion_matrix, recall_score
from sklearn.metrics import mean_absolute_percentage_error
from prophet.plot import add_changepoints_to_plot
import streamlit as st

# Read your data and preprocess it
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
            <a style="color: {'red' if selected_page == 'Trend' else '#333'}; border-bottom: {'2px solid red' if selected_page == 'Trend' else 'none'}" href="/Trend" target="_self">Trend</a>
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

    #PROPHET MODEL WITHOUT TUNING
    st.subheader('Prophet Forecast without Tuning')
    model = Prophet()
    model.fit(train_data)
    future = model.make_future_dataframe(periods=21)
    forecast = model.predict(future)
    fig1 = model.plot(forecast)
    st.pyplot(fig1)


if __name__ == '__main__':
    main()














