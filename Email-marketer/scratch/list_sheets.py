"""
Checks Google Sheets access and shows all visible sheets for the service account.
Run: python scratch/list_sheets.py
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDS_FILE = os.path.join(ROOT, "credentials.json")
ENV_FILE = os.path.join(ROOT, ".env")

with open(CREDS_FILE) as f:
    creds_data = json.load(f)
service_email = creds_data["client_email"]

# Load current sheet ID from .env
current_sheet_id = ""
with open(ENV_FILE) as f:
    for line in f:
        if line.startswith("GOOGLE_SHEET_ID="):
            current_sheet_id = line.split("=", 1)[1].strip()

print(f"Service Account : {service_email}")
print(f"Current Sheet ID: {current_sheet_id}")
print()

from google.oauth2.service_account import Credentials
import gspread

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

try:
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    print("Listing ALL spreadsheets visible to the service account...")
    sheets = client.list_spreadsheet_files()
    
    if not sheets:
        print()
        print("[NONE] The service account has NO spreadsheets accessible to it.")
        print()
        print("To fix this, you MUST do the following:")
        print()
        print("  1. Go to https://sheets.google.com and create a NEW blank spreadsheet")
        print("  2. Click Share in the top-right corner")
        print(f"  3. Add this email as EDITOR: {service_email}")
        print("  4. Click Send")
        print("  5. Copy the sheet ID from the URL bar:")
        print("       https://docs.google.com/spreadsheets/d/  <<COPY THIS PART>>  /edit")
        print("  6. Update your .env file:")
        print("       GOOGLE_SHEET_ID=<paste-id-here>")
        print("  7. Restart the backend server")
    else:
        print(f"[OK] Found {len(sheets)} accessible sheet(s):")
        for s in sheets:
            print(f"  - {s['name']}  |  ID: {s['id']}")
            print(f"    URL: https://docs.google.com/spreadsheets/d/{s['id']}")
        
        if sheets:
            first_id = sheets[0]["id"]
            if first_id != current_sheet_id:
                print()
                print(f"[MISMATCH] Your .env has ID '{current_sheet_id}'")
                print(f"           but service account can access '{first_id}'")
                print()
                print(f"Update your .env: GOOGLE_SHEET_ID={first_id}")

except Exception as e:
    print(f"[ERROR] {e}")
