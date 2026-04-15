# check_twilio_sandbox.py - Check Twilio WhatsApp Sandbox status
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

print("=" * 60)
print("Twilio WhatsApp Sandbox Status Check")
print("=" * 60)
print()

try:
    client = Client(account_sid, auth_token)
    print("OK Connected to Twilio")
    print()

    # Get account information
    account = client.api.accounts(account_sid).fetch()
    print(f"Account: {account.friendly_name}")
    print(f"Status: {account.status}")
    print()

    # Check WhatsApp sandbox numbers
    print("Checking WhatsApp Sandbox...")
    print("-" * 60)

    # Try to get sandbox phone numbers
    from_number = "whatsapp:+14155238886"
    to_number = "+923252886031"

    print(f"Sandbox From: {from_number}")
    print(f"Your To: {to_number}")
    print()

    print("IMPORTANT:")
    print("1. Your number must be verified in Twilio WhatsApp Sandbox")
    print("2. Go to: https://www.twilio.com/console/sms/whatsapp/sandbox")
    print("3. Add your number: +923252886031")
    print("4. You'll receive a WhatsApp message with verification code")
    print("5. Enter the code to complete verification")
    print()

    print("After verification, try:")
    print("python test_twilio_whatsapp.py")

except Exception as e:
    print(f"ERROR: {e}")
    print()
    print("Troubleshooting:")
    print("- Check your Account SID and Auth Token")
    print("- Verify at: https://www.twilio.com/console")
    print("- Ensure WhatsApp is enabled in your account")

print()
print("=" * 60)
