"""
Quick SMTP connection test - run with:
  python scratch/test_smtp.py
"""
import smtplib
import sys
import os

# Load from .env manually
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
email_user = ""
email_pass = ""

with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("EMAIL_USER="):
            email_user = line.split("=", 1)[1].strip()
        elif line.startswith("EMAIL_PASS="):
            email_pass = line.split("=", 1)[1].strip()

print(f"[TEST] Testing SMTP login for: {email_user}")
print(f"[TEST] Password length: {len(email_pass)} characters")
print()

try:
    print("1. Connecting to smtp.gmail.com:587 ...")
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
    
    print("2. Sending EHLO ...")
    server.ehlo()
    
    print("3. Starting TLS ...")
    server.starttls()
    server.ehlo()
    
    print(f"4. Logging in as {email_user} ...")
    server.login(email_user, email_pass)
    
    print("\n[SUCCESS] Gmail SMTP login works. Emails can be sent.")
    server.quit()

except smtplib.SMTPAuthenticationError as e:
    print(f"\n[FAIL] AUTH FAILED: {e}")
    print()
    print("[FIX] Gmail requires an App Password, not your regular password.")
    print("   Steps:")
    print("   1. Go to https://myaccount.google.com/security")
    print("   2. Enable 2-Step Verification if not already done")
    print("   3. Search for 'App Passwords' in your Google Account")
    print("   4. Create a new App Password for 'Mail'")
    print("   5. Copy the 16-character password (no spaces)")
    print("   6. Update EMAIL_PASS in your .env file with that App Password")

except Exception as e:
    print(f"\n[ERROR] {e}")
    sys.exit(1)
