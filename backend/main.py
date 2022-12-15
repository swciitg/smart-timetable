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
    url: str


class request_my_courses(BaseModel):
    roll_number: str


@app.get('/')
def welcome():
    return {'ping': 'Hello there! Go to /docs to see the Swagger documentation'}


@app.post('/generate-all-courses')
def generate_all_courses(data: request_generate):
    url = data.url
    message = ocr.generate_all_courses_CSV(url)
    if message == None:
        return HTTPException(status_code=400, detail='Invalid PDF or URL')
    else:
        return message


def return_empty_string(value):
    return '' if pd.isnull(value) else value

def get_designfresher_courses(roll_number):
    data_map=ocr.get_fresher_DF(roll_number)
    # my_courses = {
    #         'code': return_empty_string(df_entry[1]),
    #         'course': return_empty_string(df_entry[2]),
    #         'ltpc': return_empty_string(df_entry[3]),
    #         'slot': return_empty_string(df_entry[8]),
    #         'instructor': return_empty_string(df_entry[11]),
    #         'midsem': return_empty_string(df_entry[9]),
    #         'endsem': return_empty_string(df_entry[10])
    #     }

    # Correct for div 3
    courses=[
        {
            'course':'EE 101',
            'code':'EE101',
            'slot':'C',
            'instructor':'5G1',
            'ltpc':' ',
            'midsem':' ',
            'endsem':' '
        },
    ]
    if data_map['Division']=='I' or data_map['Division']=='II':
        for c in courses:
            c['slot']=c['slot']+'1'
    if data_map['Division']=='II' or data_map['Division']=='IV':
        for c in courses:
            c['instructor']='5G2'
    tutorial=[
        {
            'course':'EE 101 Tutorial',
            'code':'EE101',
            'slot':'c',
            'instructor':data_map['Location'],
            'ltpc':' ',
            'midsem':' ',
            'endsem':' '
        }
    ]
    lab=[
        {
            'course':'CE 101 Lab',
            'code':'CE110',
            'slot':'AL5',
            'instructor':'Drawing Hall Core 1',
            'ltpc':' ',
            'midsem':' ',
            'endsem':' '
        }
    ]
    
    return {
        'roll_number':roll_number,
        'courses':courses+tutorial+lab
    }

