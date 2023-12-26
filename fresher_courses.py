import numpy as np
import pandas as pd
import re
import string
import helper as hp
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
            'course': 'Engineering Mechanics',
            'code': 'ME101',
            'slot': 'A',
            'venue': 'L2',
            'instructor': 'ME101',
            'midsem': '',
            'endsem': ''
        },
        {
            'course': 'Introduction to Computing',
            'code': 'CS101',
            'slot': 'D',
            'venue': 'L2',
            'instructor': 'CS101',
            'ltpc': ' ',
            "midsem": "2023-09-19T14:00:00.000Z",
            "endsem": "2023-11-20T14:00:00.000Z"
        },
       
        # {
        #     'course': 'Mathematics - II',
        #     'code': 'MA102',
        #     'slot': 'B',
        #     'venue': 'L2',
        #     'instructor': 'MA102',
        #     'ltpc': ' ',
        #     "midsem": "2023-09-19T14:00:00.000Z",
        #     "endsem": "2023-11-20T14:00:00.000Z"
        # },
        # {
        #     'course': 'Introductory Biology',
        #     'code': 'BT101',
        #     'slot': 'C',
        #     'venue': 'L2',
        #     'instructor': 'BT101',
        #     'ltpc': ' ',
        #     "midsem": "2023-09-20T14:00:00.000Z",
        #     "endsem": "2023-11-21T14:00:00.000Z"
        # }
    ]
    if not isDesign:
        courses.extend([{
            'course': 'Mathematics - II',
            'code': 'MA102',
            'slot': 'B',
            'venue': 'L2',
            'instructor': 'MA102',
            'ltpc': ' ',
            "midsem": "2023-09-19T14:00:00.000Z",
            "endsem": "2023-11-20T14:00:00.000Z"
        },
        {
            'course': 'Introductory Biology',
            'code': 'BT101',
            'slot': 'C',
            'venue': 'L2',
            'instructor': 'BT101',
            'ltpc': ' ',
            "midsem": "2023-09-20T14:00:00.000Z",
            "endsem": "2023-11-21T14:00:00.000Z"
        },
        {
            'course': 'Physics - II',
            'code': 'PH102',
            'slot': 'E',
            'venue': 'L2',
            'instructor': 'PH102',
            'ltpc': ' ',
            "midsem": "2023-09-20T14:00:00.000Z",
            "endsem": "2023-11-21T14:00:00.000Z"
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

    if data_map['Division'] == 'III' or data_map['Division'] == 'IV':
        for c in courses:
            c['slot'] = c['slot']+'1'
    if data_map['Division'] == 'II' or data_map['Division'] == 'IV':
        for c in courses:
            c['venue'] = 'L4'
    tutorial = [
        # {
        #     'course': 'MA 102 Tutorial',
        #     'code': 'MA102',
        #     'slot': 'b',
        #     'instructor': 'MA102',
        #     'venue': '',
        #     'midsem': '',
        #     'endsem': ''
        # },
        {
            'course': 'ME 101 Tutorial',
            'code': ' ME101',
            'slot': 'a',
            'venue': '',
            'instructor': 'ME101',
            'midsem': '',
            'endsem': ''
        }
    ]

    if not isDesign:
        tutorial.extend([{
            'course': 'MA 102 Tutorial',
            'code': 'MA102',
            'slot': 'b',
            'instructor': 'MA102',
            'venue': '',
            'midsem': '',
            'endsem': ''
        },
            {
            'course': 'PH 102 Tutorial',
            'code': 'PH102',
            'slot': 'e',
            'venue': '',
            'instructor': 'PH102',
            'midsem': '',
            'endsem': ''
        }])

    lab = [
        {
            'course': 'Basic Electronics Laboratory',
            'code': 'EE102',
            'slot': 'ML' if data_map['Division'] in ['III', 'IV'] else 'AL',
            'instructor': 'EE102',
            'venue':'Basic Electronics Laboratory: Department of EEE, Academic Complex (AC)',
            'midsem':'',
            'endsem':''
        },
        {
            'course': 'Computing Laboratory',
            'code': 'CS110',
            'slot': 'ML' if data_map['Division'] in ['III', 'IV'] else 'AL',
            'instructor': 'CS110',
            'venue':'Computation Laboratory: Department of CSE, Academic Complex (AC)',
            'midsem':'',
            'endsem':''
        },
        {
            'course': 'Physics Laboratory' if data_map['Division'] in ['III', 'IV'] else 'Workshop I',
            'code':'PH110' if data_map['Division'] in ['III', 'IV'] else 'ME110',
            'slot':'AL' if data_map['Division'] in ['I', 'II'] else 'ML',
            'instructor': 'PH110' if data_map['Division'] in ['III', 'IV'] else 'ME110',
            'venue':'Department of Physics, Academic Complex (AC)' if data_map['Division'] in ['III', 'IV'] else 'Workshop (on the western side of Academic Complex (AC))',
            'midsem':'',
            'endsem':''
        }
    ]

    # if not isDesign:
    #     lab.extend([{
    #         'course': 'Chemistry Laboratory',
    #         'code': 'CH110',
    #         'slot': 'ML' if data_map['Division'] in ['II', 'I'] else 'AL',
    #         'instructor': 'CH110',
    #         'venue':'Chemistry Laboratory: Department of Chemistry, Academic Complex (AC) ',
    #         'midsem':'',
    #         'endsem':''
    #     },
    #         {
    #         'course': 'Physics Laboratory' if data_map['Division'] in ['II', 'I'] else 'Workshop I',
    #         'code':'PH110' if data_map['Division'] in ['II', 'I'] else 'ME110',
    #         'slot':'AL' if data_map['Division'] in ['III', 'IV'] else 'ML',
    #         'instructor': 'PH110' if data_map['Division'] in ['II', 'I'] else 'ME110',
    #         'venue':'Department of Physics, Academic Complex (AC)' if data_map['Division'] in ['II', 'I'] else 'Workshop (on the western side of Academic Complex (AC))',
    #         'midsem':'',
    #         'endsem':''
    #     }])

    if not isDesign:
        if data_map['Lab'] == 'L6' or data_map['Lab'] == 'L1':
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
        elif data_map['Lab'] == 'L10' or data_map['Lab'] == 'L5':
            lab[1]['slot'] = lab[1]['slot']+'4'
            lab[2]['slot'] = lab[2]['slot']+'2'
            lab[0]['slot'] = lab[0]['slot']+'5'
    else:
        lab[0]['slot'] = 'ML5'

    # for i in range(len(courses)):
    #     courses[i]['midsem'] = helper.get_midsem_time(courses[i]['slot'])
    #     courses[i]['endsem'] = helper.get_endsem_time(courses[i]['slot'])

    # Get tt json
    tt_json = get_fresher_tt_slots()

    # adding timings to tut, lab and courses
    for c in courses:
        c['timings'] = tt_json[c['slot']]
        c['midsem'] = hp.get_midsem_time(c['slot'])
        c['endsem'] = hp.get_endsem_time(c['slot'])

    for t in tutorial:
        t['timings'] = tt_json[t['slot']]
        t['venue'] = data_map['Location']

    for l in lab:
        l['timings'] = tt_json[l['slot']]

    return {
        'roll_number': roll_number,
        'courses': courses+tutorial+lab
    }
