# python -m uvicorn main:app --reload  -> To run the backend

# Required imports
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import gunicorn
from pydantic import BaseModel
import numpy as np
import pandas as pd
import re
import string

# importing helper modules
from data import fetch_courses_df
from courses import get_course_codes_from_csv
from fresher_courses import get_fresher_courses
from enhanced_fresher_courses import format_fresher_courses_response
from semester_constants import FRESHER_YEAR
from helper import *

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Default route
@app.get('/')
def welcome():
    return {'ping': 'Hello there! Go to /docs to see the Swagger documentation'}

# pydantic models
class requestMyCourses(BaseModel):
    roll_number: str

@app.post('/get-my-courses')
def get_my_courses(data: requestMyCourses):
    roll_number = data.roll_number

    # Handle BDes and BTech freshers respectively
    if roll_number.startswith(FRESHER_YEAR+'0205') or roll_number.startswith(FRESHER_YEAR+'01'):
        fresher_response = format_fresher_courses_response(roll_number)
        if fresher_response:
            return fresher_response
        # If no fresher data, fall through to regular processing
        
    # Acquire user course codes
    course_codes = get_course_codes_from_csv(roll_number)
    
    # Store all courses data in a DF 
    all_courses_df = fetch_courses_df()
    if (all_courses_df.empty):
        return HTTPException(status_code=404, detail='Courses CSV file not found. Please generate it first.')

    # Add timings columns to course df - To be run manually only once using initialise_timings script

    all_courses_df = all_courses_df.fillna('') # to avoid json errors due to nan

    # Find all course details given the course code list
    my_courses_df = all_courses_df.loc[all_courses_df['code'].isin(
        course_codes)]
    
    # Drop duplicates for each course code, keeping the first entry
    my_courses_df = my_courses_df.drop_duplicates(subset=['code'], keep='first')
    
    print(my_courses_df)

    data = {}
    my_courses_list = []

    for i in range(0, len(my_courses_df)):
        df_entry = my_courses_df.iloc[i]

        # Getting the timings json`
        timing_json = {}
        if "Monday" in all_courses_df.columns: # Checking if timings columns are there, if not there keep dict as empty
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                if df_entry[day]!="":
                    timing_json[day] = df_entry[day]
        
        venue_str = str(df_entry['venue']) if pd.notna(df_entry['venue']) else ''
        # Remove .0 suffix from venue numbers
        venue_str = venue_str.replace('.0', '') if venue_str.endswith('.0') else venue_str
        
        my_courses_nullable = {
            'code': ensure_string(df_entry['code']),
            'course': ensure_string(df_entry['name']),
            'slot': ensure_string(df_entry['slot']),
            'instructor': ensure_string(df_entry['prof']),
            'venue': ensure_string(venue_str),
            'midsem': mid_time(df_entry['exam_slot']),
            'endsem': end_time(df_entry['exam_slot']),
            'timings': timing_json,
            'midsemVenue': exam_venue(df_entry['code'], roll_number, True),
            'endsemVenue': exam_venue(df_entry['code'], roll_number, False),
        }

        my_courses = {
            k:v for k,v in my_courses_nullable.items() if not pd.isna(v)
        }

        my_courses_list.append(my_courses)
    data['courses'] = my_courses_list

    return data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)