from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import gunicorn
from pydantic import BaseModel
import numpy as np
import pandas as pd
import re
import string

# created Python modules
import ocr
import courses
import fresher_courses
import helper

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# pydantic models
class request_generate(BaseModel):
    courses_url: str
    mideem_venue_url: str
    endsem_venue_url: str

class request_my_courses(BaseModel):
    roll_number: str


@app.get('/')
def welcome():
    return {'ping': 'Hello there! Go to /docs to see the Swagger documentation'}


@app.post('/generate-all-courses')
def generate_all_courses(data: request_generate):
    inval = []
    courses_url = data.courses_url
    message = ocr.generate_all_courses_CSV(courses_url)
    if message == None:
        inval.append("Courses")

    midsem_venue_url = data.mideem_venue_url
    message = ocr.generate_venue_CSV(midsem_venue_url, "midsem")
    if message == None:
        inval.append("Midsem Venues")

    endsem_venue_url = data.endsem_venue_url
    message = ocr.generate_venue_CSV(endsem_venue_url, "endsem")
    if message == None:
        inval.append("Endsem Venues")

    if inval:
        return HTTPException(status_code=400, detail=f"Invalid {', '.join(inval)} PDF(s) or URL(s)")
    else:
        return message

@app.post('/get-my-courses')
def get_my_courses(data: request_my_courses):
    roll_number = data.roll_number
    courses_parsed = courses.get_courses_parsed(roll_number)
    print(courses_parsed)

    # Handle 2023 Btech and BDes freshers
    if roll_number.startswith('230205'):
        return fresher_courses.get_fresher_courses(roll_number,True)
    elif roll_number.startswith('2301'):
        return fresher_courses.get_fresher_courses(roll_number)


    # Store all courses in a DF
    all_courses_df = ocr.fetch_all_courses_DF()
    if (all_courses_df.empty):
        return HTTPException(status_code=404, detail='Courses CSV file not found. Please generate it first.')

    # Add timings columns to course df - To be run manually only once
    
    all_courses_df = all_courses_df.fillna('') # to avoid json errors due to nan
    # Find all course details given the course code list
    my_courses_df = all_courses_df.loc[all_courses_df['code'].isin(
        courses_parsed)]

    data = {'roll_number': roll_number}
    my_courses_list = []

    for i in range(0, len(my_courses_df)):
        df_entry = my_courses_df.iloc[i]
        # Getting the timings json`
        timing_json = {}
        if "Monday" in all_courses_df.columns: #Checking if timings columns are there, if not there keep dict as empty
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                if df_entry[day]!="":
                    timing_json[day] = df_entry[day]

        my_courses_nullable = {
            'code': helper.return_empty_string(df_entry['code']),
            'course': helper.return_empty_string(df_entry['name']),
            'slot': helper.return_empty_string(df_entry['slot']),
            'instructor': helper.return_empty_string(df_entry['prof']),
            'venue': helper.return_empty_string(df_entry['venue']),
            'midsem': helper.get_midsem_time(df_entry['slot']),
            'endsem': helper.get_endsem_time(df_entry['slot']),
            'timings': timing_json,
            'midsemVenue': helper.return_venue(df_entry['code'], roll_number, True),
            'endsemVenue': helper.return_venue(df_entry['code'], roll_number, False),
        }
        my_courses = {
            k:v for k,v in my_courses_nullable.items() if not pd.isna(v)
        }
        my_courses_list.append(my_courses)

    data['courses'] = my_courses_list

    if (len(my_courses_list) == 0):
        if (data['roll_number'] in wrong_roll_numbers.keys()):
            new_data = request_my_courses(roll_number=wrong_roll_numbers[data['roll_number']])
            return get_my_courses(data=new_data)
        return HTTPException(status_code=400, detail='Invalid roll number')

    return data


wrong_roll_numbers = {
    '190104017' : '190102110',
    '190108012' : '190102099',
}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
