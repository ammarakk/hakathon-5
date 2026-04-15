# debug/twilio_sandbox_setup.py
import os
from dotenv import load_dotenv
load_dotenv()

def setup_twilio_sandbox():
    try:
        from twilio.rest import Client

        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

        print("="*60)
        print("TWILIO SANDBOX SETUP GUIDE")
        print("="*60)
        print()

        if not account_sid or account_sid == "your_twilio_account_sid":
            print("ERROR: Twilio credentials not configured!")
            print("Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env file")
            return

        print(f"Account SID: {account_sid[:12]}...")
        print(f"WhatsApp Number: {whatsapp_number}")
        print()

        client = Client(account_sid, auth_token)

        # Get sandbox info
        try:
            services = client.messaging.v1.services.list(limit=10)

            print("AVAILABLE SERVICES:")
            print("-" * 60)
            for service in services:
                print(f"Service Name: {service.friendly_name}")
                print(f"Service SID: {service.sid}")
                print()

        except Exception as e:
            print(f"Could not fetch services: {e}")

        print("="*60)
        print("SANDBOX JOIN INSTRUCTIONS")
        print("="*60)
        print()
        print("STEP 1: Open WhatsApp on your phone")
        print()
        print("STEP 2: Send this message:")
        print(f"  To: {whatsapp_number}")
        print("  Message: join [your-sandbox-word]")
        print()
        print("STEP 3: You will receive a reply:")
        print("  'You have joined the Twilio WhatsApp Sandbox!'")
        print()
        print("STEP 4: Now send test messages:")
        print("  'bhai oud attar ka price kya hai?'")
        print("  'mujhe rose attar chahiye'")
        print()
        print("="*60)
        print("WEBHOOK CONFIGURATION")
        print("="*60)
        print()
        print("For LOCAL testing (without ngrok):")
        print("  Webhook URL: http://localhost:8000/webhooks/whatsapp")
        print()
        print("For PRODUCTION testing:")
        print("  1. Install ngrok: choco install ngrok -y")
        print("  2. Start ngrok: ngrok http 8000")
        print("  3. Copy the https URL (like: https://abc.ngrok.io)")
        print("  4. Set webhook in Twilio Console")
        print()
        print("="*60)
        print("QUICK TEST (Without Twilio):")
        print("="*60)
        print()
        print("Use this curl command to test directly:")
        print()
        print("curl -X POST http://localhost:8000/webhooks/whatsapp \\")
        print('  -d "From=whatsapp:+923001234567" \\')
        print('  -d "Body=oud price kya hai?" \\')
        print('  -d "ProfileName=Ammar" \\')
        print('  -d "NumMedia=0"')
        print()
        print("="*60)

    except Exception as e:
        print(f"Error: {e}")
        print()
        print("Make sure twilio library is installed:")
        print("pip install twilio")

if __name__ == "__main__":
    setup_twilio_sandbox()
