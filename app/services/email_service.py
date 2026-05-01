from email.message import EmailMessage
import mimetypes
from datetime import datetime, timedelta
import base64
from app.config import settings
from app.db import email_logs_collection, users_collection
from app.services.security_service import decrypt_data, encrypt_data
from app.services.sheets_service import sheets_service
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import google.auth.exceptions

async def get_user_credentials(user_email: str) -> Credentials:
    """Retrieve and refresh Google OAuth credentials for a user."""
    if users_collection is None:
        raise Exception("Database connection not established. Cannot fetch credentials.")
    user = await users_collection.find_one({"email": user_email})
    if not user:
        raise Exception(f"User {user_email} not found or not connected to Gmail.")
    
    # Check for missing metadata (requires re-login)
    required_keys = ["access_token", "token_uri", "client_id", "client_secret"]
    if not all(k in user for k in required_keys):
        raise Exception("Account setup incomplete. Please log out and log in again to refresh your connection.")

    creds = Credentials(
        token=decrypt_data(user["access_token"]),
        refresh_token=decrypt_data(user["refresh_token"]) if user.get("refresh_token") else None,
        token_uri=user["token_uri"],
        client_id=user["client_id"],
        client_secret=user["client_secret"],
        scopes=user.get("scopes", ["https://www.googleapis.com/auth/gmail.send"])
    )
    
    if creds.expired and creds.refresh_token:
        try:
            import asyncio
            await asyncio.to_thread(creds.refresh, Request())
            # Update tokens in DB
            await users_collection.update_one(
                {"email": user_email},
                {
                    "$set": {
                        "access_token": encrypt_data(creds.token),
                        "last_token_refresh": datetime.utcnow()
                    }
                }
            )
        except google.auth.exceptions.RefreshError as e:
            print(f"Token refresh failed for {user_email}: {e}")
            raise Exception("Authentication expired. Please reconnect your Gmail account.")
            
    return creds

async def send_email(to_email: str, subject: str, body: str, user_email: str, skip_log: bool = False, attachment_data: bytes = None, attachment_name: str = None, follow_up_delay: int = 0, follow_up_body: str = None, auto_reply_prompt: str = None, campaign_id: str = None) -> dict:
    """
    Sends a single email via Gmail API using OAuth 2.0 with optional PDF attachment and optional follow-up scheduling.
    """
    try:
        creds = await get_user_credentials(user_email)
        service = build('gmail', 'v1', credentials=creds)
        
        message = EmailMessage()
        message.set_content(body)
        message["To"] = to_email
        message["From"] = user_email
        message["Subject"] = subject
        
        if attachment_data and attachment_name:
            guessed = mimetypes.guess_type(attachment_name)[0]
            if guessed:
                maintype, subtype = guessed.split('/', 1)
            else:
                maintype, subtype = "application", "pdf" # Default guess
            message.add_attachment(
                attachment_data,
                maintype=maintype,
                subtype=subtype,
                filename=attachment_name
            )
        
        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        create_message = {'raw': encoded_message}
        
        import asyncio
        send_result = await asyncio.to_thread(
            service.users().messages().send(userId="me", body=create_message).execute
        )
        
        # Log to MongoDB (unless skipped)
        if not skip_log and email_logs_collection is not None:
            log_entry = {
                "user_email": user_email,
                "recipient": to_email,
                "subject": subject,
                "body": body,
                "type": "sent",
                "campaign_id": campaign_id,
                "gmail_id": send_result.get("id"),
                "thread_id": send_result.get("threadId"),
                "reply_received": False,
                "follow_up_sent": False,
                "timestamp": datetime.utcnow(),
            }
            
            # Store follow-up instructions if provided
            if follow_up_delay > 0:
                log_entry["follow_up_delay"] = follow_up_delay
                log_entry["follow_up_body"] = follow_up_body # Optional: if None, service generates one
                log_entry["follow_up_at"] = datetime.utcnow() + timedelta(minutes=follow_up_delay)
            
            if auto_reply_prompt:
                log_entry["auto_reply_prompt"] = auto_reply_prompt

            await email_logs_collection.insert_one(log_entry)

        # Log to Google Sheets
        await sheets_service.log_campaign_to_sheet(
            recipient=to_email,
            subject=subject,
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        )

        print(f"[EmailService] Email sent from {user_email} to {to_email}")
        return {"success": True, "message_id": send_result.get("id")}

    except Exception as e:
        print(f"[EmailService] Error sending email from {user_email}: {e}")
        return {"success": False, "error": str(e)}

async def send_bulk_emails(list_of_emails: list[str], subject: str, body: str, user_email: str, attachment_data: bytes = None, attachment_name: str = None, follow_up_delay: int = 0, follow_up_body: str = None, auto_reply_prompt: str = None) -> dict:
    import uuid
    import asyncio
    campaign_id = str(uuid.uuid4())
    semaphore = asyncio.Semaphore(15)
    
    async def process_email(email):
        async with semaphore:
            result = await send_email(
                to_email=email, 
                subject=subject, 
                body=body, 
                user_email=user_email,
                attachment_data=attachment_data,
                attachment_name=attachment_name,
                follow_up_delay=follow_up_delay,
                follow_up_body=follow_up_body,
                auto_reply_prompt=auto_reply_prompt,
                campaign_id=campaign_id
            )
            return {"email": email, "result": result}

    tasks = [process_email(email) for email in list_of_emails]
    results = await asyncio.gather(*tasks)

    success_count = 0
    failed_emails = []
    
    for r in results:
        if r["result"]["success"]:
            success_count += 1
        else:
            failed_emails.append(r["email"])

    return {
        "total": len(list_of_emails),
        "successful": success_count,
        "failed": len(failed_emails),
        "failed_emails": failed_emails
    }
