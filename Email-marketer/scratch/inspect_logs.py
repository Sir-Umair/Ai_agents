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
    
    print("Total logs:", await logs_col.count_documents({}))
    
    sent_logs_count = await logs_col.count_documents({"type": "sent"})
    print("Sent logs count:", sent_logs_count)
    
    if sent_logs_count > 0:
        sample_sent = await logs_col.find_one({"type": "sent"})
        print("Sample sent log:", sample_sent)
    
    intent_logs_count = await logs_col.count_documents({"intent": {"$exists": True}})
    print("Logs with intent count:", intent_logs_count)
    
    if intent_logs_count > 0:
        sample_intent = await logs_col.find_one({"intent": {"$exists": True}})
        print("Sample intent log:", sample_intent)
        
        # Check if they match
        valid_emails = set()
        async for doc in logs_col.find({"type": "sent"}, projection={"recipient": 1}):
            if "recipient" in doc:
                valid_emails.add(doc["recipient"].lower())
        
        valid_threads = set()
        async for doc in logs_col.find({"type": "sent"}, projection={"thread_id": 1}):
            if doc.get("thread_id"):
                valid_threads.add(doc["thread_id"])
        
        print(f"Valid emails: {len(valid_emails)}")
        print(f"Valid threads: {len(valid_threads)}")
        
        match_count = 0
        async for doc in logs_col.find({"intent": {"$exists": True}}):
            is_valid = False
            if doc.get("thread_id") and doc["thread_id"] in valid_threads:
                is_valid = True
            elif doc.get("email") and doc["email"].lower() in valid_emails:
                is_valid = True
            
            if is_valid:
                match_count += 1
        
        print("Matching logs count:", match_count)

if __name__ == "__main__":
    asyncio.run(inspect())
