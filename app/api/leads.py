from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime
from bson import ObjectId
from app.models.lead import LeadCreate, LeadResponse
from app.db import leads_collection
from app.api.auth import get_current_user
from app.services.sheets_service import sheets_service

router = APIRouter(prefix="/leads", tags=["Leads"])

def format_lead(lead: dict) -> dict:
    lead["id"] = str(lead.pop("_id"))
    return lead

@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(lead: LeadCreate, user: dict = Depends(get_current_user)):
    if leads_collection is None:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    lead_dict = lead.model_dump()
    lead_dict["user_email"] = user["email"]
    lead_dict["created_at"] = datetime.utcnow()
    
    result = await leads_collection.insert_one(lead_dict)
    lead_dict["_id"] = result.inserted_id
    
    # Log to Google Sheets
    await sheets_service.log_lead_to_sheet(
        name=lead_dict.get("name") or "N/A",
        email=lead_dict["email"],
        company=lead_dict.get("company", ""),
        notes=lead_dict.get("notes", "")
    )
    
    return format_lead(lead_dict)

@router.get("/", response_model=List[LeadResponse])
async def get_leads(user: dict = Depends(get_current_user)):
    if leads_collection is None:
        raise HTTPException(status_code=500, detail="Database connection not established")
        
    try:
        leads = []
        cursor = leads_collection.find({"user_email": user["email"]})
        async for document in cursor:
            leads.append(format_lead(document))
        return leads
    except Exception as e:
        print(f"Error fetching leads: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching leads: {str(e)}")


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(lead_id: str, user: dict = Depends(get_current_user)):
    if leads_collection is None:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    if not ObjectId.is_valid(lead_id):
        raise HTTPException(status_code=400, detail="Invalid lead ID format")
        
    result = await leads_collection.delete_one({
        "_id": ObjectId(lead_id),
        "user_email": user["email"]
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    return None
