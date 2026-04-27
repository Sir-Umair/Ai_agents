import sys

def log(msg):
    print(msg)
    sys.stdout.flush()

log("Importing app.services.follow_up_service...")
from app.services.follow_up_service import follow_up_service
log("Importing app.services.email_service...")
from app.services.email_service import send_bulk_emails
log("Importing app.services.ai_service...")
from app.services.ai_service import ai_service
log("Importing app.services.auto_reply_service...")
from app.services.auto_reply_service import auto_reply_service
log("Done")
