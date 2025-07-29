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

def save_to_csv(df, filename="data/courses_csv.csv"):
    """Save DataFrame to CSV file with required columns mapped to match courses_csv.csv format"""
    
    # Map the time table columns to the required courses_csv.csv format
    # Expected columns in courses_csv.csv: code, name, slot, venue, prof, exam_slot, Monday, Tuesday, Wednesday, Thursday, Friday
    
    column_mapping = {}
    
    # Map based on the actual column names from time table
    for col in df.columns:
        col_lower = col.lower()
        if 'course code' in col_lower or col_lower == 'course code':
            column_mapping[col] = 'code'
        elif 'course name' in col_lower or col_lower == 'course name':
            column_mapping[col] = 'name'
        elif 'class slot' in col_lower or col_lower == 'class slot':
            column_mapping[col] = 'slot'
        elif 'exam slot' in col_lower or col_lower == 'exam slot':
            column_mapping[col] = 'exam_slot'
        elif 'class room' in col_lower or 'classroom' in col_lower or 'lab' in col_lower:
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
    
    # Clean up professor names - remove email addresses and extra whitespace
    if 'prof' in df_mapped.columns:
        df_mapped['prof'] = df_mapped['prof'].apply(lambda x: re.sub(r'\s*\([^)]*\)', '', str(x)) if pd.notna(x) else '')
        df_mapped['prof'] = df_mapped['prof'].apply(lambda x: re.sub(r'\s+', ' ', str(x)).strip() if pd.notna(x) else '')
    
    # Handle multiple slots in the slot column (e.g., "ML3,ML4" -> separate rows)
    expanded_rows = []
    
    for _, row in df_mapped.iterrows():
        slot_value = str(row['slot']).strip()
        
        # Check if slot contains multiple values separated by comma
        if ',' in slot_value and slot_value != '':
            # Split by comma and create separate rows for each slot
            slots = [s.strip() for s in slot_value.split(',') if s.strip()]
            for slot in slots:
                new_row = row.copy()
                new_row['slot'] = slot
                expanded_rows.append(new_row)
        else:
            # Single slot or empty, keep as is
            expanded_rows.append(row)
    
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
                print(f"📊 Total courses with timings: {len(df_with_timings)}")
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
