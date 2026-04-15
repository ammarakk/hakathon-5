# debug/check_twilio_webhook.py
import os
from dotenv import load_dotenv
load_dotenv()

def check_twilio_webhook():
    try:
        from twilio.rest import Client

        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

        if not sid or not token:
            print("❌ Twilio credentials not set")
            return

        print(f"Twilio Account SID: {sid[:12]}...")
        print(f"WhatsApp Number: {whatsapp_number}")
        print()

        client = Client(sid, token)

        # Get phone number
        phone_numbers = client.messaging.v1.services \
            .list(limit=10)

        print("Twilio Services:")
        for service in phone_numbers:
            print(f"  SID: {service.sid}")
            print(f"  Friendly Name: {service.friendly_name}")
            if hasattr(service, 'webhook_url'):
                print(f"  Webhook URL: {service.webhook_url}")
            print()

        # Check current webhook configuration
        print("="*50)
        print("IMPORTANT: Webhook URL Setup")
        print("="*50)
        print("Twilio Console mein ja kar webhook URL set karein:")
        print()
        print("1. https://www.twilio.com/console open karein")
        print("2. Messaging → Services → WhatsApp Messaging Service")
        print("3. Integration → WhatsApp Sandbox Settings")
        print("4. 'When a message comes in' webhook URL set karein:")
        print()
        print("   LOCAL TESTING:")
        print("   http://localhost:8000/webhooks/whatsapp")
        print()
        print("   PRODUCTION (with ngrok):")
        print("   https://your-ngrok-url.ngrok.io/webhooks/whatsapp")
        print()
        print("5. Save karein!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_twilio_webhook()
