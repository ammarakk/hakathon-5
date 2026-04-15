#!/usr/bin/env python3
"""
Quick verification that Twilio webhook is connected
"""
import requests

print("=" * 60)
print("VERIFYING TWILIO WEBHOOK CONNECTION")
print("=" * 60)
print()

# Test through public tunnel
webhook_url = "https://wicked-hairs-start.loca.lt/webhooks/whatsapp"
data = {
    "From": "whatsapp:+923252886031",
    "Body": "Is Twilio webhook working?",
    "ProfileName": "Ammar",
    "NumMedia": "0"
}

print(f"Testing webhook: {webhook_url}")
print(f"From: {data['From']}")
print(f"Message: {data['Body']}")
print()
print("Sending request...")
print("-" * 60)

try:
    response = requests.post(webhook_url, data=data, timeout=30)

    if response.status_code == 200:
        print("[SUCCESS] Webhook Connected!")
        print()
        print("Response from Twilio:")
        print(response.text)
        print()

        # Extract AI message
        import re
        match = re.search(r'<Message>(.*?)</Message>', response.text, re.DOTALL)
        if match:
            ai_message = match.group(1)
            print(f"AI Message: {ai_message}")
            print()

        print("=" * 60)
        print("✅ TWILIO WEBHOOK IS CONNECTED!")
        print("=" * 60)
        print()
        print("You can now:")
        print("1. Send WhatsApp to: +1 415 523 8886")
        print("2. Message: 'oudh attar price'")
        print("3. Receive AI response!")
        print()

    else:
        print(f"[ERROR] Status: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"[ERROR] {e}")
    print()
    print("Check if tunnel is running:")
    print("  lt --port 8000")

print()
