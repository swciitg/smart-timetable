import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
from initialise_timings import add_timings_to_course_csv
import os
import time

# pip3 install requests pandas beautifulsoup4 lxml

def extract_iitg_courses():
    """
    Extract all course data from IITG time table page.
    The website has paginated data, so we need to handle multiple pages.
    """
    # URL of the IITG time table page
    URL = "https://iitg.ac.in/acad/time_table.php"
    
    # Headers to mimic a real browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    print("🔄 Fetching data from IITG time table page...")
    
    # Create a session to maintain cookies for pagination
    session = requests.Session()
    session.headers.update(headers)
    
    response = session.get(URL)
    response.raise_for_status()
    
    print("📄 Parsing HTML content...")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table with id="dataTable"
    table = soup.find('table', {'id': 'dataTable'})
    if not table:
        raise Exception("Could not find the data table on the page")
    
    # Extract table headers - get the first row without filters
    thead = table.find('thead')
    if not thead:
        raise Exception("Could not find table headers")
    
    # Get the first row (not the filter row)
    header_rows = thead.find_all('tr')
    header_row = header_rows[0]  # First row contains actual headers
    headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
    print(f"📋 Found columns: {headers}")
    
    # Since the table is paginated via JavaScript, we'll extract all data from the current page
    # The DataTable might load all data initially and paginate client-side
    all_data = []
    
    # Extract table body data
    tbody = table.find('tbody')
    if not tbody:
        raise Exception("Could not find table body")
    
    rows = tbody.find_all('tr')
    print(f"🔢 Found {len(rows)} course entries on current page")
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= len(headers) - 1:  # -1 because last column might be empty
            row_data = []
            for i, cell in enumerate(cells[:len(headers)]):
                # Clean up text content
                text = cell.get_text(strip=True)
                # Remove extra whitespace and normalize
                text = re.sub(r'\s+', ' ', text)
                row_data.append(text)
            
            # Pad with empty strings if row is shorter than headers
            while len(row_data) < len(headers):
                row_data.append('')
            
            all_data.append(row_data)
    
    print(f"✅ Successfully extracted {len(all_data)} course records")
    
    # Create DataFrame
    df = pd.DataFrame(all_data, columns=headers)
    
    # Clean up the DataFrame
    print("🧹 Cleaning data...")
    
    # Remove any completely empty rows
    df = df.dropna(how='all')
    
    # Remove the last column if it's empty (often an artifacts column)
    if len(df.columns) > 0 and (df.columns[-1] == '' or df.iloc[:, -1].str.strip().eq('').all()):
        df = df.iloc[:, :-1]
    
    # Strip whitespace from all string columns
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
    
    # Replace empty strings with None for better data quality
    df = df.replace('', None)
    
    return df

def parse_day_time_to_lab_code(slot_text):
    """
    Convert day+time patterns like 'FRI (2-5 PM)' to lab codes like 'AL5'
    
    Args:
        slot_text (str): Slot text like 'FRI (2-5 PM)', 'MON (9-12 AM)', etc.
    
    Returns:
        str: Lab code like 'AL5', 'ML1', or original text if no pattern matches
    """
    if not slot_text or not isinstance(slot_text, str):
        return slot_text
        
    slot_upper = slot_text.upper().strip()
    
    # Day mapping
    day_to_num = {
        'MON': '1',
        'TUE': '2', 
        'WED': '3',
        'THU': '4',
        'FRI': '5'
    }
    
    # Find day abbreviation
    day_num = None
    for day_abbr, num in day_to_num.items():
        if day_abbr in slot_upper:
            day_num = num
            break
    
    if not day_num:
        return slot_text
    
    # Determine if morning or afternoon based on time pattern
    # Look for patterns like (2-5 PM), (9-12 AM), etc.
    is_afternoon = False
    is_morning = False
    
    if 'PM' in slot_upper:
        # Check if it's afternoon lab timing (2-5 PM pattern)
        if any(time_pattern in slot_upper for time_pattern in ['2-5', '2:00-5', '14:00-17']):
            is_afternoon = True
    elif 'AM' in slot_upper:
        # Check if it's morning lab timing (9-12 AM pattern)  
        if any(time_pattern in slot_upper for time_pattern in ['9-12', '9:00-12', '09:00-12']):
            is_morning = True
    
    # Generate lab code
    if is_afternoon:
        return f'AL{day_num}'
    elif is_morning:
        return f'ML{day_num}'
    else:
        # Default to afternoon if PM but unclear timing, morning if AM
        if 'PM' in slot_upper:
            return f'AL{day_num}'
        elif 'AM' in slot_upper:
            return f'ML{day_num}'
    
    return slot_text

