#!/usr/bin/env python3
"""
Docker Health Check Script
Verifies that the enrollment system is working properly in Docker
"""

import os
import requests
import sys
from datetime import datetime, timedelta

def check_api_health():
    """Check if the FastAPI is responding"""
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        if response.status_code == 200:
            print("✅ API is responding")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check failed: {e}")
        return False

def check_csv_file():
    """Check if the CSV file exists and is recent"""
    csv_path = '/code/data/enrolled_courses.csv'
    
    if not os.path.exists(csv_path):
        print("❌ enrolled_courses.csv not found")
        return False
    
    # Check if file is recent (within 3 hours to account for cron schedule)
    mod_time = datetime.fromtimestamp(os.path.getmtime(csv_path))
    now = datetime.now()
    time_diff = now - mod_time
    
    if time_diff > timedelta(hours=3):
        print(f"⚠️ CSV file is old (last modified: {mod_time})")
        return False
    else:
        print("✅ CSV file is recent")
        return True

def check_cron_service():
    """Check if cron service is running"""
    cron_status = os.system('service cron status > /dev/null 2>&1')
    if cron_status == 0:
        print("✅ Cron service is running")
        return True
    else:
        print("❌ Cron service is not running")
        return False

def main():
    """Main health check function"""
    print("🔍 Docker Health Check")
    print("=" * 30)
    
    api_ok = check_api_health()
    csv_ok = check_csv_file()
    cron_ok = check_cron_service()
    
    if api_ok and csv_ok and cron_ok:
        print("✅ All systems healthy")
        return 0
    else:
        print("❌ Some systems unhealthy")
        return 1

if __name__ == "__main__":
    sys.exit(main())
