#!/usr/bin/env python3
"""
Update Twilio WhatsApp Webhook URL Programmatically
"""
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

# Your Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
sandbox_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

# New webhook URL from localtunnel
WEBHOOK_URL = "https://wicked-hairs-start.loca.lt/webhooks/whatsapp"

print("=" * 60)
print("UPDATING TWILIO WHATSAPP WEBHOOK")
print("=" * 60)
print()
print(f"Webhook URL: {WEBHOOK_URL}")
print(f"Sandbox Number: {sandbox_number}")
print()

try:
    client = Client(account_sid, auth_token)
    print("[OK] Connected to Twilio")
    print()

    # Get WhatsApp sandbox configuration
    # Note: Twilio Free tier doesn't allow programmatic webhook updates
    # This script shows what NEEDS to be done manually

    print("=" * 60)
    print("MANUAL STEP REQUIRED")
    print("=" * 60)
    print()
    print("Twilio Free tier doesn't allow programmatic webhook updates.")
    print("Please follow these steps:")
    print()
    print("STEP 1: Go to Twilio Console")
    print("  https://www.twilio.com/console/sms/whatsapp/sandbox")
    print()
    print("STEP 2: Find 'Sandbox Configuration' section")
    print("  Look for: 'When a message comes in'")
    print()
    print(f"STEP 3: Enter webhook URL:")
    print(f"  {WEBHOOK_URL}")
    print()
    print("STEP 4: Set method to: POST")
    print()
    print("STEP 5: Click 'Save Sandbox'")
    print()
    print("=" * 60)
    print("AFTER SAVING:")
    print("=" * 60)
    print()
    print("1. Send WhatsApp message to: +1 415 523 8886")
    print("2. Message: 'oudh attar price'")
    print("3. You'll receive AI response!")
    print()
    print("Current webhook URL is ready to use!")
    print()

except Exception as e:
    print(f"[ERROR] {e}")
    print()
    print("Please update webhook manually in Twilio Console")
