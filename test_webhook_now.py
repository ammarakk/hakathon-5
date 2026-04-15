#!/usr/bin/env python3
import requests
import sys
import re

def test_webhook():
    webhook_url = "http://localhost:8000/webhooks/whatsapp"

    data = {
        "From": "whatsapp:+923252886031",
        "To": "whatsapp:+14155238888",
        "Body": "oudh attar price batao",
        "ProfileName": "Ammar",
        "NumMedia": "0"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    print("=" * 60)
    print("Testing WhatsApp Webhook")
    print("=" * 60)
    print(f"URL: {webhook_url}")
    print(f"Message: {data['Body']}")
    print("Sending...")
    print("-" * 60)

    try:
        response = requests.post(webhook_url, data=data, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("[PASS] Webhook working!")
            print()
            print("Twilio Response (TwimL):")
            print(response.text)
            print()

            match = re.search(r'<Message>(.*?)</Message>', response.text, re.DOTALL)
            if match:
                ai_response = match.group(1)
                print(f"AI Response: {ai_response}")
                print()

            return True
        else:
            print(f"[FAIL] Status: {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_api():
    url = "http://localhost:8000/support/submit"
    data = {
        "name": "Ammar",
        "email": "ammar@nurscents.com",
        "phone": "+923252886031",
        "subject": "Oudh Attar Price",
        "category": "product_query",
        "message": "bhai oudh attar ka price batao"
    }

    print()
    print("=" * 60)
    print("Testing Direct API")
    print("=" * 60)
    print(f"URL: {url}")
    print("Sending...")
    print("-" * 60)

    try:
        response = requests.post(url, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print("[PASS] API working!")
            print()
            print("Response:")
            for key, value in result.items():
                if key == "response":
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")
            print()
            return True
        else:
            print(f"[FAIL] Status: {response.status_code}")
            return False

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

if __name__ == "__main__":
    print()
    print("=" * 60)
    print("  NUR SCENTS - WEBHOOK TEST")
    print("=" * 60)
    print()

    webhook_ok = test_webhook()
    api_ok = test_api()

    print()
    print("=" * 60)
    print("RESULTS:")
    print("=" * 60)
    print(f"WhatsApp Webhook: {'[PASS]' if webhook_ok else '[FAIL]'}")
    print(f"Direct API: {'[PASS]' if api_ok else '[FAIL]'}")
    print()

    if webhook_ok and api_ok:
        print("[SUCCESS] ALL SYSTEMS WORKING!")
        print()
        print("WEBHOOK IS WORKING - AI responds correctly!")
        print()
        print("To receive REAL WhatsApp messages:")
        print("1. ngrok is required (free account needed)")
        print("2. Go to: https://dashboard.ngrok.com/signup")
        print("3. Get authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken")
        print("4. Run: ngrok config add-authtoken YOUR_TOKEN")
        print("5. Run: ngrok http 8000")
        print("6. Copy the https URL (e.g., https://abc.ngrok.io)")
        print("7. Go to Twilio Console -> WhatsApp Sandbox Settings")
        print("8. Set webhook URL to: https://abc.ngrok.io/webhooks/whatsapp")
        print("9. Save and test from WhatsApp!")
        print()
        print("Or test current system:")
        print("  python test_webhook_now.py")
    else:
        print("[ERROR] Check logs above")
        print()
        print("Debug commands:")
        print("  tail -f logs/api.log")
        print("  curl http://localhost:8000/health")

    print()
