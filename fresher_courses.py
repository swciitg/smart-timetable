import numpy as np
import pandas as pd
import re
import string

# created Python modules
import ocr
import helper

time_slots = ["08:00 - 08:55 AM", "09:00 - 09:55 AM", "10:00 - 10:55 AM", "11:00 - 11:55 AM",
              "12:00 - 12:55 PM", "1:00 - 1:55 PM", "2:00 - 2:55 PM", "3:00 - 3:55 PM", "4:00 - 4:55 PM", "5:00 - 5:55 PM"]


def get_designfresher_courses(roll_number):
    data_map = ocr.get_fresher_DF(roll_number)

    # Correct for div 3
    courses = [
        {
            'course': 'Engineering Drawing',
            'code': 'CE101',
            'slot': 'A',
            'venue': 'L2',
            'instructor': 'CE101',
            'ltpc': ' ',
            'midsem': '',
            'endsem': '',
            'time': {
                'monday': '',
                'tuesday': '',
                'wednesday': '',
                'thursday': '',
                'friday': ''
            },
            'midVenue': '',
            'endVenue': ''
        },
        {
            'course': 'Mathematics - I',
            'code': 'MA101',
            'slot': 'B',
            'venue': 'L2',
            'instructor': 'MA101',
            "midsem": "2023-09-19T14:00:00.000Z",
            "endsem": "2023-11-20T14:00:00.000Z",
            'time': {
                'monday': '',
                'tuesday': '',
                'wednesday': '',
                'thursday': '',
                'friday': ''
            },
            'midVenue': '',
            'endVenue': ''
        },
    ]
    if data_map['Division'] == 'III' or data_map['Division'] == 'IV':
        for c in courses:
            c['slot'] = c['slot']+'1'
    if data_map['Division'] == 'II' or data_map['Division'] == 'IV':
        for c in courses:
            c['venue'] = 'L4'
    tutorial = [
        {
            'course': 'MA 101 Tutorial',
            'code': 'MA101',
            'slot': 'b',
            'instructor': data_map['Location'],
            'venue':'',
            'ltpc':' ',
            'midsem':'',
            'endsem':'',
            'time': {
                'monday': '',
                'tuesday': '',
                'wednesday': '',
                'thursday': '',
                'friday': ''
            },
            'midVenue': '',
            'endVenue': ''
        },
    ]
    lab = [
        {
            'course': 'Engineering Drawing Lab',
            'code': 'CE110',
            'slot': 'AL' if data_map['Division'] in ['III', 'IV'] else 'ML',
            'instructor':'CE110',
            'venue':'Engineering Drawing (Practical): 1203 and 1204, Academic Complex (AC)',
            'ltpc':' ',
            'midsem':'',
            'endsem':'',
            'time': {
                'monday': '',
                'tuesday': '',
                'wednesday': '',
                'thursday': '',
                'friday': ''
            },
            'midVenue': '',
            'endVenue': ''
        },
    ]

    for i in range(len(courses)):
        if courses[i]['slot'] == "A":
            courses[i]['time']['monday'] = time_slots[0]
            courses[i]['time']['tuesday'] = time_slots[1]
            courses[i]['time']['wednesday'] = time_slots[2]
            courses[i]['time']['thursday'] = time_slots[3]
        if courses[i]['slot'] == "B":
            courses[i]['time']['monday'] = time_slots[1]
            courses[i]['time']['tuesday'] = time_slots[2]
            courses[i]['time']['wednesday'] = time_slots[3]
            courses[i]['time']['friday'] = time_slots[0]
        if courses[i]['slot'] == "C":
            courses[i]['time']['monday'] = time_slots[2]
            courses[i]['time']['tuesday'] = time_slots[3]
            courses[i]['time']['thursday'] = time_slots[1]
            courses[i]['time']['friday'] = time_slots[0]
        if courses[i]['slot'] == "D":
            courses[i]['time']['monday'] = time_slots[3]
            courses[i]['time']['wednesday'] = time_slots[0]
            courses[i]['time']['thursday'] = time_slots[1]
            courses[i]['time']['friday'] = time_slots[2]
        if courses[i]['slot'] == "E":
            courses[i]['time']['tuesday'] = time_slots[0]
            courses[i]['time']['wednesday'] = time_slots[1]
            courses[i]['time']['thursday'] = time_slots[2]
        if courses[i]['slot'] == "F":
            courses[i]['time']['monday'] = time_slots[4]
            courses[i]['time']['tuesday'] = time_slots[4]
            courses[i]['time']['friday'] = time_slots[3]
        if courses[i]['slot'] == "G":
            courses[i]['time']['wednesday'] = time_slots[4]
            courses[i]['time']['thursday'] = time_slots[4]
            courses[i]['time']['friday'] = time_slots[4]
        if courses[i]['slot'] == "A1":
            courses[i]['time']['monday'] = time_slots[9]
            courses[i]['time']['tuesday'] = time_slots[8]
            courses[i]['time']['wednesday'] = time_slots[7]
            courses[i]['time']['thursday'] = time_slots[6]
        if courses[i]['slot'] == "B1":
            courses[i]['time']['monday'] = time_slots[8]
            courses[i]['time']['tuesday'] = time_slots[7]
            courses[i]['time']['wednesday'] = time_slots[6]
            courses[i]['time']['friday'] = time_slots[9]
        if courses[i]['slot'] == "C1":
            courses[i]['time']['monday'] = time_slots[7]
            courses[i]['time']['tuesday'] = time_slots[6]
            courses[i]['time']['thursday'] = time_slots[9]
            courses[i]['time']['friday'] = time_slots[8]
        if courses[i]['slot'] == "D1":
            courses[i]['time']['monday'] = time_slots[6]
            courses[i]['time']['wednesday'] = time_slots[9]
            courses[i]['time']['thursday'] = time_slots[8]
            courses[i]['time']['friday'] = time_slots[7]
        if courses[i]['slot'] == "E1":
            courses[i]['time']['tuesday'] = time_slots[9]
            courses[i]['time']['wednesday'] = time_slots[8]
            courses[i]['time']['thursday'] = time_slots[7]
        if courses[i]['slot'] == "F1":
            courses[i]['time']['monday'] = time_slots[5]
            courses[i]['time']['tuesday'] = time_slots[5]
            courses[i]['time']['friday'] = time_slots[6]
        if courses[i]['slot'] == "G1":
            courses[i]['time']['wednesday'] = time_slots[5]
            courses[i]['time']['thursday'] = time_slots[5]
            courses[i]['time']['friday'] = time_slots[5]

    return {
        'roll_number': roll_number,
        'courses': courses+tutorial+lab
    }


