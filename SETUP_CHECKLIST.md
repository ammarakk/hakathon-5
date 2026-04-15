# Nur Scents FTE - Configuration Checklist

## ✅ COMPLETED CONFIGURATION

- [x] **Owner Phone**: +923252886031 (0325-2886031)
  - Updated in `.env`
  - Updated in `k8s/secrets.yaml`

- [x] **Business Phone**: +923252886031
  - Updated in `.env`

- [x] **.gitignore**: Protects sensitive files
  - .env files protected ✅
  - credentials.json protected ✅
  - token.json protected ✅

---

## ⚠️ PENDING CONFIGURATION

### 1. Google Gemini API (URGENT - Key Exposed)

**Status:** ⚠️ **API KEY WAS EXPOSED - NEEDS IMMEDIATE ROTATION**

**Steps:**
1. Go to: https://console.cloud.google.com/apis/credentials
2. Find and delete: `AIzaSyABw23pHf65yyIJ7Ot7tZQxBPtqlrPmJns`
3. Create a NEW API key
4. Open `.env` file
5. Replace line 6:
   ```
   # FROM:
   GEMINI_API_KEY=your_NEW_gemini_api_key_here

   # TO:
   GEMINI_API_KEY=your_new_rotated_api_key_here
   ```
6. Save the file
7. Test: `python test_api_key.py`

**Why Urgent:** The exposed key can be used by anyone and should be revoked immediately.

---

### 2. Twilio WhatsApp (Optional - For WhatsApp Integration)

**Status:** ⏳ **Not Configured**

**Steps:**
1. Go to: https://www.twilio.com/console
2. Sign up for free Twilio account
3. Get Account SID and Auth Token from console
4. Open `.env` file
5. Update lines 18-19:
   ```
   TWILIO_ACCOUNT_SID=your_actual_account_sid
   TWILIO_AUTH_TOKEN=your_actual_auth_token
   ```
6. Save the file

**Notes:**
- Twilio Sandbox is free for development
- You can test with your own WhatsApp number
- See: `docs/twilio-setup.md` for detailed guide

---

### 3. Gmail API (Optional - For Email Integration)

**Status:** ⏳ **Not Configured**

**Steps:**
1. Go to: https://console.cloud.google.com
2. Create project (or use existing)
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json`
6. Run once: `python production/channels/gmail_handler.py auth`
7. Open `.env` file
8. Update line 26:
   ```
   GMAIL_USER=your@gmail.com
   ```
9. Save the file

**Notes:**
- See: `docs/gmail-setup.md` for complete guide
- First run requires browser authentication
- `token.json` will be created automatically

---

## 🧪 TESTING YOUR CONFIGURATION

### Test 1: API Key
```bash
python test_api_key.py
```

**Expected Output:**
```
✅ API key loaded from .env
🔑 Key starts with: AIzaSy...
🧪 Testing API connection...
✅ API Response: [Gemini response in Urdu]
✅ Your API key is working correctly!
```

### Test 2: Health Check
```bash
uvicorn production.api.main:app --reload
```

Then in another terminal:
```bash
curl http://localhost:8000/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "kafka": "connected",
    "agent": "ready"
  }
}
```

### Test 3: API Documentation
Open browser: http://localhost:8000/docs

**Should show:**
- FastAPI automatic documentation
- All 9 endpoints
- Interactive API testing

---

## 📊 CONFIGURATION PRIORITY

### High Priority (Required for Basic Functionality)
1. ⚠️ **Rotate Google API Key** - DO THIS FIRST
2. ✅ **Owner Phone** - Already configured
3. Test with: `python test_api_key.py`

### Medium Priority (For Full Functionality)
4. Twilio WhatsApp - For WhatsApp channel
5. Gmail API - For email channel

### Low Priority (Optional)
6. ngrok tunnel - For local Twilio webhooks
7. Kubernetes deployment - For production scaling

---

## 🚀 QUICK START (Minimal Setup)

### Option 1: Test with API Only (No External Services)

```bash
# 1. Rotate and add your Google API key to .env
# 2. Start the API
uvicorn production.api.main:app --reload

# 3. Test in another terminal
curl -X POST http://localhost:8000/support/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Customer",
    "email": "test@example.com",
    "phone": "03252886031",
    "subject": "Product inquiry",
    "category": "product_query",
    "message": "What are your prices for oud attar?"
  }'
```

### Option 2: Full Setup (All Channels)

1. **Google API**: Rotate exposed key, add new key to .env
2. **Twilio**: Sign up, add credentials to .env
3. **Gmail**: Set up OAuth, add email to .env
4. **Start all services**:
   ```bash
   # Terminal 1: FastAPI
   uvicorn production.api.main:app --reload

   # Terminal 2: Worker
   python production/workers/message_processor.py

   # Terminal 3: Gmail Poller
   python production/channels/gmail_handler.py poll
   ```

---

## 📞 CONTACT INFORMATION

**Owner:** Ammar
**Phone:** +923252886031 (0325-2886031)
**Business:** Nur Scents
**Location:** Karachi, Pakistan

---

## 🎯 PROJECT STATUS

- **Completion:** 18/18 steps (100%)
- **Files:** 150+ files created
- **Code:** 7000+ lines
- **Status:** Ready for configuration and deployment
- **Next:** Complete API key setup and start using!

---

**Last Updated:** 2026-04-11
**Priority:** Rotate your exposed Google API key immediately! 🔒
