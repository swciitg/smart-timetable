import pandas as pd

# Load the CSV files into DataFrames
df1 = pd.read_csv('samples/sample_divisions.csv')  # The file containing Location, Tutorial, and other columns
df2 = pd.read_csv('samples/sample_tutorial_location.csv')  # The file containing Tutorial and Location

# Merge the DataFrames on the "Tutorial" column, keeping all columns from df1
merged_df = pd.merge(df1, df2, on='Tutorial', how='left', suffixes=('', '_new'))

# Fill the Location column in df1 with the Location column from df2
merged_df['Location'] = merged_df['Location_new']

# Drop the temporary Location_new column
final_df = merged_df.drop(columns=['Location_new'])

# Save the updated DataFrame back to a CSV file
final_df.to_csv('data/divisions.csv', index=False)
