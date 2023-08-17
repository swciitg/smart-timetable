import pandas as pd
import numpy as np

# Read the CSV file
file_path = 'courses_csv.csv'
df = pd.read_csv(file_path)

# Add new columns for each day of the week and initialize with NaN (or any default value you prefer)
days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
for day in days:
    df[day] = ''

# Optionally, you can fill the new columns with specific values based on your logic
# For example, you might want to copy the slot value into the appropriate day columns
# df['mon'] = df['slot']

time_slots = ["08:00 - 08:55 AM", "09:00 - 09:55 AM", "10:00 - 10:55 AM", "11:00 - 11:55 AM", "12:00 - 12:55 PM", "1:00 - 1:55 PM", "2:00 - 2:55 PM", "3:00 - 3:55 PM", "4:00 - 4:55 PM", "5:00 - 5:55 PM"]
# Iterate through each row and modify the new columns based on your login
for index, row in df.iterrows():
    # Example logic: set the value for 'mon' column to the value in 'slot' column
    if row['slot'] == "A":
        df.at[index, 'monday'] = time_slots[0]
        df.at[index, 'tuesday'] = time_slots[1]
        df.at[index, 'wednesday'] = time_slots[2]
        df.at[index, 'thursday'] = time_slots[3]
    if row['slot'] == "B":
        df.at[index, 'monday'] = time_slots[1]
        df.at[index, 'tuesday'] = time_slots[2]
        df.at[index, 'wednesday'] = time_slots[3]
        df.at[index, 'friday'] = time_slots[0]
    if row['slot'] == "C":
        df.at[index, 'monday'] = time_slots[2]
        df.at[index, 'tuesday'] = time_slots[3]
        df.at[index, 'thursday'] = time_slots[1]
        df.at[index, 'friday'] = time_slots[0]
    if row['slot'] == "D":
        df.at[index, 'monday'] = time_slots[3]
        df.at[index, 'wednesday'] = time_slots[0]
        df.at[index, 'thursday'] = time_slots[1]
        df.at[index, 'friday'] = time_slots[2]
    if row['slot'] == "E":
        df.at[index, 'tuesday'] = time_slots[0]
        df.at[index, 'wednesday'] = time_slots[1]
        df.at[index, 'thursday'] = time_slots[2]
    if row['slot'] == "F":
        df.at[index, 'monday'] = time_slots[4]
        df.at[index, 'tuesday'] = time_slots[4]
        df.at[index, 'friday'] = time_slots[3]
    if row['slot'] == "G":
        df.at[index, 'wednesday'] = time_slots[4]
        df.at[index, 'thursday'] = time_slots[4]
        df.at[index, 'friday'] = time_slots[4]
    if row['slot'] == "A1":
        df.at[index, 'monday'] = time_slots[9]
        df.at[index, 'tuesday'] = time_slots[8]
        df.at[index, 'wednesday'] = time_slots[7]
        df.at[index, 'thursday'] = time_slots[6]
    if row['slot'] == "B1":
        df.at[index, 'monday'] = time_slots[8]
        df.at[index, 'tuesday'] = time_slots[7]
        df.at[index, 'wednesday'] = time_slots[6]
        df.at[index, 'friday'] = time_slots[9]
    if row['slot'] == "C1":
        df.at[index, 'monday'] = time_slots[7]
        df.at[index, 'tuesday'] = time_slots[6]
        df.at[index, 'thursday'] = time_slots[9]
        df.at[index, 'friday'] = time_slots[8]
    if row['slot'] == "D1":
        df.at[index, 'monday'] = time_slots[6]
        df.at[index, 'wednesday'] = time_slots[9]
        df.at[index, 'thursday'] = time_slots[8]
        df.at[index, 'friday'] = time_slots[7]
    if row['slot'] == "E1":
        df.at[index, 'tuesday'] = time_slots[9]
        df.at[index, 'wednesday'] = time_slots[8]
        df.at[index, 'thursday'] = time_slots[7]
    if row['slot'] == "F1":
        df.at[index, 'monday'] = time_slots[5]
        df.at[index, 'tuesday'] = time_slots[5]
        df.at[index, 'friday'] = time_slots[6]
    if row['slot'] == "G1":
        df.at[index, 'wednesday'] = time_slots[5]
        df.at[index, 'thursday'] = time_slots[5]
        df.at[index, 'friday'] = time_slots[5]
    
    # You can add more logic here to modify other columns as needed


# Save the updated DataFrame back to a CSV file
output_path = 'courses_csv.csv'
df.to_csv(output_path, index=False)