def get_fresher_courses(roll_number):
    data_map = ocr.get_fresher_DF(roll_number)
    print("apple")
    # Correct for div 3
    courses = [
        {
            'course': 'Engineering Drawing',
            'code': 'CE101',
            'slot': 'A',
            'venue': 'L2',
            'instructor': 'CE101',
            'midsem': '',
            'endsem': '',
            'time': {
                'monday': '',
                'tuesday': '',
                'wednesday': '',
                'thursday': '',
                'friday': ''
            },
            'midVenue': '',
            'endVenue': ''
        },
        {
            'course': 'Mathematics - I',
            'code': 'MA101',
            'slot': 'B',
            'venue': 'L2',
            'instructor': 'MA101',
            'ltpc': ' ',
            "midsem": "2023-09-19T14:00:00.000Z",
            "endsem": "2023-11-20T14:00:00.000Z",
            'time': {
                'monday': '',
                'tuesday': '',
                'wednesday': '',
                'thursday': '',
                'friday': ''
            },
            'midVenue': '',
            'endVenue': ''
        },
        {
            'course': 'Basic Electronics',
            'code': 'EE101',
            'slot': 'C',
            'venue': 'L2',
            'instructor': 'EE101',
            'ltpc': ' ',
            "midsem": "2023-09-20T14:00:00.000Z",
            "endsem": "2023-11-21T14:00:00.000Z",
            'time': {
                'monday': '',
                'tuesday': '',
                'wednesday': '',
                'thursday': '',
                'friday': ''
            },
            'midVenue': '',
            'endVenue': ''
        },
        {
            'course': 'Chemistry',
            'code': 'CH101',
            'slot': 'D',
            'venue': 'L2',
            'instructor': 'CH101',
            "midsem": "2023-09-21T14:00:00.000Z",
            "endsem": "2023-11-22T14:00:00.000Z",
            'time': {
                'monday': '',
                'tuesday': '',
                'wednesday': '',
                'thursday': '',
                'friday': ''
            },
            'midVenue': '',
            'endVenue': ''
        },
        {
            'course': 'Physics - I',
            'code': 'PH101',
            'slot': 'E',
            'venue': 'L2',
            'instructor': 'PH101',
            "midsem": "2023-09-22T14:00:00.000Z",
            "endsem": "2023-11-23T14:00:00.000Z",
            'time': {
                'monday': '',
                'tuesday': '',
                'wednesday': '',
                'thursday': '',
                'friday': ''
            },
            'midVenue': '',
            'endVenue': ''
        }
    ]
    if data_map['Division'] == 'I' or data_map['Division'] == 'II':
        for c in courses:
            c['slot'] = c['slot']+'1'
    if data_map['Division'] == 'II' or data_map['Division'] == 'IV':
        for c in courses:
            c['venue'] = 'L4'
    tutorial = [
        {
            'course': 'MA 101 Tutorial',
            'code': 'MA101',
            'slot': 'b',
            'instructor': data_map['Location'],
            'venue': '',
            'midsem':'',
            'endsem':'',
            'time': {
                'monday': '',
                'tuesday': '',
                'wednesday': '',
                'thursday': '',
                'friday': ''
            },
            'midVenue': '',
            'endVenue': ''
        },
        {
            'course': 'EE 101 Tutorial',
            'code': 'EE101',
            'slot': 'c',
            'venue': '',
            'instructor': data_map['Location'],
            'midsem':'',
            'endsem':'',
            'time': {
                'monday': '',
                'tuesday': '',
                'wednesday': '',
                'thursday': '',
                'friday': ''
            },
            'midVenue': '',
            'endVenue': ''
        },
        {
            'course': 'CH 101 Tutorial',
            'code': 'CH101',
            'venue': '',
            'slot': 'd',
            'instructor': data_map['Location'],
            'midsem':'',
            'endsem':'',
            'time': {
                'monday': '',
                'tuesday': '',
                'wednesday': '',
                'thursday': '',
                'friday': ''
            },
            'midVenue': '',
            'endVenue': ''
        },
        {
            'course': 'PH 101 Tutorial',
            'code': 'PH101',
            'slot': 'e',
            'venue': '',
            'instructor': data_map['Location'],
            'midsem':'',
            'endsem':'',
            'time': {
                'monday': '',
                'tuesday': '',
                'wednesday': '',
                'thursday': '',
                'friday': ''
            },
            'midVenue': '',
            'endVenue': ''
        },
    ]
    lab = [
        {
            'course': 'Chemistry Laboratory',
            'code': 'CH110',
            'slot': 'ML' if data_map['Division'] in ['II', 'I'] else 'AL',
            'instructor': 'CH110',
            'venue':'Chemistry Laboratory: Department of Chemistry, Academic Complex (AC) ',
            'midsem':'',
            'endsem':'',
            'time': {
                'monday': '',
                'tuesday': '',
                'wednesday': '',
                'thursday': '',
                'friday': ''
            },
            'midVenue': '',
            'endVenue': ''
        },
        {
            'course': 'Physics Laboratory' if data_map['Division'] in ['II', 'I'] else 'Workshop I',
            'code':'PH110' if data_map['Division'] in ['II', 'I'] else 'ME110',
            'slot':'AL' if data_map['Division'] in ['III', 'IV'] else 'ML',
            'instructor': 'PH110' if data_map['Division'] in ['II', 'I'] else 'ME110',
            'venue':'Department of Physics, Academic Complex (AC)' if data_map['Division'] in ['II', 'I'] else 'Workshop (on the western side of Academic Complex (AC))',
            'midsem':'',
            'endsem':'',
            'time': {
                'monday': '',
                'tuesday': '',
                'wednesday': '',
                'thursday': '',
                'friday': ''
            },
            'midVenue': '',
            'endVenue': ''
        },
        {
            'course': 'Engineering Drawing Lab',
            'code': 'CE110',
            'slot': 'AL' if data_map['Division'] in ['III', 'IV'] else 'ML',
            'instructor': 'CE110',
            'venue':'Engineering Drawing (Practical): 1203 and 1204, Academic Complex (AC)',
            'midsem':'',
            'endsem':'',
            'time': {
                'monday': '',
                'tuesday': '',
                'wednesday': '',
                'thursday': '',
                'friday': ''
            },
            'midVenue': '',
            'endVenue': ''
        },
    ]
    if data_map['Lab'] == 'L6' or data_map['Lab'] == 'L2':
        lab[0]['slot'] = lab[0]['slot']+'1'
        lab[1]['slot'] = lab[1]['slot']+'4'
        lab[2]['slot'] = lab[2]['slot']+'2'
    elif data_map['Lab'] == 'L7' or data_map['Lab'] == 'L2':
        lab[0]['slot'] = lab[0]['slot']+'3'
        lab[1]['slot'] = lab[1]['slot']+'1'
        lab[2]['slot'] = lab[2]['slot']+'4'
    elif data_map['Lab'] == 'L8' or data_map['Lab'] == 'L3':
        lab[0]['slot'] = lab[0]['slot']+'5'
        lab[1]['slot'] = lab[1]['slot']+'3'
        lab[2]['slot'] = lab[2]['slot']+'1'
    elif data_map['Lab'] == 'L9' or data_map['Lab'] == 'L4':
        lab[0]['slot'] = lab[0]['slot']+'2'
        lab[1]['slot'] = lab[1]['slot']+'5'
        lab[2]['slot'] = lab[2]['slot']+'3'
    elif data_map['Lab'] == 'L20' or data_map['Lab'] == 'L5':
        lab[0]['slot'] = lab[0]['slot']+'4'
        lab[1]['slot'] = lab[1]['slot']+'2'
        lab[2]['slot'] = lab[2]['slot']+'5'

    for i in range(len(courses)):
        if courses[i]['slot'] == "A":
            courses[i]['time']['monday'] = time_slots[0]
            courses[i]['time']['tuesday'] = time_slots[1]
            courses[i]['time']['wednesday'] = time_slots[2]
            courses[i]['time']['thursday'] = time_slots[3]
        if courses[i]['slot'] == "B":
            courses[i]['time']['monday'] = time_slots[1]
            courses[i]['time']['tuesday'] = time_slots[2]
            courses[i]['time']['wednesday'] = time_slots[3]
            courses[i]['time']['friday'] = time_slots[0]
        if courses[i]['slot'] == "C":
            courses[i]['time']['monday'] = time_slots[2]
            courses[i]['time']['tuesday'] = time_slots[3]
            courses[i]['time']['thursday'] = time_slots[1]
            courses[i]['time']['friday'] = time_slots[0]
        if courses[i]['slot'] == "D":
            courses[i]['time']['monday'] = time_slots[3]
            courses[i]['time']['wednesday'] = time_slots[0]
            courses[i]['time']['thursday'] = time_slots[1]
            courses[i]['time']['friday'] = time_slots[2]
        if courses[i]['slot'] == "E":
            courses[i]['time']['tuesday'] = time_slots[0]
            courses[i]['time']['wednesday'] = time_slots[1]
            courses[i]['time']['thursday'] = time_slots[2]
        if courses[i]['slot'] == "F":
            courses[i]['time']['monday'] = time_slots[4]
            courses[i]['time']['tuesday'] = time_slots[4]
            courses[i]['time']['friday'] = time_slots[3]
        if courses[i]['slot'] == "G":
            courses[i]['time']['wednesday'] = time_slots[4]
            courses[i]['time']['thursday'] = time_slots[4]
            courses[i]['time']['friday'] = time_slots[4]
        if courses[i]['slot'] == "A1":
            courses[i]['time']['monday'] = time_slots[9]
            courses[i]['time']['tuesday'] = time_slots[8]
            courses[i]['time']['wednesday'] = time_slots[7]
            courses[i]['time']['thursday'] = time_slots[6]
        if courses[i]['slot'] == "B1":
            courses[i]['time']['monday'] = time_slots[8]
            courses[i]['time']['tuesday'] = time_slots[7]
            courses[i]['time']['wednesday'] = time_slots[6]
            courses[i]['time']['friday'] = time_slots[9]
        if courses[i]['slot'] == "C1":
            courses[i]['time']['monday'] = time_slots[7]
            courses[i]['time']['tuesday'] = time_slots[6]
            courses[i]['time']['thursday'] = time_slots[9]
            courses[i]['time']['friday'] = time_slots[8]
        if courses[i]['slot'] == "D1":
            courses[i]['time']['monday'] = time_slots[6]
            courses[i]['time']['wednesday'] = time_slots[9]
            courses[i]['time']['thursday'] = time_slots[8]
            courses[i]['time']['friday'] = time_slots[7]
        if courses[i]['slot'] == "E1":
            courses[i]['time']['tuesday'] = time_slots[9]
            courses[i]['time']['wednesday'] = time_slots[8]
            courses[i]['time']['thursday'] = time_slots[7]
        if courses[i]['slot'] == "F1":
            courses[i]['time']['monday'] = time_slots[5]
            courses[i]['time']['tuesday'] = time_slots[5]
            courses[i]['time']['friday'] = time_slots[6]
        if courses[i]['slot'] == "G1":
            courses[i]['time']['wednesday'] = time_slots[5]
            courses[i]['time']['thursday'] = time_slots[5]
            courses[i]['time']['friday'] = time_slots[5]

    return {
        'roll_number': roll_number,
        'courses': courses+tutorial+lab
    }
