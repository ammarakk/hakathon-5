#!/usr/bin/env python3
"""
Final solution: List all numbers and update webhook
"""
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
webhook_url = "https://wicked-hairs-start.loca.lt/webhooks/whatsapp"

print("=" * 70)
print("TWILIO WEBHOOK UPDATE - FINDING SANDBOX NUMBER")
print("=" * 70)
print()

try:
    client = Client(account_sid, auth_token)
    print("[OK] Connected to Twilio")
    print()

    # List ALL phone numbers in account
    print("Searching for WhatsApp Sandbox number...")
    print("-" * 70)

    numbers = client.incoming_phone_numbers.list()

    if len(numbers) == 0:
        print("[INFO] No phone numbers found")
        print()
        print("This is expected with WhatsApp Sandbox.")
        print("Sandbox numbers are configured differently.")
        print()

    else:
        print(f"Found {len(numbers)} phone number(s):")
        print()
        for i, number in enumerate(numbers, 1):
            print(f"{i}. {number.phone_number}")
            print(f"   SID: {number.sid}")
            print(f"   Capabilities: {number.capabilities}")
            print()

        # Try to update the sandbox number
        for number in numbers:
            # Check if it's a WhatsApp number
            if 'whatsapp' in str(number.phone_number).lower() or '14155238886' in number.phone_number:
                print(f"Found WhatsApp Sandbox: {number.phone_number}")
                print()

                # Try to update webhook
                print("Updating webhook URL...")
                try:
                    # Update with SMS URL
                    updated_number = client.incoming_phone_numbers(number.sid).update(
                        sms_url=webhook_url,
                        sms_method='POST'
                    )

                    print("[SUCCESS] Webhook updated!")
                    print(f"New SMS URL: {updated_number.sms_url}")
                    print()

                    print("=" * 70)
                    print("✅ WEBHOOK CONFIGURED!")
                    print("=" * 70)
                    print()
                    print("You can now test:")
                    print("  python test_webhook_now.py")
                    print()
                    print("Or send WhatsApp to:")
                    print("  +1 415 523 8886")
                    print()
                    break

                except Exception as e:
                    print(f"[ERROR] Could not update: {e}")
                    print()
                    print("This number may not support webhook updates")
                    print()

    print("=" * 70)
    print("IF AUTO-UPDATE FAILED - MANUAL STEPS:")
    print("=" * 70)
    print()
    print("Twilio Sandbox has special configuration.")
    print("Please update webhook manually:")
    print()
    print("1. Open this link:")
    print("   https://www.twilio.com/console/sms/whatsapp/sandbox")
    print()
    print(f"2. Set webhook URL to:")
    print(f"   {webhook_url}")
    print()
    print("3. Set method to POST")
    print()
    print("4. Click 'Save Sandbox'")
    print()

except Exception as e:
    print(f"[ERROR] {e}")
    print()

print()
print("=" * 70)
print("TESTING AFTER UPDATE:")
print("=" * 70)
print()
print("Run this command to test:")
print("  python test_webhook_now.py")
print()
print("Or send WhatsApp message:")
print("  To: +1 415 523 8886")
print("  Message: join silver-tiger")
print()
