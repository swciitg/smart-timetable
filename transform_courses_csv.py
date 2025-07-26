#!/usr/bin/env python3
"""
Transform the existing courses_csv.csv to the required format
"""

import pandas as pd
import os

def transform_courses_csv():
    """Transform the existing courses CSV to required format"""
    
    input_file = 'data/courses_csv.csv'
    output_file = 'data/courses_csv.csv'
    
    if not os.path.exists(input_file):
        print(f"❌ Input file {input_file} not found")
        return False
    
    try:
        # Read the existing CSV
        print(f"📖 Reading {input_file}...")
        df = pd.read_csv(input_file)
        print(f"   Found {len(df)} rows with columns: {list(df.columns)}")
        
        # Map the current columns to the required format
        column_mapping = {
            'Course Code': 'code',
            'Course Name': 'name', 
            'Exam Slot': 'slot',
            'Instructor(s)': 'prof'
        }
        
        # Check if required columns exist
        required_columns = ['Course Code', 'Course Name', 'Exam Slot', 'Instructor(s)']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            print(f"   Available columns: {list(df.columns)}")
            return False
        
        # Select and rename only the required columns
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
        
        # Create backup of original file
        backup_file = input_file + '.backup'
        if os.path.exists(input_file):
            os.rename(input_file, backup_file)
            print(f"📦 Created backup: {backup_file}")
        
        # Save transformed CSV
        df_final.to_csv(output_file, index=False)
        print(f"💾 Transformed data saved to {output_file}")
        
        # Print summary statistics
        print(f"\n📊 Summary:")
        print(f"   Total courses: {len(df_final)}")
        print(f"   Unique course codes: {df_final['code'].nunique()}")
        print(f"   Final columns: {list(df_final.columns)}")
        
        # Show sample data
        print(f"\n🔍 Sample data (first 5 rows):")
        print(df_final.head().to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"❌ Error transforming CSV: {e}")
        return False

def main():
    """Main function"""
    print("🔄 Transforming courses CSV to required format...")
    
    if transform_courses_csv():
        print("\n✅ Transformation completed successfully!")
        return 0
    else:
        print("\n❌ Transformation failed!")
        return 1

if __name__ == "__main__":
    exit(main())
