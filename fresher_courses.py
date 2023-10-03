from typing import final
import numpy as np
import pandas as pd
import re
import string
from fastapi import HTTPException

# created Python modules
import ocr
import helper


def get_fresher_tt_slots():
    # Get tt json
    tt_json = helper.read_tt()

    # Adding tutorial slots
    tt_json['b']['Friday'] = "8:00 - 8:55 AM"
    tt_json['a']['Monday'] = "8:00 - 8:55 AM"
    tt_json['e']['Tuesday'] = "8:00 - 8:55 AM"
    tt_json['d']['Wednesday'] = "8:00 - 8:55 AM"
    tt_json['c']['Thursday'] = "8:00 - 8:55 AM"
    return tt_json

def get_fresher_courses(roll_number, isDesign: bool = False):
    data_map = ocr.get_fresher_DF(roll_number)
    print(data_map)
    # Correct for div 3
    courses = [
        {
            'course': 'Engineering Drawing',
            'code': 'CE 101',
            'slot': 'A',
            'venue': 'L2',
            'instructor': 'CE101',
            'midsem': "2023-09-18T14:00:00.000Z",
            'endsem': "2023-11-19T14:00:00.000Z"
        },
        {
            'course': 'Mathematics - I',
            'code': 'MA 101',
            'slot': 'B',
            'venue': 'L2',
            'instructor': 'MA101',
            'ltpc': ' ',
            "midsem": "2023-09-19T14:00:00.000Z",
            "endsem": "2023-11-20T14:00:00.000Z"
        },
        {
            'course': 'Basic Electronics',
            'code': 'EE 101',
            'slot': 'C',
            'venue': 'L2',
            'instructor': 'EE101',
            'ltpc': ' ',
            "midsem": "2023-09-20T14:00:00.000Z",
            "endsem": "2023-11-21T14:00:00.000Z"
        }
    ]
    if not isDesign:
        courses.extend([{
            'course': 'Chemistry',
            'code': 'CH 101',
            'slot': 'D',
            'venue': 'L2',
            'instructor': 'CH101',
            "midsem": "2023-09-21T14:00:00.000Z",
            "endsem": "2023-11-22T14:00:00.000Z"
        },
            {
            'course': 'Physics - I',
            'code': 'PH 101',
            'slot': 'E',
            'venue': 'L2',
            'instructor': 'PH101',
            "midsem": "2023-09-22T14:00:00.000Z",
            "endsem": "2023-11-23T14:00:00.000Z"
        }])

    # ? The else block is for adding design only courses
    # else:
    #     # Adding DD courses
    #     all_courses_df = ocr.fetch_all_courses_DF()
    #     if (all_courses_df.empty):
    #         return HTTPException(status_code=404, detail='Courses CSV file not found. Please generate it first.')
    #     all_courses_df = all_courses_df.fillna('')
    #     design_courses = ["DD "+str(num) for num in range(101, 106)]
    #     design_courses_df = all_courses_df.loc[all_courses_df['code'].isin(
    #         design_courses)]
    #     for _, df_entry in design_courses_df.iterrows():
    #         # Getting design course details
    #         #! There are some errors in midsem and endsem timetable and class time table due to random times of design courses
    #         my_courses = {
    #             'code': helper.return_empty_string(df_entry['code']),
    #             'course': helper.return_empty_string(df_entry['name']),
    #             'slot': helper.return_empty_string(df_entry['slot']),
    #             'instructor': helper.return_empty_string(df_entry['prof']),
    #             'venue': helper.return_empty_string(df_entry['venue']),
    #             'midsem': helper.get_midsem_time(df_entry['slot']) if helper.return_empty_string(df_entry['code']) != "DD 105" else helper.get_midsem_time("E"),
    #             'endsem': helper.get_endsem_time(df_entry['slot']) if helper.return_empty_string(df_entry['code']) != "DD 105" else helper.get_endsem_time("E"),
    #         }  # According to https://www.iitg.ac.in/acad/classtt/1st_year_Course_wise_Instructor_name_and_exam_schedule.pdf , DD 105 exam slot is different
    #         my_courses = {
    #         k:v for k,v in my_courses.items() if not pd.isna(v)
    #         }
    #         courses.append(my_courses)

    if data_map['Division'] == 'I' or data_map['Division'] == 'II':
        for c in courses:
            c['slot'] = c['slot']+'1'
    if data_map['Division'] == 'II' or data_map['Division'] == 'IV':
        for c in courses:
            c['venue'] = 'L4'
    tutorial = [
        {
            'course': 'MA 101 Tutorial',
            'code': 'MA 101',
            'slot': 'b',
            'instructor': 'MA101',
            'venue': '',
            'midsem': '',
            'endsem': ''
        },
        {
            'course': 'EE 101 Tutorial',
            'code': 'EE 101',
            'slot': 'c',
            'venue': '',
            'instructor': 'MA101',
            'midsem': '',
            'endsem': ''
        }
    ]

    if not isDesign:
        tutorial.extend([{
            'course': 'CH 101 Tutorial',
            'code': 'CH 101',
            'venue': '',
            'slot': 'd',
            'instructor': 'CH101',
            'midsem': '',
            'endsem': ''
        },
            {
            'course': 'PH 101 Tutorial',
            'code': 'PH 101',
            'slot': 'e',
            'venue': '',
            'instructor': 'PH101',
            'midsem': '',
            'endsem': ''
        }])
    lab = [
        {
            'course': 'Engineering Drawing Lab',
            'code': 'CE 110',
            'slot': 'AL' if data_map['Division'] in ['III', 'IV'] else 'ML',
            'instructor': 'CE110',
            'venue':'Engineering Drawing (Practical): 1203 and 1204, Academic Complex (AC)',
            'midsem':'',
            'endsem':''
        }
    ]

    if not isDesign:
        lab.extend([{
            'course': 'Chemistry Laboratory',
            'code': 'CH 110',
            'slot': 'ML' if data_map['Division'] in ['II', 'I'] else 'AL',
            'instructor': 'CH110',
            'venue':'Chemistry Laboratory: Department of Chemistry, Academic Complex (AC) ',
            'midsem':'',
            'endsem':''
        },
            {
            'course': 'Physics Laboratory' if data_map['Division'] in ['II', 'I'] else 'Workshop I',
            'code':'PH1 10' if data_map['Division'] in ['II', 'I'] else 'ME 110',
            'slot':'AL' if data_map['Division'] in ['III', 'IV'] else 'ML',
            'instructor': 'PH110' if data_map['Division'] in ['II', 'I'] else 'ME110',
            'venue':'Department of Physics, Academic Complex (AC)' if data_map['Division'] in ['II', 'I'] else 'Workshop (on the western side of Academic Complex (AC))',
            'midsem':'',
            'endsem':''
        }])

    if not isDesign:
        if data_map['Lab'] == 'L6' or data_map['Lab'] == 'L2':
            lab[1]['slot'] = lab[1]['slot']+'1'
            lab[2]['slot'] = lab[2]['slot']+'4'
            lab[0]['slot'] = lab[0]['slot']+'2'
        elif data_map['Lab'] == 'L7' or data_map['Lab'] == 'L2':
            lab[1]['slot'] = lab[1]['slot']+'3'
            lab[2]['slot'] = lab[2]['slot']+'1'
            lab[0]['slot'] = lab[0]['slot']+'4'
        elif data_map['Lab'] == 'L8' or data_map['Lab'] == 'L3':
            lab[1]['slot'] = lab[1]['slot']+'5'
            lab[2]['slot'] = lab[2]['slot']+'3'
            lab[0]['slot'] = lab[0]['slot']+'1'
        elif data_map['Lab'] == 'L9' or data_map['Lab'] == 'L4':
            lab[1]['slot'] = lab[1]['slot']+'2'
            lab[2]['slot'] = lab[2]['slot']+'5'
            lab[0]['slot'] = lab[0]['slot']+'3'
        elif data_map['Lab'] == 'L20' or data_map['Lab'] == 'L5':
            lab[1]['slot'] = lab[1]['slot']+'4'
            lab[2]['slot'] = lab[2]['slot']+'2'
            lab[0]['slot'] = lab[0]['slot']+'5'
    else:
        lab[0]['slot'] = 'AL5'


    # Get tt json
    tt_json = get_fresher_tt_slots()

    # adding timings to tut, lab and courses
    for c in courses:
        c['timings'] = tt_json[c['slot']]

    for t in tutorial:
        t['timings'] = tt_json[t['slot']]
        t['venue'] = data_map['Location']

    for l in lab:
        l['timings'] = tt_json[l['slot']]


    final_courses = courses+tutorial+lab
    for course in final_courses:
        course["midsem_venue"] = helper.return_venue(course["code"], roll_number, True)
        course["endsem_venue"] = helper.return_venue(course["code"], roll_number, False)

    return {
        'roll_number':roll_number,
        'courses': final_courses
    }