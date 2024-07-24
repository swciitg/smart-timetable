import requests
import os
import csv
from semester_constants import *
from bs4 import BeautifulSoup

# POST request params
url = "https://academic.iitg.ac.in/sso/gen/student2.jsp"
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

def get_courses(roll_number):
    '''
    Gets all courses taken by a person

    This function makes a request to the IITG maintained endpoint
    https://academic.iitg.ac.in/sso/gen/student2.jsp and fetches all
    registered courses for an individual

    Sample response can be found in samples section as sample_response_get_courses.html

    Arguments:
        roll_number: a string
    Returns:
        A list of all courses of the person in HTML format
    '''
    payload = 'rno={}'.format(roll_number)
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

def get_course_codes(roll_number):
    '''
    Gets all course codes of the user for the current semester

    This function makes use of get_courses and generates all a list of
    all courses of an individual. This is the sample response format.

    ['CE 616', 'CS 508', 'CS 561', 'CS 581', 'HS 247', 'ME 620']

    Arguments:
        roll_number: a string
    Returns:
        All list of course codes taken by an individual
    '''

    jsp_response = get_courses(roll_number)
    course_code_list = []

    # FIXME: Make sure to change/update this erroneous string later if needed
    data_label = 'Couse Code'
    sem_session = SEM_SESSION
    sem_year = SEM_YEAR
    parsed_html = BeautifulSoup(jsp_response, features="html.parser")

    all_rows = parsed_html.body.find_all('tr')
    for row in all_rows:
        descendants = list(row.descendants)
        # Check if its the correct sem since all sem courses are displayed:
        if (sem_session in descendants and sem_year in descendants):
          # Add only if course is approved
            approval_status = row.find_all('td',{"data-label": "Status"})[-1].text
            if (approval_status == "Approved" or approval_status == ""):
              course_code_list.append(
                row.find('td', {"data-label": data_label}).text)
    
    # The following is a temporary measure since HSS do not update in sso soon
    # Comment the below once sso is updated
    roll_to_code = {}
    with open('data/hss.csv', 'r', newline='',encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(row)
            roll_to_code[row['roll']] = row['code']
    
    if roll_number in roll_to_code:
        if roll_to_code[roll_number] not in course_code_list:
            course_code_list.append(roll_to_code[roll_number])

    return course_code_list