def get_lab_timing(lab_code):
    """
    Get the timing string for a lab code
    
    Args:
        lab_code (str): Lab code like 'ML1', 'AL5', etc.
    
    Returns:
        str: Timing string like '9:00 - 11:55 AM' or '2:00 - 4:55 PM'
    """
    if not lab_code or not isinstance(lab_code, str):
        return ''
        
    if lab_code.startswith('ML'):
        return "9:00 - 11:55 AM"
    elif lab_code.startswith('AL'):  
        return "2:00 - 4:55 PM"
    
    return ''

def get_day_from_lab_code(lab_code):
    """
    Extract day name from lab code
    
    Args:
        lab_code (str): Lab code like 'ML1', 'AL5', etc.
    
    Returns:
        str: Day name like 'Monday', 'Friday', or empty string
    """
    if not lab_code or len(lab_code) != 3:
        return ''
        
    day_mapping = {
        '1': 'Monday',
        '2': 'Tuesday', 
        '3': 'Wednesday',
        '4': 'Thursday',
        '5': 'Friday'
    }
    
    if lab_code.startswith(('ML', 'AL')):
        day_num = lab_code[2]
        return day_mapping.get(day_num, '')
    
    return ''

def process_slot_for_days(slot, row):
    """
    Process slot and set appropriate day columns based on lab codes or day abbreviations
    
    Args:
        slot (str): The slot value to process
        row (pandas.Series): The row data to update
    
    Returns:
        pandas.Series: Updated row with day columns filled
    """
    new_row = row.copy()
    
    # First, try to convert day+time patterns to lab codes
    processed_slot = parse_day_time_to_lab_code(slot)
    
    # Update the slot if it was converted
    if processed_slot != slot:
        new_row['slot'] = processed_slot
        slot = processed_slot
    
    # Now process the (possibly converted) slot for day assignments
    if slot.startswith(('ML', 'AL')) and len(slot) == 3:
        # It's a proper lab code
        day_name = get_day_from_lab_code(slot)
        timing = get_lab_timing(slot)
        
        if day_name and timing:
            new_row[day_name] = timing
    else:
        # Handle other slot patterns that might contain day abbreviations
        slot_upper = slot.upper()
        day_checks = [
            ('MON', 'Monday'),
            ('TUE', 'Tuesday'), 
            ('WED', 'Wednesday'),
            ('THU', 'Thursday'),
            ('FRI', 'Friday')
        ]
        
        for day_abbr, day_name in day_checks:
            if day_abbr in slot_upper:
                # Try to determine timing from context
                if 'ML' in slot_upper or 'MORNING' in slot_upper or '9' in slot_upper:
                    new_row[day_name] = "9:00 - 11:55 AM"
                elif 'AL' in slot_upper or 'AFTERNOON' in slot_upper or '2' in slot_upper:
                    new_row[day_name] = "2:00 - 4:55 PM"
                else:
                    new_row[day_name] = slot  # Use original slot if timing unclear
    
    return new_row

