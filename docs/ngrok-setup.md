# ngrok Setup Guide

## Install ngrok
1. Go to ngrok.com
2. Sign up free
3. Download ngrok
4. Add authtoken:
   ngrok config add-authtoken YOUR_TOKEN

## Start ngrok
Open NEW terminal:
ngrok http 8000

## Copy URL
You'll see:
Forwarding: https://abc123.ngrok.io -> localhost:8000

Copy: https://abc123.ngrok.io

## Set in Twilio
Twilio Console ->
Messaging -> Sandbox Settings ->
When a message comes in:
https://abc123.ngrok.io/webhooks/whatsapp

## Important Notes
- ngrok URL changes every restart
- Update Twilio webhook each time
- Or use ngrok paid plan for static URL
- Keep ngrok terminal open while testing
