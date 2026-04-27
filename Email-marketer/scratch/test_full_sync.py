"""
End-to-end test: Directly runs check_and_reply_to_emails() and shows all output.
This tests MongoDB logging + Google Sheets logging in one shot.

Run: python scratch/test_full_sync.py
"""
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Force reload of .env before anything imports settings
from dotenv import load_dotenv
load_dotenv(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
    override=True
)

import motor.motor_asyncio
from app.config import settings

# ── Print current config ───────────────────────────────────────────────────────
print("=" * 60)
print("CURRENT CONFIGURATION")
print("=" * 60)
print(f"EMAIL_USER   : {settings.email_user}")
print(f"SHEET_ID     : {settings.google_sheet_id}")
print(f"CREDS FILE   : {settings.google_credentials_file}")
print()

# ── Connect MongoDB manually so motor event loop works ─────────────────────────
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
db = mongo_client.email_marketer

# Patch the db module so the service uses our connection
import app.db as db_module
db_module.email_logs_collection = db.email_logs
db_module.leads_collection = db.leads

async def run():
    # ── Step 1: Test Google Sheets directly ───────────────────────────────────
    print("STEP 1: Testing Google Sheets...")
    from app.services.sheets_service import SheetsService
    sheets = SheetsService()
    import datetime
    await sheets.log_responder_to_sheet(
        name="TEST CLIENT",
        email="testclient@example.com",
        message_snippet="[DIRECT TEST] This entry was written by test_full_sync.py"
    )
    print()

    # ── Step 2: Run the actual Sync Replies ───────────────────────────────────
    print("STEP 2: Running Sync Replies (IMAP scan)...")
    from app.services.auto_reply_service import AutoReplyService
    svc = AutoReplyService()
    result = await svc.check_and_reply_to_emails()
    print(f"Result: {result}")
    print()

    # ── Step 3: Check what's in MongoDB ───────────────────────────────────────
    print("STEP 3: MongoDB email_logs (latest 5):")
    cursor = db.email_logs.find({"intent": {"$exists": True}}).sort("timestamp", -1).limit(5)
    count = 0
    async for doc in cursor:
        count += 1
        print(f"  [{count}] {doc.get('name')} | {doc.get('email')} | {doc.get('intent')} | {doc.get('timestamp')}")
    if count == 0:
        print("  (no reply records found in MongoDB)")

    mongo_client.close()
    print()
    print("Done. Check your Google Sheet and the Responses page now.")

asyncio.run(run())
