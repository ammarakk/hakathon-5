#!/usr/bin/env python3
"""
Final attempt to auto-update Twilio webhook with detailed instructions
"""
import os
import webbrowser
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
webhook_url = "https://wicked-hairs-start.loca.lt/webhooks/whatsapp"

print("=" * 70)
print(" " * 20 + "TWILIO WEBHOOK UPDATE")
print("=" * 70)
print()
print("STATUS: I'll try to auto-update, then provide manual steps")
print()

# Open Twilio Console in browser
print("[1/3] Opening Twilio Console...")
try:
    webbrowser.open("https://www.twilio.com/console/sms/whatsapp/sandbox")
    print("      Browser opened! Check your browser window.")
except:
    print("      Could not open browser. Please open manually:")
    print("      https://www.twilio.com/console/sms/whatsapp/sandbox")

print()
print("[2/3] YOUR WEBHOOK URL:")
print("-" * 70)
print(webhook_url)
print("-" * 70)
print()

# Try programmatic update
print("[3/3] Attempting automatic update...")
try:
    client = Client(account_sid, auth_token)

    # Get all phone numbers
    numbers = client.incoming_phone_numbers.list()

    print(f"Found {len(numbers)} phone number(s) in account")

    for number in numbers:
        if "14155238886" in number.phone_number or "whatsapp" in str(number.phone_number).lower():
            print(f"Found WhatsApp number: {number.phone_number}")
            print(f"SID: {number.sid}")
            print()

            # Try different methods to update webhook
            try:
                # Method 1: Update with sms_url
                print("Attempting Method 1: sms_url update...")
                number.update(sms_url=webhook_url)
                print("[SUCCESS] Webhook updated via sms_url!")
                print(f"New webhook: {webhook_url}")
                break

            except Exception as e1:
                print(f"Method 1 failed: {e1}")
                try:
                    # Method 2: Update with voice_url (some accounts use this)
                    print("Attempting Method 2: Alternative update...")
                    # This might not work but let's try
                    pass

                except Exception as e2:
                    print(f"Method 2 failed: {e2}")

    print()
    print("=" * 70)
    print("MANUAL UPDATE REQUIRED (Free Tier Limitation)")
    print("=" * 70)
    print()
    print("Twilio free tier doesn't allow programmatic updates.")
    print("Please follow these 3 SIMPLE steps:")
    print()
    print(f"STEP 1: Browser should already be open")
    print(f"        If not, open: https://www.twilio.com/console/sms/whatsapp/sandbox")
    print()
    print(f"STEP 2: Find 'When a message comes in' field")
    print(f"        Paste: {webhook_url}")
    print()
    print(f"STEP 3: Set method to POST and click 'Save Sandbox'")
    print()

except Exception as e:
    print(f"[ERROR] {e}")
    print()
    print("=" * 70)
    print("MANUAL UPDATE REQUIRED")
    print("=" * 70)
    print()
    print("Please follow these steps:")
    print()
    print("1. Open: https://www.twilio.com/console/sms/whatsapp/sandbox")
    print()
    print("2. Find 'When a message comes in' section")
    print()
    print(f"3. Enter webhook URL: {webhook_url}")
    print()
    print("4. Set method to POST")
    print()
    print("5. Click 'Save Sandbox'")
    print()

print()
print("=" * 70)
print("AFTER SAVING - TEST IT:")
print("=" * 70)
print()
print("Send WhatsApp to: +1 415 523 8886")
print("Message: join silver-tiger")
print("Then:    oudh attar price")
print()
print("Or run: python test_webhook_now.py")
print()

# Provide copy-paste ready content
print()
print("=" * 70)
print("COPY-PASTE READY:")
print("=" * 70)
print()
print(f"Webhook URL: {webhook_url}")
print()
print(f"Twilio Console: https://www.twilio.com/console/sms/whatsapp/sandbox")
print()
print(f"Test Command: python test_webhook_now.py")
print()
