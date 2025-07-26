#!/usr/bin/env python3
"""
Docker-optimized Enrollment Fetcher Script
This script fetches all enrolled students and their courses from the IITG academic portal
and updates the enrolled_courses.csv file. Optimized for Docker container environments.
"""

import requests
import csv
import os
import glob
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from semester_constants import SEM_SESSION, SEM_YEAR

# Configure logging for both Docker and local environments
if os.path.exists('/code'):
    # Docker environment
    log_dir = '/code/logs'
    data_dir = '/code/data'
else:
    # Local development environment
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    data_dir = os.path.join(os.path.dirname(__file__), 'data')

os.makedirs(log_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'enrollment_fetcher.log')),
        logging.StreamHandler()
    ]
)

def get_session_cookies():
    """
    Get session cookies from the IITG academic portal
    Returns: cookies dictionary or None if failed
    """
    try:
        session = requests.Session()
        session.timeout = 30  # Add timeout for Docker environment
        response = session.get('https://academic.iitg.ac.in/sso/gen/students.jsp')
        response.raise_for_status()
        
        cookies = session.cookies.get_dict()
        logging.info(f"Successfully obtained session cookies")
        return session
    except requests.RequestException as e:
        logging.error(f"Failed to get session cookies: {e}")
        return None

def fetch_enrolled_courses(session):
    """
    Fetch enrolled courses data from the IITG portal
    Returns: HTML response text or None if failed
    """
    url = "https://academic.iitg.ac.in/sso/gen/student1.jsp"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Form data as specified in the requirements
    data = {
        'cid': 'All',
        'sess': SEM_SESSION,
        'yr': SEM_YEAR
    }
    
    try:
        response = session.post(url, headers=headers, data=data, timeout=30)
        response.raise_for_status()
        
        logging.info("Successfully fetched enrolled courses data")
        return response.text
    except requests.RequestException as e:
        logging.error(f"Failed to fetch enrolled courses: {e}")
        return None

def parse_html_to_csv(html_content):
    """
    Parse the HTML response and extract course enrollment data
    Returns: List of dictionaries containing course data
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the table with course data
    table = soup.find('table', class_='table table-striped')
    if not table:
        logging.error("Could not find the courses table in the HTML response")
        return []
    
    courses_data = []
    rows = table.find_all('tr')[1:]  # Skip header row
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 10:  # Ensure we have all required columns
            course_data = {
                'sl_no': cells[0].text.strip(),
                'student_name': cells[1].text.strip(),
                'roll_number': cells[2].text.strip(),
                'course_code': cells[3].text.strip(),
                'course_name': cells[4].text.strip(),
                'credit_audit': cells[5].text.strip(),
                'approval_status': cells[6].text.strip(),
                'adjustment_status': cells[7].text.strip(),
                'year': cells[8].text.strip(),
                'session': cells[9].text.strip()
            }
            
            # Only include approved courses
            status = course_data['approval_status'].lower()
            if status == 'approved' or status == 'pending':
                courses_data.append(course_data)
    
    logging.info(f"Parsed {len(courses_data)} approved course enrollments")
    return courses_data

def update_csv_file(courses_data):
    """
    Update the enrolled_courses.csv file with the new data
    """
    if os.path.exists('/code'):
        # Docker environment
        data_dir = '/code/data'
    else:
        # Local development environment
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    os.makedirs(data_dir, exist_ok=True)
    csv_file_path = os.path.join(data_dir, 'enrolled_courses.csv')
    
    # Remove previous backup files before creating a new one
    backup_pattern = f"{csv_file_path}.backup.*"
    existing_backups = glob.glob(backup_pattern)
    for backup_file in existing_backups:
        try:
            os.remove(backup_file)
            logging.info(f"Removed previous backup file: {backup_file}")
        except Exception as e:
            logging.warning(f"Could not remove backup file {backup_file}: {e}")
    
    # Create a backup of the existing file if it exists
    if os.path.exists(csv_file_path):
        backup_path = f"{csv_file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            os.rename(csv_file_path, backup_path)
            logging.info(f"Created backup at {backup_path}")
        except Exception as e:
            logging.warning(f"Could not create backup: {e}")
    
    # Write new data to CSV
    try:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            if courses_data:
                fieldnames = courses_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(courses_data)
                
                logging.info(f"Successfully updated {csv_file_path} with {len(courses_data)} records")
            else:
                # Write empty file with headers if no data
                fieldnames = ['sl_no', 'student_name', 'roll_number', 'course_code', 
                             'course_name', 'credit_audit', 'approval_status', 
                             'adjustment_status', 'year', 'session']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                logging.warning("No course data to write, created empty CSV with headers")
    except Exception as e:
        logging.error(f"Failed to update CSV file: {e}")
        raise

def main():
    """
    Main function to orchestrate the enrollment data fetching and updating
    """
    logging.info("Starting enrollment data fetch process (Docker version)")
    
    # Get session cookies
    session = get_session_cookies()
    if not session:
        logging.error("Failed to obtain session cookies, aborting")
        return False
    
    # Fetch enrolled courses data
    html_content = fetch_enrolled_courses(session)
    if not html_content:
        logging.error("Failed to fetch enrollment data, aborting")
        return False
    
    # Parse HTML and extract course data
    courses_data = parse_html_to_csv(html_content)
    if not courses_data:
        logging.warning("No course data found in the response")
    
    # Update CSV file
    try:
        update_csv_file(courses_data)
        logging.info("Enrollment data fetch and update completed successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to update CSV file: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
