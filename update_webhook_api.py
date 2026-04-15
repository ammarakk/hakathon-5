#!/usr/bin/env python3
"""
Update Twilio Sandbox Webhook using Twilio API
This updates the webhook URL for WhatsApp sandbox
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
webhook_url = "https://wicked-hairs-start.loca.lt/webhooks/whatsapp"

print("=" * 70)
print("UPDATING TWILIO SANDBOX WEBHOOK (PROGRAMMATIC)")
print("=" * 70)
print()
print(f"Account SID: {account_sid}")
print(f"New Webhook: {webhook_url}")
print()

# Twilio API endpoint for updating phone number
# The sandbox number is +14155238886
url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/IncomingPhoneNumbers/PN2a0b9bed9f02903b4c26e4662883bd15a.json"

print(f"API Endpoint: {url}")
print()

# Update payload
data = {
    "SmsUrl": webhook_url,
    "SmsMethod": "POST"
}

print("Sending update request...")
print("-" * 70)

try:
    response = requests.post(
        url,
        data=data,
        auth=(account_sid, auth_token),
        timeout=30
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        print("[SUCCESS] Webhook updated!")
        print()
        result = response.json()
        print(f"Phone Number: {result.get('phone_number', 'N/A')}")
        print(f"SMS URL: {result.get('sms_url', 'N/A')}")
        print(f"SMS Method: {result.get('sms_method', 'N/A')}")
        print()
        print("=" * 70)
        print("✅ WEBHOOK CONFIGURED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print("Your webhook URL is now:")
        print(f"  {webhook_url}")
        print()
        print("Test it now:")
        print("  python test_webhook_now.py")
        print()
        print("Or send WhatsApp to: +1 415 523 8886")
        print("  Message: oudh attar price")
        print()

    else:
        print(f"[ERROR] Status: {response.status_code}")
        print(f"Response: {response.text}")
        print()
        print("=" * 70)
        print("MANUAL UPDATE REQUIRED")
        print("=" * 70)
        print()
        print("Please open:")
        print("  https://www.twilio.com/console/sms/whatsapp/sandbox")
        print()
        print("And set webhook to:")
        print(f"  {webhook_url}")
        print()

except Exception as e:
    print(f"[ERROR] {e}")
    print()
    print("Please update manually in Twilio Console")

print()
