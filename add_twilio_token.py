# add_twilio_token.py - Add your Twilio Auth Token to .env
import os
from pathlib import Path

print("=" * 60)
print("Adding Twilio Auth Token to .env")
print("=" * 60)
print()

auth_token = input("Enter your Twilio Auth Token: ").strip()

if not auth_token or auth_token == "your_twilio_auth_token":
    print("❌ Invalid Auth Token")
    exit(1)

print(f"✅ Auth Token received (length: {len(auth_token)})")

# Read .env file
env_path = Path(".env")
with open(env_path, "r") as f:
    lines = f.readlines()

# Update the auth token line
for i, line in enumerate(lines):
    if line.startswith("TWILIO_AUTH_TOKEN="):
        lines[i] = f'TWILIO_AUTH_TOKEN={auth_token}\n'
        print(f"✅ Updated line {i+1} in .env")
        break

# Write back to .env
with open(env_path, "w") as f:
    f.writelines(lines)

print()
print("=" * 60)
print("✅ Twilio Auth Token added successfully!")
print("=" * 60)
print()
print("Next: Test Twilio WhatsApp with:")
print("python test_twilio_whatsapp.py")
