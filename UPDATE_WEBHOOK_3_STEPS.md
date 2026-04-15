# 🔧 TWILIO WEBHOOK UPDATE - EASY 3 STEPS

## 📋 COPY THIS URL:
```
https://wicked-hairs-start.loca.lt/webhooks/whatsapp
```

## 🌐 OPEN THIS LINK:
```
https://www.twilio.com/console/sms/whatsapp/sandbox
```

## ⚙️ UPDATE SETTINGS:

### STEP 1 (30 seconds):
1. Link opens in browser ✅
2. Login to Twilio (if not already)

### STEP 2 (1 minute):
Find the section: **"When a message comes in"**

You'll see:
```
┌─────────────────────────────────────┐
│ When a message comes in             │
│                                      │
│ [Webhook URL input field]          │
│                                      │
│ [HTTP method dropdown]              │
│                                      │
│ [Save Sandbox button]               │
└─────────────────────────────────────┘
```

### STEP 3 (30 seconds):
1. **Paste the URL:**
   ```
   https://wicked-hairs-start.loca.lt/webhooks/whatsapp
   ```

2. **Set method to:** POST

3. **Click:** Save Sandbox

## ✅ VERIFICATION:

### Step 1 - Check console:
After saving, you should see:
```
✓ Sandbox settings saved
```

### Step 2 - Test immediately:
```bash
python test_webhook_now.py
```

Expected output:
```
[PASS] Webhook working!
AI Response: Ji! AI response yahan aayega...
```

### Step 3 - Send WhatsApp message:
```
To: +1 415 523 8888
Message: oudh attar price
```

**You should receive AI response!**

---

## 🚨 IF YOU DON'T SEE THE FIELD:

### Look for these sections:
- "Sandbox Configuration"
- "Webhook URL"
- "When a message comes in"
- "Messaging Settings"

### Alternative location:
- Console → Messaging → Settings
- WhatsApp Sandbox Settings

---

## 🧪 QUICK TEST:

### Option 1 - Python script:
```bash
python test_webhook_now.py
```

### Option 2 - cURL:
```bash
curl -X POST https://wicked-hairs-start.loca.lt/webhooks/whatsapp \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+923252886031&Body=test&ProfileName=Test&NumMedia=0"
```

---

## 📊 SUCCESS INDICATORS:

✅ Console says: "Settings saved"
✅ Test script says: "[PASS] Webhook working!"
✅ WhatsApp responses start working

---

## 🔧 TROUBLESHOOTING:

### Issue: "Field not visible"
- Solution: Scroll down on the page
- Look for "Advanced Settings"

### Issue: "Save button not working"
- Solution: Refresh page and try again
- Check if URL is valid

### Issue: "No response after saving"
- Solution: Wait 30 seconds
- Twilio might take time to propagate

---

## 🎯 AFTER SETUP:

You're all set! Send WhatsApp message to:
```
+1 415 523 8888
```

With any message like:
- "oudh attar price"
- "order karna hai"
- "delivery status"

**AI will respond automatically!**

---

**TIP:** Keep this tunnel running! If it stops, run:
```bash
lt --port 8000
```

Copy the new URL and update in Twilio!
