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
    
    Process:
    1. Get all enrolled courses for the student from enrolled_courses.csv
    2. Get course details from courses_csv.csv
    3. Apply freshers_courses.csv updates (venues, pre-mid filtering)
    4. Only drop courses based on pre-mid value, not based on presence in freshers_courses.csv
    
    Args:
        roll_number (str): Student roll number
        
    Returns:
        DataFrame: Filtered course data
    """
    # Check if this is a fresher
    if not (roll_number.startswith(FRESHER_YEAR + '01') or 
            roll_number.startswith(FRESHER_YEAR + '0205')):
        return None
    
    # Step 1: Get the student's enrolled courses
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
    
    # Step 2: Get course details from main courses CSV
    try:
        main_courses_df = pd.read_csv('data/courses_csv.csv')
    except FileNotFoundError:
        raise Exception("Main courses CSV file not found")
    
    # Get all enrolled courses from main courses data
    my_courses_df = main_courses_df[main_courses_df['code'].isin(enrolled_course_codes)].copy()
    
    if len(my_courses_df) == 0:
        print(f"No course details found in main CSV for enrolled courses")
        return pd.DataFrame()
    
    print(f"Found {len(my_courses_df)} courses in main CSV")
    
    # Step 3: Apply freshers_courses.csv updates
    try:
        freshers_df = pd.read_csv('data/freshers_courses.csv')
        
        # Merge to get fresher-specific updates
        my_courses_df = my_courses_df.merge(
            freshers_df[['code', 'venue', 'pre-mid']], 
            on='code', 
            how='left',
            suffixes=('_main', '_fresher')
        )
        
        # Use fresher venue if available, otherwise keep main venue
        my_courses_df['venue'] = my_courses_df['venue_fresher'].fillna(my_courses_df['venue_main'])
        
        # Step 4: Apply pre/post midsem filtering
        before_midsem = is_before_midsem()
        print(f"Before midsem: {before_midsem}")
        
        # Create a mask for courses to keep
        keep_course_mask = []
        
        for _, row in my_courses_df.iterrows():
            course_code = row['code']
            pre_mid = row['pre-mid']
            
            # Default: keep the course (for courses not in freshers_courses.csv)
            keep_course = True
            
            # Apply pre-mid filtering only if the course has pre-mid info
            if pd.notna(pre_mid):
                if before_midsem:
                    # Before midsem: keep if pre-mid is True
                    keep_course = (pre_mid == True)
                else:
                    # After midsem: keep if pre-mid is False
                    keep_course = (pre_mid == False)
                    
                print(f"  {course_code}: pre-mid={pre_mid}, keep={keep_course}")
            else:
                print(f"  {course_code}: no pre-mid info, keeping course")
            
            keep_course_mask.append(keep_course)
        
        # Apply the filter
        my_courses_df = my_courses_df[keep_course_mask]
        
        # Drop temporary columns
        cols_to_drop = [col for col in my_courses_df.columns if col.endswith(('_main', '_fresher'))]
        my_courses_df = my_courses_df.drop(columns=cols_to_drop)
        
    except FileNotFoundError:
        print("Warning: Freshers courses CSV file not found, using main courses only")
    
    # Convert venue to string and handle NaN values
    if 'venue' in my_courses_df.columns:
        my_courses_df['venue'] = my_courses_df['venue'].fillna('').astype(str)
        my_courses_df['venue'] = my_courses_df['venue'].replace('nan', '')  # Replace 'nan' strings with empty
        
        # Remove .0 suffix from venue numbers (e.g., "5401.0" -> "5401")
        my_courses_df['venue'] = my_courses_df['venue'].str.replace(r'\.0$', '', regex=True)
    
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
