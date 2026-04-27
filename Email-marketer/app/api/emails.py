from fastapi import APIRouter, HTTPException, status, Depends, File, Form, UploadFile
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import json
from app.services import email_service
from app.services.ai_service import ai_service
from app.services.follow_up_service import follow_up_service
from app.services.auto_reply_service import auto_reply_service
from app.api.auth import get_current_user

router = APIRouter(prefix="/emails", tags=["Emails"])

class GenerateEmailRequest(BaseModel):
    prompt: str

class GenerateFollowUpRequest(BaseModel):
    original_subject: str
    original_body: str

@router.post("/generate-content")
async def generate_content(request: GenerateEmailRequest):
    content = await ai_service.generate_email_content(request.prompt)
    if content.startswith("Failed to generate") or content.startswith("Error"):
        raise HTTPException(status_code=500, detail=content)
    return {"generated_content": content}

@router.post("/generate-followup-content")
async def generate_followup_content(request: GenerateFollowUpRequest):
    content = await ai_service.generate_follow_up_content(request.original_subject, request.original_body)
    if content.startswith("Failed to generate") or content.startswith("Error"):
        raise HTTPException(status_code=500, detail=content)
    return {"generated_content": content}

class GenerateFollowUpPromptRequest(BaseModel):
    prompt: str
    original_subject: str
    original_body: str

@router.post("/generate-followup-from-prompt")
async def generate_followup_from_prompt(request: GenerateFollowUpPromptRequest):
    # We can create a specialized method in ai_service or just reuse generate_email_content with context
    context = f"Context: This is a follow-up to a previous email.\nOriginal Subject: {request.original_subject}\nOriginal Body: {request.original_body}\n\nUser Request: {request.prompt}"
    content = await ai_service.generate_email_content(context)
    if content.startswith("Failed to generate") or content.startswith("Error"):
        raise HTTPException(status_code=500, detail=content)
    return {"generated_content": content}

@router.post("/send-bulk")
async def send_bulk(
    emails_json: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    follow_up_delay: int = Form(0),
    follow_up_body: Optional[str] = Form(None),
    auto_reply_prompt: Optional[str] = Form(None),
    attachment: Optional[UploadFile] = File(None),
    user: dict = Depends(get_current_user)
):
    try:
        emails = json.loads(emails_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid email list format")
        
    attachment_data = await attachment.read() if attachment else None
    attachment_name = attachment.filename if attachment else None
    
    if not emails:
        raise HTTPException(status_code=400, detail="Email list cannot be empty")

    if attachment and not attachment_name.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF attachments are permitted.")

    result = await email_service.send_bulk_emails(
        list_of_emails=emails,
        subject=subject,
        body=body,
        user_email=user["email"],
        attachment_data=attachment_data,
        attachment_name=attachment_name,
        follow_up_delay=follow_up_delay,
        follow_up_body=follow_up_body,
        auto_reply_prompt=auto_reply_prompt
    )

    if result["successful"] == 0 and len(emails) > 0:
        detail = result.get("error") or "All emails failed to send."
        raise HTTPException(status_code=500, detail=detail)
    
    return result

@router.post("/process-followups")
async def process_followups():
    """Triggers the automated processing of pending follow-ups for emails without replies."""
    results = await follow_up_service.process_pending_follow_ups()
    return {"processed": len(results), "details": results}

@router.post("/auto-reply-suggestions")
async def get_suggestions(request: dict):
    subject = request.get("subject", "")
    body = request.get("body", "")
    if not subject or not body:
        return {"suggestions": ["Be professional", "Answer questions", "Try to book a call"]}
    suggestions = await ai_service.generate_response_suggestions(subject, body)
    return {"suggestions": suggestions}

@router.post("/process-replies")
async def process_replies(user: dict = Depends(get_current_user)):
    """Manually triggers the check for unread emails and auto-replies."""
    result = await auto_reply_service.check_and_reply_to_emails(user_email=user["email"])
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
    return result
