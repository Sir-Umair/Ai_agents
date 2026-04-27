import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def test_db():
    uri = os.getenv("MONGODB_URL")
    print(f"Connecting to: {uri[:30]}...")
    try:
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        # Try a simple command
        await client.admin.command('ping')
        print("Ping successful!")
        db = client.email_marketer
        count = await db.users.count_documents({})
        print(f"Connected! User count: {count}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_db())
