import requests
import os

# POST request params
url = "https://academic.iitg.ac.in/sso/gen/student2.jsp"
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Locally stored PDF
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
COURSES_PDF_PATH = os.path.join(BASE_DIR, 'samples/courses.pdf')

# URL stored PDF
COURSES_URL = 'https://iitg.ac.in/acad/pdfs/Courses_Winter_2022.pdf'


def get_courses(roll_number):
    '''
    Gets all courses taken by a person

    This function makes a request to the IITG maintained endpoint
    https://academic.iitg.ac.in/sso/gen/student2.jsp and fetches all
    registered courses for an individual

    Arguments:
        roll_number: a string
    Returns:
        A list of courses
    '''
    payload = 'rno={}'.format(roll_number)
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


def get_courses_parsed(roll_number):
    '''
    Gets all courses with additional details in a JSON format

    This function makes use of get_courses and generates all a JSON
    with all courses of an individual. This is the sample response format.
    {
      roll_number: '180123062',
      courses:[
        {
          code: 'BT202M',
          course: 'Molecular Biotechnology',
          ltpc: '3 0 0 6',
          slot: 'G',
          instructor: 'Dr. Jaganathan B. G'.
        },
        {
          code: 'BT202M',
          course: 'Molecular Biotechnology',
          ltpc: '3 0 0 6',
          slot: 'G',
          instructor: 'Dr. Jaganathan B. G'.
        }
      ]
    }

    Arguments:
        roll_number: a string
    Returns:
        All courses taken by an individual with more details
    '''
    jsp_response = get_courses(roll_number)
    course_code_list = []

    # FIXME: Make sure to change/update this erroneous string later if needed
    data_label = 'Couse Code'

    for line in jsp_response.split('\n'):
        if data_label in line:
            table_entry = line.strip()
            course_code = table_entry.split('>')[1].split('<')[0]
            course_code_list.append(course_code.replace(' ', ''))

    return course_code_list
