#!/usr/bin/env python3

import requests
import json

# Test the API with roll number
# Start server with python -m uvicorn main:app --reload --host 0.0.0.0 --port 8002
roll = "250101001"
url = "http://localhost:8002/get-my-courses"
data = {"roll_number": roll}

try:
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        print("SUCCESS: API call successful")
        print("Response:")
        print(json.dumps(result, indent=2))
    else:
        print(f"ERROR: API call failed with status code {response.status_code}")
        print(f"Response: {response.text}")
except requests.exceptions.ConnectionError:
    print("ERROR: Could not connect to the server. Make sure it's running on http://localhost:8002")
except Exception as e:
    print(f"ERROR: {e}")