def get_fresher_courses(roll_number):
    data_map=ocr.get_fresher_DF(roll_number)
    # my_courses = {
    #         'code': return_empty_string(df_entry[1]),
    #         'course': return_empty_string(df_entry[2]),
    #         'ltpc': return_empty_string(df_entry[3]),
    #         'slot': return_empty_string(df_entry[8]),
    #         'instructor': return_empty_string(df_entry[11]),
    #         'midsem': return_empty_string(df_entry[9]),
    #         'endsem': return_empty_string(df_entry[10])
    #     }

    # Correct for div 3
    courses=[
        {
            'course':'CE 101',
            'code':'CE101',
            'slot':'A',
            'instructor':'5G1',
            'ltpc':' ',
            'midsem':' ',
            'endsem':' '
        },
        {
            'course':'MA 101',
            'code':'MA101',
            'slot':'B',
            'instructor':'5G1',
            'ltpc':' ',
            'midsem':' ',
            'endsem':' '
        },
        {
            'course':'EE 101',
            'code':'EE101',
            'slot':'C',
            'instructor':'5G1',
            'ltpc':' ',
            'midsem':' ',
            'endsem':' '
        },
        {
            'course':'CH 101',
            'code':'CH101',
            'slot':'D',
            'instructor':'5G1',
            'ltpc':' ',
            'midsem':' ',
            'endsem':' '
        },
        {
            'course':'PH 101',
            'code':'PH101',
            'slot':'E',
            'instructor':'5G1',
            'ltpc':' ',
            'midsem':' ',
            'endsem':' '
        }
    ]
    if data_map['Division']=='I' or data_map['Division']=='II':
        for c in courses:
            c['slot']=c['slot']+'1'
    if data_map['Division']=='II' or data_map['Division']=='IV':
        for c in courses:
            c['instructor']='5G2'
    tutorial=[
        {
            'course':'MA 101 Tutorial',
            'code':'MA101',
            'slot':'b',
            'instructor':data_map['Location'],
            'ltpc':' ',
            'midsem':' ',
            'endsem':' '
        },
        {
            'course':'EE 101 Tutorial',
            'code':'EE101',
            'slot':'c',
            'instructor':data_map['Location'],
            'ltpc':' ',
            'midsem':' ',
            'endsem':' '
        },
        {
            'course':'CH 101 Tutorial',
            'code':'CH101',
            'slot':'d',
            'instructor':data_map['Location'],
            'ltpc':' ',
            'midsem':' ',
            'endsem':' '
        },
        {
            'course':'PH 101 Tutorial',
            'code':'PH101',
            'slot':'e',
            'instructor':data_map['Location'],
            'ltpc':' ',
            'midsem':' ',
            'endsem':' '
        }
    ]
    lab=[
        {
            'course':'CH 110 Lab',
            'code':'CH110',
            'slot':'AL' if data_map['Division'] in ['III','IV'] else 'ML',
            'instructor':'Chemistry Lab Core 3',
            'ltpc':' ',
            'midsem':' ',
            'endsem':' '
        },
        {
            'course':'CE 101 Lab',
            'code':'CE110',
            'slot':'AL' if data_map['Division'] in ['III','IV'] else 'ML',
            'instructor':'Drawing Hall Core 1',
            'ltpc':' ',
            'midsem':' ',
            'endsem':' '
        },
        {
            'course':'ME 110 Lab' if data_map['Division'] in ['III','IV'] else 'PH 110 Lab',
            'code':'ME110' if data_map['Division'] in ['III','IV'] else 'PH110',
            'slot':'AL' if data_map['Division'] in ['III','IV'] else 'ML',
            'instructor':'Central Workshop' if data_map['Division'] in ['III','IV'] else 'Physics Lab Core 4',
            'ltpc':' ',
            'midsem':' ',
            'endsem':' '
        }
    ]
    if data_map['Lab']=='L6' or data_map['Lab']=='L1':
        lab[0]['slot']=lab[0]['slot']+'1'
        lab[1]['slot']=lab[1]['slot']+'2'
        lab[2]['slot']=lab[2]['slot']+'4'
    elif data_map['Lab']=='L7' or data_map['Lab']=='L2':
        lab[0]['slot']=lab[0]['slot']+'3'
        lab[1]['slot']=lab[1]['slot']+'4'
        lab[2]['slot']=lab[2]['slot']+'1'
    elif data_map['Lab']=='L8' or data_map['Lab']=='L3':
        lab[0]['slot']=lab[0]['slot']+'5'
        lab[1]['slot']=lab[1]['slot']+'1'
        lab[2]['slot']=lab[2]['slot']+'3'
    elif data_map['Lab']=='L9' or data_map['Lab']=='L4':
        lab[0]['slot']=lab[0]['slot']+'2'
        lab[1]['slot']=lab[1]['slot']+'3'
        lab[2]['slot']=lab[2]['slot']+'5'
    elif data_map['Lab']=='L10' or data_map['Lab']=='L5':
        lab[0]['slot']=lab[0]['slot']+'4'
        lab[1]['slot']=lab[1]['slot']+'5'
        lab[2]['slot']=lab[2]['slot']+'2'
    
    return {
        'roll_number':roll_number,
        'courses':courses+tutorial+lab
    }



@app.post('/get-my-courses')
def get_my_courses(data: request_my_courses):
    roll_number = data.roll_number
    courses_parsed = courses.get_courses_parsed(roll_number)
    if roll_number.startswith('220205'):
        return get_designfresher_courses(roll_number)
    elif roll_number.startswith('220'):
        return get_fresher_courses(roll_number)


    # Store all courses in a DF
    all_courses_df = ocr.fetch_all_courses_DF()
    if (all_courses_df.empty):
        return HTTPException(status_code=404, detail='Courses CSV file not found. Please generate it first.')

    # Find all course details given the course code list
    my_courses_df = all_courses_df.loc[all_courses_df['1'].isin(
        courses_parsed)]

    data = {'roll_number': roll_number}
    my_courses_list = []

    for i in range(0, len(my_courses_df)):
        df_entry = my_courses_df.iloc[i]
        my_courses = {
            'code': return_empty_string(df_entry[1]),
            'course': return_empty_string(df_entry[2]),
            'ltpc': return_empty_string(df_entry[3]),
            'slot': return_empty_string(df_entry[8]),
            'instructor': return_empty_string(df_entry[11]),
            'midsem': return_empty_string(df_entry[9]),
            'endsem': return_empty_string(df_entry[10])
        }
        my_courses_list.append(my_courses)

    data['courses'] = my_courses_list

    if (len(my_courses_list) == 0):
        if (data['roll_number'] in wrong_roll_numbers.keys()):
            new_data = request_my_courses(roll_number=wrong_roll_numbers[data['roll_number']])
            return get_my_courses(data=new_data)
        return HTTPException(status_code=400, detail='Invalid roll number')

    return data


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)


wrong_roll_numbers = {
    '190104017' : '190102110',
}