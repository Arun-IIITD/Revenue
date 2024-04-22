import pandas as pd
df1 = pd.read_excel('covid_room_revenue.xlsx')
df2 = pd.read_excel('revenue.xlsx')
print(df1.columns)
print(df2.columns)
# Merge the DataFrames on the 'Room Revenue' column, using an inner join to keep only matching records
merged_df = pd.merge(df1, df2, on=["Occupancy","Room Revenue","Rooms Sold", "Arrival Rooms", "OOO Rooms", "Pax", "Dep Rooms", "House Use"], how='outer')
# fields = ["Occupancy","Room Revenue", "ARR", "Arrival Rooms", "OOO Rooms", "Pax", "Rooms for Sale", "Departure Rooms", "House Use", "Total Room Inventory"]

# Print the columns of the merged DataFrame to understand what is available
print("Columns in merged DataFrame:", merged_df.columns.tolist())

# If the 'Business Date' column (from either DataFrame) exists, sort by it, otherwise handle it gracefully
if 'Business Date_x' in merged_df.columns and 'Business Date_y' in merged_df.columns:
    # Sort the final DataFrame by one of the 'Business Date' columns
    final_merged_df = merged_df.sort_values(by='Business Date_x')
    print(final_merged_df[['Business Date_x', 'Business Date_y', 'Room Revenue']])
    # Save the sorted DataFrame to an Excel file
    final_merged_df.to_excel('sorted.xlsx', index=False)
else:
    print("The expected 'Business Date' columns do not exist in the merged DataFrame.")
    # You might still want to save the merged but unsorted DataFrame
    merged_df.to_excel('merged_output.xlsx', index=False)



