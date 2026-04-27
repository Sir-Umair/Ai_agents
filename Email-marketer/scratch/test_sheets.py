"""
Test Google Sheets connectivity.
Run: python scratch/test_sheets.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Load env manually
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
sheet_id = ""
creds_file = "credentials.json"

with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("GOOGLE_SHEET_ID="):
            sheet_id = line.split("=", 1)[1].strip()
        elif line.startswith("GOOGLE_CREDENTIALS_FILE="):
            creds_file = line.split("=", 1)[1].strip()

import json
with open(creds_file) as f:
    creds_data = json.load(f)
service_account_email = creds_data.get("client_email", "unknown")

print(f"[TEST] Sheet ID     : {sheet_id}")
print(f"[TEST] Service Acct : {service_account_email}")
print()

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

try:
    print("1. Authenticating with Google...")
    creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    client = gspread.authorize(creds)
    print("   [OK] Authenticated.")

    print("2. Opening spreadsheet...")
    sheet = client.open_by_key(sheet_id).sheet1
    print(f"   [OK] Opened sheet: '{sheet.title}'")

    print("3. Writing a test row...")
    import datetime
    sheet.append_row(
        ["TEST_NAME", "test@example.com", "Test query from script", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        value_input_option="USER_ENTERED"
    )
    print("   [OK] Test row written successfully!")
    print()
    print("[SUCCESS] Google Sheets is working correctly.")

except gspread.exceptions.SpreadsheetNotFound:
    print()
    print("[FAIL] Spreadsheet NOT FOUND.")
    print()
    print("[FIX] You must share your Google Sheet with the service account email:")
    print(f"   -> {service_account_email}")
    print("   Steps:")
    print("   1. Open your Google Sheet")
    print("   2. Click Share (top right)")
    print(f"   3. Add this email as Editor: {service_account_email}")
    print("   4. Click Send")

except Exception as e:
    print(f"[FAIL] Error: {e}")
