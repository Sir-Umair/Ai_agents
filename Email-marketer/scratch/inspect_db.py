import asyncio
from app.db import email_logs_collection

async def main():
    docs = await email_logs_collection.find().sort("timestamp", -1).limit(5).to_list(None)
    for d in docs:
        print(d.get("type"), d.get("subject"), d.get("thread_id"), d.get("intent"))

asyncio.run(main())
