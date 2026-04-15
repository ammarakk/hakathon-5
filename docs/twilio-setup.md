# Twilio WhatsApp Sandbox Setup

## Step 1 — Create Free Account
1. Go to twilio.com
2. Click "Sign up for free"
3. Verify email + phone
4. Skip credit card — free tier only

## Step 2 — Get Credentials
1. Dashboard → Account Info
2. Copy: Account SID
3. Copy: Auth Token
4. Save in .env file

## Step 3 — WhatsApp Sandbox
1. Console → Messaging → Try it out
2. Click "Send a WhatsApp message"
3. You'll see sandbox number:
   +1 415 523 8886
4. Note the JOIN word shown
   Example: "join silver-tiger"

## Step 4 — Join Sandbox (Test)
From your WhatsApp:
Send: "join silver-tiger"
(use your actual word shown)
To: +1 415 523 8886

You'll get confirmation message.

## Step 5 — Set Webhook URL
1. Console → Messaging → Settings
2. WhatsApp Sandbox Settings
3. When a message comes in:
   Set URL: https://YOUR_NGROK_URL/webhooks/whatsapp
   Method: HTTP POST
4. Save

## Step 6 — Start ngrok
Terminal:
ngrok http 8000

Copy the https URL shown:
Example: https://abc123.ngrok.io

Use this as webhook URL in Twilio.

## Sandbox Limitation (Document this)
- Customers must join sandbox first
- Send "join [word]" to sandbox number
- This is expected for development
- Production: Apply for WhatsApp Business API
