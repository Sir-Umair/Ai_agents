from fastapi import APIRouter
from app.db import email_logs_collection
from app.api.auth import get_current_user
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/logs", tags=["Logs"])


def _serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    if "timestamp" in doc:
        doc["timestamp"] = doc["timestamp"].isoformat()
    return doc


@router.get("/recent")
async def get_recent_logs(limit: int = 10, user: dict = Depends(get_current_user)):
    """Returns the most recent activity logs for the authenticated user."""
    if email_logs_collection is None:
        return []
    cursor = email_logs_collection.find({"user_email": user["email"]}).sort("timestamp", -1).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [_serialize(doc) for doc in docs]
