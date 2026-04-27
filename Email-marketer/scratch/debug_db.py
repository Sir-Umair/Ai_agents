"""
Debug script - checks what records exist in MongoDB email_logs.
Run: python scratch/debug_db.py
"""
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = os.getenv("MONGODB_URL", "")

async def main():
    print(f"[DB] Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client.email_marketer

    # Count all records
    total = await db.email_logs.count_documents({})
    with_intent = await db.email_logs.count_documents({"intent": {"$exists": True}})
    sent_only = await db.email_logs.count_documents({"type": "sent"})

    print(f"[DB] Total email_logs docs : {total}")
    print(f"[DB] With 'intent' field   : {with_intent}  <- these show in Responses page")
    print(f"[DB] With 'type: sent'     : {sent_only}")
    print()

    if with_intent > 0:
        print("[DB] Latest response records:")
        cursor = db.email_logs.find({"intent": {"$exists": True}}).sort("timestamp", -1).limit(5)
        async for doc in cursor:
            print(f"  - {doc.get('name')} | {doc.get('email')} | {doc.get('intent')} | {doc.get('timestamp')}")
    else:
        print("[DB] No response records found yet.")
        print()
        print("     Possible reasons:")
        print("     1. No lead has replied to your emails yet")
        print("     2. 'Sync Replies' button has not been clicked on the Dashboard")
        print("     3. Backend was not reloaded after the code changes")
        print()
        print("     -> Click 'Sync Replies' on the dashboard, then run this again.")

    client.close()

asyncio.run(main())
