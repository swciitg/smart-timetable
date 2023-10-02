import pandas as pd
import helper


def add_timings_to_course_csv(url: str):
    try:
        course_df = pd.read_csv(url)

        # Create new columns with empty string as default value
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            course_df[day] = ""

        # Read the time table json
        tt_json = helper.read_tt()

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
