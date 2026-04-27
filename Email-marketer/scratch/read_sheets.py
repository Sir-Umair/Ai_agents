"""
Diagnostic: Reads the Google Sheet to see what is actually stored there.
Run: python scratch/read_sheets.py
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(override=True)

from app.config import settings
from google.oauth2.service_account import Credentials
import gspread

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def read():
    print(f"Checking Sheet ID: {settings.google_sheet_id}")
    try:
        creds = Credentials.from_service_account_file(settings.google_credentials_file, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(settings.google_sheet_id).sheet1
        
        records = sheet.get_all_records()
        print(f"Total records found: {len(records)}")
        print("\nLast 5 rows:")
        rows = sheet.get_all_values()
        for r in rows[-5:]:
            print(f"  {r}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read()