def save_to_csv(df, filename="data/courses_csv.csv"):
    """Save DataFrame to CSV file with required columns mapped to match courses_csv.csv format"""
    
    # Map the time table columns to the required courses_csv.csv format
    # Expected columns in courses_csv.csv: code, name, slot, venue, prof, exam_slot, Monday, Tuesday, Wednesday, Thursday, Friday
    
    column_mapping = {}
    
    # Map based on the actual column names from time table
    for col in df.columns:
        col_lower = col.lower().replace(' ', '')
        if col_lower == 'coursecode':
            column_mapping[col] = 'code'
        elif col_lower == 'coursename':
            column_mapping[col] = 'name'
        elif col_lower == 'classslot':
            column_mapping[col] = 'slot'
        elif col_lower == 'examslot':
            column_mapping[col] = 'exam_slot'
        elif 'classroom' in col_lower or 'classroom' in col_lower or 'lab' in col_lower:
            column_mapping[col] = 'venue'
        elif 'faculty' in col_lower or 'instructor' in col_lower or 'email' in col_lower:
            column_mapping[col] = 'prof'
    
    print(f"🔄 Column mapping: {column_mapping}")
    
    # Create new dataframe with mapped columns
    df_mapped = pd.DataFrame()
    
    # Map existing columns
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df_mapped[new_col] = df[old_col]
    
    # Add missing required columns with empty values
    required_columns = ['code', 'name', 'slot', 'venue', 'prof', 'exam_slot', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    for col in required_columns:
        if col not in df_mapped.columns:
            df_mapped[col] = ''
    
    # Clean up data before expanding slots
    df_mapped = df_mapped.fillna('')  # Replace NaN with empty strings
    
    # Clean up course codes - remove all spaces (e.g., "ME 679" -> "ME679")
    if 'code' in df_mapped.columns:
        df_mapped['code'] = df_mapped['code'].apply(lambda x: re.sub(r'\s+', '', str(x)) if pd.notna(x) else '')
    
    # Clean up professor names - remove email addresses and extra whitespace
    if 'prof' in df_mapped.columns:
        df_mapped['prof'] = df_mapped['prof'].apply(lambda x: re.sub(r'\s*\([^)]*\)', '', str(x)) if pd.notna(x) else '')
        df_mapped['prof'] = df_mapped['prof'].apply(lambda x: re.sub(r'\s+', ' ', str(x)).strip() if pd.notna(x) else '')
    
    # Handle multiple slots in the slot column (e.g., "ML3,ML4" -> separate rows)
    # Also process lab codes and day assignments
    expanded_rows = []
    
    for _, row in df_mapped.iterrows():
        slot_value = str(row['slot']).strip()
        
        # Check if slot contains multiple values separated by comma
        if (',' in slot_value or '+' in slot_value) and slot_value != '':
            # Replace both delimiters with comma, then split
            slot_value_clean = slot_value.replace('+', ',')
            slots = [s.strip() for s in slot_value_clean.split(',') if s.strip()]
            for slot in slots:
                new_row = row.copy()
                new_row['slot'] = slot
                # Process this slot for day assignments
                new_row = process_slot_for_days(slot, new_row)
                expanded_rows.append(new_row)
        else:
            # Single slot or empty, keep as is but process for day assignments
            if slot_value != '':
                new_row = process_slot_for_days(slot_value, row)
            else:
                new_row = row.copy()
            expanded_rows.append(new_row)
    
    # Create new dataframe from expanded rows
    df_expanded = pd.DataFrame(expanded_rows)
    
    # Reorder columns to match expected format
    df_final = df_expanded[required_columns].copy()
    
    # Remove duplicates based on course code and slot combination (keep first occurrence)
    initial_count = len(df_final)
    df_final = df_final.drop_duplicates(subset=['code', 'slot'], keep='first')
    duplicates_removed = initial_count - len(df_final)
    if duplicates_removed > 0:
        print(f"🔄 Removed {duplicates_removed} duplicate course code-slot combinations")
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Save to CSV
    df_final.to_csv(filename, index=False)
    print(f"💾 Data saved to '{filename}' with required columns")
    
    # Print summary statistics
    print(f"\n📊 Summary:")
    print(f"   Total course entries: {len(df_final)}")
    print(f"   Unique course codes: {df_final['code'].nunique()}")
    print(f"   Columns: {list(df_final.columns)}")
    
    # Show sample data
    print(f"\n🔍 Sample data (first 5 rows):")
    print(df_final.head().to_string(index=False))

def main():
    """Main function to extract and save course data"""
    try:
        # Extract course data
        df = extract_iitg_courses()
        
        # Save to CSV with proper column mapping
        save_to_csv(df)
        
        # Determine environment and set appropriate paths
        if os.path.exists('/code'):
            # Docker environment
            data_dir = '/code/data'
        else:
            # Local development environment
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        csv_path = os.path.join(data_dir, 'courses_csv.csv')
        
        # Add timings to the course CSV
        try:
            df_with_timings = add_timings_to_course_csv(csv_path)
            if not df_with_timings.empty:
                print("\n🕒 Courses with timing adjustments:")
                print("=" * 80)
                print(df_with_timings.to_string(index=False, max_colwidth=15))
                print("=" * 80)
                # print(f"📊 Total courses with timings: {len(df_with_timings)}")
            else:
                print("⚠️  No timing data available to display")
        except Exception as e:
            print(f"⚠️  Warning: Could not add timings - {e}")
        
        print("\n🎉 Data extraction completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    result = main()
    if result != 0:
        print("ERROR: FAILED TO EXTRACT COURSE DATA")
        exit(result)
    exit(result)
