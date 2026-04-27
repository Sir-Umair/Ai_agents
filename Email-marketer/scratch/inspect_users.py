import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient

# Add current directory to path
sys.path.append(os.getcwd())

from app.config import settings

async def inspect():
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client.email_marketer
    logs_col = db.email_logs
    
    # Check distinct user_emails in logs
    user_emails = await logs_col.distinct("user_email")
    print("User emails in logs:", user_emails)
    
    # Check distinct user_emails in sent logs
    sent_user_emails = await logs_col.distinct("user_email", {"type": "sent"})
    print("User emails in sent logs:", sent_user_emails)
    
    # Check distinct user_emails in intent logs
    intent_user_emails = await logs_col.distinct("user_email", {"intent": {"$exists": True}})
    print("User emails in intent logs:", intent_user_emails)

    # Check a few users in the users collection
    users_col = db.users
    all_users = await users_col.find({}, projection={"email": 1}).to_list(length=None)
    print("All users in DB:", [u["email"] for u in all_users])

if __name__ == "__main__":
    asyncio.run(inspect())
