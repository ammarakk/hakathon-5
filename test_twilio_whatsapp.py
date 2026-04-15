# test_twilio_whatsapp.py - Test Twilio WhatsApp integration
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

# Get Twilio credentials from .env
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
to_number = "+923252886031"  # Owner's phone

print("=" * 60)
print("Testing Twilio WhatsApp Integration")
print("=" * 60)
print()

# Check credentials
if not account_sid or account_sid == "your_twilio_account_sid":
    print("ERROR Twilio Account SID not configured!")
    print("Please add TWILIO_ACCOUNT_SID to .env")
    exit(1)

if not auth_token or auth_token == "your_twilio_auth_token_here":
    print("ERROR Twilio Auth Token not configured!")
    print("Please add TWILIO_AUTH_TOKEN to .env")
    print("Run: python add_twilio_token.py")
    exit(1)

print(f"OK Account SID: {account_sid[:10]}...")
print(f"OK Auth Token: {auth_token[:6]}...")
print(f"OK From: {from_number}")
print(f"OK To: {to_number}")
print()

# Initialize Twilio client
try:
    client = Client(account_sid, auth_token)
    print("OK Twilio client initialized")
except Exception as e:
    print(f"ERROR Twilio client error: {e}")
    exit(1)

print()
print("Sending test WhatsApp message...")
print("-" * 60)

# Send WhatsApp message
try:
    # Option 1: Using content template (as in your example)
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
        content_variables='{"1":"12/1","2":"3pm"}',
        to='whatsapp:+923252886031'
    )

    print()
    print("=" * 60)
    print("OK WhatsApp Message Sent Successfully!")
    print("=" * 60)
    print()
    print(f"Message SID: {message.sid}")
    print(f"Status: {message.status}")
    print(f"To: {message.to}")
    print(f"From: {message.from_}")
    print()
    print("Check your WhatsApp (+923252886031) for the message!")

except Exception as e:
    print()
    print("=" * 60)
    print(f"ERROR Error sending WhatsApp message")
    print("=" * 60)
    print(f"Error: {e}")
    print()
    print("Common issues:")
    print("1. Auth Token is incorrect")
    print("2. Phone number not added to Twilio Sandbox")
    print("3. Content template not approved")
    print("4. Account SID is incorrect")
    print()
    print("Troubleshooting:")
    print("- Check your Twilio Console: https://www.twilio.com/console")
    print("- Verify Sandbox numbers: https://www.twilio.com/console/sms/whatsapp/sandbox")
    print("- Ensure your phone is added to sandbox")
