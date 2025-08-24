import os
import csv
import logging
from semester_constants import *

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_course_codes_from_csv(roll_number):
    '''
    Gets all course codes of the user for the current semester from CSV file
    
    This function reads from the enrolled_courses.csv file that is updated 
    by the cron job and returns courses for the specified roll number.

    Arguments:
        roll_number: a string
    Returns:
        A list of course codes taken by an individual
    '''
    # Check if running in Docker container
    if os.path.exists('/code/data'):
        csv_file_path = '/code/data/enrolled_courses.csv'
    else:
        # Local development path
        script_dir = os.path.dirname(__file__)
        csv_file_path = os.path.join(script_dir, 'data', 'enrolled_courses.csv')
    
    # Check if CSV file exists
    if not os.path.exists(csv_file_path):
        logging.error(f"Enrolled courses CSV file not found at {csv_file_path}")
        return []
    
    course_codes = []
    
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Check if this row is for the requested roll number
                if row['roll_number'] == roll_number:
                    # Check if it's for the current semester
                    if (row['session'] == SEM_SESSION and 
                        row['year'] == SEM_YEAR and 
                        row['approval_status'].lower() == 'approved'):
                        course_code = row['course_code'].strip()
                        if course_code and course_code not in course_codes:
                            course_codes.append(course_code)
        
        logging.info(f"Found {len(course_codes)} courses for roll number {roll_number}")
        return course_codes
    
    except Exception as e:
        logging.error(f"Error reading enrolled courses CSV: {e}")
        return []

