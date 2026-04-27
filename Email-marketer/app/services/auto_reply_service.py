from googleapiclient.discovery import build
import base64
from email.message import EmailMessage
from app.services.email_service import get_user_credentials, send_email
from app.services.ai_service import ai_service
from app.services.sheets_service import sheets_service
from app.db import email_logs_collection, settings_collection
from datetime import datetime
import asyncio
import traceback

class AutoReplyService:
    def _get_recursive_body(self, payload) -> str:
        """Helper to recursively find text/plain body in nested email parts."""
        # 1. Check if this part itself is the text body
        if payload.get('mimeType') == 'text/plain':
            data = payload.get('body', {}).get('data', '')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
        
        # 2. If it has parts, search them recursively
        if 'parts' in payload:
            for part in payload['parts']:
                body = self._get_recursive_body(part)
                if body:
                    return body
        return ""

    async def check_and_reply_to_emails(self, user_email: str):
        """Checks for unread emails and processes them using Gmail API in parallel."""
        try:
            # Check if auto-reply is enabled for this user (case-insensitive)
            user_settings = await settings_collection.find_one({
                "user_email": {"$regex": f"^{user_email}$", "$options": "i"}
            })
            
            if user_settings and not user_settings.get("auto_reply_enabled", True):
                print(f"[AutoReply] SKIPPED: Auto-reply is paused for {user_email}")
                return {"status": "skipped", "message": "Auto-reply is paused"}

            creds = await get_user_credentials(user_email)
            service = build('gmail', 'v1', credentials=creds)

            # Search only for UNREAD messages in the inbox
            query = "is:unread label:inbox"
            results = await asyncio.to_thread(service.users().messages().list(userId='me', q=query).execute)
            messages = results.get('messages', [])
            
            if not messages:
                print(f"[AutoReply] No new unread messages for {user_email}")
                return {"status": "success", "processed": 0, "replies_sent": 0}

            print(f"[AutoReply] Found {len(messages)} unread messages to process for {user_email}")

            # Get already processed IDs for this user
            already_processed = set()
            if email_logs_collection is not None:
                cursor = email_logs_collection.find(
                    {"user_email": user_email, "message_id": {"$exists": True}},
                    {"message_id": 1}
                )
                async for doc in cursor:
                    already_processed.add(doc.get("message_id"))

            # Filter out already processed messages
            new_messages = [m for m in messages if m['id'] not in already_processed]
            
            if not new_messages:
                print(f"[AutoReply] All {len(messages)} unread messages were already processed for {user_email}")
                return {"status": "success", "processed": 0, "replies_sent": 0}

            # Process new messages in parallel with a concurrency limit
            semaphore = asyncio.Semaphore(20)
            
            async def bounded_process(msg_id):
                async with semaphore:
                    return await self._process_single_message(creds, user_email, msg_id)

            tasks = [bounded_process(msg_item['id']) for msg_item in new_messages]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            processed_count = 0
            replied_count = 0
            skipped_count = len(messages) - len(new_messages)

            for res in results:
                if isinstance(res, dict):
                    if res.get("status") == "success":
                        processed_count += 1
                        if res.get("replied"):
                            replied_count += 1
                    elif res.get("status") == "skipped":
                        skipped_count += 1
                elif isinstance(res, Exception):
                    print(f"[AutoReply] Task failed with exception: {res}")

            return {
                "status": "success",
                "processed": processed_count,
                "replies_sent": replied_count,
                "skipped": skipped_count
            }

        except Exception as e:
            print(f"Error in auto-reply service for {user_email}: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    async def _process_single_message(self, creds, user_email: str, msg_id: str):
        """Processes a single Gmail message: categorizes, replies, marks as read, and logs."""
        try:
            # Build service locally for this task (thread-safety)
            service = build('gmail', 'v1', credentials=creds)
            msg = await asyncio.to_thread(service.users().messages().get(userId='me', id=msg_id, format='full').execute)
            
            payload = msg.get('payload', {})
            headers = payload.get('headers', [])
            
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(No Subject)')
            sender_raw = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            
            # Basic sender parsing
            if "<" in sender_raw:
                sender_name = sender_raw.split("<")[0].strip().strip('"')
                sender_email = sender_raw.split("<")[1].strip().rstrip(">")
            else:
                sender_email = sender_raw.strip()
                sender_name = sender_email.split("@")[0]

            if sender_email.lower() == user_email.lower():
                # Still mark as read so we don't keep checking it
                await asyncio.to_thread(service.users().messages().batchModify(userId='me', body={
                    'ids': [msg_id],
                    'removeLabelIds': ['UNREAD']
                }).execute)
                return {"status": "skipped", "reason": "self-email"}

            print(f"[AutoReply] Processing email from: {sender_email} (Subject: {subject})")

            # Get body recursively
            body = self._get_recursive_body(payload)
            if not body:
                # Fallback for simple messages
                data = payload.get('body', {}).get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')

            # 1. Look for original campaign instructions
            campaign_instruction = None
            orig_log = None
            if email_logs_collection is not None:
                orig_log = await email_logs_collection.find_one({
                    "user_email": user_email,
                    "type": "sent",
                    "recipient": {"$regex": f"^{sender_email}$", "$options": "i"}
                }, sort=[("timestamp", -1)])
                
            if not orig_log:
                # Mark as read so we don't process it again, but skip AI categorization
                await asyncio.to_thread(service.users().messages().batchModify(userId='me', body={
                    'ids': [msg_id],
                    'removeLabelIds': ['UNREAD']
                }).execute)
                print(f"[AutoReply] SKIPPED: No previous sent email found for {sender_email}. Not a lead response.")
                return {"status": "skipped", "reason": "not-a-lead"}

            campaign_instruction = orig_log.get("auto_reply_prompt")

            # 2. Process with AI
            email_data = {
                "body": body or "", 
                "name": sender_name, 
                "email": sender_email, 
                "subject": subject,
                "instruction": campaign_instruction
            }
            graph_result = await ai_service.process_with_graph(email_data)
            intent = graph_result.get("intent", "unknown")
            reply_content = graph_result.get("reply_body", "")

            # Send reply if needed
            reply_sent = False
            if reply_content:
                result = await send_email(
                    to_email=sender_email,
                    subject=f"Re: {subject}",
                    body=reply_content,
                    user_email=user_email,
                    skip_log=True
                )
                reply_sent = result.get("success", False)
                
            # Mark as read in Gmail
            await asyncio.to_thread(service.users().messages().batchModify(userId='me', body={
                'ids': [msg_id],
                'removeLabelIds': ['UNREAD']
            }).execute)

            # Log to MongoDB
            if email_logs_collection is not None:
                record = {
                    "user_email": user_email,
                    "message_id": msg_id,
                    "thread_id": msg.get('threadId'),
                    "campaign_id": orig_log.get("campaign_id"), # Link to campaign
                    "name": sender_name,
                    "email": sender_email,
                    "subject": subject,
                    "intent": intent,
                    "message": (body or ""), # Full message as requested
                    "ai_reply": reply_content,
                    "reply_sent": reply_sent,
                    "timestamp": datetime.utcnow(),
                }
                await email_logs_collection.insert_one(record)
                
                # Detect reply and mark original 'sent' message to prevent follow-ups
                query = {"user_email": user_email, "type": "sent"}
                if msg.get('threadId'):
                    query["$or"] = [{"thread_id": msg.get('threadId')}, {"recipient": {"$regex": f"^{sender_email}$", "$options": "i"}}]
                else:
                    query["recipient"] = {"$regex": f"^{sender_email}$", "$options": "i"}
                
                await email_logs_collection.update_many(
                    query,
                    {"$set": {"reply_received": True}}
                )
            
            # Log to Google Sheets
            try:
                await sheets_service.log_responder_to_sheet(
                    name=sender_name,
                    email=sender_email,
                    message_snippet=(body or "")[:200]
                )
            except Exception as e:
                print(f"[AutoReply] Sheet logging failed: {e}")

            return {"status": "success", "replied": reply_sent}

        except Exception as e:
            print(f"Error processing message {msg_id}: {e}")
            return {"status": "error", "error": str(e)}

auto_reply_service = AutoReplyService()

