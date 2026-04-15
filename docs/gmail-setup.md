# Gmail API Setup Guide

## Step 1 — Google Cloud Console
1. Go to console.cloud.google.com
2. Create new project:
   Name: "nur-scents-crm"
3. Click "Create"

## Step 2 — Enable Gmail API
1. APIs & Services → Library
2. Search: "Gmail API"
3. Click Enable

## Step 3 — Create Credentials
1. APIs & Services → Credentials
2. Create Credentials → OAuth 2.0 Client
3. Application type: Desktop App
4. Name: nur-scents-gmail
5. Download JSON
6. Save as: credentials.json
7. Move to project root:
   nurscents-fte/credentials.json

## Step 4 — OAuth Consent Screen
1. APIs & Services → OAuth consent screen
2. User Type: External
3. App name: Nur Scents CRM
4. Add your email as test user
5. Scopes: gmail.readonly, gmail.send,
           gmail.modify

## Step 5 — First Run Auth
Run once to authenticate:
python production/channels/gmail_handler.py auth

Browser will open → Login with Gmail
Grant permissions
token.json will be created

## Step 6 — Add to .env
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json
GMAIL_USER=your@gmail.com
GMAIL_POLL_INTERVAL=30

## Important Notes
- credentials.json = never commit to git
- token.json = never commit to git
- Add both to .gitignore
- Re-authenticate if token expires
- For webhook: need Google Cloud Pub/Sub
- For hackathon: polling is acceptable
