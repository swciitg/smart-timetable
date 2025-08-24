"""
Enhanced fresher course handling with pre/post midsem filtering
"""

import pandas as pd
from datetime import datetime, timezone
from semester_constants import FRESHER_YEAR, MID_TIMINGS


def is_before_midsem():
    """
    Check if current date is before the last midsem exam date
    
    Returns:
        bool: True if before midsem period, False if after
    """
    # Get current date
    current_date = datetime.now(timezone.utc)
    
    # Find the latest midsem date
    midsem_dates = []
    for timing_str in MID_TIMINGS.values():
        midsem_date = datetime.fromisoformat(timing_str.replace('Z', '+00:00'))
        midsem_dates.append(midsem_date)
    
    latest_midsem = max(midsem_dates)
    
    return current_date < latest_midsem


def get_fresher_courses_enhanced(roll_number):
    """
    Get courses for freshers with enhanced filtering based on pre/post midsem
    
    Args:
        roll_number (str): Student roll number
        
    Returns:
        dict: Course data with proper filtering
    """
    # Check if this is a fresher
    if not (roll_number.startswith(FRESHER_YEAR + '01') or 
            roll_number.startswith(FRESHER_YEAR + '0205')):
        return None
    
    # First, get the student's enrolled courses
    try:
        enrolled_df = pd.read_csv('data/enrolled_courses.csv')
        enrolled_df['roll_number'] = enrolled_df['roll_number'].astype(str)
        
        # Get courses for this specific student
        student_courses = enrolled_df[enrolled_df['roll_number'] == roll_number]
        if len(student_courses) == 0:
            print(f"No enrolled courses found for roll number {roll_number}")
            return pd.DataFrame()
            
        # Get the course codes this student is enrolled in
        enrolled_course_codes = student_courses['course_code'].tolist()
        print(f"Student {roll_number} enrolled in {len(enrolled_course_codes)} courses: {enrolled_course_codes}")
        
    except FileNotFoundError:
        raise Exception("Enrolled courses CSV file not found")
    
    # Load fresher courses data for venue and pre/post midsem info
    try:
        freshers_df = pd.read_csv('data/freshers_courses.csv')
    except FileNotFoundError:
        print("Warning: Freshers courses CSV file not found, using main courses only")
        freshers_df = pd.DataFrame()
    
    # Load main courses data for additional details
    try:
        main_courses_df = pd.read_csv('data/courses_csv.csv')
    except FileNotFoundError:
        raise Exception("Main courses CSV file not found")
    
    # Filter main courses to only include the student's enrolled courses
    my_courses_df = main_courses_df[main_courses_df['code'].isin(enrolled_course_codes)].copy()
    
    if len(my_courses_df) == 0:
        print(f"No course details found in main CSV for enrolled courses")
        return pd.DataFrame()
    
    # Apply pre/post midsem filtering if fresher course data is available
    if not freshers_df.empty:
        # Filter based on pre/post midsem
        before_midsem = is_before_midsem()
        
        if before_midsem:
            # Before midsem: include courses where pre-mid is True or empty
            valid_pre_mid_courses = freshers_df[
                (freshers_df['pre-mid'] == True) | 
                (freshers_df['pre-mid'].isna()) |
                (freshers_df['pre-mid'] == '')
            ]['code'].tolist()
        else:
            # After midsem: include courses where pre-mid is False or empty
            valid_pre_mid_courses = freshers_df[
                (freshers_df['pre-mid'] == False) | 
                (freshers_df['pre-mid'].isna()) |
                (freshers_df['pre-mid'] == '')
            ]['code'].tolist()
        
        # Further filter by pre/post midsem validity
        my_courses_df = my_courses_df[my_courses_df['code'].isin(valid_pre_mid_courses)]
        
        # Merge with fresher-specific venue information
        my_courses_df = my_courses_df.merge(
            freshers_df[['code', 'venue']], 
            on='code', 
            how='left',
            suffixes=('_main', '_fresher')
        )
        
        # Use fresher venue if available, otherwise use main venue
        my_courses_df['venue'] = my_courses_df['venue_fresher'].fillna(my_courses_df['venue_main'])
        
        # Convert venue to string and handle NaN values
        my_courses_df['venue'] = my_courses_df['venue'].fillna('').astype(str)
        my_courses_df['venue'] = my_courses_df['venue'].replace('nan', '')  # Replace 'nan' strings with empty
        
        # Remove .0 suffix from venue numbers (e.g., "5401.0" -> "5401")
        my_courses_df['venue'] = my_courses_df['venue'].str.replace(r'\.0$', '', regex=True)
        
        # Drop temporary columns
        my_courses_df = my_courses_df.drop(columns=['venue_main', 'venue_fresher'])
    
    # Drop duplicates for each course code, keeping the first entry
    my_courses_df = my_courses_df.drop_duplicates(subset=['code'], keep='first')
    
    # Fill NaN values to avoid JSON errors
    my_courses_df = my_courses_df.fillna('')
    
    print(f"Final filtered courses: {len(my_courses_df)}")
    
    return my_courses_df


def format_fresher_courses_response(roll_number):
    """
    Format fresher courses into the expected API response format
    
    Args:
        roll_number (str): Student roll number
        
    Returns:
        dict: Formatted course data
    """
    from helper import ensure_string, mid_time, end_time, exam_venue
    
    # Get filtered courses
    my_courses_df = get_fresher_courses_enhanced(roll_number)
    
    if my_courses_df is None:
        return None
    
    data = {}
    my_courses_list = []
    
    for i in range(len(my_courses_df)):
        df_entry = my_courses_df.iloc[i]
        
        # Getting the timings JSON
        timing_json = {}
        day_columns = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        # Check if timing columns exist
        for day in day_columns:
            if day in my_courses_df.columns and df_entry[day] != "":
                timing_json[day] = df_entry[day]
        
        venue_str = str(df_entry['venue']) if pd.notna(df_entry['venue']) else ''
        # Remove .0 suffix from venue numbers
        venue_str = venue_str.replace('.0', '') if venue_str.endswith('.0') else venue_str
        
        my_courses_nullable = {
            'code': ensure_string(df_entry['code']),
            'course': ensure_string(df_entry['name']),
            'slot': ensure_string(df_entry['slot']),
            'instructor': ensure_string(df_entry['prof']),
            'venue': ensure_string(venue_str),
            'midsem': mid_time(df_entry['exam_slot']),
            'endsem': end_time(df_entry['exam_slot']),
            'timings': timing_json,
            'midsemVenue': exam_venue(df_entry['code'], roll_number, True),
            'endsemVenue': exam_venue(df_entry['code'], roll_number, False),
        }
        
        # Remove null/NaN values
        my_courses = {
            k: v for k, v in my_courses_nullable.items() 
            if not pd.isna(v) and v != ""
        }
        
        my_courses_list.append(my_courses)
    
    data['courses'] = my_courses_list
    data['is_fresher'] = True
    data['before_midsem'] = is_before_midsem()
    data['fresher_year'] = FRESHER_YEAR
    
    return data
