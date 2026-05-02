from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

class DBManager:
    def __init__(self):
        self._client = None
        self._db = None

    def get_db(self):
        if self._db is None:
            print(f"DEBUG: Lazy initializing MongoDB client for {settings.mongodb_url[:20]}...")
            self._client = AsyncIOMotorClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                retryWrites=True
            )
            self._db = self._client.email_marketer
        return self._db

_manager = DBManager()

class CollectionProxy:
    def __init__(self, name):
        self.name = name

    def __getattr__(self, item):
        db = _manager.get_db()
        collection = db[self.name]
        return getattr(collection, item)

# We export 'db' as a proxy as well in case it's used directly
class DBProxy:
    def __getattr__(self, item):
        db = _manager.get_db()
        return getattr(db, item)

db = DBProxy()

# Export all collections using the proxy so they don't block import
users_collection = CollectionProxy("users")
leads_collection = CollectionProxy("leads")
email_logs_collection = CollectionProxy("email_logs")
settings_collection = CollectionProxy("settings")
follow_ups_collection = CollectionProxy("follow_ups")
