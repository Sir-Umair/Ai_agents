"""
Creates a new Google Sheet owned by the service account,
sets up headers, and auto-updates .env with the new Sheet ID.

Run: python scratch/setup_sheet.py
"""
import os, sys, re

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Resolve paths relative to project root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(ROOT, ".env")
CREDS_FILE = os.path.join(ROOT, "credentials.json")

print("[Setup] Creating Google Sheet using service account...")

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

try:
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    # Create a new spreadsheet owned by the service account
    sheet = client.create("Email Marketer - Client Responses")
    ws = sheet.sheet1
    ws.update_title("Client Responses")

    # Add headers
    ws.append_row(
        ["Name", "Email", "Intent", "Query / Message", "Timestamp"],
        value_input_option="USER_ENTERED",
    )
    ws.format("A1:E1", {"textFormat": {"bold": True}})

    new_sheet_id = sheet.id
    sheet_url = f"https://docs.google.com/spreadsheets/d/{new_sheet_id}"

    print(f"[OK] Sheet created: {sheet_url}")
    print(f"[OK] Sheet ID: {new_sheet_id}")

    # Update .env with the new sheet ID
    with open(ENV_PATH, "r") as f:
        env_content = f.read()

    if "GOOGLE_SHEET_ID=" in env_content:
        env_content = re.sub(
            r"GOOGLE_SHEET_ID=.*", f"GOOGLE_SHEET_ID={new_sheet_id}", env_content
        )
    else:
        env_content += f"\nGOOGLE_SHEET_ID={new_sheet_id}\n"

    with open(ENV_PATH, "w") as f:
        f.write(env_content)

    print(f"[OK] .env updated with new GOOGLE_SHEET_ID.")
    print()
    print("=" * 60)
    print("SUCCESS! Open your new sheet here:")
    print(sheet_url)
    print("=" * 60)
    print()
    print("IMPORTANT: Restart the backend server for the new Sheet ID to take effect.")

except Exception as e:
    print(f"[FAIL] {e}")
    sys.exit(1)
