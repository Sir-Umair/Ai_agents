"""
Diagnostic: Queries the RUNNING backend API to see what it returns for responses.
Run: python scratch/check_api.py
"""
import requests

def check():
    url = "http://localhost:8000/responses/"
    print(f"Querying {url}...")
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Count: {len(data)}")
        if data:
            print("First item sample:")
            print(f"  ID: {data[0].get('id')}")
            print(f"  Name: {data[0].get('name')}")
            print(f"  Intent: {data[0].get('intent')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
