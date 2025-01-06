import numpy as np
import pandas as pd
import re
import string
from fastapi import HTTPException

# created Python modules
from data import fetch_division_mapping, fetch_courses_df
import helper as hp


def get_fresher_tt_slots():
    # Get tt json
    ttJson = hp.read_TT()

    ttJson['B'].pop('Friday')
    ttJson['A'].pop('Monday')
    ttJson['E'].pop('Tuesday')
    ttJson['D'].pop('Wednesday')
    ttJson['C'].pop('Thursday')

    # Adding tutorial slots
    ttJson['b']['Friday'] = "8:00 - 8:55 AM"
    ttJson['a']['Monday'] = "8:00 - 8:55 AM"
    ttJson['e']['Tuesday'] = "8:00 - 8:55 AM"
    ttJson['d']['Wednesday'] = "8:00 - 8:55 AM"
    ttJson['c']['Thursday'] = "8:00 - 8:55 AM"
    return ttJson

def get_fresher_courses(roll_number, isDesign: bool = False):
    div_map = fetch_division_mapping(roll_number)

    # Correct for div 3
    # COMMON FOR BOTH BTECH & BDES
    courses = [
        # {
        #     'course': 'Engineering Drawing',
        #     'code': 'CE101',
        #     'slot': 'A',
        #     'venue': 'L2',
        #     'instructor': 'Baleshwar Singh',
        #     'ltpc': ' '
        # },
        # {
        #     'course': 'Basic Electronics',
        #     'code': 'EE101',
        #     'slot': 'C',
        #     'venue': 'L2',
        #     'instructor': 'A. Rajesh',
        #     'ltpc': ' '
        # },
        {
            'course': 'Engineering Mechanics',
            'code': 'ME101',
            'slot': 'A',
            'venue': '',
            'instructor': 'arupn, atanub, pankaj.biswas',
            'ltpc': ' '
        },
        {
            'course': 'Introduction to Computing',
            'code': 'CS101',
            'slot': 'D',
            'venue': '',
            'instructor': 'arijit, pinaki, ranbir, sushantak',
            'ltpc': ' '
        },
    ]
    # ONLY BTECH
    if not isDesign:
        courses.extend([
            # {
            #     'course': 'Mathematics - I',
            #     'code': 'MA101',
            #     'slot': 'B',
            #     'venue': 'L2',
            #     'instructor': 'Bhupen Deka',
            #     'ltpc': ' '
            # },
            # {
            #     'course': 'Chemistry',
            #     'code': 'CH101',
            #     'slot': 'D',
            #     'venue': 'L2',
            #     'instructor': 'A. Das, P. K. Kancharla, A. Chattopadhyay, C. V. Sastri',
            #     'ltpc': ' '
            # },
            # {
            #     'course': 'Physics - I',
            #     'code': 'PH101',
            #     'slot': 'E',
            #     'venue': 'L2',
            #     'instructor': 'Arunansu Sil',
            #     'ltpc': ' '
            # }
            {
                'course': 'Mathematics - II',
                'code': 'MA102',
                'slot': 'B',
                'venue': '',
                'instructor': 'kvsrikanth, natesan, shbora, vinay.wagh',
                'ltpc': ' '
            },
            {
                'course': 'Introductory Biology',
                'code': 'BT101',
                'slot': 'C',
                'venue': '',
                'instructor': 'csouptick, kapgupta, rsw, singh',
                'ltpc': ' '
            },
            {
                'course': 'Physics - II',
                'code': 'PH102',
                'slot': 'E',
                'venue': '',
                'instructor': 'debu, mckumar, sayan.chakrabarti, sovan',
                'ltpc': ' '
            }
        ])
    # ONLY BDES
    else:
        # Adding DD courses
        all_courses_df = fetch_courses_df()
        if (all_courses_df.empty):
            return HTTPException(status_code=404, detail='Courses CSV file not found. Please generate it first.')
        all_courses_df = all_courses_df.fillna('')
        design_courses = ["DD "+str(num) for num in range(111, 114)] # CHANGE THIS ACCORDING TO SEMESTER
        design_courses_df = all_courses_df.loc[all_courses_df['code'].isin(
            design_courses)]
        for _, df_entry in design_courses_df.iterrows():
            # Getting design course details
            #! There are some errors in midsem and endsem timetable and class time table due to random times of design courses
            my_courses = {
                'code': hp.ensure_string(df_entry['code']),
                'course': hp.ensure_string(df_entry['name']),
                'slot': hp.ensure_string(df_entry['slot']),
                'instructor': hp.ensure_string(df_entry['prof']),
                'venue': hp.ensure_string(df_entry['venue']),
                'midsem': '',
                'endsem': '',
                # 'midsem': hp.mid_time(df_entry['slot']) if hp.ensure_string(df_entry['code']) != "DD 105" else hp.mid_time("E"),
                # 'endsem': hp.end_time(df_entry['slot']) if hp.ensure_string(df_entry['code']) != "DD 105" else hp.end_time("E"),
            }  # According to https://www.iitg.ac.in/acad/classtt/1st_year_Course_wise_Instructor_name_and_exam_schedule.pdf , DD 105 exam slot is different
            my_courses = {
            k:v for k,v in my_courses.items() if not pd.isna(v)
            }
            courses.append(my_courses)

    if div_map['Division'] == 'I' or div_map['Division'] == 'II':
        for c in courses:
            c['slot'] = c['slot']+'1'
    if div_map['Division'] == 'II' or div_map['Division'] == 'IV':
        for c in courses:
            c['venue'] = 'L4'
    tutorial = [
        {
            'course': 'MA 102 Tutorial',
            'code': 'MA102',
            'slot': 'b',
            'instructor': '',
            'venue': '',
            'midsem': '',
            'endsem': ''
        },
        {
            'course': 'ME 101 Tutorial',
            'code': ' ME101',
            'slot': 'a',
            'venue': '',
            'instructor': '',
            'midsem': '',
            'endsem': ''
        }
        # {
        #     'course': 'EE 101 Tutorial',
        #     'code': ' EE101',
        #     'slot': 'c',
        #     'venue': '',
        #     'instructor': '',
        #     'midsem': '',
        #     'endsem': ''
        # }
    ]

    if not isDesign:
        tutorial.extend([
            # {
            #     'course': 'MA 101 Tutorial',
            #     'code': 'MA101',
            #     'slot': 'b',
            #     'instructor': '',
            #     'venue': '',
            #     'midsem': '',
            #     'endsem': ''
            # },
            # {
            #     'course': 'CH 101 Tutorial',
            #     'code': 'CH101',
            #     'slot': 'd',
            #     'venue': '',
            #     'instructor': '',
            #     'midsem': '',
            #     'endsem': ''
            # }
            {
                'course': 'MA 102 Tutorial',
                'code': 'MA102',
                'slot': 'b',
                'instructor': '',
                'venue': '',
                'midsem': '',
                'endsem': ''
            },
                {
                'course': 'PH 102 Tutorial',
                'code': 'PH102',
                'slot': 'e',
                'venue': '',
                'instructor': '',
                'midsem': '',
                'endsem': ''
            }
        ])
    
    # COMMON LABS FOR BTECH & BDES
    lab = [
        {
            'course': 'Basic Electronics Laboratory',
            'code': 'EE102',
            'slot': 'ML' if div_map['Division'] in ['III', 'IV'] else 'AL',
            'instructor': 'tonyj',
            'venue':'Basic Electronics Laboratory: Department of EEE, Academic Complex (AC)',
            'midsem':'',
            'endsem':''
        },
        {
            'course': 'Computing Laboratory',
            'code': 'CS110',
            'slot': 'ML' if div_map['Division'] in ['III', 'IV'] else 'AL',
            'instructor': 'anand.ashish',
            'venue':'Computation Laboratory: Department of CSE, Academic Complex (AC)',
            'midsem':'',
            'endsem':''
        },
        # {
        #     'course': 'Physics Laboratory' if div_map['Division'] in ['III', 'IV'] else 'Workshop I',
        #     'code':'PH110' if div_map['Division'] in ['III', 'IV'] else 'ME110',
        #     'slot':'AL' if div_map['Division'] in ['I', 'II'] else 'ML',
        #     'instructor': 'bhuyan, bkhazra, malli, saurabh, udaymaiti' if div_map['Division'] in ['III', 'IV'] else 'kanagaraj, psr, spanda, ssg',
        #     'venue':'Department of Physics, Academic Complex (AC)' if div_map['Division'] in ['III', 'IV'] else 'Workshop (on the western side of Academic Complex (AC))',
        #     'midsem':'',
        #     'endsem':''
        # }
    ]

    # lab = [
    #     {
    #         'course': 'Engineering Drawing (Practical)',
    #         'code': 'CE101',
    #         'slot': 'ML' if div_map['Division'] in ['II', 'I'] else 'AL',
    #         'instructor': '',
    #         'venue':'1203 and 1204, Academic Complex',
    #         'midsem':'',
    #         'endsem':''
    #     }
    # ]

    # ONLY FOR BTECH
    if not isDesign:
        lab.extend([{
        #     'course': 'Chemistry Laboratory',
        #     'code': 'CH110',
        #     'slot': 'ML' if div_map['Division'] in ['II', 'I'] else 'AL',
        #     'instructor': '',
        #     'venue':'Chemistry Laboratory: Department of Chemistry, Academic Complex (AC) ',
        #     'midsem':'',
        #     'endsem':''
        # },
        # {
            'course': 'Physics Laboratory' if div_map['Division'] in ['II', 'I'] else 'Workshop I',
            'code':'PH110' if div_map['Division'] in ['II', 'I'] else 'ME110',
            'slot':'AL' if div_map['Division'] in ['III', 'IV'] else 'ML',
            'instructor': 'bhuyan, bkhazra, malli, saurabh, udaymaiti' if div_map['Division'] in ['II', 'I'] else 'kanagaraj, psr, spanda, ss',
            'venue':'Department of Physics, Academic Complex (AC)' if div_map['Division'] in ['II', 'I'] else 'Workshop (on the western side of Academic Complex (AC))',
            'midsem':'',
            'endsem':''
        }])

    if not isDesign:
        if div_map['Lab'] == 'L6' or div_map['Lab'] == 'L1':
            lab[1]['slot'] = lab[1]['slot']+'1'
            lab[2]['slot'] = lab[2]['slot']+'4'
            lab[0]['slot'] = lab[0]['slot']+'2'
        elif div_map['Lab'] == 'L7' or div_map['Lab'] == 'L2':
            lab[1]['slot'] = lab[1]['slot']+'3'
            lab[2]['slot'] = lab[2]['slot']+'1'
            lab[0]['slot'] = lab[0]['slot']+'4'
        elif div_map['Lab'] == 'L8' or div_map['Lab'] == 'L3':
            lab[1]['slot'] = lab[1]['slot']+'5'
            lab[2]['slot'] = lab[2]['slot']+'3'
            lab[0]['slot'] = lab[0]['slot']+'1'
        elif div_map['Lab'] == 'L9' or div_map['Lab'] == 'L4':
            lab[1]['slot'] = lab[1]['slot']+'2'
            lab[2]['slot'] = lab[2]['slot']+'5'
            lab[0]['slot'] = lab[0]['slot']+'3'
        elif div_map['Lab'] == 'L10' or div_map['Lab'] == 'L5':
            lab[1]['slot'] = lab[1]['slot']+'4'
            lab[2]['slot'] = lab[2]['slot']+'2'
            lab[0]['slot'] = lab[0]['slot']+'5'
    else:
        if div_map['Lab'] == 'L6':
            lab[0]['slot'] = lab[0]['slot']+'2'
        elif div_map['Lab'] == 'L7':
            lab[0]['slot'] = lab[0]['slot']+'4'
        elif div_map['Lab'] == 'L8':
            lab[0]['slot'] = lab[0]['slot']+'1'
        elif div_map['Lab'] == 'L9':
            lab[0]['slot'] = lab[0]['slot']+'3'
        elif div_map['Lab'] == 'L10':
            lab[0]['slot'] = lab[0]['slot']+'5'

    # Get tt json
    ttJson = get_fresher_tt_slots()

    # adding timings to tut, lab and courses
    for c in courses:
        c['timings'] = ttJson[c['slot']]
        c['midsem'] = hp.mid_time(c['slot'])
        c['endsem'] = hp.end_time(c['slot'])

    for t in tutorial:
        t['timings'] = ttJson[t['slot']]
        t['venue'] = div_map['Location']

    for l in lab:
        l['timings'] = ttJson[l['slot']]

    return {
        'roll_number': roll_number,
        'courses': courses+tutorial+lab
    }
