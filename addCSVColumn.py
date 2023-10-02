import pandas as pd
import helper

def add_timings_to_course_csv():
    try:
        course_df = pd.read_csv('data/courses_csv.csv')

        # Create new columns with empty string as default value
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            course_df[day] = ""

        # Read the time table json
        tt_json = helper.read_tt()
        num_row,_ = course_df.shape
        for row in range(num_row):
            slot = course_df.loc[row,'slot']
            if pd.isnull(slot):
                continue
            else:
                day_dict = tt_json[slot]
                for day,time in day_dict.items():
                    course_df.loc[row,day] = time
            
        course_df.to_csv('data/courses_csv.csv', index=False)
        return course_df
    except Exception as e:
        print(e)
        return pd.DataFrame()