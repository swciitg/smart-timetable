import requests
import os
import csv
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

    Arguments:
        roll_number: a string
    Returns:
        A list of courses
    '''
    payload = 'rno={}'.format(roll_number)
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

def get_hss_code_for_roll(target_roll):
    try:
        with open('data/hss.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['roll'] == target_roll:
                    return row['code']
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' not found.")
    except Exception as e:
        print(f"Error: {e}")

    return ""

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
    sem_session = 'Jan-May'
    sem_year = '2024'
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
    
    tmp = get_hss_code_for_roll(roll_number)
    if tmp:
      course_code_list.append(tmp)
    return course_code_list
