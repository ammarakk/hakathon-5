#!/usr/bin/env python3
"""
Twilio Webhook Update Helper
Opens Twilio console and provides easy instructions
"""
import webbrowser
import os

webhook_url = "https://wicked-hairs-start.loca.lt/webhooks/whatsapp"

print("=" * 60)
print("TWILIO WEBHOOK UPDATE HELPER")
print("=" * 60)
print()

print("I'll open Twilio Console for you...")
print()

# Open Twilio Console in browser
twilio_url = "https://www.twilio.com/console/sms/whatsapp/sandbox"
webbrowser.open(twilio_url)

print(f"1. Twilio Console opened in your browser")
print()
print(f"2. Find: 'When a message comes in' section")
print()
print(f"3. Paste this URL:")
print(f"   {webhook_url}")
print()
print(f"4. Select: POST")
print()
print(f"5. Click: Save Sandbox")
print()

print("=" * 60)
print("AFTER SAVING - TEST IT:")
print("=" * 60)
print()
print("Send WhatsApp to: +1 415 523 8888")
print("Message: oudh attar price")
print()
print("Or test here:")
print("  python test_webhook_now.py")
print()

input("Press Enter after you've saved the webhook...")

print()
print("Testing webhook...")

import requests
import time
time.sleep(3)

try:
    data = {
        "From": "whatsapp:+923252886031",
        "Body": "Testing webhook update",
        "ProfileName": "Test User",
        "NumMedia": "0"
    }

    response = requests.post(
        "http://localhost:8000/webhooks/whatsapp",
        data=data,
        timeout=30
    )

    if response.status_code == 200:
        print("[SUCCESS] Webhook is working!")
        print()
        print("You can now send WhatsApp messages to:")
        print("  +1 415 523 8888")
        print()
        print("You'll receive AI responses!")
    else:
        print(f"[ERROR] Status: {response.status_code}")

except Exception as e:
    print(f"[ERROR] {e}")

print()
print("=" * 60)
