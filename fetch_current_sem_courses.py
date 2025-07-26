import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
from initialise_timings import add_timings_to_course_csv
import os

# pip3 install requests pandas beautifulsoup4 lxml

def extract_iitg_courses():
    """
    Extract all course data from IITG offered courses page.
    The website loads all data in the HTML table (no AJAX pagination).
    """
    # URL of the IITG offered courses page
    URL = "https://iitg.ac.in/acad/offered_courses.php"
    
    # Headers to mimic a real browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    print("🔄 Fetching data from IITG...")
    response = requests.get(URL, headers=headers)
    response.raise_for_status()
    
    print("📄 Parsing HTML content...")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table with id="dataTable"
    table = soup.find('table', {'id': 'dataTable'})
    if not table:
        raise Exception("Could not find the data table on the page")
    
    # Extract table headers
    thead = table.find('thead')
    if not thead:
        raise Exception("Could not find table headers")
    
    header_row = thead.find('tr')
    headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
    print(f"📋 Found columns: {headers}")
    
    # Extract table body data
    tbody = table.find('tbody')
    if not tbody:
        raise Exception("Could not find table body")
    
    rows = tbody.find_all('tr')
    print(f"🔢 Found {len(rows)} course entries")
    
    all_data = []
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= len(headers) - 1:  # -1 because last column might be empty
            row_data = []
            for i, cell in enumerate(cells[:len(headers)]):
                # Clean up text content
                text = cell.get_text(strip=True)
                # Remove extra whitespace
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
    if df.columns[-1] == '' or df.iloc[:, -1].str.strip().eq('').all():
        df = df.iloc[:, :-1]
    
    # Strip whitespace from all string columns
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
    
    # Replace empty strings with None for better data quality
    df = df.replace('', None)
    
    return df

def save_to_csv(df, filename="data/courses_csv.csv"):
    """Save DataFrame to CSV file with required columns only"""
    
    # Map the current columns to the required format
    column_mapping = {
        'Course Code': 'code',
        'Course Name': 'name', 
        'Exam Slot': 'slot',
        'Instructor(s)': 'prof'
    }
    
    # Select and rename only the required columns
    required_columns = ['Course Code', 'Course Name', 'Exam Slot', 'Instructor(s)']
    df_filtered = df[required_columns].copy()
    df_filtered = df_filtered.rename(columns=column_mapping)
    
    # Add missing columns that the API expects
    df_filtered['venue'] = ''  # Empty venue column
    df_filtered['Monday'] = ''    # Empty timing columns
    df_filtered['Tuesday'] = ''
    df_filtered['Wednesday'] = ''
    df_filtered['Thursday'] = ''
    df_filtered['Friday'] = ''
    
    # Reorder columns to match expected format
    final_columns = ['code', 'name', 'slot', 'venue', 'prof', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    df_final = df_filtered[final_columns]
    
    # Clean up data
    df_final = df_final.fillna('')  # Replace NaN with empty strings
    
    # Save to CSV
    df_final.to_csv(filename, index=False)
    print(f"💾 Data saved to '{filename}' with required columns only")
    
    # Print summary statistics
    print(f"\n📊 Summary:")
    print(f"   Total courses: {len(df_final)}")
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
        
        # Save to CSV
        save_to_csv(df)
        # Determine environment and set appropriate paths
        if os.path.exists('/code'):
            # Docker environment
            data_dir = '/code/data'
        else:
            # Local development environment
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
        
        csv_path = os.path.join(data_dir, 'courses_csv.csv')
        add_timings_to_course_csv(csv_path)
        
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
