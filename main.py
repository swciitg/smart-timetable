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
import ocr
from courses import get_course_codes
from fresher_courses import getFresherCourses
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
    rollNumber: str

@app.post('/get-my-courses')
def getMyCourses(data: requestMyCourses):
    rollNumber = data.rollNumber

    # Handle BDes and BTech freshers respectively
    if rollNumber.startswith(FRESHER_YEAR+'0205'):
        return getFresherCourses(rollNumber,True)
    elif rollNumber.startswith(FRESHER_YEAR+'01'):
        return getFresherCourses(rollNumber)

    # Acquire user course codes
    course_codes = get_course_codes(rollNumber)
    print(course_codes)
    
    # Store all courses data in a DF 
    all_courses_df = ocr.fetchCourseDF()
    if (all_courses_df.empty):
        return HTTPException(status_code=404, detail='Courses CSV file not found. Please generate it first.')

    # Add timings columns to course df - To be run manually only once

    all_courses_df = all_courses_df.fillna('') # to avoid json errors due to nan

    # Find all course details given the course code list
    my_courses_df = all_courses_df.loc[all_courses_df['code'].isin(
        course_codes)]

    data = {'rollNumber': rollNumber}
    my_courses_list = []

    for i in range(0, len(my_courses_df)):
        df_entry = my_courses_df.iloc[i]
        # Getting the timings json`
        timing_json = {}
        if "Monday" in all_courses_df.columns: # Checking if timings columns are there, if not there keep dict as empty
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                if df_entry[day]!="":
                    timing_json[day] = df_entry[day]

        my_courses_nullable = {
            'code': ensureString(df_entry['code']),
            'course': ensureString(df_entry['name']),
            'slot': ensureString(df_entry['slot']),
            'instructor': ensureString(df_entry['prof']),
            'venue': ensureString(df_entry['venue']),
            'midsem': getMidsTime(df_entry['slot']),
            'endsem': getEndsTime(df_entry['slot']),
            'timings': timing_json,
            'midsemVenue': examVenue(df_entry['code'], rollNumber, True),
            'endsemVenue': examVenue(df_entry['code'], rollNumber, False),
        }

        my_courses = {
            k:v for k,v in my_courses_nullable.items() if not pd.isna(v)
        }

        my_courses_list.append(my_courses)
    
    
    data['courses'] = my_courses_list

    if (len(my_courses_list) == 0):
        if (data['rollNumber'] in wrong_rollNumbers.keys()):
            new_data = request_my_courses(rollNumber=wrong_rollNumbers[data['rollNumber']])
            return get_my_courses(data=new_data)
        return HTTPException(status_code=400, detail='Invalid roll number')

    return data

wrong_rollNumbers = {
    '190104017' : '190102110',
    '190108012' : '190102099',
}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
