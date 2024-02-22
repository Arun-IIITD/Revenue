import pandas as pd

# Load the data from Excel files
accuracy = pd.read_excel('accuracy.xlsx')
revenue = pd.read_excel('revenue.xlsx')

# Ensure the 'Date' columns are in datetime format
accuracy['Business Date'] = pd.to_datetime(accuracy['Business Date'])
revenue['Business Date'] = pd.to_datetime(revenue['Business Date'])

# Find the last date in the accuracy DataFrame
last_date_in_accuracy = accuracy['Business Date'].max()

# Filter the revenue DataFrame to only include data after the last date in accuracy
revenue_after_last_date = revenue[revenue['Business Date'] > last_date_in_accuracy]

# Assuming 'Room Sold' and 'Room Rev' are the columns you want to copy
# Check if these columns exist in both DataFrames and concatenate accordingly
if 'Rooms Sold' in accuracy.columns and 'Rooms Sold' in revenue.columns:
    # Concatenate Room Sold data
    accuracy = pd.concat([accuracy, revenue_after_last_date[['Business Date', 'Rooms Sold']]], ignore_index=True)

if 'Room Revenue' in accuracy.columns and 'Room Revenue' in revenue.columns:
    # Concatenate Room Rev data
    accuracy = pd.concat([accuracy, revenue_after_last_date[['Business Date', 'Room Revenue']]], ignore_index=True)

# Optionally, you might want to sort the DataFrame by 'Date' after concatenation
accuracy.sort_values(by='Business Date', inplace=True)

# Reset the index of the DataFrame
accuracy.reset_index(drop=True, inplace=True)

# Save the updated DataFrame back to an Excel file
accuracy.to_excel('accurac1y.xlsx', index=False)
