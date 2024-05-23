# To run -> python initialise_timings.py

import pandas as pd
import helper

# Run this script only once you generate the courses_csv.csv
# This script initialises the default times of each course according to its slot

def add_timings_to_course_csv(url: str):
    url = "data/courses_csv.csv"
    try:
        course_df = pd.read_csv(url)

        # Create new columns with empty string as default value
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            course_df[day] = ""
        
        # Read the time table json
        tt_json = helper.readTT()

        # Getting the time and day of classes from df
        num_row, _ = course_df.shape
        for row in range(num_row):
            slot = course_df.loc[row, 'slot']
            if pd.isnull(slot):
                continue
            else:
                day_dict = tt_json[slot]
                for day, time in day_dict.items():
                    course_df.loc[row, day] = time

        # Saving the CSV back
        course_df.to_csv(url, index=False)
        return course_df
    # Exception handling
    except Exception as e:
        print(e)
        return pd.DataFrame()

add_timings_to_course_csv("data/courses_csv.csv")