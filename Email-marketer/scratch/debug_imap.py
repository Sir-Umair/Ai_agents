"""
Manually simulates 'Sync Replies' — shows each step with full output.
Run: python scratch/debug_imap.py
"""
import asyncio, os, sys, imaplib, email as email_lib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASS = os.getenv("EMAIL_PASS", "")

print(f"[IMAP] Connecting as: {EMAIL_USER}")

try:
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_USER, EMAIL_PASS)
    print("[IMAP] Login OK")
except Exception as e:
    print(f"[FAIL] IMAP login failed: {e}")
    sys.exit(1)

mail.select("inbox")

# Check UNSEEN emails
status, messages = mail.search(None, 'UNSEEN')
mail_ids = messages[0].split()
print(f"[IMAP] Unread emails in inbox: {len(mail_ids)}")

if not mail_ids:
    # Also check ALL recent emails (last 5)
    print("[IMAP] No UNREAD emails. Showing last 5 emails (any status)...")
    status2, all_msgs = mail.search(None, 'ALL')
    all_ids = all_msgs[0].split()
    recent = all_ids[-5:] if len(all_ids) >= 5 else all_ids
    for mid in reversed(recent):
        res, data = mail.fetch(mid, "(RFC822)")
        for part in data:
            if isinstance(part, tuple):
                msg = email_lib.message_from_bytes(part[1])
                print(f"  From   : {msg.get('From')}")
                print(f"  Subject: {msg.get('Subject')}")
                print(f"  Date   : {msg.get('Date')}")
                print()
else:
    print("[IMAP] Processing each unread email...")
    for i, mid in enumerate(mail_ids):
        res, data = mail.fetch(mid, "(RFC822)")
        for part in data:
            if isinstance(part, tuple):
                msg = email_lib.message_from_bytes(part[1])
                sender = msg.get("From", "")
                subject = msg.get("Subject", "")
                print(f"\n--- Email {i+1} ---")
                print(f"  From   : {sender}")
                print(f"  Subject: {subject}")

                # Extract body
                body = ""
                if msg.is_multipart():
                    for p in msg.walk():
                        if p.get_content_type() == "text/plain":
                            try:
                                body = p.get_payload(decode=True).decode("utf-8", errors="replace")
                            except Exception:
                                body = str(p.get_payload())
                            break
                else:
                    try:
                        body = msg.get_payload(decode=True).decode("utf-8", errors="replace")
                    except Exception:
                        body = str(msg.get_payload())

                print(f"  Body preview: {body[:200]}")

print()
print("[Done] If emails appeared above, run 'Sync Replies' on the dashboard (backend must be running).")
mail.close()
mail.logout()
