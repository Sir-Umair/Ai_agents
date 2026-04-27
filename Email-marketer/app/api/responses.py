from fastapi import APIRouter, Depends
from app.db import email_logs_collection
from bson import ObjectId
from app.api.auth import get_current_user

router = APIRouter(prefix="/responses", tags=["Responses"])


def _serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    if "timestamp" in doc:
        doc["timestamp"] = doc["timestamp"].isoformat()
    return doc


@router.get("/")
async def get_responses(limit: int = 100, user: dict = Depends(get_current_user)):
    """Returns all logged client email responses from MongoDB."""
    if email_logs_collection is None:
        return []
        
    # We fetch records that have an 'intent' field, which indicates they were processed by our AI auto-reply system.
    # We filter by user_email to ensure privacy and only show relevant records for the logged-in user.
    cursor = email_logs_collection.find(
        {"user_email": user["email"], "intent": {"$exists": True}}
    ).sort("timestamp", -1).limit(limit)
    
    docs = await cursor.to_list(length=limit)
    return [_serialize(doc) for doc in docs]


@router.get("/campaigns")
async def get_campaign_dashboard(user: dict = Depends(get_current_user)):
    """Returns a grouped dashboard of campaigns and lead responses."""
    if email_logs_collection is None:
        return []

    # 1. Fetch all 'sent' logs for this user to identify campaigns
    sent_cursor = email_logs_collection.find(
        {"user_email": user["email"], "type": "sent"}
    ).sort("timestamp", -1)
    sent_logs = await sent_cursor.to_list(length=1000)

    # 2. Fetch all responses for this user
    resp_cursor = email_logs_collection.find(
        {"user_email": user["email"], "intent": {"$exists": True}}
    ).sort("timestamp", -1)
    all_responses = await resp_cursor.to_list(length=1000)

    # 3. Group by campaign_id
    # We use (subject, body[:50]) as a fallback for old logs without campaign_id
    campaigns = {}
    
    for log in sent_logs:
        c_id = log.get("campaign_id") or f"legacy-{log.get('subject')}-{log.get('timestamp').date()}"
        if c_id not in campaigns:
            campaigns[c_id] = {
                "id": c_id,
                "subject": log.get("subject"),
                "timestamp": log.get("timestamp").isoformat(),
                "leads": []
            }
        
        # Check if this lead replied
        # A reply matches by email AND (campaign_id OR subject/thread)
        response = next((r for r in all_responses if r.get("email") == log.get("recipient") and 
                         (r.get("campaign_id") == log.get("campaign_id") or r.get("thread_id") == log.get("thread_id"))), None)
        
        campaigns[c_id]["leads"].append({
            "email": log.get("recipient"),
            "replied": response is not None,
            "response": _serialize(response) if response else None
        })

    return list(campaigns.values())


@router.get("/thread/{thread_id}")
async def get_thread(thread_id: str, user: dict = Depends(get_current_user)):
    """Returns all emails in a specific thread."""
    if email_logs_collection is None:
        return []
    cursor = email_logs_collection.find(
        {"user_email": user["email"], "thread_id": thread_id}
    ).sort("timestamp", 1)  # oldest to newest
    docs = await cursor.to_list(length=100)
    return [_serialize(doc) for doc in docs]

@router.delete("/{response_id}")
async def delete_response(response_id: str, user: dict = Depends(get_current_user)):
    """Deletes a single response log entry."""
    if email_logs_collection is None:
        return {"error": "DB not available"}
    await email_logs_collection.delete_one({
        "_id": ObjectId(response_id),
        "user_email": user["email"]
    })
    return {"deleted": True}
