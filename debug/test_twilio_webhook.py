# debug/test_twilio_webhook.py
import httpx
import json
import os
import sys

def get_ngrok_url():
    try:
        response = httpx.get(
            "http://localhost:4040/api/tunnels",
            timeout=5
        )
        tunnels = response.json().get("tunnels", [])
        for t in tunnels:
            if t.get("proto") == "https":
                return t.get("public_url")
        return None
    except Exception:
        return None

def test_local_webhook():
    print("Testing local webhook...")
    try:
        response = httpx.post(
            "http://localhost:8000/webhooks/whatsapp",
            data={
                "From": "whatsapp:+923001234567",
                "Body": "bhai oud attar ka price?",
                "ProfileName": "Debug Test",
                "NumMedia": "0",
                "MessageSid": "SMdebug123"
            },
            headers={
                "Content-Type":
                "application/x-www-form-urlencoded"
            },
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_ngrok_webhook(ngrok_url):
    print(f"\nTesting ngrok webhook...")
    try:
        response = httpx.post(
            f"{ngrok_url}/webhooks/whatsapp",
            data={
                "From": "whatsapp:+923001234567",
                "Body": "test from ngrok",
                "ProfileName": "Ngrok Test",
                "NumMedia": "0"
            },
            headers={
                "Content-Type":
                "application/x-www-form-urlencoded"
            },
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def check_env():
    print("\nChecking .env file...")
    from dotenv import load_dotenv
    load_dotenv()

    checks = {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID", ""),
        "TWILIO_AUTH_TOKEN": os.getenv("TWILIO_AUTH_TOKEN", ""),
        "OWNER_PHONE": os.getenv("OWNER_PHONE", ""),
        "DATABASE_URL": os.getenv("DATABASE_URL", "")
    }

    all_ok = True
    for key, value in checks.items():
        if value:
            masked = value[:8] + "..."
            print(f"  [OK] {key}: {masked}")
        else:
            print(f"  [MISSING] {key}: NOT SET")
            all_ok = False

    return all_ok

def main():
    print("="*50)
    print("Nur Scents WhatsApp Debug Tool")
    print("="*50)

    env_ok = check_env()

    print("\n" + "="*50)
    local_ok = test_local_webhook()

    print("\n" + "="*50)
    ngrok_url = get_ngrok_url()

    if ngrok_url:
        print(f"\n[OK] ngrok URL: {ngrok_url}")
        ngrok_ok = test_ngrok_webhook(ngrok_url)
        print("\n" + "="*50)
        print("SET THIS IN TWILIO CONSOLE:")
        print(f"\n  {ngrok_url}/webhooks/whatsapp\n")
        print("Steps:")
        print("1. twilio.com/console")
        print("2. Messaging → Try it out")
        print("3. Send a WhatsApp message")
        print("4. Sandbox Settings")
        print(f"5. URL: {ngrok_url}/webhooks/whatsapp")
        print("6. Method: HTTP POST")
        print("7. Save")
    else:
        print("\n[ERROR] ngrok NOT running!")
        print("Run: ngrok http 8000")
        ngrok_ok = False

    print("\n" + "="*50)
    print("DIAGNOSIS SUMMARY:")
    print("="*50)
    print(f"  ENV vars:      {'[OK]' if env_ok else '[MISSING]'}")
    print(f"  Local webhook: {'[OK]' if local_ok else '[FAILING]'}")
    print(f"  ngrok:         {'[OK]' if ngrok_url else '[NOT RUNNING]'}")
    print(f"  ngrok webhook: {'[OK]' if ngrok_ok else '[FAILING]'}")

    if env_ok and local_ok and ngrok_url and ngrok_ok:
        print("\n[OK] EVERYTHING WORKING!")
    else:
        print("\n[ERROR] Issues found — fix above errors")

if __name__ == "__main__":
    main()
