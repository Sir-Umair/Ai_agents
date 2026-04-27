
import asyncio
from app.db import users_collection, settings_collection, email_logs_collection

async def check_db():
    print("--- Users ---")
    users = await users_collection.find({}).to_list(length=10)
    for u in users:
        print(f"Email: {u.get('email')}")

    print("\n--- Settings ---")
    settings = await settings_collection.find({}).to_list(length=10)
    for s in settings:
        print(f"User Email: {s.get('user_email')}, Auto-Reply Enabled: {s.get('auto_reply_enabled')}")

    print("\n--- Recent Logs ---")
    logs = await email_logs_collection.find({}).sort("timestamp", -1).limit(5).to_list(length=5)
    for l in logs:
        print(f"User: {l.get('user_email')}, To: {l.get('recipient')}, Type: {l.get('type')}, Timestamp: {l.get('timestamp')}")

if __name__ == "__main__":
    asyncio.run(check_db())
